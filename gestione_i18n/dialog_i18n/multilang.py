import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLabel, QCheckBox, 
    QHBoxLayout, QComboBox, QSpinBox, QRadioButton, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush

class PagesMultilang:
    """Gestisce la costruzione della pagina per lo Step 4 (Multi-lingua) e il caricamento delle lingue."""
    def __init__(self, dialog):
        self.dialog = dialog  # Riferimento al Dialog principale

    def costruisci_pagina_step4(self):
        """Scheda 6: Step 4 (Multi-lingua)."""
        pag = QWidget()
        layout = QVBoxLayout(pag)
        group = QGroupBox(self.dialog.i18n.t("step_4_multilang_config_title"))
        layout_lingue = QVBoxLayout(group)
        layout_lingue.setSpacing(6)
        
        self.dialog.chk_step4 = QCheckBox(self.dialog.i18n.t("step_4_enable_label"))
        self.dialog.chk_step4.setChecked(True)
        layout_lingue.addWidget(self.dialog.chk_step4)

        h_modello = QHBoxLayout()
        h_modello.addWidget(QLabel(self.dialog.i18n.t("auto_extracted.model_gemini_step_4_short")))
        self.dialog.combo_modelli_step4 = QComboBox()
        self.dialog.combo_modelli_step4.addItems([
            "models/gemini-3.1-flash-lite",
            "models/gemini-3.5-flash",
            "models/gemini-3.7-flash",
            "models/gemini-2.5-flash"
        ])
        h_modello.addWidget(self.dialog.combo_modelli_step4)
        layout_lingue.addLayout(h_modello)

        h_batch = QHBoxLayout()
        h_batch.addWidget(QLabel(self.dialog.i18n.t("label_step_4_batch_size")))
        self.dialog.spin_batch_step4 = QSpinBox()
        self.dialog.spin_batch_step4.setRange(10, 200)
        self.dialog.spin_batch_step4.setValue(50)
        h_batch.addWidget(self.dialog.spin_batch_step4)
        layout_lingue.addLayout(h_batch)
        
        self.dialog.radio_lingue_esistenti = QRadioButton(self.dialog.i18n.t("opt_translate_specific_languages"))
        self.dialog.radio_lingue_tutte = QRadioButton(self.dialog.i18n.t("opt_translate_all_locales"))
        self.dialog.radio_lingue_miste = QRadioButton(self.dialog.i18n.t("opt_translate_all_plus_new"))
        self.dialog.radio_lingue_tutte.setChecked(True)
        
        layout_lingue.addWidget(self.dialog.radio_lingue_esistenti)
        layout_lingue.addWidget(self.dialog.radio_lingue_tutte)
        layout_lingue.addWidget(self.dialog.radio_lingue_miste)
        
        self.dialog.lbl_riepilogo = QLabel(self.dialog.i18n.t("label_selected_languages"))
        self.dialog.lbl_riepilogo.setStyleSheet("margin-top: 4px;")
        layout_lingue.addWidget(self.dialog.lbl_riepilogo)
        
        self.dialog.txt_riepilogo = QTextEdit()
        self.dialog.txt_riepilogo.setReadOnly(True)
        self.dialog.txt_riepilogo.setMaximumHeight(65)
        layout_lingue.addWidget(self.dialog.txt_riepilogo)

        h_layout_lingue_split = QHBoxLayout()
        v_esistenti = QVBoxLayout()
        v_esistenti.setSpacing(2)
        v_esistenti.addWidget(QLabel(self.dialog.i18n.t("label_existing_languages")))
        self.dialog.combo_esistenti = QComboBox()
        self.dialog.model_esistenti = QStandardItemModel(self.dialog.combo_esistenti)
        self.dialog.combo_esistenti.setModel(self.dialog.model_esistenti)
        self.dialog.combo_esistenti.setEditable(True)
        self.dialog.combo_esistenti.lineEdit().setReadOnly(True)
        v_esistenti.addWidget(self.dialog.combo_esistenti)
        h_layout_lingue_split.addLayout(v_esistenti)
        
        v_aggiunta = QVBoxLayout()
        v_aggiunta.setSpacing(2)
        v_aggiunta.addWidget(QLabel(self.dialog.i18n.t("label_global_language_archive")))
        self.dialog.combo_globali = QComboBox()
        self.dialog.model_globali = QStandardItemModel(self.dialog.combo_globali)
        self.dialog.combo_globali.setModel(self.dialog.model_globali)
        self.dialog.combo_globali.setEditable(True)
        self.dialog.combo_globali.lineEdit().setReadOnly(True)
        v_aggiunta.addWidget(self.dialog.combo_globali)
        h_layout_lingue_split.addLayout(v_aggiunta)
        
        layout_lingue.addLayout(h_layout_lingue_split)
        
        self.dialog.model_esistenti.itemChanged.connect(self.aggiorna_riepilogo_lingue)
        self.dialog.model_globali.itemChanged.connect(self.aggiorna_riepilogo_lingue)
        self.popola_archivio_lingue()
        self.rileva_lingue_esistenti()
        
        layout.addWidget(group)
        return pag

    def popola_archivio_lingue(self, codici_esistenti=None):
        if codici_esistenti is None:
            codici_esistenti = set()
            
        self.dialog.model_globali.clear()
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(os.path.dirname(base_dir), 'global_languages.json')
        
        archivio = []
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    archivio = json.load(f)
            except Exception as e:
                print(f"⚠️ Errore durante la lettura di global_languages.json: {e}")
        
        for elem in archivio:
            code = elem.get("code", "").lower()
            native = elem.get("native", "")
            english = elem.get("english", "")
            
            display_text = f"{native} - {english}"
            is_gia_presente = code in codici_esistenti
            if is_gia_presente:
                display_text += " *"
                
            item = QStandardItem(display_text)
            item.setData((code, english), Qt.ItemDataRole.UserRole)
            
            if is_gia_presente:
                item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                item.setToolTip(self.dialog.i18n.t("msg_language_already_exists"))
                item.setForeground(QBrush(QColor("#334155")))
            else:
                item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                item.setCheckState(Qt.CheckState.Unchecked)
                
            self.dialog.model_globali.appendRow(item)

    def rileva_lingue_esistenti(self):
        self.dialog.model_esistenti.clear()
        if hasattr(self.dialog, 'combo_json_principale'):
            self.dialog.combo_json_principale.clear()
            
        locales_dir = self.dialog.input_cartella_locales.text()
        codici_trovati = set()
        
        if os.path.exists(locales_dir):
            for f in sorted(os.listdir(locales_dir)):
                if f.endswith(".json"):
                    code = f.replace(".json", "").lower()
                    codici_trovati.add(code)
                    
                    if hasattr(self.dialog, 'combo_json_principale'):
                        self.dialog.combo_json_principale.addItem(f, f)
                    
                    english_name = code.capitalize()
                    
                    item = QStandardItem(f"{code.upper()} - {english_name}")
                    item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                    item.setCheckState(Qt.CheckState.Checked)
                    item.setData((code, english_name), Qt.ItemDataRole.UserRole)
                    self.dialog.model_esistenti.appendRow(item)
                    
        if hasattr(self.dialog, 'combo_json_principale'):
            idx = self.dialog.combo_json_principale.findText("it.json")
            if idx >= 0:
                self.dialog.combo_json_principale.setCurrentIndex(idx)
                    
        self.popola_archivio_lingue(codici_trovati)

    def aggiorna_riepilogo_lingue(self, item=None):
        selezionate = set()
        for i in range(self.dialog.model_esistenti.rowCount()):
            it = self.dialog.model_esistenti.item(i)
            if it and it.checkState() == Qt.CheckState.Checked:
                _, english_name = it.data(Qt.ItemDataRole.UserRole)
                selezionate.add(english_name)
        for i in range(self.dialog.model_globali.rowCount()):
            it = self.dialog.model_globali.item(i)
            if it and it.checkState() == Qt.CheckState.Checked:
                _, english_name = it.data(Qt.ItemDataRole.UserRole)
                selezionate.add(english_name)
        self.dialog.txt_riepilogo.setPlainText(", ".join(sorted(list(selezionate))))

