from __future__ import annotations
from abc import ABC, abstractmethod

class Filter(ABC):
    @abstractmethod
    def apply_filter(self):
        pass

    @abstractmethod
    def set_next(self,handler:Filter)-> Filter:
        pass