import os
from PyQt6.QtWidgets import QFileDialog

class I18NConfigController:
    """Gestisce la logica di navigazione, i pulsanti e l'acquisizione dei dati di configurazione del wizard i18n."""
    def __init__(self, dialog):
        self.dialog = dialog  # Riferimento al Dialog principale

    def pagina_precedente(self):
        idx = self.dialog.stack_pagine.currentIndex()
        if idx > 0:
            self.dialog.stack_pagine.setCurrentIndex(idx - 1)
            self.dialog.lista_navigazione.setCurrentRow(idx - 1)

    def pagina_successiva(self):
        idx = self.dialog.stack_pagine.currentIndex()
        if idx < self.dialog.stack_pagine.count() - 1:
            self.dialog.stack_pagine.setCurrentIndex(idx + 1)
            self.dialog.lista_navigazione.setCurrentRow(idx + 1)

    def aggiorna_stato_pulsanti_navigazione(self, index):
        self.dialog.btn_indietro.setEnabled(index > 0)
        self.dialog.btn_avanti.setEnabled(index < self.dialog.stack_pagine.count() - 1)

    def sfoglia_progetto(self):
        dir_path = QFileDialog.getExistingDirectory(self.dialog, "Seleziona Progetto", self.dialog.input_cartella_progetto.text())
        if dir_path:
            self.dialog.input_cartella_progetto.setText(dir_path)
            self.dialog.input_cartella_locales.setText(os.path.join(dir_path, "locales") if 'os' in globals() or __import__('os').path.exists(dir_path) else dir_path + "/locales")
            self.dialog.multilang_page.rileva_lingue_esistenti()

    def sfoglia_locales(self):
        import os
        dir_path = QFileDialog.getExistingDirectory(self.dialog, "Seleziona Locales", self.dialog.input_cartella_locales.text())
        if dir_path:
            self.dialog.input_cartella_locales.setText(dir_path)
            self.dialog.multilang_page.rileva_lingue_esistenti()

    def ottieni_configurazione(self):
        tutti_attivi = self.dialog.chk_tutti_step.isChecked() if hasattr(self.dialog, 'chk_tutti_step') else True
        modalita_lingue = 'B'
        if hasattr(self.dialog, 'radio_lingue_esistenti') and self.dialog.radio_lingue_esistenti.isChecked():
            modalita_lingue = 'A'
        elif hasattr(self.dialog, 'radio_lingue_miste') and self.dialog.radio_lingue_miste.isChecked():
            modalita_lingue = 'C'

        lingue_custom = {}
        if hasattr(self.dialog, 'model_globali'):
            for i in range(self.dialog.model_globali.rowCount()):
                it = self.dialog.model_globali.item(i)
                import os
                from PyQt6.QtCore import Qt
                if it and it.checkState() == Qt.CheckState.Checked:
                    code, english_name = it.data(Qt.ItemDataRole.UserRole)
                    lingue_custom[code] = english_name

        return {
            "progetto_root": self.dialog.input_cartella_progetto.text(),
            "locales_dir": self.dialog.input_cartella_locales.text(),
            "json_principale": self.dialog.combo_json_principale.currentText().strip() if hasattr(self.dialog, 'combo_json_principale') else "it.json",
            "modello_ia": self.dialog.combo_modelli_step2.currentText().strip(),
            "modello_ia_step4": self.dialog.combo_modelli_step4.currentText().strip() if hasattr(self.dialog, 'combo_modelli_step4') else "",
            "batch_size": self.dialog.spin_batch_step2.value(),
            "batch_size_step4": self.dialog.spin_batch_step4.value() if hasattr(self.dialog, 'spin_batch_step4') else 50,
            "successione_completa": tutti_attivi,
            "step1_1": tutti_attivi or self.dialog.chk_step1_1.isChecked(),
            "step2": tutti_attivi or self.dialog.chk_step2.isChecked(),
            "step3_1": tutti_attivi or self.dialog.chk_step3_1.isChecked(),
            "step3_2": tutti_attivi or self.dialog.chk_step3_2.isChecked(),
            "step4": tutti_attivi or self.dialog.chk_step4.isChecked(),
            "modalita_lingue": modalita_lingue,
            "lingue_custom": lingue_custom
        }