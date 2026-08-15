# the project model class is documented in BaseDataModel

from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnums import DataBaseEnum
from .db_schemes.project import Project


class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[  # type: ignore
            DataBaseEnum.COLLECTION_PROJECT_NAME.value
        ]  # as a Table (create the name collection with name COLLECTION_PROJECT_NAME)

    """
    async for any handling with motor (database)
    and await for any handling with asyncio (collection)
    """

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()

        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:

            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"], name=index["name"], unique=index["unique"]
                )

    async def create_project(self, project: Project):
        """create_project : create the document in db

        Returns:
            project: Project (model pydantic document)
        """
        record = await self.collection.insert_one(
            project.model_dump(by_alias=True, exclude_unset=True)
        )
        # record is a single document (doc (key , value))
        # returns a Python dictionary representation of the Project model instance

        project.id = record.inserted_id
        # gives the unique _id of the document you just inserted
        return project

    async def get_project_or_create_one(self, project_id: str):

        # find if the project exist
        # how (find_one db) (search by dict {project_id:project_id})
        # if none then create one
        record = await self.collection.find_one({"project_id": project_id})

        if record is None:
            project = Project(project_id=project_id)  # type: ignore
            project = await self.create_project(project)
            return project

        return Project(**record)

    async def get_all_project(self, page: int = 1, page_size: int = 10):
        # because load all page be mistake we want divide the total on pages
        # total documents
        # total pages
        # cursor
        total_documents = await self.collection.count_documents(
            {}
        )  # {} because we want all documents

        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1

        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)

        project = []
        async for document in cursor:
            project.append(Project(**document))
        return project
