import json
import os
import time

# 📁 Percorso della cartella principale delle personalità
FOLDER_PATH = "D:/Test Personality/perGM/"

# 📁 Percorso del file PGN (cambia con il tuo percorso esatto)
PGN_FILE = "D:/Test Personality/games/Personality.pgn"

# 🔹 Funzione per ottenere l'ultimo risultato dal PGN
def get_last_game_result():
    with open(PGN_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    winner, loser = None, None
    white, black = None, None  # 🔥 Inizializziamo sempre le variabili

    for line in reversed(lines):  # Leggiamo il file PGN dalla fine
        if "[White " in line:
            white = line.split('"')[1].rsplit(" ", 1)[0]  # Rimuove il rating
        if "[Black " in line:
            black = line.split('"')[1].rsplit(" ", 1)[0]  # Rimuove il rating
        if "1-0" in line and white and black:
            winner, loser = white, black  # Vince il Bianco, perde il Nero
        elif "0-1" in line and white and black:
            winner, loser = black, white  # Vince il Nero, perde il Bianco
        elif "1/2-1/2" in line:
            return None, None  # Patta, nessuno viene aggiornato

    if not white or not black:
        print("❌ Errore: Nomi dei giocatori non trovati nel PGN!")
    
    return winner, loser  # Restituisce i nomi puliti

# 🔹 Funzione per aggiornare `loss_streak` nel JSON
def update_loss_streak(winner, loser):
    if not winner or not loser:
        print("❌ Errore: non ho trovato un vincitore o un perdente nel PGN!")
        return

    for subfolder in os.listdir(FOLDER_PATH):
        subfolder_path = os.path.join(FOLDER_PATH, subfolder)

        if os.path.isdir(subfolder_path):
            for filename in os.listdir(subfolder_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(subfolder_path, filename)

                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    if "name" in data:
                        player_name = data["name"]  # ✅ Definiamo player_name

                        # 🔥 Se è il perdente, aumenta loss_streak
                        if player_name == loser:
                            data["loss_streak"] += 1
                            print(f"❌ {player_name} ha perso! Nuovo loss_streak: {data['loss_streak']}")
                        
                        # 🏆 Se è il vincitore, resetta loss_streak
                        elif player_name == winner:
                            data["loss_streak"] = 0
                            print(f"🏆 {player_name} ha vinto! Loss_streak resettato.")

                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=4)

# 🔥 MONITORAGGIO AUTOMATICO DEL PGN
print("🔄 Monitoraggio del file PGN avviato...")
last_size = os.path.getsize(PGN_FILE)  # Dimensione iniziale del file

while True:
    time.sleep(5)  # Controlla ogni 5 secondi
    new_size = os.path.getsize(PGN_FILE)

    if new_size > last_size:  # Se il file PGN è cambiato
        print("📌 Nuova partita rilevata! Analizzando...")
        winner = get_last_game_result()
        winner, loser = get_last_game_result()
        update_loss_streak(winner, loser)
        last_size = new_size  # Aggiorna la dimensione del file
