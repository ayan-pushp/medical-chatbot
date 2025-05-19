from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Dict, Any, Union, Optional
from bson import ObjectId

class DialogState(BaseModel):
    full_input: List[str] = []
    symptoms: List[str] = []
    disease_predictions: List[Dict[str, Any]] = []
    intent: Optional[str] = None
    awaiting_confirmation: bool = False
    awaiting_symptoms: bool = False
    final_assessment_done: bool = False
    confidence_threshold: float = 0.7

class ChatRequest(BaseModel):
    message: str
    dialog_state: Optional[DialogState] = None

class ChatResponse(BaseModel):
    reply: str
    intent: Optional[str]
    dialog_state: DialogState

class DiseasePrediction(BaseModel):
    name: str
    probability: float

class ChatMessage(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    message: str
    is_user: bool
    intent: Union[str, None] = None
    symptoms: List[str] = []
    disease_predictions: List[DiseasePrediction] = []
    timestamp: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        arbitrary_types_allowed=True
    )

    @classmethod
    def from_mongo(cls, data: Dict):
        """Helper to convert MongoDB data to model"""
        if '_id' in data:
            data['_id'] = str(data['_id'])
        if 'disease_predictions' in data:
            cleaned_predictions = []
            for item in data['disease_predictions']:
                if isinstance(item, dict):
                    # already dict, maybe rename keys if needed
                    name = item.get('name') or item.get('disease') or "Unknown"
                    prob = item.get('probability') or item.get('prob') or 0.0
                elif isinstance(item, (list, tuple)) and len(item) == 2:
                    name, prob = item
                else:
                    # fallback default
                    name, prob = "Unknown", 0.0
                cleaned_predictions.append({'name': name, 'probability': float(prob)})
            data['disease_predictions'] = cleaned_predictions

        return cls(**data)
