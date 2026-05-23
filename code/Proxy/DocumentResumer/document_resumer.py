import os
import argparse
import datetime
from database import DataBase
from database_handler import DatabaseHandler
from carbonprovider import CarbonProvider
from real_resumer import Resumer_RealService
from proxy_resumer_ca import Resumer_CarbonAware

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    parser = argparse.ArgumentParser(description="Demo Document Resumer")
    parser.add_argument("--co2", type=float, default=300.0, help="Livello di CO2 attuale")
    parser.add_argument("--forecast", type=float, default=100.0, help="Previsione CI futuro")
    parser.add_argument("--threshold", type=float, default=200.0, help="Soglia CO2 per processare")
    args = parser.parse_args()

    print(f"Inizializzazione DocumentResumer -> CO2: {args.co2} | Forecast: {args.forecast} | Threshold: {args.threshold}")

    provider = CarbonProvider()
    provider.set_co2_attuale(datetime.datetime.now(), args.co2)
    orarioforecast = datetime.datetime.now() + datetime.timedelta(seconds=5)
    provider.set_forecast(orarioforecast, args.forecast)

    real_resumer = Resumer_RealService()
    proxy_resumer = Resumer_CarbonAware(real_resumer, provider, args.threshold)
    db = DataBase()
    db_handler = DatabaseHandler(proxy_resumer, db)

    print("\nistema pronto. Modalità interattiva avviata. (Premi Ctrl+C per chiudere)")

    try:
        while True:
            print("\n" + "-"*50)
            # Ripristina i valori di forecast fittizi per ogni iterazione della demo
            orarioforecast = datetime.datetime.now() + datetime.timedelta(seconds=5)
            provider.set_forecast(time=orarioforecast, intensity=args.forecast)
            provider.set_co2_attuale(datetime.datetime.now(), args.co2)
            
            book = input("Nome del libro da riassumere: ")
            if book.lower() == 'esci': break
            author = input("Autore del libro: ")
            
            resume = db_handler.get_resume(book, author)
            print("\n📝 RIASSUNTO:")
            print(f"{resume}")
            
    except KeyboardInterrupt:
        print("\nChiusura del sistema...")

if __name__ == "__main__":
    main()