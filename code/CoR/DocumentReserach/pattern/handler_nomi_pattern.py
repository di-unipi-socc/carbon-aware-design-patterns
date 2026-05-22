from handler import Handler
from request import Request
from spacy_han import nlp

class HandlerNomi(Handler):
    def handle(self, request:Request):
        doc = nlp(request.original_text)
        for token in doc:
            if not token.is_punct and not token.is_space and not token.is_stop:
                if token.pos_ in ['NOUN','PROPN','ADJ','X']:
                    request.name.add(token.lemma_.lower())
        request.n_filters+=1
        request.filters.append("NAME")

        return super().handle(request)