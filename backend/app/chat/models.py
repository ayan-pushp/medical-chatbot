from datetime import datetime
from typing import Optional

class ChatMessageDB:
    def __init__(self, user_id: str, message: str, is_user: bool, 
                 intent: Optional[str] = None, symptoms: Optional[list] = None,
                 disease_predictions: Optional[list] = None):
        self.user_id = user_id
        self.message = message
        self.timestamp = datetime.utcnow()
        self.is_user = is_user
        self.intent = intent
        self.symptoms = symptoms or []
        self.disease_predictions = disease_predictions or []