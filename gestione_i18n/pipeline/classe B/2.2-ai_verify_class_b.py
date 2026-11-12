import os
import csv
import json
from google import genai

def load_ai_config():
    """Carica la configurazione globale dell'IA dal file ai_config.json nella root del progetto."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, '..', 'ai_config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Errore di lettura in ai_config.json: {e}")
    return {}

def get_gemini_client_and_model():
    """Inizializza il client del nuovo SDK utilizzando il modello configurato."""
    config = load_ai_config()
    provider = config.get("active_provider", "gemini")
    provider_cfg = config.get("providers", {}).get(provider, {})
    
    api_key = provider_cfg.get("api_key", "")
    default_model = provider_cfg.get("default_model", "models/gemini-2.5-flash")
    
    if not api_key:
        print("❌ Attenzione: Chiave API non trovata in ai_config.json!")
        
    client = genai.Client(api_key=api_key)
    print(f"🤖 Modello IA attivato: {default_model}")
    return client, default_model

def ottieni_percorso_csv(nome_progetto):
    """Restituisce il percorso del file CSV unificato per il progetto."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dubbi_dir = os.path.join(base_dir, 'dubbi')
    os.makedirs(dubbi_dir, exist_ok=True)
    return os.path.join(dubbi_dir, f"{nome_progetto}.csv")

def verifica_classe_b_con_ia_csv_puro(csv_path):
    if not os.path.exists(csv_path):
        print(f"❌ File CSV non trovato: {csv_path}")
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
            row['classe'] = row['classe'].strip() if row['classe'].strip() else 'A'
            row['da_sostituire'] = row['da_sostituire'].strip().lower()
            df_rows.append(row)

    for field in fieldnames_standard:
        if field not in fieldnames:
            fieldnames.append(field)

    da_verificare = [
        r for r in df_rows 
        if r.get('classe', '').strip().upper() == 'B' 
        and r.get('da_sostituire', '') == 'si'
    ]

    if not da_verificare:
        print("✨ Nessuna stringa di Classe B con decisione 'SI' da verificare.")
        return

    print(f"🚀 Trovate {len(da_verificare)} stringhe di Classe B ('SI') da verificare (le altre classi nel CSV saranno preservate).")
    client, model_name = get_gemini_client_and_model()

    batch_size = 50
    for i in range(0, len(da_verificare), batch_size):
        batch = da_verificare[i:i + batch_size]
        print(f"\n📦 Invio batch di verifica ({i + 1} - {i + len(batch)} di {len(da_verificare)})...")

        prompt = f"""Sei un system architect ed esperto senior in internazionalizzazione (i18n) di software PyQt/Python.
Ti viene fornita una lista tabulare di stringhe estratte dal codice (Classe B) che erano state classificate come da tradurre ("SI").

Il tuo compito è analizzare con estrema cura il testo, il file di origine e il numero di riga applicando questa logica di giudizio:
1. "SI": Se sei assolutamente certo che sia un testo di interfaccia utente (UI) visibile all'utente finale da tradurre.
2. "NO": Se si tratta di un falso positivo sicuro, frammenti tecnici, stili CSS puri, chiavi di dizionario o logica interna.
3. "FORSE": **Fallo frequentemente se hai il minimo dubbio**, se la stringa è ambigua, se potrebbe essere un log tecnico ma anche un'etichetta, o se non sei al 100% sicuro. Usare "FORSE" ci aiuta a concentrare il controllo manuale di qualità dove serve.
4. Fornisci o conferma la chiave i18n semantica (`key`) in inglese snake_case (obbligatoria se "SI" o "FORSE").

Rispondi ESCLUSIVAMENTE in formato JSON valido come una lista di oggetti, ciascuno con chiavi:
- "stringa": il testo esatto della stringa
- "file_sorgente": il file di origine
- "riga": il numero di riga
- "decisione": "SI", "NO" oppure "FORSE"
- "key": la chiave i18n semantica se "SI" o "FORSE", altrimenti stringa vuota ""

Elementi da verificare in questo batch:
"""
        for item in batch:
            prompt += f"- File: {item['file_sorgente']} | Riga: {item['riga']} | Stringa: '{item['stringa']}' | Key attuale: '{item.get('key', '')}'\n"

        prompt += "\nRestituisci solo il JSON array valido racchiuso in ```json ... ```."

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            text = response.text.strip()
            
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            risultati = json.loads(text)
            print(f"  ✅ Ricevute {len(risultati)} risposte dall'IA.")

            for res in risultati:
                res_str = res.get("stringa", "").strip()
                res_file = res.get("file_sorgente", "").strip()
                res_riga = str(res.get("riga", ""))
                nuova_decisione = res.get("decisione", "").strip().upper()
                nuova_key = res.get("key", "").strip()

                if nuova_decisione in ["SI", "NO", "FORSE"]:
                    for r in df_rows:
                        if (r.get('classe', '').strip().upper() == 'B' and
                            r.get('file_sorgente', '').strip() == res_file and 
                            r.get('stringa', '').strip() == res_str and 
                            str(r.get('riga', '')).strip() == res_riga):
                            
                            r['da_sostituire'] = nuova_decisione.lower()
                            
                            if nuova_decisione in ["SI", "FORSE"] and nuova_key:
                                r['key'] = nuova_key
                            elif nuova_decisione == "NO":
                                r['key'] = ""
                                
                            print(f"    🔹 [{res_file} : Riga {res_riga}] '{res_str[:25]}...' -> **{nuova_decisione}** (Key: '{r.get('key','')}')")
                            break

        except Exception as e:
            print(f"⚠️ Errore durante la chiamata IA per il batch: {e}")

    # Scrittura protetta con QUOTE_MINIMAL e newline pulito
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(df_rows)

    print(f"\n✨ Salvataggio completato! Tutte le classi e gli step nel CSV sono stati preservati. File aggiornato: {csv_path}")

def main():
    print("=== PADAS DevStudio - Step 1.4: Verifica IA (Blindato) ===")

    nome_progetto = input("Inserisci il nome del progetto (es. GitMap_Control): ").strip()
    if not nome_progetto:
        print("❌ Nome progetto non valido.")
        return

    csv_path = ottieni_percorso_csv(nome_progetto)
    verifica_classe_b_con_ia_csv_puro(csv_path)

if __name__ == "__main__":
    main()


