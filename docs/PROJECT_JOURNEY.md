
<h5><code>#!/usr/bin/env markdown</code><br>
<code>#==============================================================================</code><br>
<code># 🔐 RAVENFOOT PASSWORDS — P100 PROJECT JOURNEY</code><br>
<code>#==============================================================================</code><br>
<code># Purpose: Narrative walkthrough of how a simple text-scraper evolved into a retro-styled, cross-platform, deterministic password generator.</code><br>
<code># Audience: Reviewers, hiring managers, Developers, tinkerers, and future maintainers.</code><br>
<code># Stack: Python · Tkinter · (optional) Pillow</code><br>
<code># Context:  Complements README.md (Technical Docs)</code><br>
<code># Version: 1.2.0</code><br>
<code># License: Apache-2.0</code><br>
<code># Status: Production / Stable</code><br>
<code># Author: Ravenfoot</code><br>
<code>#==============================================================================</code></h5>


---

## 0. 🧬 Ravenfoot projects

* **a)** [Ravenfoot Calculator (Legacy)](https://github.com/ravenfoot/Ravenfoot.Calculator.Legacy.Edition)
* **b)** Ravenfoot Passwords — P100 (Teletext Edition) <--- You are here (PROJECT JOURNEY.md)
* **c)** [Ravenfoot Rune Timer (Dota 2)](https://github.com/ravenfoot/Ravenfoot.Rune.Timer.Dota.2)
* **d)** [Ravenfoot NAS Automation (Bash Edition)](https://github.com/ravenfoot/Ravenfoot.NAS.Automation.Bash.Edition)
* **e)** [Ravenfoot Webpage](https://github.com/ravenfoot/Ravenfoot.Webpage)
* **f)** [Ravenfoot Scryer — AoW Overlay (Stage 1)](https://github.com/ravenfoot/Ravenfoot.Scryer.AoW.Overlay.1)


## 1. Contents:

* **❓ Problem & Context**
* **🎯 Success Criteria**
* **🏗️ Evolution: From Script to Application**
* **🩹 Engineering Challenges (Breakpoints & Fixes)**
* **🤖 AI as a Tool**


## 2. ❓ Problem & Context

The project began as a set of loose utility scripts for an unrelated project. I initially needed a portable way to extract words from PDFs and clean up text files.

As a trilingual speaker, I noticed standard password generators were lacking:
- **Monolingual bias:** They rarely allowed mixing languages (e.g., English + Spanish + Swedish) organically.
- **Lack of determinism:** No guarantee that specific character sets would be used.
- **Boring UX:** Standard GUI forms felt sterile.

**My needs:** `<Portability>` `<Multilingual Entropy>` `<Aesthetic>` `<Offline Safety>` `<Opensource>`

---

## 3. 🎯 Success Criteria

**Technical Goals:**
* **Dynamic Loading:** The system must scan the `/library` folder and ingest *any* `*_words_clean.txt` file found.
* **Guaranteed Mixing:** If multiple languages are present, the algorithm must force a mix.
* **User History:** Save generated passwords to a persistent log respecting OS permissions (`%APPDATA%` vs `~/.home`).

**Design Goals:**
* **Retro Aesthetic:** A "Teletext / Ceefax P100" interface. High contrast (Cyan/Yellow/Green on Black).
* **Visual Feedback:** "Fastext" color-coded buttons and live clock.

---

## 4. 🏗️ Evolution: From Script to Application

**Phase 1: The Scrapers**

Started as two portable scripts:
1.  **PDF Extractor:** Scanned directories for PDFs to dump words.
2.  **Text Cleaner:** Removed duplicates and normalized special characters (e.g., 'ø' → 'o').

**Phase 2: The Logic Core**

Moved to a Python script that combined lists.
* **Logic:** `Word` + `Special Char` + `Number`.

**Phase 3: The GUI Transformation**

Shifted from Terminal I/O to `tkinter`.
* **V1 GUI:** Standard dark mode. Functional but generic.
* **V2 GUI (Teletext):** Complete overhaul to implement the P100 aesthetic. Implemented "Fastext" navigation.

---

## 5. 🩹 Engineering Challenges (Breakpoints & Fixes)

This project encountered several environment-specific bugs that required deep diving into OS protocols.

# **5.1 The X11 "BadLength" Crash 🐧**
**Issue:** The app crashed immediately on Linux with `X Error of failed request: BadLength`.
**Root Cause:** The window icon was too high-resolution for the X11 protocol to handle via Tkinter directly.
**Fix:** Implemented a safe-loader using `Pillow` to resize the icon to 32x32 before passing it to the window manager. Added a fallback to standard Tkinter methods if Pillow is missing.

# **5.2 The "Relative Path" Trap 🏗️**
**Issue:** `PyInstaller` failed with "Script file does not exist" even when the file was visible.
**Root Cause:** Running the build command from *inside* the `generator_core` directory meant relative paths were misaligned.
**Fix:** Refactored the build process to run strictly from the project root, using a flat directory structure.

# **5.3 Docker Permission Hell 🐳**
**Issue:** Cross-compiling for Windows using Docker resulted in `Permission denied` errors on the `dist/` folder.
**Root Cause:** Docker created the `dist` folder as `root`, locking out the standard user.
**Fix:** `sudo chown -R $USER:$USER .` to reclaim ownership, followed by a clean build.

# **5.4 Move toward pyinstaller**
* **See 🔄 Refactoring Log: v1.0 → v1.1 in README.md**

---

## 6. 🤖 AI as a Tool

**What Worked**
- **Aesthetic translation:** Turning “make it look like Ceefax” into concrete Tkinter color constants and layout grids.
- **Packaging setup:** Drafting initial PyInstaller spec files and flags.
- **Documentation polish:** Structuring the README and tightening code comments.
- **Learning partner:** Explaining the “why” behind choices and suggesting viable alternatives—so it wasn’t just vibe-coding.

**What Required Human Intervention**
- **Docker group/sockets:** After `usermod -aG docker $USER`, the current shell didn’t inherit the group. Needed `newgrp docker` or a re-login/reboot.
- **Algorithm validation:** The “guaranteed mixing” logic needed explicit checks to enforce sampling from at least two distinct word lists (not merely random choice).
- **System architecture:** AI was useful at the component level, but scaffolding had to be explicit and continuous (interfaces, boundaries, failure modes).

**Takeaways**
- Use AI for speed on boilerplate and exploration; use human review for correctness, architecture, and edge-case handling.


<code>#==============================================================================</code><br>
<code>#🛑 END</code><br>
<code>#==============================================================================</code></h5>