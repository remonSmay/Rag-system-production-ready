from controllers.BaseController import BaseController
from controllers.ProjectController import ProjectController
from models import ProcessTypeEnum
import os
from typing import Any

from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ProcessController(BaseController):
    def __init__(self, project_id: str):
        """Load and preprocess project files for downstream processing.

        This controller centralizes file-loading and text-splitting responsibilities
        for a given project. It locates files within a project's storage, selects
        the appropriate loader based on file extension (e.g., plain text or PDF),
        loads the raw document objects using LangChain-compatible loaders, and
        splits the loaded text into smaller chunks suitable for embedding,
        indexing, or other downstream NLP tasks.

        Why:
        - Keeps file ingestion logic in one place so other controllers and
            ingestion pipelines can reuse consistent behavior.
        - Encapsulates file-type handling and text-splitting details, making it
            simpler to support new file types or change chunking strategy later.

        Public methods:
        - `get_file_extension(file_name)`: return the file extension for a name.
        - `get_file_loader(file_id)`: return a loader instance for supported
            extensions or `None` when unsupported.
        - `get_file_content(file_id)`: load and return a list of document objects
            from the file (or an empty list if no loader is available).
        - `process_file_content(file_id, content, chunk_size, chunk_overlap)`:
            split loaded documents into chunked documents using a
            `RecursiveCharacterTextSplitter`.
        """
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self, file_name: str) -> str:
        """get the extension of file for know the loader for use in files

        Args:
            file_name (str): file name

        Returns:
            (str) : the extension
        """

        return os.path.splitext(file_name)[-1].lower()

    def get_file_loader(self, file_id: str) -> TextLoader | PyMuPDFLoader | None:
        """get_file_loader : process loader over the file by file extension

        Args:
            file_id (str): file id
        Returns:
            _type_: mode of loader and file
        """

        file_ext = self.get_file_extension(file_name=file_id)
        file_path = os.path.join(self.project_path, file_id)
        if not os.path.exists(file_path):
            return None

        if file_ext == ProcessTypeEnum.TXT.value:
            return TextLoader(file_path=file_path, encoding="utf-8")

        elif file_ext == ProcessTypeEnum.PDF.value:

            return PyMuPDFLoader(file_path)

        else:
            return None

    def get_file_content(self, file_id: str) -> list[Any] | None:
        """Retrieve the content of a stored file by delegating to its configured loader.

        file_id (str): Unique identifier associated with the target file.

        list[Any] | None: Loaded document list when available, otherwise None.
        """
        loader = self.get_file_loader(file_id)
        if loader is None:
            return None

        return loader.load()

    def process_file_content(
        self,
        file_id: str,
        content: list,
        chunk_size: int = 100,
        overlap_size: int = 20,
    ) -> list:
        """process_file_content : process the file content by splitting it into chunks

        Args:
            file_id (str): file id

        Returns:
            list: list of chunks
        """
        if not content:
            return []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )

        file_content_text = [rec.page_content for rec in content]

        file_content_metadata = [rec.metadata for rec in content]

        chunks = text_splitter.create_documents(
            file_content_text, file_content_metadata
        )

        return chunks
