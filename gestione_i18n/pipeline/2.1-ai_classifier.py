import os
import csv
import json
from google import genai

# Impostazione batch configurabile
BATCH_SIZE = 50

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
    """Inizializza il client del nuovo SDK e restituisce client e modello predefinito."""
    config = load_ai_config()
    provider = config.get("active_provider", "gemini")
    provider_cfg = config.get("providers", {}).get(provider, {})
    
    api_key = provider_cfg.get("api_key", "")
    default_model = provider_cfg.get("default_model", "models/gemini-2.5-flash")
    
    if not api_key:
        print("❌ Attenzione: Chiave API non trovata in ai_config.json!")
        
    client = genai.Client(api_key=api_key)
    return client, default_model

def genera_chiavi_stringhe(csv_path):
    if not os.path.exists(csv_path):
        print(f"File CSV non trovato: {csv_path}")
        return
        
    df_rows = []
    fieldnames_standard = ["stringa", "file_sorgente", "classe", "riga", "da_sostituire", "key", "note"]
    
    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else fieldnames_standard
        for row in reader:
            for field in fieldnames_standard:
                if field not in row:
                    row[field] = ''
            
            row['classe'] = row['classe'].strip() if row['classe'].strip() else 'A'
            df_rows.append(row)
            
    # Assicurazione rigorosa presenza campi standard nei fieldnames
    for field in fieldnames_standard:
        if field not in fieldnames:
            fieldnames.append(field)
            
    # Filtriamo le stringhe di Classe A che non hanno ancora una chiave generata
    da_processare = [
        r for r in df_rows 
        if r.get('classe', '').upper() == 'A' and not r.get('key', '').strip()
    ]
    
    if not da_processare:
        print("✨ Nessuna stringa di Classe A in sospeso a cui generare la chiave!")
        return
        
    print(f"🚀 Trovate {len(da_processare)} stringhe di Classe A a cui generare le chiavi i18n in batch da {BATCH_SIZE}...")
    client, model_name = get_gemini_client_and_model()
    
    for i in range(0, len(da_processare), BATCH_SIZE):
        batch = da_processare[i:i+BATCH_SIZE]
        print(f"📦 Elaborazione batch {i//BATCH_SIZE + 1} ({len(batch)} elementi)...")
        
        prompt = """Sei un assistente esperto in internazionalizzazione (i18n) di codice Python.
Analizza la seguente lista di stringhe di interfaccia utente (Classe A) estratte dal codice sorgente.

Per ciascuna stringa:
- Proponi una chiave i18n semantica breve, sintetica e pulita in inglese (formato snake_case, es. "sidebar_title", "btn_refresh", "status_modified").
- La chiave deve rispecchiare il significato del testo.

Rispondi ESCLUSIVAMENTE in formato JSON valido, come una lista di oggetti con chiavi "id" (lo stesso ID fornito) e "key".

Elementi da analizzare:
"""
        for idx, item in enumerate(batch):
            prompt += f"ID: {idx} | File: {item['file_sorgente']} | Riga: {item['riga']} | Stringa: {item['stringa']}\n"
            
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
            print(f"✅ JSON decodificato: {len(risultati)} chiavi ricevute dall'IA.")
            
            for res in risultati:
                res_id = res.get("id")
                chiave_generata = res.get("key", "").strip()
                
                if chiave_generata and res_id is not None and res_id < len(batch):
                    target_item = batch[res_id]
                    for r in df_rows:
                        if r['file_sorgente'] == target_item['file_sorgente'] and r['stringa'] == target_item['stringa'] and r['riga'] == target_item['riga']:
                            r['key'] = chiave_generata
                            r['da_sostituire'] = 'si'  # Marchiamo subito come approvato per la sostituzione
                            print(f"  🔹 File: {r['file_sorgente']} | Stringa: '{r['stringa']}' ===> Key: '{chiave_generata}' [SI]")
                            break
                            
        except Exception as e:
            print(f"⚠️ Errore durante l'elaborazione del batch IA: {e}")
            
    # Scrittura protetta con QUOTE_MINIMAL e newline pulito
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(df_rows)
        
    print(f"\n✨ Generazione chiavi completata! Il file CSV è stato aggiornato su {csv_path}.")

if __name__ == "__main__":
    nome_progetto = input("Inserisci il nome del progetto (es. GitMap_Control): ").strip()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'dubbi', f"{nome_progetto}.csv")
    genera_chiavi_stringhe(csv_path)