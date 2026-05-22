import os
import pypdf
from spacy_han import nlp

def extract_text(filepath:str) -> str:
    extension = os.path.splitext(filepath)[1].lower()
    if extension == '.txt':
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    elif extension == '.pdf':
        whole_text= []
        with open(filepath,'rb')as f :
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                extractedtext= page.extract_text()
                if extractedtext:
                    whole_text.append(extractedtext + " ")
        return "".join(whole_text)
    else:
        raise ValueError(f"Formato file non supportato: {extension}")
    

def elaborate(filepath:str)-> dict:
    name = os.path.basename(filepath)

    full_text = extract_text(filepath)
    chunck_size = 100000
    characters_number= len(full_text)
    labels = {}
    for i in range(0,characters_number,chunck_size):
        chunk = full_text[i:i+chunck_size]
        doc = nlp(chunk)

        for token in doc:
            if not token.is_punct and not token.is_space and not token.is_stop:
                    lemma = token.lemma_.lower()
                    labels[lemma] = labels.get(lemma, 0) + 1
            
        for ent in doc.ents:
            ent_text = ent.text.lower()
            labels[ent_text] = labels.get(ent_text, 0) + 1

    return labels