import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit, 
    QPushButton, QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem, 
    QHeaderView, QLabel, QAbstractItemView
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from .progetti_ctrl import ProgettiController


class DialogGestioneProgetti(QDialog):
    """Finestra pop-up per selezionare, aggiungere o eliminare progetti recenti (tramite Composizione)."""
    def __init__(self, parent=None, percorso_corrente=""):
        super().__init__(parent)
        self.i18n = getattr(parent, 'i18n', None)
        self.percorso_selezionato = percorso_corrente
        self.controller = ProgettiController(self)

        self.setWindowTitle(self.i18n.t("auto_extracted.title_project_management"))
        self.resize(720, 560)

        layout = QVBoxLayout(self)

        # Sezione 1: Tabella Progetti Recenti
        layout.addWidget(QLabel(self.i18n.t("auto_extracted.instr_select_project")))
        
        self.tabella_progetti = QTableWidget(0, 3)
        self.tabella_progetti.setHorizontalHeaderLabels(["Nome Progetto", "Percorso", "Note"])
        self.tabella_progetti.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabella_progetti.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tabella_progetti.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabella_progetti.setWordWrap(True)
        
        self.tabella_progetti.keyPressEvent = self._tabella_key_press
        
        header = self.tabella_progetti.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabella_progetti.setColumnWidth(0, 150)
        self.tabella_progetti.setColumnWidth(1, 280)

        self.tabella_progetti.itemSelectionChanged.connect(self._on_riga_selezionata)
        self.tabella_progetti.itemDoubleClicked.connect(self._carica_da_riga_selezionata)
        layout.addWidget(self.tabella_progetti)

        btn_carica_tabella = QPushButton(self.i18n.t("auto_extracted.btn_open_selected_project"))
        btn_carica_tabella.clicked.connect(self._carica_da_riga_selezionata)
        layout.addWidget(btn_carica_tabella)

        layout.addSpacing(15)

        # Sezione 2: Inserimento / Modifica Progetto
        layout.addWidget(QLabel(self.i18n.t("auto_extracted.instr_edit_project")))
        form_layout = QFormLayout()

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText(self.i18n.t("auto_extracted.placeholder_project_name"))
        form_layout.addRow("<b>Nome Progetto:</b>", self.input_nome)

        box_percorso = QHBoxLayout()
        self.input_percorso = QLineEdit()
        self.input_percorso.setPlaceholderText(self.i18n.t("placeholder_project_path"))
        btn_sfoglia = QPushButton(self.i18n.t("auto_extracted.btn_browse"))
        btn_sfoglia.clicked.connect(self._sfoglia_cartella)
        box_percorso.addWidget(self.input_percorso)
        box_percorso.addWidget(btn_sfoglia)
        form_layout.addRow("<b>Percorso:</b>", box_percorso)

        self.input_note = QTextEdit()
        self.input_note.setPlaceholderText(self.i18n.t("auto_extracted.placeholder_project_notes"))
        self.input_note.setMaximumHeight(70)
        form_layout.addRow("<b>Note:</b>", self.input_note)

        layout.addLayout(form_layout)

        btn_salva_nuovo = QPushButton(self.i18n.t("auto_extracted.btn_save_open_project"))
        btn_salva_nuovo.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        btn_salva_nuovo.setStyleSheet("background-color: #16A34A; color: white; padding: 6px; border-radius: 4px;")
        btn_salva_nuovo.clicked.connect(self._salva_e_carica_nuovo)
        layout.addWidget(btn_salva_nuovo)

        self._carica_csv()

    def _tabella_key_press(self, event):
        """Intercetta la pressione dei tasti Backspace o Canc sulla tabella per cancellare le righe."""
        if event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            self._elimina_righe_selezionate()
        else:
            QTableWidget.keyPressEvent(self.tabella_progetti, event)

    def _elimina_righe_selezionate(self):
        """Rimuove le righe selezionate dalla tabella e aggiorna il file CSV tramite il controller."""
        selected_items = self.tabella_progetti.selectedItems()
        if not selected_items:
            return

        rows = sorted(list(set(item.row() for item in selected_items)), reverse=True)
        
        risposta = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare {len(rows)} progetto/i selezionato/i dalla cronologia?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if risposta == QMessageBox.StandardButton.Yes:
            self.controller.elimina_righe(rows)
            self._carica_csv()
            self.input_nome.clear()
            self.input_percorso.clear()
            self.input_note.clear()

    def _carica_csv(self):
        """Legge i progetti dal controller e popola la tabella."""
        progetti = self.controller.carica_csv()
        self.tabella_progetti.setRowCount(0)

        for row_idx, p in enumerate(progetti):
            self.tabella_progetti.insertRow(row_idx)
            self.tabella_progetti.setItem(row_idx, 0, QTableWidgetItem(p['nome']))
            self.tabella_progetti.setItem(row_idx, 1, QTableWidgetItem(p['percorso']))
            self.tabella_progetti.setItem(row_idx, 2, QTableWidgetItem(p['note']))

        self.tabella_progetti.resizeRowsToContents()

    def _sfoglia_cartella(self):
        cartella = QFileDialog.getExistingDirectory(self, "Seleziona la cartella radice del progetto")
        if cartella:
            self.input_percorso.setText(cartella)
            if not self.input_nome.text().strip():
                self.input_nome.setText(os.path.basename(cartella))

    def _on_riga_selezionata(self):
        row = self.tabella_progetti.currentRow()
        if 0 <= row < len(self.controller.progetti):
            p = self.controller.progetti[row]
            self.input_nome.setText(p['nome'])
            self.input_percorso.setText(p['percorso'])
            self.input_note.setPlainText(p['note'])

    def _carica_da_riga_selezionata(self):
        nome = self.input_nome.text().strip()
        percorso = self.input_percorso.text().strip()
        note = self.input_note.toPlainText().strip()

        if percorso and os.path.exists(percorso):
            self.controller.salva_csv(nome, percorso, note)
            self.percorso_selezionato = percorso
            self.accept()
        else:
            QMessageBox.warning(self, "Percorso non trovato", f"La cartella non esiste sul disco:\n{percorso}")

    def _salva_e_carica_nuovo(self):
        nome = self.input_nome.text().strip()
        percorso = self.input_percorso.text().strip()
        note = self.input_note.toPlainText().strip()

        if not nome or not percorso:
            QMessageBox.warning(self, "Campi Mancanti", "Inserisci sia il nome che il percorso del progetto!")
            return

        if not os.path.exists(percorso):
            QMessageBox.warning(self, "Percorso Errato", "Il percorso inserito non esiste sul disco!")
            return

        self.controller.salva_csv(nome, percorso, note)
        self.percorso_selezionato = percorso
        self.accept()

