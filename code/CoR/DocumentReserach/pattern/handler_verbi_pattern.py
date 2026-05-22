from handler import Handler
from request import Request
from spacy_han import nlp

class HandlerVerbi(Handler):
    def handle(self, request:Request):
        doc = nlp(request.original_text)
        for token in doc:
            if token.pos_ in ['VERB', 'AUX']:
                request.verbs.add(token.lemma_.lower())
        request.n_filters+=1
        request.filters.append("VERBS")
        return super().handle(request)