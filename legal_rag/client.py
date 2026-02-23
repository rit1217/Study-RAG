import os

from google import genai
from google.genai import types

from legal_rag.prompts import load_prompt


class LegalRAGClient:
    """Gemini-based Legal RAG client wrapping file stores, document management, and queries."""

    def __init__(self, api_key=None, prompts_dir="./prompts"):
        """Initialize the client.

        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
            prompts_dir: Root directory for prompt template files.
        """
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.prompts_dir = prompts_dir

    # ── Prompt loading ──────────────────────────────────────────────

    def load_prompt(self, agent_type, model, name, version="v02"):
        """Load a prompt template from the prompts directory."""
        return load_prompt(agent_type, model, name, version, self.prompts_dir)

    # ── File Store management ───────────────────────────────────────

    def list_file_stores(self):
        """List all File Search stores with their documents.

        Returns:
            List of file search store objects.
        """
        stores = list(self.client.file_search_stores.list())
        for fs in stores:
            docs = list(self.client.file_search_stores.documents.list(parent=fs.name))
            print(f"{fs.display_name} ({fs.name}) — {len(docs)} documents")
            for doc in docs:
                print(f"  - {doc.display_name} [{doc.name}]")
            print()
        return stores

    def create_file_store(self, display_name):
        """Create a new File Search store.

        Returns:
            Created file search store object.
        """
        store = self.client.file_search_stores.create(config={"display_name": display_name})
        print(f"Created store: {store.display_name} ({store.name})")
        return store

    def delete_file_store(self, file_search_store_name, force=True):
        """Delete a File Search store."""
        self.client.file_search_stores.delete(name=file_search_store_name, config={"force": force})
        print(f"Deleted store: {file_search_store_name}")

    # ── Document management ─────────────────────────────────────────

    def list_documents(self, file_search_store_name):
        """List all documents in a File Search store.

        Returns:
            List of document objects.
        """
        docs = list(self.client.file_search_stores.documents.list(parent=file_search_store_name))
        for doc in docs:
            print(f"  - {doc.display_name} [{doc.name}]")
        return docs

    def store_file(self, file_name, file_search_store_name, file_path="./documents/KKP/LNC", metadata=None):
        """Upload a file to a Gemini File Search store.

        Args:
            file_name: Relative file path within file_path directory.
            file_search_store_name: Target File Search store name.
            file_path: Base directory for files.
            metadata: List of metadata dicts with 'key' and value fields.

        Returns:
            Upload operation object.
        """
        full_file_path = os.path.join(file_path, file_name)
        print(f"Storing File: {full_file_path}")

        config = {"display_name": file_name}
        if metadata:
            print(metadata)
            config["custom_metadata"] = metadata

        operation = self.client.file_search_stores.upload_to_file_search_store(
            file=full_file_path,
            file_search_store_name=file_search_store_name,
            config=config,
        )
        return operation

    def delete_document(self, document_name, force=True):
        """Delete a document from a File Search store.

        Args:
            document_name: Full document resource name
                (e.g. "fileSearchStores/.../documents/...").
            force: Force delete even if document is referenced.
        """
        self.client.file_search_stores.documents.delete(name=document_name, config={"force": force})
        print(f"Deleted: {document_name}")

    # ── Query ───────────────────────────────────────────────────────

    def ask(self, question, file_store_name_list, prompt_template=None, with_grounding=True, gemini_model="gemini-3-flash-preview"):
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
            prompt_template = self.load_prompt("legal_qa", gemini_model, "legal_qa")

        def _generate():
            return self.client.models.generate_content(
                model=gemini_model,
                contents=prompt_template.format(question=question),
                config=types.GenerateContentConfig(
                    temperature=0.7,
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
