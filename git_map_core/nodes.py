import os
import subprocess
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QMenu, QGraphicsItem, QGraphicsPathItem
from PyQt6.QtGui import QPen, QBrush, QColor, QPainterPath, QFont, QAction
from PyQt6.QtCore import Qt, QPointF

class NodoMindMap(QGraphicsRectItem):
    """Rappresenta un elemento della Mappa Mentale (Cartella o File) espandibile e cliccabile."""
    def __init__(self, nome, percorso, is_dir=True, parent_node=None):
        super().__init__(-75, -20, 150, 40)
        self.nome = nome
        self.percorso = percorso
        self.is_dir = is_dir
        self.parent_node = parent_node
        self.child_nodes = []
        self.linee_connessione = []
        self.espanso = False
        self.stato_git = None

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self._imposta_stile_base()

        etichetta = f"📁 {self.nome}" if self.is_dir else f"📄 {self.nome}"
        self.testo_item = QGraphicsTextItem(etichetta, self)
        font = QFont("Segoe UI", 9, QFont.Weight.Bold if self.is_dir else QFont.Weight.Normal)
        self.testo_item.setFont(font)
        self.testo_item.setDefaultTextColor(QColor(30, 41, 59))
        
        rect_t = self.testo_item.boundingRect()
        self.testo_item.setPos(-rect_t.width() / 2, -rect_t.height() / 2)

    def _imposta_stile_base(self):
        """Ripristina i colori standard del nodo."""
        self.stato_git = None
        if self.is_dir:
            self.setBrush(QBrush(QColor(239, 246, 255)))
            self.setPen(QPen(QColor(37, 99, 235), 2))
        else:
            self.setBrush(QBrush(QColor(243, 244, 246)))
            self.setPen(QPen(QColor(100, 116, 139), 1.5))

    def evidenzia_ricerca(self):
        """Evidenzia visivamente il nodo trovato dalla ricerca con colore Giallo/Oro."""
        self.setBrush(QBrush(QColor(254, 240, 138)))
        self.setPen(QPen(QColor(217, 119, 6), 3.5))

    def imposta_stile_git(self, stato):
        """Applica uno stile visivo specifico in base allo stato Git del file o della cartella."""
        self.stato_git = stato
        if stato == 'M':
            self.setBrush(QBrush(QColor(255, 237, 213)))
            self.setPen(QPen(QColor(234, 88, 12), 2.5))
        elif stato in ('??', 'A'):
            self.setBrush(QBrush(QColor(220, 252, 231)))
            self.setPen(QPen(QColor(22, 163, 74), 2.5))
        elif stato == 'DIR_HAS_CHANGES':
            self.setBrush(QBrush(QColor(254, 243, 199)))
            self.setPen(QPen(QColor(217, 119, 6), 2, Qt.PenStyle.DashLine))

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.aggiorna_linee()
        return super().itemChange(change, value)

    def aggiorna_linee(self):
        for linea, child in self.linee_connessione:
            linea.aggiorna_percorso(self.scenePos(), child.scenePos())
        if self.parent_node:
            for linea, child in self.parent_node.linee_connessione:
                if child == self:
                    linea.aggiorna_percorso(self.parent_node.scenePos(), self.scenePos())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_dir:
            self.toggle_espansione()
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        """Menu contestuale al tasto destro: Apre il percorso in Esplora Risorse."""
        menu = QMenu()
        
        # Recupero sicuro di i18n dalla vista/scena principale o fallback diretto
        testo_azione = "Apri in Esplora Risorse"
        try:
            # Tenta di risalire alla finestra principale attraverso la scena e le views
            view = self.scene().views()[0]
            main_win = view.parent()
            if hasattr(main_win, 'i18n') and main_win.i18n:
                testo_azione = main_win.i18n.t("auto_extracted.btn_open_file_explorer")
        except Exception:
            pass

        azione_apri = QAction(testo_azione, menu)
        azione_apri.triggered.connect(self._apri_in_esplora_risorse)
        menu.addAction(azione_apri)
        menu.exec(event.screenPos())

    def _apri_in_esplora_risorse(self):
        abs_path = os.path.abspath(self.percorso)
        if not os.path.exists(abs_path):
            return
        try:
            if os.path.isdir(abs_path):
                subprocess.Popen(["explorer", abs_path])
            else:
                subprocess.Popen(["explorer", "/select,", abs_path])
        except Exception as e:
            print(f"[ERRORE] Impossibile aprire Esplora Risorse: {e}")

    def toggle_espansione(self, forza_stato=None):
        if not self.is_dir:
            return

        nuovo_stato = not self.espanso if forza_stato is None else forza_stato
        if self.espanso == nuovo_stato:
            return

        self.espanso = nuovo_stato
        if self.espanso:
            self._crea_figli()
        else:
            self._rimuovi_figli()

    def _crea_figli(self):
        if self.child_nodes or not os.path.exists(self.percorso):
            return

        try:
            elementi = os.listdir(self.percorso)
        except PermissionError:
            return

        elementi_validi = []
        for el in elementi:
            full_p = os.path.join(self.percorso, el)
            if os.path.isdir(full_p) and not el.startswith(('.', '__')) and el != '.venv':
                elementi_validi.append((el, full_p, True))
            elif el.endswith((".py", ".json", ".md", ".csv")):
                elementi_validi.append((el, full_p, False))

        elementi_validi.sort(key=lambda x: (not x[2], x[0].lower()))

        num_figli = len(elementi_validi)
        if num_figli == 0:
            return

        offset_y_iniziale = -((num_figli - 1) * 60) / 2
        pos_base = self.scenePos()

        for i, (nome, full_p, is_d) in enumerate(elementi_validi):
            pos_x = pos_base.x() + 240
            pos_y = pos_base.y() + offset_y_iniziale + (i * 60)

            figlio = NodoMindMap(nome, full_p, is_dir=is_d, parent_node=self)
            figlio.setPos(pos_x, pos_y)
            self.scene().addItem(figlio)
            self.child_nodes.append(figlio)

            linea = LineaConnessione()
            self.scene().addItem(linea)
            linea.aggiorna_percorso(pos_base, QPointF(pos_x, pos_y))
            self.linee_connessione.append((linea, figlio))

    def _rimuovi_figli(self):
        for linea, figlio in self.linee_connessione:
            figlio._rimuovi_figli()
            self.scene().removeItem(figlio)
            self.scene().removeItem(linea)
        self.child_nodes.clear()
        self.linee_connessione.clear()

    def setVisible(self, visible):
        """Nasconde o mostra il nodo e la relativa linea di connessione con il genitore."""
        super().setVisible(visible)
        if self.parent_node:
            for linea, child in self.parent_node.linee_connessione:
                if child == self:
                    linea.setVisible(visible and self.parent_node.isVisible())

    def setOpacity(self, opacity):
        """Aggiorna l'opacità del nodo e della relativa linea di connessione."""
        super().setOpacity(opacity)
        if self.parent_node:
            for linea, child in self.parent_node.linee_connessione:
                if child == self:
                    linea.setOpacity(opacity)


class LineaConnessione(QGraphicsPathItem):
    """Linea curva dinamica che collega i nodi della mappa mentale."""
    def __init__(self):
        super().__init__()
        self.setPen(QPen(QColor(148, 163, 184), 2, Qt.PenStyle.DashLine))
        self.setZValue(-1)

    def aggiorna_percorso(self, start_pos: QPointF, end_pos: QPointF):
        path = QPainterPath()
        path.moveTo(start_pos)
        
        dx = end_pos.x() - start_pos.x()
        ctrl1 = QPointF(start_pos.x() + dx * 0.5, start_pos.y())
        ctrl2 = QPointF(end_pos.x() - dx * 0.5, end_pos.y())
        
        path.cubicTo(ctrl1, ctrl2, end_pos)
        self.setPath(path)

