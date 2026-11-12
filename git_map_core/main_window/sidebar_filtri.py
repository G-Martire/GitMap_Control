from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGroupBox, QCheckBox, QRadioButton, QListWidget, QListWidgetItem, QPushButton, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class SidebarFiltri(QFrame):
    """Pannello laterale a scomparsa per i Filtri e la Cronologia dei Commit Git."""
    def __init__(self, parent_window):
        super().__init__()
        self.main_win = parent_window
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedWidth(280)
        self.setStyleSheet("background-color: #F8FAFC; border-left: 1px solid #CBD5E1;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Header Sidebar
        lbl_titolo = QLabel(self.main_win.i18n.t("auto_extracted.filters_git_history"))
        lbl_titolo.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(lbl_titolo)

        # Gruppo 1: Filtro Colori / Stati Git
        group_stati = QGroupBox(self.main_win.i18n.t("auto_extracted.git_status_display"))
        layout_stati = QVBoxLayout(group_stati)

        self.chk_modificati = QCheckBox(self.main_win.i18n.t("auto_extracted.status_modified"))
        self.chk_modificati.setChecked(True)
        self.chk_modificati.stateChanged.connect(self._notifica_cambio_filtri)
        layout_stati.addWidget(self.chk_modificati)

        self.chk_nuovi = QCheckBox(self.main_win.i18n.t("auto_extracted.status_new_uncommitted"))
        self.chk_nuovi.setChecked(True)
        self.chk_nuovi.stateChanged.connect(self._notifica_cambio_filtri)
        layout_stati.addWidget(self.chk_nuovi)

        self.chk_invariati = QCheckBox(self.main_win.i18n.t("auto_extracted.status_unchanged_neutral"))
        self.chk_invariati.setChecked(True)
        self.chk_invariati.stateChanged.connect(self._notifica_cambio_filtri)
        layout_stati.addWidget(self.chk_invariati)

        layout.addWidget(group_stati)

        # Gruppo 2: Modalità per Nodi Esclusi
        group_modo = QGroupBox(self.main_win.i18n.t("auto_extracted.filter_excluded_nodes"))
        layout_modo = QVBoxLayout(group_modo)

        self.radio_opacizza = QRadioButton(self.main_win.i18n.t("auto_extracted.filter_opacity_semi"))
        self.radio_opacizza.setChecked(True)
        self.radio_opacizza.toggled.connect(self._notifica_cambio_filtri)
        layout_modo.addWidget(self.radio_opacizza)

        self.radio_nascondi = QRadioButton(self.main_win.i18n.t("auto_extracted.filter_hide_completely"))
        self.radio_nascondi.toggled.connect(self._notifica_cambio_filtri)
        layout_modo.addWidget(self.radio_nascondi)

        layout.addWidget(group_modo)

        # Gruppo 3: Cronologia Commit Salvati (CSV)
        group_history = QGroupBox(self.main_win.i18n.t("auto_extracted.git_history_csv"))
        layout_history = QVBoxLayout(group_history)

        self.lista_commit = QListWidget()
        self.lista_commit.setStyleSheet("font-size: 11px;")
        self.lista_commit.itemClicked.connect(self._seleziona_commit_click)
        self.lista_commit.itemDoubleClicked.connect(self._mostra_dettagli_commit)
        layout_history.addWidget(self.lista_commit)

        btn_refresh_history = QPushButton(self.main_win.i18n.t("auto_extracted.btn_refresh_history"))
        btn_refresh_history.clicked.connect(self.carica_cronologia_commit)
        layout_history.addWidget(btn_refresh_history)

        layout.addWidget(group_history)

        # Pulsanti d'Azione
        btn_reset_filtri = QPushButton(self.main_win.i18n.t("auto_extracted.btn_reset_all_nodes"))
        btn_reset_filtri.clicked.connect(self._reset_filtri_click)
        layout.addWidget(btn_reset_filtri)

        self.carica_cronologia_commit()

    def carica_cronologia_commit(self):
        """Popola la lista con le versioni salvate nel registro CSV del progetto."""
        self.lista_commit.clear()
        cronologia = self.main_win.git_ctrl.ottieni_cronologia_commit()
        if not cronologia:
            self.lista_commit.addItem(QListWidgetItem(self.main_win.i18n.t("auto_extracted.msg_no_saved_commits")))
            return

        for item in cronologia:
            testo = f"[{item['tag_git']}] {item['roadmap']}\n📅 {item['data']} | 📄 {item['file']}"
            list_item = QListWidgetItem(testo)
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.lista_commit.addItem(list_item)

    def _mostra_dettagli_commit(self, list_item):
        """Apre una finestra pop-up con i dettagli completi della versione selezionata."""
        dati = list_item.data(Qt.ItemDataRole.UserRole)
        if not dati or not isinstance(dati, dict):
            return

        msg = (
            f"<b>Tag Git:</b> {dati.get('tag_git')}<br>"
            f"<b>Data e Ora:</b> {dati.get('data')}<br>"
            f"<b>Roadmap / Obiettivo:</b> {dati.get('roadmap')}<br><br>"
            f"<b>File Modificati:</b><br>{dati.get('file')}<br><br>"
            f"<b>Argomenti / Dettagli:</b><br>{dati.get('argomenti')}<br><br>"
            f"<b>Note:</b><br>{dati.get('note')}"
        )
        QMessageBox.information(self.main_win, f"Dettagli {dati.get('tag_git')}", msg)

    def _notifica_cambio_filtri(self):
        self.main_win.map_ctrl.applica_filtri_sidebar()

    def _reset_filtri_click(self):
        self.chk_modificati.setChecked(True)
        self.chk_nuovi.setChecked(True)
        self.chk_invariati.setChecked(True)
        self.radio_opacizza.setChecked(True)
        self.main_win.map_ctrl.applica_filtri_sidebar()

    def ottieni_impostazioni_filtro(self):
        return {
            'mostra_M': self.chk_modificati.isChecked(),
            'mostra_NEW': self.chk_nuovi.isChecked(),
            'mostra_CLEAN': self.chk_invariati.isChecked(),
            'modalita_nascondi': self.radio_nascondi.isChecked()
        }

    def _seleziona_commit_click(self, list_item):
        """Quando si clicca un commit nella lista, aggiorna visivamente la mappa con le modifiche di quel commit."""
        dati = list_item.data(Qt.ItemDataRole.UserRole)
        if dati and isinstance(dati, dict):
            self.main_win.git_history_ctrl.visualizza_commit_passato(dati)