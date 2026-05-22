from pattern_ca.handler_ner import HandlerNER
from pattern_ca.handler_nomi import HandlerNames
from pattern_ca.handler_verbi import HandlerVerbs
from request import Request
from pattern_ca.handler import Handler

def configure_chain_of_responsibility():
    h_ner = HandlerNER()
    h_nomi = HandlerNames()
    h_verbi = HandlerVerbs()
    
    h_ner.set_next(h_nomi).set_next(h_verbi)
    return h_ner


def cor_ca(chain:Handler,request:Request,co2_intensity:float,budgetCOR:float):
    chain.handle(request,budgetCOR,co2_intensity,total_cost=0)
    return