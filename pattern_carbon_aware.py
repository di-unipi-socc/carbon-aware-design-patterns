import sys
import os
import subprocess
import argparse

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECTS = {
    "coldstorage": (
        os.path.join("code", "Proxy", "ColdStorage"),
        "coldstorage.py",
        "runner_coldstorage.py",
        "graph_generetor_cache.py"
    ),
    "document-research": (
        os.path.join("code", "CoR", "DocumentResearch"),
        "document_research.py",
        "test_cor.py",
        "graphs_generator_cor.py"
    ),
    "document-resumer": (
        os.path.join("code", "Proxy", "DocumentResumer"),
        "document_resumer.py",
        "test_proxy.py",
        "graphs_resumer.py"
    ),
    "image-filters": (
        os.path.join("code", "CoR", "ImageFilters"),
        "imagefilters.py",
        "test_apply_filters.py",
        "graphs_generator.py"
    )
}

def print_help():
    print("\n" + "="*60)
    print("="*60)
    print("Uso: python pattern_carbon_aware.py <comando> [argomenti...]")
    print("\nComandi disponibili per le DEMO (inserimento argomenti richiesto):")
    for cmd in PROJECTS.keys():
        print(f"  - {cmd}")
    print("\nComandi disponibili per i TEST (esecuzione automatica test + grafici):")
    for cmd in PROJECTS.keys():
        print(f"  - test-{cmd}")
    print("\nEsempi:")
    print("  python pattern_carbon_aware.py coldstorage --co2 120 --threshold 150")
    print("  python pattern_carbon_aware.py test-image-filters")
    print("="*60 + "\n")

def run_script(folder_path, script_name, args=None):
    script_path = os.path.join(ROOT_DIR, folder_path, script_name)
    if not os.path.exists(script_path):
        print(f" [ERRORE] File '{script_path}' non trovato.")
        return False
    
    command = [sys.executable, script_path]
    if args:
        command.extend(args)
        
    print(f"\nEsecuzione di: {script_name}...")
    try:
        # Lancia il processo impostando cwd alla cartella del progetto
        subprocess.run(command, cwd=os.path.join(ROOT_DIR, folder_path), check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"\nErrore durante l'esecuzione di {script_name}.")
        return False
    except KeyboardInterrupt:
        print("\nEsecuzione interrotta dall'utente.")
        return True

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print_help()
        sys.exit(0)

    command = sys.argv[1].lower()
    script_args = sys.argv[2:]

    if command.startswith("test-"):
        base_cmd = command.replace("test-", "")
        if base_cmd in PROJECTS:
            folder, _, test_file, graph_file = PROJECTS[base_cmd]
            print(f"🔄 AVVIO FASE DI TEST PER: {base_cmd.upper()}")
            if run_script(folder, test_file):
                run_script(folder, graph_file)
            print(f"✅ Pipeline di test per {base_cmd.upper()} completata!")
        else:
            print(f"⚠️ Comando '{command}' non riconosciuto.")
            print_help()

    elif command in PROJECTS:
        folder, demo_file, _, _ = PROJECTS[command]
        run_script(folder, demo_file, script_args)

    else:
        print(f"Comando '{command}' non riconosciuto.")
        print_help()

if __name__ == "__main__":
    main()