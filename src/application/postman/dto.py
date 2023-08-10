from pydantic import BaseModel


class DispatchMessage(BaseModel):
    from_username: str
    message: str
