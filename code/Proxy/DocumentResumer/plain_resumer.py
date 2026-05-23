from resumer import Resumer
from doc_resume import Document_resume

class ProxyResumer(Resumer):
    def __init__(self, real_resumer: Resumer):
        self.real_resumer = real_resumer

    def resume(self, doc: Document_resume) -> str:
        if len(doc.resume)==0:
            doc.resume = self.real_resumer.resume(doc)
            return doc.resume
        else:
            return doc.resume
