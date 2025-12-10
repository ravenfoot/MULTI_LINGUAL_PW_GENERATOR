"""
Ravenfoot Password Generator (Teletext Edition) — v2 portable
================================================================
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

# Optional Pillow for nicer icon scaling (falls back to Tk's PhotoImage).
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except Exception:
    HAS_PIL = False
    from tkinter import PhotoImage  # type: ignore

# -----------------------------------------------------------------------------
# Portable path helpers
# -----------------------------------------------------------------------------
def resource_path(*segments: str) -> Path:
    """
    Return an absolute path to bundled/static resources.

    Works in both:
      • Development: base = project root (…/ravenfoot_password_generator)
      • PyInstaller (--onefile): base = sys._MEIPASS temporary dir

    Parameters
    ----------
    *segments : str
        Path fragments to append to the base.

    Returns
    -------
    Path
        Absolute path to the requested resource.
    """
    base = getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1])
    return Path(base, *segments)


def user_history_path() -> Path:
    """
    Compute a cross-platform, user-writable path for the history log.

    On Windows, prefers %APPDATA%. On POSIX, uses ~/.ravenfoot_password/.

    Returns
    -------
    Path
        Absolute path to the plaintext history file.
    """
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
        return base / "RavenfootPassword" / "password_history.txt"
    else:
        base = Path.home() / ".ravenfoot_password"
        return base / "password_history.txt"


# -----------------------------------------------------------------------------
# Configuration / Constants
# -----------------------------------------------------------------------------
ROOT         = resource_path()
LIBRARY_DIR  = resource_path("library")
HISTORY_PATH = user_history_path()
ICON_PATH    = resource_path("gui", "logo", "ravenfootlogo_icon.png")

# Teletext palette & typography (fixed-width for the retro look)
FONT_MAIN   = ("Courier New", 12, "bold")
FONT_HEADER = ("Courier New", 24, "bold")
FONT_INPUT  = ("Courier New", 14, "bold")

COL_BG    = "#000000"  # black
COL_TEXT  = "#FFFFFF"  # white
COL_CYAN  = "#00FFFF"
COL_YELL  = "#FFFF00"
COL_GREEN = "#00FF00"
COL_RED   = "#FF0000"
COL_BLUE  = "#0000FF"


# -----------------------------------------------------------------------------
# Dynamic loaders
# -----------------------------------------------------------------------------
def load_file_lines(path: Path) -> list[str]:
    """
    Load non-empty, stripped lines from `path`. UTF-8 with ignore for safety.

    Parameters
    ----------
    path : Path
        File to load.

    Returns
    -------
    list[str]
        List of trimmed lines, or [] if the file doesn't exist.
    """
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]


# Load token sources (with minimal fallbacks to keep the UI operable)
SPECIALS = load_file_lines(LIBRARY_DIR / "special_characters.txt") or ["!"]
NUMBERS  = load_file_lines(LIBRARY_DIR / "numbers.txt") or ["1"]

# Load any wordlist matching "*_words_clean.txt" to allow multilingual mixes
WORD_LISTS: list[list[str]] = []
for wf in sorted(LIBRARY_DIR.glob("*_words_clean.txt")):
    words = load_file_lines(wf)
    if words:
        WORD_LISTS.append(words)

if not WORD_LISTS:
    # Last-ditch fallback so the app still runs visibly.
    WORD_LISTS = [["error", "missing", "words"]]


# -----------------------------------------------------------------------------
# Generator logic
# -----------------------------------------------------------------------------
def pick_words_dynamic(n_words: int) -> list[str]:
    """
    Select `n_words` across available wordlists.

    Guarantees:
      • If there's only one list OR n_words == 1 → sample from that list.
      • If >= 2 lists AND n_words >= 2 → ensure at least two distinct lists
        contribute (improves linguistic variety).

    Parameters
    ----------
    n_words : int
        Number of words to include.

    Returns
    -------
    list[str]
        Selected words in random order (length may be 0 if n_words <= 0).
    """
    if n_words <= 0:
        return []

    if len(WORD_LISTS) == 1 or n_words == 1:
        chosen_list = WORD_LISTS[0]
        return [random.choice(chosen_list) for _ in range(n_words)]

    # Ensure diversity when we can: seed with two different lists.
    lists = list(range(len(WORD_LISTS)))
    random.shuffle(lists)
    idx_a, idx_b = lists[0], lists[1]
    selected = [random.choice(WORD_LISTS[idx_a]), random.choice(WORD_LISTS[idx_b])]

    # Fill remaining slots from any lists
    while len(selected) < n_words:
        li = random.choice(WORD_LISTS)
        selected.append(random.choice(li))

    random.shuffle(selected)
    return selected


def distribute_tokens(words: list[str], tokens: list[str]) -> list[str]:
    """
    Distribute `tokens` around `words` by randomly prefixing or suffixing tokens.

    This keeps words as the spine of the passphrase while adding entropy via
    symbol/number placement.

    Parameters
    ----------
    words : list[str]
        Base words for the passphrase.
    tokens : list[str]
        Symbols and/or digits to be inserted.

    Returns
    -------
    list[str]
        Words decorated with randomly placed tokens.
    """
    decorated = [{"pre": "", "word": w, "post": ""} for w in words]
    for t in tokens:
        idx = random.randrange(len(decorated))
        if random.random() < 0.5:
            decorated[idx]["pre"] += t
        else:
            decorated[idx]["post"] += t
    return [f"{d['pre']}{d['word']}{d['post']}" for d in decorated]


def generate_password(n_words: int, n_specials: int, n_numbers: int) -> tuple[str, float]:
    """
    Generate a password and a rough entropy estimate (bits).

    Entropy model (heuristic):
      • Word choices: n_words * log2(avg_vocab_size)
      • Specials:     n_specials * log2(|SPECIALS|)
      • Numbers:      n_numbers  * log2(|NUMBERS|)
      • Placement:    log2(choices) for where tokens land (prefix/suffix across words)

    Parameters
    ----------
    n_words : int
        Number of words to include.
    n_specials : int
        Count of special characters to add.
    n_numbers : int
        Count of digits to add.

    Returns
    -------
    tuple[str, float]
        (password_string, entropy_bits)
    """
    words = pick_words_dynamic(n_words)

    # Build token pool then shuffle so placement feels organic.
    tokens = [random.choice(SPECIALS) for _ in range(max(0, n_specials))]
    tokens += [random.choice(NUMBERS) for _ in range(max(0, n_numbers))]
    random.shuffle(tokens)

    pw = "".join(distribute_tokens(words, tokens))

    # Pragmatic entropy approximation for UX feedback:
    total_vocab = sum(len(l) for l in WORD_LISTS)
    avg_vocab = total_vocab / max(1, len(WORD_LISTS))
    entropy = (
        n_words    * math.log2(max(2, avg_vocab))
        + n_specials * (math.log2(len(SPECIALS)) if SPECIALS else 0.0)
        + n_numbers  * (math.log2(len(NUMBERS))  if NUMBERS  else 0.0)
        + len(tokens) * math.log2(2 * max(1, n_words))  # 2 placements (pre/post) × slots
    )
    return pw, entropy


def append_history(lines: list[str]) -> None:
    """
    Append generated passwords to the history file (plaintext).

    Parameters
    ----------
    lines : list[str]
        One password per list element.
    """
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_PATH.open("a", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


def clear_history() -> None:
    """
    Delete the history file if it exists.

    Notes
    -----
    This is a best-effort convenience feature. It does not guarantee secure
    deletion from storage media.
    """
    if HISTORY_PATH.exists():
        HISTORY_PATH.unlink()


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------
class TeletextGUI(tk.Tk):
    """
    Teletext-styled Tkinter application.

    Responsibilities
    ----------------
    - Layout the header/clock, inputs, output list, and bottom bar.
    - Manage user interactions (generate, copy, clear log).
    - Provide continuous entropy feedback as the user edits inputs.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("RAVENFOOT P100")
        self.configure(bg=COL_BG)
        self.geometry("800x600")

        self._icon: PhotoImage | ImageTk.PhotoImage | None = None

        self.setup_icon()
        self.create_interface()

        # Optional: live clock in header (refresh every 60s)
        self.after(1000, self._tick_clock)

    def setup_icon(self) -> None:
        """Load and set a 32x32 app icon if available (Pillow optional)."""
        if not ICON_PATH.exists():
            return
        try:
            if HAS_PIL:
                img = Image.open(ICON_PATH)
                img = img.resize((32, 32), Image.LANCZOS)
                self._icon = ImageTk.PhotoImage(img)
            else:
                self._icon = PhotoImage(file=str(ICON_PATH))
            self.iconphoto(True, self._icon)
        except Exception:
            # Icon is non-critical; ignore failures silently.
            pass

    def create_interface(self) -> None:
        """Build the full UI: header, info row, inputs, list, and buttons."""
        # === 1) HEADER (Blue banner) ===
        header = tk.Frame(self, bg=COL_BLUE, height=50)
        header.pack(fill="x", side="top")

        tk.Label(header, text="P100", fg=COL_TEXT, bg=COL_BLUE, font=FONT_HEADER).pack(
            side="left", padx=10
        )
        tk.Label(
            header,
            text="RAVENFOOT PASSWORDS",
            fg=COL_YELL,
            bg=COL_BLUE,
            font=FONT_HEADER,
        ).pack(side="left", expand=True)
        self.clock_lbl = tk.Label(
            header, text=self._clock_text(), fg=COL_TEXT, bg=COL_BLUE, font=FONT_MAIN
        )
        self.clock_lbl.pack(side="right", padx=10)

        # === 2) SUB-HEADER / ENTROPY ===
        info = tk.Frame(self, bg=COL_BG)
        info.pack(fill="x", pady=(10, 5), padx=20)

        tk.Label(
            info, text="SECURE LINK ESTABLISHED...", fg=COL_CYAN, bg=COL_BG, font=FONT_MAIN
        ).pack(side="left")

        self.entropy_label = tk.Label(
            info, text="ENTROPY: -- BITS", fg=COL_GREEN, bg=COL_BG, font=FONT_MAIN
        )
        self.entropy_label.pack(side="right")

        # === 3) INPUT GRID ===
        grid = tk.Frame(self, bg=COL_BG)
        grid.pack(fill="x", padx=20, pady=5)

        def make_input(label: str, default: str, col: int) -> tk.Entry:
            """Create a labeled numeric entry with teletext underline."""
            tk.Label(grid, text=label, fg=COL_YELL, bg=COL_BG, font=FONT_MAIN).grid(
                row=0, column=col, sticky="w"
            )
            e = tk.Entry(
                grid,
                width=4,
                bg=COL_BG,
                fg=COL_TEXT,
                font=FONT_INPUT,
                insertbackground=COL_TEXT,
                relief="flat",
            )
            e.insert(0, default)
            e.grid(row=0, column=col + 1, sticky="w", padx=10)
            underline = tk.Frame(grid, bg=COL_TEXT, height=2, width=40)
            underline.grid(row=1, column=col + 1, sticky="w", padx=10, pady=(0, 10))
            e.bind("<KeyRelease>", lambda _e: self.update_entropy())
            return e

        self.entry_words = make_input("WORDS....", "4", 0)
        self.entry_specials = make_input("SPECIALS.", "2", 2)
        self.entry_numbers = make_input("NUMBERS..", "1", 4)

        # === 4) PASSWORD LIST ===
        self.password_frame = tk.Frame(self, bg=COL_BG)
        self.password_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # === 5) BOTTOM (Fastext-style) buttons ===
        bar = tk.Frame(self, bg=COL_BG)
        bar.pack(side="bottom", fill="x", pady=20, padx=20)

        def fastext_button(text: str, color: str, cmd) -> None:
            """Create a faux-teletext colored button block."""
            block = tk.Frame(bar, bg=color, padx=2, pady=2)
            block.pack(side="left", fill="x", expand=True, padx=5)
            btn = tk.Button(
                block,
                text=text,
                command=cmd,
                bg=COL_BG,
                fg=color,
                activebackground=color,
                activeforeground=COL_BG,
                font=FONT_MAIN,
                relief="flat",
                cursor="hand2",
            )
            btn.pack(fill="both", expand=True)

        fastext_button("GENERATE", COL_GREEN, self.generate)
        fastext_button("CLEAR LOG", COL_RED, self.clear_log)
        fastext_button("CLOSE", COL_CYAN, self.destroy)

        self.update_entropy()

    # ----- Header clock helpers ------------------------------------------------
    def _clock_text(self) -> str:
        """Return a short timestamp (e.g., 'Tue 09 Dec 10:32')."""
        return datetime.now().strftime("%a %d %b %H:%M")

    def _tick_clock(self) -> None:
        """Update the header clock once per minute."""
        self.clock_lbl.config(text=self._clock_text())
        self.after(60000, self._tick_clock)

    # ----- UX actions ----------------------------------------------------------
    def update_entropy(self) -> None:
        """Recompute and display entropy as the user edits numeric inputs."""
        try:
            n_w = int(self.entry_words.get())
            n_s = int(self.entry_specials.get())
            n_n = int(self.entry_numbers.get())
            _, bits = generate_password(n_w, n_s, n_n)
            self.entropy_label.config(text=f"ENTROPY: {bits:.1f} BITS", fg=COL_GREEN)
        except ValueError:
            self.entropy_label.config(text="ENTROPY: ERR", fg=COL_RED)

    def generate(self) -> None:
        """Generate 10 passwords, render them with [COPY] links, and append history."""
        # Clear previous results
        for w in self.password_frame.winfo_children():
            w.destroy()

        # Validate numeric entries
        try:
            n_w = int(self.entry_words.get())
            n_s = int(self.entry_specials.get())
            n_n = int(self.entry_numbers.get())
        except ValueError:
            messagebox.showerror("Input error", "WORDS/SPECIALS/NUMBERS must be integers.")
            return

        # Build list view
        results: list[str] = []
        for i in range(10):
            pw, _ = generate_password(n_w, n_s, n_n)
            results.append(pw)

            row = tk.Frame(self.password_frame, bg=COL_BG)
            row.pack(fill="x", pady=2)

            tk.Label(row, text=f"{i+1:02d}", fg=COL_YELL, bg=COL_BG, font=FONT_MAIN).pack(
                side="left", padx=(0, 10)
            )
            tk.Label(row, text=pw, fg=COL_TEXT, bg=COL_BG, font=FONT_MAIN).pack(
                side="left", expand=True, anchor="w"
            )

            link = tk.Label(
                row, text="[COPY]", fg=COL_CYAN, bg=COL_BG, font=FONT_MAIN, cursor="hand2"
            )
            link.pack(side="right")
            # Use default argument binding to capture current pw/link
            link.bind("<Button-1>", lambda _e, p=pw, l=link: self.copy_to_clipboard(p, l))

        append_history(results)

    def copy_to_clipboard(self, text: str, widget: tk.Label) -> None:
        """Copy `text` to clipboard and flash a short visual confirmation."""
        self.clipboard_clear()
        self.clipboard_append(text)
        original = widget.cget("text")
        widget.config(text="DONE!", fg=COL_GREEN)
        self.after(1000, lambda: widget.config(text=original, fg=COL_CYAN))

    def clear_log(self) -> None:
        """Delete the plaintext history file and briefly notify in the UI."""
        clear_history()
        self.entropy_label.config(text="LOG DELETED", fg=COL_RED)
        self.after(1500, self.update_entropy)


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    TeletextGUI().mainloop()
