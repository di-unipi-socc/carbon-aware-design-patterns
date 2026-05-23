import csv
import time
import datetime
import os

from doc_resume import Document_resume
from real_resumer import Resumer_RealService
from plain_resumer import ProxyResumer as PlainResumer
from proxy_resumer_pattern import ProxyResumer as PatternResumer
from proxy_resumer_ca import Resumer_CarbonAware as CAResumer
from carbonprovider import CarbonProvider

# ──────────────────────────────────────────────
# CONFIGURAZIONE PERCORSI ASSOLUTI
# ──────────────────────────────────────────────
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))

DATA_DIR = os.path.join(CURRENT_DIR, "data")
DIR_OUT = os.path.join(PROJECT_ROOT, "results", "DocumentResumer")

WORKLOAD_FILE = os.path.join(DATA_DIR, "workload_libri.csv")
OUTPUT_FILE   = os.path.join(DIR_OUT, "risultati_resumer.csv")
# ──────────────────────────────────────────────

POTENZA_WATT = 50.0
THRESHOLDS   = [150, 200, 250]
BASE_DATE = datetime.date(2024, 1, 1)

def orario_to_datetime(orario_str: str) -> datetime.datetime:
    h, m = map(int, orario_str.split(":"))
    return datetime.datetime.combine(BASE_DATE, datetime.time(h, m))

def calcola_emissioni(tempo_sec: float, ci: float) -> float:
    energia_kwh = (POTENZA_WATT / 1000.0) * (tempo_sec / 3600.0)
    return energia_kwh * ci

def crea_documento(book_name: str, author: str) -> Document_resume:
    doc = Document_resume(book_name,author)
    return doc

def esegui_test():
    os.makedirs(DIR_OUT, exist_ok=True)

    try:
        with open(WORKLOAD_FILE, newline="", encoding="utf-8") as f:
            workload = list(csv.DictReader(f, delimiter=";"))
    except FileNotFoundError:
        print(f" [ERRORE] '{WORKLOAD_FILE}' non trovato. Esegui prima workload_generator_virtual.py!")
        return

    print(f" {len(workload)} richieste caricate dal workload.\n")
    print(" Caricamento modello LLM...")
    real_resumer = Resumer_RealService()
    print(" Modello pronto.\n")

    risultati = []

    for threshold in THRESHOLDS:
        print(f"\n{'='*58}")
        print(f"  THRESHOLD = {threshold} gCO₂/kWh")
        print(f"{'='*58}")

        for versione in ["plain", "pattern", "ca"]:
            print(f"\n   Versione: {versione.upper()}")

            provider = CarbonProvider()

            if versione == "plain":
                proxy = PlainResumer(real_resumer)
            elif versione == "pattern":
                proxy = PatternResumer(real_resumer)
            else:  # ca
                proxy = CAResumer(real_resumer, provider, threshold)

            documenti: dict[str, Document_resume] = {}
            
            slot_keys = []
            slot_map  = {}
            for riga in workload:
                k = riga["time_slot"]
                if k not in slot_map:
                    slot_keys.append(k)
                    slot_map[k] = []
                slot_map[k].append(riga)

            for slot_from in slot_keys:
                richieste = slot_map[slot_from]
                actual_ci    = float(richieste[0]["actual_ci"])
                forecast_ci  = float(richieste[0]["forecast_ci"])
                forecast_time_str = richieste[0]["forecast_time"]
                now_dt       = orario_to_datetime(slot_from)
                forecast_dt  = orario_to_datetime(forecast_time_str)

                provider.set_co2_attuale(now_dt, actual_ci)
                provider.set_forecast(forecast_dt, forecast_ci)

                print(f"\n    Slot {slot_from} | CI={actual_ci} | Forecast {forecast_time_str}: {forecast_ci}")

                for riga in richieste:
                    book_name = riga["book_name"]
                    author    = riga["author"]

                    if book_name not in documenti:
                        documenti[book_name] = crea_documento(book_name, author)
                    doc = documenti[book_name]

                    resume_vuoto_prima = (doc.resume == "")
                    in_coda_prima      = (versione == "ca" and book_name in proxy.delayed_doc)

                    start = time.perf_counter()
                    proxy.resume(doc)
                    end   = time.perf_counter()
                    tempo = end - start
                    co2   = calcola_emissioni(tempo, actual_ci)

                    if versione in ("plain", "pattern"):
                        stato = "eseguito"
                    else:
                        if book_name in proxy.delayed_doc:
                            stato = "posticipato"
                        elif in_coda_prima and book_name not in proxy.delayed_doc:
                            stato = "eseguito"
                        elif doc.resume != "" and resume_vuoto_prima:
                            stato = "eseguito"
                        else:
                            stato = "eseguito"

                    print(f"      [{stato.upper():12s}] {book_name} ({riga['tipo']})")

                    risultati.append({
                        "threshold":        threshold,
                        "versione":         versione,
                        "time_slot":        slot_from,
                        "book_name":        book_name,
                        "tipo":             riga["tipo"],
                        "stato":            stato,
                        "actual_ci":        actual_ci,
                        "forecast_time":    forecast_time_str,
                        "forecast_ci":      forecast_ci,
                        "tempo_sec":        tempo,
                        "co2_emessa_g":     co2,
                    })

    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["threshold", "versione", "time_slot", "book_name", "tipo",
                        "stato", "actual_ci", "forecast_time", "forecast_ci",
                        "tempo_sec", "co2_emessa_g"],
            delimiter=";"
        )
        writer.writeheader()
        writer.writerows(risultati)

    n_per_suite = len(workload)
    print(f"\n Test completato! {len(risultati)} righe salvate in '{OUTPUT_FILE}'.")
    print(f"   ({len(THRESHOLDS)} threshold × 3 versioni × {n_per_suite} richieste/slot)")

if __name__ == "__main__":
    esegui_test()