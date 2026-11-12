"""
=============================================================================
PADAS DevStudio - Step 1.4: Classe C (Verifica Manuale Empirica post-processo)
=============================================================================

SPIEGAZIONE E FINALITÀ:
In questo step, il programmatore o chi si occupa del controllo qualità 
verifica "manualmente" che l'interfaccia sia tradotta correttamente e corregge 
eventuali errori residui direttamente nel codice o nei file di localizzazione.

Tale verifica viene effettuata alla fine di tutti gli step precedenti, 
intervenendo solo in una percentuale minima di casi (0-5% della regola 
di Pareto), coprendo eventuali ambiguità contestuali o sfumature che 
l'automazione non poteva cogliere.

Questo file non esegue modifiche automatiche sul codice sorgente, ma funge 
da promemoria operativo e checklist interattiva per l'operatore.
=============================================================================
"""

import os
import csv

def ottieni_percorso_csv(nome_progetto):
    """Restituisce il percorso del file CSV unificato per il progetto."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dubbi_dir = os.path.join(base_dir, 'dubbi')
    os.makedirs(dubbi_dir, exist_ok=True)
    return os.path.join(dubbi_dir, f"{nome_progetto}.csv")

def analizza_residui_classe_c(csv_path):
    """Analizza il CSV in modo blindato alla ricerca di elementi in sospeso o marcati come 'FORSE' / non definiti, tracciando anche le note."""
    if not os.path.exists(csv_path):
        print(f"❌ File CSV non trovato: {csv_path}")
        return

    totale_righe = 0
    in_sospeso = 0
    forse_count = 0
    fstring_count = 0
    
    fieldnames_standard = ["stringa", "file_sorgente", "classe", "riga", "da_sostituire", "key", "note"]

    try:
        with open(csv_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                totale_righe += 1
                
                # Normalizzazione e compensazione campi
                for field in fieldnames_standard:
                    if field not in row:
                        row[field] = ''
                        
                decisione = row.get('da_sostituire', '').strip().lower()
                nota = row.get('note', '').strip().lower()

                if not decisione or decisione == '':
                    in_sospeso += 1
                elif decisione == 'forse':
                    forse_count += 1
                    if 'f-string' in nota:
                        fstring_count += 1
    except Exception as e:
        print(f"❌ Errore nella lettura del CSV: {e}")
        return

    print("\n" + "="*70)
    print("📋 [CHECKLIST CLASSE C] - STATO FINALE DEL PROGETTO")
    print("="*70)
    print(f"📊 Totale elementi tracciati nel CSV: {totale_righe}")
    print(f"⚠️ Elementi non ancora processati o in sospeso: {in_sospeso}")
    print(f"❓ Elementi marcati come 'FORSE': {forse_count}")
    if fstring_count > 0:
        print(f"   🔒 Di cui f-string protette in quarantena: {fstring_count}")
    print("-"*70)
    
    if in_sospeso == 0 and forse_count == 0:
        print("✨ Ottimo! Non risultano elementi in sospeso o dubbi.")
        print("   La Classe C residua (0-5%) è pronta per la verifica empirica finale a schermo.")
    else:
        print("💡 Suggerimento: Controlla nel CSV le righe senza decisione o con 'forse'")
        print("   per completare la rifinitura manuale prima del deploy definitivo.")
    print("="*70 + "\n")

def main():
    print("=== PADAS DevStudio - Step 1.4: Gestione Classe C (Blindato) ===")

    nome_progetto = input("Inserisci il nome del progetto (es. GitMap_Control): ").strip()
    if not nome_progetto:
        print("❌ Nome progetto non valido.")
        return

    csv_path = ottieni_percorso_csv(nome_progetto)
    analizza_residui_classe_c(csv_path)

    print("ℹ️ Ricorda la regola di Pareto:")
    print("   - L'80-90% del lavoro pesante è stato fatto dai moduli automatici (Classe A e B).")
    print("   - Il 0-5% richiede questo controllo umano mirato (Classe C).")

if __name__ == "__main__":
    main()