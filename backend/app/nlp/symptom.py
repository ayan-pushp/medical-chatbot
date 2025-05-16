import spacy
from scispacy.linking import EntityLinker

class SymptomExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_sci_sm")
        self.linker=self.nlp.add_pipe("scispacy_linker", config={
                                        "resolve_abbreviations": True,
                                        "linker_name": "umls",
                                        "threshold": 0.7,
                                    })
    def get_concept_name(self, linker, cui):
        """Get preferred name from linker's knowledge base"""
        if cui in linker.kb.cui_to_entity:
            return linker.kb.cui_to_entity[cui].canonical_name
        return "UNKNOWN"
        
    def extract(self, text):
        doc = self.nlp(text)
        symptoms = []
        for ent in doc.ents:
            if hasattr(ent._, 'kb_ents') and ent._.kb_ents:
                top_cui, top_score = ent._.kb_ents[0]
            
                semtypes = []
                if top_cui in self.linker.kb.cui_to_entity:
                    semtypes = self.linker.kb.cui_to_entity[top_cui].types
            
                symptom_types = {"T184",  # Sign or Symptom
                                "T033",  # Finding
                                "T046",  # Pathologic Function
                                "T037",  # Injury or Poisoning
                                "T047",  # Disease or Syndrome
                                "T048"   # Mental or Behavioral Dysfunction
                                }
                if any(t in symptom_types for t in semtypes):
                    concept_name = self.get_concept_name(self.linker, top_cui)
                    symptoms.append({
                        "symptom": ent.text,
                        "cui": top_cui,
                        "preferred_name": concept_name,
                        "confidence": top_score,
                        "semantic_types": semtypes
                    })
        return symptoms