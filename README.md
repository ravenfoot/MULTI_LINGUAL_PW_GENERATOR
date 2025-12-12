
**!/usr/bin/env markdown**

**==============================================================================**

**🔐 RAVENFOOT P100 — README**

**==============================================================================**

**A retro-styled, multilingual passphrase generator.**

**Version:  1.2.0 (Teletext Edition)**
**License:  Apache License 2.0**
**Status:   Production / Stable**

**==============================================================================**

## 0. 🧬 Ravenfoot projects

* **a)** [Ravenfoot Calculator (Legacy)](https://github.com/ravenfoot/Ravenfoot.Calculator.Legacy.Edition)
* **b)** Ravenfoot Passwords — P100 (Teletext Edition) <--- You are here
* **c)** [Ravenfoot Rune Timer (Dota 2)](https://github.com/ravenfoot/Ravenfoot.Rune.Timer.Dota.2)
* **d)** [Ravenfoot NAS Automation (Bash Edition)](https://github.com/ravenfoot/Ravenfoot.NAS.Automation.Bash.Edition)
* **e)** [Ravenfoot Webpage](https://github.com/ravenfoot/Ravenfoot.Webpage)
* **f)** [Ravenfoot Scryer — AoW Overlay (Stage 1)](https://github.com/ravenfoot/Ravenfoot.Scryer.AoW.Overlay.1)


## 1. ️️⬇️ Downloads (Binaries)

No coding required. Download the pre-compiled standalone for your OS from **[Releases]**:

- 🪟 **Windows (.exe)** — [Ravenfoot_P100.exe](https://github.com/ravenfoot/Ravenfoot.Passwords.P100.Teletext-Edition/releases/download/Latest/Ravenfoot_P100.exe) (Portable, no install needed)
- 🐧 **Linux (.deb)** — [ravenfoot_p100_v1.0_amd64.deb](https://github.com/ravenfoot/Ravenfoot.Passwords.P100.Teletext-Edition/releases/download/Latest.deb/ravenfoot_p100_v1.0_amd64.deb) (Debian/Ubuntu package)

> Or browse the **[latest release page](../../releases/latest)** for notes and checksums.


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

### Run from source (Linux/Windows/macOS)
```bash
# Clone and enter directory
git clone https://github.com/ravenfoot/Ravenfoot.Passwords.P100.Teletext-Edition.git
cd Ravenfoot.Passwords.P100.Teletext-Edition

# Optional (for nicer icon scaling)
python3 -m pip install --upgrade pip
python3 -m pip install pillow

# Launch
python3 generator_core/teletext_generator.py
