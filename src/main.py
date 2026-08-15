from __future__ import annotations

import logging
from contextlib import asynccontextmanager  # for lifespan management

import uvicorn
from fastapi import FastAPI

from helpers.config import Settings, get_settings
from helpers.db import close_mongo_connection, connect_to_mongo
from routes import base, data, nlp
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # init config , var 
    settings: Settings = get_settings()
    llm_factory = LLMProviderFactory(settings)
    vectorDB_factory = VectorDBProviderFactory(settings)
    try:
        # startup the connection or initial once
        app.state.template_parser = TemplateParser(
            language=settings.PRIMARY_LANG, default_language=settings.DEFAULT_LANG
        )
        generation_model = llm_factory.create(provider=settings.GENERATION_BACKEND)
        if generation_model and settings.GENERATION_MODEL_ID:
            generation_model.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
        app.state.generation_model = generation_model

        embedding_model = llm_factory.create(provider=settings.EMBEDDING_BACKEND)
        if (
            embedding_model
            and settings.EMBEDDING_MODEL_ID
            and settings.EMBEDDING_MODEL_SIZE is not None
        ):
            embedding_model.set_embedding_model(
                model_id=settings.EMBEDDING_MODEL_ID,
                embedding_size=settings.EMBEDDING_MODEL_SIZE,
            )
        app.state.embedding_model = embedding_model
        vectorDB = vectorDB_factory.create(
            provider=(
                settings.VECTOR_DB_BACKEND if settings.VECTOR_DB_BACKEND else "QDRANT"
            )
        )
        app.state.vectorDB = vectorDB
        if vectorDB:
            vectorDB.connect()

        await connect_to_mongo()
        yield
    finally:
        vector_db = getattr(app.state, "vectorDB", None)
        if vector_db:
            vector_db.disconnect()
        close_mongo_connection()


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
# cd /home/remoo/Desktop/Project-mini-rag/src && /home/remoo/miniconda3/envs/mini-rag-app/bin/python main.py
