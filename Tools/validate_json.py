import os
import json

# 📁 Cartella da controllare (MODIFICA questo percorso con quello corretto)
FOLDER_PATH = "D:/Test Personality/perGM/"

def validate_json_files(folder_path):
    print("🔍 Scansione della cartella per file JSON...\n")
    
    error_found = False
    
    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)

        if os.path.isdir(subfolder_path):
            for filename in os.listdir(subfolder_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(subfolder_path, filename)
                    print(f"📂 Controllando: {filename}... ", end="")

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            json.load(f)  # Prova a caricare il JSON
                        print("✅ OK")
                    except json.JSONDecodeError as e:
                        print(f"❌ ERRORE! {e}")
                        error_found = True
                    except Exception as e:
                        print(f"⚠️ Errore generico: {e}")
                        error_found = True

    if error_found:
        print("\n🚨 ATTENZIONE: Alcuni file JSON contengono errori! Correggili prima di procedere.\n")
    else:
        print("\n🎉 Tutti i file JSON sono validi! Puoi avviare il monitoraggio senza problemi.\n")

# 🔥 Esegue la validazione
if __name__ == "__main__":
    validate_json_files(FOLDER_PATH)
