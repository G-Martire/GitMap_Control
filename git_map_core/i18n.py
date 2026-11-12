import os
import json

class LanguageManager:
    """Gestisce il caricamento dei file JSON di traduzione, la persistenza e la ricerca delle lingue."""
    def __init__(self, default_lang="it", language_dir=None):
        self.translations = {}
        self.current_lang = default_lang
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Root del progetto (GitMap_Control)
        self.project_root = os.path.abspath(os.path.join(base_dir, '..'))
        
        if language_dir is None:
            self.language_dir = os.path.join(self.project_root, 'locales')
        else:
            self.language_dir = language_dir
        
        self.config_path = os.path.join(self.project_root, 'config.json')
        
        # Carica la lingua salvata in precedenza se esiste
        saved_lang = self._carica_config_lingua()
        if saved_lang:
            self.current_lang = saved_lang
        
        self.carica_lingua(self.current_lang)

    def _carica_config_lingua(self):
        """Legge la preferenza della lingua dal file di configurazione."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("language")
            except Exception:
                pass
        return None

    def salva_config_lingua(self, lang_code):
        """Salva la preferenza della lingua nel file di configurazione."""
        data = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                pass
        data["language"] = lang_code
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Errore salvataggio config lingua: {e}")

    def ottieni_lingue_disponibili(self):
        """Scansiona la cartella language/ e restituisce un dizionario delle lingue con i metadati."""
        lingue = {}
        if os.path.exists(self.language_dir):
            for filename in os.listdir(self.language_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.language_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            meta = data.get("meta", {})
                            code = meta.get("code", filename.replace(".json", ""))
                            lingue[code] = {
                                "native_name": meta.get("native_name", code),
                                "english_name": meta.get("english_name", code)
                            }
                    except Exception as e:
                        print(f"Errore lettura metadati per {filename}: {e}")
        return lingue

    def carica_lingua(self, lang_code):
        """Carica il file JSON corrispondente alla lingua scelta e salva la preferenza."""
        self.current_lang = lang_code
        file_path = os.path.join(self.language_dir, f"{lang_code}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            except Exception as e:
                print(f"Errore caricamento lingua {lang_code}: {e}")
                self.translations = {}
        else:
            print(f"File lingua non trovato: {file_path}")
            self.translations = {}
        self.salva_config_lingua(lang_code)

    def t(self, key_path):
        """
        Recupera la stringa tradotta usando una chiave gerarchica (es. 'menu_progetto.titolo').
        Se la chiave non esiste, restituisce la chiave stessa come fallback.
        """
        if not self.translations:
            return key_path
            
        parti = key_path.split('.')
        nodo = self.translations
        for parte in parti:
            if isinstance(nodo, dict) and parte in nodo:
                nodo = nodo[parte]
            else:
                return key_path  # Fallback di sicurezza
        return nodo if isinstance(nodo, str) else key_path

