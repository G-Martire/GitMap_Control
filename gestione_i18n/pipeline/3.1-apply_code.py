import os
import csv
import shutil
import re

def pulisci_chiave_fallback(testo):
    """Genera una chiave snake_case di ripiego se la chiave CSV è vuota."""
    testo_pulito = re.sub(r'[^\w\s]', '', testo, flags=re.UNICODE)
    chiave = re.sub(r'\s+', '_', testo_pulito.strip()).lower()
    return chiave if chiave else "stringa_generica"

def ottieni_percorsi_progetto(cartella_progetto):
    """Calcola i percorsi necessari per CSV e file di configurazione."""
    nome_progetto = os.path.basename(os.path.abspath(cartella_progetto))
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'dubbi', f"{nome_progetto}.csv")
    return nome_progetto, csv_path

def verifica_sintassi_file(file_path):
    """Verifica se il file Python compila correttamente senza errori di sintassi."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            codice = f.read()
        compile(codice, file_path, 'exec')
        return True, ""
    except Exception as e:
        return False, str(e)

def applica_sostituzioni_codice(nome_progetto, cartella_progetto):
    """
    Sostituzione codice (Classe A):
    1. Backup preventivo dei file coinvolti in 'backup_sorgenti/'.
    2. Sostituzione testuale dal basso verso l'alto usando le chiavi semantiche del CSV.
    3. Controllo sintattico post-modifica.
    4. Rollback automatico dal backup in caso di errore di sintassi.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'dubbi', f"{nome_progetto}.csv")
    report_txt_path = os.path.join(base_dir, 'dubbi', 'i18n_pipeline_report.txt')
    backup_dir = os.path.join(base_dir, 'backup_sorgenti')

    def scrivi_log(messaggio):
        os.makedirs(os.path.dirname(report_txt_path), exist_ok=True)
        with open(report_txt_path, 'a', encoding='utf-8') as log_f:
            log_f.write(f"[APPLY CODE] {messaggio}\n")
        print(messaggio)

    if not os.path.exists(csv_path):
        scrivi_log(f"❌ Errore: File CSV non trovato in: {csv_path}")
        return

    df_rows = []
    fieldnames_standard = ["stringa", "file_sorgente", "classe", "riga", "da_sostituire", "key", "note"]
    fieldnames = []

    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else fieldnames_standard
        for row in reader:
            for field in fieldnames_standard:
                if field not in row:
                    row[field] = ''
            df_rows.append(row)

    for field in fieldnames_standard:
        if field not in fieldnames:
            fieldnames.append(field)

    stringhe_da_applicare = [
        r for r in df_rows 
        if r.get('da_sostituire', '').strip().lower() == 'si'
    ]

    if not stringhe_da_applicare:
        scrivi_log("✨ Nessuna stringa approvata con 'si' trovata nel CSV!")
        return

    scrivi_log(f"📦 Trovate {len(stringhe_da_applicare)} stringhe da sostituire nel codice.")

    sostituzioni_per_file = {}
    for item in stringhe_da_applicare:
        rel_path = item['file_sorgente']
        if rel_path not in sostituzioni_per_file:
            sostituzioni_per_file[rel_path] = []
        sostituzioni_per_file[rel_path].append(item)

    os.makedirs(backup_dir, exist_ok=True)
    scrivi_log(f"🛡️ Creazione backup preventivo in: {backup_dir}")
    
    for rel_path in sostituzioni_per_file.keys():
        abs_path = os.path.join(cartella_progetto, rel_path)
        if os.path.exists(abs_path):
            backup_dest = os.path.join(backup_dir, rel_path.replace('/', '_').replace('\\', '_'))
            shutil.copy2(abs_path, backup_dest)

    sostituzioni_effettuate = 0
    file_falliti = set()

    for rel_path, elementi in sostituzioni_per_file.items():
        abs_path = os.path.join(cartella_progetto, rel_path)
        if not os.path.exists(abs_path):
            scrivi_log(f"⚠️ File sorgente non trovato: {abs_path}")
            continue

        with open(abs_path, 'r', encoding='utf-8') as f:
            righe = f.readlines()

        elementi_ordinati = sorted(elementi, key=lambda x: int(x['riga']), reverse=True)

        modificato = False
        for item in elementi_ordinati:
            stringa_orig = item['stringa']
            chiave_csv = item.get('key', '').strip()
            if not chiave_csv:
                chiave_csv = pulisci_chiave_fallback(stringa_orig)
            
            # Utilizziamo direttamente la chiave semantica pulita dal CSV
            chiave_i18n = chiave_csv
            riga_num = int(item['riga']) - 1

            if 0 <= riga_num < len(righe):
                riga_testo = righe[riga_num]
                if f'"{stringa_orig}"' in riga_testo:
                    righe[riga_num] = riga_testo.replace(f'"{stringa_orig}"', f'self.i18n.t("{chiave_i18n}")')
                    modificato = True
                    sostituzioni_effettuate += 1
                elif f"'{stringa_orig}'" in riga_testo:
                    righe[riga_num] = riga_testo.replace(f"'{stringa_orig}'", f'self.i18n.t("{chiave_i18n}")')
                    modificato = True
                    sostituzioni_effettuate += 1

        if modificato:
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.writelines(righe)

            is_valido, err_msg = verifica_sintassi_file(abs_path)
            if not is_valido:
                scrivi_log(f"❌ Errore di sintassi in {rel_path}: {err_msg}")
                scrivi_log(f"🔄 ROLLBACK automatico attivato per: {rel_path}")
                
                backup_dest = os.path.join(backup_dir, rel_path.replace('/', '_').replace('\\', '_'))
                if os.path.exists(backup_dest):
                    shutil.copy2(backup_dest, abs_path)
                
                file_falliti.add(rel_path)
            else:
                scrivi_log(f"  📝 File aggiornato e validato con successo: {rel_path}")

    if file_falliti:
        scrivi_log(f"🧹 Declassamento voci nel CSV per i {len(file_falliti)} file ripristinati...")
        for row in df_rows:
            if row.get('file_sorgente') in file_falliti and row.get('da_sostituire', '').strip().lower() == 'si':
                row['da_sostituire'] = 'forse'
                row['note'] = 'Rollback per errore di sintassi post-sostituzione'

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(df_rows)

    scrivi_log(f"✨ Sostituzione codice completata. Sostituzioni effettuate: {sostituzioni_effettuate}. File ripristinati: {len(file_falliti)}.")

def main():
    print("=== PADAS DevStudio - Sostituzione & Validazione Codice (Classe A) ===")
    cartella = input("Inserisci il percorso della cartella del progetto: ").strip()
    if not cartella or not os.path.exists(cartella):
        print("❌ Errore: Cartella del progetto non valida.")
        return

    nome_progetto, csv_path = ottieni_percorsi_progetto(cartella)
    applica_sostituzioni_codice(nome_progetto, cartella)

if __name__ == "__main__":
    main()