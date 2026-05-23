import os
import time
import argparse
import sys
from coldstorage_ca import ColdStorage_ca
from coldstorage_realservice import ColdStorage_RealService
from carbonprovider import CarbonProvider

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "data", "database.csv")

def main():
    parser = argparse.ArgumentParser(description="Demo ColdStorage Carbon Aware")
    parser.add_argument("--co2", type=float, default=200.0, help="Livello attuale di CO2 (g/kWh)")
    parser.add_argument("--threshold", type=float, default=150.0, help="Soglia CO2")
    parser.add_argument("--ttl", type=float, default=3.0, help="TTL Base in secondi")
    args = parser.parse_args()

    print(f"Inizializzazione ColdStorage -> CO2: {args.co2} | Threshold: {args.threshold} | TTL: {args.ttl}")
    
    provider = CarbonProvider()
    provider.set_co2(args.co2)
    service = ColdStorage_RealService(DB_PATH)
    proxy_ca = ColdStorage_ca(service, provider, args.threshold, args.ttl)

    print("\nSistema pronto. Modalità interattiva avviata. (Premi Ctrl+C per uscire)")
    
    try:
        while True:
            print("\n" + "-"*40)
            op = input("Operazione ('correlazione' o 'anomalia'): ").strip().lower()
            if op not in ["correlazione", "anomalia", "esci"]:
                print("Operazione non valida.")
                continue
            if op == "esci": break

            sens_a = input("Sensore A (es. TD, TB, UM, CO): ").strip().upper()
            
            if op == "correlazione":
                sens_b = input("Sensore B: ").strip().upper()
                risultato = proxy_ca.calculate_correlation(op, sens_a, sens_b)
            else:
                risultato = proxy_ca.calculate_anomaly(op, sens_a)
                
            print(f"Risultato (Valore, Eta, TTL Corrente): {risultato}")
            
    except KeyboardInterrupt:
        print("\nChiusura del sistema...")

if __name__ == "__main__":
    main()