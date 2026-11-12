import os
import csv
import json
import re

def pulisci_chiave_fallback(testo):
    """Genera una chiave snake_case di ripiego se la chiave CSV è vuota."""
    testo_pulito = re.sub(r'[^\w\s]', '', testo, flags=re.UNICODE)
    chiave = re.sub(r'\s+', '_', testo_pulito.strip()).lower()
    return chiave if chiave else "stringa_generica"

def ottieni_percorsi_progetto(cartella_progetto):
    """Calcola i percorsi necessari per CSV e JSON principale."""
    nome_progetto = os.path.basename(os.path.abspath(cartella_progetto))
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'dubbi', f"{nome_progetto}.csv")
    lingua_json_path = os.path.join(cartella_progetto, 'locales', 'it.json')
    return nome_progetto, csv_path, lingua_json_path

def aggiorna_json_principale(nome_progetto, lingua_json_path):
    """
    Aggiorna il file JSON principale registrando le chiavi approvate ('si') 
    e scrivendo sul log unificato, usando direttamente le chiavi semantiche generate dall'IA.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'dubbi', f"{nome_progetto}.csv")
    report_txt_path = os.path.join(base_dir, 'dubbi', 'i18n_pipeline_report.txt')

    def scrivi_log(messaggio):
        os.makedirs(os.path.dirname(report_txt_path), exist_ok=True)
        with open(report_txt_path, 'a', encoding='utf-8') as log_f:
            log_f.write(f"[UPDATE JSON] {messaggio}\n")
        print(messaggio)

    if not os.path.exists(csv_path):
        scrivi_log(f"❌ Errore: File CSV non trovato in: {csv_path}")
        return

    if not os.path.exists(lingua_json_path):
        scrivi_log(f"❌ Errore: File JSON lingua non trovato in: {lingua_json_path}")
        return

    # Lettura blindata del CSV con compensazione schema campi
    stringhe_da_applicare = []
    fieldnames_standard = ["stringa", "file_sorgente", "classe", "riga", "da_sostituire", "key", "note"]

    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in fieldnames_standard:
                if field not in row:
                    row[field] = ''
            
            # Filtro rigoroso: prende SOLO le stringhe approvate con 'si'.
            if row.get('da_sostituire', '').strip().lower() == 'si':
                stringhe_da_applicare.append(row)

    if not stringhe_da_applicare:
        scrivi_log("✨ Nessuna stringa approvata con 'si' trovata nel CSV!")
        return

    scrivi_log(f"📦 Trovate {len(stringhe_da_applicare)} stringhe approvate per l'aggiornamento JSON.")

    with open(lingua_json_path, 'r', encoding='utf-8') as f:
        dati_json = json.load(f)

    # Se non esiste una struttura a sezioni, inseriamo direttamente nella root o gestiamo dizionari piatti
    chiave_mappate_count = 0
    for item in stringhe_da_applicare:
        stringa_orig = item['stringa']
        chiave_csv = item.get('key', '').strip()
        if not chiave_csv:
            chiave_csv = pulisci_chiave_fallback(stringa_orig)

        # Gestione duplicati della chiave nello stesso JSON
        idx = 1
        chiave_univoca = chiave_csv
        while chiave_univoca in dati_json and dati_json[chiave_univoca] != stringa_orig:
            chiave_univoca = f"{chiave_csv}_{idx}"
            idx += 1

        dati_json[chiave_univoca] = stringa_orig
        chiave_mappate_count += 1

    with open(lingua_json_path, 'w', encoding='utf-8') as f:
        json.dump(dati_json, f, ensure_ascii=False, indent=2)
        
    scrivi_log(f"✅ File JSON principale aggiornato con successo: {lingua_json_path} (Inserite: {chiave_mappate_count} chiavi)")

def main():
    print("=== PADAS DevStudio - Aggiornamento JSON Principale (Classe A) ===")
    cartella = input("Inserisci il percorso della cartella del progetto: ").strip()
    if not cartella or not os.path.exists(cartella):
        print("❌ Errore: Cartella del progetto non valida.")
        return

    nome_progetto, csv_path, lingua_json_path = ottieni_percorsi_progetto(cartella)
    aggiorna_json_principale(nome_progetto, lingua_json_path)

if __name__ == "__main__":
    main()