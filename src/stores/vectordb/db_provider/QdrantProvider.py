from __future__ import annotations  # noqa: N999

import logging  # noqa: N999
from uuid import uuid4

from qdrant_client import QdrantClient, models

from models.db_schemes.DataChunk import RetrievedDocument

from ..VectorDBEnums import DistanceMethodEnums
from ..VectorDBInterface import VectorDBInterface


class QdrantProvider(VectorDBInterface):
    def __init__(self, path_db: str, distance_method: str):
        self.path_db = path_db
        self.distance_method = None

        self.client: QdrantClient

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = DistanceMethodEnums.COSINE.value
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = DistanceMethodEnums.DOT.value
        else:
            raise ValueError("the not found the distance method")
        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.path_db)

    def disconnect(self):
        return None

    def is_collection_existed(self, collection_name: str) -> bool:
        if getattr(self, "client", None) is None:
            self.logger.error("Qdrant client not initialized")
            return False
        try:
            return self.client.collection_exists(collection_name=collection_name)
        except Exception as e:
            self.logger.exception("error checking collection existence: %s", e)
            return False

    def get_collection_info(self, collection_name: str):
        """
        Retrieve information about a specific collection from the Qdrant database.

        Args:
            collection_name (str): The name of the collection to retrieve information for.

        Returns:
            Collection: A Collection object containing metadata and information about the
                    specified collection, or None if the collection does not exist or
                    an error occurs during retrieval.

        Raises:
            None: Exceptions are caught and logged; the method returns None on error.

        Note:
            - Returns None if the Qdrant client is not initialized.
            - Returns None if the specified collection does not exist.
            - Returns None if an exception occurs during collection retrieval.
        """
        if not self.client:
            self.logger.error("Qdrant client not initialized")
            return None
        try:
            collection = self.client.get_collection(collection_name)
        except Exception as e:
            self.logger.exception("can't get collection '%s': %s", collection_name, e)
            return None
        return collection

    def list_all_collection(self):
        if not self.client:
            self.logger.error("Qdrant client not initialized")
            return None
        try:
            collection = self.client.get_collections()
        except Exception as e:
            self.logger.exception("can't get collections '%s': %s", e)
            return None
        return collection

    def delete_collection(self, collection_name: str):
        if not self.client:
            self.logger.error("Qdrant client not initialized")
            return None
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name)
        return None

    def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ):
        if do_reset:
            _ = self.delete_collection(collection_name)
        if not self.client.collection_exists(collection_name):

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size, distance=self.distance_method  # type: ignore
                ),
            )
            print(f"Collection '{collection_name}' created successfully")
            return True
        return False

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: models.List,
        record_id: str | None = None,
        metadata: dict | None = None,
    ):

        if not self.is_collection_existed(collection_name):
            self.logger.error(
                f"can no insert new record to non-existed collection{collection_name}"
            )
            return False
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=record_id or str(uuid4()),
                        vector=vector,
                        payload={
                            "text": text,
                            "metadata": metadata or {},
                        },
                    )
                ],
            )
        except Exception as e:
            self.logger.error(f"can't insert vector {e}")
            return False
        return True

    def insert_many(
        self,
        collection_name: str,
        texts: list[str],
        vectors: list,
        metadata: list | None = None,
        record_ids: list | None = None,
        batch_size: int = 50,
    ):
        if not self.is_collection_existed(collection_name):
            self.logger.error(
                f"can no insert new record to non-existed collection{collection_name}"
            )
            return False
        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = list(range(0, len(texts)))

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_records_id = record_ids[i:batch_end]
            batch_records = [
                models.PointStruct(
                    id=batch_records_id[x],
                    vector=batch_vectors[x],
                    payload={"text": batch_texts[x], "metadata": batch_metadata[x]},
                )
                for x in range(len(batch_texts))
            ]

            try:
                self.client.upsert(
                    collection_name,
                    points=batch_records,
                )
            except Exception as e:
                self.logger.warning(f"cant's add the many points {e}")
                return False
        return True



    def search_by_vector(
        self, collection_name: str, vector: list[float], limit: int
    ) -> list[RetrievedDocument]:

        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit,
                with_payload=True,
            )
        except Exception as e:
            self.logger.exception(
                "error searching collection '%s': %s", collection_name, e  # noqa: TRY401
            )
            return []


        if not results or len(results)==0:
            return []



        return [
            RetrievedDocument(score= result.score , text= result.payload['text'] ) # type: ignore
            for result in results
        ]
