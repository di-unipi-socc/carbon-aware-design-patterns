import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import json
import os

# ──────────────────────────────────────────────
# STILE GLOBALE
# ──────────────────────────────────────────────
sns.set_theme(style="whitegrid")

plt.rcParams.update({
    # "text.usetex":  True,
    "font.family":  "serif",
    "font.serif":   ["Computer Modern Roman", "DejaVu Serif"],
    "mathtext.fontset": "cm",
})

# ──────────────────────────────────────────────
# CONFIGURAZIONE DEI PERCORSI
# ──────────────────────────────────────────────
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))

DIR_OUT_BASE = os.path.join(PROJECT_ROOT, "results", "DocumentResearch", "base_ttl")
DIR_OUT_INCR = os.path.join(PROJECT_ROOT, "results", "DocumentResearch", "increased_ttl")

FILE_CSV_BASE = os.path.join(DIR_OUT_BASE, "risultati_cor_base.csv")
FILE_CSV_INCR = os.path.join(DIR_OUT_INCR, "risultati_cor_incr.csv")

FILE_JSON_TIME = os.path.join(CURRENT_DIR, "time_slot.json")

# Configurazione base (comune a entrambi gli scenari)
CONFIG_COR = {
    "col_versione":     "Versione",
    "col_budget":       "Budget",
    "col_co2":          "CO2_Emessa_g",
    "col_filtri":       "Filtri_applicati",
    "versioni_ordine":  ["Plain", "Pattern", "CA"],
    "versioni_patt":    ["Pattern", "CA"],
    "palette": {
        "Plain":   "#b24541",
        "Pattern": "#e16f0b",
        "CA":      "#1a6498",
    },
    "labels": {
        "Plain":   "Plain",
        "Pattern": "Pattern Standard",
        "CA":      "Pattern CA",
    },
    "handlers":       ["NER", "NAME", "VERBS"],
    "handler_labels": ["NER", "NAME", "VERBS"],
    "prefix_output":  "cor",
    "titolo_g2":      "Andamento Emissioni CO2 al Variare del Budget\n",
}

def carica_dati(cfg: dict) -> pd.DataFrame:
    df = pd.read_csv(cfg["file"], sep=";")
    df[cfg["col_filtri"]] = df[cfg["col_filtri"]].fillna("").astype(str)
    return df

# ──────────────────────────────────────────────
# GRAFICO 1 — Emissioni medie per versione
# ──────────────────────────────────────────────
def grafico1_emissioni_medie(df: pd.DataFrame, cfg: dict):
    output = os.path.join(cfg["out_dir"], f"1_{cfg['prefix_output']}_emissioni_medie.pdf")

    medie = (
        df.groupby(cfg["col_versione"], sort=False)[cfg["col_co2"]]
        .mean()
        .reindex(cfg["versioni_ordine"])
        .reset_index()
    )
    medie["label"] = medie[cfg["col_versione"]].map(cfg["labels"])

    fig, ax = plt.subplots(figsize=(6.5, 4))
    bars = ax.bar(
        medie["label"],
        medie[cfg["col_co2"]],
        color=[cfg["palette"][v] for v in medie[cfg["col_versione"]]],
        alpha=1, width=0.5,
    )
    for bar in bars:
        h = bar.get_height()
        ax.annotate(
            f"{h:.6f}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 5), textcoords="offset points",
            ha="center", va="bottom", fontsize=8,
        )

    ax.set_title("Emissioni Medie di CO2", fontsize=11)
    ax.set_ylabel("CO2 Emessa", fontsize=9)
    ax.set_xlabel("Versione", fontsize=9)
    ax.set_ylim(0, medie[cfg["col_co2"]].max() * 1.2)
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f"Salvato: {output}")


# ──────────────────────────────────────────────
# GRAFICO 2 — Andamento emissioni al variare del budget
# ──────────────────────────────────────────────
def grafico2_emissioni_vs_budget(df: pd.DataFrame, cfg: dict):
    output = os.path.join(cfg["out_dir"], f"2_{cfg['prefix_output']}_emissioni_vs_budget.pdf")

    media_budget = (
        df.groupby([cfg["col_versione"], cfg["col_budget"]])[cfg["col_co2"]]
        .mean()
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8,5))
    for v in cfg["versioni_ordine"]:
        sub = media_budget[media_budget[cfg["col_versione"]] == v].sort_values(cfg["col_budget"])
        ax.plot(
            sub[cfg["col_budget"]], sub[cfg["col_co2"]],
            marker="o", linewidth=2.0,
            color=cfg["palette"][v], label=cfg["labels"][v],
        )

    ax.set_title(cfg["titolo_g2"], fontsize=11)
    ax.set_xlabel("Budget", fontsize=9)
    ax.set_ylabel("CO2 Emessa", fontsize=9)
    ax.legend(title="Versione", fontsize=8, title_fontsize=8)
    ax.xaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    
    # Usa i ticks passati dinamicamente
    plt.xticks(cfg["xticks"], fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f"Salvato: {output}")


# ──────────────────────────────────────────────
# GRAFICO 3 — Percentuale di esecuzione degli handler
# ──────────────────────────────────────────────
def grafico3_handler_percentuale(df: pd.DataFrame, cfg: dict):
    output = os.path.join(cfg["out_dir"], f"3_{cfg['prefix_output']}_handler_percentuale.pdf")

    pct_data = []
    for v in cfg["versioni_patt"]:
        sub   = df[df[cfg["col_versione"]] == v]
        total = len(sub)
        for h, hl in zip(cfg["handlers"], cfg["handler_labels"]):
            count = sub[cfg["col_filtri"]].str.contains(h, case=False, na=False).sum()
            pct_data.append({"versione": v, "handler": hl, "pct": count / total * 100})

    df_pct = pd.DataFrame(pct_data)
    x      = np.arange(len(cfg["handler_labels"]))
    width  = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    for i, v in enumerate(cfg["versioni_patt"]):
        sub    = df_pct[df_pct["versione"] == v]
        vals   = sub["pct"].values
        offset = (i - 0.5) * width
        bars   = ax.bar(x + offset, vals, width,
                        label=cfg["labels"][v], color=cfg["palette"][v], alpha=1)
        for bar, val in zip(bars, vals):
            ax.annotate(
                f"{val:.1f}%",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4), textcoords="offset points",
                ha="center", va="bottom", fontsize=8,
                color=cfg["palette"][v],
            )

    ax.set_title("Percentuale di Esecuzione degli Handler", fontsize=11)
    ax.set_ylabel("Frequenza di Esecuzione (%)", fontsize=9)
    ax.set_xlabel("Handler", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(cfg["handler_labels"], fontsize=8)
    ax.set_ylim(0, 115)
    ax.axhline(100, color="gray", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.legend(title="Versione", fontsize=8, title_fontsize=8)
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f"Salvato: {output}")


# ──────────────────────────────────────────────
# GRAFICO 4 — Andamento CO2 per time slot
# ──────────────────────────────────────────────
def grafico4_andamentoco2(cfg: dict):
    output = os.path.join(cfg["out_dir"], "4_andamentoco2.pdf")
    
    with open(FILE_JSON_TIME, "r", encoding="utf-8") as f:
        time_data = json.load(f)["data"]

    df_time = pd.DataFrame([{
        "time_slot": d["from"],
        "actual":    float(d["intensity"]["actual"])
    } for d in time_data])

    plt.figure(figsize=(8, 5))
    sns.lineplot(data=df_time, x="time_slot", y="actual", color="gray", linewidth=1.5)
    plt.scatter(data=df_time, x="time_slot", y="actual", c="blue", s=50, zorder=5)

    for _, row in df_time.iterrows():
        plt.annotate(
            f"{row['actual']:.0f}",
            xy=(row["time_slot"], row["actual"]),
            xytext=(0, 10), textcoords="offset points",
            ha="center", fontsize=8, color="black",
        )

    plt.title("Andamento Carbon Intensity", fontsize=11)
    plt.xlabel("Time Slot", fontsize=9)
    plt.ylabel("Carbon Intensity (gCO2/kWh)", fontsize=9)
    plt.xticks(rotation=45, fontsize=8)
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f"Salvato: {output}")


def grafico_risparmio_percentuale(df: pd.DataFrame, cfg: dict):
    output = os.path.join(cfg["out_dir"], f"5_{cfg['prefix_output']}_risparmio_percentuale.pdf")
    
    col_ver = cfg["col_versione"]
    col_co2 = cfg["col_co2"]
    
    totali = df.groupby(col_ver)[col_co2].sum()
    
    plain_tot = totali.get("Plain", 1)
    pattern_tot = totali.get("Pattern", 0)
    ca_tot = totali.get("CA", 0)
    
    risparmio_pattern = ((plain_tot - pattern_tot) / plain_tot) * 100
    risparmio_ca = ((plain_tot - ca_tot) / plain_tot) * 100
    
    dati_plot = pd.DataFrame({
        "Versione": ["Pattern", "CA"],
        "Risparmio (%)": [risparmio_pattern, risparmio_ca]
    })
    
    plt.figure(figsize=(8, 5))
    
    colori = [cfg["palette"].get("Pattern", "#e16f0b"), cfg["palette"].get("CA", "#1a6498")]
    
    ax = sns.barplot(data=dati_plot, x="Versione", y="Risparmio (%)", hue="Versione", palette=colori, legend=False)
    
    plt.axhline(0, color='black', linewidth=1.2)
    
    for p in ax.patches:
        height = p.get_height()
        offset = 5 if height >= 0 else 10
        va = 'bottom' if height >= 0 else 'top'
        
        ax.annotate(f"{height:.2f}%",
                    (p.get_x() + p.get_width() / 2., height),
                    ha='center', va=va,
                    xytext=(0, offset), textcoords='offset points',
                    fontsize=8)
                    
    plt.title("Risparmio di CO2 rispetto al Plain", fontsize=11)
    plt.xlabel("Versione", fontsize=9)
    plt.ylabel("Risparmio di CO2 (%)", fontsize=9)
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f"Salvato: {output}")


def grafico_handler_vs_budget(df, cfg):
    output = os.path.join(cfg["out_dir"], f"{cfg['prefix_output']}_handler_vs_budget.pdf")

    df_plot = df.groupby([cfg['col_budget'], cfg['col_versione']])['Numero_filtri'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(8, 5))

    sns.lineplot(data=df_plot, x=cfg['col_budget'], y='Numero_filtri', hue=cfg['col_versione'],
                palette=cfg['palette'], hue_order=cfg['versioni_ordine'], marker='o', linewidth=2, ax=ax)
    
    ax.set_title("Media di Handler Eseguiti vs Budget", fontsize=11)
    ax.set_xlabel("Budget", fontsize=9)
    ax.set_ylabel("Media Handler Eseguiti", fontsize=9)
    ax.legend(title="Versione", fontsize=8, title_fontsize=8)
    
    ax.xaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    
    # Usa i ticks dinamici
    plt.xticks(cfg["xticks"], fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f"Salvato: {output}")


def grafico_dual_axis_accuratezza_risparmio(df, cfg):
    output = os.path.join(cfg["out_dir"], f"{cfg['prefix_output']}_accuratezza_vs_risparmio_dual.pdf")

    plain_mean_co2 = df[df[cfg['col_versione']] == 'Plain'].groupby(cfg['col_budget'])[cfg['col_co2']].mean().reset_index()
    plain_mean_co2 = plain_mean_co2.rename(columns={cfg['col_co2']: 'CO2_Plain_Medio'})
    
    df_plot = df[df[cfg['col_versione']].isin(cfg['versioni_patt'])]
    
    agg_df = df_plot.groupby([cfg['col_budget'], cfg['col_versione']]).agg(
        Corretti_Totali=('File_corretto_trovato', 'sum'),
        Totale_Query=('File_corretto_trovato', 'count'),
        CO2_Media=(cfg['col_co2'], 'mean')
    ).reset_index()
    
    agg_df = pd.merge(agg_df, plain_mean_co2, on=cfg['col_budget'], how='left')
    
    agg_df['Risparmio_Medio'] = ((agg_df['CO2_Plain_Medio'] - agg_df['CO2_Media']) / agg_df['CO2_Plain_Medio']) * 100
    agg_df['Corretti_%'] = (agg_df['Corretti_Totali'] / agg_df['Totale_Query']) * 100
    
    ordine_versioni = ['Pattern', 'CA']
    
    fig, ax1 = plt.subplots(figsize=(9.5, 6.5))
    
    budgets = agg_df[cfg['col_budget']].unique()
    budgets.sort()
    min_dist = np.min(np.diff(budgets))
    bar_width = min_dist * 0.40
    
    for i, v in enumerate(ordine_versioni):
        sub = agg_df[agg_df[cfg['col_versione']] == v].sort_values(by=cfg['col_budget'])
        offset = (i - 0.5) * bar_width
        
        ax1.bar(
            sub[cfg['col_budget']] + offset,
            sub['Corretti_%'],
            width=bar_width,
            color=cfg['palette'][v],
            label=v,
            alpha=0.5
        )
        
    ax1.set_ylabel("Libri Corretti Trovati (%)", fontsize=9, color='#333333')
    ax1.set_xlabel("Budget", fontsize=9)
    ax1.set_ylim(-5, 110)
    
    ax1.xaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=True))
    ax1.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    
    # Usa i ticks dinamici
    plt.xticks(cfg["xticks"], fontsize=8)
    
    ax2 = ax1.twinx()
    
    for i, v in enumerate(ordine_versioni):
        sub = agg_df[agg_df[cfg['col_versione']] == v].sort_values(by=cfg['col_budget'])
        ax2.plot(
            sub[cfg['col_budget']],
            sub['Risparmio_Medio'],
            marker=['s', 'o'][i],
            linestyle=['-', '--'][i],
            color=cfg['palette'][v],
            label=v,
            linewidth=2.5, markersize=8
        )
    
    ax2.set_ylabel("Risparmio CO2 rispetto al Plain (%)", fontsize=9)
    ax2.set_ylim(-5, 110)
    
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2,
            loc='upper right', framealpha=0.9, fontsize=7, ncol=2)

    plt.title("Accuratezza vs Risparmio CO2", fontsize=11)
    ax2.grid(False)
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f"Salvato: {output}")


# ──────────────────────────────────────────────
# ENTRY POINT — Gestione scenari (Base e Incr)
# ──────────────────────────────────────────────
def genera_grafici_cor():
    print("=== GRAFICI CORREZIONE (NLP) ===")
    
    scenari = [
        {
            "nome": "Budget Base",
            "file_input": FILE_CSV_BASE,
            "dir_output": DIR_OUT_BASE,
            "xticks": [0.000009, 0.0000142, 0.000024, 0.000034, 0.0000435, 0.000053, 0.000063, 0.000073]
        },
        {
            "nome": "Budget Incrementato",
            "file_input": FILE_CSV_INCR,
            "dir_output": DIR_OUT_INCR,
            "xticks": [0.000024, 0.000031, 0.000038, 0.000046, 0.000053, 0.000060, 0.000067, 0.000073]
        }
    ]

    for scenario in scenari:
        print(f"\n--- Elaborazione Scenario: {scenario['nome']} ---")
        
        if not os.path.exists(scenario["file_input"]):
            print(f" [AVVISO] File '{scenario['file_input']}' non trovato. Salto lo scenario.")
            continue
            
        os.makedirs(scenario["dir_output"], exist_ok=True)
        
        cfg_attuale = CONFIG_COR.copy()
        cfg_attuale["file"] = scenario["file_input"]
        cfg_attuale["out_dir"] = scenario["dir_output"]
        cfg_attuale["xticks"] = scenario["xticks"]
        
        df = carica_dati(cfg_attuale)
        print(f"   {len(df):,} righe caricate.")

        grafico1_emissioni_medie(df, cfg_attuale)
        grafico2_emissioni_vs_budget(df, cfg_attuale)
        grafico3_handler_percentuale(df, cfg_attuale)
        grafico4_andamentoco2(cfg_attuale)
        grafico_risparmio_percentuale(df, cfg_attuale)
        grafico_handler_vs_budget(df, cfg_attuale)
        grafico_dual_axis_accuratezza_risparmio(df, cfg_attuale)

    print("\n Tutti i grafici sono stati generati con successo nei rispettivi percorsi!")

if __name__ == "__main__":
    genera_grafici_cor()