from motor.motor_asyncio import AsyncIOMotorDatabase

from helpers.config import Settings, get_settings


class BaseDataModel():
    def __init__(self,db_client: object):
        self.app_settings : Settings = get_settings()
        self.db_client: AsyncIOMotorDatabase = db_client  # type: ignore[assignment]