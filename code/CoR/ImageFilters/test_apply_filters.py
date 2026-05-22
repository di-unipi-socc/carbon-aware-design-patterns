import time
import csv
import os
from plain import Plain
from filter_ca import filter_ca
from filter import filter
from request import Request

# ──────────────────────────────────────────────
# CONFIGURAZIONE
# ──────────────────────────────────────────────
N_ESECUZIONI = 1
POTENZA_WATT = 50.0

PLAIN_FILTRI = "resolution,saturation,blur,relighting"


def calcola_emissioni(tempo_sec: float, ci: float) -> float:
    energia_kwh = (POTENZA_WATT / 1000.0) * (tempo_sec / 3600.0)
    return energia_kwh * ci


def esegui_test():
    # ── Caricamento workload ──────────────────────────────────────────────
    try:
        with open("workload_immagini_completo.csv", mode="r") as f:
            workload = list(csv.DictReader(f))
    except FileNotFoundError:
        print(" Workload non trovato. Esegui prima workload_generator.py!")
        return

    print(f"Caricate {len(workload)} righe dal workload.")

    risultati_finali = []
    plain_instance   = Plain()

    for idx, item in enumerate(workload):
        img_name  = item["image_name"]
        budget    = float(item["budget"])
        ci        = float(item["carbon_intensity"])
        time_slot = item["time_slot"]

        print(f"[{idx + 1}/{len(workload)}] slot={time_slot} | img={img_name} "
            f"| budget={budget:.7f} | CI={ci}")

        for versione in ["plain", "pattern_standard", "ca_pattern"]:

            tempi         = []
            emissioni     = []
            filtri_lista  = ""

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

    # ── Salvataggio risultati ─────────────────────────────────────────────
    output_file = "risultati_finali_filtri.csv"
    with open(output_file, mode="w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["TimeSlot", "Immagine", "Versione", "Budget", "CI",
                        "Tempo_s", "CO2_Emessa_g","Numero_filtri", "Filtri_Applicati"],
            delimiter=";"
        )
        writer.writeheader()
        writer.writerows(risultati_finali)

    print(f"\n Completato! {len(risultati_finali)} righe salvate in '{output_file}'.")


if __name__ == "__main__":
    esegui_test()
