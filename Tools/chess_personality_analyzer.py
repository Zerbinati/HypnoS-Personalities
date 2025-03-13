import sys
import chess
import chess.pgn
import chess.engine
import json
import chess.svg
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QComboBox, QLineEdit, QTextEdit, QMessageBox
)
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import QByteArray


class ChessPersonalityAnalyzer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chess Personality Analyzer")
        self.setGeometry(100, 100, 900, 700)

        self.layout = QVBoxLayout()

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

        # Board Display (Scacchiera)
        self.board_widget = QSvgWidget()
        self.board_widget.setFixedSize(400, 400)
        self.layout.addWidget(self.board_widget)

        # Analysis Button
        self.analyze_button = QPushButton("Analyze Game")
        self.analyze_button.clicked.connect(self.analyze_game)
        self.layout.addWidget(self.analyze_button)

        # Table for Results
        self.result_table = QTableWidget(0, 2)
        self.result_table.setHorizontalHeaderLabels(["Parameter", "Deviation"])
        self.layout.addWidget(self.result_table)

        # Report Output
        self.report_output = QTextEdit()
        self.report_output.setReadOnly(True)
        self.layout.addWidget(self.report_output)

        self.setLayout(self.layout)

        self.pgn_file = None
        self.json_file = None
        self.engine = None
        self.personality = {}
        self.board = chess.Board()  # Inizializza la scacchiera

    def load_pgn(self):
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
            self.board = game.board()  # Resetta la scacchiera
            self.update_board()  # Aggiorna la grafica della scacchiera

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
        file_name, _ = QFileDialog.getOpenFileName(self, "Select UCI Engine", "", "Executables (*.exe)")
        if file_name:
            self.engine = chess.engine.SimpleEngine.popen_uci(file_name)
            self.engine_label.setText(f"Engine: {file_name}")

    def analyze_game(self):
        if not self.pgn_file or not self.json_file or not self.engine:
            QMessageBox.warning(self, "Warning", "Load PGN, JSON, and UCI engine before analyzing.")
            return

        with open(self.pgn_file) as f:
            game = chess.pgn.read_game(f)

        self.board = game.board()  # Reset board
        analysis_results = {}

        for move in game.mainline_moves():
            self.board.push(move)
            info = self.engine.analyse(self.board, chess.engine.Limit(depth=15))

            eval_score = info["score"].relative.score()
            self.evaluate_move(move, eval_score, analysis_results)

            self.update_board()  # Mostra la nuova posizione sulla scacchiera

        self.generate_report(analysis_results)

    def evaluate_move(self, move, eval_score, analysis_results):
        parameters = self.personality.get("evaluation", {})

        # Esempio di valutazione base
        aggressiveness = parameters.get("Aggressiveness", 25)
        king_safety = parameters.get("KingSafety", 50)
        piece_activity = parameters.get("PieceActivity", 35)

        move_aggressiveness = eval_score / 100  # Normalizza punteggio
        move_king_safety = 50 if self.board.is_check() else 100
        move_piece_activity = len(list(self.board.legal_moves))

        analysis_results["Aggressiveness"] = abs(aggressiveness - move_aggressiveness)
        analysis_results["KingSafety"] = abs(king_safety - move_king_safety)
        analysis_results["PieceActivity"] = abs(piece_activity - move_piece_activity)

    def generate_report(self, analysis_results):
        report_text = "🎭 Personality Analysis Report\n"
        report_text += "=" * 40 + "\n"

        for param, deviation in analysis_results.items():
            report_text += f"🔹 {param}: Deviation {deviation:.2f}\n"

        self.report_output.setText(report_text)

    def update_board(self):
        """Aggiorna la scacchiera nella GUI"""
        svg_data = chess.svg.board(board=self.board)
        self.board_widget.load(QByteArray(svg_data.encode("utf-8")))

    def closeEvent(self, event):
        if self.engine:
            self.engine.quit()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChessPersonalityAnalyzer()
    window.show()
    sys.exit(app.exec_())
