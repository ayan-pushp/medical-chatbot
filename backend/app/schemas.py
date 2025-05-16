from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel

class DialogState(BaseModel):
    intent: Optional[str] = None
    symptoms: List[str] = []
    disease_predictions: Optional[List[Tuple[str, float]]] = None
    confidence_threshold: float = 0.6
    awaiting_confirmation: bool = False
    awaiting_symptoms: bool = False
    final_assessment_done: bool = False
    full_input: List[str] = []

class ChatRequest(BaseModel):
    message: str
    dialog_state: Optional[DialogState] = None

class ChatResponse(BaseModel):
    reply: str
    intent: Optional[str]
    dialog_state: DialogState
