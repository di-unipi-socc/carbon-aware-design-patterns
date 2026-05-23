from abc import ABC, abstractmethod
from doc_resume import Document_resume

class Resumer(ABC):
    @abstractmethod
    def resume(self,document:Document_resume)-> str:
        pass