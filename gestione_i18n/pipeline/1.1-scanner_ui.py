import os
import csv
import re

def ottieni_percorso_csv(nome_progetto):
    """Restituisce il percorso del file CSV unificato per il progetto."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dubbi_dir = os.path.join(base_dir, 'dubbi')
    os.makedirs(dubbi_dir, exist_ok=True)
    return os.path.join(dubbi_dir, f"{nome_progetto}.csv")

def carica_decisioni_esistenti(csv_path):
    """Carica lo storico delle decisioni e delle note salvate nel CSV con sanitizzazione."""
    decisioni = {}
    note_esistenti = {}
    righe_esistenti = []
    
    fieldnames_standard = ["stringa", "file_sorgente", "classe", "riga", "da_sostituire", "key", "note"]

    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Normalizzazione e validazione chiavi/campi mancanti
                    for field in fieldnames_standard:
                        if field not in row:
                            row[field] = ''
                            
                    row['classe'] = row['classe'].strip() if row['classe'].strip() else 'A'
                    row['da_sostituire'] = row['da_sostituire'].strip().lower()
                    
                    chiave = (row.get('file_sorgente', '').strip(), row.get('stringa', '').strip())
                    decisioni[chiave] = row.get('da_sostituire', '')
                    note_esistenti[chiave] = row.get('note', '').strip()
                    righe_esistenti.append(row)
        except Exception as e:
            print(f"⚠️ Errore lettura CSV esistente: {e}")
            
    return decisioni, note_esistenti, righe_esistenti

def scansiona_codice(cartella_progetto):
    """
    Scansiona i file .py cercando stringhe all'interno di componenti UI e metodi grafici (whitelist).
    Rileva automaticamente anche le f-string dirottandole in quarantena ('forse').
    """
    stringhe_trovate = []

    target_ui = {
        'QPushButton', 'QLabel', 'QCheckBox', 'QRadioButton', 'QGroupBox',
        'QAction', 'QMenu', 'QTreeWidgetItem', 'QListWidgetItem', 'QTableWidgetItem',
        'QMessageBox', 'QInputDialog', 'QFileDialog', 'QLineEdit', 'QTextEdit', 'QPlainTextEdit',
        'setWindowTitle', 'setToolTip', 'setStatusTip', 'setPlaceholderText',
        'setText', 'setTitle', 'setHeaderLabel', 'setHeaderLabels', 'addAction', 'addMenu'
    }

    pattern_ui_stringa = re.compile(r'\b([a-zA-Z_]\w*)\s*\(\s*([fF]?)(["\'])([^"\n]+)\3')

    for root, _, files in os.walk(cartella_progetto):
        if '.venv' in root or '__pycache__' in root or 'translate_dev' in root:
            continue

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, cartella_progetto)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        in_docstring = False
                        for num_riga, riga in enumerate(f, start=1):
                            riga_stripped = riga.strip()

                            if '"""' in riga_stripped or "'''" in riga_stripped:
                                count_double = riga_stripped.count('"""')
                                count_single = riga_stripped.count("'''")
                                if count_double == 1 or count_single == 1:
                                    in_docstring = not in_docstring
                                continue

                            if in_docstring or riga_stripped.startswith('#'):
                                continue

                            matches = pattern_ui_stringa.findall(riga)
                            for func_name, prefisso, quote, testo in matches:
                                if func_name in target_ui:
                                    # Sanitizzazione rigorosa del testo estratto
                                    testo_clean = testo.strip().replace('\n', ' ')
                                    if testo_clean:
                                        is_fstring = bool(prefisso)
                                        da_sostituire_val = "forse" if is_fstring else ""
                                        nota_val = "f-string" if is_fstring else ""

                                        stringhe_trovate.append({
                                            "stringa": testo_clean,
                                            "file_sorgente": rel_path,
                                            "classe": "A",
                                            "riga": num_riga,
                                            "da_sostituire": da_sostituire_val,
                                            "key": "",
                                            "note": nota_val
                                        })
                except Exception as e:
                    print(f"⚠️ Errore lettura file {file_path}: {e}")

    return stringhe_trovate

def main():
    print("=== PADAS DevStudio - Step 1.1: Scanner UI Classe A (Blindato) ===")

    cartella = input("Inserisci il percorso della cartella da analizzare: ").strip()
    if not cartella or not os.path.exists(cartella):
        print("❌ Errore: Cartella non valida o inesistente.")
        return

    nome_progetto = os.path.basename(os.path.abspath(cartella))
    csv_path = ottieni_percorso_csv(nome_progetto)

    print(f"\n📁 Analisi della cartella: {cartella}")
    print(f"📦 Progetto rilevato: {nome_progetto}")

    decisioni_precedenti, note_precedenti, righe_esistenti = carica_decisioni_esistenti(csv_path)
    stringhe_estratte = scansiona_codice(cartella)

    viste_nel_csv = {(r['file_sorgente'], r['stringa']) for r in righe_esistenti}

    nuove_aggiunte = 0
    final_rows = list(righe_esistenti)

    for item in stringhe_estratte:
        chiave = (item['file_sorgente'], item['stringa'])
        if chiave not in viste_nel_csv:
            da_sost = item['da_sostituire'] if item['da_sostituire'] else decisioni_precedenti.get(chiave, "")
            nota_val = item['note'] if item['note'] else note_precedenti.get(chiave, "")

            final_rows.append({
                "stringa": item['stringa'],
                "file_sorgente": item['file_sorgente'],
                "classe": item['classe'],
                "riga": item['riga'],
                "da_sostituire": da_sost,
                "key": item.get('key', ''),
                "note": nota_val
            })
            viste_nel_csv.add(chiave)
            nuove_aggiunte += 1

    fieldnames = ["stringa", "file_sorgente", "classe", "riga", "da_sostituire", "key", "note"]

    # Scrittura protetta con QUOTE_MINIMAL e newline pulito
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(final_rows)

    print(f"\n✅ Scansione Classe A completata!")
    print(f"📊 Totale righe tracciate nel CSV: {len(final_rows)}")
    print(f"✨ Nuove stringhe UI identificate (Classe A): {nuove_aggiunte}")
    print(f"📂 CSV salvato in: {csv_path}")

if __name__ == "__main__":
    main()