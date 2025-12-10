#!/usr/bin/env markdown
# ==============================================================================
# 🏗️ RAVENFOOT P100 — ARCHITECTURE
# ==============================================================================
# Purpose:  Technical blueprint of the Ravenfoot P100 passphrase generator.
#           Covers component structure, data flow, and build logic.
#
# Path:     docs/ARCHITECTURE.md
# Context:  complements PROJECT_JOURNEY.md (narrative) & README.md (usage).
# ==============================================================================

## 1. 📐 System Goals

* **Portability:** Single-file execution via PyInstaller (`--onefile`). Uses `sys._MEIPASS` to resolve bundled assets at runtime.
* **Dynamic Content:** Auto-ingests any `*_words_clean.txt` file found in `/library` without recompilation.
* **Safe I/O:** Writes history logs to OS-compliant user directories (`%APPDATA%` / `~`) to avoid permission locks.
* **Retro UX:** Strict Teletext/Ceefax aesthetic (Monospace, Cyan/Yellow/Green on Black) implemented via standard Tkinter.

---

## 2. 🧱 Component Map

```text
ravenfoot_password_generator/
├── generator_core/
│   └── teletext_generator.py   # 🧠 The Brain: GUI, Logic, & Path Helpers
├── library/                    # 📚 The Data: Runtime content loaded via glob
│   ├── *_words_clean.txt       #    → English, Spanish, Kanji, etc.
│   ├── special_characters.txt  #    → Tokens
│   └── numbers.txt             #    → Numerals
├── gui/
│   └── logo/                   # 🎨 The Assets
│       └── ravenfootlogo_icon.png
└── docs/                       # 📄 The Documentation
    ├── ARCHITECTURE.md         #    ← You are here
    └── PROJECT_JOURNEY.md