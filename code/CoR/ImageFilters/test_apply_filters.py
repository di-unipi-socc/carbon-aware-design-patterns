import time
import csv
import os
from plain import Plain
from filter_pattern import filter
from filter_ca import filter_ca
from request import Request

# ──────────────────────────────────────────────
# CONFIGURAZIONE PERCORSI ASSOLUTI
# ──────────────────────────────────────────────
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))

FILE_WORKLOAD_BASE = os.path.join(CURRENT_DIR, "workload_base.csv")
FILE_WORKLOAD_INCR = os.path.join(CURRENT_DIR, "workload_incr.csv")

DIR_OUT_BASE = os.path.join(PROJECT_ROOT, "results", "ImageFilters", "base_ttl")
DIR_OUT_INCR = os.path.join(PROJECT_ROOT, "results", "ImageFilters", "increased_ttl")

FILE_CSV_OUT_BASE = os.path.join(DIR_OUT_BASE, "risultati_finali_filtri.csv")
FILE_CSV_OUT_INCR = os.path.join(DIR_OUT_INCR, "risultati_finali_filtri.csv")
# ──────────────────────────────────────────────

N_ESECUZIONI = 1
POTENZA_WATT = 50.0
PLAIN_FILTRI = "resolution,saturation,blur,relighting"

def calcola_emissioni(tempo_sec: float, ci: float) -> float:
    energia_kwh = (POTENZA_WATT / 1000.0) * (tempo_sec / 3600.0)
    return energia_kwh * ci

def esegui_test(workload_file, output_file, dir_out, scenario_name):
    print(f"\n--- Avvio Test Scenario: {scenario_name} ---")
    
    try:
        with open(workload_file, mode="r") as f:
            workload = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f" [ERRORE] Workload '{workload_file}' non trovato. Esegui prima workload_generator.py!")
        return

    os.makedirs(dir_out, exist_ok=True)
    
    risultati_finali = []
    plain_instance   = Plain()

    for idx, item in enumerate(workload):
        img_name  = item["image_name"]
        budget    = float(item["budget"])
        ci        = float(item["carbon_intensity"])
        time_slot = item["time_slot"]

        print(f"[{idx + 1}/{len(workload)}] img={img_name} | budget={budget:.6f} | CI={ci}")

        for versione in ["plain", "pattern_standard", "ca_pattern"]:
            tempi, emissioni = [], []
            filtri_lista = ""

            for _ in range(N_ESECUZIONI):
                req = Request(img_name)
                req.applied_filters   = []
                req.n_applied_filters = 0
                start_time = time.perf_counter()

                if versione == "plain":
                    plain_instance.apply_filter(req)
                    numero_filtri = 4
                    filtri_lista = PLAIN_FILTRI
                elif versione == "pattern_standard":
                    output = filter(req)
                    numero_filtri = output.n_applied_filters
                    filtri_lista = ",".join(output.applied_filters) if output.applied_filters else ""
                elif versione == "ca_pattern":
                    output = filter_ca(req, ci, budget)
                    numero_filtri = output.n_applied_filters
                    filtri_lista = ",".join(output.applied_filters) if output.applied_filters else ""

                end_time = time.perf_counter()
                t_exec = end_time - start_time
                tempi.append(t_exec)
                emissioni.append(calcola_emissioni(t_exec, ci))

            risultati_finali.append({
                "TimeSlot":         time_slot,
                "Immagine":         img_name,
                "Versione":         versione,
                "Budget":           budget,
                "CI":               ci,
                "Tempo_s":          round(sum(tempi)     / N_ESECUZIONI, 10),
                "CO2_Emessa_g":     round(sum(emissioni) / N_ESECUZIONI, 10),
                "Numero_filtri":    numero_filtri,
                "Filtri_Applicati": filtri_lista,
            })

    # Salvataggio
    with open(output_file, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["TimeSlot", "Immagine", "Versione", "Budget", "CI",
                                            "Tempo_s", "CO2_Emessa_g", "Numero_filtri", "Filtri_Applicati"], delimiter=";")
        writer.writeheader()
        writer.writerows(risultati_finali)
    print(f" Completato! Risultati salvati in '{output_file}'.")


if __name__ == "__main__":
    print("=== ESECUZIONE TEST IMAGE FILTERS ===")
    esegui_test(FILE_WORKLOAD_BASE, FILE_CSV_OUT_BASE, DIR_OUT_BASE, "Base TTL")
    esegui_test(FILE_WORKLOAD_INCR, FILE_CSV_OUT_INCR, DIR_OUT_INCR, "Increased TTL")