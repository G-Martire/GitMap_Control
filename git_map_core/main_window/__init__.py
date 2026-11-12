import os
import ctypes
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QSplitter, QGraphicsScene, QApplication, QLabel, QLineEdit
)
from PyQt6.QtGui import QTransform, QIcon, QFont
from PyQt6.QtCore import Qt

from git_map_core.nodes import NodoMindMap
from git_map_core.views import VistaMappa
from git_map_core.dialogs import ottieni_ultimo_progetto
from git_map_core.git_controller import GitController
from git_map_core.search_export_controller import SearchExportController
from git_map_core.i18n import LanguageManager

from gestione_i18n.sidebar_i18n import SidebarProcessiI18N

# Importazione dei moduli figli a composizione
from .sidebar_filtri import SidebarFiltri
from .menu import MenuController
from .map import MapController
from .git_history import GitHistoryController
from .theme import ThemeController
from .i18n import I18NController

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..', '..')) if os.path.basename(BASE_DIR) == 'main_window' else BASE_DIR

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('padas.devstudio.mappasistema.2.0')
except Exception:
    pass

class MappaSistemaWindow(QMainWindow):
    """Dashboard di navigazione interattiva a forma di Mappa Mentale (Architettura a Composizione)."""
    def __init__(self, root_dir=None):
        super().__init__()
        self.i18n = LanguageManager()

        ultimo_progetto = ottieni_ultimo_progetto()
        if root_dir is None or not os.path.exists(root_dir):
            self.root_dir = ultimo_progetto if (ultimo_progetto and os.path.exists(ultimo_progetto)) else PROJECT_ROOT
        else:
            self.root_dir = root_dir

        self.project_root = self.root_dir

        # Inizializzazione Controller tramite Composizione
        self.git_ctrl = GitController(self)
        self.search_export_controller = SearchExportController(self)
        
        self.map_ctrl = MapController(self)
        self.menu_ctrl = MenuController(self)
        self.git_history_ctrl = GitHistoryController(self)
        self.theme_ctrl = ThemeController(self)
        self.i18n_ctrl = I18NController(self)

        self.theme_ctrl.carica_e_applica_tema_iniziale()

        self.setWindowTitle(self.i18n.t("window.title"))
        self.resize(1280, 750)
        if not (icon := QIcon.fromTheme("folder-open")).isNull():
            self.setWindowIcon(icon)

        self._costruisci_interfaccia()
        self.map_ctrl.inizializza_nodo_radice()

    def _costruisci_interfaccia(self):
        widget_centrale = QWidget()
        layout_principale = QVBoxLayout(widget_centrale)

        header_layout = QHBoxLayout()
        lbl_titolo = QLabel(self.i18n.t("auto_extracted.arch_git_map"))
        lbl_titolo.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        header_layout.addWidget(lbl_titolo)
        header_layout.addStretch()

        # Costruzione dei menu tramite controller dedicato
        self.menu_ctrl.crea_menu_progetto(header_layout)
        self.menu_ctrl.crea_menu_git(header_layout)
        self.menu_ctrl.crea_menu_opzioni(header_layout)

        # Pulsante Toggle Sidebar Filtri
        btn_sidebar = QPushButton(self.i18n.t("toolbar.filtri"))
        btn_sidebar.setToolTip(self.i18n.t("toolbar.filtri_tooltip"))
        btn_sidebar.clicked.connect(self.map_ctrl.toggle_sidebar)
        header_layout.addWidget(btn_sidebar)
        header_layout.addSpacing(15)

        # Ricerca e Reset
        self.input_cerca = QLineEdit()
        self.input_cerca.setPlaceholderText(self.i18n.t("toolbar.placeholder_cerca"))
        self.input_cerca.setFixedWidth(180)
        self.input_cerca.returnPressed.connect(self.map_ctrl.esegui_ricerca)
        header_layout.addWidget(self.input_cerca)

        for text_key, slot in [
            (self.i18n.t("toolbar.cerca"), self.map_ctrl.esegui_ricerca), 
            (self.i18n.t("toolbar.reset_vista"), self.map_ctrl.reset_vista)
        ]:
            btn = QPushButton(text_key)
            btn.clicked.connect(slot)
            header_layout.addWidget(btn)

        layout_principale.addLayout(header_layout)

        # Splitter Principale
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.sidebar_i18n = SidebarProcessiI18N(self)
        self.splitter.addWidget(self.sidebar_i18n)
        self.sidebar_i18n.setVisible(False)

        self.scene = QGraphicsScene()
        self.view = VistaMappa(self.scene, self)
        self.splitter.addWidget(self.view)

        self.sidebar = SidebarFiltri(self)
        self.splitter.addWidget(self.sidebar)
        self.sidebar.setVisible(False)

        layout_principale.addWidget(self.splitter)
        self.setCentralWidget(widget_centrale)