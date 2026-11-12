import os
import csv
import re

def ottieni_percorso_csv(nome_progetto):
    """Restituisce il percorso del file CSV unificato per il progetto."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dubbi_dir = os.path.join(base_dir, 'dubbi')
    os.makedirs(dubbi_dir, exist_ok=True)
    return os.path.join(dubbi_dir, f"{nome_progetto}.csv")

def carica_chiavi_esistenti(csv_path):
    """Carica l'elenco delle coppie (file_sorgente, stringa) già presenti nel CSV con normalizzazione dello schema."""
    viste = set()
    fieldnames_standard = ["stringa", "file_sorgente", "classe", "riga", "da_sostituire", "key", "note"]
    
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Validazione e compensazione campi mancanti
                    for field in fieldnames_standard:
                        if field not in row:
                            row[field] = ''
                    viste.add((row.get('file_sorgente', '').strip(), row.get('stringa', '').strip()))
        except Exception as e:
            print(f"⚠️ Errore lettura CSV esistente: {e}")
            
    return viste

def scansiona_classe_b(cartella_progetto):
    """
    Scansione Classe B: Mira a strutture dati complesse (liste, tuple, 
    blocchi HTML e stringhe multiriga) e rileva automaticamente le f-string
    dirottandole in quarantena ('forse') con apposita nota.
    """
    stringhe_trovate = []
    pattern_stringhe_generiche = re.compile(r'([fF]?)(["\'])([^"\n\']+)\2')

    for root, _, files in os.walk(cartella_progetto):
        if '.venv' in root or '__pycache__' in root or 'translate_dev' in root:
            continue

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, cartella_progetto)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        contenuto_file = f.read()
                        
                        for num_riga, riga in enumerate(contenuto_file.splitlines(), start=1):
                            riga_stripped = riga.strip()
                            
                            if riga_stripped.startswith('#') or not riga_stripped:
                                continue

                            if any(keyword in rel_path.lower() for keyword in ['dialog', 'view', 'window', 'riepilogo']):
                                matches = pattern_stringhe_generiche.findall(riga)
                                for prefisso, quote, testo in matches:
                                    # Sanitizzazione rigorosa del testo estratto
                                    testo_clean = testo.strip().replace('\n', ' ')
                                    
                                    if len(testo_clean) > 2 and not testo_clean.startswith(('http', 'C:', '/', '\\', '__', '.')):
                                        if not testo_clean.endswith(('.py', '.json', '.csv', '.png', '.txt')):
                                            
                                            is_fstring = bool(prefisso)
                                            da_sostituire_val = "forse" if is_fstring else ""
                                            nota_val = "f-string" if is_fstring else ""

                                            stringhe_trovate.append({
                                                "stringa": testo_clean,
                                                "file_sorgente": rel_path,
                                                "classe": "B",
                                                "riga": num_riga,
                                                "da_sostituire": da_sostituire_val,
                                                "key": "",
                                                "note": nota_val
                                            })
                except Exception as e:
                    print(f"⚠️ Errore lettura file {file_path}: {e}")

    return stringhe_trovate

def main():
    print("=== PADAS DevStudio - Step 1.2: Scanner Classe B (Blindato) ===")

    cartella = input("Inserisci il percorso della cartella del progetto: ").strip()
    if not cartella or not os.path.exists(cartella):
        print("❌ Errore: Cartella non valida o inesistente.")
        return

    nome_progetto = os.path.basename(os.path.abspath(cartella))
    csv_path = ottieni_percorso_csv(nome_progetto)

    print(f"\n📁 Analisi Classe B sulla cartella: {cartella}")
    print(f"📦 Progetto: {nome_progetto}")

    viste_nel_csv = carica_chiavi_esistenti(csv_path)
    stringhe_estratte = scansiona_classe_b(cartella)

    nuove_righe = []
    for item in stringhe_estratte:
        chiave = (item['file_sorgente'], item['stringa'])
        if chiave not in viste_nel_csv:
            nuove_righe.append(item)
            viste_nel_csv.add(chiave)

    file_esiste = os.path.exists(csv_path)
    fieldnames = ["stringa", "file_sorgente", "classe", "riga", "da_sostituire", "key", "note"]

    # Scrittura protetta con QUOTE_MINIMAL e newline pulito
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        
        if not file_esiste:
            writer.writeheader()
            
        writer.writerows(nuove_righe)

    print(f"\n✅ Scansione Classe B completata!")
    print(f"✨ Nuove stringhe aggiunte in coda (Classe B): {len(nuove_righe)}")
    print(f"📂 CSV aggiornato in: {csv_path}")

if __name__ == "__main__":
    main()