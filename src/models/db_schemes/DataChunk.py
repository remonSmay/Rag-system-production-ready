
from bson.objectid import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator


class DataChunk(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: ObjectId | None = Field(None,alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId
    chunk_asset_id : ObjectId

    @classmethod
    def get_indexes(cls):

        return [
            {
                "key": [("chunk_project_id", 1)],
                "name": "chunk_project_id_index",
                "unique": False,
            }
        ]

    # @field_validator("_id", "chunk_project_id", mode="before")
    # @classmethod
    # def _validate_object_id(cls, value):
    #     if value is None:
    #         return value
    #     if isinstance(value, ObjectId):
    #         return value
    #     if isinstance(value, str) and ObjectId.is_valid(value):
    #         return ObjectId(value)
    #     raise TypeError("ObjectId expected")


class RetrievedDocument(BaseModel):
    """
        this scheme for return the result form Qdrant vector database , also i want the text and score form all result 
    """
    text: str
    score: float
