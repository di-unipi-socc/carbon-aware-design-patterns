import spacy

print("[NLP] Avvio inizializzazione modello spaCy (it_core_news_sm)...")

try:
    nlp = spacy.load("it_core_news_sm")

    nlp.max_length=500000000
    print("[NLP] Modello linguistico caricato con successo!")
    
except OSError:
    print("\n[ERRORE FATALE] Modello spaCy non trovato!")
    print("Per favore, esegui da terminale: python -m spacy download it_core_news_sm\n")
    raise