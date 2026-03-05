import os

from google import genai
from google.genai import types

from rag_agent import RAGClient
from skill import load_prompt


class LegalRAGClient(RAGClient):
    def __init__(self, api_key=None, prompts_dir="./instruction_archive"):
        super().__init__(api_key=api_key, prompts_dir=prompts_dir)

    # ── Prompt loading ──────────────────────────────────────────────
    def load_prompt(self, agent_type, name, version="v02"):
        """Load a prompt template from the prompts directory."""

        return load_prompt(agent_type, name, version, self.prompts_dir)

    # ── Query ───────────────────────────────────────────────────────

    def ask(self, question, file_store_name_list, temperature=0.5, prompt_template=None, with_grounding=True, gemini_model="gemini-3-flash-preview"):
        """Query Gemini with legal RAG using File Search stores.

        Args:
            question: Legal question text.
            file_store_name_list: List of Gemini File Search store names.
            prompt_template: Prompt string with {question} placeholder.
                If None, auto-loads via load_prompt().
            with_grounding: If True, append grounding source citations.
            gemini_model: Gemini model ID.

        Returns:
            Tuple of (response object, response text string).
        """
        if prompt_template is None:
            prompt_template = self.load_prompt("legal_qa", "legal_qa")

        def _generate():
            return self.client.models.generate_content(
                model=gemini_model,
                contents=prompt_template.format(question=question),
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=file_store_name_list,
                            )
                        )
                    ],
                ),
            )

        response = _generate()

        grounding = response.candidates[0].grounding_metadata
        if not grounding:
            ground_txt = "No grounding sources found"
        else:
            sources = {c.retrieved_context.title for c in grounding.grounding_chunks}
            ground_txt = f"Sources: {sources}"

        if with_grounding:
            try:
                return response, response.text + "\n" + ground_txt
            except Exception:
                response = _generate()

        return response, response.text
