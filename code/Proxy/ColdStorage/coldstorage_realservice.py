from service import Service
import pandas as pd

class ColdStorage_RealService(Service):
    def __init__(self, database:str = 'database.csv'):
        self.database = database

    def calculate_correlation(self, operation, sensor_a, sensor_b):
        db=pd.read_csv(self.database, sep=';')
        correlation= db[sensor_a].corr(db[sensor_b])
        return correlation
    
    def calculate_anomaly(self, operation, sensor):
        db= pd.read_csv(self.database, sep=';')
        mean = db[sensor].mean()
        dev_std=db[sensor].std()

        if dev_std==0:
            return 0.0
        
        z_score= abs((db[sensor]-mean)/dev_std)
        anomalies = db[z_score>3]

        if not anomalies.empty:
            anomaly_index= z_score.idxmax()
            row= db.loc[anomaly_index]
            value =row[sensor]
            return float(value)
        
        else:
            return 0.0