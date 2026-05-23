import csv
import random
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")
FILE_WORKLOAD = os.path.join(DATA_DIR, "workload_cella.csv")

NUM_RICHIESTE = 200

def genera_workload():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if os.path.exists(FILE_WORKLOAD):
        return
        
    sensori = ["TD", "TB", "UM", "CO"]
    tipi_operazione = ["correlazione", "anomalia"]

    print(f"Generazione di {NUM_RICHIESTE} richieste in corso...")

    with open(FILE_WORKLOAD, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["tipo", "sensore_a", "sensore_b"])

        for _ in range(NUM_RICHIESTE):
            tipo = random.choice(tipi_operazione)

            if tipo == "correlazione":
                s_a, s_b = random.sample(sensori, 2)
            else:
                s_a = random.choice(sensori)
                s_b = ""

            writer.writerow([tipo, s_a, s_b])

    print(f"✅ Workload salvato con successo in '{FILE_WORKLOAD}'.")

if __name__ == "__main__":
    genera_workload()