import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QStackedWidget
)

from .intro import PagesIntroSteps
from .code_json import PagesCodeJson
from .multilang import PagesMultilang
from .summary import PagesSummary
from .config import I18NConfigController

class DialogConfigurazioneI18N(QDialog):
    """Finestra di dialogo per la configurazione dei parametri della pipeline i18n (Composizione)."""
    def __init__(self, parent_window, progetto_root):
        super().__init__(parent_window)
        self.parent_win = parent_window
        self.i18n = parent_window.i18n
        self.progetto_root = progetto_root
        
        self.setWindowTitle(self.i18n.t("auto_extracted.title_pipeline_config"))
        self.resize(850, 680)

        # Inizializzazione Controller e Moduli tramite Composizione
        self.config_ctrl = I18NConfigController(self)
        self.intro_steps_page = PagesIntroSteps(self)
        self.code_json_page = PagesCodeJson(self)
        self.multilang_page = PagesMultilang(self)
        self.summary_page = PagesSummary(self)

        layout_radice = QVBoxLayout(self)
        layout_radice.setContentsMargins(14, 14, 14, 14)
        layout_radice.setSpacing(12)

        h_layout_corpo = QHBoxLayout()
        h_layout_corpo.setSpacing(14)

        # Barra laterale di navigazione
        self.lista_navigazione = QListWidget()
        self.lista_navigazione.setFixedWidth(240)
        
        voci_navigazione = [
            self.i18n.t("nav_intro"),
            self.i18n.t("nav_step_1_1"),
            self.i18n.t("nav_step_2"),
            self.i18n.t("nav_step_3_1"),
            self.i18n.t("nav_step_3_2"),
            self.i18n.t("nav_step_4"),
            self.i18n.t("nav_summary")
        ]
        
        for voce in voci_navigazione:
            self.lista_navigazione.addItem(QListWidgetItem(voce))

        h_layout_corpo.addWidget(self.lista_navigazione)

        # Contenitore a pagine (QStackedWidget)
        self.stack_pagine = QStackedWidget()
        
        self.pag_intro = self.intro_steps_page.costruisci_pagina_intro()
        self.pag_step1_1 = self.intro_steps_page.costruisci_pagina_step1_1()
        self.pag_step2 = self.intro_steps_page.costruisci_pagina_step2()
        self.pag_step3_1 = self.code_json_page.costruisci_pagina_step3_1()
        self.pag_step3_2 = self.code_json_page.costruisci_pagina_step3_2()
        self.pag_step4 = self.multilang_page.costruisci_pagina_step4()
        self.pag_riepilogo = self.summary_page.costruisci_pagina_riepilogo()

        for pag in [self.pag_intro, self.pag_step1_1, self.pag_step2, self.pag_step3_1, self.pag_step3_2, self.pag_step4, self.pag_riepilogo]:
            self.stack_pagine.addWidget(pag)

        h_layout_corpo.addWidget(self.stack_pagine)
        layout_radice.addLayout(h_layout_corpo)

        self.lista_navigazione.currentRowChanged.connect(self.stack_pagine.setCurrentIndex)
        self.lista_navigazione.setCurrentRow(0)

        # Barra dei pulsanti in basso
        h_btn = QHBoxLayout()
        self.btn_indietro = QPushButton(self.i18n.t("auto_extracted.btn_back"))
        self.btn_avanti = QPushButton(self.i18n.t("auto_extracted.btn_forward"))
        self.btn_avvia = QPushButton(self.i18n.t("auto_extracted.btn_start_pipeline"))
        btn_annulla = QPushButton(self.i18n.t("auto_extracted.btn_cancel"))

        self.btn_indietro.clicked.connect(self.config_ctrl.pagina_precedente)
        self.btn_avanti.clicked.connect(self.config_ctrl.pagina_successiva)
        self.btn_avvia.clicked.connect(self.accept)
        btn_annulla.clicked.connect(self.reject)

        h_btn.addWidget(self.btn_indietro)
        h_btn.addWidget(self.btn_avanti)
        h_btn.addStretch()
        h_btn.addWidget(btn_annulla)
        h_btn.addWidget(self.btn_avvia)

        layout_radice.addLayout(h_btn)
        self.stack_pagine.currentChanged.connect(self.config_ctrl.aggiorna_stato_pulsanti_navigazione)
        self.config_ctrl.aggiorna_stato_pulsanti_navigazione(0)

    def ottieni_configurazione(self):
        return self.config_ctrl.ottieni_configurazione()

