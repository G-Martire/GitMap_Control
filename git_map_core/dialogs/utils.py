import os
import csv

# Corretto salendo di due livelli per puntare alla cartella principale GitMap_Control/
CSV_PROGETTI = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'progetti_recenti.csv')


def ottieni_ultimo_progetto():
    """Restituisce il percorso dell'ultimo progetto aperto presente in cima a progetti_recenti.csv."""
    csv_path = os.path.abspath(CSV_PROGETTI)
    if os.path.exists(csv_path):
        try:
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                next(reader, None)  # Salta intestazione
                for riga in reader:
                    if len(riga) >= 2 and riga[1].strip():
                        percorso = riga[1].strip()
                        if os.path.exists(percorso):
                            return percorso
        except Exception:
            pass
    return None
