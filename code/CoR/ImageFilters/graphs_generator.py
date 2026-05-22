import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import json

# ──────────────────────────────────────────────
# STILE GLOBALE
# ──────────────────────────────────────────────
sns.set_theme(style="whitegrid")

# ──────────────────────────────────────────────
# FONT LATEX-COMPATIBILE
# Per LaTeX completo (richiede LaTeX installato): decommentare text.usetex
# Nota: con text.usetex=True usare r'\%' al posto di '%' nelle stringhe
# ──────────────────────────────────────────────
plt.rcParams.update({
    # "text.usetex":  True,
    "font.family":  "serif",
    "font.serif":   ["Computer Modern Roman", "DejaVu Serif"],
    "mathtext.fontset": "cm",
})

PALETTE = {
    "plain":            "#b24541",
    "pattern_standard": "#e16f0b",
    "ca_pattern":       "#1a6498",
}
LABELS = {
    "plain":            "Plain",
    "pattern_standard": "Pattern Standard",
    "ca_pattern":       "Pattern CA",
}
HANDLERS       = ["resolution", "saturation", "blur", "relighting"]
HANDLER_LABELS = ["Resolution", "Saturation", "Blur", "Relighting"]


def carica_dati(path: str = "risultati_finali_filtri.csv") -> pd.DataFrame:
    df = pd.read_csv(path, sep=";")
    df["Filtri_Applicati"] = df["Filtri_Applicati"].fillna("")
    return df


# ──────────────────────────────────────────────
# GRAFICO 1 — Emissioni medie per versione
# ──────────────────────────────────────────────
def grafico1_emissioni_medie(df: pd.DataFrame, output: str = "1_emissioni_medie.pdf"):
    medie = (
        df.groupby("Versione", sort=False)["CO2_Emessa_g"]
        .mean()
        .reindex(["plain", "pattern_standard", "ca_pattern"])
        .reset_index()
    )
    medie["label"] = medie["Versione"].map(LABELS)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        medie["label"],
        medie["CO2_Emessa_g"],
        color=[PALETTE[v] for v in medie["Versione"]],
        alpha=1, width=0.5,
    )
    for bar in bars:
        h = bar.get_height()
        ax.annotate(
            f"{h:.6f}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 5), textcoords="offset points",
            ha="center", va="bottom", fontsize=8
        )
    ax.set_title("Emissioni Medie di CO2 per Versione", fontsize=11)
    ax.set_ylabel("CO2 Emessa Media", fontsize=9)
    ax.set_xlabel("Versione", fontsize=9)
    ax.set_ylim(0, medie["CO2_Emessa_g"].max() * 1.2)
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f"Salvato: {output}")


# ──────────────────────────────────────────────
# GRAFICO 2 — Andamento emissioni al variare del budget
# ──────────────────────────────────────────────
def grafico2_emissioni_vs_budget(df: pd.DataFrame, output: str = "2_emissioni_vs_budget.pdf"):
    media_budget = (
        df.groupby(["Versione", "Budget"])["CO2_Emessa_g"]
        .mean()
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    for v in ["plain", "pattern_standard", "ca_pattern"]:
        sub = media_budget[media_budget["Versione"] == v].sort_values("Budget")
        ax.plot(
            sub["Budget"], sub["CO2_Emessa_g"],
            marker="o", linewidth=2.0,
            color=PALETTE[v], label=LABELS[v],
        )

    ax.set_title("Andamento Emissioni CO2 al Variare del Budget", fontsize=11)
    ax.set_xlabel("Budget", fontsize=9)
    ax.set_ylabel("CO2 Emessa Media", fontsize=9)
    ax.legend(title="Versione", fontsize=8, title_fontsize=8)
    ax.xaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    plt.xticks([0.005, 0.006907, 0.008814, 0.010721, 0.012629, 0.014536, 0.016443, 0.01835], fontsize=8)#0.01, 0.01119, 0.01238,0.01357,0.01477,0.01596,0.01715,0.01835.....0.0000047,0.0009338,0.0045347,0.0094174,0.01835
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f"Salvato: {output}")


# ──────────────────────────────────────────────
# GRAFICO 3 — Percentuale di esecuzione degli handler
# ──────────────────────────────────────────────
def grafico3_handler_percentuale(df: pd.DataFrame, output: str = "3_handler_percentuale.pdf"):
    versioni_cache = ["pattern_standard", "ca_pattern"]
    pct_data = []

    for v in versioni_cache:
        sub   = df[df["Versione"] == v]
        total = len(sub)
        for h, hl in zip(HANDLERS, HANDLER_LABELS):
            count = sub["Filtri_Applicati"].str.contains(h, na=False).sum()
            pct_data.append({"versione": v, "handler": hl, "pct": count / total * 100})

    df_pct = pd.DataFrame(pct_data)
    x      = np.arange(len(HANDLER_LABELS))
    width  = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    for i, v in enumerate(versioni_cache):
        sub    = df_pct[df_pct["versione"] == v]
        vals   = sub["pct"].values
        offset = (i - 0.5) * width
        bars   = ax.bar(x + offset, vals, width,
                        label=LABELS[v], color=PALETTE[v], alpha=1)
        for bar, val in zip(bars, vals):
            ax.annotate(
                f"{val:.1f}%",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4), textcoords="offset points",
                ha="center", va="bottom", fontsize=8,
                color=PALETTE[v],
            )

    ax.set_title("Percentuale di Esecuzione degli Handler", fontsize=11)
    ax.set_ylabel("Frequenza di Esecuzione (%)", fontsize=9)
    ax.set_xlabel("Handler", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(HANDLER_LABELS, fontsize=8)
    ax.set_ylim(0, 115)
    ax.axhline(100, color="gray", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.legend(title="Versione", fontsize=8, title_fontsize=8)
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f"Salvato: {output}")

def grafico4_andamentoco2(df: pd.DataFrame, output: str = "4_andamentoco2.pdf"):
    with open('time_slot.json', 'r', encoding='utf-8') as f:
        time_data = json.load(f)['data']
    
    df_time = pd.DataFrame([{
        'time_slot': d['from'],
        'actual': float(d['intensity']['actual'])
    } for d in time_data])
    plt.figure(figsize=(6.5, 4))
    sns.lineplot(data=df_time, x='time_slot', y='actual', color='gray', linewidth=1.5)

    plt.scatter(data=df_time, x='time_slot', y='actual', c='#1a6498', s=50, zorder=5)
    for index, row in df_time.iterrows():
        plt.annotate(
            f"{row['actual']:.0f}",
            xy=(row['time_slot'], row['actual']),
            xytext=(0, 10),
            textcoords="offset points",
            ha='center',
            fontsize=8,
            color='black'
        )
    plt.title("Andamento Carbon Intensity", fontsize=11)
    plt.xlabel("Time Slot", fontsize=9)
    plt.ylabel("Carbon Intensity(gCO2/kWh)", fontsize=9)
    plt.xticks(rotation=45, fontsize=8)
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    return

# ──────────────────────────────────────────────
# GRAFICO 5 — Risparmio Percentuale Emissioni (rispetto a Plain)
# ──────────────────────────────────────────────
def grafico5_risparmio_percentuale(df: pd.DataFrame, output: str = "5_risparmio_percentuale.pdf"):
    totali = df.groupby("Versione")["CO2_Emessa_g"].sum()
    
    plain_tot = totali.get("plain", 1)
    pattern_tot = totali.get("pattern_standard", 0)
    ca_tot = totali.get("ca_pattern", 0)
    
    risparmio_pattern = ((plain_tot - pattern_tot) / plain_tot) * 100
    risparmio_ca = ((plain_tot - ca_tot) / plain_tot) * 100
    
    dati_plot = pd.DataFrame({
        "Versione_Label": [LABELS["pattern_standard"], LABELS["ca_pattern"]],
        "Risparmio (%)": [risparmio_pattern, risparmio_ca]
    })
    
    plt.figure(figsize=(6.5, 4))
    
    colori = [PALETTE["pattern_standard"], PALETTE["ca_pattern"]]
    
    ax = sns.barplot(data=dati_plot, x="Versione_Label", y="Risparmio (%)",
                    hue="Versione_Label", palette=colori, legend=False)
    
    plt.axhline(0, color='black', linewidth=1.2)
    
    for p in ax.patches:
        height = p.get_height()
        offset = 5 if height >= 0 else -10
        va = 'bottom' if height >= 0 else 'top'
        
        ax.annotate(f"{height:.2f}%",
                    (p.get_x() + p.get_width() / 2., height),
                    ha='center', va=va,
                    xytext=(0, offset), textcoords='offset points',
                    fontsize=8)
                    
    plt.title("Risparmio di CO2 rispetto al Plain", fontsize=11)
    plt.xlabel("Versione", fontsize=9)
    plt.ylabel("Risparmio di CO2 (%)", fontsize=9)
    
    plt.ylim(-5, 100)
    
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f"Salvato: {output}")

def grafico6_handler_vs_budget(df: pd.DataFrame, output: str = "6_handler_vs_budget.pdf"):
    df_plot = df.groupby(["Budget", "Versione"])["Numero_filtri"].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    sns.lineplot(
        data=df_plot, x="Budget", y="Numero_filtri", hue="Versione",
        palette=PALETTE, hue_order=["plain", "pattern_standard", "ca_pattern"],
        marker='o', linewidth=2, ax=ax
    )
    
    ax.set_title("Media di Handler Eseguiti vs Budget", fontsize=11)
    ax.set_xlabel("Budget", fontsize=9)
    ax.set_ylabel("Media Handler Eseguiti", fontsize=9)
    
    ax.xaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    plt.xticks([0.005, 0.006907, 0.008814, 0.010721, 0.012629, 0.014536, 0.016443, 0.01835], fontsize=8)
    
    handles, labels = ax.get_legend_handles_labels()
    mapped_labels = [LABELS.get(l, l) for l in labels]
    ax.legend(handles, mapped_labels, title="Versione", fontsize=8, title_fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f"Salvato: {output}")

# ──────────────────────────────────────────────
# GRAFICO 7 — Curve di Trade-off: Handler (%) vs Risparmio CO2 (%)
# ──────────────────────────────────────────────
def grafico8_curve_handler_risparmio(df: pd.DataFrame, output: str = "7_curve_handler_risparmio.pdf"):
    # ── Preparazione dati risparmio CO2 ──────────────────────────────────────
    plain_df = (
        df[df["Versione"] == "plain"]
        .groupby("Budget")["CO2_Emessa_g"]
        .mean()
        .reset_index()
        .rename(columns={"CO2_Emessa_g": "CO2_Plain_Medio"})
    )

    df_cache = df[df["Versione"].isin(["pattern_standard", "ca_pattern"])]

    agg_df = df_cache.groupby(["Budget", "Versione"]).agg(
        Handler_Medi=("Numero_filtri", "mean"),
        CO2_Media=("CO2_Emessa_g", "mean")
    ).reset_index()

    agg_df = pd.merge(agg_df, plain_df, on="Budget", how="left")
    agg_df["Risparmio_%"]  = ((agg_df["CO2_Plain_Medio"] - agg_df["CO2_Media"]) / agg_df["CO2_Plain_Medio"]) * 100
    agg_df["Handler_%"]    = (agg_df["Handler_Medi"] / 4.0) * 100
    agg_df = agg_df.sort_values(by=["Versione", "Budget"])

    budgets    = sorted(agg_df["Budget"].unique())
    versioni   = ["pattern_standard", "ca_pattern"]
    n_budgets  = len(budgets)
    n_versioni = len(versioni)

    # ── Layout barre raggruppate ──────────────────────────────────────────────
    bar_total_width = 0.6
    bar_w           = bar_total_width / n_versioni
    x               = np.arange(n_budgets)

    fig, ax1 = plt.subplots(figsize=(9, 6))
    ax2 = ax1.twinx()

    # ── Asse sinistro: istogramma Handler % ───────────────────────────────────
    for i, v in enumerate(versioni):
        sub    = agg_df[agg_df["Versione"] == v].sort_values("Budget")
        vals   = sub["Handler_%"].values
        offset = (i - (n_versioni - 1) / 2) * bar_w
        bars   = ax1.bar(
            x + offset, vals, bar_w,
            label=f"{LABELS[v]} - Handler",
            color=PALETTE[v], alpha=0.60,
        )

    # ── Asse destro: linee Risparmio CO2 % ───────────────────────────────────
    for v in versioni:
        sub = agg_df[agg_df["Versione"] == v].sort_values("Budget")
        ax2.plot(
            x, sub["Risparmio_%"].values,
            color=PALETTE[v], marker="o", linewidth=2.5,
            linestyle="--", markersize=7,
            label=f"{LABELS[v]} - CO2 saving",
        )

    # ── Etichette assi e titolo ───────────────────────────────────────────────
    ax1.set_title("Percentuale di esecuzione vs Risparmio", fontsize=11)
    ax1.set_xlabel("Budget", fontsize=9)
    ax1.set_ylabel("Esecuzione Handler (%)", fontsize=9)
    ax2.set_ylabel("Risparmio CO2 rispetto a Plain (%)", fontsize=9)

    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{b:.6f}" for b in budgets], rotation=35, ha="right", fontsize=8)
    ax1.set_ylim(0, 110)
    ax2.set_ylim(-10, 110)
    ax1.axhline(100, color="gray", linewidth=0.8, linestyle=":", alpha=0.5)
    ax2.axhline(0,   color="gray", linewidth=0.8, linestyle=":", alpha=0.5)

    # ── Legenda unificata ─────────────────────────────────────────────────────
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1, l1, fontsize=7, title_fontsize=7,
               loc="upper right", ncol=2)
    ax2.grid(False)
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f"Salvato: {output}")

# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
def genera_grafici_tesi(path: str = "risultati_finali_filtri.csv"):
    df = carica_dati(path)

    grafico1_emissioni_medie(df)
    grafico2_emissioni_vs_budget(df)
    grafico3_handler_percentuale(df)
    grafico4_andamentoco2(df)
    grafico5_risparmio_percentuale(df)
    grafico6_handler_vs_budget(df)
    grafico8_curve_handler_risparmio(df)

    print("\nTutti i grafici sono stati generati con successo!")


if __name__ == "__main__":
    genera_grafici_tesi()
