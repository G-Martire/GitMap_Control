from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QCheckBox, QTextEdit

class PagesSummary:
    """Gestisce la costruzione della pagina di Riepilogo & Avvio del wizard i18n."""
    def __init__(self, dialog):
        self.dialog = dialog  # Riferimento al Dialog principale

    def costruisci_pagina_riepilogo(self):
        """Scheda 7: Riepilogo & Avvio."""
        pag = QWidget()
        layout = QVBoxLayout(pag)
        group = QGroupBox(self.dialog.i18n.t("summary_execution_options_title"))
        vbox = QVBoxLayout(group)
        
        self.dialog.chk_tutti_step = QCheckBox(self.dialog.i18n.t("label_run_all_steps"))
        self.dialog.chk_tutti_step.setChecked(True)
        self.dialog.chk_tutti_step.setStyleSheet("font-weight: bold; color: #0284c7;")
        vbox.addWidget(self.dialog.chk_tutti_step)
        
        self.dialog.txt_riepilogo_generale = QTextEdit()
        self.dialog.txt_riepilogo_generale.setReadOnly(True)
        self.dialog.txt_ri2 = self.dialog.txt_riepilogo_generale
        self.dialog.txt_riepilogo_generale.setMinimumHeight(260)
        self.dialog.txt_riepilogo_generale.setStyleSheet(
            "background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px; font-family: monospace; font-size: 11px;"
        )
        vbox.addWidget(self.dialog.txt_riepilogo_generale)
        
        self.dialog.stack_pagine.currentChanged.connect(self.aggiorna_testo_riepilogo_generale)
        layout.addWidget(group)
        return pag

    def aggiorna_testo_riepilogo_generale(self, index):
        if index == 6:  # Indice 6 corrisponde alla settima scheda (Riepilogo & Avvio)
            config = self.dialog.config_ctrl.ottieni_configurazione()
            
            s1_1 = f"✅ {self.dialog.i18n.t('status_enabled')}" if config["step1_1"] else f"⏭️ {self.dialog.i18n.t('status_skipped')}"
            s2 = f"✅ {self.dialog.i18n.t('status_enabled')}" if config["step2"] else f"⏭️ {self.dialog.i18n.t('status_skipped')}"
            s3_1 = f"✅ {self.dialog.i18n.t('status_enabled')}" if config["step3_1"] else f"⏭️ {self.dialog.i18n.t('status_skipped')}"
            s3_2 = f"✅ {self.dialog.i18n.t('status_enabled')}" if config["step3_2"] else f"⏭️ {self.dialog.i18n.t('status_skipped')}"
            s4 = f"✅ {self.dialog.i18n.t('status_enabled')}" if config["step4"] else f"⏭️ {self.dialog.i18n.t('status_skipped')}"
            
            lingue_str = ", ".join([f"{k} ({v})" for k, v in config["lingue_custom"].items()]) if config["lingue_custom"] else self.dialog.i18n.t("no_extra_languages")

            html_sintesi = (
                f"<b>{self.dialog.i18n.t('summary_project_folder_lbl')}</b><br>{config['progetto_root']}<br><br>"
                f"<b>{self.dialog.i18n.t('summary_locales_folder_lbl')}</b><br>{config['locales_dir']}<br><br>"
                f"<b>{self.dialog.i18n.t('summary_ai_model_lbl')}</b><br>{config['modello_ia']} (Batch: {config['batch_size']})<br><br>"
                f"<b>--------------------------------------------------</b><br>"
                f"<b>{self.dialog.i18n.t('summary_steps_status_lbl')}</b><br>"
                f"<b>--------------------------------------------------</b><br>"
                f"&nbsp;&nbsp;🔍 <b>Step 1.1 (Scansione & CSV):</b> {s1_1}<br>"
                f"&nbsp;&nbsp;🤖 <b>Step 2 (Classificazione IA):</b> {s2}<br>"
                f"&nbsp;&nbsp;📦 <b>Step 3.1 (Aggiornamento JSON):</b> {s3_1}<br>"
                f"&nbsp;&nbsp;📝 <b>Step 3.2 (Sostituzioni Codice):</b> {s3_2}<br>"
                f"&nbsp;&nbsp;🌍 <b>Step 4 (Traduzione Multi-lingua):</b> {s4}<br><br>"
                f"<b>{self.dialog.i18n.t('summary_extra_languages_lbl')}</b><br>{lingue_str}<br><br>"
                f"<b>{self.dialog.i18n.t('summary_auto_execution_lbl')}</b> {'Sì (Tutti in sequenza)' if config['successione_completa'] else 'Personalizzata (Solo step attivi)'}"
            )
            self.dialog.txt_riepilogo_generale.setHtml(html_sintesi)

