import logging
import os

import aiofiles
from fastapi import APIRouter, Depends, UploadFile, status

# why use Request for visible the app on here routing
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from controllers import DataController, ProcessController, ProjectController
from helpers.config import Settings, get_settings
from helpers.db import get_db
from models import ResponseStatus
from models.AssetModel import AssetModel
from models.ChunkModel import ChunkModel
from models.db_schemes.asset import Asset
from models.db_schemes.DataChunk import DataChunk
from models.enums.AssetTypeEnums import AssetTypeEnum
from models.ProjectModel import ProjectModel
from routes.schemes.data import ProcessRequest

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1,data"])


@data_router.post("/upload/{project_id}")
async def upload_file(
    project_id: str,
    file: UploadFile,
    db_client: AsyncIOMotorDatabase = Depends(get_db),
    app_settings: Settings = Depends(get_settings),
):

    project_model = await ProjectModel.create_instance(db_client=db_client)

    try:
        project = await project_model.get_project_or_create_one(project_id=project_id)
    except Exception as exc:
        logger.error("MongoDB error while ensuring project exists: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"signal": ResponseStatus.DATABASE_UNFOUND.value},
        )

    if project.id is None:
        logger.error(
            "Project created/retrieved without database id for project_id=%s",
            project_id,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": ResponseStatus.FILE_UPLOAD_FAILED.value},
        )

    is_valid, result_signal = DataController().validate_upload_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"signal": result_signal}
        )

    project_dir_path = ProjectController().get_project_path(project_id=project_id)

    file_path, file_id = DataController().get_unique_filepath(
        original_filename=file.filename, project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, "wb") as out_file:  # type: ignore
            while chunk := await file.read(size=app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await out_file.write(chunk)
    except Exception as e:
        logger.error(f"error while upload file : {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseStatus.FILE_UPLOAD_FAILED.value},
        )
    asset_model = await AssetModel.create_instance(db_client=db_client)

    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
        asset_config=None,  # Explicitly setting asset_config to None as it's optional and not provided here.
    )  # type: ignore

    asset_record = await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseStatus.FILE_UPLOAD_SUCCESS.value,
            "file_id": str(asset_record.id),
        },
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(
    project_id: str,
    process_request: ProcessRequest,
    db_client: AsyncIOMotorDatabase = Depends(get_db),
):

    chunk_size = (
        process_request.chunk_size if process_request.chunk_size is not None else 100
    )
    overlap_size = (
        process_request.overlap_size if process_request.overlap_size is not None else 20
    )
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=db_client
    )  # for handling with database (create the collection ) & It ensures/creates the project's collection
    try:
        project = await project_model.get_project_or_create_one(
            project_id=project_id
        )  # ensure the collection is created
    except Exception as exc:
        logger.error("MongoDB error while ensuring project exists: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"signal": "Database unavailable"},
        )

    if project.id is None:
        logger.error(
            "Project created/retrieved without database id for project_id=%s",
            project_id,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": ResponseStatus.PROCESSING_FAILED.value},
        )

    project_db_id = project.id

    asset_model = await AssetModel.create_instance(
        db_client=db_client
    )  # the collection of store the asset ,(ensure the collection and indexing with create )

    project_files_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project_db_id,  # the project (collection) id is same id in asset
            asset_name=process_request.file_id,
        )
        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.FILE_ID_ERROR.value,
                },
            )
        project_files_ids = {asset_record.id: asset_record.asset_name}
    else:
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=str(project.id), asset_type=AssetTypeEnum.FILE.value
        )  # get all file from asset for handling files in once

        project_files_ids = {record.id: record.asset_name for record in project_files}
        if len(project_files_ids) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseStatus.FILE_NOT_CONTENT_TYPE.value},
            )

    process_controller = ProcessController(
        project_id=project_id
    )  # for all handling with logic and chunking and loader file extension
    no_record = 0
    no_file = 0
    chunk_model = await ChunkModel.create_instance(
        db_client=db_client
    )  # for store the chunk in db
    if do_reset == 1:
        await chunk_model.delete_chunks_by_project_id(project_id=project_db_id)
    for asset_id, file_id in project_files_ids.items():
        file_content = process_controller.get_file_content(file_id)
        if file_content is None:
            logger.error(f"Error while processing file:{file_id}")
            continue
        chunks = process_controller.process_file_content(
            content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
        )
        if chunks is None or len(chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseStatus.PROCESSING_FAILED.value},
            )
            continue
        # now we want chunk records
        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i + 1,
                chunk_project_id=project_db_id,
                chunk_asset_id=asset_id,
            )  # type: ignore
            for i, chunk in enumerate(chunks)
        ]
        no_record += await chunk_model.insert_many_chunk(chunks=file_chunks_records)
        no_file += 1
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseStatus.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_record,
            "process_files": no_file,
        },
    )
