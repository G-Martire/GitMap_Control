import os
import json
from PyQt6.QtWidgets import QMenu, QApplication, QColorDialog

class ThemeController:
    """Gestisce l'applicazione e il salvataggio dei temi QSS e del color picker personalizzato."""
    def __init__(self, manager):
        self.manager = manager  # Riferimento al manager principale

    def carica_e_applica_tema_iniziale(self):
        """Legge dal file config.json il tema salvato e lo applica all'avvio."""
        config_path = os.path.join(self.manager.project_root, "config.json")
        tema_salvato = "light_clean"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    tema_salvato = data.get("theme", "light_clean")
            except Exception:
                pass
        self._applica_stile_css(tema_salvato, salva=False)

    def crea_menu_colori(self, parent_menu):
        """Crea il menu gerarchico per la selezione dei temi e personalizzazione."""
        menu_colori = QMenu("🎨 Tema Colori", self.manager)

        # 1. TEMA SCURO
        menu_scuro = menu_colori.addMenu("🌙 Tema Scuro")
        menu_scuro.addAction("Slate Scuro", lambda: self._cambia_e_salva_tema("dark_slate"))
        menu_scuro.addAction("Midnight Profondo", lambda: self._cambia_e_salva_tema("dark_midnight"))
        menu_scuro.addAction("Cyber Dark", lambda: self._cambia_e_salva_tema("dark_cyber"))

        # 2. TEMA CHIARO
        menu_chiaro = menu_colori.addMenu("☀️ Tema Chiaro")
        menu_chiaro.addAction("Clean Light (Default)", lambda: self._cambia_e_salva_tema("light_clean"))
        menu_chiaro.addAction("Warm Paper", lambda: self._cambia_e_salva_tema("light_warm"))
        menu_chiaro.addAction("Soft Gray", lambda: self._cambia_e_salva_tema("light_gray"))

        # 3. TEMI PREDEFINITI
        menu_predefiniti = menu_colori.addMenu("🎯 Temi Predefiniti")
        menu_predefiniti.addAction("Blu PADAS Brand", lambda: self._cambia_e_salva_tema("brand_blue"))
        menu_predefiniti.addAction("Industrial Steel", lambda: self._cambia_e_salva_tema("industrial_steel"))
        menu_predefiniti.addAction("Forest Green", lambda: self._cambia_e_salva_tema("forest_green"))

        menu_colori.addSeparator()

        # 4. PERSONALIZZA
        action_personalizza = menu_colori.addAction("⚙️ Personalizza...")
        action_personalizza.triggered.connect(self.apri_personalizzatore_colori)

        parent_menu.addMenu(menu_colori)

    def _cambia_e_salva_tema(self, nome_tema):
        """Applica il tema scelto e aggiorna il file config.json."""
        self._applica_stile_css(nome_tema, salva=True)

    def _applica_stile_css(self, tema, salva=True):
        """Genera e applica il foglio di stile QSS globale all'applicazione."""
        palette_stili = {
            "light_clean": "",
            "dark_slate": "QMainWindow { background-color: #1e293b; color: #f8fafc; } QGroupBox { color: #f8fafc; border: 1px solid #475569; }",
            "dark_midnight": "QMainWindow { background-color: #0f172a; color: #e2e8f0; } QGroupBox { color: #e2e8f0; border: 1px solid #334155; }",
            "dark_cyber": "QMainWindow { background-color: #090d16; color: #00ffcc; } QGroupBox { color: #00ffcc; border: 1px solid #00ffcc; }",
            "light_warm": "QMainWindow { background-color: #fdf8f6; color: #2d2320; } QGroupBox { color: #2d2320; border: 1px solid #e7d7d3; }",
            "light_gray": "QMainWindow { background-color: #f1f5f9; color: #0f172a; } QGroupBox { color: #0f172a; border: 1px solid #cbd5e1; }",
            "brand_blue": "QMainWindow { background-color: #f0f9ff; color: #0369a1; } QGroupBox { color: #0369a1; border: 1px solid #bae6fd; }",
            "industrial_steel": "QMainWindow { background-color: #e2e8f0; color: #334155; } QGroupBox { color: #334155; border: 1px solid #94a3b8; }",
            "forest_green": "QMainWindow { background-color: #f0fdf4; color: #166534; } QGroupBox { color: #166534; border: 1px solid #bbf7d0; }"
        }

        qss = palette_stili.get(tema, "")
        QApplication.instance().setStyleSheet(qss)

        if salva:
            config_path = os.path.join(self.manager.project_root, "config.json")
            data = {}
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception:
                    pass
            data["theme"] = tema
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"Errore nel salvataggio del tema in config.json: {e}")

    def apri_personalizzatore_colori(self):
        """Apre un color picker nativo per personalizzare il colore di sfondo principale."""
        colore = QColorDialog.getColor()
        if colore.isValid():
            hex_color = colore.name()
            qss_custom = f"QMainWindow {{ background-color: {hex_color}; color: #0f172a; }} QGroupBox {{ color: #0f172a; border: 1px solid #cbd5e1; }}"
            QApplication.instance().setStyleSheet(qss_custom)
            
            config_path = os.path.join(self.manager.project_root, "config.json")
            data = {}
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception:
                    pass
            data["theme"] = f"custom_{hex_color}"
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            except Exception:
                pass