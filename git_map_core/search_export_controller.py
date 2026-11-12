import os
import json
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox


class SearchExportController:
    """Gestisce la ricerca nel filesystem, la generazione dell'albero testuale e l'esportazione JSON sul progetto attivo."""
    def __init__(self, manager):
        self.manager = manager

    @property
    def root_dir(self):
        """Restituisce dinamicamente la cartella radice del progetto attualmente attivo."""
        return getattr(self.manager, 'root_dir', os.getcwd())

    @property
    def project_root(self):
        """Restituisce dinamicamente il percorso di riferimento per i file relativi."""
        return getattr(self.manager, 'project_root', self.root_dir)

    def trova_percorso_filesystem(self, query: str):
        query_norm = query.lower()
        target_file = f"{query_norm}.py" if not query_norm.endswith(".py") and "." not in query_norm else query_norm

        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if not d.startswith(('.', '__')) and d != '.venv']
            for f in files:
                if f.lower() == target_file or query_norm in f.lower():
                    return os.path.join(root, f)
            for d in dirs:
                if d.lower() == query_norm or query_norm in d.lower():
                    return os.path.join(root, d)
        return None

    def _costruisci_albero_txt(self, dir_path, prefisso=""):
        righe = []
        try:
            elementi = sorted(os.listdir(dir_path))
        except PermissionError:
            return righe

        elementi_filtrati = [e for e in elementi if not e.startswith(('.', '__')) and e != '.venv']
        cartelle = [e for e in elementi_filtrati if os.path.isdir(os.path.join(dir_path, e))]
        file_validi = [e for e in elementi_filtrati if os.path.isfile(os.path.join(dir_path, e)) and e.endswith(('.py', '.json', '.md'))]
        
        tutti = cartelle + file_validi
        totale = len(tutti)

        for i, nome in enumerate(tutti):
            is_ultimo = (i == totale - 1)
            connettore = "└── " if is_ultimo else "├── "
            full_p = os.path.join(dir_path, nome)

            if os.path.isdir(full_p):
                righe.append(f"{prefisso}{connettore}{nome}/")
                nuovo_prefisso = prefisso + ("    " if is_ultimo else "│   ")
                righe.extend(self._costruisci_albero_txt(full_p, nuovo_prefisso))
            else:
                righe.append(f"{prefisso}{connettore}{nome}")

        return righe

    def copia_albero_appunti(self, parent_widget=None):
        nome_radice = os.path.basename(os.path.abspath(self.root_dir))
        righe = [f"{nome_radice}/"]
        righe.extend(self._costruisci_albero_txt(self.root_dir))
        
        testo_albero = "\n".join(righe)
        QApplication.clipboard().setText(testo_albero)
        if parent_widget:
            QMessageBox.information(parent_widget, "Albero Copiato!", "La struttura ad albero è stata copiata negli appunti per l'IA!")

    def esporta_json_dettagliato(self, parent_widget=None):
        lista_dati = []
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if not d.startswith(('.', '__')) and d != '.venv']
            for file in sorted(files):
                if file.endswith(".py"):
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, start=self.project_root).replace("\\", "/")
                    lista_dati.append({"percorso": rel_p, "nome_file": file})

        percorso_salvataggio, _ = QFileDialog.getSaveFileName(parent_widget, "Salva JSON Architettura", "struttura_progetto.json", "JSON (*.json)")
        if percorso_salvataggio:
            with open(percorso_salvataggio, "w", encoding="utf-8") as f:
                json.dump(lista_dati, f, indent=2, ensure_ascii=False)
            if parent_widget:
                QMessageBox.information(parent_widget, "Esportazione Completata", f"File salvato in:\n{percorso_salvataggio}")

