import os
import json
import csv

def ottieni_percorso_csv(nome_progetto):
    """Restituisce il percorso del file CSV unificato per il progetto."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dubbi_dir = os.path.join(base_dir, 'dubbi')
    os.makedirs(dubbi_dir, exist_ok=True)
    return os.path.join(dubbi_dir, f"{nome_progetto}.csv")

def carica_chiavi_json_principale(locales_dir, nome_json="it.json"):
    """
    Carica tutte le chiavi (inclusi i namespace nidificati convertiti in dot-notation)
    presenti nel file JSON di riferimento principale.
    """
    json_path = os.path.join(locales_dir, nome_json)
    chiavi_tradotte = set()
    
    if not os.path.exists(json_path):
        print(f"⚠️ Attenzione: File JSON di riferimento non trovato in {json_path}")
        return chiavi_tradotte

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            dati_json = json.load(f)
            
            def _appiattisci(nodo, prefisso=""):
                if isinstance(nodo, dict):
                    for k, v in nodo.items():
                        nuovo_prefisso = f"{prefisso}.{k}" if prefisso else k
                        _appiattisci(v, nuovo_prefisso)
                elif isinstance(nodo, str):
                    chiavi_tradotte.add(prefisso.strip())
                    chiavi_tradotte.add(nodo.strip())
                    
            _appiattisci(dati_json)
            print(f"📖 Caricate {len(chiavi_tradotte)} chiavi/valori di riscontro dal JSON principale ({nome_json}).")
    except Exception as e:
        print(f"❌ Errore durante la lettura del file JSON: {e}")
        
    return chiavi_tradotte

def pulisci_csv_gia_tradotti(csv_path, chiavi_escluse):
    """
    Legge il CSV in modo blindato, individua le righe già presenti nel JSON ed elimina 
    procedendo dal basso verso l'alto (in ordine inverso) per evitare sfasamenti,
    preservando rigorosamente la colonna 'note'.
    """
    if not os.path.exists(csv_path):
        print(f"❌ File CSV non trovato: {csv_path}")
        return

    righe = []
    fieldnames_standard = ["stringa", "file_sorgente", "classe", "riga", "da_sostituire", "key", "note"]
    fieldnames = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else fieldnames_standard
            for row in reader:
                for field in fieldnames_standard:
                    if field not in row:
                        row[field] = ''
                righe.append(row)
    except Exception as e:
        print(f"❌ Errore nella lettura del CSV: {e}")
        return

    righe_rimaste = []
    eliminate_count = 0

    for row in reversed(righe):
        stringa = row.get('stringa', '').strip()
        chiave_gia_esistente = row.get('key', '').strip()
        
        is_gia_tradotta = (stringa in chiavi_escluse) or (chiave_gia_esistente in chiavi_escluse)
        
        if is_gia_tradotta:
            eliminate_count += 1
            print(f"  🗑️ Rimossa chiave già tradotta/presente: '{stringa[:40]}...' (Key: {chiave_gia_esistente})")
        else:
            righe_rimaste.append(row)

    righe_rimaste.reverse()

    if not fieldnames:
        fieldnames = fieldnames_standard
    elif "note" not in fieldnames:
        fieldnames.append("note")

    # Scrittura protetta con QUOTE_MINIMAL e newline pulito
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(righe_rimaste)

    print(f"\n✅ Pulizia completata con successo!")
    print(f"📊 Righe iniziali nel CSV: {len(righe)}")
    print(f"🗑️ Righe duplicate/già tradotte eliminate: {eliminate_count}")
    print(f"✨ Righe rimaste in sospeso: {len(righe_rimaste)}")
    print(f"📂 CSV aggiornato: {csv_path}")

def main():
    print("=== PADAS DevStudio - Step 1.3: Pulizia Preventiva CSV (Blindato) ===")

    nome_progetto = input("Inserisci il nome del progetto (es. GitMap_Control): ").strip()
    if not nome_progetto:
        print("❌ Nome progetto non valido.")
        return

    csv_path = ottieni_percorso_csv(nome_progetto)

    locales_dir = input("Inserisci il percorso della cartella 'locales' (es. .../locales): ").strip()
    if not locales_dir or not os.path.exists(locales_dir):
        print("⚠️ Cartella locales non specificata o inesistente. Salto il filtro JSON.")
        return

    nome_json = input("Nome del file JSON principale [default: it.json]: ").strip()
    if not nome_json:
        nome_json = "it.json"

    print(f"\n🔍 Avvio confronto tra CSV e file JSON ({nome_json})...")
    chiavi_escluse = carica_chiavi_json_principale(locales_dir, nome_json)
    
    if chiavi_escluse:
        pulisci_csv_gia_tradotti(csv_path, chiavi_escluse)
    else:
        print("✨ Nessuna chiave trovata nel JSON di riferimento. Il CSV rimane invariato.")

if __name__ == "__main__":
    main()