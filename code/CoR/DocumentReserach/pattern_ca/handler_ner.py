import time
from .handler import Handler
from request import Request
from spacy_han import nlp

class HandlerNER(Handler):
    
    def handle(self, request: Request,budgetCO2:float,co2:float,total_cost:float):
        average_cost= co2 * 0.05 * 0.00000113
        if(budgetCO2>=average_cost):
            start_time= time.perf_counter()
            print ("sono entrato")
            
            doc = nlp(request.original_text)
        
            for ent in doc.ents:
                request.entity.add(ent.text.lower())
                
            end_time=time.perf_counter()
            total_time= end_time-start_time
            actual_cost = co2 * 0.05 * (total_time/3600)
            budgetCO2-=actual_cost
            total_cost+=actual_cost
            request.n_filters+=1
            request.filters.append("NER")


        super().handle(request,budgetCO2,co2,total_cost)