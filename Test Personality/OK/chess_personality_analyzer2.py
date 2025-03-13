import sys
import os  # ✅ Aggiunto qui
import chess
import chess.pgn
import chess.engine
import json
import chess.svg
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
    QTableWidget, QTableWidgetItem, QTextEdit, QMessageBox, QComboBox, QInputDialog
)
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import QByteArray, QThread, pyqtSignal

# Set terminal title
os.system("title HypnoS Chess Personality Analyzer")



class ChessPersonalityAnalyzer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HypnoS Chess Personality Analyzer")
        self.setGeometry(100, 100, 900, 700)

        self.layout = QVBoxLayout()

        # Chessboard
        self.board_widget = QSvgWidget()
        self.board_widget.setFixedSize(400, 400)
        self.layout.addWidget(self.board_widget)

        # PGN Selection
        self.pgn_label = QLabel("No PGN selected")
        self.layout.addWidget(self.pgn_label)

        self.pgn_button = QPushButton("Select PGN File")
        self.pgn_button.clicked.connect(self.load_pgn)
        self.layout.addWidget(self.pgn_button)

        # JSON Selection
        self.json_label = QLabel("No JSON selected")
        self.layout.addWidget(self.json_label)

        self.json_button = QPushButton("Select JSON File")
        self.json_button.clicked.connect(self.load_json)
        self.layout.addWidget(self.json_button)

        # Engine Selection
        self.engine_label = QLabel("No UCI engine selected")
        self.layout.addWidget(self.engine_label)

        self.engine_button = QPushButton("Select UCI Engine")
        self.engine_button.clicked.connect(self.load_engine)
        self.layout.addWidget(self.engine_button)

        # Debug Log File
        self.debug_label = QLabel("Debug Log File")
        self.layout.addWidget(self.debug_label)

        # UCI Options Dropdown
        self.uci_options_dropdown = QComboBox()
        self.layout.addWidget(self.uci_options_dropdown)

        self.uci_set_button = QPushButton("Set UCI Option")
        self.uci_set_button.clicked.connect(self.set_uci_option)
        self.layout.addWidget(self.uci_set_button)

        # Analysis Button
        self.analyze_button = QPushButton("Analyze Games")
        self.analyze_button.clicked.connect(self.analyze_games)
        self.layout.addWidget(self.analyze_button)

        # Table for Results
        self.result_table = QTableWidget(0, 2)
        self.result_table.setHorizontalHeaderLabels(["Parameter", "Deviation"])
        self.layout.addWidget(self.result_table)

        # Report Output
        self.report_output = QTextEdit()
        self.report_output.setReadOnly(True)
        self.layout.addWidget(self.report_output)

        # 🔥 NEW: Analysis Details Box (Score, Depth, Best Move, Principal Variation)
        self.analysis_details = QTextEdit()
        self.analysis_details.setReadOnly(True)
        self.analysis_details.setPlaceholderText("Analysis details will appear here...")
        self.layout.addWidget(self.analysis_details)

        # Save Report
        self.save_report_button = QPushButton("Save Report")
        self.save_report_button.clicked.connect(self.save_report)
        self.layout.addWidget(self.save_report_button)

        self.setLayout(self.layout)

        # State Variables
        self.pgn_file = None
        self.json_file = None
        self.engine = None
        self.personality = {}
        self.board = chess.Board()

        # Definition of playstyles based on parameters
        self.styles = {
            "attackers": ["Aggressiveness", "KingAttack", "PieceSacrifice", "PawnPush"],
            "positional": ["PawnStructure", "CenterControl", "PieceActivity", "OpenFileControl"],
            "strategic": ["CalculationDepth", "PositionalSacrifice", "Defense", "EndgameKnowledge"],
            "defensive": ["KingSafety", "Defense", "PieceTrade"],
            "creative": ["RiskTaking", "KnightVsBishop", "BishopPair", "KnightPair"],
            "universal": ["Aggressiveness", "PieceActivity", "CenterControl", "CalculationDepth", "KingSafety"]
        }

        self.update_board()

    def load_pgn(self):
        """Loads a PGN file selected by the user."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select PGN File", "", "PGN Files (*.pgn)")
        if file_name:
            self.pgn_file = file_name
            self.pgn_label.setText(f"PGN: {file_name}")
            self.load_game()

    def load_game(self):
        if not self.pgn_file:
            return

        with open(self.pgn_file) as f:
            game = chess.pgn.read_game(f)
            self.board = game.board()  # Resets the chessboard
            self.update_board()  # Updates the board display

    def load_json(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)")
        if file_name:
            self.json_file = file_name
            self.json_label.setText(f"JSON: {file_name}")
            self.load_personality()

    def load_personality(self):
        if not self.json_file:
            return

        try:
            with open(self.json_file, "r") as f:
                self.personality = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load JSON: {e}")

    def load_engine(self):
        """Loads a selected UCI engine and retrieves its options."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select UCI Engine", "", "Executables (*.exe)")
        if file_name:
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(file_name)
                self.engine_label.setText(f"Engine: {file_name}")
                print(f"✅ UCI engine loaded: {file_name}")
                self.load_uci_options()  # 🔥 Load available UCI options immediately!
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load UCI engine: {e}")

    def load_uci_options(self):
        """Loads available UCI engine options and makes them editable."""
        if self.engine:
            self.uci_options_dropdown.clear()
            self.uci_options_dropdown.setEditable(True)
            for option in self.engine.options:
                self.uci_options_dropdown.addItem(option)

    def set_uci_option(self):
        """Allows modifying UCI engine settings."""
        if not self.engine:
            QMessageBox.warning(self, "Warning", "No UCI engine loaded!")
            return

        option_name = self.uci_options_dropdown.currentText()

        if option_name in self.engine.options:
            option = self.engine.options[option_name]
            option_dict = option.__dict__  # ✅ Controlliamo gli attributi interni dell'opzione

            print(f"DEBUG: {option_name} attributes: {option_dict}")  # 🔥 Debug per verificare gli attributi

            if hasattr(option, "min") and hasattr(option, "max"):  # ✅ Riconosciamo "Threads" come SpinOption
                value, ok = QInputDialog.getInt(self, "Set UCI Option", f"Set {option_name}:", option.default, option.min, option.max)
            elif isinstance(option.default, str):  # ✅ È una StringOption
                value, ok = QInputDialog.getText(self, "Set UCI Option", f"Set {option_name}:", text=option.default)
            elif isinstance(option.default, bool):  # ✅ È una CheckOption (True/False)
                value, ok = QInputDialog.getItem(self, "Set UCI Option", f"Enable {option_name}?", ["True", "False"], 0, False)
                value = value == "True"
            else:
                QMessageBox.critical(self, "Error", f"Unsupported UCI option type for {option_name}. (Attributes: {option_dict})")
                return

            if ok:
                try:
                    self.engine.configure({option_name: value})  # ✅ Ora tutte le opzioni dovrebbero funzionare
                    QMessageBox.information(self, "Success", f"{option_name} set to {value}!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to set UCI option: {e}")

    class AnalysisThread(QThread):
        analysis_complete = pyqtSignal(dict)

        def __init__(self, engine, pgn_file, personality):
            super().__init__()
            self.engine = engine
            self.pgn_file = pgn_file
            self.personality = personality

        def run(self):
            """Runs the game analysis in a separate thread."""
            analysis_results = {param: 0 for param in self.personality.get("evaluation", {}).keys()}
            total_games = 0

            with open(self.pgn_file) as f:
                while True:
                    game = chess.pgn.read_game(f)
                    if game is None:
                        break
                    total_games += 1
                    board = game.board()

                    for move in game.mainline_moves():
                        board.push(move)
                        info = self.engine.analyse(board, chess.engine.Limit(depth=15))
                        eval_score = info["score"].relative.score()
                        self.evaluate_move(eval_score, analysis_results)

            if total_games > 0:
                for param in analysis_results.keys():
                    analysis_results[param] /= total_games

            self.analysis_complete.emit(analysis_results)  # ✅ Segnale per aggiornare la GUI

    def update_analysis_details(self, move_number, move_san, score_text, depth, best_move_san, pv_san):
        """Updates the analysis details box in the GUI in real-time."""
        new_entry = (
            f"\nMove {move_number}: {move_san}\n"
            f"  ➤ Evaluation: {score_text}\n"
            f"  ➤ Depth: {depth}\n"
            f"  ➤ Best Move: {best_move_san}\n"
            f"  ➤ Principal Variation: {pv_san}\n"
        )

        self.analysis_details.append(new_entry)  # ✅ Add text to the box
        self.analysis_details.verticalScrollBar().setValue(self.analysis_details.verticalScrollBar().maximum())  # 🔄 Auto-scroll
        QApplication.processEvents()  # ✅ Prevents GUI freeze

    def analyze_games(self):
        """Analyzes games and updates the board and GUI in real-time."""
        if not self.pgn_file or not self.json_file or not self.engine:
            QMessageBox.warning(self, "Warning", "Load PGN, JSON, and UCI engine before analyzing.")
            return

        with open(self.pgn_file) as f:
            games = []
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                games.append(game)

        analysis_results = {param: 0 for param in self.personality.get("evaluation", {}).keys()}
        total_games = len(games)

        print("\n=== Starting Analysis ===")  # ✅ Start message
        game_number = 1

        for game in games:
            self.board = game.board()
            move_number = 1

            print(f"\n--- Analyzing Game {game_number} ---")
            game_number += 1

            for move in game.mainline_moves():
                self.board.push(move)

                # Analyze position with the engine
                info = self.engine.analyse(self.board, chess.engine.Limit(depth=15))
                eval_score = info["score"].relative

                # Score handling: centipawn or checkmate
                if eval_score.is_mate():
                    score_text = f"# {eval_score.mate()}"  # Example: #3 (Mate in 3)
                else:
                    score_text = f"{eval_score.score() / 100:.2f}"  # Convert to pawn units

                best_move = info.get("pv", [None])[0]  # Get best move suggested
                depth = info.get("depth", 0)  # Get analysis depth
                pv = info.get("pv", [])  # Get principal variation

                # Check if move is legal before converting to SAN notation
                if move in self.board.legal_moves:
                    move_san = self.board.san(move)
                else:
                    move_san = move.uci()  # If not legal, use UCI notation

                # Check if best move is valid before converting
                if best_move and best_move in self.board.legal_moves:
                    best_move_san = self.board.san(best_move)
                else:
                    best_move_san = best_move.uci() if best_move else "N/A"

                # Check if principal variation is valid
                if pv:  # Ensure the PV is not empty
                    try:
                        pv_san = " ".join(self.board.san(m) for m in pv if m in self.board.legal_moves)
                    except Exception as e:
                        print(f"Error processing PV: {e}")  # Debugging message
                        pv_san = "N/A"
                else:
                    pv_san = "N/A"

                # Print move information in the terminal
                print(f"\nMove {move_number}: {move_san}")
                print(f"  ➤ Evaluation: {score_text}")
                print(f"  ➤ Depth: {depth}")
                print(f"  ➤ Best Move: {best_move_san}")
                print(f"  ➤ Principal Variation: {pv_san}")

                # 🔥 Update the GUI with move information
                self.update_analysis_details(move_number, move_san, score_text, depth, best_move_san, pv_san)

                # Calculate deviations
                self.evaluate_move(eval_score.score(), analysis_results)

                move_number += 1

                # ✅ Update the board after every analyzed move
                self.update_board()
                QApplication.processEvents()  # ✅ Prevents GUI freeze, updates in real-time

        # Normalize results based on the number of analyzed games
        for param in analysis_results.keys():
            analysis_results[param] /= total_games

        self.generate_report(analysis_results)
        self.suggest_json_update(analysis_results)

        print("\n=== Analysis Complete ===")  # ✅ End message

    def on_analysis_complete(self, analysis_results):
        """Updates the GUI when analysis is complete."""
        self.generate_report(analysis_results)
        self.suggest_json_update(analysis_results)
        self.update_board()  # ✅ Aggiorna la scacchiera dopo l'analisi

    def update_board(self):
        """Updates the chessboard with the current position."""
        if not self.board:
            return

        try:
            board_svg = chess.svg.board(self.board).encode("utf-8")
            self.board_widget.load(QByteArray(board_svg))
        except Exception as e:
            print(f"Error updating the chessboard: {e}")

    def evaluate_move(self, eval_score, analysis_results):
        parameters = self.personality.get("evaluation", {})

        # Define the maximum range for each parameter
        max_ranges = {
            "Aggressiveness": 30, "RiskTaking": 30, "KingSafety": 50, "PieceActivity": 50,
            "PawnStructure": 50, "KnightPair": 50, "BishopPair": 50, "Defense": 50,
            "CalculationDepth": 18, "EndgameKnowledge": 50, "PieceSacrifice": 50,
            "CenterControl": 50, "PositionClosure": 50, "PieceTrade": 50, "KingAttack": 50,
            "PositionalSacrifice": 50, "KnightVsBishop": 100,  # -50 to 50 → total range 100
            "PawnPush": 50, "OpenFileControl": 50
        }

        for param in parameters.keys():
            expected_value = parameters[param]  # Expected value from JSON
            actual_value = eval_score / 100 if eval_score else 0  # Normalization

            # Get the maximum range for the parameter, default to 50 if not found
            max_range = max_ranges.get(param, 50)

            # Calculate deviation
            deviation = abs(expected_value - actual_value)

            # 🔥 Debug: Print raw values before normalization
            print(f"{param}: Expected={expected_value}, Actual={actual_value}, Raw Deviation={deviation:.2f}")

            # Avoid division by zero
            if max_range > 0:
                normalized_deviation = (deviation / max_range) * 50  # Scale to a max range of 50
            else:
                normalized_deviation = 0

            # Cap the deviation but allow smoother scaling
            adjusted_deviation = min(normalized_deviation, 50)  # Max deviation is 50

            # 🔥 Debug: Print normalized values
            print(f"{param}: Normalized Deviation={normalized_deviation:.2f}, Adjusted Deviation={adjusted_deviation:.2f}")

            analysis_results[param] += adjusted_deviation

    def determine_playstyle(self, analysis_results):
        """Determines the playstyle based on weighted scoring, ensuring clear differentiation."""

        playstyle_scores = {style: 0 for style in self.styles.keys()}

        dominant_traits = {
            "attackers": ["Aggressiveness", "RiskTaking", "PieceSacrifice", "KingAttack"],
            "positional": ["PawnStructure", "CenterControl", "PieceActivity"],
            "strategic": ["CalculationDepth", "EndgameKnowledge", "PositionalSacrifice"],
            "defensive": ["KingSafety", "Defense", "PieceTrade"],
            "creative": ["RiskTaking", "KnightVsBishop", "BishopPair"],
            "universal": ["Aggressiveness", "PieceActivity", "CenterControl", "CalculationDepth", "KingSafety"]
        }

        # 🔥 **Assign weighted scores to each playstyle**
        for style, params in self.styles.items():
            for param in params:
                if param in analysis_results:
                    deviation = analysis_results[param]

                    # ✅ Double weight for dominant characteristics of each playstyle
                    if param in dominant_traits[style]:
                        playstyle_scores[style] += deviation * 3.0  # 🔥 Aumentato da 2.0 a 3.0
                    else:
                        playstyle_scores[style] += deviation * 1.0

        # 🎯 **Debug: Print assigned scores for each playstyle**
        print("\n🎯 Playstyle Scores:")
        for style, score in playstyle_scores.items():
            print(f"  {style.upper()}: {score:.2f}")

        # 🏆 **Determine the best fitting playstyle**
        best_fit = max(playstyle_scores, key=playstyle_scores.get)

        # ⚖️ **Check if one playstyle dominates over others**
        sorted_scores = sorted(playstyle_scores.values(), reverse=True)
        if sorted_scores[0] > 1.3 * sorted_scores[1]:  
            print(f"\n🏆 Best Fit: {best_fit.upper()} (Dominant)")
            return best_fit.upper()

        print(f"\n⚖️ No clear dominance, assigning UNIVERSAL")
        return "UNIVERSAL"

    def update_result_table(self, analysis_results):
        """Updates the table with calculated deviations."""
        self.result_table.setRowCount(len(analysis_results))  # Set number of rows

        for row, (param, deviation) in enumerate(analysis_results.items()):
            deviation = min(round(deviation), 50)  # 🔥 Round to an integer and limit to 50
            self.result_table.setItem(row, 0, QTableWidgetItem(param))  # Column 1: Parameter name
            self.result_table.setItem(row, 1, QTableWidgetItem(f"{deviation}"))  # Column 2: Rounded value

    def generate_report(self, analysis_results):
        """Generates a detailed report comparing expected and actual playstyle."""
        report_text = "🎭 HypnoS Personality Analysis Report\n"
        report_text += "=" * 40 + "\n"

        for param, deviation in analysis_results.items():
            expected_value = self.personality["evaluation"].get(param, "N/A")  # Expected value from JSON
            deviation = min(round(deviation), 50)  # 🔥 Round to an integer and limit to 50

            # Interpretation based on deviation
            if deviation > 40:
                interpretation = "🔺 Significantly higher than expected."
            elif deviation > 20:
                interpretation = "⚠️ Slightly higher than expected."
            elif deviation < 10:
                interpretation = "🔹 Similar to expected style."
            else:
                interpretation = "⚖️ Moderate difference from expected."

            report_text += f"{param}: Expected {expected_value}, Deviation {deviation} → {interpretation}\n"

        # Determine playstyle and add it to the report
        playstyle = self.determine_playstyle(analysis_results)
        report_text += f"\n♟️ **Detected playstyle:** **{playstyle}** ♜\n"

        self.report_output.setText(report_text)  # Update text report
        self.update_result_table(analysis_results)  # 🔥 Update table with results

    def suggest_json_update(self, analysis_results):
        """Suggests updating JSON values while preserving distinct playstyles."""
        reply = QMessageBox.question(
            self, "Update JSON?", "Deviation detected. Update JSON values?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            updated_values = {}

            # Define key traits for each playstyle
            aggressive_traits = ["Aggressiveness", "RiskTaking", "PieceSacrifice", "KingAttack"]
            defensive_traits = ["KingSafety", "Defense", "PositionalSacrifice", "PieceTrade"]
            calculation_traits = ["CalculationDepth"]

            max_uci_range = {"Aggressiveness": 30, "RiskTaking": 30, "CalculationDepth": 18}

            for key, deviation in analysis_results.items():
                expected_value = self.personality["evaluation"].get(key, 25)

                # 🔹 Adjust the scaling to avoid over-correction
                deviation_scaled = (deviation / 350) ** 1.1  # Exponential scaling for smoother adaptation
                
                # 🔹 Adjust correction factor based on playstyle tendencies
                if key in aggressive_traits:
                    correction_factor = 0.4 + (expected_value / 100)  # 🔥 Aggressive players stay aggressive
                elif key in defensive_traits:
                    correction_factor = 4.0 + (expected_value / 50)  # 🔥 Prevents too much defense growth
                elif key in calculation_traits:
                    correction_factor = 1.2 + (expected_value / 80)  # 🔥 Encourages deeper calculation
                else:
                    correction_factor = 1.9 + (expected_value / 70)  # 🔥 Standard correction

                correction = round(deviation_scaled / correction_factor)

                # 🔹 Preserve aggressive identity
                if key in aggressive_traits:
                    actual_value = max(expected_value, expected_value - correction)  # 🔥 Never decrease aggression
                elif key in defensive_traits:
                    actual_value = min(expected_value, expected_value + correction)  # 🔥 Avoid boosting defense
                else:
                    actual_value = expected_value - correction if deviation > 0 else expected_value + correction

                max_value = max_uci_range.get(key, 50)
                min_value = 10  # General minimum
                if key in aggressive_traits:
                    min_value = 30  # 🔥 Ensure Tal remains aggressive
                elif key in calculation_traits:
                    min_value = 14  

                corrected_value = max(min_value, min(max_value, round(actual_value)))

                updated_values[key] = corrected_value
                print(f"Updating {key}: Expected={expected_value}, Deviation={deviation}, Suggested={corrected_value}")

            self.personality["evaluation"].update(updated_values)

            try:
                with open(self.json_file, "w") as f:
                    json.dump(self.personality, f, indent=4)
                QMessageBox.information(self, "Update", "JSON updated successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save JSON: {e}")

    def save_report(self):
        """Saves the analysis report as a TXT file."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "Text Files (*.txt)")

        if file_name:
            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(self.report_output.toPlainText())  # ✅ Salva il contenuto della GUI nel file TXT
                QMessageBox.information(self, "Success", "Report saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save report: {e}")

    def closeEvent(self, event):
        if self.engine:
            self.engine.quit()
        event.accept()

        try:
            board_svg = chess.svg.board(self.board).encode("utf-8")
            self.board_widget.load(QByteArray(board_svg))
        except Exception as e:
            print(f"Error updating the chessboard: {e}")

# Start the GUI
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChessPersonalityAnalyzer()
    window.show()
    sys.exit(app.exec_())
