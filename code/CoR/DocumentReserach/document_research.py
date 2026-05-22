import datetime
import database
from database_handler import DatabaseHandler
from matcher import Matcher
from request import Request
from pattern_ca.handler_ner import HandlerNER
from pattern_ca.handler_nomi import HandlerNames
from pattern_ca.handler_verbi import HandlerVerbs
from carbonprovider import CarbonProvider



def configure_chain_of_responsibility():
    h_ner = HandlerNER()
    h_nomi = HandlerNames()
    h_verbi = HandlerVerbs()
    
    h_ner.set_next(h_nomi).set_next(h_verbi)
    return h_ner

def main():

    provider = CarbonProvider()
    provider.set_co2_attuale(100.0)
    db = database.DataBase()
    print(f"ho fatto il db handler")
    db_handler = DatabaseHandler(db)
    matcher = Matcher(db_handler)

    catena_ricerca = configure_chain_of_responsibility()
    while True:
        fatto = False
        while not fatto:
            temp= input("Inserisci il budget di CO2 : ")
            if temp == "":
                budgetCOR=0.005
                fatto = True
            else:
                try:
                    budgetCOR=float(temp)
                    fatto = True
                except ValueError:
                    print ("Input non valido")

        print("\n" + "-"*50)
        query_utente = input("Cosa vuoi cercare? (Scrivi 'esci' per chiudere): ")
        
        if query_utente.lower() == 'esci':
            print("Chiusura del sistema...")
            break
            
        if not query_utente.strip():
            continue
        
        co2=provider.get_co2()
        richiesta = Request(query_utente)
        catena_ricerca.handle(richiesta,budgetCOR,co2,total_cost=0)
        res = matcher.search(richiesta)
        print("\n=== RISULTATI DELLA RICERCA ===")
        if not res:
            print("Nessun documento trovato corrispondente alla tua ricerca.")
        else:
            print(f"{res['nome_file']} (Affinità: {res['score']})")
            print(f"   -> Match su: {res['parole_in_comune']}")


if __name__ == "__main__":
    main()