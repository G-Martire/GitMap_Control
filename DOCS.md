# 📚 PADAS GitMap Control - Technical Guide & Architecture

This document provides a detailed breakdown of core modules, file organization, and design principles for **PADAS GitMap Control**.

---

## ⚡ Core Features & Operations Table

Overview of the primary automated workflows and components managed within the canvas interface:

| Feature / Module | Action / Description |
| :--- | :--- |
| **Canvas Mind Map** | Visualizes project nodes, directories, and file relationships dynamically. |
| **Local Git Manager** | Executes status checks, commit summaries, and visual diff comparisons. |
| **AI i18n Pipeline** | Scans Python code, extracts UI strings, and generates structured localization files. |
| **USB / External Sync** | Exports clean project snapshots (stripping `.venv`, cache, and `.git`) or delta updates. |
| **Quick File Search** | Locates files across the codebase and opens them directly in OS File Explorer. |
| **Tree Exporter** | Copies the clean directory structure instantly to feed LLMs or documentation. |

---

## 🗂️ Application File Structure

```text
GitMap_Control/
├── gestione_git/
├── gestione_i18n/
│   ├── dialog_i18n/
│   │   ├── code_json.py
│   │   ├── config.py
│   │   ├── intro.py
│   │   ├── multilang.py
│   │   └── summary.py
│   ├── dubbi/
│   ├── pipeline/
│   │   ├── classe B/
│   │   │   ├── backup_sorgenti/
│   │   │   ├── 1.2-scanner_class_b.py
│   │   │   ├── 2.2-ai_verify_class_b.py
│   │   │   ├── 2.3-classe_c_manuale.py
│   │   │   └── 3.3-patch_init.py
│   │   ├── 1.1-scanner_ui.py
│   │   ├── 1.2-cleanup_translated.py
│   │   ├── 2.1-ai_classifier.py
│   │   ├── 3.1-apply_code.py
│   │   ├── 3.2-update_json.py
│   │   └── 4-auto_translate.py
│   ├── global_languages.json
│   ├── list_models.py
│   ├── sidebar_i18n.py
│   └── worker_i18n.py
├── git_map_core/
│   ├── dialogs/
│   │   ├── progetti.py
│   │   ├── progetti_ctrl.py
│   │   ├── riepilogo.py
│   │   ├── riepilogo_ctrl.py
│   │   ├── riepilogo_helpers.py
│   │   ├── salva.py
│   │   ├── usb.py
│   │   └── utils.py
│   ├── main_window/
│   │   ├── git_history.py
│   │   ├── i18n.py
│   │   ├── map.py
│   │   ├── menu.py
│   │   ├── sidebar_filtri.py
│   │   └── theme.py
│   ├── git_controller.py
│   ├── i18n.py
│   ├── nodes.py
│   ├── search_export_controller.py
│   └── views.py
├── locales/
│   ├── de.json
│   ├── en.json
│   └── it.json
├── ai_config.json
├── config.json
└── main.py
```

---
## 🏛️ Architectural Philosophy & Design Principles

Anti-Monolithic Modular Design
The project intentionally rejects single-file monolithic scripts. Whenever a module expands, it is refactored into domain-specific sub-packages with highly targeted files, maintaining a clean separation of concerns between UI views, background workers, and core controllers.

### Core Benefits

1. **Maintainability & Clean Architecture:** Isolating responsibilities into specialized sub-folders (`gestione_git`, `gestione_i18n`, `git_map_core`) keeps the codebase readable and easy to navigate.
2. **Resource Efficiency:** Allows selective component loading, reducing memory footprint and startup overhead in PyQt6.
3. **AI-Assisted Workflow Optimization:** Keeps file contexts small and modular, drastically reducing token generation costs and avoiding LLM context dilution when updating specific features.
4. **Team Collaboration:** Prevents merge conflicts and allows developers to work simultaneously on isolated features without touching the same central file.
