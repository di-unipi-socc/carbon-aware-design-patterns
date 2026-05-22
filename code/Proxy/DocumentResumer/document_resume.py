
class Document_resume:
    def __init__(self,name:str,author:str):
        self.name=name
        self.author = author
        self.resume = ""


    def set_resume(self,res:str):
        self.resume = res

    def get_resume(self):
        return self.resume