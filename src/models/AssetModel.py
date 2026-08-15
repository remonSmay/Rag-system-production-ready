from bson import ObjectId  # noqa: N999
from motor.motor_asyncio import AsyncIOMotorDatabase  # noqa: F401

from models.BaseDataModel import BaseDataModel
from models.db_schemes import Asset

from .enums import DataBaseEnum


class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client = db_client)
        self.db_client : AsyncIOMotorDatabase = db_client
        self.collection = self.db_client[
            DataBaseEnum.COLLECTION_ASSET_NAME.value
        ]  # as a Table

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()

        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collections:

            self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]

            indexes = Asset.get_indexes()

            for index in indexes:
                await self.collection.create_index(
                    index["key"], name=index["name"], unique=index["unique"]
                )

    async def create_asset(self, asset: Asset):
        """
        Asynchronously insert an Asset into the collection.

        Parameters
        ----------
        asset : Asset
            The asset model to persist. It will be serialized with
            `model_dump(by_alias=True, exclude_unset=True)` before insertion.

        Returns
        -------
        pymongo.results.InsertOneResult
            The result returned by the `insert_one` operation.

        Side effects
        ------------
        - Sets `asset.id` to the inserted document's ObjectId (`result.inserted_id`).
        - Performs an asynchronous write to the database.

        Raises
        ------
        pymongo.errors.PyMongoError
            If the underlying database operation fails.

        Notes
        -----
        This coroutine must be awaited.
        """
        result = await self.collection.insert_one(
            asset.model_dump(by_alias=True, exclude_unset=True)
        )
        asset.id = result.inserted_id
        return asset

    async def get_all_project_assets(
        self, asset_project_id: str | ObjectId, asset_type: str
    ):
        records = await self.collection.find(
            {
                "asset_project_id": (
                    ObjectId(asset_project_id)
                    if isinstance(asset_project_id, str)
                    else asset_project_id
                ),
                "asset_type": asset_type,
            }
        ).to_list(length=None)

        return [Asset(**record) for record in records]

    async def get_asset_record(self, asset_project_id: str | ObjectId, asset_name: str):
        record = await self.collection.find_one(
            {
                "asset_project_id": (
                    ObjectId(asset_project_id)
                    if isinstance(asset_project_id, str)
                    else asset_project_id
                ),
                "asset_name": asset_name,
            }
        )
        if record:
            return Asset(**record)

        return None
