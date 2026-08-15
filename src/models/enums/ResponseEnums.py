from enum import Enum


class ResponseStatus(Enum):
    FILE_NOT_CONTENT_TYPE = "File has no content type"
    FILE_TYPE_NOT_ALLOWED = "File type is not allowed"
    FILE_SIZE_EXCEEDED = "File size exceeds the maximum limit"
    FILE_VALIDATION_SUCCESS = "File validation successful"
    FILE_UPLOAD_FAILED = "File upload failed"
    FILE_UPLOAD_SUCCESS = "File upload successful"

    FILE_ID_ERROR = "the file not found "
    PROCESSING_SUCCESS = "File processing successful"
    PROCESSING_FAILED = "File processing failed"

    DATABASE_UNFOUND = "database not available"
    PROJECT_NOT_FOUND_ERROR = "project no found or can not create "

    INSERT_INTO_VECTORDB_SUCCUSS = "insert into vector database succuss "
    INSERT_INTO_VECTORDB_FAIL = "insert into vector database fail"

    VECTOR_DB_RETRIEVED = " info project vector db is succuss"

    VECTOR_DB_SEARCH_ERROR = "vectordb_search_error"

    VECTOR_DB_SEARCH_SUCCESS = "vectordb_search_success"

    RAG_ANSWER_ERROR="not found answer"
    RAG_ANSWER_SUCCESS="success found answer "
