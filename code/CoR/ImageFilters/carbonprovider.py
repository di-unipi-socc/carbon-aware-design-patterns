
class CarbonProvider:
    def __init__(self):
        self.co2 = 0.0

    def set_co2(self, intensity: float):
        self.co2 = intensity

    def get_co2(self) -> float:
        return self.co2
