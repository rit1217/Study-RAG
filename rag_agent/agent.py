from google import genai
from google.genai import types

import os


class RAGClient:
    """Gemini-based Legal RAG client wrapping file stores, document management, and queries."""
    def __init__(self, api_key=None, prompts_dir="./skill_archive"):
        """Initialize the client.

        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
            prompts_dir: Root directory for prompt template files.
        """
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.prompts_dir = prompts_dir

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

    def store_file(self, file_name, file_search_store_name, file_path="./docs/KKP/LNC", metadata=None):
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

