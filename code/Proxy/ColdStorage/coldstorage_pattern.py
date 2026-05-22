from service import Service
import time

class Cache_Proxy(Service):
    def __init__(self, real_service: Service,ttl:float):
        self.cache = {}
        self.real_service = real_service
        self.ttl = ttl

    def generate_corr_key(self, operation: str, sensors: list) -> str:
        ordered_sensors = sorted(sensors)
        return f"{operation}_{'_'.join(ordered_sensors)}"

    def generate_anom_key(self, operation: str, sensor: str) -> str:
        return f"{operation}_{sensor}"
    
    def calculate_correlation(self, operation, sensor_a, sensor_b):
        key = self.generate_corr_key(operation, [sensor_a, sensor_b])
        now = time.time()

        if key not in self.cache:
            correlation = self.real_service.calculate_correlation(operation, sensor_a, sensor_b)
            self.cache[key] = {"value": correlation, "time": now}
            return correlation,0.0,None
        
        cache_entry = self.cache[key]
        eta = now-cache_entry['time']

        if eta > self.ttl:
            correlation = self.real_service.calculate_correlation(operation, sensor_a, sensor_b)
            self.cache[key] = {"value": correlation, "time": now}
            return correlation,0.0,None
        
        else:
            return cache_entry['value'],eta,None
        

    def calculate_anomaly(self, operation, sensor):
        key = self.generate_anom_key(operation, sensor)
        now = time.time()

        if key not in self.cache:
            anomaly = self.real_service.calculate_anomaly(operation, sensor)
            self.cache[key] = {"value": anomaly, "time": now}
            return anomaly,0.0,None
        
        cache_entry = self.cache[key]
        eta = now -cache_entry['time']

        if eta >self.ttl:
            anomaly = self.real_service.calculate_anomaly(operation, sensor)
            self.cache[key] = {"value": anomaly, "time": now}
            return anomaly,0.0,None
        else:
            return cache_entry['value'],eta,None