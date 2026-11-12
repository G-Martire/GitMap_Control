import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QCheckBox, QHBoxLayout, QLineEdit, QPushButton, QComboBox, QSpinBox

class PagesIntroSteps:
    """Gestisce la costruzione delle pagine di Intro, Step 1.1 e Step 2 del wizard i18n."""
    def __init__(self, dialog):
        self.dialog = dialog  # Riferimento al Dialog principale

    def costruisci_pagina_intro(self):
        """Scheda 1: Introduzione e spiegazione delle funzionalità della pipeline."""
        pag = QWidget()
        layout = QVBoxLayout(pag)
        group = QGroupBox(self.dialog.i18n.t("auto_extracted.guide_i18n_pipeline"))
        vbox = QVBoxLayout(group)
        
        lbl_intro = QLabel(self.dialog.i18n.t("intro_full_description"))
        lbl_intro.setWordWrap(True)
        lbl_intro.setStyleSheet("color: #334155; font-size: 12px; line-height: 1.5;")
        vbox.addWidget(lbl_intro)
        vbox.addStretch()
        layout.addWidget(group)
        return pag

    def costruisci_pagina_step1_1(self):
        """Scheda 2: Step 1.1 (Scansione Codice & CSV)."""
        pag = QWidget()
        layout = QVBoxLayout(pag)
        group = QGroupBox(self.dialog.i18n.t("step_1_1_scan_title"))
        vbox = QVBoxLayout(group)
        
        self.dialog.chk_step1_1 = QCheckBox(self.dialog.i18n.t("step_1_1_enable_label"))
        self.dialog.chk_step1_1.setChecked(True)
        vbox.addWidget(self.dialog.chk_step1_1)

        h_proj = QHBoxLayout()
        h_proj.addWidget(QLabel(self.dialog.i18n.t("label_project_folder")))
        self.dialog.input_cartella_progetto = QLineEdit(self.dialog.progetto_root)
        h_proj.addWidget(self.dialog.input_cartella_progetto)
        btn_sfoglia_proj = QPushButton(self.dialog.i18n.t("btn_browse"))
        btn_sfoglia_proj.clicked.connect(self.dialog.config_ctrl.sfoglia_progetto)
        h_proj.addWidget(btn_sfoglia_proj)
        vbox.addLayout(h_proj)

        h_loc = QHBoxLayout()
        h_loc.addWidget(QLabel(self.dialog.i18n.t("label_locales_folder")))
        self.dialog.input_cartella_locales = QLineEdit(os.path.join(self.dialog.progetto_root, "locales"))
        h_loc.addWidget(self.dialog.input_cartella_locales)
        btn_sfoglia_loc = QPushButton(self.dialog.i18n.t("btn_browse"))
        btn_sfoglia_loc.clicked.connect(self.dialog.config_ctrl.sfoglia_locales)
        h_loc.addWidget(btn_sfoglia_loc)
        vbox.addLayout(h_loc)

        vbox.addStretch()
        layout.addWidget(group)
        return pag

    def costruisci_pagina_step2(self):
        """Scheda 3: Step 2 (Classificazione IA)."""
        pag = QWidget()
        layout = QVBoxLayout(pag)
        group = QGroupBox(self.dialog.i18n.t("auto_extracted.step_2_classification_params"))
        vbox = QVBoxLayout(group)
        
        self.dialog.chk_step2 = QCheckBox(self.dialog.i18n.t("auto_extracted.enable_step_2"))
        self.dialog.chk_step2.setChecked(True)
        vbox.addWidget(self.dialog.chk_step2)

        h_modello = QHBoxLayout()
        h_modello.addWidget(QLabel(self.dialog.i18n.t("auto_extracted.model_gemini_classification_short")))
        self.dialog.combo_modelli_step2 = QComboBox()
        self.dialog.combo_modelli_step2.addItems([
            "models/gemini-3.1-flash-lite",
            "models/gemini-3.5-flash",
            "models/gemini-3.7-flash",
            "models/gemini-2.5-flash"
        ])
        h_modello.addWidget(self.dialog.combo_modelli_step2)
        vbox.addLayout(h_modello)

        h_batch = QHBoxLayout()
        h_batch.addWidget(QLabel(self.dialog.i18n.t("label_batch_size")))
        self.dialog.spin_batch_step2 = QSpinBox()
        self.dialog.spin_batch_step2.setRange(10, 200)
        self.dialog.spin_batch_step2.setValue(50)
        h_batch.addWidget(self.dialog.spin_batch_step2)
        vbox.addLayout(h_batch)

        vbox.addStretch()
        layout.addWidget(group)
        return pag

