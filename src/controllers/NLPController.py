import json  # noqa: N999
import logging

from controllers.BaseController import BaseController
from models.db_schemes import DataChunk, Project
from stores.llm.LLMEnums import DocumentTypeEnum
from stores.llm.LLMProviders import CoHereProvider, OpenAiProvider
from stores.llm.templates.template_parser import TemplateParser
from stores.vectordb.db_provider import QdrantProvider


class NLPController(BaseController):
    def __init__(
        self,
        generation_client,
        embedding_client: OpenAiProvider,
        vectorDB_client: QdrantProvider,
        template_parser: TemplateParser,
    ):
        super().__init__()
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.vectorDB_client = vectorDB_client
        self.template_parser = template_parser

        self.logger = logging.getLogger(__name__)

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()

    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        print(self.vectorDB_client.list_all_collection())
        collection_info = self.vectorDB_client.get_collection_info(
            collection_name=collection_name
        )
        return json.loads(json.dumps(collection_info, default=lambda x: x.__dict__))

    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectorDB_client.delete_collection(collection_name)

    def index_into_vector_db(
        self,
        project: Project,
        chunks: list[DataChunk],
        chunk_id: list[int],
        do_reset: bool = False,
    ):
        collection_name = self.create_collection_name(project_id=project.project_id)
        texts = [chunk.chunk_text for chunk in chunks]
        metadata = [chunk.chunk_metadata for chunk in chunks]
        vectors = [
            self.embedding_client.generate_embedding(
                text=text, document_type=DocumentTypeEnum.DOCUMENT.value
            )
            for text in texts
        ]

        # 3 : indexing in vdb
        self.vectorDB_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,  # type: ignore
            do_reset=do_reset,
        )

        self.vectorDB_client.insert_many(
            collection_name,
            texts=texts,
            vectors=vectors,
            metadata=metadata,
            record_ids=chunk_id,
        )
        return True

    def search_vector_db_collection(self, project: Project, text: str, limit: int = 5):
        # step1: get collection name

        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2:get text embedding vector

        vector = self.embedding_client.generate_embedding(
            text, document_type=DocumentTypeEnum.QUERY.value
        )
        if not vector or len(vector) == 0:
            return False

        # step3: do semantic search

        results = self.vectorDB_client.search_by_vector(
            collection_name, vector=vector, limit=limit
        )
        if not results:
            return False

        return results

    def answer_question_rag(self, project: Project, query: str, limit: int = 10):
        answer , full_prompt , chat_history = None , None , None
        # step 1 : retrieve related documents

        retrieve_document = self.search_vector_db_collection(
            project=project, text=query, limit=limit
        )
        if not retrieve_document or len(retrieve_document)==0:
            return answer , full_prompt , chat_history

        # step 2 : construct LLM prompt (locales (reference text )) (system , document , footer)

        system_prompt = self.template_parser.get("rag", "system_prompt")

        doc_prompt = [
            self.template_parser.get(
                "rag", "document_prompt", {"doc_num": idx + 1, "chunk_text": doc.text}
            )
            for idx, doc in enumerate(retrieve_document)
        ]
        doc_prompt = "\n".join(doc_prompt)  # type: ignore

        footer_prompt = self.template_parser.get("rag", "footer_prompt" , {"query":query})

        # step 3 : Construct Generation Client Prompts

        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt, role=self.generation_client.enums.SYSTEM.value
            )
        ]
        full_prompt = "\n\n".join([doc_prompt, footer_prompt]) # pyright: ignore[reportCallIssue]

        # step 4 : Retrieve the Answer
        answer = self.generation_client.generate_text(prompt= full_prompt , chat_history=chat_history)

        return answer , full_prompt , chat_history 
