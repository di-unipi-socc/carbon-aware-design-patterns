import json
import csv
import time

from request import Request
import cor_plain
from cor_pattern import configure_chain_of_responsibility as configure_chain_pattern
from pattern_ca.handler_ner import HandlerNER as CA_NER
from pattern_ca.handler_nomi import HandlerNames as CA_Nomi
from pattern_ca.handler_verbi import HandlerVerbs as CA_Verbi
from matcher import Matcher
from database_handler import DatabaseHandler
from database import DataBase


FILE_JSON = "time_slot.json"
FILE_CSV_OUT_BASE = "risultati_cor_base.csv"
FILE_CSV_OUT_INCR = "risultati_cor_incr.csv"
POTENZA_WATT_COR = 50.0
BASE_BUDGETS = [0.000009, 0.0000142,0.000024,0.000034,0.0000435,0.000053,0.000063,0.000073]
INCR_BUDGETS =[0.000024,0.000031,0.000038,0.000046,0.000053,0.000060,0.000067,0.000073]

QUERIES_TEST = [
    ("il signore degli anelli.pdf", "Corta", "Frodo"),
    ("il signore degli anelli.pdf", "Media", "Frodo Baggins distrugge l'anello a Mordor"),
    ("il signore degli anelli.pdf", "Lunga", " Frodo Baggins, Samvise Gamgee, Meriadoc Brandibuck e Peregrino Tuc lasciarono la Contea per incontrare Aragorn figlio di Arathorn, Legolas l'Elfo, Gimli il Nano e Gandalf il Grigio a Gran Burrone"),
    
    ("Harry Potter e la pietra filosfale.pdf", "Corta", "Harry Potter"),
    ("Harry Potter e la pietra filosfale.pdf", "Media", "Harry va a lezione di pozioni dal professore Piton"),
    ("Harry Potter e la pietra filosfale.pdf", "Lunga", ": Il Ministero della Magia britannico situato a Londra ha inviato Albus Silente e Harry Potter presso la Scuola di Magia e Stregoneria di Hogwarts per indagare sui Mangiamorte fuggiti dalla prigione di Azkaban in Inghilterra."),
    
    ("Memorie dal sottosuolo.pdf", "Corta", "Sottosuolo"),
    ("Memorie dal sottosuolo.pdf", "Media", "Le riflessioni di un uomo malato e cattivo"),
    ("Memorie dal sottosuolo.pdf", "Lunga", "Le profonde riflessioni filosofiche di un uomo isolato e tormentato che vive in un misero appartamento a San Pietroburgo, in Russia, rifiutando categoricamente le fredde leggi della natura, la logica matematica e l'utopico Palazzo di Cristallo della società moderna.")
]

def calcola_emissioni(tempo_sec: float, potenza_watt: float, co2_intensity: float) -> float:
    energia_kwh = (potenza_watt / 1000.0) * (tempo_sec / 3600.0)
    return energia_kwh * co2_intensity

def configure_chain_ca():
    h_ner = CA_NER()
    h_nomi = CA_Nomi()
    h_verbi = CA_Verbi()
    h_ner.set_next(h_nomi).set_next(h_verbi)
    return h_ner

def main_base():
    chain_pattern = configure_chain_pattern()
    chain_ca = configure_chain_ca()
    db = DataBase()
    db_handler = DatabaseHandler(None,db)
    matcher = Matcher(db_handler)
    with open(FILE_JSON, "r") as f:
        time_slots = json.load(f)["data"]

    risultati = []

    for slot in time_slots:
        co2_act = float(slot["intensity"]["actual"])
        
        for doc_name, tipo_query, testo_query in QUERIES_TEST:
            for budget in BASE_BUDGETS:
                
                # --- PLAIN ---
                tempo_plain_tot=0
                for i in range (0,10):
                    req_plain = Request(testo_query)
                    start = time.perf_counter()
                    cor_plain.create_labels(req_plain)
                    end = time.perf_counter()
                    t_plain = end - start
                    tempo_plain_tot += t_plain
                t_plain = tempo_plain_tot/10
                parole_plain = len(req_plain.entity) + len(req_plain.name) + len(req_plain.verbs)
                em_plain = calcola_emissioni(t_plain, POTENZA_WATT_COR, co2_act)
                req_plain.filters=["NER","NAME","VERBS"]
                res_plain = matcher.search(req_plain)
                if res_plain['nome_file']== doc_name.replace(".pdf",""):
                    file_trovato_plain = True
                else:
                    file_trovato_plain = False
                risultati.append([doc_name, tipo_query, "Plain", budget, co2_act, t_plain, em_plain, req_plain.n_filters,req_plain.filters, parole_plain,file_trovato_plain])

                # --- PATTERN ---
                tempo_patt_tot = 0
                for i in range (0,10):
                    req_patt = Request(testo_query)
                    start = time.perf_counter()
                    chain_pattern.handle(req_patt)
                    end = time.perf_counter()
                    t_patt = end - start
                    tempo_patt_tot += t_patt
                t_patt = tempo_patt_tot/10
                parole_patt = len(req_patt.entity) + len(req_patt.name) + len(req_patt.verbs)
                em_patt = calcola_emissioni(t_patt, POTENZA_WATT_COR, co2_act)
                res_pattern = matcher.search(req_patt)
                if res_pattern['nome_file']== doc_name.replace(".pdf",""):
                    file_trovato_pattern = True
                else:
                    file_trovato_pattern = False
                risultati.append([doc_name, tipo_query, "Pattern", budget, co2_act, t_patt, em_patt, req_patt.n_filters,req_patt.filters, parole_patt,file_trovato_pattern])

                # --- CARBON AWARE ---
                tempo_ca_tot=0
                for i in range(0,10):
                    req_ca = Request(testo_query)
                    start = time.perf_counter()
                    chain_ca.handle(req_ca, budget, co2_act, 0.0)
                    end = time.perf_counter()
                    t_ca = end - start
                    tempo_ca_tot += t_ca
                t_ca = tempo_ca_tot/10
                parole_ca = len(req_ca.entity) + len(req_ca.name) + len(req_ca.verbs)
                em_ca = calcola_emissioni(t_ca, POTENZA_WATT_COR, co2_act)
                res_ca = matcher.search(req_ca)
                if res_ca and res_ca['nome_file']== doc_name.replace(".pdf",""):
                    file_trovato_ca = True
                else:
                    file_trovato_ca = False
                risultati.append([doc_name, tipo_query, "CA", budget, co2_act, t_ca, em_ca, req_ca.n_filters,req_ca.filters, parole_ca,file_trovato_ca])

    # Salvataggio
    with open(FILE_CSV_OUT_BASE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Documento", "Tipo_query", "Versione", "Budget", "CI", "Tempo_s", "CO2_Emessa_g", "Numero_filtri","Filtri_applicati","Parole_trovate","File_corretto_trovato"])
        writer.writerows(risultati)

    print(f" Test CoR completato! Risultati salvati in '{FILE_CSV_OUT_BASE}'")


def main_incr():
    chain_pattern = configure_chain_pattern()
    chain_ca = configure_chain_ca()
    db = DataBase()
    db_handler = DatabaseHandler(None,db)
    matcher = Matcher(db_handler)
    with open(FILE_JSON, "r") as f:
        time_slots = json.load(f)["data"]

    risultati = []

    for slot in time_slots:
        co2_act = float(slot["intensity"]["actual"])
        
        for doc_name, tipo_query, testo_query in QUERIES_TEST:
            for budget in INCR_BUDGETS:
                
                # --- PLAIN ---
                tempo_plain_tot=0
                for i in range (0,10):
                    req_plain = Request(testo_query)
                    start = time.perf_counter()
                    cor_plain.create_labels(req_plain)
                    end = time.perf_counter()
                    t_plain = end - start
                    tempo_plain_tot += t_plain
                t_plain = tempo_plain_tot/10
                parole_plain = len(req_plain.entity) + len(req_plain.name) + len(req_plain.verbs)
                em_plain = calcola_emissioni(t_plain, POTENZA_WATT_COR, co2_act)
                req_plain.filters=["NER","NAME","VERBS"]
                res_plain = matcher.search(req_plain)
                if res_plain['nome_file']== doc_name.replace(".pdf",""):
                    file_trovato_plain = True
                else:
                    file_trovato_plain = False
                risultati.append([doc_name, tipo_query, "Plain", budget, co2_act, t_plain, em_plain, req_plain.n_filters,req_plain.filters, parole_plain,file_trovato_plain])

                # --- PATTERN ---
                tempo_patt_tot = 0
                for i in range (0,10):
                    req_patt = Request(testo_query)
                    start = time.perf_counter()
                    chain_pattern.handle(req_patt)
                    end = time.perf_counter()
                    t_patt = end - start
                    tempo_patt_tot += t_patt
                t_patt = tempo_patt_tot/10
                parole_patt = len(req_patt.entity) + len(req_patt.name) + len(req_patt.verbs)
                em_patt = calcola_emissioni(t_patt, POTENZA_WATT_COR, co2_act)
                res_pattern = matcher.search(req_patt)
                if res_pattern['nome_file']== doc_name.replace(".pdf",""):
                    file_trovato_pattern = True
                else:
                    file_trovato_pattern = False
                risultati.append([doc_name, tipo_query, "Pattern", budget, co2_act, t_patt, em_patt, req_patt.n_filters,req_patt.filters, parole_patt,file_trovato_pattern])

                # --- CARBON AWARE ---
                tempo_ca_tot=0
                for i in range(0,10):
                    req_ca = Request(testo_query)
                    start = time.perf_counter()
                    chain_ca.handle(req_ca, budget, co2_act, 0.0)
                    end = time.perf_counter()
                    t_ca = end - start
                    tempo_ca_tot += t_ca
                t_ca = tempo_ca_tot/10
                parole_ca = len(req_ca.entity) + len(req_ca.name) + len(req_ca.verbs)
                em_ca = calcola_emissioni(t_ca, POTENZA_WATT_COR, co2_act)
                res_ca = matcher.search(req_ca)
                if res_ca and res_ca['nome_file']== doc_name.replace(".pdf",""):
                    file_trovato_ca = True
                else:
                    file_trovato_ca = False
                risultati.append([doc_name, tipo_query, "CA", budget, co2_act, t_ca, em_ca, req_ca.n_filters,req_ca.filters, parole_ca,file_trovato_ca])

    # Salvataggio
    with open(FILE_CSV_OUT_INCR, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Documento", "Tipo_query", "Versione", "Budget", "CI", "Tempo_s", "CO2_Emessa_g", "Numero_filtri","Filtri_applicati","Parole_trovate","File_corretto_trovato"])
        writer.writerows(risultati)

    print(f" Test CoR completato! Risultati salvati in '{FILE_CSV_OUT_INCR}'")

if __name__ == "__main__":
    main_base()
    main_incr()