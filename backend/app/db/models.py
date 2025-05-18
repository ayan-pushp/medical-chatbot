from pydantic import BaseModel
from typing import Optional

class UserDB(BaseModel):
    username: str
    hashed_password: str
    disabled: Optional[bool] = False

class ChatMessageDB(BaseModel):
    user_id: str
    message: str
    timestamp: str
    is_user: bool
    intent: Optional[str]
    symptoms: list
    disease_predictions: list