import csv
import json
import os
from itertools import product

# --- CONFIGURAZIONE PERCORSI ASSOLUTI ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TIMESLOT_PATH = os.path.join(CURRENT_DIR, "time_slot.json")

FILE_WORKLOAD_BASE = os.path.join(CURRENT_DIR, "workload_base.csv")
FILE_WORKLOAD_INCR = os.path.join(CURRENT_DIR, "workload_incr.csv")
# ----------------------------------------

NUM_IMMAGINI  = 10

BUDGETS_INCR = [0.005, 0.006907, 0.008814, 0.010721, 0.012629, 0.014536, 0.016443, 0.01835]
BUDGET_BASE = [0.0000047, 0.0000589, 0.0001188, 0.0003246, 0.0009338, 0.0045347, 0.0094174, 0.01835]

def genera_workload(file_out, budgets):
    with open(TIMESLOT_PATH, "r", encoding="utf-8") as f:
        time_slots = json.load(f)["data"]

    immagini = [f"immagine{i}.jpeg" for i in range(1, NUM_IMMAGINI + 1)]
    righe = []
    
    for slot in time_slots:
        for img, budget in product(immagini, budgets):
            righe.append({
                "time_slot":       slot["from"],
                "carbon_intensity": slot["intensity"]["actual"],
                "image_name":      img,
                "budget":          budget
            })

    with open(file_out, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["time_slot", "carbon_intensity", "image_name", "budget"])
        writer.writeheader()
        writer.writerows(righe)

    print(f" Workload generato in '{os.path.basename(file_out)}' ({len(righe)} combinazioni).")

if __name__ == "__main__":
    print("=== GENERAZIONE WORKLOAD IMAGE FILTERS ===")
    genera_workload(FILE_WORKLOAD_BASE, BUDGET_BASE)
    genera_workload(FILE_WORKLOAD_INCR, BUDGETS_INCR)