import os
from PyQt6.QtWidgets import QMessageBox

from git_map_core.dialogs import DialogSalvaVersione, DialogRiepilogoStatoGit, DialogSincronizzazioneUSB

class GitHistoryController:
    """Gestisce l'interazione avanzata con Git, il salvataggio versioni, la sincronizzazione USB e i commit passati."""
    def __init__(self, manager):
        self.manager = manager  # Riferimento al manager principale

    def evidenzia_modifiche_git(self):
        """Calcola lo stato Git, mostra il riepilogo nidificato per macro-moduli ed evidenzia i nodi sulla mappa."""
        if not (mappa_git := self.manager.git_ctrl.ottieni_mappa_stato_git()):
            QMessageBox.information(self.manager, "Stato Git Pulito", "Nessuna modifica rilevata nel progetto!")
            return

        self.manager.map_ctrl._reset_tutti_stili(self.manager.nodo_radice)
        self._aggiorna_nodi_git_ricorsivo(self.manager.nodo_radice, mappa_git)

        riepilogo = self.manager.git_ctrl.calcola_riepilogo_moduli(mappa_git)
        dlg = DialogRiepilogoStatoGit(self.manager, git_controller=self.manager.git_ctrl, riepilogo_dati=riepilogo)
        dlg.exec()
    
    def _aggiorna_nodi_git_ricorsivo(self, nodo, mappa_git):
        rel_p = os.path.relpath(nodo.percorso, start=self.manager.project_root).replace("\\", "/")
        if not nodo.is_dir:
            if rel_p in mappa_git:
                nodo.imposta_stile_git(mappa_git[rel_p])
        else:
            ha_modifiche = any(
                p == rel_p or p.startswith(rel_p + "/") or rel_p == "." 
                for p in mappa_git
            )
            if ha_modifiche:
                if not nodo.espanso:
                    nodo.toggle_espansione(forza_stato=True)
                if rel_p != ".":
                    stato_dir = mappa_git.get(rel_p, 'DIR_HAS_CHANGES')
                    nodo.imposta_stile_git(stato_dir)
                for _, child in nodo.linee_connessione:
                    self._aggiorna_nodi_git_ricorsivo(child, mappa_git)

    def apri_dialog_salva_versione(self):
        if DialogSalvaVersione(self.manager, git_controller=self.manager.git_ctrl).exec():
            self.manager.map_ctrl.reset_vista()
            self.manager.sidebar.carica_cronologia_commit()

    def visualizza_commit_passato(self, dati_commit):
        """Evidenzia sulla mappa visiva i file modificati nello specifico commit passato selezionato."""
        tag_git = dati_commit.get('tag_git', '')
        file_csv = dati_commit.get('file', '')
        
        mappa_commit = self.manager.git_ctrl.ottieni_mappa_commit_specifico(tag_git, file_csv)
        if not mappa_commit:
            QMessageBox.information(self.manager, "Nessuna Modifica", f"Nessun file rilevato per il commit {tag_git}.")
            return
        
        self.manager.map_ctrl._reset_tutti_stili(self.manager.nodo_radice)
        self._aggiorna_nodi_git_ricorsivo(self.manager.nodo_radice, mappa_commit)
        
        QMessageBox.information(
            self.manager, 
            "Vista Commit Storico", 
            f"<b>Visualizzazione Commit:</b> {tag_git}<br>"
            f"• Roadmap: <b>{dati_commit.get('roadmap')}</b><br>"
            f"• Risorse modificate: <b>{len(mappa_commit)}</b>"
        )

    def apri_dialog_usb(self):
        """Apre la finestra di dialogo per la sincronizzazione USB."""
        DialogSincronizzazioneUSB(self.manager, git_controller=self.manager.git_ctrl).exec()