import numpy as np
import pandas as pd
from keras.models import load_model
import joblib
from typing import List, Tuple

class DiseasePredictor:
    def __init__(self):
        try:
            self.model = load_model("ml_models/disease/disease_model.h5")
            self.disease_encoder = joblib.load("ml_models/disease/disease_encoder.pkl")
            self.symptom_mappings = pd.read_csv("ml_models/disease/symptom_mappings.csv").drop(columns='diseases').apply(pd.to_numeric, errors='coerce').fillna(0).astype('float32')
        except Exception as e:
            raise RuntimeError(f"Failed to load disease prediction models: {str(e)}")

    def predict(self, symptoms: List[str], top_n: int = 3) -> List[Tuple[str, float]]:
        
        if not symptoms:
            raise ValueError("At least one symptom must be provided")

        # Create input vector (mirrors your notebook code)
        input_vector = np.zeros(len(self.symptom_mappings.columns), dtype='float32')
        found_symptoms = []
        
        for symptom in symptoms:
            norm_symptom = symptom.lower().strip()
            if norm_symptom in self.symptom_mappings.columns:
                idx = self.symptom_mappings.columns.get_loc(norm_symptom)
                input_vector[idx] = 1.0
                found_symptoms.append(norm_symptom)

        if not found_symptoms:
            return [("No matching symptoms found", 0.0)]

        # Get predictions
        proba = self.model.predict(input_vector.reshape(1, -1), verbose=0)[0]
        top_indices = np.argsort(proba)[-top_n:][::-1]
        
        return [
            (self.disease_encoder.inverse_transform([idx])[0], float(proba[idx]))
            for idx in top_indices
        ]