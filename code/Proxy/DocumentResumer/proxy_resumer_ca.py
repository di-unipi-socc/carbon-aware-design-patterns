import datetime
from resumer import Resumer
from document_resume import Document_resume
from carbonprovider import CarbonProvider

class Resumer_CarbonAware(Resumer):
    def __init__(self, real_resumer: Resumer, provider : CarbonProvider,co2_threshold: float):
        self.real_resumer= real_resumer
        self.provider = provider
        self.co2_threshold = co2_threshold
        self.delayed_doc = {}

    def resume(self, doc:Document_resume) -> str:
        if len(doc.resume)==0:
            now = self.provider.now_time
            if doc.name in self.delayed_doc:
                resume_time= self.delayed_doc[doc.name]
                if now >= resume_time:
                    doc.resume = self.real_resumer.resume(doc)
                    del self.delayed_doc[doc.name]
                    return self.create_response(doc)
                else:
                    return self.create_response(doc)
            co2= self.provider.get_co2()
            if co2 <= self.co2_threshold:
                doc.resume= self.real_resumer.resume(doc)
                return self.create_response(doc)
            else:
                forecast_time,co2_forecast= self.provider.get_forecast()
                if forecast_time and (co2_forecast <= self.co2_threshold) and (forecast_time > now):
                    self.delayed_doc[doc.name] = forecast_time
                    return self.create_response(doc)
                else:
                    doc.resume= self.real_resumer.resume(doc)
                    return self.create_response(doc)
        else:
            return self.create_response(doc)

    def create_response(self,doc:Document_resume)-> str:
        if doc.resume == "":
            response = f"- {doc.name}\n- {doc.author}"
        else:
            response = f"- {doc.name}\n- {doc.author}\n- {doc.resume[:500]}..."
        return response