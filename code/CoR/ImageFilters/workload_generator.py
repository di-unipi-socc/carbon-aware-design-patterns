import csv
import json
import os
from itertools import product

FILE_WORKLOAD = "workload_immagini_completo.csv"
NUM_IMMAGINI  = 10
TIMESLOT_PATH = "time_slot.json"

BUDGETS = [0.005, 0.006907, 0.008814, 0.010721, 0.012629, 0.014536, 0.016443, 0.01835]
"""     0.0000047,   # minimo
    0.0000589,
    0.0001188,
    0.0003246,
    0.0009338,
    0.0045347,
    0.0094174,
    0.01835,   # massimo """

def genera_workload():
    if os.path.exists(FILE_WORKLOAD):
        print(f"Il file '{FILE_WORKLOAD}' esiste già. Eliminalo per rigenerarlo.")
        return

    with open(TIMESLOT_PATH, "r", encoding="utf-8") as f:
        time_slots = json.load(f)["data"]

    immagini = [f"immagine{i}.jpeg" for i in range(1, NUM_IMMAGINI + 1)]

    righe = []
    for slot in time_slots:
        for img, budget in product(immagini, BUDGETS):
            righe.append({
                "time_slot":       slot["from"],
                "carbon_intensity": slot["intensity"]["actual"],
                "image_name":      img,
                "budget":          budget
            })

    with open(FILE_WORKLOAD, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["time_slot", "carbon_intensity", "image_name",
                                            "budget"])
        writer.writeheader()
        writer.writerows(righe)

    print(f"Workload generato: {len(righe)} combinazioni "
        f"({len(time_slots)} slot × {NUM_IMMAGINI} immagini × {len(BUDGETS)} budget) "
        f"in '{FILE_WORKLOAD}'.")


if __name__ == "__main__":
    genera_workload()
