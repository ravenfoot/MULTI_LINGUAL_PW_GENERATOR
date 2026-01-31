"""
Ravenfoot Password Generator (P100 Teletext Edition)
====================================================

A cross-platform, deterministic password generator with a retro Teletext/Ceefax
aesthetic. It combines multiple language dictionaries with numeric and symbol
tokens to generate high-entropy passphrases.

Features:
    - Dynamic Library Loading: Ingests any `*_words_clean.txt` found in `/library`.
    - Live Entropy Calculation: Estimates bit-strength in real-time.
    - Secure Logging: Writes history to user-owned directories (%APPDATA% / ~).
    - Portable: Compiles to a single binary via PyInstaller.

Author:  Ravenfoot
License: Apache-2.0
Version: 1.2.0
"""

from __future__ import annotations

import math
import os
import random
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

# -----------------------------------------------------------------------------
# DEPENDENCY HANDLING
# -----------------------------------------------------------------------------
# Attempt to load Pillow for high-quality icon rendering (anti-aliasing).
# If unavailable (e.g., minimal environments), fall back to standard Tkinter.
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    from tkinter import PhotoImage  # type: ignore


# -----------------------------------------------------------------------------
# RESOURCE MANAGEMENT
# -----------------------------------------------------------------------------

def resource_path(*segments: str) -> Path:
    """
    Resolves the absolute path to bundled resources for PyInstaller.

    This handles the file system difference between a development environment
    (local disk) and a frozen executable (unpacked to a temp directory).

    Args:
        *segments: Path components to join (e.g., "library", "words.txt").

    Returns:
        Path: The absolute path to the requested resource.
    """
    # PyInstaller unpacks data to a temp folder named _MEIxxxx referenced by sys._MEIPASS.
    # We fall back to the script's parent directory for dev execution.
    base = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    return Path(base, *segments)


def user_history_path() -> Path:
    """
    Determines a safe, OS-compliant path for the password history log.

    To avoid permission errors in Program Files or /usr/bin, we target
    user-writable profile directories.

    Returns:
        Path: Absolute path to 'password_history.txt'.
          - Windows: %APPDATA%/RavenfootPassword/
          - Linux/Mac: ~/.ravenfoot_password/
    """
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
        log_dir = base / "RavenfootPassword"
    else:
        log_dir = Path.home() / ".ravenfoot_password"
    
    return log_dir / "password_history.txt"


# -----------------------------------------------------------------------------
# GLOBAL CONSTANTS & CONFIGURATION
# -----------------------------------------------------------------------------

ROOT_DIR    = resource_path()
LIBRARY_DIR = resource_path("library")
LOG_FILE    = user_history_path()

# Branding Assets (Located in Root)
ICON_WIN = "ravenfoot_icon.ico"
ICON_LIN = "ravenfoot_icon_64.png"

# Teletext Theme Palette (High Contrast)
FONT_MAIN   = ("Courier New", 12, "bold")
FONT_HEADER = ("Courier New", 24, "bold")
FONT_INPUT  = ("Courier New", 14, "bold")

COL_BG    = "#000000"  # Black
COL_TEXT  = "#FFFFFF"  # White
COL_CYAN  = "#00FFFF"
COL_YELL  = "#FFFF00"
COL_GREEN = "#00FF00"
COL_RED   = "#FF0000"
COL_BLUE  = "#0000FF"


# -----------------------------------------------------------------------------
# DATA LOADING ENGINE
# -----------------------------------------------------------------------------

def load_clean_lines(filepath: Path) -> list[str]:
    """
    Reads a file and returns a list of non-empty, stripped lines.

    Note: This function silently ignores encoding errors to prioritize 
    application stability over data correctness for user-supplied lists.

    Args:
        filepath: The path to the text file.

    Returns:
        list[str]: A list of strings, or an empty list if file is missing.
    """
    if not filepath.exists():
        return []
    with filepath.open("r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]

# Initialize Token Pools
SPECIALS = load_clean_lines(LIBRARY_DIR / "special_characters.txt") or ["!"]
NUMBERS  = load_clean_lines(LIBRARY_DIR / "numbers.txt") or ["1"]

# Initialize Word Lists (Dynamic Discovery)
WORD_LISTS: list[list[str]] = []
# Scans for english_words_clean.txt, spanish_words_clean.txt, etc.
for word_file in sorted(LIBRARY_DIR.glob("*_words_clean.txt")):
    words = load_clean_lines(word_file)
    if words:
        WORD_LISTS.append(words)

# Fail-safe: Ensure the app runs even if the library is corrupted or missing
if not WORD_LISTS:
    WORD_LISTS = [["error", "library", "missing"]]


# -----------------------------------------------------------------------------
# CORE LOGIC
# -----------------------------------------------------------------------------

def select_words(count: int) -> list[str]:
    """
    Selects `count` words from available word lists.

    Implements logic to ensure linguistic diversity: if multiple dictionaries
    are loaded (e.g., English + Spanish), it forces sampling from at least 
    two distinct lists before filling the remaining slots randomly.

    Args:
        count: The number of words to select.

    Returns:
        list[str]: A randomized list of words.
    """
    if count <= 0:
        return []

    # Simple case: Single list available or only 1 word requested
    if len(WORD_LISTS) == 1 or count == 1:
        return [random.choice(WORD_LISTS[0]) for _ in range(count)]

    # Complex case: Mix languages (e.g., English + Spanish)
    # 1. Pick two distinct source lists via index shuffling
    list_indices = list(range(len(WORD_LISTS)))
    random.shuffle(list_indices)
    idx_a, idx_b = list_indices[0], list_indices[1]
    
    selected = [random.choice(WORD_LISTS[idx_a]), random.choice(WORD_LISTS[idx_b])]

    # 2. Fill the remaining slots from any random list
    while len(selected) < count:
        chosen_list = random.choice(WORD_LISTS)
        selected.append(random.choice(chosen_list))

    random.shuffle(selected)
    return selected


def inject_tokens(words: list[str], tokens: list[str]) -> list[str]:
    """
    Randomly attaches tokens (numbers/symbols) to the start or end of words.
    
    Args:
        words: The list of base words.
        tokens: The list of special characters/numbers to inject.
        
    Returns:
        list[str]: The decorated list of words.
    """
    decorated = [{"pre": "", "word": w, "post": ""} for w in words]
    
    for token in tokens:
        target = random.choice(decorated)
        # Flip a coin for prefix vs suffix placement
        if random.random() < 0.5:
            target["pre"] += token
        else:
            target["post"] += token
            
    return [f"{d['pre']}{d['word']}{d['post']}" for d in decorated]


def generate_passphrase(n_words: int, n_specials: int, n_numbers: int) -> tuple[str, float]:
    """
    Generates a single passphrase and calculates its estimated entropy.

    Entropy is calculated using a heuristic model:
        H = log2(PoolSize ^ Count) + PermutationFactors

    Args:
        n_words: Number of words.
        n_specials: Number of special characters.
        n_numbers: Number of digits.

    Returns:
        tuple: (passphrase_string, entropy_bits)
    """
    words = select_words(n_words)
    
    # Gather and shuffle tokens
    pool = [random.choice(SPECIALS) for _ in range(max(0, n_specials))]
    pool += [random.choice(NUMBERS) for _ in range(max(0, n_numbers))]
    random.shuffle(pool)

    # Assemble
    passphrase = "".join(inject_tokens(words, pool))

    # Entropy Calculation
    total_vocab = sum(len(l) for l in WORD_LISTS)
    avg_vocab = total_vocab / max(1, len(WORD_LISTS))
    
    entropy = (
        n_words * math.log2(max(2, avg_vocab)) +
        n_specials * (math.log2(len(SPECIALS)) if SPECIALS else 0) +
        n_numbers * (math.log2(len(NUMBERS)) if NUMBERS else 0) +
        # Add permutation factor for token placement (approx. 2 slots per word)
        len(pool) * math.log2(2 * max(1, n_words))
    )
    
    return passphrase, entropy


def log_to_history(passwords: list[str]) -> None:
    """Appends generated passwords to the plaintext log file."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            for pw in passwords:
                f.write(pw + "\n")
    except OSError as e:
        print(f"Logging failed: {e}")


def purge_history() -> None:
    """Deletes the history file from the disk."""
    if LOG_FILE.exists():
        LOG_FILE.unlink()


# -----------------------------------------------------------------------------
# GRAPHICAL USER INTERFACE
# -----------------------------------------------------------------------------

class TeletextApp(tk.Tk):
    """
    Main Application Window.
    Implements the 'Ceefax/Oracle' visual style using standard Tkinter widgets.
    """

    def __init__(self) -> None:
        # 'className' is CRITICAL for Linux/Gnome taskbar grouping.
        # It must match the StartupWMClass in the .desktop file.
        super().__init__(className="ravenfoot-p100")
        
        self.title("RAVENFOOT P100")
        self.configure(bg=COL_BG)
        self.geometry("800x600")
        
        # Keep a strong reference to the icon to prevent garbage collection by Python
        self._icon_ref = None 
        
        self.configure_branding()
        self.build_ui()
        
        # Start Clock Loop
        self.after(1000, self.update_clock)

    def configure_branding(self) -> None:
        """Applies OS-specific window icons (ICO for Windows, PNG for Linux)."""
        try:
            if sys.platform.startswith("win"):
                # Windows: Uses .ico for the window frame
                icon_path = resource_path(ICON_WIN)
                if icon_path.exists():
                    self.iconbitmap(icon_path)
            else:
                # Linux: Uses .png (Requires Pillow for best results)
                icon_path = resource_path(ICON_LIN)
                if icon_path.exists():
                    if HAS_PIL:
                        img = Image.open(icon_path)
                        self._icon_ref = ImageTk.PhotoImage(img)
                    else:
                        self._icon_ref = PhotoImage(file=str(icon_path))
                    self.iconphoto(True, self._icon_ref)
        except Exception as e:
            print(f"Branding Warning: {e}")

    def build_ui(self) -> None:
        """Constructs the widget hierarchy."""
        # 1. Header (Blue Bar)
        header = tk.Frame(self, bg=COL_BLUE, height=50)
        header.pack(fill="x", side="top")
        
        tk.Label(header, text="P100", fg=COL_TEXT, bg=COL_BLUE, font=FONT_HEADER).pack(side="left", padx=10)
        tk.Label(header, text="RAVENFOOT PASSWORDS", fg=COL_YELL, bg=COL_BLUE, font=FONT_HEADER).pack(side="left", expand=True)
        
        self.clock_lbl = tk.Label(header, text="--:--", fg=COL_TEXT, bg=COL_BLUE, font=FONT_MAIN)
        self.clock_lbl.pack(side="right", padx=10)

        # 2. Status Row
        status_row = tk.Frame(self, bg=COL_BG)
        status_row.pack(fill="x", pady=(10, 5), padx=20)
        tk.Label(status_row, text="SECURE LINK ESTABLISHED...", fg=COL_CYAN, bg=COL_BG, font=FONT_MAIN).pack(side="left")
        self.entropy_display = tk.Label(status_row, text="ENTROPY: --", fg=COL_GREEN, bg=COL_BG, font=FONT_MAIN)
        self.entropy_display.pack(side="right")

        # 3. Inputs
        input_frame = tk.Frame(self, bg=COL_BG)
        input_frame.pack(fill="x", padx=20, pady=5)

        self.input_words = self._create_input(input_frame, "WORDS....", "4", 0)
        self.input_specials = self._create_input(input_frame, "SPECIALS.", "2", 2)
        self.input_numbers = self._create_input(input_frame, "NUMBERS..", "1", 4)

        # 4. Results Area
        self.results_frame = tk.Frame(self, bg=COL_BG)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 5. Control Bar (Fastext Buttons)
        control_bar = tk.Frame(self, bg=COL_BG)
        control_bar.pack(side="bottom", fill="x", pady=20, padx=20)
        
        self._create_fastext_btn(control_bar, "GENERATE", COL_GREEN, self.on_generate)
        self._create_fastext_btn(control_bar, "CLEAR LOG", COL_RED, self.on_clear_log)
        self._create_fastext_btn(control_bar, "CLOSE", COL_CYAN, self.destroy)

        # Initial calculation
        self.update_entropy_display()

    def _create_input(self, parent, label, default, col) -> tk.Entry:
        """Factory method for creating standardized labeled inputs."""
        tk.Label(parent, text=label, fg=COL_YELL, bg=COL_BG, font=FONT_MAIN).grid(row=0, column=col, sticky="w")
        entry = tk.Entry(parent, width=4, bg=COL_BG, fg=COL_TEXT, font=FONT_INPUT, insertbackground=COL_TEXT, relief="flat")
        entry.insert(0, default)
        entry.grid(row=0, column=col+1, sticky="w", padx=10)
        
        # Pseudo-underline for Teletext look
        underline = tk.Frame(parent, bg=COL_TEXT, height=2, width=40)
        underline.grid(row=1, column=col+1, sticky="w", padx=10, pady=(0, 10))
        
        entry.bind("<KeyRelease>", lambda e: self.update_entropy_display())
        return entry

    def _create_fastext_btn(self, parent, text, color, command) -> None:
        """Factory method for creating 'Fastext' style block buttons."""
        container = tk.Frame(parent, bg=color, padx=2, pady=2)
        container.pack(side="left", fill="x", expand=True, padx=5)
        
        btn = tk.Button(container, text=text, command=command, bg=COL_BG, fg=color, 
                        activebackground=color, activeforeground=COL_BG, 
                        font=FONT_MAIN, relief="flat", cursor="hand2")
        btn.pack(fill="both", expand=True)

    def update_clock(self) -> None:
        """Updates the header clock label every minute."""
        now = datetime.now().strftime("%a %d %b %H:%M")
        self.clock_lbl.config(text=now)
        self.after(60000, self.update_clock)

    def update_entropy_display(self) -> None:
        """Recalculates entropy based on current inputs and updates the UI."""
        try:
            n_w = int(self.input_words.get())
            n_s = int(self.input_specials.get())
            n_n = int(self.input_numbers.get())
            _, bits = generate_passphrase(n_w, n_s, n_n)
            self.entropy_display.config(text=f"ENTROPY: {bits:.1f} BITS", fg=COL_GREEN)
        except ValueError:
            self.entropy_display.config(text="ENTROPY: ERR", fg=COL_RED)

    def on_generate(self) -> None:
        """Event handler for the Generate button."""
        # Clean old results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        try:
            n_w = int(self.input_words.get())
            n_s = int(self.input_specials.get())
            n_n = int(self.input_numbers.get())
        except ValueError:
            messagebox.showerror("Error", "Inputs must be whole numbers.")
            return

        passwords = []
        for i in range(10):
            pw, _ = generate_passphrase(n_w, n_s, n_n)
            passwords.append(pw)
            
            row = tk.Frame(self.results_frame, bg=COL_BG)
            row.pack(fill="x", pady=2)
            
            # Index
            tk.Label(row, text=f"{i+1:02d}", fg=COL_YELL, bg=COL_BG, font=FONT_MAIN).pack(side="left", padx=(0, 10))
            # Password
            tk.Label(row, text=pw, fg=COL_TEXT, bg=COL_BG, font=FONT_MAIN).pack(side="left")
            # Copy Link
            link = tk.Label(row, text="[COPY]", fg=COL_CYAN, bg=COL_BG, font=FONT_MAIN, cursor="hand2")
            link.pack(side="right")
            link.bind("<Button-1>", lambda e, p=pw, l=link: self.on_copy(p, l))

        log_to_history(passwords)

    def on_copy(self, text, widget) -> None:
        """Clipboard helper that provides visual feedback to the user."""
        self.clipboard_clear()
        self.clipboard_append(text)
        original_text = widget.cget("text")
        widget.config(text="DONE!", fg=COL_GREEN)
        self.after(1000, lambda: widget.config(text=original_text, fg=COL_CYAN))

    def on_clear_log(self) -> None:
        """Event handler for the Clear Log button."""
        purge_history()
        self.entropy_display.config(text="LOG DELETED", fg=COL_RED)
        self.after(1500, self.update_entropy_display)


if __name__ == "__main__":
    app = TeletextApp()
    app.mainloop()