# 🚀 PADAS GitMap Control

> *Part of the PADAS DevStudio ecosystem.*

**PADAS GitMap Control** is a "Canvas-First" developer utility built with **Python** and **PyQt6**.

📍 **Featured on LinkedIn:** [Connect on LinkedIn](https://www.linkedin.com)
*(il link lo aggiorno in data lunedì 16 novembre)*
---

## 📌 Project Overview

- **What it is:** A developer tool built in Python (with a PyQt6 interface) designed to provide full visual control over coding workflows.
- **General Purpose:** Automates code development processes, from local Git repository management to UI localization and offline portability.
- **Core Objective:** Leverages a visual mind-map and table-based interface — eliminating command-line friction — to perform fast macro-comparisons across code versions, drilling down into individual file diffs with a single click.

---

## ⚡ Key Features

- **Local Git & Visual Diffs:** Executes local Git operations with a tabular summary combined with the visual status of individual files directly on the canvas.
- **AI Translation Pipeline (i18n):** Automatically scans Python codebases, extracts UI strings, and generates structured JSON localization files (powered by Gemini).
- **USB & External Sync:** Exports a clean project snapshot (excluding `.venv`, cache, and `.git`) or just the latest commit delta to an external drive, re-importing updates without overwriting local configurations.
- **Quick Search & Navigation:** Searches files across the project and opens them directly in the OS File Explorer via right-click.

---

## 📖 Documentation & Architecture Guide

For a complete breakdown of modules, AI pipeline stages, and directory structure, see the detailed technical guide:

👉 [Read the Full Technical Documentation (DOCS.md)](DOCS.md)

---

## 📦 Quick Start

### Developer Setup

```bash
git clone [https://github.com/G-Martire/GitMap_Control.git](https://github.com/G-Martire/GitMap_Control.git)
cd GitMap_Control
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python main.py
```

---

🔮 Roadmap & Future Developments
- **Remote Synchronization (GitHub / GitLab):** Native integration of remote operations (`push`, `pull`, `fetch`) directly from the canvas to sync local repositories with the cloud.
- **Extended LLM Support:** Integration with local models (e.g., LM Studio / Ollama) alongside Gemini for offline i18n pipelines.
- **Advanced Branch Visualizer:** Enhanced node mapping for fast, visual resolution of complex merge conflicts.

## MIT License - see LICENSE for details.
