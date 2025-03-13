import json
import math
import datetime  # ✅ AGGIUNGI QUESTA RIGA
import tkinter as tk
from tkinter import ttk, messagebox

K = 20  # Elo update constant
FILE_NAME = "ratings.json"

# Function to load ratings, handling empty or corrupted files
def load_ratings():
    try:
        with open(FILE_NAME, "r") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}  # If empty, return {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # If the file does not exist or is corrupted, return an empty dictionary

# Function to save ratings
def save_ratings(ratings):
    with open(FILE_NAME, "w") as f:
        json.dump(ratings, f, indent=4)

# Function to update dropdown menus with saved players
def update_comboboxes():
    ratings = load_ratings()
    player_list = sorted(ratings.keys()) if ratings else []

    combo_player1["values"] = player_list
    combo_player2["values"] = player_list

    if player_list:
        combo_player1.set(player_list[0])
        combo_player2.set(player_list[0])

# Function to enable manual entry for new players
def enable_manual_entry():
    entry_player1.grid(row=0, column=1)  
    entry_player2.grid(row=1, column=1)  

    combo_player1.grid_remove()  
    combo_player2.grid_remove()

    entry_player1.delete(0, tk.END)
    entry_player2.delete(0, tk.END)

def update_elo():
    player_a = entry_player1.get() if entry_player1.winfo_ismapped() else combo_player1.get()
    player_b = entry_player2.get() if entry_player2.winfo_ismapped() else combo_player2.get()
    elo_a = entry_elo1.get()
    elo_b = entry_elo2.get()
    result_str = entry_result.get()

    if not player_a or not player_b or not result_str:
        messagebox.showerror("Error", "Please fill in all fields!")
        return

    ratings = load_ratings()

    # Recupera gli Elo attuali o imposta 1500 di default
    old_elo_a = ratings.get(player_a, {"elo": 1500})["elo"]
    old_elo_b = ratings.get(player_b, {"elo": 1500})["elo"]

    elo_a = int(elo_a) if elo_a else old_elo_a
    elo_b = int(elo_b) if elo_b else old_elo_b

    try:
        wins_a, wins_b = map(float, result_str.split("-"))
    except ValueError:
        messagebox.showerror("Error", "Invalid result format! Use format: 30-20 or 24.5-24.5")
        return

    total_games = wins_a + wins_b
    if total_games == 0:
        messagebox.showerror("Error", "Total games cannot be 0!")
        return

    expected_a = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    expected_b = 1 - expected_a

    new_elo_a = elo_a + K * total_games * (wins_a / total_games - expected_a)
    new_elo_b = elo_b + K * total_games * (wins_b / total_games - expected_b)

    delta_a = round(new_elo_a - old_elo_a)
    delta_b = round(new_elo_b - old_elo_b)

    win_rate_a = round((wins_a / total_games) * 100, 2)
    win_rate_b = round((wins_b / total_games) * 100, 2)

    update_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Media Elo degli avversari affrontati
    avg_opp_a = ratings.get(player_a, {}).get("avg_opp", 0)
    avg_opp_b = ratings.get(player_b, {}).get("avg_opp", 0)

    total_games_a = ratings.get(player_a, {}).get("games", 0) + total_games
    total_games_b = ratings.get(player_b, {}).get("games", 0) + total_games

    new_avg_opp_a = ((avg_opp_a * (total_games_a - total_games)) + (elo_b * total_games)) / total_games_a
    new_avg_opp_b = ((avg_opp_b * (total_games_b - total_games)) + (elo_a * total_games)) / total_games_b

    # 📊 Salvataggio della cronologia Elo per i grafici
    history_a = ratings.get(player_a, {}).get("history", [])
    history_b = ratings.get(player_b, {}).get("history", [])

    history_a.append({"total_games": total_games_a, "elo": round(new_elo_a)})
    history_b.append({"total_games": total_games_b, "elo": round(new_elo_b)})

    # Aggiorna i dati nei ratings
    ratings[player_a] = {
        "elo": round(new_elo_a),
        "games": total_games_a,
        "won": ratings.get(player_a, {}).get("won", 0) + int(wins_a),
        "avg_opp": round(new_avg_opp_a, 1),
        "matches": ratings.get(player_a, {}).get("matches", []) + [
            {"opponent": player_b, "opp_elo": round(new_elo_b), "result": f"{wins_a}-{wins_b}"}
        ],
        "history": history_a  # Cronologia Elo
    }

    ratings[player_b] = {
        "elo": round(new_elo_b),
        "games": total_games_b,
        "won": ratings.get(player_b, {}).get("won", 0) + int(wins_b),
        "avg_opp": round(new_avg_opp_b, 1),
        "matches": ratings.get(player_b, {}).get("matches", []) + [
            {"opponent": player_a, "opp_elo": round(new_elo_a), "result": f"{wins_b}-{wins_a}"}
        ],
        "history": history_b
    }

    # Salva i dati aggiornati
    save_ratings(ratings)
    update_comboboxes()

    messagebox.showinfo("Elo Updated!", 
        f"{player_a}: {old_elo_a} → {round(new_elo_a)} ({'+' if delta_a >= 0 else ''}{delta_a})\n"
        f"{player_b}: {old_elo_b} → {round(new_elo_b)} ({'+' if delta_b >= 0 else ''}{delta_b})")

    # Restore dropdowns after update
    entry_player1.grid_remove()
    entry_player2.grid_remove()
    combo_player1.grid(row=0, column=1)
    combo_player2.grid(row=1, column=1)

def show_rankings():
    ratings = load_ratings()

    if not ratings:
        messagebox.showinfo("Rankings Empty", "No data found!")
        return

    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1]["elo"], reverse=True)

    ranking_window = tk.Toplevel()
    ranking_window.title("Elo Rankings")
    ranking_window.geometry("900x600")  # 🔥 Aumentato per includere la cronologia sotto
    ranking_window.resizable(True, True)  # 🔥 Permette di ridimensionare la finestra della classifica

    # Frame per separare classifica e cronologia
    frame_top = tk.Frame(ranking_window)
    frame_top.pack(fill="both", expand=True)

    frame_bottom = tk.Frame(ranking_window)
    frame_bottom.pack(fill="both", expand=True)

    tree = ttk.Treeview(frame_top, columns=("Pos", "Player", "Elo", "+", "-", "Games", "Won", "Win%", "Av.opp", "Last Update"), show="headings", height=10)

    # Intestazioni delle colonne
    tree.heading("Pos", text="Position")
    tree.heading("Player", text="Player")
    tree.heading("Elo", text="Elo")
    tree.heading("+", text="+")  # Margine di errore positivo
    tree.heading("-", text="-")  # Margine di errore negativo
    tree.heading("Games", text="Games")
    tree.heading("Won", text="Won")
    tree.heading("Win%", text="Win %")
    tree.heading("Av.opp", text="Av.opp")
    tree.heading("Last Update", text="Last Update")

    # Larghezza colonne
    tree.column("Pos", width=50, anchor="center")
    tree.column("Player", width=150)
    tree.column("Elo", width=100, anchor="center")
    tree.column("+", width=50, anchor="center")
    tree.column("-", width=50, anchor="center")
    tree.column("Games", width=80, anchor="center")
    tree.column("Won", width=80, anchor="center")
    tree.column("Win%", width=80, anchor="center")
    tree.column("Av.opp", width=100, anchor="center")
    tree.column("Last Update", width=150, anchor="center")

    # Creazione della tabella per la cronologia degli avversari
    history_tree = ttk.Treeview(frame_bottom, columns=("Opponent", "Opp Elo", "Result"), show="headings", height=5)
    
    # Intestazioni della cronologia
    history_tree.heading("Opponent", text="Opponent")
    history_tree.heading("Opp Elo", text="Opp Elo")
    history_tree.heading("Result", text="Result")

    # Larghezza colonne
    history_tree.column("Opponent", width=150)
    history_tree.column("Opp Elo", width=100, anchor="center")
    history_tree.column("Result", width=100, anchor="center")

    # Funzione per aggiornare la cronologia quando si seleziona un giocatore
    def update_history(event):
        selected_item = tree.selection()
        if not selected_item:
            print("DEBUG: Nessun giocatore selezionato")
            return

        player = tree.item(selected_item[0])["values"][1]
        matches = ratings.get(player, {}).get("matches", [])

        # 🔥 Debug: stampa i dati per vedere se sono corretti
        print(f"DEBUG: Giocatore selezionato → {player}")
        print(f"DEBUG: Matches trovati → {matches}")

        # Pulisce la tabella
        history_tree.delete(*history_tree.get_children())

        if matches:
            for match in matches:
                print(f"DEBUG: Aggiungo match {match}")  # 🔥 Stampa ogni match trovato
                history_tree.insert("", "end", values=(match["opponent"], match["opp_elo"], match["result"]))
        else:
            print("DEBUG: Nessun match trovato!")
            history_tree.insert("", "end", values=("N/A", "N/A", "N/A"))  # 🔥 Se vuoto, mostra "N/A"

    # Inserimento dati con colori
    for idx, (player, data) in enumerate(sorted_ratings, start=1):
        rating = data["elo"]
        plus_minus = round((40 / (data["games"] + 1)) ** 0.5 * 100)  # Stima del margine di errore
        win_percentage = round((data["won"] / data["games"]) * 100, 1) if data["games"] > 0 else 0

        # Determina il colore in base al rating
        if rating >= 2200:
            color = "light green"  # 🟢 Forte
        elif rating >= 1800:
            color = "yellow"  # 🟡 Medio
        else:
            color = "red"  # 🔴 Debole

        # Evidenziare il primo classificato
        if idx == 1:
            color = "light blue"  # 🏆 Leader

        tree.insert("", "end", values=(
            idx, player, rating, plus_minus, plus_minus, 
            data["games"], data["won"], f"{win_percentage}%", 
            data["avg_opp"], data.get("last_update", "N/A")
        ), tags=(color,))

    # Associa l'evento di selezione alla funzione update_history
    tree.bind("<<TreeviewSelect>>", update_history)

    # Definire i colori nei tag
    tree.tag_configure("light green", background="light green")
    tree.tag_configure("yellow", background="yellow")
    tree.tag_configure("red", background="light coral")
    tree.tag_configure("light blue", background="light blue")  # Leader

    tree.pack(expand=True, fill="both")
    history_tree.pack(expand=True, fill="both")
    
import matplotlib.pyplot as plt
import numpy as np
import mplcursors
import os  # ✅ Aggiunto per la gestione dell'icona

def show_player_rating_graph():
    ratings = load_ratings()
    
    if not ratings:
        messagebox.showinfo("Graph Error", "No data available!")
        return

    # ✅ Controllo se un giocatore è stato selezionato
    player = combo_player1.get()
    if not player:
        messagebox.showerror("Error", "Please select a player!")
        return

    if player not in ratings:
        messagebox.showerror("Error", f"Player '{player}' not found!")
        return

    # ✅ Recupera la cronologia del rating
    history = ratings[player].get("history", [])
    if not history:
        messagebox.showinfo("Graph Error", f"No rating history found for {player}!")
        return

import matplotlib.pyplot as plt
import numpy as np
import mplcursors  # Per tooltip interattivi

def show_player_rating_graph():
    ratings = load_ratings()

    if not ratings:
        messagebox.showinfo("Graph Error", "No data available!")
        return

    # ✅ Controllo se un giocatore è stato selezionato
    player = combo_player1.get()
    if not player:
        messagebox.showerror("Error", "Please select a player!")
        return

    if player not in ratings:
        messagebox.showerror("Error", f"Player '{player}' not found!")
        return

    # ✅ Recupera la cronologia del rating
    history = ratings[player].get("history", [])
    if not history:
        messagebox.showinfo("Graph Error", f"No rating history found for {player}!")
        return

    # ✅ Se non ci sono dati, interrompi la funzione
    if not history:
        messagebox.showinfo("Graph Error", f"No rating history found for {player}!")
        return

    # ✅ Estrai il numero totale di partite giocate e il punteggio Elo
    games_played = [entry["total_games"] for entry in history]
    elos = [entry["elo"] for entry in history]

    # ✅ Controllo per evitare errori se ci sono meno di 2 partite
    if len(elos) < 2:
        messagebox.showinfo("Graph Error", "Not enough data to generate the graph!")
        return

    # ✅ Usa un tema grafico più leggibile
    plt.style.use("fivethirtyeight")  # Grafico chiaro e leggibile  

    # ✅ Creazione del grafico
    plt.figure(figsize=(8, 5))  
    # ✅ Imposta l'icona personalizzata
    icon_path = "Hypnos.ico"

    fig = plt.gcf()
    try:
        fig.canvas.manager.window.iconbitmap(icon_path)
    except Exception as e:
        print(f"Errore impostando l'icona: {e}")

    # ✅ Evita errori se ci sono meno di 2 dati
    if len(elos) < 2:
        messagebox.showinfo("Graph Error", "Not enough data to generate the graph!")
        return

    # ✅ Cambia colore della linea in base alla tendenza globale
    trend_color = "green" if elos[-1] > elos[0] else "red"
    plt.plot(games_played, elos, marker="o", linestyle="-", color=trend_color, linewidth=2)

    # ✅ Controllo se l'Elo cambia: se è costante, rimuove la legenda
    if len(set(elos)) == 1:  
        plt.legend().remove()  # 🔥 Rimuove la legenda se non serve
    else:
        # ✅ Aggiunge la linea di tendenza SOLO se l'Elo cambia
        z = np.polyfit(games_played, elos, 1)  
        p = np.poly1d(z)
        plt.plot(games_played, p(games_played), "--", color="gray", linewidth=2, label="Trend")

        # ✅ Ombreggia l'area attorno alla linea di tendenza
        # plt.fill_between(games_played, p(games_played), alpha=0.1, color="gray")  # Disattivato per evitare warning

    # ✅ Controllo extra per evitare errori se `elos` è vuoto
    if elos and games_played:
        plt.annotate(f"{elos[-1]}", (games_played[-1], elos[-1]), textcoords="offset points",
                     xytext=(-10,5), ha='center', fontsize=10, fontweight='bold', color='black', backgroundcolor="white")

    plt.xlabel("Total Games Played")  
    plt.ylabel("Elo Rating")
    plt.title(f"Elo Rating Progression of {player}\n({games_played[0]} → {games_played[-1]} games)")

    plt.ticklabel_format(style="plain", axis="x")  # 🔥 Evita la notazione scientifica sull'asse X
    plt.ticklabel_format(style="plain", axis="y")  # 🔥 Evita la notazione scientifica sull'asse Y

    plt.xticks(rotation=30)  
    plt.legend()
    plt.grid(True)

    # ✅ Tooltip interattivo per visualizzare Elo al passaggio del mouse
    cursor = mplcursors.cursor(hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(f"Elo: {int(sel.target[1])}"))

    plt.show()

# Function to save rankings to a text file
import os  # 🔥 Importiamo os per cancellare il file prima

def save_rankings_txt():
    ratings = load_ratings()
    
    if not ratings:
        messagebox.showinfo("Export Failed", "No data to save!")
        return

    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1]["elo"], reverse=True)

    with open("rankings.txt", "w", encoding="utf-8") as f:
        f.write("Pos | Player       | Rating |  +  |  -  | Games | Won  | Win%  | Av.opp | Last Update\n")
        f.write("-" * 120 + "\n")  

        for idx, (player, data) in enumerate(sorted_ratings, start=1):
            plus_minus = round((40 / (data["games"] + 1)) ** 0.5 * 100)  
            win_percentage = round((data["won"] / data["games"]) * 100, 1) if data["games"] > 0 else 0  

            # Scrive la riga principale del giocatore
            f.write(f"{idx:<4} | {player:<12} | {data['elo']:<6} | {plus_minus:<3} | {plus_minus:<3} | "
                    f"{data['games']:<5} | {data['won']:<4} | {win_percentage:<5.1f}% | {data['avg_opp']:<6} | "
                    f"{data.get('last_update', 'N/A')}\n")

            # 📌 Scrive la cronologia degli avversari, su righe separate con indentazione
            matches = data.get("matches", [])
            if matches:
                f.write("     Matches:\n")  # Intestazione per i match
                for match in matches:
                    f.write(f"       - {match['opponent']} ({match['opp_elo']}) {match['result']}\n")

            f.write("\n")  # Riga vuota per separare i giocatori

    messagebox.showinfo("Export Successful", "Rankings saved as rankings.txt")


# Function to save rankings to a CSV file
import csv  # ✅ Importiamo il modulo per CSV

def save_rankings_csv():
    ratings = load_ratings()

    if not ratings:
        messagebox.showinfo("Export Failed", "No data to save!")
        return

    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1]["elo"], reverse=True)

    # 🔥 Elimina il file prima di scriverlo (se esiste)
    if os.path.exists("rankings.csv"):
        os.remove("rankings.csv")

    with open("rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="|") 
        
        writer.writerow(["Pos", "Player", "Rating", "+", "-", "Games", "Won", "Win %", "Av.opp", "Last Update", "Matches"])
        
        for idx, (player, data) in enumerate(sorted_ratings, start=1):
            plus_minus = round((40 / (data["games"] + 1)) ** 0.5 * 100)  
            win_percentage = round((data["won"] / data["games"]) * 100, 1) if data["games"] > 0 else 0  

            # 📌 Recupera la cronologia degli avversari
            matches_text = " | ".join(
                [f"{m['opponent']} ({m['opp_elo']}) {m['result']}" for m in data.get("matches", [])]
            )

            print(f"CSV DEBUG → {player}: {matches_text}")

            writer.writerow([
                idx, player, data["elo"], plus_minus, plus_minus, 
                data["games"], data["won"], win_percentage, data["avg_opp"], 
                data.get("last_update", "N/A"), matches_text
            ])

    messagebox.showinfo("Export Successful", "Rankings saved as rankings.csv")

# Create GUI
# Creazione della finestra principale
root = tk.Tk()
root.title("Elo Ranking Manager")
root.geometry("800x600")  # 🔥 Imposta dimensioni iniziali
root.resizable(True, True)  # 🔥 Permette il ridimensionamento

# Configurare il layout per ridimensionamento automatico
root.columnconfigure(1, weight=1)  # Permette allargamento delle colonne
root.columnconfigure(2, weight=1)

# Player 1
tk.Label(root, text="Player 1:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
combo_player1 = ttk.Combobox(root, state="readonly")
combo_player1.grid(row=0, column=1, sticky="ew", padx=10, pady=5)  # 🔥 Si espande
entry_player1 = tk.Entry(root)
entry_player1.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
entry_player1.grid_remove()

tk.Label(root, text="Initial Elo:").grid(row=0, column=2, sticky="w", padx=10, pady=5)
entry_elo1 = tk.Entry(root)
entry_elo1.grid(row=0, column=3, sticky="ew", padx=10, pady=5)

# Player 2
tk.Label(root, text="Player 2:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
combo_player2 = ttk.Combobox(root, state="readonly")
combo_player2.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
entry_player2 = tk.Entry(root)
entry_player2.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
entry_player2.grid_remove()

tk.Label(root, text="Initial Elo:").grid(row=1, column=2, sticky="w", padx=10, pady=5)
entry_elo2 = tk.Entry(root)
entry_elo2.grid(row=1, column=3, sticky="ew", padx=10, pady=5)

# Result input
tk.Label(root, text="Result (e.g., 30-20 or 24.5-24.5):").grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)
entry_result = tk.Entry(root)
entry_result.grid(row=2, column=2, columnspan=2, sticky="ew", padx=10, pady=5)

# Buttons - Espandiamo orizzontalmente con `columnspan`
tk.Button(root, text="New Match", command=enable_manual_entry).grid(row=3, column=0, sticky="ew", padx=10, pady=5)
tk.Button(root, text="Update Elo", command=update_elo).grid(row=3, column=1, sticky="ew", padx=10, pady=5)
tk.Button(root, text="Show Rankings", command=show_rankings).grid(row=3, column=2, columnspan=2, sticky="ew", padx=10, pady=5)

tk.Button(root, text="Save Rankings to TXT", command=save_rankings_txt).grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
tk.Button(root, text="Save Rankings to CSV", command=save_rankings_csv).grid(row=4, column=2, columnspan=2, sticky="ew", padx=10, pady=5)
tk.Button(root, text="Show Player Graph", command=show_player_rating_graph).grid(row=6, column=0, columnspan=4, sticky="ew", padx=10, pady=5)


update_comboboxes()

root.mainloop()
