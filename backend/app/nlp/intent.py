import joblib
import torch
from transformers import AutoTokenizer, AutoModel

class IntentClassifier:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2").to(self.device)
        self.clf = joblib.load("ml_models/intent/intent_classifier.pkl")
        self.label_encoder = joblib.load("ml_models/intent/intent_labels.pkl")

    def predict(self, text):
        tokens = self.tokenizer(text, return_tensors='pt', padding=True, truncation=True).to(self.device)
        with torch.no_grad():
            output = self.model(**tokens)
        embedding = output.last_hidden_state.mean(dim=1).cpu().numpy()[0]
        pred = self.clf.predict(embedding.reshape(1, -1))[0]
        return self.label_encoder.inverse_transform([pred])[0]