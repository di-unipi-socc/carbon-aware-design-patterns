import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import seaborn as sns
import numpy as np


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
    "plain":   "#b24541",
    "pattern": "#e16f0b",
    "ca":      "#1a6498",
}
LABELS = {
    "plain":   "Plain",
    "pattern": "Pattern",
    "ca":      "Pattern CA",
}
THRESHOLDS = [150, 200, 250]
VERSIONI   = ["plain", "pattern", "ca"]


def carica_dati(path: str = "risultati_resumer.csv") -> pd.DataFrame:
    df = pd.read_csv(path, sep=";")
    df["time_slot"] = pd.Categorical(
        df["time_slot"],
        categories=sorted(df["time_slot"].unique()),
        ordered=True,
    )
    return df

def grafico1_ci_trend_generale(df: pd.DataFrame):

    slot_info = (
        df.groupby("time_slot", observed=True)[["actual_ci", "forecast_ci"]]
        .first()
        .reset_index()
        .sort_values("time_slot")
    )
    slots       = slot_info["time_slot"].tolist()
    actual_vals = slot_info["actual_ci"].tolist()
    forec_vals  = slot_info["forecast_ci"].tolist()
    x           = np.arange(len(slots))
    x_forec     = x + 1

    try:
        last_time = pd.to_datetime(slots[-1], format='%H:%M')
        next_time = (last_time + pd.Timedelta(minutes=30)).strftime('%H:%M')
    except:
        next_time = "Next"

    extended_slots = slots + [next_time]
    extended_x     = np.arange(len(extended_slots))

    fig, ax = plt.subplots(figsize=(9,5))

    # --- Actual ---
    ax.plot(x, actual_vals, color="gray", linewidth=1.5, zorder=1)
    ax.scatter(x, actual_vals, c="#1a6498", s=40, zorder=3)

    for i, (xi, val) in enumerate(zip(x, actual_vals)):
        offset_y = 12
        if i > 0:
            val_forec_stessa_x = forec_vals[i - 1]
            if val <= val_forec_stessa_x:
                offset_y = -18
        ax.annotate(str(int(val)), xy=(xi, val),
                    xytext=(0, offset_y), textcoords="offset points",
                    ha="center", fontsize=8, color="black")

    # --- Forecast ---
    ax.plot(x_forec, forec_vals, color="#1f77b4", linewidth=1.5,
            linestyle="--", zorder=2, alpha=0.85)
    ax.scatter(x_forec, forec_vals, c="#1a6498", s=30, marker="D",
            zorder=3, alpha=0.85)

    for i, (xi, val) in enumerate(zip(x_forec, forec_vals)):
        offset_y = -18
        if i + 1 < len(actual_vals):
            val_actual_stessa_x = actual_vals[i + 1]
            if val >= val_actual_stessa_x:
                offset_y = 12
        ax.annotate(str(int(val)), xy=(xi, val),
                    xytext=(0, offset_y), textcoords="offset points",
                    ha="center", fontsize=8, color="#1f77b4", fontstyle="italic")

    ax.set_xticks(extended_x)
    ax.set_xticklabels(extended_slots, rotation=45, ha="right", fontsize=8)
    ax.set_xlabel("Time Slot", fontsize=9)
    ax.set_ylabel("Carbon Intensity (gCO2/kWh)", fontsize=9)
    ax.set_title("Andamento Carbon Intensity", fontsize=11)

    leg_actual   = mlines.Line2D([], [], color="gray", marker="o",
                                markersize=7, label="CI Actual")
    leg_forecast = mlines.Line2D([], [], color="#1f77b4", marker="D",
                                markersize=6, linestyle="--", label="CI Forecast")
    ax.legend(handles=[leg_actual, leg_forecast], fontsize=8, loc="upper left")

    plt.tight_layout()
    out = "1_resumer_ci_trend.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f" Salvato: {out}")

# ──────────────────────────────────────────────
# GRAFICO 1 — Andamento CI actual + forecast per time slot
# ──────────────────────────────────────────────
def grafico1_ci_trend(df: pd.DataFrame):

    slot_info = (
        df.groupby("time_slot", observed=True)[["actual_ci", "forecast_ci"]]
        .first()
        .reset_index()
        .sort_values("time_slot")
    )
    slots       = slot_info["time_slot"].tolist()
    actual_vals = slot_info["actual_ci"].tolist()
    forec_vals  = slot_info["forecast_ci"].tolist()
    x           = np.arange(len(slots))
    x_forec = x + 1

    try:
        last_time = pd.to_datetime(slots[-1], format='%H:%M')
        next_time = (last_time + pd.Timedelta(minutes=30)).strftime('%H:%M')
    except:
        next_time = "Next"
        
    extended_slots = slots + [next_time]
    extended_x = np.arange(len(extended_slots))

    for th in THRESHOLDS:
        fig, ax = plt.subplots(figsize=(9,6))
        ax.plot(x, actual_vals, color="gray", linewidth=1.5, zorder=1)
        colors_actual = ["#139A43" if v < th else "#543406" for v in actual_vals]
        ax.scatter(x, actual_vals, c=colors_actual, s=40, zorder=3)

        for i, (xi, val) in enumerate(zip(x, actual_vals)):
            offset_y = 12
            if i > 0:
                val_forec_stessa_x = forec_vals[i-1]
                if val <= val_forec_stessa_x:
                    offset_y = -18
            ax.annotate(str(int(val)), xy=(xi, val),
                        xytext=(0, offset_y), textcoords="offset points",
                        ha="center", fontsize=8, color="black")

        ax.plot(x_forec, forec_vals, color="#1f77b4", linewidth=1.5,
                linestyle="--", zorder=2, alpha=0.85)

        colors_forec = ["#139A43" if v < th else "#543406" for v in forec_vals]
        ax.scatter(x_forec, forec_vals, c=colors_forec, s=30, marker="D",
                zorder=3, alpha=0.85)

        for i, (xi, val) in enumerate(zip(x_forec, forec_vals)):
            offset_y = -18
            if i + 1 < len(actual_vals):
                val_actual_stessa_x = actual_vals[i+1]
                if val >= val_actual_stessa_x:
                    offset_y = 12
            ax.annotate(str(int(val)), xy=(xi, val),
                        xytext=(0, offset_y), textcoords="offset points",
                        ha="center", fontsize=8, color="#1f77b4", fontstyle="italic")

        ax.axhline(y=th, color="black", linestyle="--",
                linewidth=2, label=f"Threshold = {th}")

        ax.set_xticks(extended_x)
        ax.set_xticklabels(extended_slots, rotation=45, ha="right", fontsize=8)
        ax.set_xlabel("Time Slot", fontsize=9)
        ax.set_ylabel("Carbon Intensity (gCO2/kWh)", fontsize=9)
        ax.set_title(f"Andamento Carbon Intensity - Threshold {th}", fontsize=11)

        leg_actual   = mlines.Line2D([], [], color="gray", marker="o",
                                    markersize=7, label="CI Actual")
        leg_forecast = mlines.Line2D([], [], color="#1f77b4", marker="D",
                                    markersize=6, linestyle="--", label="CI Forecast")
        leg_th       = mlines.Line2D([], [], color="black", linestyle="--",
                                    linewidth=2, label=f"Threshold = {th}")
        leg_green    = mlines.Line2D([], [], color="#139A43", marker="o",
                                    linestyle="None", markersize=8, label="< Threshold")
        leg_red      = mlines.Line2D([], [], color="#543406", marker="o",
                                    linestyle="None", markersize=8, label=">= Threshold")
        ax.legend(handles=[leg_actual, leg_forecast, leg_th, leg_green, leg_red],
                fontsize=7, loc="upper left", ncol=2)

        plt.tight_layout()
        out = f"1_resumer_ci_trend_th_{th}.pdf"
        plt.savefig(out, bbox_inches="tight")
        plt.close()
        print(f" Salvato: {out}")


# ──────────────────────────────────────────────
# GRAFICO 2 — Risparmio % pattern e CA rispetto a plain
# ──────────────────────────────────────────────
def grafico2_risparmio_pct(df: pd.DataFrame):
    dot_palette = {"pattern": "#e16f0b", "ca": "#1a6498"}
    markers     = {"pattern": "o",       "ca": "D"}

    dot_data = []
    for th in THRESHOLDS:
        df_th     = df[df["threshold"] == th]
        plain_tot = df_th[df_th["versione"] == "plain"]["co2_emessa_g"].sum()
        for v in ["pattern", "ca"]:
            v_tot     = df_th[df_th["versione"] == v]["co2_emessa_g"].sum()
            risparmio = (plain_tot - v_tot) / plain_tot * 100
            if risparmio < 0:
                risparmio = 0
            dot_data.append({"threshold": str(th), "versione": v, "risparmio": risparmio})

    df_dot    = pd.DataFrame(dot_data)
    th_labels = [str(t) for t in THRESHOLDS]

    fig, ax = plt.subplots(figsize=(8, 5))

    for v in ["pattern", "ca"]:
        subset = df_dot[df_dot["versione"] == v]
        ax.scatter(subset["risparmio"], subset["threshold"],
                color=dot_palette[v], marker=markers[v],
                s=50, zorder=5, label=LABELS[v])
        for _, row in subset.iterrows():
            ax.annotate(f"{row['risparmio']:.1f}%",
                        xy=(row["risparmio"], row["threshold"]),
                        xytext=(8, 0), textcoords="offset points",
                        va="center", fontsize=8,
                        color=dot_palette[v])

    ax.axvline(x=0, color="gray", linestyle="--", linewidth=1, alpha=0.6)

    for th_str in th_labels:
        row_data = df_dot[df_dot["threshold"] == th_str]
        ax.plot([row_data["risparmio"].min(), row_data["risparmio"].max()],
                [th_str, th_str], color="lightgray", linewidth=1.5, zorder=1)

    ax.set_xlabel("Risparmio CO2 rispetto al Plain (%)", fontsize=9)
    ax.set_ylabel("Threshold (gCO2/kWh)", fontsize=9)
    ax.set_title("Risparmio CO2 per Versione e Threshold", fontsize=11)
    ax.legend(title="Versione", fontsize=8, title_fontsize=8)
    ax.set_xlim(left=df_dot["risparmio"].min() - 5,
                right=df_dot["risparmio"].max() + 15)

    plt.tight_layout()
    out = "2_resumer_risparmio_pct.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f" Salvato: {out}")


# ──────────────────────────────────────────────
# GRAFICO 3 — Andamento emissioni per time slot
# ──────────────────────────────────────────────
def grafico3_emissioni_per_slot(df: pd.DataFrame):
    for th in THRESHOLDS:
        df_th = df[df["threshold"] == th]

        em_slot = (
            df_th.groupby(["versione", "time_slot"], observed=True)["co2_emessa_g"]
            .sum()
            .reset_index()
            .sort_values("time_slot")
        )

        fig, ax = plt.subplots(figsize=(9,6))

        for v in VERSIONI:
            sub = em_slot[em_slot["versione"] == v]
            ax.plot(sub["time_slot"].astype(str), sub["co2_emessa_g"],
                    marker="o", linewidth=2.2,
                    color=PALETTE[v], label=LABELS[v])

        ax.set_title(f"Andamento Emissioni CO2 per Time Slot - Threshold {th}",
                    fontsize=11)
        ax.set_xlabel("Time Slot", fontsize=9)
        ax.set_ylabel("CO2 Emessa", fontsize=9)
        ax.legend(title="Versione", fontsize=8, title_fontsize=8)
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.tight_layout()

        out = f"3_resumer_emissioni_slot_th_{th}.pdf"
        plt.savefig(out, bbox_inches="tight")
        plt.close()
        print(f" Salvato: {out}")


# ──────────────────────────────────────────────
# GRAFICO 4 — % richieste con riassunto restituito
# ──────────────────────────────────────────────
def grafico4_pct_riassunti(df: pd.DataFrame):
    for th in THRESHOLDS:
        df_th = df[df["threshold"] == th]

        pct_data = []
        for v in VERSIONI:
            sub   = df_th[df_th["versione"] == v]
            total = len(sub)
            eseg  = (sub["stato"] == "eseguito").sum()
            pct_data.append({
                "versione": v,
                "label":    LABELS[v],
                "pct":      eseg / total * 100,
            })
        df_pct = pd.DataFrame(pct_data)

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(
            df_pct["label"], df_pct["pct"],
            color=[PALETTE[v] for v in df_pct["versione"]],
            alpha=1, width=0.5,
        )

        for bar, row in zip(bars, df_pct.itertuples()):
            h = bar.get_height()
            ax.annotate(f"{h:.1f}%",
                        xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 5), textcoords="offset points",
                        ha="center", va="bottom", fontsize=8)

        ax.set_ylim(0, 115)
        ax.axhline(100, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.set_title(f"Percentuale Richieste con Riassunto Restituito - Threshold {th}",
                    fontsize=11)
        ax.set_xlabel("Versione", fontsize=9)
        ax.set_ylabel("Richieste con Riassunto (%)", fontsize=9)
        plt.tight_layout()

        out = f"4_resumer_pct_riassunti_th_{th}.pdf"
        plt.savefig(out, bbox_inches="tight")
        plt.close()
        print(f" Salvato: {out}")

def grafico5_emissioni_totali_per_threshold(df: pd.DataFrame,
                                            output: str = "5_resumer_emissioni_totali_th.pdf"):
    totali = (
        df.groupby(["threshold", "versione"])["co2_emessa_g"]
        .sum()
        .reset_index()
    )

    x     = np.arange(len(THRESHOLDS))
    width = 0.25

    fig, ax = plt.subplots(figsize=(8, 5))

    for i, v in enumerate(VERSIONI):
        sub  = totali[totali["versione"] == v].sort_values("threshold")
        vals = sub["co2_emessa_g"].values
        offset = (i - 1) * width
        bars = ax.bar(x + offset, vals, width,
                    label=LABELS[v], color=PALETTE[v], alpha=1)

        for bar, val in zip(bars, vals):
            ax.annotate(
                f"{val:.5f}",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4), textcoords="offset points",
                ha="center", va="bottom", fontsize=8,
                color=PALETTE[v],
            )

    ax.set_title("Emissioni CO2", fontsize=11)
    ax.set_xlabel("Threshold (gCO2/kWh)", fontsize=9)
    ax.set_ylabel("CO2 Emessa", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels([str(t) for t in THRESHOLDS], fontsize=8)
    ax.legend(title="Versione", fontsize=8, title_fontsize=8)
    ax.set_ylim(0, totali["co2_emessa_g"].max() * 1.18)
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f" Salvato: {output}")

# ──────────────────────────────────────────────
# GRAFICO 6 — Dual Axis: % Riassunti Restituiti vs % Risparmio CO2
# ──────────────────────────────────────────────
def grafico6_dual_axis_riassunti_risparmio(df: pd.DataFrame,
                                        output: str = "6_resumer_dual_axis_riassunti_risparmio.pdf"):
    dati_agg = []
    
    for th in THRESHOLDS:
        df_th = df[df["threshold"] == th]
        plain_tot = df_th[df_th["versione"] == "plain"]["co2_emessa_g"].sum()
        
        for v in ["pattern", "ca"]:
            sub = df_th[df_th["versione"] == v]
            v_tot = sub["co2_emessa_g"].sum()
            risparmio = ((plain_tot - v_tot) / plain_tot) * 100
            total_req = len(sub)
            eseg = (sub["stato"] == "eseguito").sum()
            pct_eseg = (eseg / total_req) * 100 if total_req > 0 else 0
            
            dati_agg.append({
                "Threshold": th,
                "Versione": v,
                "Risparmio_%": risparmio,
                "Riassunti_%": pct_eseg
            })
            
    df_agg = pd.DataFrame(dati_agg)
    ordine_versioni = ["pattern", "ca"]
    
    fig, ax1 = plt.subplots(figsize=(8, 5))
    
    x = np.arange(len(THRESHOLDS))
    width = 0.35
    
    for i, v in enumerate(ordine_versioni):
        sub = df_agg[df_agg["Versione"] == v].sort_values("Threshold")
        offset = (i - 0.5) * width
        ax1.bar(
            x + offset,
            sub["Riassunti_%"],
            width=width,
            color=PALETTE[v],
            label=LABELS[v],
            alpha=0.50
        )
        
    ax1.set_ylabel("Richieste con Riassunto Restituito (%)", fontsize=9, color='#333333')
    ax1.set_xlabel("Threshold (gCO2/kWh)", fontsize=9)
    ax1.set_xticks(x)
    ax1.set_xticklabels([str(t) for t in THRESHOLDS], fontsize=8)
    ax1.set_ylim(0, 115)
    
    ax2 = ax1.twinx()
    for i, v in enumerate(ordine_versioni):
        sub = df_agg[df_agg["Versione"] == v].sort_values("Threshold")
        ax2.plot(
            x,
            sub["Risparmio_%"],
            marker=['s', 'o'][i],
            linestyle=['-', '--'][i],
            color=PALETTE[v],
            label=LABELS[v],
            linewidth=2.5, markersize=8, zorder=4
        )
        
    ax2.set_ylabel("Risparmio CO2 rispetto a Plain (%)", fontsize=9)
    
    y2_min = min(-5, df_agg["Risparmio_%"].min() * 1.1)
    y2_max = max(110, df_agg["Risparmio_%"].max() * 1.1)
    ax2.set_ylim(y2_min, y2_max)
    ax2.axhline(0, color='gray', linestyle=':', linewidth=1.5, zorder=1)
    
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2,
               loc='upper right', framealpha=0.9, fontsize=7, ncol=2)
    
    plt.title("Confronto Riassunti restituiti e Threshold", fontsize=11)
    ax2.grid(False)
    
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    plt.close()
    print(f" Salvato: {output}")

# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
def genera_grafici_resumer(path: str = "risultati_resumer.csv"):
    print("Lettura dei dati...")
    df = carica_dati(path)
    print(f"   {len(df):,} righe caricate.\n")
    grafico1_ci_trend_generale(df)
    grafico1_ci_trend(df)
    grafico2_risparmio_pct(df)
    grafico3_emissioni_per_slot(df)
    grafico4_pct_riassunti(df)
    grafico5_emissioni_totali_per_threshold(df)
    grafico6_dual_axis_riassunti_risparmio(df)
    print("\n Tutti i grafici generati con successo!")


if __name__ == "__main__":
    genera_grafici_resumer()
