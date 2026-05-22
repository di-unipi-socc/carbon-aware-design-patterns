import os

class DataBase:
    def __init__(self):
        self.documents=[]
        self.json_labels={}
        self.FILE_JSON = os.path.join("data", "labels.json")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.FILE_JSON = os.path.join(current_dir, "data", "labels.json")

