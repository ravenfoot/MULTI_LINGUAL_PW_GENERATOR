#!/usr/bin/env markdown
# ==============================================================================
# 🔐 RAVENFOOT P100 — README
# ==============================================================================
# A retro-styled, multilingual passphrase generator.
#
# Version:  1.0 (Teletext Edition)
# License:  MIT (or your choice)
# Status:   Production / Stable
# ==============================================================================

## 1. 💾 Quick Start (Binaries)

No coding required. Download the pre-compiled standalone for your OS from **[Releases]**:

* **Windows:** `Ravenfoot_P100.exe` (Portable, no install needed)
* **Linux:** `ravenfoot_p100_v1.0_amd64.deb` (Debian/Ubuntu package)

---

## 2. 📺 The Mission

**Ravenfoot P100** is a secure password generator wrapped in a nostalgic **Ceefax/Teletext** interface. It solves the "monolingual bias" of standard tools by allowing you to mix words from multiple languages (English, Spanish, Kanji, etc.) into a single, high-entropy passphrase.

**Core Philosophy:**
* **Visuals:** High-contrast, monospaced retro aesthetic.
* **Logic:** Deterministic mixing of word lists + numeric/special tokens.
* **Feedback:** Live entropy estimation (in bits) as you type settings.

---

## 3. ⚡ Capabilities

* **Portable Architecture:** Runs as a single file. Uses `sys._MEIPASS` logic to handle asset extraction transparently in frozen builds.
* **Dynamic Library:** The engine scans the `/library` folder at startup. Any file matching `*_words_clean.txt` is automatically ingested and used for generation.
* **Guaranteed Mixing:** If multiple language lists are detected, the algorithm enforces a mix (preventing "all English" rolls).
* **User-Safe Logging:** Generates a plaintext history log in your User Profile (e.g., `%APPDATA%`), avoiding permission errors in read-only directories.

---

## 4. 🛠️ Usage & Extensibility

### Running from Source
```bash
# Clone and enter directory
git clone [https://github.com/yourusername/ravenfoot_p100.git](https://github.com/yourusername/ravenfoot_p100.git)
cd ravenfoot_p100

# Install dependencies (Pillow is optional but recommended for icons)
pip install pillow

# Launch
python3 generator_core/teletext_generator.py
