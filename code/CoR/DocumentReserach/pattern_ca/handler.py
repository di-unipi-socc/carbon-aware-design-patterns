from abc import ABC, abstractmethod
from request import Request

class Handler(ABC):
    def __init__(self):
        self.next_handler = None

    def set_next(self, handler):
        self.next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request: Request,budget:float,co2:float,total_cost:float):
        if self.next_handler is not None:
            self.next_handler.handle(request,budget,co2,total_cost)
