import os
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


# Caricamento configurazione e inizializzazione del client
config = load_ai_config()
provider = config.get("active_provider", "gemini")
provider_cfg = config.get("providers", {}).get(provider, {})
api_key = provider_cfg.get("api_key", "")

if not api_key:
    print("❌ Attenzione: Chiave API non trovata in ai_config.json!")

# Inizializzazione corretta con il nuovo SDK
client = genai.Client(api_key=api_key)

print("🔍 Interrogazione dei modelli disponibili per la tua chiave API...\n")

try:
    for m in client.models.list():
        print(f"✅ Modello disponibile: {m.name}")
except Exception as e:
    print(f"❌ Errore durante il recupero dei modelli: {e}")


"""
🔍 Interrogazione dei modelli disponibili per la tua chiave API...

✅ Modello disponibile: models/gemini-2.5-flash
✅ Modello disponibile: models/gemini-2.5-pro
✅ Modello disponibile: models/gemini-2.5-flash-preview-tts
✅ Modello disponibile: models/gemini-2.5-pro-preview-tts
✅ Modello disponibile: models/gemma-4-26b-a4b-it
✅ Modello disponibile: models/gemma-4-31b-it
✅ Modello disponibile: models/gemini-flash-latest
✅ Modello disponibile: models/gemini-flash-lite-latest
✅ Modello disponibile: models/gemini-pro-latest
✅ Modello disponibile: models/gemini-2.5-flash-lite
✅ Modello disponibile: models/gemini-2.5-flash-image
✅ Modello disponibile: models/gemini-3-flash-preview
✅ Modello disponibile: models/gemini-3.1-pro-preview
✅ Modello disponibile: models/gemini-3.1-pro-preview-customtools
✅ Modello disponibile: models/gemini-3.1-flash-lite-preview
✅ Modello disponibile: models/gemini-3.1-flash-lite
✅ Modello disponibile: models/gemini-3-pro-image-preview
✅ Modello disponibile: models/gemini-3-pro-image
✅ Modello disponibile: models/nano-banana-pro-preview
✅ Modello disponibile: models/gemini-3.1-flash-image-preview
✅ Modello disponibile: models/gemini-3.1-flash-image
✅ Modello disponibile: models/gemini-3.1-flash-lite-image
✅ Modello disponibile: models/gemini-nano-banana-2.1
✅ Modello disponibile: models/gemini-3.5-flash
✅ Modello disponibile: models/gemini-3.5-flash-lite
✅ Modello disponibile: models/gemini-omni-flash-preview
✅ Modello disponibile: models/gemini-omni-1.1-flash
✅ Modello disponibile: models/gemini-omni-1.2-flash
✅ Modello disponibile: models/gemini-3.5-transcribe
✅ Modello disponibile: models/gemini-3.6-flash
✅ Modello disponibile: models/gemini-3.7-flash
✅ Modello disponibile: models/gemini-3.8-flash
✅ Modello disponibile: models/gemini-4-argon
✅ Modello disponibile: models/lyria-3-clip-preview
✅ Modello disponibile: models/lyria-3-pro-preview
✅ Modello disponibile: models/lyria-3.5
✅ Modello disponibile: models/gemini-3.1-flash-tts-preview
✅ Modello disponibile: models/gemini-3.8-flash-tts
✅ Modello disponibile: models/gemini-3.8-flash-lite-tts
✅ Modello disponibile: models/gemini-robotics-er-2-preview
✅ Modello disponibile: models/gemini-2.5-computer-use-preview-10-2025
✅ Modello disponibile: models/antigravity-preview-05-2026
✅ Modello disponibile: models/antigravity-preview-09-2026
✅ Modello disponibile: models/antigravity-preview-latest
✅ Modello disponibile: models/deep-research-max-preview-04-2026
✅ Modello disponibile: models/deep-research-preview-04-2026
✅ Modello disponibile: models/deep-research-pro-preview-12-2025
✅ Modello disponibile: models/gemini-embedding-001
✅ Modello disponibile: models/gemini-embedding-2-preview
✅ Modello disponibile: models/gemini-embedding-2
✅ Modello disponibile: models/aqa
✅ Modello disponibile: models/gemini-3.5-transcribe-live
✅ Modello disponibile: models/gemini-2.5-flash-native-audio-latest
✅ Modello disponibile: models/gemini-2.5-flash-native-audio-preview-09-2025
✅ Modello disponibile: models/gemini-2.5-flash-native-audio-preview-12-2025
✅ Modello disponibile: models/gemini-3.1-flash-live-preview
✅ Modello disponibile: models/gemini-3.8-live
✅ Modello disponibile: models/gemini-3.8-live-extended-thinking
✅ Modello disponibile: models/gemini-robotics-er-2-streaming-preview
✅ Modello disponibile: models/gemini-3.5-live-translate-preview
✅ Modello disponibile: models/lyria-realtime-exp
"""