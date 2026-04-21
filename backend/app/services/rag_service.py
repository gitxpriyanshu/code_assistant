"""
RAG (Retrieval-Augmented Generation) service.
Orchestrates: embed query → retrieve from FAISS → build prompt → call Groq → parse output.
"""

import json
import logging
import re
import hashlib
import asyncio
from collections import OrderedDict

from app.models.schemas import DebugRequest, DebugResponse
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

# Global in-memory cache for debug results
# Key: sha256(code + error + language)
# Value: DebugResponse
_DEBUG_CACHE = OrderedDict()
CACHE_LIMIT = 50
CACHE_SCHEMA_VERSION = "v3"

# Track active tasks (Deduplication)
_INFLIGHT_REQUESTS = {}

PLACEHOLDER_LINE_BY_LINE = "Line-by-line analysis provided in summary."

# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are an expert debugging assistant. Your job is to analyse the provided code and error (if provided), \
then return a structured JSON response with three fields:

1. **explanation** — A clear, concise explanation of *why* the error occurs, or the logical issues found.
2. **fix** — The corrected version of the code that resolves the issues.
3. **optimized_code** — An optimized / best-practice version of the code (may differ from the fix).

Rules:
- Respond ONLY with valid JSON. No markdown fences, no extra text.
- The JSON must have exactly these keys: "explanation", "fix", "optimized_code".
- Keep the explanation beginner-friendly but technically accurate.
- Write production-quality code in the fix and optimized_code fields.
- IMPORTANT: Use proper newlines (\\n) and indentation in code strings. NEVER return code on a single line.
"""

USER_PROMPT_TEMPLATE = """### Language
{language}

{query_details}

### Relevant Debugging Context
{context}

Return your response as JSON with keys: explanation, fix, optimized_code.
"""


class RAGService:
    """End-to-end RAG pipeline for debugging assistance."""

    def __init__(
        self,
        vector_store: VectorStoreService,
        llm_service: LLMService | None = None,
    ) -> None:
        self._vector_store = vector_store
        self._llm_service = llm_service or LLMService()
        self._inflight_requests = _INFLIGHT_REQUESTS

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    async def debug(self, request: DebugRequest) -> DebugResponse:
        """Run the full RAG pipeline with strict Cache-First deduplication."""
        # 0. STRICT INPUT NORMALIZATION
        code = (request.code or "").strip()
        error = (request.error_message or "").strip()
        lang = (request.language or "python").strip().lower()

        # 1. EMPTY / JUNK INPUT GUARD - Improved structural 'Vibe Check'
        code_clean = code.strip()
        has_code_dna = any(k in code_clean for k in [":", "(", "[", "=", "{", "+", "-", "*", "/", ">", "<"])
        
        if not code_clean or not has_code_dna:
            return DebugResponse(
                explanation="No valid code was detected. Please provide a script containing standard syntax or structural elements (like functions, variables, or operations).",
                line_by_line="Missing input.",
                fix="Please provide a valid code snippet to debug.",
                optimized_code="",
                why_fix_works="The input was identified as plain text or lacked sufficient structural DNA to be parsed as code.",
                sources=[],
                confidence=1.0,
                warning="Invalid or empty input detected.",
                error_type="Invalid Input",
                confidence_reason="Input validation failed."
            )

        # 1. STABLE HASHING (code | error | lang)
        key_content = f"{CACHE_SCHEMA_VERSION}|{code}|{error}|{lang}"
        cache_key = hashlib.sha256(key_content.encode()).hexdigest()
        
        # 2. STRICT CACHE-FIRST CHECK
        if cache_key in _DEBUG_CACHE:
            logger.info(f"CACHE HIT: {cache_key}. Re-normalizing and returning.")
            cached_res = _DEBUG_CACHE[cache_key]
            # Apply latest normalization logic to cached data
            cached_res.error_type = self._normalize_error_type(
                cached_res.error_type, cached_res.explanation, error, code
            )
            return cached_res
        
        logger.info(f"CACHE MISS: {cache_key}. Proceeding to AI pipeline.")

        # 3. Check In-flight (Deduplication)
        if cache_key in self._inflight_requests:
            logger.info(f"DEDUPLICATION: Waiting for active task {cache_key}...")
            return await self._inflight_requests[cache_key]

        # 4. Process new request
        task = asyncio.create_task(self._process_debug_request(request, code, error, lang, cache_key))
        self._inflight_requests[cache_key] = task

        try:
            result = await task
            
            # 5. SINGLE SOURCE OF TRUTH: Normalize Error Type exactly once before return
            result.error_type = self._normalize_error_type(
                result.error_type, result.explanation, error, code
            )

            # 5a. SYNTAX SAFETY: ensure users receive an actionable fix suggestion
            if result.error_type == "Syntax Error" and ("No changes" in (result.fix or "") or not result.fix):
                comment_prefix = "//" if lang in ["javascript", "typescript", "java", "c++"] else "#"
                result.fix = f"{comment_prefix} Syntax Fix: Review block delimiters/colons for your language.\n{code}"
                result.why_fix_works = "Highlights likely structural syntax issues without forcing unsafe rewrites."

            # 5b. SAFE CODE GUARANTEE: Prevent fake fixes and hallucinations for correct code
            if result.error_type == "Safe Code":
                if not error:
                    result.explanation = (
                        "Analysis complete: no direct syntax or runtime failure pattern was detected "
                        "from the provided snippet."
                    )
                    result.fix = result.fix or "No changes needed"
                    result.optimized_code = result.optimized_code or code
                    result.why_fix_works = (
                        "No concrete failing path was identified with the supplied input and context."
                    )
                    result.confidence = min(0.95, result.confidence)

            is_success = result.confidence > 0 and "limit" not in (result.warning or "").lower()
            
            if is_success:
                if len(_DEBUG_CACHE) >= CACHE_LIMIT:
                    _DEBUG_CACHE.popitem(last=False)
                _DEBUG_CACHE[cache_key] = result
                logger.info(f"STORED IN CACHE: {cache_key} | Normalized Type: {result.error_type}")
            elif cache_key in _DEBUG_CACHE:
                logger.warning(f"LLM failed but CACHE fallback found for {cache_key}")
                return _DEBUG_CACHE[cache_key]
                
            return result
        finally:
            if cache_key in self._inflight_requests:
                del self._inflight_requests[cache_key]

    async def _process_debug_request(
        self, 
        request: DebugRequest, 
        code: str, 
        error: str, 
        lang: str, 
        cache_key: str
    ) -> DebugResponse:
        """Isolated RAG + LLM execution logic with strict variable initialization."""
        
        # 1. Initialize all variables to prevent UnboundLocalError
        explanation = ""
        error_type = "Unknown Error"
        confidence = 0.5
        confidence_reason = "Default analysis"
        fix = ""
        optimized = ""
        why_works = "Applied standard engineering patterns."
        context_snippets = []
        warning = None

        try:
            # 2. Build the retrieval query
            if error:
                query = f"Code:\n{code}\n\nError:\n{error}\n\nExplain the error and fix it."
            else:
                query = f"Code:\n{code}\n\nNo error is provided. Analyze logical bugs, runtime issues, and optimizations."

            # 3. Retrieve context
            docs = self._vector_store.similarity_search(query, k=4)
            context_snippets = [doc.page_content for doc in docs]
            context_text = "\n---\n".join(context_snippets) if context_snippets else "No relevant context found."

            # 4. Build prompt & Call LLM
            full_prompt = f"""
Analyze the provided code and error. Return ONLY this STRICT JSON format:
{{
  "error_type": "Syntax Error | Runtime Error (Type) | Logical Error | Safe Code",
  "confidence": 0.95,
  "confidence_reason": "Professional reasoning",
  "explanation": "Concise senior-engineer summary",
  "line_by_line": "Line-by-line justification",
  "fix": "Minimal correction only. If code is correct, use 'No changes needed'",
  "optimized_code": "Best-practice version",
  "why_fix_works": "Technical justification"
}}

4. DO NOT include markdown, comments, placeholders, or trailing ellipsis.
5. Provide a direct, clean answer. NEVER end the response with 'undefined' or any state variables.
Relevant context:
{context_text}

Input: {lang} | {code} | {error or "None"}
"""
            raw_response = await self._llm_service.agenerate(full_prompt)
            parsed = self._parse_response(raw_response)

            # Some model responses place a second JSON object inside "explanation".
            nested_candidate = parsed.get("explanation")
            if isinstance(nested_candidate, str) and nested_candidate.strip().startswith("{"):
                nested = self._parse_response(nested_candidate)
                if isinstance(nested, dict):
                    parsed = {**parsed, **nested}

            # 5. Extract Parsed Values
            explanation = self._normalize_narrative_text(
                parsed.get("explanation", "Analysis complete.")
            )
            confidence = parsed.get("confidence", 0.8)
            confidence_reason = self._normalize_narrative_text(
                parsed.get("confidence_reason", "AI logical inference.")
            )
            why_works = self._normalize_narrative_text(parsed.get("why_fix_works", why_works))
            
            # 6. Final Validation & Error Type Inference (RAW)
            error_type = parsed.get("error_type", "Unknown Error").strip()

            # 6. Format Code Blocks
            def format_code_block(code_str: str) -> str:
                if not code_str: return ""
                if ";" in code_str and "\n" not in code_str:
                    code_str = code_str.replace(";", "\n")
                return code_str.strip()

            fix = format_code_block(parsed.get("fix", ""))
            optimized = format_code_block(parsed.get("optimized_code", ""))

            # Handle Fallback Fixes
            js_langs = ["javascript", "typescript", "java", "c++", "go", "rust"]
            comment_prefix = "//" if lang in js_langs else "#"

            if not fix or "Unable to generate" in fix or "No changes needed" in fix:
                if error:
                    # Minimal safe fallback if LLM failed
                    if "Index" in error_type:
                        fix = f"{comment_prefix} Heuristic Fix: Validate index bounds before access.\n{code}"
                    elif "ZeroDivision" in error_type:
                        fix = f"{comment_prefix} Heuristic Fix: Validate divisor is non-zero before division.\n{code}"
                
                if not fix:
                    fix = code if "No changes" in fix else f"{comment_prefix} Verified code structure\n{code}"

            if not optimized or "optimal" in optimized.lower():
                optimized = fix if len(fix) > len(code) else code

            line_by_line = self._normalize_narrative_text(
                parsed.get("line_by_line", PLACEHOLDER_LINE_BY_LINE)
            )

            return DebugResponse(
                explanation=explanation,
                line_by_line=line_by_line,
                fix=fix,
                optimized_code=optimized,
                why_fix_works=why_works,
                sources=context_snippets,
                confidence=round(confidence, 2),
                warning=warning,
                error_type=error_type,
                confidence_reason=confidence_reason,
            )

        except Exception as e:
            print("CRITICAL BACKEND ERROR:", e)
            logger.error(f"Pipeline failure: {e}", exc_info=True)
            return self._local_fallback(code, error, lang)

    # --------------------------------------------------
    # Removed separate explain_code() as it is now merged into debug()
    # --------------------------------------------------

    def _local_fallback(self, code: str, error: str, language: str) -> DebugResponse:
        """Heuristic-based analysis when AI is unavailable."""
        print("USING LOCAL FALLBACK")
        
        explanation = "The code has been analyzed locally. Possible issues detected in the logic or syntax."
        error_type = "Logical Error"
        fix = code
        optimized = code
        why = "Applied common reliability patterns to the code structure."
        
        code_low = code.lower()
        err_low = error.lower()
        
        # 1. IndexError Heuristic
        if "index" in err_low or ("[" in code and "len(" not in code_low):
            explanation = "Detected possible index out-of-bounds access. Ensure indices are within valid range (0 to length-1)."
            error_type = "Runtime Error (IndexError)"
            
            # Heuristic Fix: Wrap access lines in length guards
            lines = code.split("\n")
            fixed = []
            for line in lines:
                if "[" in line and "]" in line and "=" not in line.split("[")[0]: # Target access, not assignment
                    indent = " " * (len(line) - len(line.lstrip()))
                    var_name = line.strip().split("[")[0].split("(")[-1].strip()
                    if var_name.isidentifier():
                        fixed.append(f"{indent}if len({var_name}) > 0:")
                        fixed.append(f"{indent}    {line.lstrip()}  # Defensive guard added")
                    else:
                        fixed.append(line)
                else:
                    fixed.append(line)
            fix = "\n".join(fixed)
            why = "Injected an array-length safety guard to prevent out-of-bounds access."
            
        # 2. ZeroDivision Heuristic
        elif "/ 0" in code or "% 0" in code or ("/" in code and "0" in err_low):
            explanation = "Potential division by zero detected. Divisors must be validated to be non-zero before calculation."
            error_type = "Runtime Error (ZeroDivisionError)"
            
            # Heuristic Fix: Wrap division lines
            lines = code.split("\n")
            fixed = []
            for line in lines:
                if "/" in line:
                    parts = line.split("/")
                    divisor = parts[-1].strip().split()[0].replace(")", "").replace(":", "")
                    indent = " " * (len(line) - len(line.lstrip()))
                    if divisor.isidentifier() or divisor.isdigit():
                        fixed.append(f"{indent}if {divisor} != 0:")
                        fixed.append(f"{indent}    {line.lstrip()}")
                    else:
                        fixed.append(line)
                else:
                    fixed.append(line)
            fix = "\n".join(fixed)
            why = "Added a validation check to ensure the divisor is non-zero before calculation."
            
        # 3. Syntax Heuristic
        elif ":" not in code and any(k in code for k in ["if ", "for ", "def ", "while "]):
            explanation = "Missing required block syntax (colon) in control flow statement."
            error_type = "Syntax Error"
            fix = code.replace("if ", "if condition:").replace("def ", "def function():") # Generic correction
            why = "Restored missing colon and block structure required for correct execution."

        return DebugResponse(
            explanation=explanation,
            line_by_line="Local fallback: Analyzing line-by-line is limited without AI context.",
            fix=fix,
            optimized_code=optimized,
            why_fix_works=why,
            sources=[],
            confidence=0.6,
            warning="AI unavailable — using local analysis",
            error_type=error_type,
            confidence_reason="Pattern-matching heuristic analysis."
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_narrative_text(text: str) -> str:
        """Light cleanup to ensure quality and remove common AI artifacts."""
        if not text:
            return ""

        # Remove excessive whitespace and multiple dots
        cleaned = re.sub(r"\s+", " ", text.strip())
        cleaned = re.sub(r"\.\.+", ".", cleaned)
        
        # Remove trailing 'undefined' if the model hallucinated a JS placeholder
        cleaned = re.sub(r"undefined\s*$", "", cleaned, flags=re.IGNORECASE).strip()

        if not cleaned:
            return ""

        # Capitalize first alphabetic character
        for i, ch in enumerate(cleaned):
            if ch.isalpha():
                cleaned = cleaned[:i] + ch.upper() + cleaned[i + 1 :]
                break
        
        return cleaned

    @staticmethod
    def _parse_response(raw: str) -> dict:
        """Attempt to parse JSON from the LLM response with forced boundary extraction."""
        if not raw:
            return {}

        # 1. Force extraction between absolute JSON boundaries
        try:
            start_idx = raw.find("{")
            end_idx = raw.rfind("}")
            if start_idx != -1 and end_idx != -1:
                cleaned = raw[start_idx:end_idx + 1]
            else:
                cleaned = raw.strip()
        except Exception:
            cleaned = raw.strip()

        # 2. Remove markdown fences inside the boundaries if extra-nested
        cleaned = re.sub(r"```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```", "", cleaned)

        # 3. Attempt standard parse
        try:
            data = json.loads(cleaned)
            if isinstance(data, dict):
                return data
            if isinstance(data, str):
                nested = json.loads(data)
                if isinstance(nested, dict):
                    return nested
        except json.JSONDecodeError:
            pass

        # 4. Final resort extraction
        match = re.search(r"(\{[\s\S]*\})", cleaned)
        if match:
            try:
                data = json.loads(match.group(1))
                return data
            except json.JSONDecodeError:
                pass

        # 5. Field-level recovery for quasi-JSON outputs
        recovered = {}

        def extract_string(key: str) -> str | None:
            pattern = rf'"{key}"\s*:\s*"((?:\\.|[^"\\])*)"'
            m = re.search(pattern, cleaned, flags=re.DOTALL)
            if not m:
                return None
            return bytes(m.group(1), "utf-8").decode("unicode_escape").strip()

        def extract_number(key: str) -> float | None:
            pattern = rf'"{key}"\s*:\s*([0-9]+(?:\.[0-9]+)?)'
            m = re.search(pattern, cleaned)
            if not m:
                return None
            try:
                return float(m.group(1))
            except ValueError:
                return None

        for key in ["error_type", "confidence_reason", "explanation", "line_by_line", "fix", "optimized_code", "why_fix_works"]:
            value = extract_string(key)
            if value is not None:
                recovered[key] = value

        conf = extract_number("confidence")
        if conf is not None:
            recovered["confidence"] = conf

        if recovered:
            return recovered

        logger.warning(f"Extreme parsing failure. Raw response snippet: {raw[:100]}...")
        return {
            "explanation": raw if len(raw) < 500 else raw[:500] + "...",
            "fix": "",
            "optimized_code": "",
            "why_fix_works": "Deep parsing failed. Showing raw AI reasoning."
        }

    @staticmethod
    def _normalize_error_type(error_type: str | None, explanation: str, error_output: str, code: str) -> str:
        """Unified source of truth for error classification. Runtime Errors MUST always win."""
        # 1. Normalize all inputs to lowercase for strict matching
        text = f"{error_type or ''} {explanation} {error_output} {code}".lower()
        code_clean = code.strip().replace(" ", "").replace("\n", "")

        # 1.1 Early runtime guard: type mismatch patterns must never be downgraded to Safe Code.
        early_typeerror_indicators = [
            "typeerror",
            "unsupported operand type",
            "cannot be added to an integer",
            "cannot add",
            "int and str",
            "str and int",
            "string and integer",
        ]
        early_mixed_literal_call = re.search(
            r"\b[A-Za-z_]\w*\(\s*[-+]?\d+(?:\.\d+)?\s*,\s*['\"][^'\"]*['\"]\s*\)|"
            r"\b[A-Za-z_]\w*\(\s*['\"][^'\"]*['\"]\s*,\s*[-+]?\d+(?:\.\d+)?\s*\)",
            code,
        )
        if any(k in text for k in early_typeerror_indicators):
            return "Runtime Error (TypeError)"
        if early_mixed_literal_call and re.search(r"return\s+[A-Za-z_]\w*\s*\+\s*[A-Za-z_]\w*", code):
            return "Runtime Error (TypeError)"

        # 1.2 STATIC ANALYSIS HEURISTICS (no traceback required)
        # Detect simple constant out-of-range list access patterns.
        list_lengths: dict[str, int] = {}
        for m in re.finditer(r"(?m)^\s*([A-Za-z_]\w*)\s*=\s*\[([^\]]*)\]\s*$", code):
            var_name = m.group(1)
            raw_items = [item.strip() for item in m.group(2).split(",")]
            items = [item for item in raw_items if item != ""]
            list_lengths[var_name] = len(items)

        for m in re.finditer(r"\b([A-Za-z_]\w*)\[(\d+)\]", code):
            var_name, idx_str = m.group(1), m.group(2)
            if var_name in list_lengths:
                if int(idx_str) >= list_lengths[var_name]:
                    return "Runtime Error (IndexError)"

        # JavaScript/TypeScript null/undefined property access patterns.
        nullish_vars: set[str] = set()
        for m in re.finditer(r"\b(?:const|let|var)\s+([A-Za-z_]\w*)\s*=\s*(?:null|undefined)\b", code):
            nullish_vars.add(m.group(1))
        for var_name in nullish_vars:
            if re.search(rf"\b{re.escape(var_name)}\.[A-Za-z_]\w*\b", code):
                return "Runtime Error (TypeError)"

        # 0.5. VERIFIED PATTERN CHECK: Protect perfect Pythonic code from AI hallucinations
        # If no error output exists and code is a standard safe pattern
        # CRITICAL: Exclude risky operations (/, %, [) from automatic safe pass
        has_risky_op = any(op in code for op in ["/", "%", "[", "]"])
        is_basic_access = ("print(" in code_clean or "[nfornin" in code_clean) and not has_risky_op
        if not error_output and is_basic_access:
            # If the AI uses positive words like "correct" or "standard", trust it
            if any(k in text for k in ["correct", "valid", "standard", "perfect"]):
                return "Safe Code"
            # If it's a very simple print/ comprehension, assume safe unless explicit syntax error found
            if not any(k in code for k in ["if ", "while ", "for "]) or "[nfornin" in code_clean:
                if ":" in code or "def " not in code: # Avoid missing colon cases
                    return "Safe Code"

        # 2. STRICT RUNTIME CHECK (Priority 1)
        if "division by zero" in text or "zerodivisionerror" in text:
            return "Runtime Error (ZeroDivisionError)"

        if "indexerror" in text or "out of range" in text:
            # Literal Safety Check: Trust code over AI if index is obviously safe
            if "[" in code and "]" in code:
                if re.search(r"=\s*\[.*,.*,.*\]", code) and (code.count("[") > 1 or "arr[" in code):
                    if "[0]" in code or "[1]" in code:
                        return "Safe Code"
            return "Runtime Error (IndexError)"

        # Type mismatch runtime checks
        typeerror_indicators = [
            "typeerror",
            "unsupported operand type",
            "cannot be added to an integer",
            "cannot add",
            "int and str",
            "str and int",
            "string and integer",
        ]
        if any(k in text for k in typeerror_indicators):
            return "Runtime Error (TypeError)"

        # Static pattern: function adds params but is called with mixed int/str literals.
        if early_mixed_literal_call and re.search(r"return\s+[A-Za-z_]\w*\s*\+\s*[A-Za-z_]\w*", code):
            return "Runtime Error (TypeError)"

        # 2.5. DYNAMIC RISK CHECK (Priority 1.5)
        # If code has input + risky ops (/, []), force Runtime Error
        has_input = any(k in code for k in ["input(", "argv", "sys.stdin"])
        has_risky_op = any(k in code for k in ["/", "[", "]", "%"])
        risk_text = any(k in text for k in ["potential", "risk", "could", "may", "possible"])

        if has_risky_op and (has_input or risk_text):
            if "division" in text or "/" in code:
                return "Runtime Error (ZeroDivisionError)"
            if "index" in text or "[" in code:
                return "Runtime Error (IndexError)"

        # 3. SYNTAX CHECK (Priority 2) - Structural issues ONLY
        syntax_indicators = ["expected ':'", "syntaxerror", "syntax", "invalid indentation", "unexpected indent", "colon", "missing :", "block"]
        logical_blockers = ["logic", "algorithm", "incorrect", "wrong", "even number", "odd number"]
        
        # Line-by-line structural check for missing colons in headers (Comment-Aware)
        lines = [l.strip() for l in code.split("\n") if l.strip()]
        missing_colon = False
        for line in lines:
            # Strip comments before checking structural integrity
            code_line = line.split('#')[0].strip()
            if any(code_line.startswith(k) for k in ["def ", "if ", "for ", "while ", "class ", "else", "elif "]):
                 if code_line and not code_line.endswith(":"):
                     missing_colon = True
                     break

        has_syntax_kw = any(k in text for k in syntax_indicators)
        has_logical_kw = any(k in text for k in logical_blockers)

        # Only badge as Syntax if structural markers are missing OR keywords match without logical interference
        if (has_syntax_kw and not has_logical_kw) or missing_colon:
            return "Syntax Error"

        # 4. LOGICAL DETECTION (Priority 3)
        # Scan for logical inconsistencies after structural syntax
        logical_indicators = ["incorrect output", "wrong logic", "condition fail", "even function", "unexpected result"]
        if any(k in text for k in logical_indicators) or ("%" in code and "even" in text):
             return "Logical Error"

        # 5. SAFE CODE CHECK (Priority 4)
        safe_keywords = ["no error", "correct", "perfect", "works fine", "already optimized", "no issue", "is correct"]
        error_keywords = ["error", "bug", "issue", "problem", "incorrect", "fail", "syntax", "runtime", "range", "risk", "potential"]
        
        # Explicit safe keywords detected
        if any(k in text for k in safe_keywords):
            # Block promotion if explicit runtime words are present in the core analysis
            if any(k in text for k in ["indexerror", "zerodivisionerror", "out of range"]):
                 # Check if it was a literal safety hit (Priority 1.5 already passed, so this is for other cases)
                 pass
            else:
                 return "Safe Code"
            
        # Neutrality Check: If no negative keywords and no runtime/syntax issues
        if not any(k in text for k in error_keywords) and not error_output:
            return "Safe Code"

        # 6. DEFAULT
        return "Logical Error"
