from abc import ABC, abstractmethod
from document import Document

class Resumer(ABC):
    @abstractmethod
    def resume(self,document:Document)-> str:
        pass