from fastapi import APIRouter
from app.nlp.intent import IntentClassifier
from app.nlp.symptom import SymptomExtractor
from app.nlp.disease import DiseasePredictor
# from app.nlp.response import ResponseGenerator
from app.schemas import ChatRequest, ChatResponse, DialogState

router = APIRouter()

intent_classifier = IntentClassifier()
symptom_extractor = SymptomExtractor()
disease_predictor = DiseasePredictor()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Initialize state if none was passed
    state = request.dialog_state or DialogState()

    user_input = request.message.strip().lower()
    state.full_input.append(user_input)

    # Handle yes/no responses
    if user_input in ["yes", "no"] and state.awaiting_confirmation:
        if user_input == "no":
            if not state.final_assessment_done:
                if not state.disease_predictions:
                    reply = "Thank you for consulting DocBot. Take care!"
                else:
                    top_disease, _ = state.disease_predictions[0]
                    sentence = " ".join(state.full_input)
                    summary =""
                    reply = f"Final assessment: {top_disease}\nSummary: {summary}\nPlease consult with a doctor."
                    state.final_assessment_done = True
        elif user_input == "yes":
            state.awaiting_symptoms = True
            reply = "Please describe your additional symptoms."
        state.awaiting_confirmation = False

    # If awaiting more symptoms
    elif state.awaiting_symptoms:
        extracted = symptom_extractor.extract(user_input)
        symptoms = []
        for item in extracted:
                if item.get('preferred_name'):
                    symptoms.append(item['preferred_name'].lower())
                if item.get('symptom'):
                    symptoms.append(item['symptom'].lower())
 
        if symptoms:
            state.symptoms.extend(list(set(symptoms)))
            state.awaiting_symptoms = False

            predictions = disease_predictor.predict(state.symptoms)
            state.disease_predictions = predictions

            reply_lines = ["Possible diseases:"]
            for disease, prob in predictions:
                reply_lines.append(f"{disease}: {prob:.1%}")

            top_disease, confidence = predictions[0]
            if confidence < state.confidence_threshold:
                state.awaiting_confirmation = True
                reply_lines.append("Could you describe any other symptoms to help me be more certain? (yes/no)")
            else:
                sentence = " ".join(state.full_input)
                summary =""
                reply_lines.append(f"Final assessment: {top_disease}")
                reply_lines.append(f"Summary: {summary}")
                reply_lines.append("Please consult with a doctor.")
                state.final_assessment_done = True

            reply = "\n".join(reply_lines)
        else:
            reply = "Sorry, I didn't recognize any symptoms. Please describe them differently."

    # Intent-based processing
    else:
        intent = intent_classifier.predict(user_input)
        state.intent = intent

        if intent == "greeting":
            reply = "Hello! Please describe your symptoms."
            state.awaiting_symptoms = True

        elif intent == "describe_symptom":
            extracted = symptom_extractor.extract(user_input)
            symptoms = []
            for item in extracted:
                    if item.get('preferred_name'):
                        symptoms.append(item['preferred_name'].lower())
                    if item.get('symptom'):
                        symptoms.append(item['symptom'].lower())
    
            if symptoms:
                state.symptoms.extend(list(set(symptoms)))

                predictions = disease_predictor.predict(state.symptoms)
                state.disease_predictions = predictions

                reply_lines = [f"Recognized symptoms: {', '.join(state.symptoms)}", "Possible diseases:"]
                for disease, prob in predictions:
                    reply_lines.append(f"{disease}: {prob:.1%}")

                top_disease, confidence = predictions[0]
                if confidence < state.confidence_threshold:
                    state.awaiting_confirmation = True
                    reply_lines.append("Could you describe any other symptoms to help me be more certain? (yes/no)")
                else:
                    sentence = " ".join(state.full_input)
                    summary =""
                    reply_lines.append(f"Final assessment: {top_disease}")
                    reply_lines.append(f"Summary: {summary}")
                    reply_lines.append("Please consult with a doctor.")
                    state.final_assessment_done = True

                reply = "\n".join(reply_lines)
            else:
                reply = "Sorry, I didn't recognize any symptoms. Please describe them differently."
                state.awaiting_confirmation = True
                state.awaiting_symptoms = True

        elif intent == "ask_treatment":
            if state.disease_predictions:
                top_disease, _ = state.disease_predictions[0]
                sentence = " ".join(state.full_input)
                summary =""
                reply = f"{summary}\nPlease consult a doctor for personalized treatment."
            else:
                reply = "Please describe your symptoms first so I can suggest treatment options."
                state.awaiting_symptoms = True

        else:
            reply = "I didn't understand that. Please describe your symptoms or ask about treatment."

    return ChatResponse(reply=reply, intent=state.intent, dialog_state=state)
