from PyQt6.QtWidgets import QMenu, QWidget, QVBoxLayout, QLineEdit, QWidgetAction, QMessageBox
from gestione_i18n.dialog_i18n import DialogConfigurazioneI18N
from gestione_i18n.worker_i18n import WorkerPipelineI18N

class I18NController:
    """Gestisce la selezione dinamica delle lingue con ricerca e la pipeline asincrona i18n."""
    def __init__(self, manager):
        self.manager = manager  # Riferimento al manager principale

    def crea_menu_lingue(self, parent_menu):
        """Crea un sottomenu con barra di ricerca per la selezione dinamica della lingua."""
        sub_menu = QMenu(self.manager.i18n.t("menu_opzioni.lingua"), self.manager)
        
        search_widget = QWidget(sub_menu)
        search_layout = QVBoxLayout(search_widget)
        search_layout.setContentsMargins(6, 4, 6, 4)
        
        self.manager.input_cerca_lingua = QLineEdit(search_widget)
        self.manager.input_cerca_lingua.setPlaceholderText(self.manager.i18n.t("auto_extracted.search_language"))
        search_layout.addWidget(self.manager.input_cerca_lingua)
        
        search_action = QWidgetAction(sub_menu)
        search_action.setDefaultWidget(search_widget)
        sub_menu.addAction(search_action)
        sub_menu.addSeparator()
        
        self.lingua_actions = {}
        lingue_disponibili = self.manager.i18n.ottieni_lingue_disponibili()
        
        for code, info in lingue_disponibili.items():
            native = info.get("native_name", code)
            english = info.get("english_name", code)
            label = f"{native} ({english})"
            
            action = sub_menu.addAction(label)
            action.setData(code)
            action.triggered.connect(lambda checked, c=code: self._cambia_lingua(c))
            
            self.lingua_actions[code] = {
                "action": action,
                "search_terms": f"{native} {english} {code}".lower()
            }
            
        self.manager.input_cerca_lingua.textChanged.connect(self._filtra_lingue)
        parent_menu.addMenu(sub_menu)

    def _filtra_lingue(self, text):
        """Filtra le voci delle lingue nel menu in base al testo digitato."""
        query = text.strip().lower()
        for code, data in self.lingua_actions.items():
            match = query in data["search_terms"]
            data["action"].setVisible(match)

    def _cambia_lingua(self, code):
        """Imposta la nuova lingua, salva la configurazione e ricarica la finestra."""
        from . import MappaSistemaWindow
        self.manager.i18n.carica_lingua(code)
        self.manager.close()
        self.manager.nuova_finestra = MappaSistemaWindow(self.manager.root_dir)
        self.manager.nuova_finestra.show()

    def avvia_traduzione_interfaccia(self):
        """Apre il dialog di configurazione e avvia la pipeline asincrona i18n con accordion."""
        dlg = DialogConfigurazioneI18N(self.manager, self.manager.root_dir)
        if dlg.exec():
            config = dlg.ottieni_configurazione()
            
            self.manager.sidebar.setVisible(False)
            self.manager.sidebar_i18n.setVisible(True)
            self.manager.sidebar_i18n.imposta_stato_attivo(True)
            self.manager.sidebar_i18n.aggiungi_log("🚀 Inizializzazione pipeline i18n...")

            self.manager.worker_i18n = WorkerPipelineI18N(config)
            self.manager.worker_i18n.log_signal.connect(self.manager.sidebar_i18n.aggiungi_dettaglio)
            self.manager.worker_i18n.step_status_signal.connect(self.manager.sidebar_i18n.aggiorna_stato_step)
            self.manager.worker_i18n.progress_signal.connect(self.manager.sidebar_i18n.progress_bar.setValue)
            self.manager.worker_i18n.finished_signal.connect(self._pipeline_i18n_completata)
            self.manager.worker_i18n.start()

    def ferma_pipeline_i18n(self):
        """Interrompe il worker in esecuzione (Kill-Switch d'emergenza)."""
        if hasattr(self.manager, 'worker_i18n') and self.manager.worker_i18n.isRunning():
            self.manager.worker_i18n.stop()

    def _pipeline_i18n_completata(self, successo, messaggio):
        """Gestisce il termine della pipeline i18n."""
        self.manager.sidebar_i18n.imposta_stato_attivo(False)
        if successo:
            self.manager.sidebar_i18n.aggiungi_log(f"\n✨ {messaggio}")
            QMessageBox.information(self.manager, "Pipeline i18n", messaggio)
        else:
            self.manager.sidebar_i18n.aggiungi_log(f"\n❌ {messaggio}")
            QMessageBox.warning(self.manager, "Errore Pipeline i18n", messaggio)