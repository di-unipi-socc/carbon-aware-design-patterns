from document_resume import Document_resume
from resumer import Resumer
from transformers import pipeline
import transformers
transformers.logging.set_verbosity_error()

class Resumer_RealService(Resumer):
    def __init__(self):
        
        self.pipe = pipeline(
            "text-generation",
            model="Qwen/Qwen2.5-0.5B-Instruct",
            device_map="auto"
        )
        
    def resume(self,doc:Document_resume) -> str:

        messages = [
            {
                "role": "system",
                "content": "Sei un assistente letterario esperto. Il tuo obiettivo è fornire riassunti  delle opere richieste."
            },
            {
                "role":"user",
                "content": f"Scrivi un riassunto dell'opera {doc.name} di {doc.author}."
            }
        ]

        out= self.pipe(messages,return_full_text=False,max_new_tokens=150)
        generated_text = out[0]['generated_text']


        return generated_text
    
