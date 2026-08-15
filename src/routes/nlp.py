import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.engine import result

from controllers.NLPController import NLPController
from helpers.config import Settings, get_settings
from helpers.db import get_db
from models.ChunkModel import ChunkModel
from models.enums.ResponseEnums import ResponseStatus
from models.ProjectModel import ProjectModel

from .schemes.nlp import PushRequest, SearchRequest

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(prefix="/api/v1", tags=["api_v1", "nlp"])


@nlp_router.post("/index/push/{project_id}")
async def index_project(
    request: Request,
    project_id: str,
    push_request: PushRequest,
    db_client: AsyncIOMotorDatabase = Depends(get_db),
):

    project_model = await ProjectModel.create_instance(db_client=db_client)

    chunk_model = await ChunkModel.create_instance(db_client=db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    project_db_id = project.id if project else None
    if not project or project_db_id is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"single": ResponseStatus.PROJECT_NOT_FOUND_ERROR.value},
        )

    nlp_controller = NLPController(
        generation_client=request.app.state.generation_model,
        embedding_client=request.app.state.embedding_model,
        vectorDB_client=request.app.state.vectorDB,
        template_parser=request.app.state.template_parser,
    )
    has_record = True
    page_no = 1
    idx = 0
    inserted_items_count = 0

    while has_record:
        page_chunks = await chunk_model.get_project_chunks(
            project_id=project_db_id, page_no=page_no
        )
        if len(page_chunks):
            page_no += 1
        if len(page_chunks) == 0 or not page_chunks:
            has_record = False
            break
        chunks_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)
        is_inserted = nlp_controller.index_into_vector_db(
            project=project,  # type: ignore
            chunks=page_chunks,
            chunk_id=chunks_ids,
            do_reset=push_request.do_reset,  # type: ignore
        )
        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseStatus.INSERT_INTO_VECTORDB_FAIL.value},
            )
        inserted_items_count += len(page_chunks)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseStatus.INSERT_INTO_VECTORDB_SUCCUSS.value,
            "no_insert": inserted_items_count,
        },
    )


@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(
    request: Request, project_id: str, db_client: AsyncIOMotorDatabase = Depends(get_db)
):

    # project model
    # use project model -> get project model id
    # NLp controller
    # use Nlp controller -> get_vectorDB_info
    project_model = await ProjectModel.create_instance(db_client=db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    try:
        nlp_controller = NLPController(
            generation_client=request.app.state.generation_model,
            embedding_client=request.app.state.embedding_model,
            vectorDB_client=request.app.state.vectorDB,
                template_parser=request.app.state.template_parser
        )
    except Exception as e:
        logger.error(f"{e}")
        raise HTTPException(
            status_code=400, detail=" error while create or get the project from DB "
        )

    collection_info = nlp_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
        content={
            "signal": ResponseStatus.VECTOR_DB_RETRIEVED.value,
            "info_collection": collection_info,
        }
    )


@nlp_router.post("/index/search/{project_id}")
async def search_index(
    request: Request,
    project_id: str,
    search_request: SearchRequest,
    db_client: AsyncIOMotorDatabase = Depends(get_db),  # noqa: B008
):
    project_model = await ProjectModel.create_instance(db_client=db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    try:
        nlp_controller = NLPController(
            generation_client=request.app.state.generation_model,
            embedding_client=request.app.state.embedding_model,
            vectorDB_client=request.app.state.vectorDB,
            template_parser=request.app.state.template_parser
        )
    except Exception as e:
        logger.error(f"{e}")
        raise HTTPException(
            status_code=400, detail=" error while create or get the project from DB "
        )
    results = nlp_controller.search_vector_db_collection(
        project=project, text=search_request.text, limit=search_request.limit # type: ignore
    )

    if not results:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST , 
            content={
                "signal": ResponseStatus.VECTOR_DB_SEARCH_ERROR.value,
            }
        )
    return JSONResponse(
        content={
            "signal": ResponseStatus.VECTOR_DB_SEARCH_SUCCESS.value,
            "results": [result.model_dump() for result in results],  # noqa: F811
        }
    )
@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request : Request , project_id : str , search_request:SearchRequest , db_client: AsyncIOMotorDatabase = Depends(get_db),):
    project_model = await ProjectModel.create_instance(db_client=db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project or project.id is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseStatus.PROJECT_NOT_FOUND_ERROR.value},
        )

    nlp_controller = NLPController(
                generation_client=request.app.state.generation_model,
                embedding_client=request.app.state.embedding_model,
                vectorDB_client=request.app.state.vectorDB,
                template_parser=request.app.state.template_parser
            )
    answer, full_prompt, chat_history = nlp_controller.answer_question_rag(
        project=project, # type: ignore
        query=search_request.text,
        limit=search_request.limit # type: ignore
    )
    if not answer :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST , 
                content= {
                    "signal": ResponseStatus.RAG_ANSWER_ERROR.value
                }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseStatus.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history,
        }
    )
