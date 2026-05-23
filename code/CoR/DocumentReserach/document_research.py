import os
import argparse
import database
from database_handler import DatabaseHandler
from matcher import Matcher
from request import Request
from pattern_ca.handler_ner import HandlerNER
from pattern_ca.handler_nomi import HandlerNames
from pattern_ca.handler_verbi import HandlerVerbs
from carbonprovider import CarbonProvider

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def configure_chain_of_responsibility():
    h_ner = HandlerNER()
    h_nomi = HandlerNames()
    h_verbi = HandlerVerbs()
    h_ner.set_next(h_nomi).set_next(h_verbi)
    return h_ner

def main():
    parser = argparse.ArgumentParser(description="Demo Document Research")
    parser.add_argument("--co2", type=float, default=100.0, help="Livello di CO2 attuale")
    parser.add_argument("--budget", type=float, default=0.005, help="Budget di CO2 a disposizione")
    args = parser.parse_args()

    print(f"Inizializzazione DocumentResearch -> CO2: {args.co2} | Budget: {args.budget}")

    provider = CarbonProvider()
    provider.set_co2_attuale(args.co2)
    db = database.DataBase()
    db_handler = DatabaseHandler(db)
    matcher = Matcher(db_handler)
    catena_ricerca = configure_chain_of_responsibility()

    print("\nSistema pronto. Modalità interattiva avviata. (Premi Ctrl+C o scrivi 'esci' per chiudere)")
    
    try:
        while True:
            print("\n" + "-"*50)
            query_utente = input("Cosa vuoi cercare? : ")
            
            if query_utente.lower() == 'esci':
                print("Chiusura del sistema...")
                break
            if not query_utente.strip():
                continue
            
            richiesta = Request(query_utente)
            catena_ricerca.handle(richiesta, args.budget, provider.get_co2(), total_cost=0)
            res = matcher.search(richiesta)
            
            print("\n=== RISULTATI DELLA RICERCA ===")
            if not res:
                print("Nessun documento trovato corrispondente alla tua ricerca.")
            else:
                print(f"{res['nome_file']} (Affinità: {res['score']})")
                print(f"   -> Match su: {res['parole_in_comune']}")
    except KeyboardInterrupt:
        print("\nChiusura del sistema...")

if __name__ == "__main__":
    main()