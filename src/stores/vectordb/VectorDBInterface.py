from abc import ABC, abstractmethod


class VectorDBInterface(ABC):

    @abstractmethod
    def connect(self):
        """Establishes a connection to a resource.

        This is an abstract method that must be implemented by subclasses.

        Raises:
            NotImplementedError: If the method is not overridden by a subclass.
        """
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnects from the current database or service connection."""
        ...

    @abstractmethod
    def is_collection_existed(self, collection_name: str) -> bool:
        """Checks if a collection exists in the database.

        Args:
            collection_name: Name of the collection to check.

        Returns:
            True if the collection exists, False otherwise.
        """
        ...

    @abstractmethod
    def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool | None = None
    ):
        """Creates a new collection with specified embedding size.

        Args:
            collection_name: Name of the collection to create.
            embedding_size: Dimension of embeddings to be stored in the collection.
            do_reset: If True, resets an existing collection. Defaults to None.

        Returns:
            None

        Raises:
            ValueError: If collection already exists and do_reset is False or None.
        """

    pass

    @abstractmethod
    def delete_collection(self, collection_name: str): ...

    """Deletes a specified collection
    Args :
        collection_name :Name of the collection delete .
    Returns :
        NoneRaises :KeyError If the collection does not exist."""
    ...

    @abstractmethod
    def get_collection_info(self, collection_name: str): ...

    @abstractmethod
    def list_all_collection(self): ...

    # the vector point ( record )
    @abstractmethod
    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        record_id: str | None = None,
        metadata: dict | None = None,
    ): ...

    @abstractmethod
    def insert_many(
        self,
        collection_name: str,
        texts: list[str],
        vectors: list,
        metadata: list | None = None,
        record_id: list | None = None,
        batch_size: int = 50,
    ): ...

    @abstractmethod
    def search_by_vector(self, collection_name: str, vector: list, limit: int): ...
