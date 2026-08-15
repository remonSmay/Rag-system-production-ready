from fastapi import APIRouter , Depends
from helpers.config import get_settings , Settings 
base_router = APIRouter(prefix='/api/v1', tags=['api_v1'])

@base_router.get("/")

async def welcome(
    app_settings : Settings = Depends(get_settings)
    ):
    """
    This is the welcome path of the API. It returns a message saying "Hello World".
    """
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    app_file = app_settings.FILE_ALLOWED_TYPES
    return {
        "version": app_version,
        "app_name": app_name,
        "type_file":app_file
        }