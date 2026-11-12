import os
import csv
import json
import importlib.util
from PyQt6.QtCore import QThread, pyqtSignal


class WorkerPipelineI18N(QThread):
    """Worker asincrono con ruolo di puro orchestratore per la pipeline i18n modulare."""
    log_signal = pyqtSignal(str, str)                     # (testo_log, step_key)
    step_status_signal = pyqtSignal(str, str, bool, bool) # (step_key, titolo, completato, espandi)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._is_running = True
        
        # Estrazione granulare dei passaggi indipendenti e del file JSON principale
        self.esegui_step1_1 = config.get("step1_1", True)
        self.esegui_step2 = config.get("step2", True)
        self.esegui_step3_1 = config.get("step3_1", True)
        self.esegui_step3_2 = config.get("step3_2", True)
        self.esegui_step4 = config.get("step4", True)
        
        self.json_principale = config.get("json_principale", "it.json")
        self.modalita_lingue = config.get("modalita_lingue", "B")
        self.lingue_custom = config.get("lingue_custom", {})

    def _carica_configurazione_ia(self):
        """Carica la configurazione dal file globale ai_config.json nella root del progetto."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, '..', 'ai_config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Errore di lettura in ai_config.json: {e}")
        return {}

    def _importa_modulo_dinamico(self, nome_file):
        """Carica dinamicamente un modulo Python con caratteri speciali nel nome (punti/trattini)."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, nome_file)
        if not os.path.exists(file_path):
            return None
        module_name = nome_file.replace('.py', '').replace('.', '_').replace('-', '_')
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def run(self):
        try:
            progetto_root = self.config.get("progetto_root")
            locales_dir = self.config.get("locales_dir")
            modello_ia = self.config.get("modello_ia", "models/gemini-2.5-flash")
            batch_size = self.config.get("batch_size", 50)
            
            nome_progetto = os.path.basename(os.path.abspath(progetto_root))
            
            ai_config = self._carica_configurazione_ia()
            provider = ai_config.get("active_provider", "gemini")
            provider_cfg = ai_config.get("providers", {}).get(provider, {})
            api_key = provider_cfg.get("api_key", "")
            
            if not api_key:
                self.log_signal.emit("⚠️ Attenzione: Chiave API non trovata in ai_config.json!", "header")

            # --- INIZIALIZZAZIONE ---
            self.step_status_signal.emit("header", "🚀 Inizializzazione & Parametri", True, True)
            self.log_signal.emit(f"📁 Progetto: {nome_progetto}", "header")
            self.log_signal.emit(f"📂 Percorso: {progetto_root}", "header")
            self.log_signal.emit(f"📦 JSON Principale: {self.json_principale}", "header")
            self.log_signal.emit(f"🤖 Modello IA: {modello_ia} (Batch: {batch_size})", "header")
            
            self.progress_signal.emit(15)

            if not self._is_running:
                return

            # ==========================================
            # STEP 1.1: SCANSIONE CODICE & CSV
            # ==========================================
            if self.esegui_step1_1:
                self.step_status_signal.emit("step1_1", "🔍 [STEP 1.1] Scansione Codice & CSV", False, True)
                mod_1_1 = self._importa_modulo_dinamico("1.1-scanner_ui.py")
                if mod_1_1 and hasattr(mod_1_1, 'scansiona_codice'):
                    self.log_signal.emit("📦 Esecuzione Step 1.1 (Scansione sorgenti)...", "step1_1")
                    csv_path = mod_1_1.ottieni_percorso_csv(nome_progetto)
                    decisioni_prev, note_prev, righe_esistenti = mod_1_1.carica_decisioni_esistenti(csv_path)
                    stringhe_estratte = mod_1_1.scansiona_codice(progetto_root)
                    
                    viste_nel_csv = {(r['file_sorgente'], r['stringa']) for r in righe_esistenti}
                    final_rows = list(righe_esistenti)
                    nuove = 0
                    for item in stringhe_estratte:
                        chiave = (item['file_sorgente'], item['stringa'])
                        if chiave not in viste_nel_csv:
                            final_rows.append({
                                "stringa": item['stringa'],
                                "file_sorgente": item['file_sorgente'],
                                "classe": item['classe'],
                                "riga": item['riga'],
                                "da_sostituire": decisioni_prev.get(chiave, ""),
                                "key": "",
                                "note": note_prev.get(chiave, "")
                            })
                            viste_nel_csv.add(chiave)
                            nuove += 1

                    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=["stringa", "file_sorgente", "classe", "riga", "da_sostituire", "key", "note"])
                        writer.writeheader()
                        writer.writerows(final_rows)
                    self.log_signal.emit(f"Totale tracciate: {len(final_rows)} | Nuove: {nuove}", "step1_1")
                self.step_status_signal.emit("step1_1", "Scansione completata", True, False)
            else:
                self.log_signal.emit("⏭️ Step 1.1 saltato per scelta utente.", "header")
                self.step_status_signal.emit("step1_1", "🔍 [STEP 1.1] (Saltato)", True, False)

            self.progress_signal.emit(35)

            if not self._is_running:
                return

            # ==========================================
            # STEP 2: CLASSIFICAZIONE IA
            # ==========================================
            if self.esegui_step2:
                self.step_status_signal.emit("step2", "🤖 [STEP 2] Classificazione IA in corso...", False, True)
                mod_2 = self._importa_modulo_dinamico("2.1-ai_classifier.py")
                if mod_2 and hasattr(mod_2, 'genera_chiavi_stringhe'):
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    csv_path = os.path.join(base_dir, 'dubbi', f"{nome_progetto}.csv")
                    mod_2.genera_chiavi_stringhe(csv_path)
                self.step_status_signal.emit("step2", "Classificazione IA completata", True, False)
            else:
                self.log_signal.emit("⏭️ Step 2 saltato per scelta utente.", "header")
                self.step_status_signal.emit("step2", "🤖 [STEP 2] (Saltato)", True, False)

            self.progress_signal.emit(55)

            if not self._is_running:
                return

            # ==========================================
            # STEP 3.1: AGGIORNAMENTO JSON PRINCIPALE
            # ==========================================
            lingua_base_path = os.path.join(locales_dir, self.json_principale)
            if self.esegui_step3_1:
                self.step_status_signal.emit("step3_1", f"📦 [STEP 3.1] Aggiornamento {self.json_principale}...", False, True)
                if os.path.exists(lingua_base_path):
                    mod_3_2 = self._importa_modulo_dinamico("3.2-update_json.py")
                    if mod_3_2 and hasattr(mod_3_2, 'aggiorna_json_principale'):
                        self.log_signal.emit(f"📦 Aggiornamento file {self.json_principale} in corso...", "step3_1")
                        mod_3_2.aggiorna_json_principale(nome_progetto, lingua_base_path)
                    self.step_status_signal.emit("step3_1", "Aggiornamento JSON completato", True, False)
                else:
                    self.log_signal.emit(f"⚠️ File base JSON non trovato: {lingua_base_path}", "step3_1")
                    self.step_status_signal.emit("step3_1", f"📦 [STEP 3.1] Errore: {self.json_principale} mancante", False, False)
            else:
                self.log_signal.emit("⏭️ Step 3.1 saltato per scelta utente.", "header")
                self.step_status_signal.emit("step3_1", "📦 [STEP 3.1] (Saltato)", True, False)

            self.progress_signal.emit(75)

            if not self._is_running:
                return

            # ==========================================
            # STEP 3.2: SOSTITUZIONI NEL CODICE SORGENTE
            # ==========================================
            if self.esegui_step3_2:
                self.step_status_signal.emit("step3_2", "📝 [STEP 3.2] Applicazione sostituzioni nel codice...", False, True)
                if os.path.exists(lingua_base_path):
                    mod_3_1 = self._importa_modulo_dinamico("3.1-apply_code.py")
                    if mod_3_1 and hasattr(mod_3_1, 'applica_sostituzioni_codice'):
                        self.log_signal.emit("📝 Applicazione modifiche ai file .py in corso...", "step3_2")
                        mod_3_1.applica_sostituzioni_codice(nome_progetto, progetto_root)
                    self.step_status_signal.emit("step3_2", "Sostituzioni nel codice completate", True, False)
                else:
                    self.log_signal.emit(f"⚠️ File base JSON non trovato: {lingua_base_path}", "step3_2")
                    self.step_status_signal.emit("step3_2", f"📝 [STEP 3.2] Errore: {self.json_principale} mancante", False, False)
            else:
                self.log_signal.emit("⏭️ Step 3.2 saltato per scelta utente.", "header")
                self.step_status_signal.emit("step3_2", "📝 [STEP 3.2] (Saltato)", True, False)

            self.progress_signal.emit(90)

            if not self._is_running:
                return

            # ==========================================
            # STEP 4: TRADUZIONE MULTI-LINGUA
            # ==========================================
            if self.esegui_step4:
                self.step_status_signal.emit("step4", "🌍 [STEP 4] Traduzione Multi-lingua", False, True)
                if os.path.exists(lingua_base_path):
                    mod_4 = self._importa_modulo_dinamico("4-auto_translate.py")
                    if mod_4:
                        self.log_signal.emit(f"🌍 Traduzione in corso (Modalità {self.modalita_lingue})...", "step4")
                        with open(lingua_base_path, 'r', encoding='utf-8') as f:
                            base_data = json.load(f)
                        base_flat = mod_4.flatten_json(base_data)
                        
                        lingue_da_processare = {}
                        if self.modalita_lingue == 'A':
                            lingue_da_processare = self.lingue_custom
                        elif self.modalita_lingue in ['B', 'C']:
                            for filename in os.listdir(locales_dir):
                                if filename.endswith(".json"):
                                    path = os.path.join(locales_dir, filename)
                                    if os.path.abspath(path) != os.path.abspath(lingua_base_path):
                                        try:
                                            with open(path, 'r', encoding='utf-8') as lf:
                                                ldata = json.load(lf)
                                                code = ldata.get("meta", {}).get("code", filename.replace(".json", ""))
                                                native = ldata.get("meta", {}).get("native_name", code.capitalize())
                                                lingue_da_processare[code] = native
                                        except Exception:
                                            pass
                            if self.modalita_lingue == 'C':
                                for code, native in self.lingue_custom.items():
                                    if code not in lingue_da_processare:
                                        lingue_da_processare[code] = native

                        for code, native_name in lingue_da_processare.items():
                            target_path = os.path.join(locales_dir, f"{code}.json")
                            target_data = {}
                            if os.path.exists(target_path):
                                try:
                                    with open(target_path, 'r', encoding='utf-8') as tf:
                                        target_data = json.load(tf)
                                except Exception:
                                    pass
                            target_flat = mod_4.flatten_json(target_data)
                            updated_flat = mod_4.traduci_chiavi_mancanti(base_flat, target_flat, code, native_name)
                            final_data = mod_4.unflatten_json(updated_flat)
                            with open(target_path, 'w', encoding='utf-8') as tf:
                                json.dump(final_data, tf, ensure_ascii=False, indent=2)
                            self.log_signal.emit(f"✅ Lingua aggiornata: {code}.json", "step4")

                    self.step_status_signal.emit("step4", "Traduzioni multi-lingua completate", True, False)
                else:
                    self.log_signal.emit(f"⚠️ File base JSON non trovato: {lingua_base_path}", "step4")
                    self.step_status_signal.emit("step4", f"🌍 [STEP 4] Errore: {self.json_principale} mancante", False, False)
            else:
                self.log_signal.emit("⏭️ Step 4 saltato per scelta utente.", "header")
                self.step_status_signal.emit("step4", "🌍 [STEP 4] (Saltato)", True, False)

            self.progress_signal.emit(100)
            self.finished_signal.emit(True, "Pipeline completata con successo!")

        except Exception as e:
            self.finished_signal.emit(False, f"Errore critico nella pipeline: {str(e)}")

    def stop(self):
            """Interrompe forzatamente il thread (Kill-Switch d'emergenza)."""
            self._is_running = False
            self.terminate()
            self.wait()
            self.log_signal.emit("🛑 Processo interrotto d'emergenza dall'utente.", "header")

