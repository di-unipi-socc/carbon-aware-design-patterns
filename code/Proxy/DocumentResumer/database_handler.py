import os
from database import DataBase
from resumer import Resumer
from doc_resume import Document_resume


class DatabaseHandler:
    def __init__(self,resumer:Resumer,db:DataBase,data_directory: str = "data"):
        self.resumer = resumer
        self.data_dir= data_directory
        self.database= db

    def get_documents(self)-> list:
        return self.database.documents_resume
    
    def get_resume(self,name:str,author:str)-> str:
        if name in self.database.documents_resume:
            doc = self.database.documents_resume[name]
        else:
            doc = Document_resume(name,author)
            self.database.documents_resume[name]= doc
        return self.resumer.resume(doc)
    
