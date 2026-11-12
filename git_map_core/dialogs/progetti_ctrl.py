import os
import csv
from .utils import CSV_PROGETTI


class ProgettiController:
    """Controller dedicato alla logica di I/O CSV, persistenza e gestione dati per i progetti."""
    def __init__(self, manager):
        self.manager = manager
        self.csv_path = os.path.abspath(CSV_PROGETTI)
        self.progetti = []

    def carica_csv(self):
        """Legge i progetti dal file CSV e restituisce la lista."""
        self.progetti = []
        if os.path.exists(self.csv_path):
            try:
                with open(self.csv_path, mode='r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=';')
                    next(reader, None)
                    for riga in reader:
                        if len(riga) >= 2 and riga[0].strip():
                            self.progetti.append({
                                'nome': riga[0].strip(),
                                'percorso': riga[1].strip(),
                                'note': riga[2].strip() if len(riga) > 2 else ''
                            })
            except Exception as e:
                print(f"[ERRORE] Lettura CSV progetti: {e}")
        return self.progetti

    def riscrivi_csv_completo(self):
        """Riscrive integralmente il file CSV con l'elenco aggiornato dei progetti."""
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        with open(self.csv_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['nome_progetto', 'percorso_progetto', 'note'])
            for p in self.progetti:
                writer.writerow([p['nome'], p['percorso'], p['note']])

    def salva_csv(self, nome, percorso, note):
        """Aggiunge o aggiorna un singolo progetto posizionandolo in cima al file CSV (primo della lista)."""
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)

        progetti_filtrati = []
        if os.path.exists(self.csv_path):
            try:
                with open(self.csv_path, mode='r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=';')
                    next(reader, None)
                    for riga in reader:
                        if len(riga) >= 2 and os.path.normpath(riga[1].strip()).lower() != os.path.normpath(percorso).lower():
                            progetti_filtrati.append(riga)
            except Exception:
                pass

        progetti_aggiornati = [[nome, percorso, note]] + progetti_filtrati if 'progetti_filtrati' in locals() else [[nome, percorso, note]] + progetti_filtrati

        with open(self.csv_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['nome_progetto', 'percorso_progetto', 'note'])
            for r in progetti_aggiornati:
                writer.writerow(r)

    def elimina_righe(self, rows):
        """Rimuove le righe specificate dai progetti e aggiorna il CSV."""
        for row in sorted(rows, reverse=True):
            if 0 <= row < len(self.progetti):
                self.progetti.pop(row)
        self.riscrivi_csv_completo()
        return self.progetti

