# 🚀 PADAS GitMap Control

> *Parte dell'ecosistema PADAS DevStudio.*

**PADAS GitMap Control** è un'utility "Canvas-First" sviluppata in **Python** e **PyQt6**.

📍 **Presentato su LinkedIn:** [Connettiti su LinkedIn](https://www.linkedin.com)

---

## 📌 Panoramica del Progetto

* **Cos'è:** Un programma per sviluppatori realizzato in Python (con interfaccia PyQt6) progettato per offrire un controllo visivo totale sui flussi di lavoro.
* **Scopo Generale:** Automatizzare i processi di sviluppo del codice, dalla gestione dei repository Git alle traduzioni e alla portabilità offline.
* **Dettaglio dello Scopo:** Sfruttare un'interfaccia grafica visuale a mappa mentale e tabelle — eliminando la riga di comando — per effettuare confronti macro e rapidi tra diverse versioni del codice, scendendo poi nel dettaglio dei singoli file con un solo click.

---

## ⚡ Cosa Fa il Programma

* **Git Locale & Diff Visivi:** Esegue operazioni Git locali con un sommario in tabella unito allo stato visivo dei singoli file direttamente sul canvas.
* **Pipeline di Traduzione IA (i18n):** Scansiona automaticamente il codice Python, estrae le stringhe dell'interfaccia e genera file JSON strutturati (alimentato da Gemini).
* **Sincronizzazione USB & Esterna:** Esporta un'istantanea pulita del progetto (escludendo `.venv`, cache e `.git`) o solo il delta dell'ultimo commit su disco esterno, reimportando gli aggiornamenti senza sovrascrivere le configurazioni locali.
* **Ricerca & Navigazione Rapida:** Cerca file nel progetto e li apre direttamente in Esplora Risorse tramite tasto destro.

---

## 📖 Documentazione & Guida all'Architettura

Per l'elenco completo dei moduli, delle fasi della pipeline IA e della struttura delle directory, consulta la guida dettagliata:

👉 [Leggi la Documentazione Tecnica Completa (DOCS.md)](DOCS.md)

---

## 📦 Avvio Rapido

### Scarica l'Esecutivo
Scarica l'eseguibile portatile `.exe` pronto all'uso dalla sezione [Releases](https://github.com/G-Martire/GitMap_Control/releases).

### Configurazione per Sviluppatori

```bash
git clone [https://github.com/G-Martire/GitMap_Control.git](https://github.com/G-Martire/GitMap_Control.git)
cd GitMap_Control
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python main.py
```

---

🔮 Roadmap & Sviluppi Futuri
- [ ] Supporto LLM Esteso: Integrazione con modelli locali oltre a Gemini per le pipeline i18n.
- [ ] CI/CD Automatizzata: Flussi GitHub Actions per build automatizzate dei file .exe.
- [ ] Visualizzatore Avanzato di Branch: Mappatura dei nodi migliorata per la risoluzione complessa dei conflitti di merge.

## MIT License - see LICENSE for details.
