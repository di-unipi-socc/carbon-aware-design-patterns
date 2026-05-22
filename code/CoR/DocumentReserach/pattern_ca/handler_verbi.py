import time
from .handler import Handler
from request import Request
from spacy_han import nlp

class HandlerVerbs(Handler):
    def handle(self, request:Request,budgetCO2:float,co2:float,total_cost:float):
        average_cost= co2 * 0.05 * 0.000001033
        if(budgetCO2>=average_cost):
            start_time= time.perf_counter()
            doc = nlp(request.original_text)
            
            for token in doc:
                if token.pos_ in ['VERB', 'AUX']:
                    request.verbs.add(token.lemma_.lower())
            end_time= time.perf_counter()
            total_time= end_time- start_time
            actual_cost = co2 * 0.05 * (total_time/3600)
            budgetCO2-=actual_cost
            total_cost+=actual_cost
            request.n_filters+=1
            request.filters.append("VERBS")
        return super().handle(request,budgetCO2,co2,total_cost)