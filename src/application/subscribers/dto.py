from pydantic import BaseModel


class Subscriber(BaseModel):
    telegram_id: str
    telegram_username: str
    # ... everything else

    class Config:
        orm_mode = True
