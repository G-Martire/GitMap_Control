from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QCheckBox, QHBoxLayout, QComboBox

class PagesCodeJson:
    """Gestisce la costruzione delle pagine per Step 3.1 (JSON principale) e Step 3.2 (Sostituzioni nel Codice)."""
    def __init__(self, dialog):
        self.dialog = dialog  # Riferimento al Dialog principale

    def costruisci_pagina_step3_1(self):
        """Scheda 4: Step 3.1 (Aggiornamento JSON principale)."""
        pag = QWidget()
        layout = QVBoxLayout(pag)
        group = QGroupBox(self.dialog.i18n.t("step_3_1_json_update_title"))
        vbox = QVBoxLayout(group)
        vbox.setSpacing(8)
        
        self.dialog.chk_step3_1 = QCheckBox(self.dialog.i18n.t("step_3_1_enable_label"))
        self.dialog.chk_step3_1.setChecked(True)
        vbox.addWidget(self.dialog.chk_step3_1)

        h_json = QHBoxLayout()
        h_json.addWidget(QLabel(self.dialog.i18n.t("label_main_json_file")))
        self.dialog.combo_json_principale = QComboBox()
        h_json.addWidget(self.dialog.combo_json_principale)
        vbox.addLayout(h_json)

        lbl_info = QLabel(self.dialog.i18n.t("step_3_1_description"))
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet("color: #334155; font-size: 12px;")
        vbox.addWidget(lbl_info)

        vbox.addStretch()
        layout.addWidget(group)
        return pag

    def costruisci_pagina_step3_2(self):
        """Scheda 5: Step 3.2 (Sostituzioni nel Codice Sorgente)."""
        pag = QWidget()
        layout = QVBoxLayout(pag)
        group = QGroupBox(self.dialog.i18n.t("step_3_2_code_replacement_title"))
        vbox = QVBoxLayout(group)
        
        self.dialog.chk_step3_2 = QCheckBox(self.dialog.i18n.t("step_3_2_enable_label"))
        self.dialog.chk_step3_2.setChecked(True)
        vbox.addWidget(self.dialog.chk_step3_2)

        lbl_info = QLabel(self.dialog.i18n.t("step_3_2_description"))
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet("color: #334155; font-size: 12px;")
        vbox.addWidget(lbl_info)

        vbox.addStretch()
        layout.addWidget(group)
        return pag

