from pydantic import BaseModel


class PushRequest(BaseModel):
    do_reset: int | None = 0 

class SearchRequest (BaseModel):
    text : str 
    limit : int | None = 5 