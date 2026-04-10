"""
RAG (Retrieval-Augmented Generation) service.
Orchestrates: embed query → retrieve from FAISS → build prompt → call Groq → parse output.
"""

import json
import logging
import re

from app.models.schemas import DebugRequest, DebugResponse
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

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

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------
    async def debug(self, request: DebugRequest) -> DebugResponse:
        """Run the full RAG pipeline and return a DebugResponse."""

        error = request.error_message
        code = request.code

        # 1. Build the retrieval query and instructions from code + optional error
        if error and error.strip():
            query = f"""
Code:
{code}

Error:
{error}

Explain the error and fix it.
"""
        else:
            query = f"""
Code:
{code}

No error is provided.

Analyze the code deeply and:
1. Identify logical bugs
2. Detect possible runtime issues
3. Identify bad practices
4. Suggest fixes
5. Provide optimized version
"""

        # 2. Retrieve relevant context from FAISS
        docs = self._vector_store.similarity_search(query, k=4)
        context_snippets = [doc.page_content for doc in docs]
        context_text = "\n---\n".join(context_snippets) if context_snippets else "No relevant context found."

        logger.info(f"Retrieved {len(docs)} context documents from FAISS")

        # 3. Build the prompt
        full_prompt = f"""
You are an expert debugging assistant.

Analyze the code and return output in STRICT JSON format.

Code:
{code}

Error:
{error if error else "No error provided"}

Context:
{context_text}

---

Output format (STRICT JSON):

{{
"explanation": "...",
"fix": "...",
"optimized_code": "..."
}}

---

Rules:

* Always return all 3 fields
* "fix" must contain ONLY valid runnable code
* Do NOT include explanations inside "fix"
* If no fix is needed, return original code
* "optimized_code" must also be valid code
* Do NOT return anything outside JSON
* Wrap code inside plain text (no markdown like ```)
* "fix" must be properly formatted multi-line code
* Use correct indentation
* Do NOT compress multiple statements into one line
* Follow standard coding style
"""

        # 4. Call the LLM
        logger.info("Sending prompt to Groq LLM …")
        raw_response = await self._llm_service.agenerate(full_prompt)

        # 5. Parse structured output
        parsed = self._parse_response(raw_response)

        confidence = 0.9  # default high confidence
        if "error" in parsed.get("explanation", "").lower():
            confidence = 0.95
        if "maybe" in parsed.get("explanation", "").lower():
            confidence = 0.7

        def format_code_block(code_str: str) -> str:
            if ";" in code_str:
                code_str = code_str.replace(";", "\n")
            return code_str.strip()

        fix = format_code_block(parsed.get("fix", ""))
        optimized = format_code_block(parsed.get("optimized_code", ""))

        if not fix:
            fix = code  # fallback to original code

        if not optimized:
            optimized = code  # fallback to original code

        return DebugResponse(
            explanation=parsed.get("explanation", "No explanation generated."),
            fix=fix,
            optimized_code=optimized,
            sources=context_snippets,
            confidence=confidence,
        )

    async def explain_code(self, code: str, language: str):
        prompt = f"""
Code:
{code}

Explain this code line by line.

Output format:
Line 1: <explanation>
Line 2: <explanation>
Line 3: <explanation>

Rules:
* Each line must be explained separately
* Keep explanations simple and short
* Do not combine multiple lines
"""
        response = await self._llm_service.agenerate(prompt)
        return response

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_response(raw: str) -> dict:
        """Attempt to parse JSON from the LLM response, with fallback."""
        # Strip markdown code fences if the LLM wrapped the JSON
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM JSON — attempting regex extraction")

        # Fallback: try to find a JSON block anywhere in the response
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # Last resort: return the raw text as the explanation
        logger.error("Could not parse LLM output as JSON")
        return {
            "explanation": raw,
            "fix": "Unable to generate fix. See explanation.",
            "optimized_code": "Unable to generate optimized code. See explanation.",
        }
