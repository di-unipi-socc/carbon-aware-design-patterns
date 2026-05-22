import os
from document import Document
from database import DataBase
from label_creator import elaborate
import json

class DatabaseHandler:
    def __init__(self,db:DataBase,data_directory: str = os.path.join("data", "books")):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(current_dir, "data", "books")
        self.database= db
        self.initialize_db()


    def initialize_db(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            return
        
        self.load_labels_db()
        for filename in os.listdir(self.data_dir):
            if filename.lower().endswith(('.txt','.pdf')):
                path= os.path.join(self.data_dir,filename)
                doc = Document(path)
                self.database.documents.append(doc)
                if doc.name in self.database.json_labels:
                    doc.labels = self.database.json_labels[doc.name]["labels"]
                    doc.processed = True
                else:
                    doc.labels = elaborate(doc.filepath)
                    doc.processed = True
                    self.database.json_labels[doc.name] = {
                        "labels":doc.labels
                    }

        self.save_labels_db()

    def load_labels_db(self):
        try:
            with open(self.database.FILE_JSON,"r",encoding="utf-8") as fr:
                if os.stat(self.database.FILE_JSON).st_size == 0 :
                    self.database.json_labels={}
                else:
                    self.database.json_labels = json.load(fr)
        except FileNotFoundError:
            print("[AVVISO] File JSON non trovato. Inizializzo un dizionario vuoto.")
            self.database.json_labels = {}
        except json.JSONDecodeError:
            print("[ERRORE] Il file JSON è corrotto o formattato male. Inizializzo un dizionario vuoto.")
            self.database.json_labels = {}


    def save_labels_db(self):
        with open(self.database.FILE_JSON,"w", encoding="utf-8") as fw:
            json.dump(self.database.json_labels,fw,indent=4, ensure_ascii= False)

    def get_documents(self)-> list:
        return self.database.documents
    
    def get_labels_json(self) -> dict:
        return self.database.json_labels
