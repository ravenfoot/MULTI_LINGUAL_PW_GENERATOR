#!/usr/bin/env markdown
# ==============================================================================
# 🔐 RAVENFOOT P100 — PROJECT JOURNEY
# ==============================================================================
# Purpose:  Narrative walkthrough of how a simple text-scraper evolved into
#           a retro-styled, cross-platform, deterministic password generator.
#
# Audience: Developers, tinkerers, and future maintainers.
#
# Path:     docs/PROJECT_JOURNEY.md
# Related:  README.md • ARCHITECTURE.md
# ==============================================================================


## 🔗 Related Docs

├── README.md
├── ARCHITECTURE.md
└── PROJECT_JOURNEY.md ← You are here


## 📖 How to Use This Document

If you are browsing the repo fresh:

- Start with `README.md` — for installation and usage.
- Read this document — to understand the "how" and "why" behind the code.

**Key Directories:**

[cite_start]→ `generator_core/` — Main application logic [cite: 28]
[cite_start]→ `library/` — Dynamic word lists and token sources [cite: 147]
[cite_start]→ `gui/` — Assets and icons [cite: 26]

---

## 🗂 Contents

1. **Problem & Context**
2. **Success Criteria**
3. **Evolution: From Script to Application**
4. **Key Decisions & Trade-offs**
5. **Breakpoints & Fixes**
6. **AI as a Tool**
7. **Testing & Evidence**
8. **Security & Operations**
9. **Repo Tour**

---


# 1. ❓ Problem & Context

## **1.1 What Was Broken / Inefficient?**

The project began as a set of loose utility scripts. I initially needed a portable way to extract words from PDFs and clean up text files.

However,as a trilungual speaker I noticed standard password generators were lacking:
- **Monolingual bias:** They rarely allowed mixing languages (e.g., English + Spanish + Swedish) organically.
- **Lack of determinism:** No guarantee that specific character sets would be used.
- **Boring UX:** Standard GUI forms felt sterile.

I decided to make something that was:
- **Opensource:** I wanted an open and auditable program.
- **Portability:** My initial scripts were tied to the dev environment; I needed a standalone executable.
- **Easy customisability** I wanted that could expand and contract easily.

**My needs:**
`<Portability>` `<Multilingual Entropy>` `<Aesthetic>` `<Offline Safety>` `<Opensource>`

---

## **1.2 Hard Constraints**

- **Cross-Platform:** Must run on Linux (Ubuntu/Xubuntu) and Windows.
- **No Installation:** The final product must be a single file (`.exe` or binary).
- **Customizable:** Users must be able to drop in new language lists (e.g., Kanji, Russian) without rewriting code.

---


# 2. 🎯 Success Criteria

## **2.1 Technical Goals**

- **Dynamic Loading:** The system must scan the `/library` folder and ingest *any* `*_words_clean.txt` file found.
- **Guaranteed Mixing:** If multiple languages are present, the algorithm must force a mix (preventing "all English" rolls).
- **Entropy Calculation:** Live feedback on password strength in bits.
- **User History:** Save generated passwords to a persistent log, but respecting OS permissions (`%APPDATA%` vs `~/.home`).

## **2.2 Design Goals**

- **Retro Aesthetic:** A "Teletext / Ceefax P100" interface. High contrast (Cyan/Yellow/Green on Black), monospaced fonts, and blocky UI elements allow for a cool look but also accessible.
- **Visual Feedback:** "Fastext" color-coded buttons and live clock.

---


# 3. 🏗️ Evolution: From Script to Application

## **Phase 1: The Scrapers**

Started as two portable scripts:
1.  **PDF Extractor:** Scanned directories for PDFs to dump words.
2.  **Text Cleaner:** Removed duplicates and normalized special characters (e.g., 'ø' → 'o').

## **Phase 2: The Logic Core**

Moved to a Python script that combined lists.
- **Logic:** `Word` + `Special Char` + `Number`.
- **Issue:** Hardcoded paths (`/word_library/english.txt`) made it rigid.

## **Phase 3: The GUI Transformation**

Shifted from Terminal I/O to `tkinter`.
- **V1 GUI:** Standard dark mode. Functional but generic.
- **V2 GUI (Teletext):** Complete overhaul to implement the P100 aesthetic. Implemented "Fastext" navigation and removed window padding.

---


# 4. 🔑 Key Decisions & Trade-offs

## **4.1 Dynamic Library Architecture**

**Decision:** Instead of hardcoding `EN_WORDS` and `ES_WORDS`, the script now uses `glob` to find `*_words_clean.txt`.
**Why:** Allows "Plug-and-Play" for new languages (e.g., dropping in `german_words_clean.txt` works instantly).

## **4.2 Sys._MEIPASS for Portability**

**Decision:** Use a `resource_path()` helper function.
**Why:** PyInstaller unpacks bundled files to a temporary `_MEIxxxx` directory at runtime. Standard relative paths fail in the `.exe`. This function routes traffic correctly whether in Dev or Frozen mode.

## **4.3 Writing Logs to User Profile**

**Decision:** Do not write logs next to the executable.
**Why:** Installed apps (e.g., in `Program Files`) are read-only.
**Fix:** Logic directs logs to `%APPDATA%/RavenfootPassword` (Windows) or `~/.ravenfoot_password` (Linux).

---


# 5. 🩹 Breakpoints & Fixes

## **5.1 The X11 "BadLength" Crash**

**Issue:** The app crashed immediately on Linux with `X Error of failed request: BadLength`.
**Root Cause:** The window icon was too high-resolution for the X11 protocol to handle via Tkinter.
**Fix:** Implemented a safe-loader using `Pillow` to resize the icon to 32x32 before passing it to the window manager (This also now allows people to cp their own .ico to the program).

## **5.2 The "Relative Path" Trap**

**Issue:** `PyInstaller` failed with "Script file does not exist" even when the file was visible.
**Root Cause:** Running the build command from *inside* the `generator_core` directory meant the relative paths (`gui:gui`) were pointing to non-existent nested folders.
**Fix:** Moved up to the project root (`cd ..`) to run the build command.

## **5.3 Docker Permission Hell**

**Issue:** Cross-compiling for Windows using Docker resulted in `Permission denied` errors on the `dist/` folder.
**Root Cause:** Docker created the `dist` folder as `root`, locking out the standard user.
**Fix:** `sudo chown -R $USER:$USER .` to reclaim ownership, followed by a clean build.

---


# 6. 🤖 AI as a Tool

## **6.1 What Worked**
- **Architecture Ideation:** Moving from hardcoded lists to a dynamic `library/` folder[cite: 143].
- **Aesthetic Translation:** Converting "make it look like Ceefax" into specific Tkinter color codes and layout grids.
- **Cross-Compilation:** Generating specific Docker and Wine commands to build Windows `.exe` files from Linux.

## **6.2 What Required Human Intervention**
- **Docker Sockets:** AI suggested `usermod`, but the immediate shell session required `newgrp docker` or a restart to take effect.
- **Logic Validation:** The "Guaranteed Mixing" algorithm required specific logical tuning to ensure it didn't just pick random words, but forced at least two distinct lists were sampled.

---


# 7. 🧪 Testing & Evidence

## **7.1 Functional Tests**

- **Entropy Check:** Verified bit-strength adjusts live as inputs change.
- **Confirmed copy:** works without freezing the UI.
- **Portability:** Verified `.exe` runs on a clean Windows VM without Python installed.

## **7.2 Deployment Builds**

- **Windows:** Built via Wine/Docker → `Ravenfoot_P100.exe`.
- **Linux:** Built natively → `ravenfoot_p100` binary wrapped in a `.deb` package.

---

# 8. 🔐 Security & Operations

- **Log Safety:** History is plaintext by design for user convenience, but stored in user-owned directories to prevent permission escalations.
- **Clipboard:** Flash notification confirms copy; user is responsible for clipboard history management.
- **Entropy:** Calculation is heuristic (based on list size and token count), serving as a guide rather than a cryptographic guarantee.

---


# 9. 🗺️ Repo Tour

```
ravenfoot_password_generator/
├── library/                 # Dynamic Content (Drag/Drop or Copy/Paste)
│   ├── english_words_clean.txt
│   ├── spanish_words_clean.txt
│   ├── special_characters.txt
│   └── numbers.txt
├── gui/
│   └── logo/
│       └── ravenfootlogo_icon.png
└── generator_core/
│    └── teletext_generator.py # The Main P100 Application
│
└── docs/
|       ├── PROJECT_JOURNEY.md   # ← You are here
|       └── ARCHITECTURE.md
|
└── README.md




==============================================================================
🛑 END
==============================================================================