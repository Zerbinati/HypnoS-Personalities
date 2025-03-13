import json
import os
import time

# 📁 Path to the main personality folder
FOLDER_PATH = "D:/Test Personality/perGM/"

# 📁 Path to the PGN file (change to your exact path)
PGN_FILE = "D:/Test Personality/games/Personality.pgn"

# 🔹 Function to get the last game result from the PGN
def get_last_game_result():
    with open(PGN_FILE, "r", encoding="latin-1") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    winner, loser = None, None
    white, black = None, None
    result = None  

    # 🔥 Read the PGN from the end
    for line in reversed(lines):  
        if line.startswith('[White "'):
            white = line.split('"')[1]  # Read White's name
        elif line.startswith('[Black "'):
            black = line.split('"')[1]  # Read Black's name
        elif line.startswith('[Result "'):
            result = line.split('"')[1]  # Read game result
        
        if white and black and result:
            break  # Exit loop once we have all needed data

    if not result:
        print("❌ Error: Game result not found in PGN!")
        return None, None

    if result == "1-0":
        winner, loser = white, black  # White wins
    elif result == "0-1":
        winner, loser = black, white  # Black wins
    elif result == "1/2-1/2":
        print("➖ Draw detected, no changes made.")
        return None, None  # Draw, no updates

    print(f" Corrected Match Result → Winner: {winner}, Loser: {loser}")  # Debug print
    return winner, loser

# 🔹 Function to update `loss_streak` in the JSON
def update_loss_streak(winner, loser):
    if winner is None and loser is None:
        print("➖ The game ended in a draw. No changes made.")
        return
    if not winner or not loser:
        print("⚠️ No valid winner or loser detected. Skipping update.")
        return

    print(f" Match result → Winner: {winner}, Loser: {loser}")  # 🔥 Stampa il risultato della partita

    for subfolder in os.listdir(FOLDER_PATH):
        subfolder_path = os.path.join(FOLDER_PATH, subfolder)

        if os.path.isdir(subfolder_path):
            for filename in os.listdir(subfolder_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(subfolder_path, filename)

                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    if "name" in data:
                        player_name = data["name"]  
                        pgn_last_name_winner = winner.split()[-1]  
                        pgn_last_name_loser = loser.split()[-1]  
                        json_last_name = player_name.split()[-1]  

                        if json_last_name == pgn_last_name_loser:
                            data["loss_streak"] += 1
                            print(f" {player_name} lost! New loss_streak: {data['loss_streak']}")  # 🔥 Stampa aggiornamento

                        if json_last_name == pgn_last_name_winner:
                            data["loss_streak"] = max(data["loss_streak"] - 2, 0)  # 🔥 Riduce di 2 invece di azzerare subito
                            print(f"🏆 {player_name} won! Loss_streak reduced to {data['loss_streak']}")  # 🔥 Stampa aggiornamento

                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=4)

# 🔥 AUTOMATIC PGN MONITORING
print("🔄 PGN file monitoring started...")
last_size = os.path.getsize(PGN_FILE)  # Initial file size

while True:
    time.sleep(5)  # Check every 5 seconds
    new_size = os.path.getsize(PGN_FILE)

    if new_size > last_size:  # If the PGN file has changed
        print(" New game detected! Analyzing...")
        winner, loser = get_last_game_result()
        update_loss_streak(winner, loser)
        last_size = new_size  # Update the file size
