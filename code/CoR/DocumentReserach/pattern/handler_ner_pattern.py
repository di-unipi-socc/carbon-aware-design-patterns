from handler import Handler
from request import Request
from spacy_han import nlp

class HandlerNER(Handler):
    def handle(self, request: Request):
            
        doc = nlp(request.original_text)
    
        for ent in doc.ents:
            request.entity.add(ent.text.lower())
        request.n_filters+=1
        request.filters.append("NER")

        super().handle(request)