# TypeStrike - the typing tutor beat 'em up

Type to fight. Every correct key is a punch, kick or sword strike; every word is an enemy. 150 lessons teach real touch typing, from the home row to code and office writing.

## Download (no Python needed)
Go to the **[Releases page](../../releases/latest)** of this repository and download the file for your system:

| System | File | How to start |
|---|---|---|
| Windows 10/11 | `TypeStrike-Windows.exe` | Double-click. If SmartScreen warns ("unknown publisher"), click **More info -> Run anyway** (the app is not code-signed). |
| macOS (Apple Silicon) | `TypeStrike-macOS.zip` | Unzip, then **right-click TypeStrike.app -> Open** the first time (not notarised). Intel Macs: use the "Run from source" way below. |
| Linux (x86-64) | `TypeStrike-Linux.tar.gz` | `tar xzf TypeStrike-Linux.tar.gz && ./TypeStrike`. Sound needs `paplay`, `pw-play` or `aplay` (already there on most desktops). |

On Windows the game opens as a transparent overlay on your desktop (emergency quit: Ctrl+Shift+Q); start it with `--window` for a normal window. macOS and Linux always use a normal window.

## Run from source (any system with Python 3.9+)
| System | Install | Start |
|---|---|---|
| Windows | Python from python.org (Tk is included) | double-click `typestrike.pyw` (or `python typestrike.py`) |
| macOS | Python from python.org or `brew install python-tk` | `python3 typestrike.py` |
| Linux | `sudo apt install python3-tk` | `python3 typestrike.py` |

Windows starts as a transparent overlay on your desktop (emergency quit: Ctrl+Shift+Q). Use `--window` for a normal window on any system. No other packages are needed.
Your old Keyboard Warrior save is copied automatically on the first start (the game was renamed).

## What is inside
- **Typing Tutor (calm learning mode):** the 150 lessons as a classic typing course - no enemies. Each lesson explains the new keys with the finger that presses them, shows two hands with the right finger lit up, and gives 5 exercise lines. A wrong key does not move on. Pass with 90% accuracy to unlock the next lesson, earn up to 3 stars.
- **Campaign, 150 lessons in 15 chapters:** home row, words, numbers, capitals, punctuation, sentences, symbols, speed, accuracy, paragraphs, office typing, code, endurance and grandmaster trials. Every lesson has a teaching card, sample text, a 3-star goal and a boss every 5 levels. Fail a level twice and assist mode softens it.
- **Moving while you fight:** Left/Right move or retreat, Up jumps (twice = flip), Down guards. Jump over ground waves, step out of lightning columns, dodge attacks.
- **Two-phase bosses:** 8 bosses with their own attacks. At half health they enrage.
- **8 heroes** with different looks and small perks, **19 weapons** and **11 fighting styles** (boxing, karate, muay thai, judo, wing chun, krav maga, taekwondo, jeet kune do, kung fu, capoeira, ninjutsu; knife, kunai, nunchaku, bo staff, katana, axes, hammers, twin starburst blades, fire / ice / storm swords ...). Each has its own moves and hit effects.
- **Modes:** Daily Challenge (a new theme every weekday, same for everyone), Challenge Mode (endless remix of everything you learned with rising speed and modifiers), Boss Rush (all 8 bosses back to back), Weak-Key Trainer (drills built from the keys you miss most), Custom Text (practise your own lines from `custom.txt`), Survival, Speed Test, Free Practice, Bangla typing (phonetic with English letters, or a real Bangla keyboard) and 53 achievements.
- **Sound:** 60+ effects synthesised by the game itself (first start takes a couple of seconds). `python typestrike.py --sounds` plays all of them.

## Keys
Type the highlighted word. Tab next target, Backspace unlock, Enter ULTIMATE (when the rage bar is full), Esc pause, F1 keyboard help, F2 theme, F3 volume, F4 difficulty.

## Build the apps yourself
`pip install pyinstaller`, then e.g. `pyinstaller --onefile --noconsole --name TypeStrike --add-data "assets/icon.png;assets" typestrike.py` (use `:` instead of `;` on macOS/Linux). The GitHub workflow in `.github/workflows/build.yml` does this for all three systems automatically.

## Settings you can change
- **Enemy speed - you choose** (0.25x very slow ... 3.0x very fast): on the level start card use the **- / +** buttons or the Left/Right keys; anywhere else press **F5**, or use the chip in the main menu / the pause screen. It is saved. Enemies also get faster with every level on their own (level 150 walks about 4x faster than level 1); your setting multiplies that. Start with `--speed 0.6` for a slower game.
- **Difficulty** (F4), **sound** (F3), **theme** (F2).
- **Bangla display fix** (Bangla map screen): some systems (for example Tk on Linux) cannot lay out Bangla vowel signs correctly. The game detects this automatically and reorders the letters itself. If Bangla still looks wrong or double-fixed on your computer, click the button to switch it ON/OFF.

## Troubleshooting
- **Windows: nothing visible / overlay is confusing** - run `TypeStrike-Windows.exe --window` for a normal window. Quit anytime with Ctrl+Shift+Q.
- **Linux: no sound** - install `pulseaudio-utils` (paplay) or `alsa-utils` (aplay). **Bangla letters show as boxes** - install a Bengali font (`sudo apt install fonts-noto`); letters jumbled - use the Bangla display fix button.
- **macOS: "cannot be opened"** - right-click the app, choose Open, confirm once. If Python's Tk is missing when running from source: `brew install python-tk`.
- Anything strange: look at `~/.typestrike/error.log` and open an issue with its content.

## Notes
- Saves, settings and generated sound files: `~/.typestrike/` (errors in `error.log`).
- Bangla native mode: switch your OS keyboard to Bangla first (Windows: Win+Space).
- Tests (no display needed): `python tests/smoke_test.py`


## License
TypeStrike is **free for personal, educational and other noncommercial use** under the [PolyForm Noncommercial License 1.0.0](LICENSE). You may play it, study the code, change it and share it - but you may **not sell it or use it commercially** (paid apps, app-store listings, paid services, selling copies) without written permission from the author. Please keep the licence and the "Required Notice" line when you share it.
Copyright (c) 2026 Shadid.
