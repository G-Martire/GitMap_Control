from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, 
    QPushButton, QMessageBox
)
from PyQt6.QtGui import QFont


class DialogSalvaVersione(QDialog):
    """Finestra pop-up per l'inserimento delle note di sviluppo e il commit Git."""
    def __init__(self, parent=None, git_controller=None):
        super().__init__(parent)
        self.i18n = getattr(parent, 'i18n', None)
        self.git_controller = git_controller
        self.setWindowTitle(self.i18n.t("auto_extracted.title_save_git_version"))
        self.resize(450, 320)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.input_roadmap = QLineEdit()
        self.input_roadmap.setPlaceholderText(self.i18n.t("auto_extracted.placeholder_refactor_hotkey"))
        form_layout.addRow(self.i18n.t("auto_extracted.label_roadmap_goal"), self.input_roadmap)

        self.input_argomenti = QLineEdit()
        self.input_argomenti.setPlaceholderText(self.i18n.t("auto_extracted.placeholder_bug_fix_example"))
        form_layout.addRow(self.i18n.t("auto_extracted.label_topics_details"), self.input_argomenti)

        self.input_note = QTextEdit()
        self.input_note.setPlaceholderText(self.i18n.t("auto_extracted.placeholder_extra_notes"))
        self.input_note.setMaximumHeight(80)
        form_layout.addRow(self.i18n.t("auto_extracted.label_optional_notes"), self.input_note)

        layout.addLayout(form_layout)

        btn_conferma = QPushButton(self.i18n.t("auto_extracted.btn_commit_register_version"))
        btn_conferma.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        btn_conferma.setStyleSheet("background-color: #2563EB; color: white; padding: 8px; border-radius: 4px;")
        btn_conferma.clicked.connect(self._conferma_click)
        layout.addWidget(btn_conferma)

    def _conferma_click(self):
        roadmap = self.input_roadmap.text().strip()
        argomenti = self.input_argomenti.text().strip()
        note = self.input_note.toPlainText().strip()

        if not roadmap:
            QMessageBox.warning(self, self.i18n.t("auto_extracted.msg_required_field"), "Inserisci almeno l'obiettivo della Roadmap!")
            return

        if self.git_controller:
            successo, msg = self.git_controller.esegui_commit(roadmap, argomenti, note)
            if successo:
                QMessageBox.information(self, self.i18n.t("auto_extracted.msg_commit_completed"), msg)
                self.accept()
            else:
                QMessageBox.critical(self, self.i18n.t("auto_extracted.msg_git_error"), msg)
        else:
            self.accept()

