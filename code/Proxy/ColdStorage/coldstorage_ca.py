from service import Service
from carbonprovider import CarbonProvider
import time

class ColdStorage_ca(Service):
    def __init__(self, real_service: Service, provider: CarbonProvider, co2Threshold: float,ttl:float):
        self.cache = {}
        self.real_service = real_service
        self.provider = provider
        self.ttl_base = ttl
        self.co2Threshold = co2Threshold

    def generate_corr_key(self, operation: str, sensors: list) -> str:
        ordered_sensors = sorted(sensors)
        return f"{operation}_{'_'.join(ordered_sensors)}"

    def generate_anom_key(self, operation: str, sensor: str) -> str:
        return f"{operation}_{sensor}"

    def calculate_correlation(self, operation, sensor_a, sensor_b):
        co2 = self.provider.get_co2()
        key = self.generate_corr_key(operation, [sensor_a, sensor_b])
        now = time.time()


        if key not in self.cache:
            correlation = self.real_service.calculate_correlation(operation, sensor_a, sensor_b)
            self.cache[key] = {"value": correlation, "time": now}
            return correlation,0.0,self.ttl_base
        
        cache_entry = self.cache[key]
        eta = now - cache_entry['time']

        if co2 < self.co2Threshold:
            ttl_dynamic = self.ttl_base / 2
        else:
            ttl_dynamic = self.ttl_base * 2

        if eta < ttl_dynamic:
            return cache_entry['value'],eta,ttl_dynamic
        else:
            correlation = self.real_service.calculate_correlation(operation, sensor_a, sensor_b)
            self.cache[key] = {"value": correlation, "time": now}
            return correlation,0.0,ttl_dynamic

    def calculate_anomaly(self, operation, sensor):
        co2 = self.provider.get_co2()
        key = self.generate_anom_key(operation, sensor)
        now = time.time()

        if key not in self.cache:
            anomaly = self.real_service.calculate_anomaly(operation, sensor)
            self.cache[key] = {"value": anomaly, "time": now}
            return anomaly,0.0,self.ttl_base

        cache_entry = self.cache[key]
        eta = now - cache_entry['time']

        if co2 < self.co2Threshold:
            ttl_dynamic = self.ttl_base / 2
        else:
            ttl_dynamic = self.ttl_base * 2

        if eta < ttl_dynamic:
            return cache_entry['value'],eta,ttl_dynamic
        else:
            anomaly = self.real_service.calculate_anomaly(operation, sensor)
            self.cache[key] = {"value": anomaly, "time": now}
            return anomaly,0.0,ttl_dynamic