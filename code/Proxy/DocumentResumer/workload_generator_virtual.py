import csv
import json
import os

# --- CONFIGURAZIONE PERCORSI ASSOLUTI ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")

BOOKS_FILE    = os.path.join(DATA_DIR, "lista_libri.csv")
TIMESLOT_FILE = os.path.join(DATA_DIR, "time_slot.json")
OUTPUT_FILE   = os.path.join(DATA_DIR, "workload_libri.csv")
# ----------------------------------------

def genera_workload():
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(OUTPUT_FILE):
        print(f"⚠️  '{OUTPUT_FILE}' esiste già. Eliminalo per rigenerarlo.")
        return

    with open(BOOKS_FILE, newline="", encoding="utf-8") as f:
        libri = list(csv.DictReader(f, delimiter=";"))
        print(f"Libri caricati: {len(libri)}")
    
    gruppi = [libri[i:i+5] for i in range(0, len(libri), 5)]

    with open(TIMESLOT_FILE, encoding="utf-8") as f:
        slots = json.load(f)["data"]

    if len(gruppi) != len(slots):
        raise ValueError(
            f"Gruppi ({len(gruppi)}) != slot ({len(slots)}). "
            "Verifica lista_libri.csv e time_slot.json."
        )

    # ── Costruzione righe del workload ─────────────────────────────────────
    righe = []
    for idx, slot in enumerate(slots):
        slot_from   = slot["from"]
        slot_to     = slot["to"]
        actual_ci   = slot["intensity"]["actual"]
        forecast_ci = slot["intensity"]["forecast"]

        # Libri correnti di questo slot
        for libro in gruppi[idx]:
            righe.append({
                "time_slot":     slot_from,
                "forecast_time": slot_to,
                "actual_ci":     actual_ci,
                "forecast_ci":   forecast_ci,
                "book_name":     libro["Nome"],
                "author":        libro["Autore"],
                "tipo":          "corrente",
            })

        # Libri del slot precedente (ri-richiesti), assenti nel primo slot
        if idx > 0:
            for libro in gruppi[idx - 1]:
                righe.append({
                    "time_slot":     slot_from,
                    "forecast_time": slot_to,
                    "actual_ci":     actual_ci,
                    "forecast_ci":   forecast_ci,
                    "book_name":     libro["Nome"],
                    "author":        libro["Autore"],
                    "tipo":          "precedente",
                })

    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["time_slot", "forecast_time", "actual_ci",
                        "forecast_ci", "book_name", "author", "tipo"],
            delimiter=";"
        )
        writer.writeheader()
        writer.writerows(righe)

    print(f"✅ Workload generato: {len(righe)} richieste in '{OUTPUT_FILE}'.")
    for idx, slot in enumerate(slots):
        correnti   = [l["Nome"] for l in gruppi[idx]]
        precedenti = [l["Nome"] for l in gruppi[idx - 1]] if idx > 0 else []
        tot = len(correnti) + len(precedenti)
        print(f"   {slot['from']}: {tot} richieste → correnti={correnti}"
            + (f" | precedenti={precedenti}" if precedenti else ""))

if __name__ == "__main__":
    genera_workload()