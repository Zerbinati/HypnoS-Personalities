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
        lines = [line.strip() for line in f.readlines() if line.strip()]  # Rimuove righe vuote

    winner, loser = None, None
    white, black = None, None

    # 🔥 Leggiamo il PGN dalla fine
    for line in reversed(lines):  
        if line.startswith('[White "'):
            white = line.split('"')[1]  # Leggiamo il nome del Bianco
        elif line.startswith('[Black "'):
            black = line.split('"')[1]  # Leggiamo il nome del Nero
        
        # 🔥 Stampiamo per debug solo se troviamo tutto
        if white and black:
            print(f"DEBUG → White: {white}, Black: {black}")

        # 🔥 Ora controlliamo il risultato SOLO DOPO aver trovato i nomi
        if white and black:
            if line.startswith('[Result "1-0"]'):
                winner, loser = white, black  # Vince il Bianco
            elif line.startswith('[Result "0-1"]'):
                winner, loser = black, white  # Vince il Nero
            elif line.startswith('[Result "1/2-1/2"]'):
                return None, None  # Patta

        if winner and loser:  # Se abbiamo trovato tutto, usciamo
            break

    if not winner or not loser:
        print("❌ Errore: Il risultato della partita non è stato assegnato correttamente!")

    return winner, loser

# 🔹 Funzione per aggiornare `loss_streak` nel JSON
def update_loss_streak(winner, loser):
    if not winner or not loser:
        print("❌ Errore: Non ho ricevuto un vincitore o un perdente validi!")
        return

    print(f"📌 DEBUG: Vincitore = {winner}, Perdente = {loser}")

    for subfolder in os.listdir(FOLDER_PATH):
        subfolder_path = os.path.join(FOLDER_PATH, subfolder)

        if os.path.isdir(subfolder_path):
            for filename in os.listdir(subfolder_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(subfolder_path, filename)

                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    if "name" in data:
                        player_name = data["name"]  # Nome completo dal JSON

                        pgn_last_name_winner = winner.split()[-1]  # Cognome vincitore
                        pgn_last_name_loser = loser.split()[-1]  # Cognome perdente
                        json_last_name = player_name.split()[-1]  # Cognome nel JSON

                        print(f"📌 DEBUG: Controllando {filename} (Nome JSON: {player_name}, PGN: {winner} / {loser})")

                        # 🔥 Se è il perdente, aumenta loss_streak
                        if json_last_name == pgn_last_name_loser:
                            data["loss_streak"] += 1
                            print(f"❌ {player_name} ha perso! Nuovo loss_streak: {data['loss_streak']}")

                        # 🏆 Se è il vincitore, resetta loss_streak
                        if json_last_name == pgn_last_name_winner:
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
        winner, loser = get_last_game_result()
        update_loss_streak(winner, loser)
        last_size = new_size  # Aggiorna la dimensione del file
