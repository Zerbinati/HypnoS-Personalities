import json
import os

# 📁 Percorso della cartella principale
FOLDER_PATH = "C:/Users/zerbi/OneDrive/Documenti/GitHub/Learn/src/perGM/"


# Scansiona tutte le sottocartelle
for subfolder in os.listdir(FOLDER_PATH):
    subfolder_path = os.path.join(FOLDER_PATH, subfolder)

    # Controlla se è una cartella
    if os.path.isdir(subfolder_path):
        for filename in os.listdir(subfolder_path):
            if filename.endswith(".json"):  # Considera solo i file JSON
                file_path = os.path.join(subfolder_path, filename)

                # Carica il file JSON
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Se manca "loss_streak", lo aggiunge
                if "loss_streak" not in data:
                    data["loss_streak"] = 0

                    # Salva il file aggiornato
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)

                    print(f"Aggiornato: {file_path}")

print("✔️ Aggiornamento completato! Ora tutti i file JSON hanno 'loss_streak'.")
