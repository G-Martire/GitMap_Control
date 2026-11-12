from PyQt6.QtWidgets import QMessageBox, QInputDialog


class RiepilogoGitController:
    """Controller dedicato alla logica dati, calcoli e gestione dei macro-moduli per il riepilogo Git."""
    def __init__(self, manager, git_controller, riepilogo_dati):
        self.manager = manager
        self.git_controller = git_controller
        self.riepilogo_dati = riepilogo_dati or {}

    def calcola_totale_modifiche(self):
        """Calcola il totale globale delle risorse modificate o nuove."""
        return sum(v['totale'] for v in self.riepilogo_dati.values())

    def aggiungi_macro_modulo(self):
        """Permette all'utente di aggiungere un nuovo macro-modulo da salvare nel CSV."""
        testo, ok = QInputDialog.getText(
            self.manager, 
            "Aggiungi Macro-Modulo", 
            "Inserisci il percorso relativo della nuova cartella principale (es. applicazioni/nuovo_tool):"
        )
        if ok and testo.strip():
            nuovo_modulo = testo.strip().replace("\\", "/")
            moduli_attuali = self.git_controller.ottieni_struttura_moduli() if self.git_controller else []
            if nuovo_modulo not in moduli_attuali:
                moduli_attuali.append(nuovo_modulo)
                if self.git_controller:
                    self.git_controller.salva_struttura_moduli(moduli_attuali)
                QMessageBox.information(
                    self.manager, 
                    "Modulo Aggiunto", 
                    f"Il modulo '<b>{nuovo_modulo}</b>' è stato salvato nel CSV <i>struttura_moduli.csv</i>.<br>"
                    "Ricarica lo stato Git per aggiornare il riepilogo."
                )
                return True
        return False

    def prepara_albero_classico_sub_tree(self, info):
        """Costruisce la struttura ad albero nidificata per la vista classica."""
        sub_tree = {'dirs': {}, 'files': []}
        for item_data in info['file']:
            if len(item_data) == 3:
                file_path, stato, ultimo_git = item_data
            else:
                file_path, stato = item_data
                ultimo_git = "-"

            modello_modulo = info.get('modulo', '') # Fallback
            parti = file_path.split('/')
            curr = sub_tree
            for i in range(len(parti) - 1):
                dname = parti[i]
                if dname not in curr['dirs']:
                    curr['dirs'][dname] = {'dirs': {}, 'files': []}
                curr = curr['dirs'][dname]
            curr['files'].append((parti[-1], file_path, stato, ultimo_git))
        return sub_tree

