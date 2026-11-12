import os
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QProgressBar, QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QColor, QBrush, QFont, QDesktopServices


class SidebarProcessiI18N(QFrame):
    """Pannello laterale per il monitoraggio a fisarmonica (accordion) della pipeline i18n."""
    def __init__(self, parent_window):
        super().__init__()
        self.main_win = parent_window
        self.i18n = parent_window.i18n  # Riferimento al gestore lingua
        
        self.setFixedWidth(340)
        self.setStyleSheet("background-color: #F8FAFC; border-right: 1px solid #CBD5E1;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Header Sidebar
        lbl_titolo = QLabel(self.i18n.t("auto_extracted.title_pipeline_monitor"))
        lbl_titolo.setStyleSheet("font-weight: bold; font-size: 13px; color: #1E293B;")
        layout.addWidget(lbl_titolo)

        # Barra di progresso generale
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                text-align: center;
                font-size: 10px;
                font-weight: bold;
                height: 16px;
            }
            QProgressBar::chunk {
                background-color: #2563EB;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Albero ad Accordion/Fisarmonica per gli Step
        self.tree_step = QTreeWidget()
        self.tree_step.setHeaderHidden(True)
        self.tree_step.setAnimated(True)
        self.tree_step.setIndentation(15)
        self.tree_step.setStyleSheet("""
            QTreeWidget {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                font-family: Consolas, "Segoe UI";
                font-size: 11px;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:hover {
                background-color: #F1F5F9;
            }
        """)
        self.tree_step.itemDoubleClicked.connect(self._apri_file_selezionato)
        layout.addWidget(self.tree_step)

        # Pulsante Kill-Switch d'emergenza
        self.btn_interrompi = QPushButton(self.i18n.t("auto_extracted.btn_stop_process"))
        self.btn_interrompi.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
        self.btn_interrompi.setEnabled(False)
        self.btn_interrompi.clicked.connect(self._richiedi_interruzione)
        layout.addWidget(self.btn_interrompi)

        self.step_items = {}

    def imposta_stato_attivo(self, attivo: bool):
        """Prepara l'interfaccia per un nuovo ciclo di esecuzione."""
        self.btn_interrompi.setEnabled(attivo)
        if attivo:
            self.tree_step.clear()
            self.step_items.clear()
            self.progress_bar.setValue(0)
            self._inizializza_struttura_step()

    def _inizializza_struttura_step(self):
        """Crea le Intestazioni di base espandibili per ciascun Step."""
        definiti = [
            (0, "header", self.i18n.t("sidebar_init_params")),
            (1, "step1", self.i18n.t("sidebar_step1_scan")),
            (2, "step2", self.i18n.t("sidebar_step2_ai")),
            (3, "step3", self.i18n.t("sidebar_steps_3_4"))
        ]
        
        for idx, key, titolo in definiti:
            item = QTreeWidgetItem(self.tree_step)
            item.setText(0, f"⏳ {titolo}")
            item.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
            item.setForeground(0, QBrush(QColor("#475569")))
            item.setExpanded(False)
            self.step_items[key] = item

    def aggiorna_stato_step(self, step_key: str, nuovo_titolo: str, completato: bool = False, espandi: bool = True):
        """Aggiorna l'intestazione dello step e gestisce l'apertura/chiusura automatica."""
        if step_key in self.step_items:
            item = self.step_items[step_key]
            prefisso = "✅ " if completato else "⏳ "
            item.setText(0, f"{prefisso}{nuovo_titolo}")
            if completato:
                item.setForeground(0, QBrush(QColor("#16A34A")))
            else:
                item.setForeground(0, QBrush(QColor("#2563EB")))
            
            if espandi:
                item.setExpanded(True)

    def aggiungi_dettaglio(self, testo: str, step_key: str = "header"):
        """Inserisce una riga di log specifica all'interno dello step di pertinenza e gestisce i path."""
        parent_item = self.step_items.get(step_key)
        if not parent_item:
            parent_item = self.step_items.get("header")
            
        child = QTreeWidgetItem(parent_item)
        child.setText(0, testo)
        child.setFont(0, QFont("Consolas", 8))
        child.setForeground(0, QBrush(QColor("#334155")))
        
        # Estrazione sicura del percorso (file o cartella)
        percorso_target = None
        import os
        
        if "Percorso:" in testo:
            # Estrae il percorso assoluto dopo la chiave "Percorso:"
            parte_path = testo.split("Percorso:", 1)[1].strip()
            if os.path.exists(parte_path):
                percorso_target = parte_path
        elif "CSV:" in testo or "Codice aggiornato:" in testo:
            # Estrae i percorsi relativi
            parte_path = testo.split(":", 1)[1].strip().split()[0]
            if hasattr(self.main_win, 'project_root'):
                ass_path = os.path.join(self.main_win.project_root, parte_path)
                if os.path.exists(ass_path):
                    percorso_target = ass_path

        if percorso_target:
            child.setData(0, Qt.ItemDataRole.UserRole, percorso_target)
            child.setForeground(0, QBrush(QColor("#1D4ED8")))  # Blu interattivo

        self.tree_step.scrollToItem(child)

    def _apri_file_selezionato(self, item, column):
        """Apre il file associato al nodo con il programma predefinito del sistema."""
        percorso = item.data(column, Qt.ItemDataRole.UserRole)
        if percorso and os.path.exists(percorso):
            QDesktopServices.openUrl(QUrl.fromLocalFile(percorso))

    def aggiungi_log(self, testo: str):
        """Metodo di compatibilità legacy."""
        self.aggiungi_dettaglio(testo, "header")

    def _richiedi_interruzione(self):
        """Gestisce il kill-switch d'emergenza."""
        self.btn_interrompi.setEnabled(False)
        self.aggiungi_dettaglio(self.i18n.t("sidebar_user_abort"), "step2")
        if hasattr(self.main_win, 'ferma_pipeline_i18n'):
            self.main_win.ferma_pipeline_i18n()

