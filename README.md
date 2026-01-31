
<h5><code>#!/usr/bin/env markdown</code><br>
<code>#==============================================================================</code><br>
<code># 🔐 RAVENFOOT PASSWORDS — P100 (Teletext Edition)</code><br>
<code>#==============================================================================</code><br>
<code># Purpose: Retro-styled, multilingual password generator with live entropy.</code><br>
<code># Audience: End users, reviewers, hiring managers.</code><br>
<code># Stack: Python · Tkinter · (optional) Pillow</code><br>
<code># Version: 1.2.0</code><br>
<code># License: Apache-2.0</code><br>
<code># Status: Production / Stable</code><br>
<code># Author: Ravenfoot</code><br>
<code>#==============================================================================</code></h5>


---

## 0. 🧬 Ravenfoot projects

* **a)** [Ravenfoot Calculator (Legacy)](https://github.com/ravenfoot/Ravenfoot.Calculator.Legacy.Edition)
* **b)** Ravenfoot Passwords — P100 (Teletext Edition) <--- You are here
* **c)** [Ravenfoot Rune Timer (Dota 2)](https://github.com/ravenfoot/Ravenfoot.Rune.Timer.Dota.2)
* **d)** [Ravenfoot NAS Automation (Bash Edition)](https://github.com/ravenfoot/Ravenfoot.NAS.Automation.Bash.Edition)
* **e)** [Ravenfoot Webpage](https://github.com/ravenfoot/Ravenfoot.Webpage)
* **f)** [Ravenfoot Scryer — AoW Overlay (Stage 1)](https://github.com/ravenfoot/Ravenfoot.Scryer.AoW.Overlay.1)

---

## 1. Contents:

* **📺 The Mission**
* **⚡ Capabilities**
* **💾 Downloads & Usage**
* **🧱 Architecture**
* **🔧 Key Engineering Decisions**
* **🔄 Refactoring Log: v1.0 → v1.3**
* **📦 Build Instructions**
* **🔧 Troubleshooting & Known Issues**


---

## 2. 📺 The Mission

**Ravenfoot P100**
Is a secure password generator wrapped in a nostalgic **Ceefax/Teletext** interface. It solves the "monolingual bias" of standard tools by allowing you to mix words from multiple languages (English, Spanish, Kanji, etc.) into a single, high-entropy passphrase.

**Core Philosophy:**

* **Visuals:** High-contrast, monospaced retro aesthetic.
* **Logic:** Deterministic mixing of word lists + numeric/special tokens (avoiding paterned passwords e.g. word-word-word).
* **Feedback:** Live entropy estimation (in bits) as you type settings.

---

## 3. ⚡ Capabilities

* **Portable Architecture:** Runs as a single file. Uses `sys._MEIPASS` logic to handle asset extraction transparently in frozen builds.
* **Dynamic Library:** The engine scans the `/library` folder at startup. Any file matching `*_words_clean.txt` is automatically ingested and used for generation.
* **Guaranteed Mixing:** If multiple language lists are detected, the algorithm enforces a mix (preventing "all English" rolls).
* **User-Safe Logging:** Generates a plaintext history log in your User Profile (e.g., `%APPDATA%`), avoiding permission errors in read-only directories. 
⚠️⚠️NOTE: This is a known security vulnerability - There's always a trade off between usabilitty and security | delete using bleachBit⚠️⚠️

---

## 4. 💾 Downloads & Usage

**No installation required.** Download the standalone executable for your OS:

- 🪟 **Windows (.exe)** — [Ravenfoot_P100.exe](https://github.com/ravenfoot/Ravenfoot.Passwords.P100.Teletext-Edition/releases/tag/Latest.exe)
- 🐧 **Linux (.deb)** — [ravenfoot_p100_amd64.deb](https://github.com/ravenfoot/Ravenfoot.Passwords.P100.Teletext-Edition/releases/tag/Latest.deb)

### 📂 Where is my Password History?
For security and permissions reasons, the plaintext log is stored in your user profile directory rather than next to the application.
* **Windows:** `%APPDATA%\RavenfootPassword\password_history.txt`
* **Linux:** `~/.ravenfoot_password/password_history.txt` (Hidden folder)

> **Pro Tip:** You can open this file directly from the application by clicking the **[OPEN LOG]** button.

---

## 5. 🧱 Architecture

This project demonstrates a clear separation of concerns, utilizing dynamic resource loading and OS-agnostic path handling.

```text

ravenfoot_password_generator/
├── ravenfoot_password_generator.py   # 🧠 The Brain: GUI, Logic, & Path Helpers
│
├── ravenfoot_icon_64.png     	 	  # 🐧 Linux Window Icon (🎞️Add your own!)
├── ravenfoot_icon.ico     	  		  # 🪟 Windows Native Icon (🎞️ Add your own!)
│
├── library/                    	  # 📚 Data Layer (Auto-ingested via glob)
│   ├── `CUSTOM_words_clean.txt`      #    → Add your own: Swedish, Kanji, Add a dictionary 📖 etc. 
│   ├── `numbers.txt`  	  			  #    → Numerals
│   ├── `spanish_words_clean.txt`	  #    → 17.7 Spanish words
│	├── `english_words_clean.txt`	  #    → 15.5k English words
│	└── `special_characters.txt`      #    → Tokens
│
├── password_log/					  
│	└── password_history.sample       #	   → A history of generatted passwordsaftter instalation this lands in:
│											🪟 Windows:  %APPDATA%\RavenfootPassword or
│											🐧 Linux:    ~/.ravenfoot_password/password_history.txt)
│
└── docs/                 		      # 📄 The Documentation
    ├── setup_script.iss 			  #    → Standard installer setup
    ├── LICENSE                       #    → Apache License Version 2.0
    ├── README.md					  #    → Technical blueprints	
    └── PROJECT_JOURNEY.md            #    → Development history & debugging log

```
---

## 6. 🔧 Key Engineering Decisions

  **6.1 Dynamic Library Architecture**
* **Decision:** Instead of hardcoding EN_WORDS and ES_WORDS, the script uses glob to find x_words_clean.txt. 
* **Why:** Allows "Plug-and-Play" extensibility. Users can drop in german_words_clean.txt and the app immediately recognizes it without recompilation.


  **6.2 Sys._MEIPASS for Portability**
* **Decision:** Implemented a robust resource_path() helper function. 
* **Why:** PyInstaller unpacks bundled files to a temporary x_MEIxxxx directory at runtime. 
           Standard relative paths fail in compiled .exe files. This function routes resource requests correctly whether running in Dev (Source) or Frozen (Binary) mode.

  **6.3 Security & Operations**
* **Entropy:** Calculation is heuristic (based on list size and token count), serving as a guide rather than a cryptographic guarantee.
* **Log Safety:** History is plaintext for user convenience but stored in user-owned directories to prevent permission escalations in shared environments.

---

## 7. 🔄 Refactoring Log: v1.0 → v1.2

To prepare for release, the code underwent a "Professional Polish" refactor:

* **File Renamed:** `teletext_generator.py` → `ravenfoot_password_generator.py`.
* **Path Logic:** Updated `resource_path()` to use `.parent` (root relative) instead of `.parents[1]`.
* **Linux Integration:** Added `className="ravenfoot-p100"` to the main Tkinter window initialization. This fixes the "missing taskbar icon" issue on GNOME/Cinnamon desktop environments.
* **User Experience:** Added an **[OPEN LOG]** button to allow users to view their password history without manually navigating hidden system folders.


## 8. 📦 Build Instructions

**🪟 Windows (.exe)**
Run in PowerShell. (win+r) Note the use of ; for data separation.

**PowerShell**
```
pyinstaller --noconfirm --onefile --windowed --name "Ravenfoot P100" --icon "ravenfoot_icon.ico" --add-data "ravenfoot_icon.ico;." --add-data "library;library" ravenfoot_password_generator.py
```
(**🟡Side Note🟡:** this creates a portable version, if you want full install functionality use **Inno Setup** (or similar) with the provided .iss script to generate a standard installer.


**🐧 Linux (.deb)**

Run in Terminal. Note the use of : for data separation.


**1. Compile Binary**

~~~ Bash
pyinstaller --noconfirm --onefile --windowed --name "ravenfoot-p100" --add-data "ravenfoot_icon_64.png:." --add-data "library:library" ravenfoot_password_generator.py

~~~

**2. Package .deb (requires dpkg-deb and standard directory structure)**

~~~Bash
dpkg-deb --build build/deb/ravenfoot-p100

~~~

## 9. 🔧 Troubleshooting & Known Issues

# **6.1 🧩 Dependencies**

* On some debian systems it might requier **python3-pil.imagetk (10.2.0-1ubuntu1)**

# **6.2 🦠 "Virus Detected" during Build (False Positive)** 

* **Symptom:** Antivirus software (Windows Defender, ClamAV, etc.) flags the executable or installer as malicious (e.g., `Trojan:Win32/Wacatac`).
* **Cause:** This project is compiled using **PyInstaller**. The bootloader code that unpacks the Python interpreter into memory shares a signature with some common malware wrappers.
             This is a known false positive affecting many Python projects.
* ***Solution:**
	* **Developers:** Add the project `dist/` and `build/` directories to your Antivirus "Exclusions" or "Whitelist".
	* **Users:** If downloading the release, you may need to "Allow" the file in your security settings.
	* **Verification:** You can compare the hash of the release with the source code by building it locally to ensure integrity.

⚠️⚠️NOTE: Always audit online code!!!⚠️⚠️

# **6.3 Functional Tests**

* **Entropy Check:** Verified bit-strength adjusts live as inputs change.
* **Confirmed copy:** works without freezing the UI.
* **Portability:** Verified `.exe` runs on a clean Windows VM without Python installed.

---

<code>#==============================================================================</code><br>
<code>#🛑 END</code><br>
<code>#==============================================================================</code></h5>
