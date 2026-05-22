from request import Request
from database_handler import DatabaseHandler
from spacy_han import nlp


class Matcher:
    def __init__(self, database_handler: DatabaseHandler):
        self.database_handler = database_handler

    def calculate_score(self, set_query: set, dict_doc: dict, file_name: str, original_query: str) -> float:
        final_score = 0.0

        name = file_name.lower().replace(".txt", "").replace(".pdf", "").replace("_", " ")
        query = original_query.lower().strip()

        doc_title = nlp(name)
        title_labels = set()
        for token in doc_title:
            if not token.is_punct and not token.is_space and not token.is_stop:
                title_labels.add(token.lemma_.lower())

        title_comm_word = set_query.intersection(title_labels)
        
        if query in name or name in query:
            final_score += 100.0
        elif len(title_comm_word)>0:
            final_score += (len(title_comm_word)* 5.0)

        if set_query and dict_doc:
            score_tf = 0.0
            found_words = 0
            
            total_doc_words = sum(dict_doc.values())

            for word in set_query:
                if word in dict_doc:
                    found_words += 1
                    frequency = (dict_doc[word] / total_doc_words) * 100
                    score_tf += frequency
                elif " " in word:
                    sub_words = word.split()
                    
                    if all(sub in dict_doc for sub in sub_words):
                        found_words += 1

                        avg_freq = sum(dict_doc[sub] for sub in sub_words) / len(sub_words)
                        frequency = (avg_freq / total_doc_words) * 100
                        score_tf += frequency

            if found_words > 0:
                query_coverage = found_words / len(set_query)
                final_score += (score_tf * query_coverage)

        return final_score

    def search(self, request: Request) -> list:

        
        query_index = request.get_all_index()

        results = []

        for doc in self.database_handler.get_documents():
            score = self.calculate_score(query_index, doc.labels, doc.name, request.original_text)
            print("sono nel matcher")
            if score > 0:
                common_words = set()
                if doc.labels:
                    for p in query_index:
                        if p in doc.labels:
                            common_words.add(p)
                        elif " " in p and all(sub in doc.labels for sub in p.split()):
                            common_words.add(p)
                results.append({
                    "nome_file": doc.clear_name,
                    "score": round(score, 2),
                    "parole_in_comune": common_words,
                    "doc": doc
                })
        results.sort(key=lambda x: x["score"], reverse=True)
        if results:
            return results[0]
        else:
            return results