from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str
    session_id: str | None = None   # None -> new session
    parent_id: str | None = None    # None -> continue latest node (branch off older node to edit/regenerate)


class QueryResponse(BaseModel):
    answer: str
    session_id: str
    user_message_id: str
    assistant_message_id: str

class url(BaseModel):
    url: str