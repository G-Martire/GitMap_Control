from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QFileDialog, QRadioButton, QLabel
)


class DialogSincronizzazioneUSB(QDialog):
    """Finestra pop-up per esportare o importare i file su chiavetta USB in modo mirato."""
    def __init__(self, parent=None, git_controller=None):
        super().__init__(parent)
        self.i18n = getattr(parent, 'i18n', None)
        self.git_controller = git_controller
        self.setWindowTitle(self.i18n.t("auto_extracted.title_usb_sync"))
        self.resize(520, 380)

        layout = QVBoxLayout(self)

        # Sezione 1: Esportazione
        layout.addWidget(QLabel(self.i18n.t("auto_extracted.instr_export_usb")))
        
        self.radio_totale = QRadioButton(self.i18n.t("auto_extracted.desc_export_clean"))
        self.radio_totale.setChecked(True)
        layout.addWidget(self.radio_totale)

        self.radio_ultimo = QRadioButton(self.i18n.t("auto_extracted.desc_export_last_commit"))
        layout.addWidget(self.radio_ultimo)

        btn_esporta = QPushButton(self.i18n.t("auto_extracted.btn_select_usb_export"))
        btn_esporta.setStyleSheet("background-color: #2563EB; color: white; padding: 6px; border-radius: 4px;")
        btn_esporta.clicked.connect(self._esegui_esportazione)
        layout.addWidget(btn_esporta)

        layout.addSpacing(20)

        # Sezione 2: Importazione
        layout.addWidget(QLabel(self.i18n.t("auto_extracted.instr_import_usb")))
        layout.addWidget(QLabel(self.i18n.t("auto_extracted.desc_import_warning")))

        btn_importa = QPushButton(self.i18n.t("auto_extracted.btn_select_usb_import"))
        btn_importa.setStyleSheet("background-color: #16A34A; color: white; padding: 6px; border-radius: 4px;")
        btn_importa.clicked.connect(self._esegui_importazione)
        layout.addWidget(btn_importa)

        layout.addSpacing(10)
        btn_chiudi = QPushButton(self.i18n.t("auto_extracted.btn_close"))
        btn_chiudi.clicked.connect(self.accept)
        layout.addWidget(btn_chiudi)

    def _esegui_esportazione(self):
        cartella_dest = QFileDialog.getExistingDirectory(self, "Seleziona la cartella di destinazione (Chiavetta USB)")
        if not cartella_dest:
            return

        modalita = "totale" if self.radio_totale.isChecked() else "ultimo_commit"
        if self.git_controller:
            successo, msg = self.git_controller.esporta_progetto_usb(cartella_dest, modalita)
            if successo:
                QMessageBox.information(self, "Esportazione Riuscita", msg)
                self.accept()
            else:
                QMessageBox.critical(self, "Errore Esportazione", msg)

    def _esegui_importazione(self):
        cartella_src = QFileDialog.getExistingDirectory(self, "Seleziona la cartella di origine (Chiavetta USB)")
        if not cartella_src:
            return

        risposta = QMessageBox.question(
            self,
            "Conferma Importazione",
            "Vuoi sovrascrivere/aggiornare i file del progetto corrente con quelli presenti nella cartella selezionata?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if risposta == QMessageBox.StandardButton.Yes and self.git_controller:
            successo, msg = self.git_controller.importa_progetto_usb(cartella_src)
            if successo:
                QMessageBox.information(self, "Importazione Riuscita", msg)
                self.accept()
            else:
                QMessageBox.critical(self, "Errore Importazione", msg)

