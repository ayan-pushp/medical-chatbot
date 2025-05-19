import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from app.nlp.intent import IntentClassifier
from app.nlp.symptom import SymptomExtractor
from app.nlp.disease import DiseasePredictor
from app.chat.schemas import DialogState, ChatResponse, ChatMessage
from app.db.session import get_db
from app.auth.schemas import User

# Initialize NLP components
intent_classifier = IntentClassifier()
symptom_extractor = SymptomExtractor()
disease_predictor = DiseasePredictor()

async def store_message(
    user_id: str,
    message: str,
    is_user: bool,
    intent: Optional[str] = None,
    symptoms: Optional[List[str]] = None,
    disease_predictions: Optional[List[Dict[str, Any]]] = None
) -> None:
    """Store chat message in MongoDB"""
    async with get_db() as db:
        await db.chats.insert_one({
            "user_id": user_id,
            "message": message,
            "is_user": is_user,
            "intent": intent,
            "symptoms": symptoms or [],
            "disease_predictions": disease_predictions or [],
            "timestamp": datetime.utcnow()
        })

def generate_response(intent: str, state: DialogState) -> str:
    """Generate bot response based on intent and dialog state"""
    if intent == "greeting":
        return "Hello! Please describe your symptoms."
    
    elif intent == "describe_symptom":
        extracted = symptom_extractor.extract(state.full_input[-1])
        symptoms = list({
                    item.get('preferred_name', '').lower() or 
                    item.get('symptom', '').lower() 
                    for item in extracted 
                    if item.get('preferred_name') or item.get('symptom')
                })        
            
        if symptoms:
            state.symptoms.extend(symptoms)
            state.awaiting_symptoms = False
            state.disease_predictions = disease_predictor.predict(state.symptoms)
            state.intent = "describe_symptom"
        else:
            return "Sorry, I didn't recognize any symptoms. Please describe them differently."
                    
        # if not state.symptoms:
        #     return "Sorry, I didn't recognize any symptoms. Please describe them differently."
        
        reply_lines = [f"Recognized symptoms: {', '.join(state.symptoms)}", 
                      "Possible diseases:"]
        
        for dp in state.disease_predictions:
            reply_lines.append(f"{dp['disease']}: {dp['probability']:.1%}")

        top_disease = state.disease_predictions[0]["disease"]
        confidence = state.disease_predictions[0]["probability"]

        if confidence < state.confidence_threshold:
            state.awaiting_confirmation = True
            reply_lines.append("Could you describe any other symptoms to help me be more certain? (yes/no)")
        else:
            reply_lines.append(f"Final assessment: {top_disease}")
            reply_lines.append("Please consult with a doctor.")
            state.final_assessment_done = True

        return "\n".join(reply_lines)
    
    elif intent == "ask_treatment":
        if state.disease_predictions:
            top_disease = state.disease_predictions[0]["disease"]
            return f"For {top_disease}, please consult a doctor for personalized treatment."
        return "Please describe your symptoms first."

    return "I didn't understand that. Please describe your symptoms or ask about treatment."

async def process_message(
    message: str,
    state: Optional[DialogState],
    username: str
) -> ChatResponse:
    """Main chatbot processing pipeline"""
    state = state or DialogState()
    user_input = message.strip().lower()
    state.full_input.append(user_input)

    # Store user message
    await store_message(username, user_input, True)

    reply=""
    # Handle yes/no responses
    if user_input in ["yes", "no"] and state.awaiting_confirmation:
        if user_input == "no":
            if not state.final_assessment_done:
                reply = ("Thank you for consulting DocBot. Take care!" 
                        if not state.disease_predictions 
                        else f"Final assessment: {state.disease_predictions[0]['disease']}\nPlease consult with a doctor.")
                state.final_assessment_done = True
        else:  # "yes"
            state.awaiting_symptoms = True
            reply = "Please describe your additional symptoms."
        state.awaiting_confirmation = False
    else:
        # Handle symptom extraction
        if state.awaiting_symptoms or state.intent == "describe_symptom":
            extracted = symptom_extractor.extract(user_input)
            symptoms = list({
                item.get('preferred_name', '').lower() or 
                item.get('symptom', '').lower() 
                for item in extracted 
                if item.get('preferred_name') or item.get('symptom')
            })
            
            if symptoms:
                state.symptoms.extend(symptoms)
                state.awaiting_symptoms = False
                state.disease_predictions = disease_predictor.predict(state.symptoms)
                state.intent = "describe_symptom"
            else:
                reply = "Sorry, I didn't recognize any symptoms. Please describe them differently."
        
        # Classify intent if not in special flow
        if not reply:  # Only if no reply was assigned above
            if not any([state.awaiting_confirmation, state.awaiting_symptoms]):
                state.intent = intent_classifier.predict(user_input)
            reply = generate_response(state.intent, state)

    # Store bot response
    await store_message(
        username,
        reply,
        False,
        state.intent,
        state.symptoms,
        state.disease_predictions
    )

    return ChatResponse(
        reply=reply,
        intent=state.intent,
        dialog_state=state
    )

async def get_chat_history(username: str, limit: int = 100) -> List[ChatMessage]:
    """Retrieve user's chat history with proper serialization"""
    async with get_db() as db:
        cursor = db.chats.find({"user_id": username}).sort("timestamp", -1).limit(limit)
        messages = await cursor.to_list(length=limit)
        return [ChatMessage.from_mongo(msg) for msg in messages]