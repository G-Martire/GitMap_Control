import os
import csv
import json
import re

def ottieni_percorso_csv(nome_progetto):
    """Restituisce il percorso del file CSV unificato per il progetto."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dubbi_dir = os.path.join(base_dir, 'dubbi')
    os.makedirs(dubbi_dir, exist_ok=True)
    return os.path.join(dubbi_dir, f"{nome_progetto}.csv")

def patch_init_progetto(nome_progetto, cartella_progetto):
    """
    Step 2.4/3.3 (Blindato): Esegue l'auto-patching mirato dei costruttori __init__ 
    escludendo file grafici strutturali (es. nodes.py) dove 'parent' non è definito.
    Chiede all'utente tramite terminale se includere anche gli elementi 'FORSE'.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = ottieni_percorso_csv(nome_progetto)
    report_txt_path = os.path.join(base_dir, 'dubbi', 'i18n_pipeline_report.txt')
    
    def scrivi_log(messaggio):
        os.makedirs(os.path.dirname(report_txt_path), exist_ok=True)
        with open(report_txt_path, 'a', encoding='utf-8') as log_f:
            log_f.write(f"[STEP 3.3 - PATCH INIT] {messaggio}\n")
        print(messaggio)

    if not os.path.exists(csv_path):
        scrivi_log(f"❌ Errore: File CSV non trovato in: {csv_path}")
        return

    # --- ANALISI INIZIALE E CONTEGGIO STATI (Blindato) ---
    conteggio_stati = {'si': 0, 'no': 0, 'forse': 0, 'in_sospeso': 0}
    file_per_stato = {'si': set(), 'forse': set()}
    fieldnames_standard = ["stringa", "file_sorgente", "classe", "riga", "da_sostituire", "key", "note"]

    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in fieldnames_standard:
                if field not in row:
                    row[field] = ''
                
            rel_p = row.get('file_sorgente', '').strip()
            dec = row.get('da_sostituire', '').strip().lower()
            
            if dec in conteggio_stati:
                conteggio_stati[dec] += 1
            else:
                conteggio_stati['in_sospeso'] += 1

            if rel_p:
                if dec == 'si':
                    file_per_stato['si'].add(rel_p)
                elif dec == 'forse':
                    file_per_stato['forse'].add(rel_p)

    print("\n" + "="*70)
    print("❓ CONFIGURAZIONE AUTO-PATCHING COSTRUTTORI __INIT__ (Blindato)")
    print("="*70)
    print(f"📊 Stringhe approvate ('SI'): {conteggio_stati['si']} (in {len(file_per_stato['si'])} file)")
    print(f"❓ Stringhe in dubbi/quarantena ('FORSE'): {conteggio_stati['forse']} (in {len(file_per_stato['forse'])} file)")
    print("-"*70)

    # --- DOMANDA INTERATTIVA ALL'UTENTE ---
    risposta = input("👉 Vuoi applicare la patch del codice anche ai file contenenti elementi 'FORSE' (Classe C)? (s/N): ").strip().lower()
    includi_forse = risposta in ['s', 'si', 'y', 'yes']

    if includi_forse:
        decisioni_valide = {'si', 'forse'}
        scrivi_log("⚠️ ATTENZIONE: Modalità estesa attivata. Inclusi file con elementi 'SI' e 'FORSE'.")
    else:
        decisioni_valide = {'si'}
        scrivi_log("🛡️ Modalità prudente (default): Inclusi SOLO file con decisioni 'SI'. I 'FORSE' rimangono esclusi.")

    # --- COSTRUZIONE WHITELIST DEFINITIVA DEI FILE (Blindato) ---
    file_whitelisted = set()
    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in fieldnames_standard:
                if field not in row:
                    row[field] = ''
            rel_p = row.get('file_sorgente', '').strip()
            dec = row.get('da_sostituire', '').strip().lower()
            if rel_p and dec in decisioni_valide:
                file_whitelisted.add(rel_p)

    if not file_whitelisted:
        scrivi_log("✨ Nessun file risponde ai criteri di whitelist selezionati per l'auto-patching.")
        return

    scrivi_log(f"\n🔍 Avvio auto-patching __init__ su {len(file_whitelisted)} file target...")
    
    report_autopatch = []
    interventi_effettuati = 0

    for rel_path in file_whitelisted:
        if 'nodes.py' in rel_path.lower() or 'graphics' in rel_path.lower():
            scrivi_log(f"  🛡️ Saltato file protetto/grafico per evitare NameError: {rel_path}")
            continue

        abs_path = os.path.join(cartella_progetto, rel_path)
        if not os.path.exists(abs_path):
            scrivi_log(f"⚠️ File sorgente non trovato: {abs_path}")
            continue
        
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if 'self.i18n' in content and 'self.i18n =' not in content:
                pattern_super = r'(super\s*\([^)]*\)\s*\.__init__\s*\([^)]*\))'
                if re.search(pattern_super, content):
                    def replacer(match):
                        super_call = match.group(1)
                        return f"{super_call}\n        self.i18n = getattr(parent, 'i18n', None)"
                    
                    new_content = re.sub(pattern_super, replacer, content, count=1)
                    if new_content != content:
                        with open(abs_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        report_autopatch.append({
                            "file": rel_path,
                            "stato": "Successo",
                            "dettaglio": "Iniettato self.i18n = getattr(parent, 'i18n', None) nel costruttore"
                        })
                        scrivi_log(f"  🔧 Auto-patch __init__ applicato a: {rel_path}")
                        interventi_effettuati += 1
        except Exception as e:
            scrivi_log(f"  ⚠️ Errore patch su {rel_path}: {e}")

    report_dir = os.path.join(base_dir, 'dubbi')
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"{nome_progetto}_autopatch_report.json")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "progetto": nome_progetto,
            "totale_interventi": interventi_effettuati,
            "inclusione_forse_attivata": includi_forse,
            "interventi_autopatch": report_autopatch
        }, f, ensure_ascii=False, indent=2)
    
    scrivi_log(f"\n✨ Step completato! Interventi eseguiti: {interventi_effettuati}")

def main():
    print("=== PADAS DevStudio - Auto-Patching Costruttori __init__ (Blindato) ===")
    
    cartella = input("Inserisci il percorso della cartella del progetto: ").strip()
    if not cartella or not os.path.exists(cartella):
        print("❌ Errore: Cartella del progetto non valida o non trovata.")
        return

    nome_progetto = os.path.basename(os.path.abspath(cartella))
    patch_init_progetto(nome_progetto, cartella)

if __name__ == "__main__":
    main()