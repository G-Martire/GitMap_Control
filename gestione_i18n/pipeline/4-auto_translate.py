import os
import json
from google import genai

BATCH_SIZE = 100

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

def flatten_json(y):
    out = {}
    def flatten(x, name=''):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + '.')
        else:
            out[name[:-1]] = x
    flatten(y)
    return out

def unflatten_json(d):
    result = {}
    for k, v in d.items():
        parts = k.split('.')
        d_curr = result
        for part in parts[:-1]:
            if part not in d_curr:
                d_curr[part] = {}
            d_curr = d_curr[part]
        d_curr[parts[-1]] = v
    return result

def traduci_chiavi_mancanti(base_flat, target_flat, target_code, target_native_name):
    # Trova le chiavi presenti nel base ma assenti nel target (escludendo 'meta')
    chiavi_da_tradurre = {k: v for k, v in base_flat.items() if k not in target_flat and not k.startswith('meta')}
    
    if not chiavi_da_tradurre:
        print(f"✨ Nessuna nuova chiave da tradurre per la lingua: {target_code.upper()}")
        return target_flat

    print(f"📦 Trovate {len(chiavi_da_tradurre)} chiavi mancanti da tradurre in [{target_native_name} ({target_code})].")
    client, model_name = get_gemini_client_and_model()
    
    items_list = list(chiavi_da_tradurre.items())
    
    for i in range(0, len(items_list), BATCH_SIZE):
        batch = dict(items_list[i:i+BATCH_SIZE])
        print(f"  🚀 Invio batch {i//BATCH_SIZE + 1} ({len(batch)} chiavi) all'IA...")
        
        prompt = f"""Sei un traduttore professionista ed esperto di internazionalizzazione (i18n) software.
Traduci i seguenti testi dalla lingua di origine alla lingua target: {target_native_name} (codice lingua: {target_code}).

Regole fondamentali:
1. Mantieni esattamente le stesse chiavi tecniche (formato JSON/dizionario).
2. Conserva immutati eventuali tag HTML (es. <b>, <i>) ed emoji presenti nel testo originale.
3. Rispondi ESCLUSIVAMENTE in formato JSON valido contenente un oggetto con le coppie chiave-valore tradotte.

Testi da tradurre:
{json.dumps(batch, ensure_ascii=False, indent=2)}
"""
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
            
            traduzioni_batch = json.loads(text)
            for k, v in traduzioni_batch.items():
                if k in base_flat:
                    target_flat[k] = v
            print(f"  ✅ Batch tradotto e integrato con successo.")
            
        except Exception as e:
            print(f"  ⚠️ Errore durante la traduzione del batch: {e}")

    # Gestione o aggiornamento del blocco meta
    if "meta.code" not in target_flat:
        target_flat["meta.code"] = target_code
    if "meta.native_name" not in target_flat:
        target_flat["meta.native_name"] = target_native_name
    if "meta.english_name" not in target_flat:
        target_flat["meta.english_name"] = target_code.capitalize()

    return target_flat

def avvia_processo_traduzione():
    print("=== PADAS DevStudio - Traduttore Multi-Lingua i18n ===")
    
    base_json_path = input("Inserisci il percorso completo del file JSON di origine (es. .../locales/it.json): ").strip()
    
    if not base_json_path or not os.path.exists(base_json_path):
        print(f"❌ Errore: File di origine non trovato o percorso non valido: {base_json_path}")
        return

    language_dir = os.path.dirname(os.path.abspath(base_json_path))
    print(f"📁 Cartella lingue individuata automaticamente: {language_dir}")

    with open(base_json_path, 'r', encoding='utf-8') as f:
        base_data = json.load(f)
    
    base_flat = flatten_json(base_data)

    print("\nScegli la modalità di traduzione:")
    print("  [A] Lingua specifica (es. spagnolo)")
    print("  [B] Tutte le lingue esistenti nel progetto")
    print("  [C] Tutte le lingue esistenti + aggiungine di nuove")
    
    scelta = input("Seleziona modalità (A / B / C): ").strip().upper()

    lingue_da_processare = {}

    if scelta == 'A':
        code = input("Inserisci il codice della lingua target (es. es, fr, de): ").strip().lower()
        name = input("Inserisci il nome nativo della lingua (es. Español, Français): ").strip()
        lingue_da_processare[code] = name
        
    elif scelta in ['B', 'C']:
        for filename in os.listdir(language_dir):
            if filename.endswith(".json"):
                path = os.path.join(language_dir, filename)
                if os.path.abspath(path) != os.path.abspath(base_json_path):
                    with open(path, 'r', encoding='utf-8') as lf:
                        try:
                            ldata = json.load(lf)
                            code = ldata.get("meta", {}).get("code", filename.replace(".json", ""))
                            native = ldata.get("meta", {}).get("native_name", code.capitalize())
                            lingue_da_processare[code] = native
                        except Exception:
                            pass
        if not lingue_da_processare:
            print("⚠️ Nessun'altra lingua trovata nella cartella.")
            
        if scelta == 'C':
            aggiungi_altre = input("Vuoi aggiungere un'altra lingua nuova oltre a queste? (s/n): ").strip().lower()
            while aggiungi_altre == 's':
                code = input("  Codice lingua (es. es): ").strip().lower()
                name = input("  Nome nativo (es. Español): ").strip()
                lingue_da_processare[code] = name
                aggiungi_altre = input("Vuoi aggiungerne un'altra? (s/n): ").strip().lower()
    else:
        print("❌ Scelta non valida.")
        return

    if not lingue_da_processare:
        print("❌ Nessuna lingua selezionata per la traduzione.")
        return

    print(f"\n🌍 Lingue da elaborare: {list(lingue_da_processare.keys())}")

    for code, native_name in lingue_da_processare.items():
        target_path = os.path.join(language_dir, f"{code}.json")
        
        target_data = {}
        if os.path.exists(target_path):
            with open(target_path, 'r', encoding='utf-8') as tf:
                try:
                    target_data = json.load(tf)
                except Exception:
                    target_data = {}
                    
        target_flat = flatten_json(target_data)
        
        updated_flat = traduci_chiavi_mancanti(base_flat, target_flat, code, native_name)
        final_data = unflatten_json(updated_flat)
        
        with open(target_path, 'w', encoding='utf-8') as tf:
            json.dump(final_data, tf, ensure_ascii=False, indent=2)
            
        print(f"✅ File lingua aggiornato salvato con successo: {target_path}\n")

    print("✨ Processo di traduzione multi-lingua completato con successo!")

if __name__ == "__main__":
    avvia_processo_traduzione()