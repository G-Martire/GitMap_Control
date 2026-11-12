from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, 
    QTreeWidgetItem, QHeaderView, QLabel
)
from PyQt6.QtGui import QFont, QColor, QBrush
from PyQt6.QtCore import Qt
from .riepilogo_ctrl import RiepilogoGitController
from .riepilogo_helpers import popola_nodo_ricorsivo, controlla_e_espandi


class DialogRiepilogoStatoGit(QDialog):
    """Finestra pop-up ad albero per mostrare il riepilogo nidificato delle modifiche Git e gestire i macro-moduli (tramite Composizione)."""
    def __init__(self, parent=None, git_controller=None, riepilogo_dati=None):
        super().__init__(parent)
        # Recupera in modo sicuro l'istanza i18n dal parent (main_window)
        self.i18n = getattr(parent, 'i18n', None)
        self.git_controller = git_controller
        self.controller = RiepilogoGitController(self, git_controller, riepilogo_dati)
        self.vista_compressa = True  # Vista compressa predefinita
        self.stato_espanso_modificati = False  # Stato toggle pulsante
        
        if self.i18n:
            self.setWindowTitle(self.i18n.t("auto_extracted.title_git_summary"))
        else:
            self.setWindowTitle(self.i18n.t("auto_extracted.title_git_changes_summary"))
            
        self.resize(780, 520)

        layout = QVBoxLayout(self)

        # Totale globale e Pulsanti superiori
        top_layout = QHBoxLayout()
        totale_modifiche = self.controller.calcola_totale_modifiche()
        
        # Corretto qui: rimosso 'fself' e usata la f-string pulita con self.i18n
        testo_totale = self.i18n.t("summary_resources_total") if self.i18n else "Risorse totali modificate:"
        lbl_info = QLabel(f"{testo_totale} {totale_modifiche}")
        lbl_info.setFont(QFont("Segoe UI", 10))
        top_layout.addWidget(lbl_info)

        top_layout.addStretch()

        self.btn_espandi_modificati = QPushButton(self.i18n.t("auto_extracted.btn_expand_modified") if self.i18n else self.i18n.t("auto_extracted.btn_expand_modified"))
        self.btn_espandi_modificati.setToolTip(self.i18n.t("auto_extracted.desc_expand_modified") if self.i18n else "")
        self.btn_espandi_modificati.clicked.connect(self._toggle_espandi_comprimi_modificati)
        self.btn_espandi_modificati.setVisible(False)  # Visibile solo in vista classica
        top_layout.addWidget(self.btn_espandi_modificati)

        self.btn_toggle_vista = QPushButton(self.i18n.t("auto_extracted.btn_view_compact_mode") if self.i18n else self.i18n.t("auto_extracted.view_compressed"))
        self.btn_toggle_vista.setToolTip(self.i18n.t("auto_extracted.desc_view_mode_toggle") if self.i18n else "")
        self.btn_toggle_vista.clicked.connect(self._toggle_vista)
        top_layout.addWidget(self.btn_toggle_vista)

        layout.addLayout(top_layout)

        # Albero visuale del riepilogo
        self.albero = QTreeWidget()
        self._aggiorna_intestazioni_albero()
        layout.addWidget(self.albero)

        self._popola_albero()

        # Pulsanti d'azione
        box_btn = QHBoxLayout()
        btn_aggiungi = QPushButton(self.i18n.t("auto_extracted.btn_add_macro_module") if self.i18n else self.i18n.t("auto_extracted.btn_add_macro_module"))
        btn_aggiungi.setToolTip(self.i18n.t("auto_extracted.desc_add_macro_module") if self.i18n else "")
        btn_aggiungi.clicked.connect(self._aggiungi_modulo_click)
        box_btn.addWidget(btn_aggiungi)

        box_btn.addStretch()

        btn_chiudi = QPushButton(self.i18n.t("auto_extracted.btn_ok") if self.i18n else "OK")
        btn_chiudi.setFixedWidth(100)
        btn_chiudi.clicked.connect(self.accept)
        box_btn.addWidget(btn_chiudi)

        layout.addLayout(box_btn)

    def _popola_albero(self):
        """Popola l'albero gestendo la vista compressa o la vista classica con la colonna Ultimo Git."""
        self.albero.clear()
        
        if self.vista_compressa:
            for modulo, info in self.controller.riepilogo_dati.items():
                # Chiave tradotta per la pipeline i18n, mappata in modo sicuro sul valore tecnico 'totale'
                chiave_totale_i18n = self.i18n.t("auto_extracted.label_total") if self.i18n else "totale"
                val_totale = info.get(chiave_totale_i18n, info.get('totale', 0))
                
                if val_totale == 0:
                    continue

                nome_display = self.i18n.t("auto_extracted.label_other_files") if modulo == 'altri_file' else f"📁 {modulo}"
                val_cartelle_nuove = str(info['cartelle_nuove']) if info['cartelle_nuove'] > 0 else "-"

                nodo_modulo = QTreeWidgetItem([
                    nome_display,
                    str(info['totale']),
                    str(info['py']),
                    str(info['cache']),
                    str(info['dati']),
                    val_cartelle_nuove
                ])

                for c in range(6):
                    nodo_modulo.setFont(c, QFont("Segoe UI", 9, QFont.Weight.Bold))
                    nodo_modulo.setBackground(c, Qt.GlobalColor.lightGray)
                    nodo_modulo.setForeground(c, Qt.GlobalColor.black)

                for sub_name, sub_info in info['sub'].items():
                    val_sub_cartelle = str(sub_info['cartelle_nuove']) if sub_info['cartelle_nuove'] > 0 else "-"
                    nodo_sub = QTreeWidgetItem([
                        f"   📂 {sub_name}",
                        str(sub_info['totale']),
                        str(sub_info['py']),
                        str(sub_info['cache']),
                        str(sub_info['dati']),
                        val_sub_cartelle
                    ])
                    nodo_modulo.addChild(nodo_sub)

                self.albero.addTopLevelItem(nodo_modulo)
            self.albero.expandAll()
        else:
            self.stato_espanso_modificati = False
            self.btn_espandi_modificati.setText(self.i18n.t("btn_expand_modified") if self.i18n else "Espandi Modificati")

            for modulo, info in self.controller.riepilogo_dati.items():
                totale_modulo_file = len(info['file'])
                if totale_modulo_file == 0:
                    continue

                mod_modulocount = sum(1 for item in info['file'] if (item[1] if len(item) >= 2 else "-") != "-")
                nome_display = "📁 Altri file (Radice / Config)" if modulo == 'altri_file' else f"📁 {modulo}"
                etichetta_mod = f"{nome_display} (Mod: {mod_modulocount})" if mod_modulocount > 0 else f"{nome_display} (Pulito)"
                
                nodo_modulo = QTreeWidgetItem([etichetta_mod, "", ""])
                nodo_modulo.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
                
                for c in range(3):
                    nodo_modulo.setBackground(c, Qt.GlobalColor.lightGray)

                sub_tree = {'dirs': {}, 'files': []}
                for item_data in info['file']:
                    if len(item_data) == 3:
                        file_path, stato, ultimo_git = item_data
                    else:
                        file_path, stato = item_data
                        ultimo_git = "-"

                    if modulo != 'altri_file':
                        rel = file_path[len(modulo)+1:] if file_path.startswith(modulo + "/") else file_path
                    else:
                        rel = file_path
                    
                    parti = rel.split('/')
                    curr = sub_tree
                    for i in range(len(parti) - 1):
                        dname = parti[i]
                        if dname not in curr['dirs']:
                            curr['dirs'][dname] = {'dirs': {}, 'files': []}
                        curr = curr['dirs'][dname]
                    curr['files'].append((parti[-1], file_path, stato, ultimo_git))

                popola_nodo_ricorsivo(nodo_modulo, sub_tree)
                self.albero.addTopLevelItem(nodo_modulo)
            
            self.albero.collapseAll()

    def _aggiungi_modulo_click(self):
        """Richiama il controller per aggiungere un macro-modulo."""
        if self.controller.aggiungi_macro_modulo():
            self.accept()

    def _aggiorna_intestazioni_albero(self):
        """Configura le colonne dell'albero in base alla modalità di visualizzazione attiva."""
        if self.vista_compressa:
            self.albero.setColumnCount(6)
            self.albero.setHeaderLabels([
                self.i18n.t("auto_extracted.header_module_subdir"), self.i18n.t("auto_extracted.header_total"), ".py", self.i18n.t("auto_extracted.header_cache"), self.i18n.t("auto_extracted.header_data_config"), self.i18n.t("auto_extracted.header_new_folders")
            ])
            header = self.albero.header()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            for col in range(1, 6):
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
                self.albero.setColumnWidth(col, 95)
        else:
            self.albero.setColumnCount(3)
            self.albero.setHeaderLabels([self.i18n.t("auto_extracted.header_file_subdir_module"), self.i18n.t("auto_extracted.header_git_status"), self.i18n.t("auto_extracted.header_last_git")])
            header = self.albero.header()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
            self.albero.setColumnWidth(2, 280)

    def _toggle_vista(self):
        """Commuta tra la visualizzazione compressa sintetica e la vista classica ad albero dei singoli file."""
        self.vista_compressa = not self.vista_compressa
        self.stato_espanso_modificati = False
        if self.vista_compressa:
            self.btn_toggle_vista.setText(self.i18n.t("btn_view_toggle_compressed"))
            self.btn_espandi_modificati.setVisible(False)
        else:
            self.btn_toggle_vista.setText(self.i18n.t("auto_extracted.btn_view_classic_mode"))
            self.btn_espandi_modificati.setVisible(True)
            self.btn_espandi_modificati.setText("🔍 Espandi Modificati")
        
        self._aggiorna_intestazioni_albero()
        self._popola_albero()

    def _toggle_espandi_comprimi_modificati(self):
        """Alterna l'espansione mirata dei soli elementi modificati e la compressione totale dell'albero."""
        if not self.stato_espanso_modificati:
            root = self.albero.invisibleRootItem()
            for i in range(root.childCount()):
                controlla_e_espandi(root.child(i))

            self.btn_espandi_modificati.setText(self.i18n.t("auto_extracted.btn_collapse_folders"))
            self.stato_espanso_modificati = True
        else:
            self.albero.collapseAll()
            self.btn_espandi_modificati.setText("🔍 Espandi Modificati")
            self.stato_espanso_modificati = False

