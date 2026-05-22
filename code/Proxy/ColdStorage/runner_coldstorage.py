import time
import csv
import json
import os

from coldstorage_realservice import ColdStorage_RealService
from plain import Plain
from cache_proxy import Cache_Proxy
from coldstorage_ca import ColdStorage_ca
from carbonprovider import CarbonProvider

# ──────────────────────────────────────────────
# CONFIGURAZIONE
# ──────────────────────────────────────────────
N_ITERAZIONI   = 1
POTENZA_WATT   = 50.0

THRESHOLDS     = [150.0, 200.0, 250.0]
TTLS           = [0.06,0.07,0.08,0.09,0.1,0.15]#0.06,0.07,0.08,0.09,0.1,0.15

DB_FILEPATH        = "database.csv"
WORKLOAD_FILEPATH  = "workload_cella.csv"
TIMESLOT_FILEPATH  = "time_slot.json"
TEMP_DB_PATH       = "_temp_slot_db.csv"


SLOT_SIZE = 70_000
SLOT_STEP = 35_000


# ──────────────────────────────────────────────
# CARICAMENTO DATI
# ──────────────────────────────────────────────
def carica_time_slots(filepath: str) -> list:
    with open(filepath) as f:
        return json.load(f)["data"]


def carica_workload(filepath: str) -> list:
    workload = []
    with open(filepath, newline="") as f:
        for row in csv.DictReader(f):
            req = {"tipo": row["tipo"]}
            if row["tipo"] == "correlazione":
                req["sensori"] = [row["sensore_a"], row["sensore_b"]]
            else:
                req["sensore"] = row["sensore_a"]
            workload.append(req)
    print(f"Workload: {len(workload)} richieste caricate da '{filepath}'.")
    return workload


def carica_database(filepath: str) -> tuple:

    print(f"Caricamento database '{filepath}' in memoria...")
    with open(filepath, newline="") as f:
        reader = csv.reader(f, delimiter=";")
        intestazione = next(reader)
        righe = list(reader)
    print(f"Database pronto: {len(righe):,} righe dati.\n")
    return intestazione, righe


def scrivi_slice(intestazione: list, righe: list,
                start: int, size: int, output_path: str) -> int:

    slice_righe = righe[start: start + size]
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(intestazione)
        writer.writerows(slice_righe)
    return len(slice_righe)


# ──────────────────────────────────────────────
# CALCOLO EMISSIONI
# ──────────────────────────────────────────────
def calcola_emissioni(tempo_sec: float, ci: float) -> float:
    energia_kwh = (POTENZA_WATT / 1000.0) * (tempo_sec / 3600.0)
    return energia_kwh * ci



def esegui_slot(versione: str, workload: list,
                threshold: float, ttl: float) -> list:
    righe_output = []

    for iterazione in range(1, N_ITERAZIONI + 1):
        
        mock_provider = CarbonProvider()
        
        if versione == "plain":
            service = Plain(filepath=TEMP_DB_PATH)
        elif versione == "pattern":
            service = Cache_Proxy(ColdStorage_RealService(filepath=TEMP_DB_PATH), ttl)
        elif versione == "pattern_ca":
            service = ColdStorage_ca(
                ColdStorage_RealService(filepath=TEMP_DB_PATH), mock_provider, threshold, ttl
            )
        
        for slot_idx, slot in enumerate(time_slots):
            slot_from  = slot["from"]
            co2_actual = float(slot["intensity"]["actual"])
            start_row  = slot_idx * SLOT_STEP
            mock_provider.set_co2(co2_actual)

            n_scritte = scrivi_slice(
                db_header, db_righe, start_row, SLOT_SIZE, TEMP_DB_PATH
            )
            print(f"    Slot {slot_from}  CO₂={co2_actual} gCO₂/kWh  "
                    f"DB righe {start_row:,}–{start_row + n_scritte - 1:,}")
            
            for req_num, req in enumerate(workload, start=1):

                start_t = time.perf_counter()

                if req["tipo"] == "correlazione":
                    raw = service.calculate_correlation(
                        "corr_test", req["sensori"][0], req["sensori"][1]
                    )
                else:
                    raw = service.calculate_anomaly("anom_test", req["sensore"])

                end_t = time.perf_counter()
                tempo_req  = end_t - start_t
                co2_emessa = calcola_emissioni(tempo_req, co2_actual)

                if versione == "plain":
                    valore, eta, ttl_corrente = raw, 0.0, 0.0
                else:
                    valore, eta, ttl_corrente = raw
                    eta          = float(eta)
                    ttl_corrente = float(ttl_corrente) if ttl_corrente is not None else 0.0

                righe_output.append({
                    "time_slot": slot_from,
                    "ci":co2_actual,
                    "numero_richiesta": req,
                    "valore":           float(valore) if valore is not None else "",
                    "eta":              eta,
                    "ttl_corrente":     ttl_corrente,
                    "tempo_sec":        tempo_req,
                    "co2_emessa":       co2_emessa,
                })

    return righe_output


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
time_slots          = carica_time_slots(TIMESLOT_FILEPATH)
workload            = carica_workload(WORKLOAD_FILEPATH)
db_header, db_righe = carica_database(DB_FILEPATH)
def main():

    versioni   = ["plain", "pattern", "pattern_ca"]
    fieldnames = [
        "versione", "time_slot", "numero_richiesta","ci",
        "threshold", "ttl",
        "valore", "eta", "ttl_corrente",
        "tempo_sec", "co2_emessa",
    ]

    righe_per_file = len(versioni) * len(time_slots) * N_ITERAZIONI * len(workload)

    file_csv = f"risultati_test.csv"
    with open(file_csv, "w", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for threshold in THRESHOLDS:
            for ttl in TTLS:

                print(f"\n{'='*54}")
                print(f"  TEST SUITE — TH={threshold} | TTL={ttl}")
                print(f"  Output: '{file_csv}'  ({righe_per_file:,} righe attese)")
                print(f"{'='*54}")

                for versione in versioni:
                    print(f"\n  ▶ Versione: {versione.upper()}")
                        
                    righe = esegui_slot(versione, workload, threshold, ttl)
                    for riga in righe:
                        writer.writerow({
                            "versione":  versione,
                            "threshold": int(threshold),
                            "ttl":       ttl,
                            **riga,
                        })

                print(f"\n  Salvato: '{file_csv}'")

    if os.path.exists(TEMP_DB_PATH):
        os.remove(TEMP_DB_PATH)

    print("\nTutti i test completati.")


if __name__ == "__main__":
    main()
