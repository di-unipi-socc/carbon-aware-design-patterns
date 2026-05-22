from abc import ABC, abstractmethod

class Service(ABC):
    @abstractmethod
    def calculate_correlation(self,operation:str,sensor_a:str,sensor_b:str)-> float:
        pass
    @abstractmethod
    def calculate_anomaly(self,operation:str, sensor:str)-> float:
        pass