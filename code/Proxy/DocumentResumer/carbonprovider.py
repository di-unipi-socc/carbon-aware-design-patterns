import datetime

class CarbonProvider:
    def __init__(self):
        self.co2 = 0.0
        self.forecast_time = None
        self.now_time = None
        self.co2_forecast = 0.0

    def set_co2_attuale(self,time:float, intensity: float):
        self.now_time = time
        self.co2 = intensity


    def set_forecast(self, time: float, intensity: float):
        self.forecast_time = time
        self.co2_forecast = intensity

    def get_co2(self) -> float:
        return self.co2

    def get_forecast(self) -> tuple:
        return self.forecast_time, self.co2_forecast