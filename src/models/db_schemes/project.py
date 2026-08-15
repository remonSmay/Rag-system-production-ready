from typing import Optional
from bson.objectid import ObjectId
from pydantic import BaseModel, Field, field_validator, ConfigDict


class Project(BaseModel):
    """Project Pydantic model representing a project record stored in MongoDB.

    Attributes
    ----------
    id : Optional[ObjectId]
        The MongoDB document identifier. Mapped from the underlying "_id" field via Field(alias="_id").
    project_id : str
        A required, non-empty alphanumeric identifier for the project. Declared with a minimum length of 1.

    Validation
    ----------
    validate_project_id(cls, value) -> str
        Ensures the project_id contains only alphanumeric characters. Raises ValueError if validation fails.

    Configuration
    -------------
    Config.arbitrary_types_allowed : bool
        Allows use of non-Pydantic native types (e.g., ObjectId).

    Indexes
    -------
    get_indexes() -> list[dict]
        Returns a list of MongoDB index configurations. The model defines a unique ascending index on "project_id"
        (named "project_id_index") to enforce uniqueness and optimize lookups.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[ObjectId] = Field(default=None,alias="_id")
    project_id: str = Field(..., min_length=1)

    @field_validator("project_id")
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric ")
        return value

    @classmethod
    def get_indexes(cls):
        """Defines MongoDB indexes for a collection

        return :Returns a list of index configurations ([{...}]) specifying:
                key: Field(s) to index (project_id in ascending order).
                name: Index identifier ("project_id_index").
                unique: Ensures no duplicate project_id values.
                Used in database models to optimize queries and enforce constraints at the schema level.
        """
        return [
            {"key": [("project_id", 1)], "name": "project_id_index", "unique": True}
        ]


# project is a Document in collection
