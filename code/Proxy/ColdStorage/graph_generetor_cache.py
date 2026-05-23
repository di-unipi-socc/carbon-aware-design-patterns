import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# --- CONFIGURAZIONE PERCORSI ASSOLUTI ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))

DATA_DIR = os.path.join(CURRENT_DIR, "data")
DIR_OUT = os.path.join(PROJECT_ROOT, "results", "ColdStorage")

FILE_JSON_TIME = os.path.join(DATA_DIR, "time_slot.json")
FILE_CSV_IN = os.path.join(DIR_OUT, "risultati_test.csv")
# ----------------------------------------

sns.set_theme(style="whitegrid")

plt.rcParams.update({
    "font.family":  "serif",
    "font.serif":   ["Computer Modern Roman", "DejaVu Serif"],
    "mathtext.fontset": "cm",
})

custom_palette = {"plain": "#b24541", "pattern": "#e16f0b", "pattern_ca": "#1a6498"}

def genera_dot_plot(df_csv, thresholds):
    dot_palette = {"pattern": "#e16f0b", "pattern_ca": "#1a6498"}
    markers     = {"pattern": "o",       "pattern_ca": "o"}
    labels      = {"pattern": "Pattern", "pattern_ca": "Pattern CA"}
    dot_plot_data = []
    for th in thresholds:
        df_th     = df_csv[df_csv['threshold'] == th]
        totali    = df_th.groupby('versione')['co2_emessa'].sum()
        plain_val = totali['plain']
        for v in ['pattern', 'pattern_ca']:
            risparmio = (plain_val - totali[v]) / plain_val * 100
            dot_plot_data.append({'threshold': str(th), 'versione':  v, 'risparmio': risparmio})
    
    df_dot = pd.DataFrame(dot_plot_data)
    th_labels = [str(t) for t in thresholds]
    fig, ax = plt.subplots(figsize=(8, 5))
    
    for v in ['pattern', 'pattern_ca']:
        subset = df_dot[df_dot['versione'] == v]
        ax.scatter(subset['risparmio'], subset['threshold'], color=dot_palette[v], marker=markers[v], s=30, zorder=5, label=labels[v])
        for _, row in subset.iterrows():
            offset_x, align = (-5, 'right') if row['threshold'] == "265" and row['versione'] == "pattern" else (+5, 'center')
            ax.annotate(f"{row['risparmio']:.1f}%", xy=(row['risparmio'], row['threshold']), xytext=(offset_x, -10),
                        textcoords="offset points", va='center', ha=align, fontsize=8, color=dot_palette[v])
    
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.6)

    for th_str in th_labels:
        row_data = df_dot[df_dot['threshold'] == th_str]
        ax.plot([row_data['risparmio'].min(), row_data['risparmio'].max()], [th_str, th_str], color='lightgray', linewidth=1.5, zorder=1)
    
    ax.set_xlabel("Risparmio CO2 rispetto al Plain (%)", fontsize=9)
    ax.set_ylabel("Threshold (gCO2/kWh)", fontsize=9)
    ax.set_title("Risparmio CO2 per Versione e Threshold", fontsize=11)
    ax.legend(title="Versione", fontsize=8, title_fontsize=8)
    ax.set_xlim(left=df_dot['risparmio'].min() - 12.3, right=df_dot['risparmio'].max() + 70)
    plt.tight_layout()
    
    output_path = os.path.join(DIR_OUT, "2_risparmio_co2_dot_plot.pdf")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(" Grafico 2 (dot plot risparmio) generato.")

def grafico5_dual_risparmio_eta(df_th, th):
    fig, ax1 = plt.subplots(figsize=(8, 5))
    mean_emissions = df_th.groupby(['ttl', 'versione'])['co2_emessa'].mean().reset_index()
    pivot_emissions = mean_emissions.pivot(index='ttl', columns='versione', values='co2_emessa').reset_index()
    
    pivot_emissions['risparmio_pattern'] = ((pivot_emissions['plain'] - pivot_emissions['pattern']) / pivot_emissions['plain']) * 100
    pivot_emissions['risparmio_pattern_ca'] = ((pivot_emissions['plain'] - pivot_emissions['pattern_ca']) / pivot_emissions['plain']) * 100

    palette = {"pattern": "#e16f0b", "pattern_ca": "#1a6498"}
    ttls_str = pivot_emissions['ttl'].astype(str).tolist()

    ax1.plot(ttls_str, pivot_emissions['risparmio_pattern'], color=palette["pattern"], marker='o', markersize=8, linewidth=3, linestyle='-', label='Risparmio % (Pattern)', zorder=10)
    ax1.plot(ttls_str, pivot_emissions['risparmio_pattern_ca'], color=palette["pattern_ca"], marker='s', markersize=8, linewidth=3, linestyle='-', label='Risparmio % (Pattern CA)', zorder=10)
    ax1.axhline(0, color='gray', linestyle=':', linewidth=1.5, zorder=1)
    ax1.set_xlabel("TTL", fontsize=9)
    ax1.set_ylabel("Risparmio CO2 rispetto al Plain (%)", fontsize=9, color='#333333')
    ax1.set_ylim(-5, 100)

    ax2 = ax1.twinx()
    df_cache = df_th[df_th['versione'].isin(['pattern', 'pattern_ca'])].copy()
    df_cache['ttl_str'] = df_cache['ttl'].astype(str)
    sns.stripplot(data=df_cache, x='ttl_str', y='eta', hue='versione', palette=palette, dodge=True, alpha=0.20, jitter=True, size=4, ax=ax2, zorder=5)

    ax2.set_ylabel("Eta del dato in Cache", fontsize=9, color='#555555')
    ax2.grid(False)

    lines1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    labels2 = ["ETA (Pattern)", "ETA (Pattern CA)"]
    ax1.legend(lines1 + handles2, labels1 + labels2, loc='upper left', framealpha=0.9, fontsize=7, ncol=2)

    if ax2.get_legend() is not None:
        ax2.get_legend().remove()

    plt.title(f"Risparmio Emissioni vs Eta - Threshold {th}", fontsize=11)
    plt.tight_layout()
    
    out_name = os.path.join(DIR_OUT, f"5_dual_risparmio_eta_th_{th}.pdf")
    plt.savefig(out_name, bbox_inches="tight")
    plt.close()
    print(f" Generato: {os.path.basename(out_name)}")

def main():
    os.makedirs(DIR_OUT, exist_ok=True)
    print("Caricamento dati...")
    with open(FILE_JSON_TIME, 'r', encoding='utf-8') as f:
        time_data = json.load(f)['data']
    
    df_time = pd.DataFrame([{'time_slot': d['from'], 'actual': float(d['intensity']['actual'])} for d in time_data])

    if not os.path.exists(FILE_CSV_IN):
        print(f" [ERRORE] File '{FILE_CSV_IN}' non trovato. Esegui prima i test!")
        return

    df_csv = pd.read_csv(FILE_CSV_IN, sep=";")
    df_csv['versione'] = df_csv['versione'].str.lower()
    
    thresholds = [150, 200, 250]

    for th in thresholds:
        print(f"Generazione grafici per Threshold: {th}...")

        plt.figure(figsize=(8, 5))
        sns.lineplot(data=df_time, x='time_slot', y='actual', color='gray', linewidth=1.5)
        colors = ['#139A43' if val < th else '#543406' for val in df_time['actual']]
        
        plt.scatter(data=df_time, x='time_slot', y='actual', c=colors, s=50, zorder=5)
        for index, row in df_time.iterrows():
            plt.annotate(f"{row['actual']:.0f}", xy=(row['time_slot'], row['actual']), xytext=(0, 10), textcoords="offset points", ha='center', fontsize=8, color='black')
        plt.axhline(y=th, color='black', linestyle='--', linewidth=2, label=f'Threshold = {th}')

        plt.title(f"Andamento Carbon Intensity - Threshold {th}", fontsize=11)
        plt.xlabel("Time Slot", fontsize=9)
        plt.ylabel("Carbon Intensity (gCO2/kWh)", fontsize=9)
        plt.xticks(rotation=45, fontsize=8)
        plt.tight_layout()
        plt.savefig(os.path.join(DIR_OUT, f"1_co2_trend_th_{th}.pdf"), bbox_inches="tight")
        plt.close()

        df_th = df_csv[df_csv['threshold'] == th]

        plt.figure(figsize=(8, 5))
        mean_emissions_ttl = df_th.groupby(['ttl', 'versione'])['co2_emessa'].mean().reset_index()
        sns.lineplot(data=mean_emissions_ttl, x='ttl', y='co2_emessa', hue='versione', marker='o', linewidth=2, palette=custom_palette)

        plt.title(f"Emissioni Medie al variare del TTL - Threshold {th}", fontsize=11)
        plt.xlabel("TTL", fontsize=9)
        plt.ylabel("Emissioni Medie (gCO2)", fontsize=9)
        plt.legend(title="Versione", fontsize=8, title_fontsize=8)
        plt.xticks([0.06,0.07,0.08,0.09,0.1,0.15], fontsize=8)
        plt.ylim(0.000005,0.00009)
        plt.yticks(np.arange(0.000010, 0.00009, 0.000005), fontsize=8)
        plt.tight_layout()
        plt.savefig(os.path.join(DIR_OUT, f"3_emissioni_vs_ttl_th_{th}.pdf"), bbox_inches="tight")
        plt.close()

        plt.figure(figsize=(8, 5))
        df_cache = df_th[df_th['versione'].isin(['pattern', 'pattern_ca'])]
        sns.stripplot(data=df_cache, x='ttl', y='eta', hue='versione', palette={"pattern": "#e16f0b", "pattern_ca": "#1a6498"}, dodge=True, alpha=0.5, jitter=True, size=4)
        
        plt.title(f"Eta del Dato rispetto al TTL - Threshold {th}", fontsize=11)
        plt.xlabel("TTL", fontsize=9)
        plt.ylabel("Eta del dato in Cache", fontsize=9)
        plt.legend(title="Versione", fontsize=8, title_fontsize=8)
        plt.tight_layout()
        plt.savefig(os.path.join(DIR_OUT, f"4_stripplot_eta_th_{th}.pdf"), bbox_inches="tight")
        plt.close()

        grafico5_dual_risparmio_eta(df_th, th)

    genera_dot_plot(df_csv, thresholds)
    print("\n Tutte le 13 immagini sono state generate con successo nei rispettivi percorsi!")

if __name__ == "__main__":
    main()