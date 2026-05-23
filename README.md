# Pattern Carbon Aware – Thesis Project

Questo repository contiene il codice sorgente sviluppato per una tesi di laurea dedicata alla progettazione e validazione di pattern architetturali *Carbon Aware*.

L’obiettivo del progetto è dimostrare come l’adattamento dinamico del comportamento del software, basato sulla **Carbon Intensity** della rete elettrica, possa contribuire alla riduzione delle emissioni di CO₂ generate dall’esecuzione delle applicazioni, mantenendo al tempo stesso un adeguato livello di servizio.

Il progetto è organizzato in quattro casi di studio, ciascuno focalizzato sull’applicazione dei pattern in differenti domini applicativi:

1. **ColdStorage**
   Applicazione del pattern **Proxy (Cache)** per l’ottimizzazione delle richieste di correlazione e rilevamento anomalie su dati IoT.

2. **DocumentResearch**
   Applicazione del pattern **Chain of Responsibility** in ambito NLP per la ricerca semantica di documenti testuali.

3. **DocumentResumer**
   Applicazione del pattern **Proxy (Delayed Execution)** per la generazione di riassunti tramite LLM.

4. **ImageFilters**
   Applicazione in ambito Computer Vision per l’adattamento dinamico di filtri grafici tramite OpenCV/TensorFlow.

---

# Prerequisiti

Per eseguire i progetti è necessario avere installato:

* Python 3.9 o superiore
* `pip` (Python Package Installer)

---

# Installazione e Configurazione

È fortemente consigliato utilizzare un ambiente virtuale per isolare le dipendenze del progetto.

## 1. Clonare il repository

```bash
git clone https://github.com/di-unipi-socc/carbon-aware-design-patterns.git
cd carbon-aware-design-patterns
```

## 2. Creare l’ambiente virtuale

```bash
python -m venv venv
```

## 3. Attivare l’ambiente virtuale

### Windows (PowerShell)

```powershell
.\venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

## 4. Installare le dipendenze

```bash
pip install -r requirements.txt
```

---

# Utilizzo del Progetto

Il progetto è gestito tramite un orchestratore centrale situato nella root del workspace: `pattern_carbon_aware.py`.

Questo script consente di eseguire tutti i casi di studio attraverso un’unica interfaccia a riga di comando.

Sono disponibili due modalità operative:

* **Demo Interattiva**
* **Test Automatizzato e Generazione Grafici**

---

# Modalità 1 – Demo Interattiva

Questa modalità consente di eseguire i singoli programmi interagendo direttamente con essi in tempo reale.

È possibile sovrascrivere i parametri ambientali (ad esempio il livello corrente di CO₂) tramite argomenti da terminale.

## Cold Storage

```bash
python pattern_carbon_aware.py coldstorage --co2 200.0 --threshold 150.0 --ttl 3.0
```

## Document Research

```bash
python pattern_carbon_aware.py document-research --co2 100.0 --budget 0.005
```

## Document Resumer

```bash
python pattern_carbon_aware.py document-resumer --co2 300.0 --forecast 100.0 --threshold 200.0
```

## Image Filters

```bash
python pattern_carbon_aware.py image-filters --image immagine1 --co2 270.0
```

> **Nota:** i parametri mostrati sopra sono opzionali e rappresentano i valori di default.
> Se omessi, verranno utilizzati automaticamente i valori predefiniti.

---

# Modalità 2 – Test Automatizzato e Generazione Grafici

Questa modalità esegue automaticamente l’intera pipeline di benchmark per ciascun caso di studio:

* elaborazione dei workload
* calcolo delle emissioni
* confronto tra le varianti:

  * Plain
  * Pattern Standard
  * Pattern Carbon Aware
* esportazione dei risultati in formato CSV
* generazione automatica dei grafici in formato PDF

Per eseguire i test, utilizzare il prefisso `test-` seguito dal nome del progetto.

```bash
python pattern_carbon_aware.py test-coldstorage
python pattern_carbon_aware.py test-document-research
python pattern_carbon_aware.py test-document-resumer
python pattern_carbon_aware.py test-image-filters
```

---

# Struttura dell’Output

Al termine dell’esecuzione della modalità di test, verrà creata automaticamente una cartella `results` nella root del progetto.

La struttura dei risultati sarà organizzata come segue:

```plaintext
results/
├── ColdStorage/
│   ├── risultati_test.csv
│   └── *.pdf
│
├── DocumentResearch/
│   ├── base_ttl/
│   └── increased_ttl/
│
├── DocumentResumer/
│
└── ImageFilters/
    ├── base_ttl/
    └── increased_ttl/
```
