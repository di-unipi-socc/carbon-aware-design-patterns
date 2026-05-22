class Request:
    def __init__(self, query_text: str):
        self.original_text = query_text
        self.entity = set()
        self.name = set()
        self.verbs = set()
        self.n_filters=0
        self.filters=[]

    def get_all_index(self) -> set:
        return self.entity | self.name | self.verbs