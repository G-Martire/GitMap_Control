from PyQt6.QtWidgets import QPushButton, QMenu, QWidget, QVBoxLayout, QLineEdit, QWidgetAction

class MenuController:
    """Gestisce la creazione e il popolamento dei menu a tendina superiori della finestra principale."""
    def __init__(self, manager):
        self.manager = manager  # Riferimento al manager principale

    def crea_menu_progetto(self, header_layout):
        """Crea il menu a tendina per la gestione del progetto e l'esportazione."""
        btn_menu_progetto = QPushButton(self.manager.i18n.t("menu_progetto.titolo"))
        btn_menu_progetto.setToolTip(self.manager.i18n.t("menu_progetto.tooltip"))
        menu_progetto = QMenu(self.manager)
        
        action_cambia = menu_progetto.addAction(self.manager.i18n.t("menu_progetto.cambia"))
        action_cambia.triggered.connect(self.manager.map_ctrl.apri_dialog_progetti)
        
        menu_progetto.addSeparator()
        
        action_albero = menu_progetto.addAction(self.manager.i18n.t("menu_progetto.copia_albero"))
        action_albero.triggered.connect(lambda: self.manager.search_export_controller.copia_albero_appunti(self.manager))

        action_json = menu_progetto.addAction(self.manager.i18n.t("menu_progetto.esporta_json"))
        action_json.triggered.connect(lambda: self.manager.search_export_controller.esporta_json_dettagliato(self.manager))
        
        menu_progetto.addSeparator()
        
        action_traduci = menu_progetto.addAction(self.manager.i18n.t("auto_extracted.menu_translate_ui"))
        action_traduci.triggered.connect(self.manager.i18n_ctrl.avvia_traduzione_interfaccia)
        
        btn_menu_progetto.setMenu(menu_progetto)
        header_layout.addWidget(btn_menu_progetto)
        header_layout.addSpacing(10)

    def crea_menu_git(self, header_layout):
        """Crea il menu a tendina per i comandi Git e la sincronizzazione."""
        btn_menu_git = QPushButton(self.manager.i18n.t("menu_git.titolo"))
        btn_menu_git.setToolTip(self.manager.i18n.t("menu_git.tooltip"))
        menu_git = QMenu(self.manager)
        
        action_stato = menu_git.addAction(self.manager.i18n.t("menu_git.stato_git"))
        action_stato.triggered.connect(self.manager.git_history_ctrl.evidenzia_modifiche_git)
        
        action_salva = menu_git.addAction(self.manager.i18n.t("menu_git.salva_versione"))
        action_salva.triggered.connect(self.manager.git_history_ctrl.apri_dialog_salva_versione)
        
        menu_git.addSeparator()
        
        action_usb = menu_git.addAction(self.manager.i18n.t("menu_git.sync_usb"))
        action_usb.triggered.connect(self.manager.git_history_ctrl.apri_dialog_usb)
        
        btn_menu_git.setMenu(menu_git)
        header_layout.addWidget(btn_menu_git)
        header_layout.addSpacing(10)

    def crea_menu_opzioni(self, header_layout):
        """Crea il menu a tendina per le opzioni, i temi e le lingue."""
        btn_menu_opzioni = QPushButton(self.manager.i18n.t("menu_opzioni.titolo"))
        btn_menu_opzioni.setToolTip(self.manager.i18n.t("menu_opzioni.tooltip"))
        menu_opzioni = QMenu(self.manager)

        self.manager.i18n_ctrl.crea_menu_lingue(menu_opzioni)
        self.manager.theme_ctrl.crea_menu_colori(menu_opzioni)

        btn_menu_opzioni.setMenu(menu_opzioni)
        header_layout.addWidget(btn_menu_opzioni)
        header_layout.addSpacing(10)