import importlib

# Caricamento dinamico sicuro dei moduli con trattini e numeri nel nome
try:
    scanner_ui = importlib.import_module(".1.1-scanner_ui", package=__name__)
    cleanup_translated = importlib.import_module(".1.2-cleanup_translated", package=__name__)
    ai_classifier = importlib.import_module(".2.1-ai_classifier", package=__name__)
    apply_code = importlib.import_module(".3.1-apply_code", package=__name__)
    update_json = importlib.import_module(".3.2-update_json", package=__name__)
    auto_translate = importlib.import_module(".4-auto_translate", package=__name__)
except Exception as e:
    print(f"[PIPELINE-INIT] Errore nel caricamento dei moduli della pipeline: {e}")