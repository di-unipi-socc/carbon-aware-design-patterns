import os

class Document:
    def __init__(self,filepath:str):
        self.filepath=filepath
        self.name= os.path.basename(filepath)
        self.clear_name=self.name.replace(".txt", "").replace(".pdf", "").replace("_", " ")
        self.labels={}
        self.processed= False
        self.author= ""
        