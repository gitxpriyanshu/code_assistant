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
SYSTEM_PROMPT = """You are an expert debugging assistant. Your job is to analyse the provided code and error, \
then return a structured JSON response with three fields:

1. **explanation** — A clear, concise explanation of *why* the error occurs.
2. **fix** — The corrected version of the code that resolves the error.
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

### Code
```
{code}
```

### Error
```
{error_message}
```

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

        # 1. Build the retrieval query from code + error
        query = f"{request.language} error: {request.error_message}\n\nCode:\n{request.code}"

        # 2. Retrieve relevant context from FAISS
        docs = self._vector_store.similarity_search(query, k=4)
        context_snippets = [doc.page_content for doc in docs]
        context_text = "\n---\n".join(context_snippets) if context_snippets else "No relevant context found."

        logger.info(f"Retrieved {len(docs)} context documents from FAISS")

        # 3. Build the prompt
        user_prompt = USER_PROMPT_TEMPLATE.format(
            language=request.language,
            code=request.code,
            error_message=request.error_message,
            context=context_text,
        )

        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

        # 4. Call the LLM
        logger.info("Sending prompt to Groq LLM …")
        raw_response = await self._llm_service.agenerate(full_prompt)

        # 5. Parse structured output
        parsed = self._parse_response(raw_response)

        return DebugResponse(
            explanation=parsed.get("explanation", "Unable to generate explanation."),
            fix=parsed.get("fix", request.code),
            optimized_code=parsed.get("optimized_code", request.code),
            relevant_context=context_snippets,
        )

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
