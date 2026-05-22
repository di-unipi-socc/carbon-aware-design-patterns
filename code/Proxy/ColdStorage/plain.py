import time
import pandas as pd


class Plain():
    def __init__(self,filepath:str = 'database.csv'):
        self.filepath= filepath

    def calculate_correlation(self,operation:str,sensor_a:str,sensor_b:str):
        db = pd.read_csv(self.filepath,sep=';')
        correlation= db[sensor_a].corr(db[sensor_b])
        return correlation
    
    def calculate_anomaly(self,operation:str,sensor:str):
        db = pd.read_csv(self.filepath,sep=';')
        mean = db[sensor].mean()
        dev_std = db[sensor].std()

        if dev_std==0:
            return 0.0
        
        z_score = abs((db[sensor]-mean)/dev_std)
        anomalies = db[z_score>3]
        if not anomalies.empty:
            anomaly_index= z_score.idxmax()
            row= db.loc[anomaly_index]
            value =row[sensor]
            
            return float(value)
        
        else:
            return 0.0