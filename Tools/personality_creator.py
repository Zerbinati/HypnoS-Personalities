import json
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QSlider, 
    QLineEdit, QFileDialog, QCheckBox, QHBoxLayout, QMessageBox, QToolButton, QStyle, QSizePolicy, QFrame
)

class PersonalityEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("HypnoS Personality Creator")
        self.setGeometry(100, 100, 650, 850)
        self.layout = QVBoxLayout()

        # 🔹 Personality Name
        self.layout.addWidget(QLabel("Personality Name:"))
        self.name_input = QLineEdit()
        self.name_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # ⬅️ Altezza fissa
        self.name_input.setMaximumHeight(25)  # ⬅️ Limita altezza
        self.layout.addWidget(self.name_input)

        # 🔹 Description
        self.layout.addWidget(QLabel("Description:"))
        self.desc_input = QLineEdit()
        self.desc_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.desc_input.setMaximumHeight(25)
        self.layout.addWidget(self.desc_input)

        # 🔹 Elo Note
        self.layout.addWidget(QLabel("Elo Note (Suggested Elo):"))
        self.elo_note_input = QLineEdit()
        self.elo_note_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.elo_note_input.setMaximumHeight(25)
        self.layout.addWidget(self.elo_note_input)

        # 🔹 Personality Book
        self.personality_book = QCheckBox("Use Opening Book")
        self.personality_book.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.personality_book.setMaximumHeight(20)
        self.layout.addWidget(self.personality_book)

        # 🔹 Book File
        self.layout.addWidget(QLabel("Book File:"))
        self.book_file_input = QLineEdit()
        self.book_file_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.book_file_input.setMaximumHeight(25)
        self.layout.addWidget(self.book_file_input)

        # 🔹 Creiamo un contenitore per gli slider per evitare problemi di layout
        slider_container = QVBoxLayout()
        slider_frame = QFrame()
        slider_frame.setLayout(slider_container)
        slider_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # ⬅️ Gli slider si ridimensionano correttamente

        # 🔹 Book Width
        book_width_layout = QHBoxLayout()
        self.book_width_label = QLabel("Book Width: 5")
        book_width_layout.addWidget(self.book_width_label)

        self.book_width_slider = QSlider()
        self.book_width_slider.setMinimum(1)
        self.book_width_slider.setMaximum(20)
        self.book_width_slider.setValue(5)
        self.book_width_slider.setOrientation(1)
        self.book_width_slider.valueChanged.connect(lambda v: self.book_width_label.setText(f"Book Width: {v}"))
        book_width_layout.addWidget(self.book_width_slider)
        slider_container.addLayout(book_width_layout)

        # 🔹 Book Depth
        book_depth_layout = QHBoxLayout()
        self.book_depth_label = QLabel("Book Depth: 5")
        book_depth_layout.addWidget(self.book_depth_label)

        self.book_depth_slider = QSlider()
        self.book_depth_slider.setMinimum(1)
        self.book_depth_slider.setMaximum(30)
        self.book_depth_slider.setValue(5)
        self.book_depth_slider.setOrientation(1)
        self.book_depth_slider.valueChanged.connect(lambda v: self.book_depth_label.setText(f"Book Depth: {v}"))
        book_depth_layout.addWidget(self.book_depth_slider)
        slider_container.addLayout(book_depth_layout)

        # 🔹 Evaluation Parameters  
        self.params = {  
            "Aggressiveness": 0, "RiskTaking": 0, "KingSafety": 0, "PieceActivity": 0,  
            "PawnStructure": 0, "KnightPair": 0, "BishopPair": 0,  
            "Defense": 0, "CalculationDepth": 0, "EndgameKnowledge": 0, "PieceSacrifice": 0,  
            "CenterControl": 0, "PositionClosure": 0, "PieceTrade": 0, "KingAttack": 0,  
            "PositionalSacrifice": 0, "KnightVsBishop": 0,  
            "PawnPush": 0, "OpenFileControl": 0  
        }  
        self.param_sliders = {}
        self.explanations = {}

        for param in self.params.keys():
            param_layout = QHBoxLayout()

            label = QLabel(f"{param}: 0")
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            param_layout.addWidget(label)

            slider = QSlider()
            if param in ["Defense", "CalculationDepth", "EndgameKnowledge"]:
                slider.setMinimum(0)
            elif param == "KnightVsBishop":
                slider.setMinimum(-50)
            else:
                slider.setMinimum(0)

            if param in ["Aggressiveness", "RiskTaking"]:
                slider.setMaximum(30)  # 🔥 Limite massimo aggiornato a 30
            elif param == "CalculationDepth":
                slider.setMaximum(18)
            else:
                slider.setMaximum(50)

            slider.setValue(0)
            slider.setOrientation(1)
            slider.valueChanged.connect(lambda value, p=param, lbl=label: self.update_param(value, p, lbl))
            param_layout.addWidget(slider)

            # 🔹 Info Button (ℹ️)
            info_button = QToolButton()
            info_button.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
            info_button.clicked.connect(lambda _, p=param: self.show_explanation(p))
            param_layout.addWidget(info_button)

            slider_container.addLayout(param_layout)
            self.param_sliders[param] = slider

        self.layout.addWidget(slider_frame)  # ⬅️ Inseriamo gli slider nel layout principale

        # 🔹 Save and Load Buttons
        btn_layout = QHBoxLayout()
        
        load_btn = QPushButton("Load Personality")
        load_btn.clicked.connect(self.load_personality)
        btn_layout.addWidget(load_btn)

        save_btn = QPushButton("Save Personality")
        save_btn.clicked.connect(self.save_personality)
        btn_layout.addWidget(save_btn)

        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)

    def update_param(self, value, param, label):
        label.setText(f"{param}: {value}")
        self.params[param] = value

    def show_explanation(self, param):
        explanation = self.explanations.get(param, "No explanation available.")
        QMessageBox.information(self, f"{param} Explanation", explanation)

    def save_personality(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Personality", "", "JSON Files (*.json)")
        if filename:
            data = {
                "name": self.name_input.text(),
                "description": self.desc_input.text(),
                "Elo_Note": self.elo_note_input.text(),  # ✅ Ora è dinamico
                "PersonalityBook": self.personality_book.isChecked(),
                "BookFile": self.book_file_input.text(),
                "BookWidth": self.book_width_slider.value(),
                "BookDepth": self.book_depth_slider.value(),
                "evaluation": self.params,
                "explanation": self.explanations,
                "loss_streak": 0  # ✅ Sempre presente nei file JSON salvati
            }
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                print(f"✅ Personality saved in {filename}")
            except Exception as e:
                print(f"❌ Error saving personality: {e}")
                QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")


    def load_personality(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Personality", "", "JSON Files (*.json)")
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.name_input.setText(data.get("name", ""))
                self.desc_input.setText(data.get("description", ""))
                self.elo_note_input.setText(data.get("Elo_Note", ""))  # ✅ Ora viene caricato correttamente
                self.personality_book.setChecked(data.get("PersonalityBook", False))
                self.book_file_input.setText(data.get("BookFile", "books/default.bin"))
                self.book_width_slider.setValue(data.get("BookWidth", 5))
                self.book_depth_slider.setValue(data.get("BookDepth", 5))

                for param, slider in self.param_sliders.items():
                    slider.setValue(data.get("evaluation", {}).get(param, 0))

                self.explanations = data.get("explanation", {})

                print(f"✅ Personality {data['name']} loaded successfully!")

            except Exception as e:
                print(f"❌ Error loading personality: {e}")
                QMessageBox.critical(self, "Error", f"Could not load file:\n{e}")

# 🔹 Launching the GUI
app = QApplication(sys.argv)
editor = PersonalityEditor()
editor.show()
sys.exit(app.exec_())
