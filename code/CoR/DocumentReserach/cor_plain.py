from request import Request
from spacy_han import nlp
import time

def create_labels(req:Request):
    Ner(req)
    Name(req)
    Verbs(req)
    return



def Ner(request:Request):
    doc = nlp(request.original_text)
    for ent in doc.ents:
        request.entity.add(ent.text.lower())
    request.n_filters+=1
    return

def Name(request:Request):
    doc = nlp(request.original_text)
    for token in doc:
        if not token.is_punct and not token.is_space and not token.is_stop:
            if token.pos_ in ['NOUN','PROPN','ADJ','X']:
                request.name.add(token.lemma_.lower())
    request.n_filters+=1
    return

def Verbs(request:Request):
    doc = nlp(request.original_text)
    for token in doc:
        if token.pos_ in ['VERB', 'AUX']:
            request.verbs.add(token.lemma_.lower())
    request.n_filters+=1
    return