import os
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QTransform

from git_map_core.nodes import NodoMindMap
from git_map_core.dialogs import DialogGestioneProgetti

class MapController:
    """Gestisce la logica della mappa mentale, la navigazione, la ricerca e i filtri visivi."""
    def __init__(self, manager):
        self.manager = manager  # Riferimento al manager principale

    def inizializza_nodo_radice(self):
        """Crea e posiziona il nodo radice della mappa sulla scena."""
        self.manager.scene.clear()
        nome_radice = os.path.basename(os.path.abspath(self.manager.root_dir))
        self.manager.nodo_radice = NodoMindMap(nome_radice, self.manager.root_dir, is_dir=True)
        self.manager.nodo_radice.setPos(100, 350)
        self.manager.scene.addItem(self.manager.nodo_radice)
        self.manager.nodo_radice.toggle_espansione(forza_stato=True)

    def apri_dialog_progetti(self):
        """Apre il pop-up per selezionare o aggiungere un nuovo progetto dal CSV e aggiorna l'interfaccia."""
        dlg = DialogGestioneProgetti(self.manager, percorso_corrente=self.manager.root_dir)
        if dlg.exec():
            nuovo_percorso = dlg.percorso_selezionato
            if os.path.exists(nuovo_percorso):
                self.manager.root_dir = nuovo_percorso
                self.manager.project_root = nuovo_percorso
                self.inizializza_nodo_radice()
                self.reset_vista()
                self.manager.sidebar.carica_cronologia_commit()

    def reset_vista(self):
        self.manager.view.setTransform(QTransform())
        if hasattr(self.manager, 'nodo_radice') and self.manager.nodo_radice:
            self._reset_tutti_stili(self.manager.nodo_radice)
            self.manager.view.centerOn(self.manager.nodo_radice)

    def _reset_tutti_stili(self, nodo):
        nodo._imposta_stile_base()
        for _, child in nodo.linee_connessione:
            self._reset_tutti_stili(child)

    def esegui_ricerca(self):
        if not (query := self.manager.input_cerca.text().strip()):
            return
        if not (target_path := self.manager.search_export_controller.trova_percorso_filesystem(query)):
            return
        self._reset_tutti_stili(self.manager.nodo_radice)
        nodo_corrente = self.manager.nodo_radice
        for parte in os.path.relpath(target_path, start=self.manager.root_dir).split(os.sep):
            if not nodo_corrente.espanso:
                nodo_corrente.toggle_espansione(forza_stato=True)
            nodo_corrente = next((child for _, child in nodo_corrente.linee_connessione if child.nome.lower() == parte.lower()), nodo_corrente)
        nodo_corrente.evidenzia_ricerca()
        self.manager.scene.clearSelection()
        nodo_corrente.setSelected(True)
        self.manager.view.centerOn(nodo_corrente)

    def toggle_sidebar(self):
        """Apre o chiude il pannello laterale dei filtri."""
        stato_attuale = self.manager.sidebar.isVisible()
        self.manager.sidebar.setVisible(not stato_attuale)

    def applica_filtri_sidebar(self):
        """Propaga le regole dei filtri a tutti i nodi dell'albero."""
        if hasattr(self.manager, 'nodo_radice') and self.manager.nodo_radice:
            impostazioni = self.manager.sidebar.ottieni_impostazioni_filtro()
            self._applica_filtri_ricorsivo(self.manager.nodo_radice, impostazioni)

    def _applica_filtri_ricorsivo(self, nodo, imp):
        """Applica visibilità/opacità al nodo corrente e ai suoi figli."""
        st = nodo.stato_git

        corrisponde = True
        if not nodo.is_dir:
            if st == 'M' and not imp['mostra_M']:
                corrisponde = False
            elif st in ('??', 'A') and not imp['mostra_NEW']:
                corrisponde = False
            elif st is None and not imp['mostra_CLEAN']:
                corrisponde = False

        if corrisponde:
            nodo.setVisible(True)
            nodo.setOpacity(1.0)
        else:
            if imp['modalita_nascondi']:
                nodo.setVisible(False)
            else:
                nodo.setVisible(True)
                nodo.setOpacity(0.2)

        for _, child in nodo.linee_connessione:
            self._applica_filtri_ricorsivo(child, imp)