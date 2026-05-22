from pattern.handler import Handler
from pattern.handler_ner_pattern import HandlerNER
from pattern.handler_nomi_pattern import HandlerNomi
from pattern.handler_verbi_pattern import HandlerVerbi
from request import Request

def configure_chain_of_responsibility():
    h_ner = HandlerNER()
    h_nomi = HandlerNomi()
    h_verbi = HandlerVerbi()
    
    h_ner.set_next(h_nomi).set_next(h_verbi)
    return h_ner

def cor_pattern(chain:Handler,request:Request):
    chain.handle(request)
    return