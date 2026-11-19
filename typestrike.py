#!/usr/bin/env python3
"""TYPESTRIKE - a typing tutor beat 'em up.  Windows, macOS and Linux.  Only needs Python 3 with Tk.

Type the text above each enemy. Every correct key throws a strike, the last key throws a finisher.
Learn touch typing from the home row to full sentences, earn coins, buy swords and fighting styles.

    python typestrike.py              Windows: transparent overlay on your desktop. macOS / Linux: game window.
    python typestrike.py --window     normal window on any system
    python typestrike.py --overlay    transparent overlay (Windows; experimental on macOS)

Menu : Up/Down choose, Left/Right change level, Enter select      F2 theme   F3 volume   F4 difficulty   F11 fullscreen
Game : Backspace unlock target   Tab next target   Enter ULTIMATE (RAGE full)   F1 keyboard help   Esc pause
Windows overlay only: Ctrl+Shift+Q = emergency quit.     Data: ~/.typestrike/
"""
import tkinter as tk, tkinter.font as tkf, ctypes, math, random, time, json, os, sys, string, argparse, traceback, datetime, wave, struct, subprocess, shutil, textwrap
from types import SimpleNamespace as NS
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ts_data as KD, ts_sound
from ts_meta import HEROES, HORDER, HGIFT, BOSSES, ACH

# ============================================================== platform, paths, save data
PLAT = 'win' if sys.platform.startswith('win') else ('mac' if sys.platform == 'darwin' else 'linux')
ap = argparse.ArgumentParser(description='TypeStrike - typing tutor beat em up')
ap.add_argument('--level', type=int, default=0, help='start on this campaign level')
ap.add_argument('--overlay', action='store_true', help='transparent desktop overlay (default on Windows)')
ap.add_argument('--window', action='store_true', help='normal window (default on macOS / Linux)')
ap.add_argument('--speed', type=float, default=None, help='enemy speed multiplier, e.g. 0.6 (slow) or 1.5 (fast)')
ap.add_argument('--version', action='version', version='TypeStrike ' + '1.2.0')
ap.add_argument('--no-sound', action='store_true', help='disable all sound effects')
ap.add_argument('--sounds', action='store_true', help='play every sound effect once (sound test) and exit')
A, _ = ap.parse_known_args()
OVERLAY = (PLAT == 'win' and not A.window) or (PLAT == 'mac' and A.overlay)
DEBUG = bool(os.environ.get('KW_DEBUG'))
DATA = os.path.join(os.path.expanduser('~'), '.typestrike'); _OLD = os.path.join(os.path.expanduser('~'), '.keyboard_warrior')
try:
    _fresh = not os.path.exists(os.path.join(DATA, 'save.json')); os.makedirs(DATA, exist_ok=True)
    if _fresh and os.path.exists(os.path.join(_OLD, 'save.json')): shutil.copy(os.path.join(_OLD, 'save.json'), os.path.join(DATA, 'save.json'))   # keep progress from the old name

except Exception: DATA = os.path.expanduser('~')
SAVE = os.path.join(DATA, 'save.json'); LOG = os.path.join(DATA, 'error.log'); SFXDIR = os.path.join(DATA, 'sfx_v3'); LOGN = [0]
def log(s):
    LOGN[0] += 1
    if LOGN[0] > 60: return
    try:
        with open(LOG, 'a') as f: f.write(time.strftime('%Y-%m-%d %H:%M:%S ') + s + '\n')
    except Exception: pass

D = {}
try:
    with open(SAVE) as f: D = json.load(f)
except Exception:
    try:
        with open(os.path.join(os.path.expanduser('~'), 'keyboard_warrior_save.json')) as f: D = json.load(f)
    except Exception: D = {}
if not isinstance(D, dict): D = {}
for _k, _v in dict(unlocked=1, best_wpm=0, att={}, miss={}, theme='dark', sound=True, vol=2, diff=2, stars={}, hist=[], keys=0, sessions=0, surv=0, test=0, streak=0, day='',
                   coins=0, rush=0, tutor_ul=1, tutor_stars={}, speed=1.0, bn_fix='auto', owned=['fists'], own_styles=['boxing'], weapon='fists', style='boxing', own_heroes=['kai'], hero='kai', ach={}, chal=0, bn_unlocked=1, bn_stars={}, bn_native=False, daily={}, fails={},
                   st=dict(kills=0, bosses=0, dodges=0, jumps=0, combo=0, perfect=0, daily=0, surv=0, bn=0, ults=0, flawless=0, earned=0)).items(): D.setdefault(_k, _v)
for _k, _v in dict(kills=0, bosses=0, dodges=0, jumps=0, combo=0, perfect=0, daily=0, surv=0, bn=0, ults=0, flawless=0, earned=0).items(): D['st'].setdefault(_k, _v)
D['unlocked'] = max(1, min(KD.TOTAL, int(D['unlocked'])))
if D.get('sound') is False: D['vol'] = 0; D['sound'] = True
att, miss = D['att'], D['miss']
def save():
    try:
        with open(SAVE, 'w') as f: json.dump(D, f)
    except Exception: pass
def DM(): return [.8, 1, 1.3][D['diff'] - 1]
def bump_streak():
    t = datetime.date.today()
    if D.get('day') == str(t): return
    try: ld = datetime.date.fromisoformat(D.get('day'))
    except Exception: ld = None
    D['streak'] = D['streak'] + 1 if (ld and (t - ld).days == 1) else 1; D['day'] = str(t)

# ============================================================== theme
TH = {'dark': dict(pan='#12162c', edge='#3a4a7a', tx='#f2f5ff', dim='#8794bd', acc='#ffd24a', good='#5fe38a', bad='#ff5d5d', hero='#ffffff', rear='#262d55', belt='#ffd24a', key='#161b36', off='#3a4260', gnd='#3fae6a', sh='#000000', cy='#4dd2ff', sel='#ffd24a', seltx='#12162c'),
      'light': dict(pan='#f6f8ff', edge='#7f8cc0', tx='#141a33', dim='#59648f', acc='#b86e00', good='#188a46', bad='#d12a2a', hero='#101a36', rear='#a3aed4', belt='#e09000', key='#ffffff', off='#aab3d6', gnd='#23844b', sh='#000000', cy='#0a7fb0', sel='#1d4ed8', seltx='#ffffff')}
def C(k): return TH[D['theme']][k]
FCD = ['#ff6b6b', '#ffa94d', '#ffe066', '#69db7c', '#4dd2ff', '#748ffc', '#da77f2', '#ff8cc8', '#b0b8d0']
FCL = ['#d6303a', '#d9730d', '#b58900', '#2f9e44', '#1c7ed6', '#4263eb', '#ae3ec9', '#d6336c', '#6b7699']
def fc(i): return (FCD if D['theme'] == 'dark' else FCL)[i]
ECD = dict(grunt='#ff6b6b', fast='#ffa94d', tank='#4dabf7', boss='#c77dff', ninja='#9d7bff', archer='#8fe388', shield='#aab6c8', bomber='#ff5fb0', healer='#63e6be')
ECL = dict(grunt='#d6303a', fast='#d9730d', tank='#1c7ed6', boss='#862e9c', ninja='#5f3dc4', archer='#2b8a3e', shield='#5c6b82', bomber='#c2255c', healer='#0b7285')
def ec(k): return (ECD if D['theme'] == 'dark' else ECL)[k]
def mix(a, b, t): return '#%02x%02x%02x' % tuple(int(int(a[i:i + 2], 16) * (1 - t) + int(b[i:i + 2], 16) * t) for i in (1, 3, 5))

# ============================================================== curriculum (150 lessons live in ts_data.py)
GR = KD.GR; MODEDESC = KD.MODEDESC; TOTAL = KD.TOTAL; info = KD.info; allowed = KD.allowed; tgt_wpm = KD.tgt_wpm
RANKS = [(0, 'Rookie'), (15, 'Apprentice'), (25, 'Fighter'), (35, 'Warrior'), (45, 'Master'), (60, 'Grandmaster'), (80, 'Legend')]
def rank(w): return [n for t, n in RANKS if w >= t][-1]
TIPS = ['Keep your wrists floating above the desk, not resting on it.', 'Sit straight, feet flat, screen at eye level.', 'Never look at the keyboard. Trust your fingers.', 'Accuracy first. Speed comes by itself.',
        'Use your thumb for Space, always.', 'After each key, let the finger return to the home row.', 'Stay relaxed. Tense fingers type slower.', 'Made a mistake? Do not rush. Slow down and find your rhythm.',
        'A steady rhythm beats fast chaos.', 'Ten minutes every day beats one long session a week.']
KD.WEAK['miss'] = miss; KD.WEAK['att'] = att
WR = random.Random()
FGM = {}
for _i, _s in enumerate(['1qaz`', '2wsx', '3edc', '45rfvtgb', '67yhnujm', '8ik,', '9ol.', "0p;/'-=[]\\"]):
    for _c in _s: FGM[_c] = _i
FGM[' '] = 8
FN = ['left pinky', 'left ring', 'left middle', 'left index', 'right index', 'right middle', 'right ring', 'right pinky', 'thumb']
SHM = {'?': '/', '!': '1', '"': "'", ':': ';', '@': '2', '#': '3', '$': '4', '%': '5', '&': '7', '*': '8', '(': '9', ')': '0', '^': '6', '_': '-', '+': '=', '{': '[', '}': ']', '|': '\\', '<': ',', '>': '.', '~': '`'}
def bk(c):
    if c.isalpha(): return c.lower(), c.isupper()
    if c in SHM: return SHM[c], True
    return c, False
def fgi(c): return FGM.get(bk(c)[0], 8)
def disp(c): return 'Space' if c == ' ' else c

def lesson_now():
    """the lesson (dict) that is currently being played / generated from"""
    return g.les if g.les is not None else KD.lesson(g.cl)
def remix_level():
    ul = max(11, min(D['unlocked'], KD.TOTAL)); lo = max(11, ul - 30)
    for _ in range(12):
        n = WR.randint(lo, ul)
        if not KD.lesson(n)['boss'] and KD.lesson(n)['mode'] != 'mixed': return n
    return 12
def new_text(kind='grunt', avoid=(), boss=False):
    """-> (typed text, display text or None)"""
    if g.mode == 'bn':
        b, p = KD.bn_gen(g.cl, WR, D['bn_native'])
        if boss and g.cl >= 6: b2, p2 = KD.bn_gen(g.cl, WR, D['bn_native']); b, p = b + ' ' + b2, p + ' ' + p2
        return (b, None) if D['bn_native'] else (p, b)
    if g.mode == 'custom': t = g.cust[g.cidx % len(g.cust)]; g.cidx += 1; return t, None
    L = g.gl if g.gl is not None else g.cl
    return (KD.boss_text(L, WR) if boss else KD.gen(L, WR, avoid, kind)), None
def max_alive():
    les = lesson_now(); m = les['mode']; ma = les.get('ma') or (2 + (g.cl >= 30) + (g.cl >= 90 and m not in KD.LONG_MODES))
    if g.mode == 'chal': ma = 2 + min(3, g.wv // 6) + (2 if g.mod == 'swarm' else 0)
    if m in KD.LONG_MODES: ma = min(ma, 3)
    if les.get('hi', 0) > 90: ma = min(ma, 2)
    return ma
def level_speed(L): return (28 + .62 * max(1, min(L, 150))) * SW / 1920       # enemy walking speed in px/s - rises with every level
def enemy_speed(w, L, boss=False):
    les = lesson_now(); lenf = 1 / (1 + max(0, len(w) - 12) / 25)             # very long sentences get a little more walking time
    return max(14, min(420, level_speed(L) * lenf * les.get('spd', 1.0) * (1.15 if g.mode == 'chal' else 1) * DM() * SPD() / g.assist / (1.7 if boss else 1)))
def budget(w, L, boss=False):
    cps = tgt_wpm(L) * 5 / 60; les = lesson_now(); sp = les.get('spd', 1.0) * (1.15 if g.mode == 'chal' else 1)
    fac = min(max(2.3, max_alive() / .6), 4.2 if g.mode == 'chal' else 9)
    return min(70, (len(w) / cps * fac + 4.0)) * (1.7 if boss else 1) / DM() / sp / g.assist / SPD()

# ============================================================== window (overlay on Windows, normal window elsewhere)
KEYC = '#010101'
if PLAT == 'win':
    try: ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try: ctypes.windll.user32.SetProcessDPIAware()
        except Exception: pass
root = tk.Tk(); SCRW, SCRH = int(root.winfo_screenwidth()), int(root.winfo_screenheight())
if OVERLAY:
    SW, SH = SCRW, SCRH
    root.overrideredirect(True); root.attributes('-topmost', True)
    if PLAT == 'win': root.config(bg=KEYC); root.attributes('-transparentcolor', KEYC); CVBG = KEYC
    else: root.attributes('-transparent', True); root.config(bg='systemTransparent'); CVBG = 'systemTransparent'
    root.geometry(f'{SW}x{SH}+0+0')
else:
    SW, SH = int(SCRW * .9), int(SCRH * .86); root.title('TypeStrike - Typing Tutor'); CVBG = '#0b1030'
    root.geometry(f'{SW}x{SH}+{(SCRW - SW) // 2}+{max(0, (SCRH - SH) // 3)}'); root.minsize(980, 620)
cv = tk.Canvas(root, width=SW, height=SH, bg=CVBG, highlightthickness=0, bd=0); cv.pack(fill='both', expand=True); root.update()
if not OVERLAY:
    try: SW, SH = max(980, int(cv.winfo_width())), max(620, int(cv.winfo_height()))
    except Exception: pass
u32 = None; HW = 0
if PLAT == 'win':
    u32 = ctypes.windll.user32
    if OVERLAY:
        try: HW = u32.GetParent(root.winfo_id()) or root.winfo_id(); u32.SetWindowLongW(HW, -20, u32.GetWindowLongW(HW, -20) | 0x80000 | 0x80)
        except Exception: HW = 0
def down(vk):
    try: return bool(u32 and OVERLAY and u32.GetAsyncKeyState(vk) & 0x8000)
    except Exception: return False
def pick_font(prefs):
    try: av = set(tkf.families(root))
    except Exception: av = set()
    for p in prefs:
        if p in av: return p
    return prefs[-1]
UIF = pick_font(['Segoe UI', 'SF Pro Display', 'Helvetica Neue', 'Ubuntu', 'Cantarell', 'DejaVu Sans', 'Arial', 'Helvetica'])
MONOF = pick_font(['Consolas', 'Menlo', 'SF Mono', 'DejaVu Sans Mono', 'Liberation Mono', 'Courier New', 'Courier'])
DISPF = pick_font(['Impact', 'Arial Black', 'Helvetica Neue', 'DejaVu Sans', 'Arial'])
BNF = pick_font(['Nirmala UI', 'Vrinda', 'Shonar Bangla', 'Noto Sans Bengali', 'Kalpurush', 'SolaimanLipi', 'Siyam Rupali', 'Lohit Bengali', 'Bangla MN', UIF])
BN_SHAPES = [False]; FCACHE = {}; FB = None; BN_FONT_OK = BNF != UIF or sys.platform == 'win32'
FS = 1.0; KS = 40; KBY = 0; GY = 0; FL = None; BG = None; PEND = [None, 0]; FULL = [False]
def make_bg():
    """Pre-rendered scenery for window mode (night city / sunny day)."""
    img = tk.PhotoImage(width=SW, height=SH); dark = D['theme'] == 'dark'; rnd = random.Random(4)
    top, bot = ('#070b24', '#2b1d52') if dark else ('#6fb1ff', '#e4f3ff')
    for y in range(0, SH, 3): img.put(mix(top, bot, y / SH), to=(0, y, SW, min(SH, y + 3)))
    if dark:
        for _ in range(110): x, y = rnd.randrange(SW), rnd.randrange(int(GY * .7)); img.put('#cfd6ff' if rnd.random() < .7 else '#ffffff', to=(x, y, x + 2, y + 2))
        mx, my, mr = int(SW * .82), int(GY * .2), int(52 * FS)
        for dy in range(-mr, mr): hw = int(math.sqrt(mr * mr - dy * dy)); img.put('#f3efd0', to=(mx - hw, my + dy, mx + hw, my + dy + 1))
        cols = ('#0e1538', '#141c48')
    else:
        mx, my, mr = int(SW * .82), int(GY * .2), int(46 * FS)
        for dy in range(-mr, mr): hw = int(math.sqrt(mr * mr - dy * dy)); img.put('#fff3a8', to=(mx - hw, my + dy, mx + hw, my + dy + 1))
        for _ in range(7):
            cx, cy = rnd.randrange(SW), rnd.randrange(int(GY * .5)); 
            for k in range(3): img.put('#ffffff', to=(cx + k * 26, cy + 8 - k % 2 * 8, cx + k * 26 + 70, cy + 24 - k % 2 * 8))
        cols = ('#9ec9e8', '#b4d8f0')
    for layer, c in enumerate(cols):
        x = 0
        while x < SW:
            w = rnd.randrange(34, 90); h = rnd.randrange(60, 200) * (1 - layer * .25) * FS; img.put(c, to=(x, int(GY - h), min(SW, x + w), GY + 6)); x += w + rnd.randrange(0, 12)
    img.put('#0c1226' if dark else '#6fbf73', to=(0, GY + 4, SW, SH)); return img
def layout():
    global FS, KB, KS, KBY, GY, FL, BG, FB
    FS = max(.9, min(1.9, SH / 1080 * 1.4)); KB = max(.7, min(1.4, SH / 1080)); KS = min(44 * KB, SW / 38); KBY = SH - (64 if OVERLAY else 26) * KB - 5 * (KS + 4); GY = int(KBY - 50 * FS)
    FL = tkf.Font(root, family=MONOF, size=-max(12, int(19 * FS)), weight='bold'); FB = tkf.Font(root, family=BNF, size=-max(14, int(24 * FS)), weight='bold'); FCACHE.clear()
    try: BN_SHAPES[0] = FB.measure('\u0995\u09cd\u09b7') < FB.measure('\u0995') + FB.measure('\u09b7') - 1
    except Exception: BN_SHAPES[0] = False
    BG = None if OVERLAY else make_bg()
layout()
def on_cfg(ev):
    if OVERLAY: return
    try:
        if abs(ev.width - SW) > 2 or abs(ev.height - SH) > 2: PEND[0] = (max(980, ev.width), max(620, ev.height)); PEND[1] = time.perf_counter()
    except Exception: pass
cv.bind('<Configure>', on_cfg)
def activate():
    try:
        root.deiconify()
        if OVERLAY: root.attributes('-topmost', True)
        if PLAT == 'win' and HW: u32.SetForegroundWindow(HW)
        root.lift(); root.focus_force()
    except Exception: pass

# ============================================================== sound effects (synthesized, no music, no external files)
SR = ts_sound.SR; VOLS = [0, .3, .6, 1.0]; VOLN = ['off', 'low', 'medium', 'high']
SOUND_NAMES = ts_sound.SOUND_NAMES; GAIN = ts_sound.GAIN
def sfx_progress(i, n, name):
    try: cv.delete('all'); cv.create_text(SW / 2, SH / 2, text=f'Preparing sound effects (first start only)...  {i}/{n}', fill='#ffffff', font=('Arial', 22, 'bold')); root.update()
    except Exception: pass
def build_sounds(): return ts_sound.build_sounds(sfx_progress)
def _write(path, sig, gain):
    pk = max(1e-6, max(abs(v) for v in sig)); data = struct.pack('<%dh' % len(sig), *[int(max(-1., min(1., v / pk * gain)) * 32000) for v in sig])
    with wave.open(path, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data)
class Snd:
    def __init__(s): s.sig = None; s.inst = {}; s.rr = {}; s.n = 0; s.mci_ok = PLAT == 'win'; s.procs = []; s.cmd = None; s.cmd_tried = False
    def path(s, name, lv): return os.path.join(SFXDIR, f'{name}_{lv}.wav')
    def ensure(s, lv):
        os.makedirs(SFXDIR, exist_ok=True)
        if all(os.path.exists(s.path(n, lv)) for n in SOUND_NAMES): return
        if s.sig is None: s.sig = build_sounds()
        for n, sig in s.sig.items(): _write(s.path(n, lv), sig, GAIN.get(n, .6) * VOLS[lv])
    def mci(s, cmd):
        try: return ctypes.windll.winmm.mciSendStringW(cmd, None, 0, None)
        except Exception: return -1
    def want(s, name): return 3 if name.startswith(('tick', 'punch', 'kick', 'slash', 'stab')) else 1 if name in ('boss', 'ultimate', 'win', 'lose', 'phase', 'crash', 'chapter', 'boom', 'ach') else 2
    def open_one(s, name, lv):
        alias = f'kw{s.n}'; s.n += 1
        if s.mci(f'open "{s.path(name, lv)}" type waveaudio alias {alias}') == 0: s.inst.setdefault((name, lv), []).append(alias); return True
        s.mci_ok = False; return False
    def warm(s):
        lv = D['vol']
        if lv <= 0 or A.no_sound: return
        s.ensure(lv)
        if PLAT != 'win': return
        for n in SOUND_NAMES:
            for _ in range(s.want(n)):
                if not s.mci_ok or not s.open_one(n, lv): return
    def reload(s):
        for lst in s.inst.values():
            for a in lst: s.mci(f'close {a}')
        s.inst.clear(); s.rr.clear(); s.mci_ok = PLAT == 'win'
        try: s.warm()
        except Exception: log(traceback.format_exc())
    def close(s):
        if PLAT == 'win': s.mci('close all')
    def spawn(s, name, lv):
        if not s.cmd_tried:
            s.cmd_tried = True
            if PLAT == 'mac': s.cmd = ['afplay'] if shutil.which('afplay') else None
            else: s.cmd = next((c for c in (['paplay'], ['pw-play'], ['aplay', '-q'], ['play', '-q']) if shutil.which(c[0])), None)
        if not s.cmd: return
        s.procs = [p for p in s.procs if p.poll() is None]
        if len(s.procs) >= 10: return
        s.ensure(lv); s.procs.append(subprocess.Popen(s.cmd + [s.path(name, lv)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    def play(s, name):
        lv = D['vol']
        if lv <= 0 or A.no_sound: return
        if PLAT != 'win': s.spawn(name, lv); return
        key = (name, lv); lst = s.inst.get(key, [])
        if len(lst) < s.want(name) and s.mci_ok: s.ensure(lv); s.open_one(name, lv); lst = s.inst.get(key, [])
        if lst and s.mci_ok:
            i = s.rr.get(key, 0); s.rr[key] = i + 1
            if s.mci(f'play {lst[i % len(lst)]} from 0') == 0: return
            s.mci_ok = False
        try:
            import winsound; s.ensure(lv); winsound.PlaySound(s.path(name, lv), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        except Exception: pass
SND = Snd()
if A.sounds:                                           # sound test: python typestrike.py --sounds
    root.withdraw(); D['vol'] = 3
    for _n in SOUND_NAMES: print(_n, flush=True); SND.play(_n); time.sleep(1.2)
    sys.exit(0)
try: SND.warm()
except Exception: log(traceback.format_exc())
SVAR = dict(punch=['punch', 'punch2', 'punch3'], kick=['kick', 'kick2'], slash=['slash', 'slash2', 'slash3'], stab=['stab', 'stab2'])
def snd(name):
    try: SND.play(random.choice(SVAR[name]) if name in SVAR else name)
    except Exception: log(traceback.format_exc())

# ============================================================== fighting: poses, moves, weapons, styles
# pose = (torso lean, lead shoulder, lead elbow, rear shoulder, rear elbow, lead hip, lead knee, rear hip, rear knee, lunge, spin, jump, weapon angle)
def PO(*a): return tuple(a) + (0,) * (14 - len(a))
G0 = PO(.12, .9, 1.7, .6, 2.0, .7, .5, -.1, .75); G0S = G0[:10] + (6.2832,) + G0[11:]
HIT = PO(-.45, -.2, .9, -.5, .7, .3, .4, -.6, .5, -4); BLK = PO(.2, 1.6, 2.4, 1.4, 2.5, .75, .6, -.1, .9, -2); BLKW = PO(.15, 1.5, 1.2, .9, 1.6, .75, .6, -.1, .9, -2); AIR = PO(.1, 1.2, 1.2, .9, 1.2, 1.0, 1.2, .4, 1.4)
RAP_IDLE = PO(.15, 1.3, .5, .4, 1.6, .85, .6, -.2, .85, 3)
# --- unarmed
JA = PO(.02, .45, 2.3, .6, 2.0, .7, .5, -.1, .75, -4); J1 = PO(.25, 1.55, .1, .6, 2.0, .85, .55, -.1, .75, 7); J2 = PO(.28, 1.62, .0, .6, 2.0, .9, .55, -.1, .75, 9)
CA = PO(-.05, .9, 1.7, .1, 2.4, .7, .5, .0, .9, -3); C1 = PO(.3, .7, 1.8, 1.55, .05, .6, .55, .15, .55, 9); C2 = PO(.34, .7, 1.8, 1.62, .0, .6, .55, .2, .5, 11)
HKA = PO(-.05, .4, 2.0, .6, 2.0, .7, .5, -.1, .75, -3); HK1 = PO(.3, 1.35, 1.2, .6, 2.0, .85, .55, -.05, .7, 8); HK2 = PO(.36, 1.5, .9, .6, 2.0, .9, .55, 0, .65, 10)
U1 = PO(.05, .9, 1.7, .2, .9, .95, .95, -.2, 1.05, -2); U2 = PO(.1, .9, 1.7, 2.4, .4, .5, .3, .0, .35, 6); U3 = PO(.12, .9, 1.7, 2.6, .3, .45, .25, .0, .3, 7)
EL1 = PO(.1, .6, 2.2, .6, 2.0, .8, .55, -.1, .75, 0); EL2 = PO(.42, 1.15, 2.85, .6, 2.0, .95, .55, .05, .6, 13)
PA1 = PO(.05, 1.0, 1.2, .9, 1.5, .9, .7, -.1, .9, -2); PA2 = PO(.38, 1.62, .05, 1.45, .25, 1.1, .9, -.5, .15, 15)
KN = PO(.35, 1.3, 2.2, 1.3, 2.2, 1.7, 2.1, -.1, .5, 3); KNJ = PO(.4, 1.3, 2.2, 1.3, 2.2, 1.9, 2.2, -.1, .4, 6, 0, 42)
LW1 = PO(-.1, .9, 1.7, .6, 2.0, .7, .5, .4, 1.3, -2); LW2 = PO(-.32, .9, 1.7, -.2, 1.4, .5, .4, 1.15, .1, 3)
F1 = PO(-.05, .9, 1.7, .6, 2.0, 1.35, 1.9, -.05, .5); F2 = PO(-.2, .9, 1.7, .6, 2.0, 1.6, .05, -.05, .45, 3)
R1 = PO(.0, .9, 1.7, -.1, 1.2, .35, .4, .9, 1.9, -2); R2 = PO(-.5, .9, 1.6, -.5, .8, .3, .35, 1.6, .15, 2); R3 = PO(-.62, .9, 1.6, -.7, .7, .25, .35, 1.75, .25, 3)
S1 = PO(-.2, 1.2, .9, .0, 1.2, 1.4, 1.9, -.1, .5); S2 = PO(-.6, 1.9, .3, -.5, .6, 1.55, .05, -.1, .4, 3)
X1 = PO(-.1, 1.3, 1.0, .3, 1.4, 2.9, .15, -.1, .5); X2 = PO(.35, 1.0, 1.3, .6, 1.6, .6, .1, -.1, .7, 4)
HKK1 = PO(.15, .9, 1.7, .6, 2.0, .6, .9, .6, 1.7, -2, 1.6); HKK2 = PO(.5, .9, 1.4, .3, 1.0, .5, .4, -1.55, .1, 0, 3.3); HKK3 = PO(.1, .9, 1.7, .6, 2.0, .7, .5, .2, 1.2, 0, 6.2832)
TO1 = PO(.1, .9, 1.7, .6, 2.0, .9, 1.0, -.2, 1.1, -2, .6); TO2 = PO(.5, 1.2, 1.0, .2, 1.0, .5, .6, -1.5, .1, 0, 3.3, 45); TO3 = PO(-.3, 1.0, 1.5, .4, 1.6, .4, .5, 1.5, .2, 2, 6.2832, 35)
CR1 = PO(-.05, 1.8, .5, -.9, .5, 1.9, 1.6, -.05, .15); CR2 = PO(-.45, 2.0, .3, -1.0, .4, 1.7, .05, -.05, .1, 3)
SWP1 = PO(.35, .9, 1.7, .6, 2.0, .6, 1.5, -.1, 1.4, -2); SWP2 = PO(.55, .4, 1.0, -.6, .8, .5, 1.7, 1.55, .1, 4)
DR1 = PO(.2, .9, 1.7, .2, .9, .9, 1.0, -.2, 1.1, -3); DR2 = PO(.05, .9, 1.7, 2.8, .2, .4, .2, .0, .3, 5, 0, 55); DR3 = PO(.0, .9, 1.7, 2.9, .1, .5, .3, -.3, 1.0, 5, 0, 38)
FLY = PO(-.7, -.5, .6, -.8, .5, 1.55, .05, .2, 1.4, 4, 0, 45)
# --- sword moves (weapon is held in the lead hand; two-handed weapons use IK for the rear hand)
SS1 = PO(-.15, 2.7, .5, -.5, .6, .8, .6, -.2, .8, -4); SS2 = PO(.3, 1.1, .1, .4, 1.0, 1.0, .7, -.2, .7, 10); SS3 = PO(.45, .7, .2, .2, 1.0, 1.1, .8, -.3, .6, 13)
SR1 = PO(.35, .3, .2, .4, 1.4, .9, 1.0, -.3, .9, -3); SR2 = PO(.1, 1.6, .6, .2, 1.2, .7, .4, -.1, .5, 7); SR3 = PO(-.05, 2.4, .5, -.3, 1.0, .5, .3, -.1, .4, 9)
ST1 = PO(.1, -.2, 1.9, .6, 2.0, .9, .7, -.2, .6, -3); ST2 = PO(.45, 1.5, .05, .5, 1.2, 1.35, .2, -.5, .05, 17)
SC1 = PO(-.3, 2.9, .4, -.8, .5, .7, .5, -.3, .9, -4); SC2 = PO(.4, 1.0, .15, .4, 1.0, 1.0, .8, -.15, .7, 11); SC3 = PO(.5, .7, .2, .2, 1.0, 1.2, .9, -.2, .6, 13)
SP1 = PO(.1, 1.57, .0, .6, 2.0, .8, .7, -.2, .8, 0, 1.2, 6); SP2 = PO(.1, 1.57, .0, .4, 1.6, .8, .7, -.2, .8, 0, 3.5, 18); SP3 = PO(.1, 1.57, .0, .6, 2.0, .8, .7, -.2, .8, 0, 6.2832, 6)
BF1 = PO(.35, .9, 1.7, .6, 2.0, .9, 1.1, -.2, 1.2, -3); BF2 = PO(.0, 1.4, 1.8, 1.2, 1.8, 1.5, 1.9, 1.0, 2.0, 0, 0, 50, 0, -3.1416); BF3 = PO(-.3, 1.6, .6, 1.3, .7, 1.5, .1, .9, .5, 2, 0, 38, 0, -5.4); BFE = PO(.12, .9, 1.7, .6, 2.0, .7, .5, -.1, .75, 0, 0, 0, 0, -6.2832)
CW1 = PO(.1, 2.9, .1, 2.9, .1, 1.0, .1, -1.0, .1, 0, 0, 22, 0, 1.5708); CW2 = PO(.1, 2.9, .1, 2.9, .1, 1.0, .1, -1.0, .1, 6, 0, 26, 0, 4.7124); CWE = PO(.12, .9, 1.7, .6, 2.0, .7, .5, -.1, .75, 0, 0, 0, 0, 6.2832)
SL1 = PO(.3, 2.8, .4, -.5, .5, .9, 1.2, -.1, 1.4); SL2 = PO(-.1, 2.9, .4, -.6, .5, 1.3, 1.1, .3, 1.0, 4, 0, 65); SL3 = PO(.5, 1.0, .15, .4, 1.0, 1.3, .9, -.3, .7, 12)
MOVES = dict(
    jab=[(0, G0), (.14, JA), (.32, J1), (.4, J2), (.62, J1), (1, G0)], cross=[(0, G0), (.16, CA), (.34, C1), (.42, C2), (.62, C1), (1, G0)], hook=[(0, G0), (.16, HKA), (.34, HK1), (.42, HK2), (.62, HK1), (1, G0)],
    upper=[(0, G0), (.3, U1), (.55, U2), (.65, U3), (.8, U2), (1, G0)], elbow=[(0, G0), (.2, EL1), (.4, EL2), (.7, EL2), (1, G0)], palm=[(0, G0), (.2, PA1), (.42, PA2), (.7, PA2), (1, G0)],
    knee=[(0, G0), (.4, KN), (.7, KN), (1, G0)], jknee=[(0, G0), (.25, U1), (.45, KNJ), (.7, KNJ), (1, G0)], low=[(0, G0), (.28, LW1), (.5, LW2), (.7, LW2), (.85, LW1), (1, G0)],
    front=[(0, G0), (.28, F1), (.5, F2), (.62, F2), (.8, F1), (1, G0)], round=[(0, G0), (.34, R1), (.55, R2), (.65, R3), (.8, R1), (1, G0)], side=[(0, G0), (.3, S1), (.52, S2), (.7, S2), (.85, S1), (1, G0)],
    axe=[(0, G0), (.38, X1), (.5, X1), (.62, X2), (.82, X2), (1, G0)], hookkick=[(0, G0), (.3, HKK1), (.55, HKK2), (.78, HKK3), (1, G0S)], tornado=[(0, G0), (.25, TO1), (.5, TO2), (.72, TO3), (.9, G0S), (1, G0S)],
    crane=[(0, G0), (.3, CR1), (.52, CR2), (.75, CR2), (1, G0)], sweep=[(0, G0), (.28, SWP1), (.52, SWP2), (.75, SWP2), (1, G0)], dragon=[(0, G0), (.25, DR1), (.5, DR2), (.66, DR2), (.86, DR3), (1, G0)],
    fly=[(0, G0), (.22, FLY), (.8, FLY), (1, G0)],
    sw_slash=[(0, G0), (.3, SS1), (.5, SS2), (.62, SS3), (.82, SS3), (1, G0)], sw_rise=[(0, G0), (.28, SR1), (.48, SR2), (.62, SR3), (.82, SR3), (1, G0)], sw_thrust=[(0, G0), (.25, ST1), (.45, ST2), (.7, ST2), (1, G0)],
    sw_chop=[(0, G0), (.35, SC1), (.52, SC2), (.65, SC3), (.85, SC3), (1, G0)], sw_spin=[(0, G0), (.2, SP1), (.5, SP2), (.78, SP3), (1, G0S)], sw_leap=[(0, G0), (.2, SL1), (.42, SL2), (.6, SL3), (.85, SL3), (1, G0)],
    flip=[(0, G0), (.2, BF1), (.45, BF2), (.7, BF3), (.88, BFE), (1, BFE)], cart=[(0, G0), (.25, CW1), (.55, CW2), (.82, CWE), (1, CWE)])
IMP = dict(jab=.32, cross=.34, hook=.34, upper=.55, elbow=.4, palm=.42, knee=.4, jknee=.45, low=.5, front=.5, round=.55, side=.52, axe=.62, hookkick=.55, tornado=.52, crane=.5, sweep=.5, dragon=.5, fly=.3,
           sw_slash=.5, sw_rise=.48, sw_thrust=.45, sw_chop=.52, sw_spin=.5, sw_leap=.6, flip=.62, cart=.45)
LAUNCH = dict(jab=(500, -250), cross=(950, -300), hook=(1000, -350), upper=(260, -1250), elbow=(1000, -300), palm=(1100, -300), knee=(500, -500), jknee=(300, -1100), low=(700, -200), front=(1000, -250), round=(900, -520),
              side=(1050, -300), axe=(380, -250), hookkick=(1100, -400), tornado=(1300, -700), crane=(900, -600), sweep=(300, -700), dragon=(300, -1400), fly=(1000, -450),
              sw_slash=(850, -450), sw_rise=(250, -1200), sw_thrust=(1300, -200), sw_chop=(400, -300), sw_spin=(1000, -550), sw_leap=(550, -750), flip=(900, -800), cart=(800, -500))
FDUR = dict(flip=.7, cart=.6, tornado=.62, dragon=.56, sw_leap=.62, sw_spin=.56, axe=.5, hookkick=.5); MINDUR = dict(tornado=.4, hookkick=.34, sw_spin=.34, sw_leap=.4, dragon=.38, flip=.45, cart=.4)
KICKS = {'front', 'round', 'side', 'axe', 'hookkick', 'tornado', 'crane', 'sweep', 'low', 'fly', 'knee', 'jknee', 'flip', 'cart'}
TH1 = PO(.35, 1.4, .6, 1.4, .6, .9, 1.0, -.2, .9, 4); TH2 = PO(-.45, 2.6, .5, 2.6, .5, .8, .6, -.1, .8, -2)
JU = PO(.08, 1.0, 1.4, .7, 1.3, 1.35, 1.9, .3, 1.2); JD = PO(.0, 2.4, .5, 2.2, .5, .5, .2, -.2, .3)
MOVES.update(throw=[(0, G0), (.3, TH1), (.55, TH2), (.8, TH2), (1, G0)], chainp=[(0, G0), (.12, J1), (.24, C1), (.36, J1), (.48, C1), (.64, J2), (.8, J1), (1, G0)],
             sw_cross=[(0, G0), (.22, SS1), (.4, SS2), (.52, SR2), (.64, SR3), (.85, SR3), (1, G0)], sw_iai=[(0, G0), (.2, ST1), (.4, ST2), (.7, ST2), (1, G0)],
             sw_flurry=[(0, G0), (.12, ST1), (.22, ST2), (.3, ST1), (.4, ST2), (.48, ST1), (.58, ST2), (.85, ST2), (1, G0)])
IMP.update(throw=.5, chainp=.42, sw_cross=.45, sw_iai=.3, sw_flurry=.58)
LAUNCH.update(throw=(-950, -950), chainp=(1000, -300), sw_cross=(900, -650), sw_iai=(1250, -300), sw_flurry=(1200, -400)); FDUR.update(throw=.6, sw_cross=.5, sw_iai=.4, sw_flurry=.62); MINDUR.update(sw_flurry=.4, throw=.4)
STY = dict(
    boxing=dict(name='Boxing', price=0, chain=['jab', 'cross', 'hook', 'cross', 'upper', 'jab', 'hook', 'upper'], fins=['upper', 'hook', 'cross'], dur=.19, power=1.0, desc='Fast hands: jabs, hooks and uppercuts.'),
    muaythai=dict(name='Muay Thai', price=250, chain=['elbow', 'knee', 'low', 'cross', 'knee', 'round', 'elbow', 'jknee'], fins=['jknee', 'round', 'elbow'], dur=.21, power=1.1, desc='Elbows, knees and punishing low kicks.'),
    taekwondo=dict(name='Taekwondo', price=450, chain=['front', 'round', 'side', 'hookkick', 'round', 'axe', 'side', 'tornado'], fins=['tornado', 'axe', 'side', 'hookkick'], dur=.22, power=1.15, desc='High fast kicks and spinning attacks.'),
    kungfu=dict(name='Kung Fu', price=650, chain=['palm', 'jab', 'crane', 'palm', 'sweep', 'elbow', 'front', 'dragon'], fins=['dragon', 'crane', 'fly'], dur=.21, power=1.2, desc='Flowing palms, sweeps and the Dragon strike.'))
STY.update(
    karate=dict(name='Karate', price=300, chain=['jab', 'cross', 'front', 'round', 'cross', 'side', 'jab', 'upper'], fins=['round', 'side', 'upper', 'hookkick'], dur=.2, power=1.1, desc='Disciplined strikes and snapping kicks.'),
    wingchun=dict(name='Wing Chun', price=500, chain=['palm', 'jab', 'palm', 'jab', 'palm', 'cross', 'elbow', 'palm'], fins=['palm', 'dragon', 'elbow'], dur=.14, power=1.0, desc='Lightning chain punches at close range.'),
    capoeira=dict(name='Capoeira', price=800, chain=['sweep', 'low', 'hookkick', 'cart', 'round', 'sweep', 'flip', 'hookkick'], fins=['flip', 'tornado', 'cart'], dur=.23, power=1.2, desc='Acrobatic, flowing kicks, cartwheels and flips.'),
    ninjutsu=dict(name='Ninjutsu', price=1000, chain=['jab', 'low', 'jknee', 'side', 'flip', 'elbow', 'round', 'jknee'], fins=['flip', 'tornado', 'dragon', 'fly'], dur=.17, power=1.25, desc='Shadow style: fast, acrobatic and deadly.'))
WP = {
    'fists': dict(name='Bare Fists', price=0, kind=None, len=0, reach=0, desc='No weapon. Uses your fighting style.'),
    'knife': dict(name='Combat Knife', price=150, kind='dagger', len=24, wb=2.6, curv=0, reach=4, two=False, dual=False, col='#dfe5ee', hilt='#4a3320', gw=3, trail='#ffffff', chain=['sw_slash', 'sw_thrust', 'sw_slash', 'sw_rise'], fins=['sw_rise', 'sw_leap'], dur=.16, power=.85, desc='Short and very fast.'),
    'daggers': dict(name='Twin Daggers', price=400, kind='dagger', len=22, wb=2.6, curv=0, reach=4, two=False, dual=True, col='#e6ecf5', hilt='#6b1f1f', gw=3, trail='#ff8a8a', chain=['sw_slash', 'sw_slash', 'sw_thrust', 'sw_rise', 'sw_spin'], fins=['sw_spin', 'sw_leap'], dur=.15, power=.9, desc='A blade in each hand. Endless combos.'),
    'gladius': dict(name='Gladius', price=450, kind='blade', len=40, wb=4.6, curv=0, reach=14, two=False, dual=False, col='#e6dcb8', hilt='#7a4a1a', gw=6, trail='#ffe08a', chain=['sw_slash', 'sw_thrust', 'sw_slash', 'sw_chop'], fins=['sw_chop', 'sw_leap'], dur=.19, power=1.0, desc='Roman short sword. Balanced and reliable.'),
    'rapier': dict(name='Rapier', price=700, kind='thin', len=62, wb=1.9, curv=0, reach=22, two=False, dual=False, col='#eef3fb', hilt='#d9a21b', gw=7, trail='#bfe3ff', idle=RAP_IDLE, chain=['sw_thrust', 'sw_thrust', 'sw_rise', 'sw_thrust'], fins=['sw_thrust', 'sw_rise'], dur=.14, power=.95, desc='Lightning thrusts from long range.'),
    'katana': dict(name='Katana', price=900, kind='blade', len=58, wb=3.4, curv=.07, reach=18, two=True, dual=False, col='#f3f6fb', hilt='#1c1c24', gw=5, trail='#d6efff', chain=['sw_slash', 'sw_rise', 'sw_slash', 'sw_thrust', 'sw_chop'], fins=['sw_rise', 'sw_spin', 'sw_leap'], dur=.17, power=1.05, desc='Razor-sharp curved steel. Fast and elegant.'),
    'scimitar': dict(name='Scimitar', price=1100, kind='blade', len=50, wb=5.2, curv=.12, reach=16, two=False, dual=False, col='#e4e9f1', hilt='#c8921a', gw=6, trail='#ffd27a', chain=['sw_slash', 'sw_slash', 'sw_rise', 'sw_spin', 'sw_chop'], fins=['sw_spin', 'sw_slash', 'sw_leap'], dur=.18, power=1.05, desc='Sweeping desert blade.'),
    'longsword': dict(name='Longsword', price=1500, kind='blade', len=68, wb=4.8, curv=0, reach=24, two=True, dual=False, col='#d3dcea', hilt='#2a4a9a', gw=10, trail='#9cc8ff', chain=['sw_chop', 'sw_slash', 'sw_thrust', 'sw_rise', 'sw_slash'], fins=['sw_leap', 'sw_chop', 'sw_spin'], dur=.21, power=1.2, desc='Knightly steel with great reach.'),
    'greatsword': dict(name='Greatsword', price=2200, kind='blade', len=86, wb=7.4, curv=0, reach=32, two=True, dual=False, col='#bcc8da', hilt='#3a2418', gw=13, trail='#ff9a4a', chain=['sw_chop', 'sw_slash', 'sw_rise', 'sw_chop'], fins=['sw_leap', 'sw_spin', 'sw_chop'], dur=.27, power=1.4, desc='Huge and heavy. Every hit shakes the screen.'),
    'spear': dict(name='Spear', price=1800, kind='staff', len=70, wb=4.4, curv=0, reach=48, two=True, dual=False, col='#e4eaf3', hilt='#6a4424', gw=0, trail='#c4ffd4', idle=RAP_IDLE, chain=['sw_thrust', 'sw_thrust', 'sw_rise', 'sw_spin'], fins=['sw_thrust', 'sw_spin', 'sw_leap'], dur=.19, power=1.15, desc='Longest reach. Keep your enemies far away.')}
WP.update(bow=dict(name='Bow', price=0, kind='bow', len=46, wb=0, curv=0, reach=0, two=False, dual=False, col='#a9743a', hilt='#5a3a1b', gw=0, trail='#ffffff', chain=[], fins=[], dur=.2, power=1, desc=''),
          bomb=dict(name='Bomb', price=0, kind='bomb', len=0, wb=0, curv=0, reach=0, two=False, dual=False, col='#222', hilt='#222', gw=0, trail='#ffd24a', chain=[], fins=[], dur=.2, power=1, desc=''),
          orbstaff=dict(name='Healing Staff', price=0, kind='staff', len=62, wb=0, curv=0, reach=0, two=False, dual=False, col='#9bffb8', hilt='#6a4424', gw=0, trail='#9bffb8', orb=True, chain=[], fins=[], dur=.2, power=1, desc=''))
for _k, _g in dict(katana='#8fe3ff', longsword='#9cc8ff', greatsword='#ff9a4a', spear='#9bffb8', rapier='#e8f4ff', daggers='#ff9a9a', scimitar='#ffd27a').items(): WP[_k]['glow'] = _g
STY.update(
    judo=dict(name='Judo', price=550, chain=['palm', 'low', 'sweep', 'throw', 'knee', 'sweep', 'throw', 'elbow'], fins=['throw', 'sweep'], dur=.22, power=1.15, desc='Grips, sweeps and powerful throws.'),
    kravmaga=dict(name='Krav Maga', price=700, chain=['jab', 'knee', 'elbow', 'cross', 'knee', 'elbow', 'hook', 'jknee'], fins=['jknee', 'elbow', 'hook'], dur=.15, power=1.2, desc='Brutal efficiency: fast, close and merciless.'),
    jkd=dict(name='Jeet Kune Do', price=900, chain=['jab', 'cross', 'side', 'chainp', 'low', 'side', 'jab', 'chainp'], fins=['side', 'chainp', 'fly'], dur=.14, power=1.15, desc='Lightning hands and a lightning side kick.'))
STY['wingchun'].update(chain=['chainp', 'palm', 'jab', 'chainp', 'palm', 'cross', 'elbow', 'chainp'], fins=['chainp', 'palm', 'dragon'])
WP.update(
    kunai=dict(name='Kunai', price=350, kind='dagger', len=21, wb=2.8, curv=0, reach=4, two=False, dual=False, col='#aab4c8', hilt='#2b2b3a', gw=3, trail='#b18cff', glow='#7c5cff', chain=['sw_thrust', 'sw_slash', 'sw_thrust', 'sw_rise'], fins=['sw_rise', 'sw_leap', 'sw_iai'], dur=.15, power=.9, desc='Ninja blade. Silent and sudden.'),
    nunchaku=dict(name='Nunchaku', price=650, kind='nunchaku', len=40, wb=0, curv=0, reach=10, two=False, dual=False, col='#c8a46a', hilt='#6a4424', gw=0, trail='#ffe14a', chain=['sw_spin', 'sw_slash', 'sw_cross', 'sw_chop'], fins=['sw_spin', 'sw_cross', 'sw_leap'], dur=.15, power=1.0, desc='Whirling sticks on a chain. Fast and flashy.'),
    bostaff=dict(name='Bo Staff', price=850, kind='bo', len=76, wb=0, curv=0, reach=40, two=True, dual=False, col='#c8a46a', hilt='#8a5a2a', gw=0, trail='#e8d3a0', idle=RAP_IDLE, chain=['sw_chop', 'sw_spin', 'sw_thrust', 'sw_slash'], fins=['sw_spin', 'sw_leap', 'sw_chop'], dur=.17, power=1.05, desc='Long wooden staff: great reach, great spins.'),
    axe=dict(name='Battle Axe', price=1400, kind='axe', len=56, wb=0, curv=0, reach=18, two=True, dual=False, col='#cfd6e4', hilt='#6a4424', gw=0, trail='#ff9a4a', glow='#ff6a2a', chain=['sw_chop', 'sw_chop', 'sw_slash', 'sw_leap'], fins=['sw_leap', 'sw_chop', 'sw_spin'], dur=.24, power=1.35, desc='Heavy chops that shake the ground.'),
    warhammer=dict(name='War Hammer', price=2000, kind='hammer', len=60, wb=0, curv=0, reach=22, two=True, dual=False, col='#aeb9cf', hilt='#4a3320', gw=0, trail='#ffe08a', chain=['sw_chop', 'sw_chop', 'sw_leap'], fins=['sw_leap', 'sw_chop'], dur=.3, power=1.6, desc='Slow and devastating. Every hit is an earthquake.'),
    twinswords=dict(name='Starburst Twin Blades', price=2600, kind='blade', len=58, wb=3.6, curv=0, reach=16, two=False, dual=True, col='#eaf4ff', hilt='#1f3a6a', gw=6, trail='#8fd4ff', glow='#6fc8ff', chain=['sw_slash', 'sw_slash', 'sw_cross', 'sw_flurry', 'sw_spin'], fins=['sw_flurry', 'sw_spin', 'sw_leap', 'sw_cross'], dur=.13, power=1.15, desc='Two blades, endless starburst combos (sword-art style).'),
    flamebrand=dict(name='Flame Brand', price=3000, kind='blade', len=68, wb=5, curv=.02, reach=22, two=False, dual=False, col='#ffe3b0', hilt='#7a1f0f', gw=9, trail='#ff7a2a', glow='#ff6a1a', chain=['sw_chop', 'sw_slash', 'sw_thrust', 'sw_rise', 'sw_slash'], fins=['sw_leap', 'sw_flurry', 'sw_spin'], dur=.18, power=1.3, desc='A sword wreathed in fire.'),
    frostbrand=dict(name='Frost Brand', price=3000, kind='blade', len=68, wb=5, curv=.02, reach=22, two=False, dual=False, col='#e6fbff', hilt='#1a4a7a', gw=9, trail='#9be8ff', glow='#7fe0ff', chain=['sw_slash', 'sw_thrust', 'sw_slash', 'sw_rise', 'sw_cross'], fins=['sw_iai', 'sw_spin', 'sw_leap'], dur=.17, power=1.25, desc='Freezes enemies where they stand.'),
    stormblade=dict(name='Storm Blade', price=3400, kind='blade', len=64, wb=4.2, curv=0, reach=20, two=False, dual=False, col='#fffbe0', hilt='#3a3a1a', gw=8, trail='#ffe14a', glow='#ffe14a', chain=['sw_slash', 'sw_cross', 'sw_thrust', 'sw_flurry'], fins=['sw_flurry', 'sw_cross', 'sw_leap'], dur=.15, power=1.3, desc='Crackling with lightning.'))
WORDER = ['fists', 'knife', 'kunai', 'daggers', 'gladius', 'nunchaku', 'rapier', 'bostaff', 'katana', 'scimitar', 'axe', 'longsword', 'spear', 'warhammer', 'greatsword', 'twinswords', 'flamebrand', 'frostbrand', 'stormblade']
SORDER = ['boxing', 'karate', 'muaythai', 'judo', 'wingchun', 'kravmaga', 'taekwondo', 'jkd', 'kungfu', 'capoeira', 'ninjutsu']
GIFT = {5: 'knife', 10: 'gladius', 15: 'katana', 20: 'longsword', 25: 'greatsword', 30: 'kunai', 35: 'nunchaku', 45: 'twinswords', 55: 'bostaff', 65: 'axe', 75: 'flamebrand', 85: 'frostbrand', 95: 'stormblade', 105: 'warhammer'}
SGIFT = {40: 'judo', 70: 'kravmaga', 90: 'jkd'}
FXP = dict(  # shape, colour 1, colour 2, hit sound, impact words
    boxing=('star', '#ff5a5a', '#ffffff', 'punch', ['POW!', 'BAM!', 'WHAM!']), karate=('lines', '#ffffff', '#9fd8ff', 'punch', ['OSU!', 'HAI!', 'KIAI!']), muaythai=('ember', '#ff9a3c', '#ffe08a', 'punch', ['CRACK!', 'SMASH!']),
    wingchun=('ripple', '#ffd24a', '#ffffff', 'punch', ['RAPID!', 'FLOW!']), taekwondo=('arc', '#6ec8ff', '#ffffff', 'kick', ['HYAH!', 'SNAP!']), kungfu=('chi', '#7dff9a', '#ffe066', 'punch', ['CHI!', 'HAH!']),
    capoeira=('dust', '#ffe066', '#69db7c', 'kick', ['GINGA!', 'AXE!']), ninjutsu=('smoke', '#b18cff', '#e6dcff', 'punch', ['SHADOW!', 'SILENT!']), judo=('dust', '#ffffff', '#c8d0e0', 'thud', ['IPPON!', 'WAZA-ARI!']),
    kravmaga=('star', '#ff9f43', '#ffffff', 'punch', ['SMASH!', 'CRUSH!']), jkd=('ripple', '#ffe14a', '#ffffff', 'kick', ['WATAH!', 'HAH!']), knife=('spark', '#ff7a7a', '#ffffff', 'knife', ['SLICE!']),
    kunai=('smoke', '#9d7bff', '#ffffff', 'knife', ['SWISH!']), daggers=('crossx', '#ff8a8a', '#ffffff', 'knife', ['FLURRY!']), gladius=('spark', '#ffe08a', '#ffffff', 'slash', ['STRIKE!']), rapier=('pierce', '#bfe3ff', '#ffffff', 'stab', ['TOUCHE!']),
    katana=('petal', '#ffb7d5', '#ffffff', 'shing', ['ZAN!', 'SLASH!']), scimitar=('sand', '#ffd27a', '#ffffff', 'slash', ['SWISH!']), longsword=('arc', '#9cc8ff', '#ffffff', 'slash', ['STRIKE!']),
    greatsword=('shock', '#ff9a4a', '#ffe08a', 'slash', ['CRUSH!']), spear=('pierce', '#c4ffd4', '#ffffff', 'stab', ['PIERCE!']), nunchaku=('wood', '#ffe14a', '#ffffff', 'wood', ['WATAH!', 'HYAA!']),
    bostaff=('wood', '#c8a46a', '#ffffff', 'wood', ['WHACK!']), axe=('shock', '#ff9a4a', '#ffd27a', 'axe', ['CHOP!']), warhammer=('shock', '#c9d4ea', '#ffe08a', 'hammer', ['BOOM!', 'CRUSH!']),
    twinswords=('starburst', '#8fd4ff', '#ffffff', 'shing', ['STARBURST!']), flamebrand=('fire', '#ff7a2a', '#ffe14a', 'fire', ['BURN!']), frostbrand=('ice', '#9be8ff', '#ffffff', 'ice', ['FREEZE!']), stormblade=('bolt', '#ffe14a', '#ffffff', 'zap', ['ZAP!']))
ATK = dict(grunt=['jab', 'front'], fast=['jab', 'jab', 'front'], tank=['round', 'front', 'hook'], boss=['round', 'side', 'axe', 'upper', 'hookkick'], ninja=['jab', 'low', 'side'], shield=['jab', 'front'], archer=['jab'], bomber=['jab'], healer=['jab'])
CDR = dict(grunt=(1.5, 2.4), fast=(1.2, 2.0), tank=(1.8, 2.6), boss=(2.0, 3.0), ninja=(1.0, 1.8), shield=(1.8, 2.6), archer=(2.4, 3.4), bomber=(2, 3), healer=(3.2, 4.2))
SCALE = dict(hero=1.0, grunt=.95, fast=.9, tank=1.25, boss=1.55, ninja=.9, archer=.95, shield=1.05, bomber=.95, healer=.95)
def lerp(a, b, t): return tuple(x + (y - x) * t for x, y in zip(a, b))
def interp(kf, p, imp):
    for i in range(len(kf) - 1):
        t0, a = kf[i]; t1, b = kf[i + 1]
        if p <= t1:
            t = (p - t0) / (t1 - t0) if t1 > t0 else 1
            t = 1 - (1 - t) ** 2 if (i > 0 and t1 <= imp + .09) else t * t * (3 - 2 * t)
            return lerp(a, b, t)
    return kf[-1][1]
def ik(o, t, l1, l2, d):
    """two-bone IK in screen space; elbow is the lower of the two solutions."""
    dx, dy = t[0] - o[0], t[1] - o[1]; dist = max(abs(l1 - l2) + 1e-3, min(math.hypot(dx, dy), l1 + l2 - 1e-3)); a = math.atan2(dy, dx)
    b = math.acos(max(-1., min(1., (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist))))
    e1 = (o[0] + math.cos(a + b) * l1, o[1] + math.sin(a + b) * l1); e2 = (o[0] + math.cos(a - b) * l1, o[1] + math.sin(a - b) * l1)
    return (e1 if e1[1] > e2[1] else e2), (o[0] + math.cos(a) * dist, o[1] + math.sin(a) * dist)

class F:
    def __init__(s, kind, x, y):
        s.kind = kind; s.x, s.y = x, y; s.vx = s.vy = 0; s.face = 1; s.ph = random.uniform(0, 6); s.zoom = 1.0; s._gy = None; s.wp = None
        s.mv = None; s.mp = 0; s.md = .3; s.hd = True; s.pend = None; s.stun = 0; s.block = 0; s.dead = 0; s.ds = 1; s.dying = False; s.crashed = False; s.spinr = 10
        s.hp = 100; s.w = ''; s.i = 0; s.hpw = 1; s.spd = 80; s.cd = 1.0; s.cur = G0; s.rate = 16; s.trail = []
        s.tele = 0; s.dhit = False; s.p2at = 0; s.guard = False; s.hk = 'kai'; s.jumps = 0; s.flipt = 0; s.gh = []; s.glast = 0; s.bt = None; s.ph2 = False; s.disp = None; s.bsc = 1.0; s.cd2 = 0; s.mod = 0
        s.flash = 0; s.t1 = [0., 0.]; s.t2 = [0., 0.]; s.shield = False; s.mh = 1; s.fuse = 0; s.dsh = 0; s.dcd = 2.0; s.aim = 0
    @property
    def sc(s): return SCALE[s.kind] * FS * s.zoom * s.bsc * (HEROES[s.hk]['sc'] if s.kind == 'hero' else 1)
    @property
    def gy(s): return GY if s._gy is None else s._gy
    def play(s, name, dur):
        if s.pend: s.flush()
        s.mv = name; s.mp = 0; s.md = dur; s.hd = False; s.stun = 0; s.block = 0
    def flush(s):
        fn = s.pend[1]; s.pend = None; fn()
    def target(s):
        if s.dead or s.stun > 0: s.rate = 60; return HIT
        if s.block > 0: s.rate = 50; return BLKW if s.wp else BLK
        if s.mv: s.rate = 42; return interp(MOVES[s.mv], min(1, s.mp), IMP[s.mv])
        s.rate = 16
        if s.y < s.gy - 2:
            if s.kind == 'hero':
                p = list(JU if s.vy < -150 else JD if s.vy > 150 else AIR)
                if s.flipt > 0: p[13] = -6.2832 * (1 - s.flipt / .5)
                return tuple(p)
            return AIR
        base = (WP[s.wp].get('idle') if s.wp else None) or G0; p = list(base)
        if abs(s.vx) > 20:
            sw = math.sin(s.ph); p[5] += sw * .45; p[7] -= sw * .45; p[6] += max(0, sw) * .4; p[8] += max(0, -sw) * .4; p[1] += sw * .1
        else:
            b = math.sin(s.ph * .5); p[0] += b * .03; p[1] += b * .06; p[3] -= b * .05; p[9] += math.sin(s.ph * .45) * 1.8; p[11] += abs(math.sin(s.ph * .9)) * 2.4; p[5] += b * .04; p[7] -= b * .04
        return tuple(p)
    def step(s, dt):
        s.ph += dt * (5 + abs(s.vx) / 35); s.stun = max(0, s.stun - dt); s.flipt = max(0, s.flipt - dt); s.block = max(0, s.block - dt); s.flash = max(0, s.flash - dt); s.aim = max(0, s.aim - dt)
        tx_ = -s.face * 17 * s.sc - s.vx * .035; ty_ = math.sin(s.ph * 2) * 3 * s.sc + s.vy * .015; k1 = min(1, dt * 18); k2 = min(1, dt * 9)
        s.t1[0] += (tx_ * .6 - s.t1[0]) * k1; s.t1[1] += (ty_ * .6 - s.t1[1]) * k1; s.t2[0] += (tx_ - s.t2[0]) * k2; s.t2[1] += (ty_ - s.t2[1]) * k2
        if s.mv:
            s.mp += dt / s.md
            if s.pend and s.mp >= s.pend[0]: s.flush()
            if s.mp >= 1: s.mv = None
        tg = s.target(); k = 1 - math.exp(-s.rate * min(dt, .05)); c = [a + (b - a) * k for a, b in zip(s.cur, tg)]; c[10] = tg[10]; c[13] = tg[13]; s.cur = tuple(c)
    def phys(s, dt):
        s.vy += 1500 * dt; s.x += s.vx * dt; s.y += s.vy * dt
        if s.y >= GY:
            if s.kind == 'hero':
                if s.vy > 250: dust(s.x, GY, 4)
                s.jumps = 0
            if s.vy > 500: snd('land' if s.kind == 'hero' else 'thud')
            if s.kind == 'boss' and s.dead and s.vy > 650 and not s.crashed: s.crashed = True; crash(s)
            s.y = GY; s.vy = -s.vy * .3 if (s.vy > 400 and s.dead) else 0
            if s.stun > 0 or s.dead: s.vx *= .9
        if s.x < 25: s.x = 25; s.vx = abs(s.vx) * .6
        if s.x > SW - 25: s.x = SW - 25; s.vx = -abs(s.vx) * .6
    def draw(s):
        if s.dead > (2.8 if s.kind == 'boss' else 1.8) and int(s.dead * 12) % 2 == 0: return
        S = s.sc; d = s.face; x, y = s.x, s.y; gy = s.gy
        TL, A1, E1, A2, E2, L1, K1, L2, K2, HX, SP, JY, WA, RT = s.cur
        th, sk, ua, fa = 18 * S, 18 * S, 15 * S, 14 * S
        def seg(o, a, l): return (o[0] + d * math.sin(a) * l, o[1] + math.cos(a) * l)
        def lim(o, a, b, l1, l2): m = seg(o, a, l1); return m, seg(m, b, l2)
        z = (0, 0); kn1, ft1 = lim(z, L1, L1 - K1, th, sk); kn2, ft2 = lim(z, L2, L2 - K2, th, sk)
        hip = (x + d * HX * S, y - max(ft1[1], ft2[1]) - JY * S)
        def ab(p): return (p[0] + hip[0], p[1] + hip[1])
        kn1, ft1, kn2, ft2 = ab(kn1), ab(ft1), ab(kn2), ab(ft2)
        neck = (hip[0] + d * math.sin(TL) * 30 * S, hip[1] - math.cos(TL) * 30 * S); shl = (hip[0] + d * math.sin(TL) * 26 * S, hip[1] - math.cos(TL) * 26 * S)
        hc = (neck[0] + d * math.sin(TL + .1) * 11 * S, neck[1] - math.cos(TL + .1) * 11 * S)
        el1, hd1 = lim(shl, A1, A1 + E1, ua, fa); el2, hd2 = lim(shl, A2, A2 + E2, ua, fa)
        wp = WP[s.wp] if s.wp else None; ang1 = A1 + E1 + WA; ang2 = A2 + E2 + WA
        if wp and wp['kind'] and wp['two']:
            dirx, diry = d * math.sin(ang1), math.cos(ang1); el2, hd2 = ik(shl, (hd1[0] - dirx * 9 * S, hd1[1] - diry * 9 * S), ua, fa, d)
        sx_, sy_ = g.sx, g.sy
        rot = ((s.dead * s.spinr if y < gy - 2 else 1.5708) * s.ds if s.dead else 0) + RT * d; sx, sy = g.sx, g.sy; cs = math.cos(SP); cs = cs if abs(cs) > .28 else (.28 if cs >= 0 else -.28); hx0 = hip[0]
        ox, oy = hip[0], hip[1] - 22 * S; cr, sr = math.cos(rot), math.sin(rot)
        def R(p):
            px = hx0 + (p[0] - hx0) * cs
            if rot: a, b = px - ox, p[1] - oy; return (ox + a * cr - b * sr + sx, oy + a * sr + b * cr + sy)
            return (px + sx, p[1] + sy)
        sk_ = HEROES.get(s.hk, HEROES['kai']) if s.kind == 'hero' else None; now_ = time.perf_counter()
        col = (sk_['col'] if D['theme'] == 'dark' else sk_['lcol']) if sk_ else (mix(BOSSES[s.bt]['col'], '#ff2a2a', .35 if s.ph2 else 0) if (s.kind == 'boss' and s.bt) else ec(s.kind))
        if s.flash > 0: col = mix(col, '#ffffff', .8)
        rear = mix(col, C('rear'), .55); w = max(3, int(4.6 * S))
        REC = []
        def ln(c, *pts):
            q = [v for p in pts for v in R(p)]; REC.append(q); cv.create_line(*q, width=w, fill=c, capstyle='round', joinstyle='round')
        sa = max(.35, 1 - (gy - y + JY * S) / 420) * (1 if not rot else .8)
        if OVERLAY: cv.create_oval(x - 26 * S * sa + sx, gy - 2, x + 26 * S * sa + sx, gy + 8 * S, fill=C('sh'), outline='', stipple='gray50')
        else: cv.create_oval(x - 26 * S * sa + sx, gy - 2, x + 26 * S * sa + sx, gy + 8 * S, fill='#06091a' if D['theme'] == 'dark' else '#3f7f45', outline='')
        if s.gh:
            s.gh = [q for q in s.gh if now_ - q[0] < .22]
            for t0, segs, wd_, gc in s.gh:
                kk = 1 - (now_ - t0) / .22
                for pts in segs: cv.create_line(*pts, width=max(1, int(wd_ * kk * .8)), fill=gc, capstyle='round', joinstyle='round')
        if s.kind == 'boss' and s.bt:
            ar_ = (66 + 5 * math.sin(now_ * 7)) * S; cx_ = x + sx_; cv.create_oval(cx_ - ar_, y - 56 * S - ar_ + sy_, cx_ + ar_, y - 56 * S + ar_ + sy_, outline=mix(col, '#000000', .25), width=2, dash=(6, 6) if s.ph2 else ())
        if sk_ and 'cape' in sk_['acc']:
            tp = R(shl); p1 = R((shl[0], shl[1] + 8 * S)); t1_ = R((shl[0] + s.t2[0] * 1.8, shl[1] + 40 * S + s.t2[1])); t2_ = R((shl[0] + s.t2[0] * 2.4, shl[1] + 14 * S + s.t2[1] * .5))
            cv.create_polygon(tp[0], tp[1], t2_[0], t2_[1], t1_[0], t1_[1], p1[0], p1[1], fill=sk_['belt'], outline='', smooth=False)
        ln(rear, shl, el2, hd2); ln(rear, hip, kn2, ft2, (ft2[0] + d * 7 * S, ft2[1]))
        if wp and wp['kind'] and wp['dual']: s.blade(wp, hd2, ang2, S, R, False)
        ln(col, hip, neck); ln(col, hip, kn1, ft1, (ft1[0] + d * 7 * S, ft1[1])); ln(col, shl, el1, hd1)
        hr = R(hc); r = 9 * S; cv.create_oval(hr[0] - r, hr[1] - r, hr[0] + r, hr[1] + r, outline=col, width=w); cv.create_oval(hr[0] + d * 3.6 * S - 1.6 * S, hr[1] - 2 * S - 1.6 * S, hr[0] + d * 3.6 * S + 1.6 * S, hr[1] - 2 * S + 1.6 * S, fill=col, outline='')
        if s.kind == 'boss': cv.create_line(hr[0] - r * .8, hr[1] - r * .6, hr[0] - r * 1.5, hr[1] - r * 1.9, width=max(2, int(3 * S)), fill=col, capstyle='round'); cv.create_line(hr[0] + r * .8, hr[1] - r * .6, hr[0] + r * 1.5, hr[1] - r * 1.9, width=max(2, int(3 * S)), fill=col, capstyle='round')
        belt = sk_['belt'] if sk_ else mix(col, '#ffffff', .5); bp = R((hip[0], hip[1] - 3 * S)); cv.create_oval(bp[0] - 3.5 * S, bp[1] - 3.5 * S, bp[0] + 3.5 * S, bp[1] + 3.5 * S, fill=belt, outline='')
        b0 = R((hc[0] - d * 9 * S, hc[1] - 2 * S)); b1 = R((hc[0] + s.t1[0], hc[1] + s.t1[1])); b2 = R((hc[0] + s.t2[0], hc[1] + s.t2[1])); cv.create_line(b0[0], b0[1], b1[0], b1[1], b2[0], b2[1], width=max(2, int(3 * S)), fill=belt, smooth=True, capstyle='round')
        if sk_: s.gear(sk_, hr, r, S, d, col, w, b1, b2, now_)
        if s.shield and not s.dead:
            cx_, cy_ = hip[0] + d * 26 * S, hip[1] - 26 * S; pts = [(cx_ - 11 * S, cy_ - 30 * S), (cx_ + 11 * S, cy_ - 30 * S), (cx_ + 15 * S, cy_ - 6 * S), (cx_, cy_ + 26 * S), (cx_ - 15 * S, cy_ - 6 * S)]
            cv.create_polygon([v for p in pts for v in R(p)], fill='#8da2c0', outline='#2b3a55', width=2); a_, b_ = R((cx_, cy_ - 24 * S)), R((cx_, cy_ + 16 * S)); cv.create_line(a_[0], a_[1], b_[0], b_[1], fill='#e6eefc', width=max(1, int(2 * S)))
        for hp_ in (hd1, hd2):
            q = R(hp_); cv.create_oval(q[0] - 3.2 * S, q[1] - 3.2 * S, q[0] + 3.2 * S, q[1] + 3.2 * S, fill=col, outline='')
        if wp and wp['kind']:
            tip = s.blade(wp, hd1, ang1, S, R, True)
            active = s.mv and s.mv.startswith('sw_') and .22 < s.mp < .9 and not s.dead
            if tip and active:
                if s.trail and math.hypot(tip[0] - s.trail[-1][0], tip[1] - s.trail[-1][1]) > 200 * FS: s.trail = []
                s.trail.append(tip); s.trail = s.trail[-9:]
            elif s.trail: s.trail = s.trail[1:]
        if s.kind in ('hero', 'boss') and not s.dead and ((s.mv and .1 < s.mp < .9) or abs(s.vx) > 480) and now_ - s.glast > .03:
            s.glast = now_; gc_ = FXP.get(s.wp or (skey() if s is g.hero else 'boxing'), ('', '#ffffff'))[1] if s.kind == 'hero' else mix(col, '#ffffff', .2); s.gh.append((now_, REC[:], w, gc_)); s.gh = s.gh[-7:]
    def gear(s, sk, hr, r, S, d, col, w, b1, b2, now):
        ac = sk['acc']; hx, hy = hr; belt = sk['belt']; hair = '#8a5a3a' if D['theme'] == 'dark' else '#4a2c18'
        def poly(pts, fill): cv.create_polygon(*[v for p in pts for v in p], fill=fill, outline='')
        if 'spike' in ac:
            for ox, hh in ((-.6, 1.3), (-.05, 1.8), (.5, 1.3)): poly([(hx + (ox - .32) * r, hy - r * .8), (hx + ox * r, hy - r * (.8 + hh * .9)), (hx + (ox + .32) * r, hy - r * .8)], col)
        if 'pony' in ac:
            cv.create_arc(hx - r, hy - r, hx + r, hy + r, start=10, extent=160, style='arc', outline=hair, width=w)
            cv.create_line(hx - d * r * .9, hy - r * .5, b1[0], b1[1] - 5 * S, b2[0], b2[1] + 9 * S, width=max(3, int(5 * S)), fill=hair, smooth=True, capstyle='round')
        if 'ribbon' in ac: poly([(hx - d * r * .7, hy - r * .95), (hx - d * r * 1.5, hy - r * 1.5), (hx - d * r * 1.5, hy - r * .5)], belt); poly([(hx - d * r * .7, hy - r * .95), (hx + d * r * .1, hy - r * 1.5), (hx + d * r * .1, hy - r * .5)], belt)
        if 'topknot' in ac: cv.create_oval(hx - r * .4 - d * r * .2, hy - r * 1.9, hx + r * .4 - d * r * .2, hy - r * 1.1, fill=col, outline='')
        if 'mask' in ac: cv.create_arc(hx - r, hy - r, hx + r, hy + r, start=195, extent=150, style='chord', fill=belt, outline=belt)
        if 'scarf' in ac: cv.create_line(hx - d * r * .6, hy + r * 1.1, b1[0] - d * 6 * S, b1[1] + 12 * S, b2[0] - d * 10 * S, b2[1] + 22 * S, width=max(3, int(4 * S)), fill=belt, smooth=True, capstyle='round')
        if 'helm' in ac:
            cv.create_arc(hx - r * 1.1, hy - r * 1.1, hx + r * 1.1, hy + r * 1.1, start=0, extent=180, style='chord', fill='#9aa6bd', outline='#3a4458', width=1)
            for sg in (-1, 1): cv.create_line(hx + sg * r, hy - r * .3, hx + sg * r * 1.55, hy - r * .9, hx + sg * r * 1.4, hy - r * 1.8, smooth=True, width=max(2, int(3 * S)), fill='#f0e6c8', capstyle='round')
        if 'beard' in ac: poly([(hx - r * .75, hy + r * .35), (hx + r * .75, hy + r * .35), (hx + d * r * .3, hy + r * 2.0)], '#a05a1a')
        if 'visor' in ac: cv.create_rectangle(hx - r * .9 + d * r * .2, hy - r * .5, hx + r * .9 + d * r * .2, hy + r * .1, fill='#00e5ff', outline='')
        if 'antenna' in ac:
            cv.create_line(hx, hy - r, hx - d * r * .3, hy - r * 1.9, width=max(2, int(2 * S)), fill=col); cv.create_oval(hx - d * r * .3 - 2.5 * S, hy - r * 1.9 - 2.5 * S, hx - d * r * .3 + 2.5 * S, hy - r * 1.9 + 2.5 * S, fill='#ff4d4d' if int(now * 3) % 2 else '#ffd24a', outline='')
        if 'halo' in ac: cv.create_oval(hx - r * .95, hy - r * 2.0, hx + r * .95, hy - r * 1.45, outline='#fff27a', width=max(2, int(2.4 * S)))
    def blade(s, wp, hand, ang, S, R, lead):
        """draw a weapon held at `hand` pointing along `ang`; returns the (screen) tip position"""
        d = s.face; dx, dy = d * math.sin(ang), math.cos(ang); nx, ny = -dy, dx; L = wp['len'] * S; k = wp['kind']; col = wp['col']; hilt = wp['hilt']; glow = wp.get('glow')
        gp = (hand[0] + dx * 2 * S, hand[1] + dy * 2 * S)
        def line(a, b, c, wd): a, b = R(a), R(b); cv.create_line(a[0], a[1], b[0], b[1], width=max(1, int(wd)), fill=c, capstyle='round')
        if lead and s.trail:
            n = len(s.trail)
            for i in range(1, n): cv.create_line(s.trail[i - 1][0], s.trail[i - 1][1], s.trail[i][0], s.trail[i][1], width=max(1, int(i / n * 9 * S)), fill=wp['trail'], capstyle='round')
        if k == 'bomb':
            c = R((hand[0] + dx * 7 * S, hand[1] + dy * 7 * S - 3 * S)); r = 9 * S
            cv.create_oval(c[0] - r, c[1] - r, c[0] + r, c[1] + r, fill='#1b1b24', outline='#6a6a7a', width=2); cv.create_oval(c[0] - r * .55, c[1] - r * .65, c[0] - r * .1, c[1] - r * .2, fill='#8a8aa0', outline='')
            sp = '#ffd24a' if int(time.perf_counter() * 18) % 2 else '#ff6a00'; fz = (c[0] + r * .55, c[1] - r * 1.2)
            cv.create_line(c[0] + r * .2, c[1] - r * .85, fz[0], fz[1], fill='#c9b8a0', width=2); cv.create_oval(fz[0] - 3.5 * S, fz[1] - 3.5 * S, fz[0] + 3.5 * S, fz[1] + 3.5 * S, fill=sp, outline='')
            return c
        if k == 'bow':
            a = (hand[0] - nx * 26 * S, hand[1] - ny * 26 * S); b = (hand[0] + nx * 26 * S, hand[1] + ny * 26 * S); m_ = (hand[0] + dx * 12 * S, hand[1] + dy * 12 * S)
            cv.create_line(*[v for p in (a, m_, b) for v in R(p)], width=max(2, int(3.4 * S)), fill=col, smooth=True, capstyle='round'); line(a, b, '#e8e0c8', 1.2 * S)
            if s.aim > 0: line((hand[0] - dx * 6 * S, hand[1] - dy * 6 * S), (hand[0] + dx * 36 * S, hand[1] + dy * 36 * S), '#f0e6c0', 2 * S)
            return R((hand[0] + dx * 36 * S, hand[1] + dy * 36 * S))
        if k in ('bo', 'nunchaku', 'axe', 'hammer'):
            tnow = time.perf_counter()
            if k == 'bo':
                a = (hand[0] - dx * 38 * S, hand[1] - dy * 38 * S); b = (hand[0] + dx * (L - 38 * S), hand[1] + dy * (L - 38 * S)); line(a, b, hilt, 4.4 * S)
                for p_ in (a, b): c_ = R(p_); cv.create_oval(c_[0] - 4 * S, c_[1] - 4 * S, c_[0] + 4 * S, c_[1] + 4 * S, fill='#d9b44a', outline='')
                return R(b)
            if k == 'nunchaku':
                b = (hand[0] + dx * 20 * S, hand[1] + dy * 20 * S); act = s.mv and s.mv.startswith('sw_'); phi = 1.2 + (1.6 * math.sin(tnow * 16) if act else .5 * math.sin(tnow * 3))
                ex, ey = dx * math.cos(phi) - dy * math.sin(phi), dx * math.sin(phi) + dy * math.cos(phi); m_ = (b[0] + ex * 7 * S, b[1] + ey * 7 * S); c = (m_[0] + ex * 22 * S, m_[1] + ey * 22 * S)
                line((hand[0] - dx * 6 * S, hand[1] - dy * 6 * S), b, hilt, 4.6 * S); line(b, m_, '#9aa3b8', 1.6 * S); line(m_, c, hilt, 4.6 * S); return R(c)
            end = (hand[0] + dx * (L - 12 * S), hand[1] + dy * (L - 12 * S)); line((hand[0] - dx * 10 * S, hand[1] - dy * 10 * S), end, hilt, 3.6 * S)
            if k == 'axe': pts = [(end[0] - dx * 8 * S + nx * 3 * S, end[1] - dy * 8 * S + ny * 3 * S), (end[0] - dx * 15 * S + nx * 27 * S, end[1] - dy * 15 * S + ny * 27 * S), (end[0] + dx * 14 * S + nx * 27 * S, end[1] + dy * 14 * S + ny * 27 * S), (end[0] + dx * 12 * S + nx * 3 * S, end[1] + dy * 12 * S + ny * 3 * S)]
            else: pts = [(end[0] - dx * 11 * S + nx * 16 * S, end[1] - dy * 11 * S + ny * 16 * S), (end[0] + dx * 11 * S + nx * 16 * S, end[1] + dy * 11 * S + ny * 16 * S), (end[0] + dx * 11 * S - nx * 16 * S, end[1] + dy * 11 * S - ny * 16 * S), (end[0] - dx * 11 * S - nx * 16 * S, end[1] - dy * 11 * S - ny * 16 * S)]
            if wp.get('glow'): cv.create_polygon([v for p in pts for v in R(p)], fill=wp['glow'], outline=wp['glow'], width=max(3, int(5 * S)))
            cv.create_polygon([v for p in pts for v in R(p)], fill=col, outline='#3a4458', width=1); return R(end)
        if k == 'staff':
            a = (hand[0] - dx * 34 * S, hand[1] - dy * 34 * S); b = (hand[0] + dx * (L - 14 * S), hand[1] + dy * (L - 14 * S)); line(a, b, hilt, 3 * S)
            if wp.get('orb'):
                c = R((b[0] + dx * 8 * S, b[1] + dy * 8 * S)); r = 9 * S; pulse = 1 + .15 * math.sin(time.perf_counter() * 6)
                cv.create_oval(c[0] - r * 1.5 * pulse, c[1] - r * 1.5 * pulse, c[0] + r * 1.5 * pulse, c[1] + r * 1.5 * pulse, outline=col, width=2); cv.create_oval(c[0] - r, c[1] - r, c[0] + r, c[1] + r, fill=col, outline='#ffffff', width=2)
                return c
            hd = [(b[0] + nx * 5 * S, b[1] + ny * 5 * S), (b[0] + dx * 22 * S, b[1] + dy * 22 * S), (b[0] - nx * 5 * S, b[1] - ny * 5 * S), (b[0] + dx * 4 * S, b[1] + dy * 4 * S)]
            cv.create_polygon([v for p in hd for v in R(p)], fill=col, outline='#3a4458', width=1); line((b[0] - dx * 6 * S, b[1] - dy * 6 * S), (b[0] - dx * 6 * S + nx * 5 * S, b[1] - dy * 6 * S + ny * 5 * S), '#d23a3a', 2 * S)
            return R((b[0] + dx * 22 * S, b[1] + dy * 22 * S))
        N = 8; left = []; right = []; wb = wp['wb'] * S
        for i in range(N + 1):
            t = i / N; cx = gp[0] + dx * L * t + nx * wp['curv'] * L * t * t; cy = gp[1] + dy * L * t + ny * wp['curv'] * L * t * t; wd = wb * (1 - t) if k == 'thin' else wb * (1 - t ** 2.4)
            left.append((cx + nx * wd, cy + ny * wd)); right.append((cx - nx * wd, cy - ny * wd))
        poly = [v for p in left + right[::-1] for v in R(p)]
        if glow: cv.create_polygon(poly, fill=glow, outline=glow, width=max(3, int(5 * S)))
        cv.create_polygon(poly, fill=col, outline='#3a4458', width=1)
        cv.create_line(*[v for p in left[1:-1] for v in R(p)], fill='#ffffff', width=1)
        gw = wp['gw'] * S
        if gw: line((gp[0] - nx * gw, gp[1] - ny * gw), (gp[0] + nx * gw, gp[1] + ny * gw), hilt if k != 'thin' else '#d9a21b', 3 * S)
        if k == 'thin':
            c = R(gp); cv.create_oval(c[0] - 4 * S, c[1] - 4 * S, c[0] + 4 * S, c[1] + 4 * S, outline='#d9a21b', width=max(1, int(S)))
        line((hand[0] - dx * 7 * S, hand[1] - dy * 7 * S), gp, hilt, 3.4 * S); c = R((hand[0] - dx * 8 * S, hand[1] - dy * 8 * S)); cv.create_oval(c[0] - 2.5 * S, c[1] - 2.5 * S, c[0] + 2.5 * S, c[1] + 2.5 * S, fill='#d9b44a', outline='')
        tip = R(left[-1])
        if lead and glow and s.mv and s.mv.startswith('sw_') and .2 < s.mp < .9 and len(g.fx) < 400: g.fx.append([tip[0], tip[1], random.uniform(-70, 70), random.uniform(-150, -20), .4, glow])
        return tip
class E(F): pass

# ============================================================== game state & logic
g = NS(state='menu', mode='camp', mi=0, sel=1, lv=1, cl=1, last=time.perf_counter(), fx=[], tx=[], rings=[], lines=[], en=[], ultq=[], hero=None, tg=None, help=True, unf=0, err='', wrong=('', 0),
       ok=0, bad=0, cb=0, mc=0, score=0, kills=0, t=0, ct=0, rage=0, sp=0, ban=0, to=0, bq=False, wv=1, slow=0, hs=0, shake=0, sx=0, sy=0, inv=0, wk=[], stars=0, passed=False, title='', sub='',
       tip=0, new_rec=False, ult_t=0, toast=['', 0], quit=False, warn=0, coins=0, earned=0, tab=0, si=0, pv=None, pvd=None, pvt=0, pvi=0, pvh=0,
       les=None, gl=None, bl=1, assist=1.0, manual=0, flash=0, haz=[], sched=[], mod='', hit_taken=False, ap=0, mch=0, mmode='camp', achq=[], ach_show=None, ach_t=0, dly=None, chw=0)
HELD = {'Left': 0, 'Right': 0, 'Down': 0}; JT = [0.0]; g.bsel = max(1, min(12, D['bn_unlocked'])); g.tsel = max(1, min(KD.TOTAL, D['tutor_ul']))
g.sel = max(1, min(D['unlocked'], A.level or D['unlocked'])); g.proj = []; g.beams = []; g.slashes = []; g.bolts = []; g.mmoved = False; g.cursor = ''
SPEEDS = [.25, .4, .5, .6, .75, .9, 1.0, 1.15, 1.3, 1.5, 1.75, 2.0, 2.5, 3.0]
def SPD():
    try: return max(.2, min(4.0, float(D['speed'])))
    except Exception: return 1.0
def spd_label(v=None): v = SPD() if v is None else v; return 'Very slow' if v < .6 else 'Slow' if v < .95 else 'Normal' if v < 1.1 else 'Fast' if v < 1.6 else 'Very fast'
def step_speed(d):
    i = min(range(len(SPEEDS)), key=lambda k: abs(SPEEDS[k] - SPD())); D['speed'] = SPEEDS[max(0, min(len(SPEEDS) - 1, i + d))]; save(); snd('move')
if A.speed: D['speed'] = max(.2, min(4.0, A.speed))
MENU = ['Typing Tutor', 'Campaign', 'Daily Challenge', 'Challenge Mode', 'Bangla Typing', 'Free Practice', 'Survival', 'Boss Rush', 'Weak-Key Trainer', 'Custom Text', 'Speed Test  60s', 'Heroes', 'Armory', 'Achievements', 'Stats', 'Quit']
LVROWS = ('Campaign', 'Free Practice')
WEAKL = dict(n=100, title='Weak-Key Trainer', mode='weak', lo=3, hi=9, new='', text='Words built from YOUR weakest keys, picked from your own mistakes. No damage - just train.', boss=False, spd=1.0, strict=False, ch=0)
CUSTOML = dict(n=100, title='Custom Text', mode='custom', lo=3, hi=80, new='', text='Practice your own text. Edit the file custom.txt in the TypeStrike data folder (one line per enemy).', boss=False, spd=1.0, strict=False, ch=0)
NEUTRAL = dict(n=100, title='', mode='mixed', lo=10, hi=60, new='', text='', boss=False, spd=1.0, strict=False, ch=0)
BNL = lambda L: dict(n=100, title=KD.bn_title(L), mode='bn', lo=3, hi=30, new='', text='Type the Bangla word using English letters (phonetic), or switch your keyboard to Bangla and press the real Bangla keys (see option on the map screen).', boss=L % 6 == 0, spd=1.0, strict=False, ch=0)
def wkey(): return D['weapon'] if D['weapon'] in D['owned'] else 'fists'
def skey(): return D['style'] if D['style'] in D['own_styles'] else 'boxing'
def new_hero():
    h = F('hero', SW / 2, GY); h.wp = None if wkey() == 'fists' else wkey(); h.hk = D['hero'] if D['hero'] in D['own_heroes'] and D['hero'] in HEROES else 'kai'; return h
g.hero = new_hero()
def quit_():
    save(); g.quit = True; SND.close()
    try: root.destroy()
    except Exception: pass
def pshape(x, y, vx, vy, life, c, sz=4, sh='s', grav=900):
    g.fx.append([x, y, vx, vy, life, c, sz, sh, grav, life])
    if len(g.fx) > 450: del g.fx[:150]
def puff(x, y, c, n=5, sz=7):
    for _ in range(n): pshape(x + random.uniform(-12, 12) * FS, y, random.uniform(-90, 90), random.uniform(-90, -10), random.uniform(.35, .6), c, sz * random.uniform(.7, 1.3), 'o', -30)
def dust(x, y, n=5): puff(x, y - 4, '#b8a58c' if D['theme'] == 'dark' else '#8a7a62', n, 6)
def bolt(x1, y1, x2, y2, c, n=8, jit=26):
    pts = [(x1, y1)] + [(x1 + (x2 - x1) * i / n + random.uniform(-jit, jit) * FS, y1 + (y2 - y1) * i / n + random.uniform(-jit * .3, jit * .3) * FS) for i in range(1, n)] + [(x2, y2)]
    g.bolts.append([pts, .28, c])
    if len(g.bolts) > 16: del g.bolts[:4]
def spark(x, y, c, n=8):
    g.fx.extend([x, y, random.uniform(-320, 320), random.uniform(-460, 60), .5, c] for _ in range(n))
    if len(g.fx) > 450: del g.fx[:150]
def say(x, y, t, c=None, life=.8, z=22):
    g.tx.append([x, y, t, life, c or C('acc'), z])
    if len(g.tx) > 25: del g.tx[:5]
def ring(x, y, c=None): g.rings.append([x, y, 8, .35, c or C('acc')])
def toast(t): g.toast = [t, 2.2]
def wpm(): return round(g.ok / 5 / max(g.t / 60, .05))
def acc(): return round(g.ok / (g.ok + g.bad) * 100) if g.ok + g.bad else 100
def reach(f): return (WP[f.wp]['reach'] if f.wp else 0) * FS
def gap(e): return 34 * FS + 18 * e.sc + reach(e)
def hgap(e): return 30 * FS + 16 * e.sc + reach(g.hero)
def alive(): return [e for e in g.en if not e.dead and not e.dying]
def chain(): h = g.hero; return WP[h.wp]['chain'] if h.wp else STY[skey()]['chain']
def fins(): h = g.hero; return WP[h.wp]['fins'] if h.wp else STY[skey()]['fins']
def ldur(): h = g.hero; return (WP[h.wp]['dur'] if h.wp else STY[skey()]['dur']) / HEROES[h.hk]['sp']
def power(): h = g.hero; return (WP[h.wp]['power'] if h.wp else STY[skey()]['power']) * HEROES[h.hk]['pw']
def nextwave():
    les = lesson_now(); m = les['mode']; g.mod = ''
    if g.mode in ('camp', 'prac'): g.to = KD.enemies(g.cl); g.bq = les['boss']
    elif g.mode == 'daily': g.to = 10; g.bq = True
    elif g.mode == 'bn': g.to = 6 if g.bl % 6 == 0 else 8; g.bq = g.bl % 6 == 0
    elif g.mode == 'rush': g.to = 0; g.bq = True; g.cl = min(120, 20 + 10 * g.wv)
    elif g.mode == 'weak': g.to = 14; g.bq = False
    elif g.mode == 'custom': g.to = min(25, len(g.cust)); g.bq = False
    elif g.mode == 'surv': g.to = 3 + g.wv; g.bq = g.wv % 5 == 0; g.cl = min(100, 12 + 2 * g.wv)
    elif g.mode == 'chal':
        g.to = min(14, 4 + g.wv // 2); g.bq = g.wv % 5 == 0; g.cl = min(120, 14 + 3 * g.wv)
        if g.wv % 3 == 0 and not g.bq: g.mod = ['fast', 'swarm', 'blind'][(g.wv // 3 - 1) % 3]; toast({'fast': 'MODIFIER: FAST ENEMIES', 'swarm': 'MODIFIER: SWARM', 'blind': 'MODIFIER: BLIND - letters hide!'}[g.mod])
    else: g.to = 99999; g.bq = False
    g.ban = 2.0; g.sp = .6
CUSTOM_SAMPLE = ['Put your own practice lines in this file, one line per enemy.', 'Typing my own notes is the best way to learn them.', 'The quick brown fox jumps over the lazy dog.']
def load_custom():
    p = os.path.join(DATA, 'custom.txt'); ln = []
    try:
        if not os.path.exists(p): open(p, 'w', encoding='utf-8').write('\n'.join(CUSTOM_SAMPLE) + '\n')
        for l in open(p, encoding='utf-8', errors='replace').read().split('\n'):
            l = ''.join(c for c in l.strip() if c in string.printable and c not in '\t\r\x0b\x0c')[:90]
            if len(l) >= 2: ln.append(l)
    except Exception: log(traceback.format_exc())
    return ln or list(CUSTOM_SAMPLE)
def begin(mode, L=1):
    g.mode = mode; g.lv = L; g.hero = new_hero(); g.en = []; g.fx = []; g.tx = []; g.rings = []; g.lines = []; g.tg = None; g.ultq = []; g.proj = []; g.beams = []; g.slashes = []; g.bolts = []; g.haz = []; g.sched = []
    g.ok = g.bad = g.cb = g.mc = g.score = g.kills = g.coins = g.earned = 0; g.t = g.ct = g.rage = g.slow = g.hs = g.shake = g.sx = g.sy = g.inv = g.flash = g.manual = 0; g.wv = 1; g.wrong = ('', 0); g.unf = 0; g.err = ''; g.toast = ['', 0]; g.hit_taken = False
    for k_ in HELD: HELD[k_] = 0
    WR.seed(); g.les = None; g.gl = None; g.assist = 1.0; g.bl = 1; g.mod = ''
    if mode in ('camp', 'prac'): g.cl = L; g.assist = 1.2 if (mode == 'camp' and D['fails'].get(str(L), 0) >= 2) else 1.0; g.assist = 1.35 if (mode == 'camp' and D['fails'].get(str(L), 0) >= 4) else g.assist
    elif mode == 'surv': g.cl = 12; g.les = NEUTRAL
    elif mode == 'chal': g.cl = 14; g.les = NEUTRAL
    elif mode == 'test': g.cl = 12; g.les = NEUTRAL; g.gl = 12
    elif mode == 'rush': g.cl = 30; g.les = NEUTRAL
    elif mode == 'weak': g.cl = 20; g.les = WEAKL; g.gl = WEAKL
    elif mode == 'custom': g.cl = 25; g.les = CUSTOML; g.cust = load_custom(); g.cidx = 0
    elif mode == 'bn': g.bl = L; g.cl = 11 + L; g.les = BNL(L)
    elif mode == 'daily':
        wd = datetime.date.today().weekday(); g.les = KD.daily_lesson(wd); g.gl = g.les; g.cl = max(12, min(D['unlocked'], 100)); g.bl = max(1, min(12, D['bn_unlocked'])); WR.seed(int(datetime.date.today().strftime('%Y%m%d')))
    g.tip = L; nextwave(); g.state = 'intro' if mode in ('camp', 'prac', 'bn', 'daily', 'weak', 'custom') else 'play'; g.last = time.perf_counter(); activate()

def armed_for(kind, L):
    r = random.random()
    if kind == 'boss': return 'greatsword' if L >= 14 else 'katana' if L >= 10 else 'longsword' if L >= 5 else 'gladius' if L >= 2 else None
    if kind == 'archer': return 'bow'
    if kind == 'bomber': return 'bomb'
    if kind == 'healer': return 'orbstaff'
    if kind == 'ninja': return 'katana' if (L >= 14 and r < .4) else 'daggers'
    if kind == 'shield': return 'gladius'
    if kind == 'tank': return 'greatsword' if L >= 16 else 'longsword' if L >= 10 else 'gladius' if L >= 7 else None
    if kind == 'fast': return 'daggers' if (L >= 6 and r < .6) else None
    if kind == 'grunt' and r < min(.5, .05 * (L - 2)): return random.choice(['knife', 'gladius', 'scimitar', 'rapier', 'spear'][:1 + L // 5])
    return None
KINDW = dict(fast='fast', ninja='fast', archer='fast', bomber='fast', healer='fast', tank='tank', shield='tank', grunt='grunt', boss='grunt')
LONGM = ('sent', 'para', 'code', 'office')
def pick_kind(L, m):
    if m in LONGM: return 'ninja' if (L >= 60 and random.random() < .1) else 'grunt'
    al = [e.kind for e in g.en if not e.dead and not e.dying]; pool = [('grunt', 40)]
    if L >= 3: pool.append(('fast', 14))
    if L >= 5: pool.append(('shield', 12))
    if L >= 6: pool.append(('tank', 11))
    if L >= 7: pool.append(('ninja', 12))
    if L >= 9 and 'archer' not in al: pool.append(('archer', 10))
    if L >= 11 and 'bomber' not in al: pool.append(('bomber', 9))
    if L >= 12 and 'healer' not in al and any(k in al for k in ('tank', 'shield', 'boss')): pool.append(('healer', 14))
    return random.choices([k for k, _ in pool], [w for _, w in pool])[0]
def boss_type():
    les = lesson_now()
    if g.mode == 'camp' or g.mode == 'prac': return les.get('bt', 'brute')
    if g.mode == 'daily': return KD.BOSS_ORDER[datetime.date.today().toordinal() % len(KD.BOSS_ORDER)]
    if g.mode == 'bn': return 'ninja' if g.bl < 12 else 'dragon'
    if g.mode == 'rush': return (KD.BOSS_ORDER + ['dragon'])[(g.wv - 1) % 8]
    return 'dragon' if g.wv % 25 == 0 else KD.BOSS_ORDER[(g.wv // 5 - 1) % len(KD.BOSS_ORDER)]
def spawn(boss=False, kindforce=None):
    L = g.cl; les = lesson_now(); m = les['mode']
    if g.mode in ('surv', 'chal', 'rush'): g.gl = remix_level()
    used = [e.w[:1] for e in g.en if not e.dead and e.w]; kind = 'boss' if boss else (kindforce or pick_kind(L, m))
    w, dsp = new_text(KINDW[kind], used, boss)
    sky = kind in ('grunt', 'fast', 'ninja') and m not in LONGM and random.random() < .25; hx_ = g.hero.x
    side = (-1 if hx_ > SW / 2 else 1) if random.random() < .8 else random.choice([-1, 1])
    if abs((-40 if side < 0 else SW + 40) - hx_) < .3 * SW: side = -side
    if sky:
        fx_ = hx_ + random.choice([-1, 1]) * random.uniform(.3, .48) * SW
        if not 80 < fx_ < SW - 80: fx_ = hx_ - (fx_ - hx_) if 80 < hx_ - (fx_ - hx_) < SW - 80 else (80 if hx_ > SW / 2 else SW - 80)
        sx0 = min(max(fx_, 80), SW - 80)
    e = E(kind, sx0 if sky else (-40 if side < 0 else SW + 40), -60 if sky else GY); e.wp = armed_for(kind, L); e.disp = dsp
    e.w = w; e.hpw = 2 if kind in ('tank', 'shield') else 1
    if boss:
        e.bt = boss_type(); bd = BOSSES[e.bt]; e.wp = bd['wp']; e.bsc = bd['sc'] / SCALE['boss']; ln_ = lesson_now().get('n', 1) if g.mode in ('camp', 'prac') else max(10, g.cl)
        p1 = 1 + (ln_ >= 60); p2 = 1 + (ln_ >= 30) + (ln_ >= 100) + (ln_ in (100, 150)); e.p2at = p2; e.hpw = p1 + p2; e.cd2 = random.uniform(3.5, 5.0)
        toast(f'BOSS: {bd["name"]}'); say(SW / 2, SH * .36, bd['line'], bd['col'], 2.2, 28)
    e.mh = e.hpw; e.shield = kind == 'shield'; e.cd = 1.0; e.dcd = random.uniform(1.2, 2.5)
    dist = max(80, abs(e.x - g.hero.x) - gap(e)); ramp = (1 + (g.wv - 1) * .06) if g.mode == 'chal' else (1 + g.wv * .03 if g.mode == 'surv' else 1)
    e.spd = min(420, enemy_speed(w, L, boss) * ramp * (1.25 if g.mod == 'fast' else 1))
    if kind == 'fast': e.spd *= 1.35
    if kind == 'bomber': e.spd *= 1.5
    if kind == 'ninja': e.spd *= 1.15
    g.en.append(e)
    if boss: snd('boss')
    return e
def fxkey(): h = g.hero; return h.wp if h.wp else skey()
def hit_sound(m):
    sn = FXP.get(fxkey(), ('', '', '', 'punch'))[3]
    if sn == 'punch' and m in KICKS: sn = 'kick'
    if sn == 'slash' and m == 'sw_thrust': sn = 'stab'
    if m == 'throw': sn = 'thud'
    snd(sn)
def hit_fx(e, m, fin=False):
    h = g.hero; wp = h.wp; cx, cy = e.x, e.y - 52 * e.sc; f = h.face; sh, c1, c2, _sn, words = FXP.get(fxkey(), ('spark', '#ffffff', '#ffffff', 'punch', ['HIT!'])); R_ = random.uniform; ch_ = random.choice
    L = (120 if fin else 74) * FS * (1.45 if wp in ('greatsword', 'axe', 'warhammer') else .8 if wp in ('knife', 'daggers', 'kunai') else 1); n = 10 if fin else 5
    if m.startswith('sw_'):
        a = dict(sw_slash=.6, sw_rise=-1.0, sw_chop=1.45, sw_thrust=0., sw_spin=.15, sw_leap=1.3, sw_cross=.7, sw_iai=0., sw_flurry=0.)[m]; lf = .3 if not fin else .45
        g.slashes.append([cx, cy, f * math.cos(a), math.sin(a), L, lf, lf, c1, 5 if fin else 3])
        if fin or wp in ('daggers', 'scimitar', 'twinswords') or m == 'sw_cross': g.slashes.append([cx, cy, f * math.cos(-a), math.sin(-a), L * .9, .3, .3, c1, 4])
    if sh == 'star':
        for k in range(8): an = k * .7854 + R_(-.1, .1); g.slashes.append([cx, cy, math.cos(an), math.sin(an), (60 if fin else 36) * FS, .22, .22, c1 if k % 2 else c2, 3])
        ring(cx, cy, c1)
    elif sh == 'lines':
        for k in range(5): g.slashes.append([cx - f * 20 * FS, cy + (k - 2) * 14 * FS, f, 0, 90 * FS, .2, .2, c1 if k % 2 else c2, 2])
        ring(cx, cy, c2)
    elif sh == 'ember':
        for _ in range(n + 3): pshape(cx, cy, R_(-160, 160), R_(-300, -60), R_(.3, .55), ch_([c1, c2]), 4.5, 'f', -200)
    elif sh == 'ripple': ring(cx, cy, c1); g.rings.append([cx, cy, 2, .45, c2])
    elif sh == 'arc':
        c0x, c0y = cx - f * 20 * FS, cy + 20 * FS
        for k in range(6): an = -1.3 + k * .5; g.slashes.append([c0x + f * math.cos(an) * 58 * FS, c0y + math.sin(an) * 58 * FS, -f * math.sin(an), math.cos(an), 30 * FS, .22, .22, c1, 4])
    elif sh == 'chi':
        ring(cx, cy, c1); g.rings.append([cx, cy, 2, .5, c2])
        for _ in range(8): pshape(cx + R_(-20, 20) * FS, cy + R_(-20, 20) * FS, R_(-60, 60), -R_(40, 130), R_(.4, .7), ch_([c1, c2]), 3.5, 'o', -20)
    elif sh == 'dust': puff(e.x, e.y - 6, mix(c2, '#8a7a62', .45), 5, 7); spark(cx, cy, c1, 3)
    elif sh == 'smoke':
        puff(cx, cy, mix(c1, '#000000', .35), 5, 8)
        for _ in range(3): pshape(cx, cy, R_(-380, 380), R_(-380, -80), .45, c2, 4, '*', 500)
    elif sh == 'petal':
        for _ in range(n + 4): pshape(cx + R_(-20, 20) * FS, cy + R_(-20, 20) * FS, R_(-140, 140), R_(-260, -60), R_(.6, 1.0), ch_([c1, '#ffffff']), 3.2, 'p', 160)
        if fin: spark(cx, cy, '#8fe3ff', 7)
    elif sh == 'spark': spark(cx, cy, c1, 6)
    elif sh == 'crossx':
        g.slashes.append([cx, cy, f * math.cos(.7), math.sin(.7), L, .25, .25, c1, 4]); g.slashes.append([cx, cy, f * math.cos(-.7), math.sin(-.7), L, .25, .25, c1, 4])
    elif sh == 'pierce':
        for k in range(6): an = k * 1.0472; g.slashes.append([cx, cy, math.cos(an), math.sin(an), 34 * FS, .2, .2, c1, 2])
        ring(cx, cy, c1)
    elif sh == 'sand': puff(e.x, e.y - 8, '#e0c070', 5, 6); spark(cx, cy, c1, 4)
    elif sh == 'shock':
        ring(e.x, e.y - 8, c1); g.rings.append([e.x, e.y - 4, 4, .5, c2])
        for k in (-1, 1): g.slashes.append([e.x + k * 50 * FS, e.y - 2, k, 0, 90 * FS, .25, .25, c2, 3])
        for _ in range(6): pshape(e.x, e.y - 8, R_(-260, 260), R_(-420, -120), .5, '#8d8574', 4.5, 's', 1100)
        g.shake = max(g.shake, 4 if not fin else 9)
    elif sh == 'wood':
        for _ in range(6): pshape(cx, cy, R_(-300, 300), R_(-300, -50), .35, c1, 3, 'l', 600)
        ring(cx, cy, c1)
    elif sh == 'starburst':
        for k in range(16): an = k * .3927; g.slashes.append([cx, cy, math.cos(an), math.sin(an), (90 if fin else 60) * FS * (1 if k % 2 else .6), .28, .28, c1 if k % 2 else c2, 3])
        ring(cx, cy, c1)
        for _ in range(3): pshape(cx, cy, R_(-300, 300), R_(-300, -60), .5, '#ffffff', 4, '*', 400)
    elif sh == 'fire':
        for _ in range(n + 6): pshape(cx + R_(-15, 15) * FS, cy + R_(-10, 10) * FS, R_(-90, 90), R_(-340, -100), R_(.35, .6), ch_([c1, c2, '#ff4a1a']), 6, 'f', -120)
        ring(cx, cy, c1)
    elif sh == 'ice':
        for k in range(8): an = k * .785 + R_(-.2, .2); pshape(cx, cy, math.cos(an) * 300, math.sin(an) * 300 - 80, .5, ch_([c1, c2]), 4, 't', 500)
        ring(cx, cy, c1)
    elif sh == 'bolt':
        bolt(cx + R_(-40, 40) * FS, cy - 240 * FS, cx, cy, c1)
        if fin: bolt(cx + R_(-80, 80) * FS, cy - 260 * FS, cx, cy, c1, 9, 34)
        ring(cx, cy, c1); spark(cx, cy, c2, 5)
    if fin: ring(cx, cy, c1); g.flash = max(g.flash, .1)
def dash(e):
    h = g.hero; h.face = 1 if e.x > h.x else -1
    if abs(h.x - e.x) > hgap(e) * 1.6:
        if g.manual > 0 or h.y < GY - 30 * FS:           # moving or in the air: ranged strike instead of a dash
            c1 = FXP.get(fxkey(), ('', '#ffffff'))[1]; x0 = h.x + h.face * 30 * FS
            for k in range(7): pshape(x0 + (e.x - x0) * k / 7, h.y - 60 * FS + random.uniform(-6, 6), h.face * 700, 0, .22, c1, 3, 'l', 0)
            snd('dash'); return
        nx = min(max(e.x - h.face * hgap(e), 40), SW - 40)
        for k in range(8): g.lines.append([h.x + (nx - h.x) * k / 8, h.y - (30 + k * 3) * FS, h.x + (nx - h.x) * k / 8 - h.face * 40 * FS, h.y - (30 + k * 3) * FS, .2])
        snd('dash'); dust(h.x, GY, 4); h.x = nx; h.vx = 0; h.trail = []
def coin_reward(e):
    if g.mode in ('prac',): return
    n = {'grunt': 3, 'fast': 4, 'tank': 8, 'boss': 40, 'ninja': 6, 'shield': 7, 'archer': 7, 'bomber': 8, 'healer': 9}[e.kind] + g.cb // 10
    n = max(1, int(n * HEROES[g.hero.hk]['lk'])); g.coins += n; say(e.x, e.y - 160 * e.sc, f'+{n}', '#ffd24a', 1.0, 18); snd('coin')
def crash(e):
    spark(e.x, e.y - 20, '#ffffff' if D['theme'] == 'dark' else '#ff9f1c', 50); spark(e.x, e.y - 20, ec('boss'), 40)
    for r_ in range(3): g.rings.append([e.x, e.y - 10, 8 - r_ * 6, .5 + r_ * .15, ec('boss')])
    say(e.x, e.y - 140 * e.sc, 'CRASH!', C('acc'), 1.2, 40); g.shake = max(g.shake, 22); g.hs = .08; snd('crash')
def launch(e, name, big=False):
    h = g.hero; vx, vy = LAUNCH[name]; pw = power(); e.dying = False; e.dead = .001; e.ds = h.face; e.stun = 0; e.shield = False; e.fuse = 0; g.kills += 1; D['st']['kills'] += 1
    if e.kind == 'boss': D['st']['bosses'] += 1; D['st']['flawless'] += 0 if g.hit_taken else 1
    if big: e.vx = h.face * min(1700, SW * .75); e.vy = -1300; e.spinr = 6; g.slow = max(g.slow, .9); g.hs = .12; g.shake = max(g.shake, 18); say(e.x, e.y - 150 * e.sc, 'LEGENDARY FINISH!', C('acc'), 1.6, 34); snd('crash')
    else:
        e.vx = h.face * vx * pw; e.vy = vy * min(1.3, pw); g.slow = max(g.slow, .22); g.hs = .06; g.shake = max(g.shake, 10 + (6 if h.wp == 'greatsword' else 0)); say(e.x, e.y - 130 * e.sc, random.choice(FXP.get(fxkey(), ('', '', '', '', ['FINISH!']))[4] + ['K.O.!']), C('acc'), .9, 26); snd('finish')
    spark(e.x, e.y - 50 * e.sc, ec(e.kind), 26); ring(e.x, e.y - 50 * e.sc, ec(e.kind)); hit_fx(e, name, True); h.hp = min(100, h.hp + 4); coin_reward(e)
def finish(e, imm=False):
    h = g.hero; g.score += round(len(e.w) * 10 * (1 + g.cb // 10 * .5)); g.rage = min(100, g.rage + 5); fl = fins()
    if e.hpw > 1:
        e.hpw -= 1; e.w, e.disp = new_text('tank', (), e.kind == 'boss'); e.i = 0; e.vx = h.face * 350; e.vy = -300; e.stun = .45; was_sh = e.shield; e.shield = False
        spark(e.x, e.y - 50 * e.sc, C('acc'), 14); ring(e.x, e.y - 50 * e.sc); say(e.x, e.y - 140 * e.sc, 'SHIELD BREAK!' if was_sh else 'BREAK!', C('cy')); snd('clang' if (h.wp or was_sh) else 'break'); h.play(random.choice(chain()), .3); g.hs = .05; g.shake = max(g.shake, 6)
        if e.kind == 'boss' and e.bt and not e.ph2 and e.hpw <= e.p2at: phase2(e)
        return
    big = e.kind == 'boss'; name = random.choice(fl if g.cb < 10 else fl[::-1][:2]); dur = FDUR.get(name, .45)
    h.play(name, dur * (.7 if imm else 1)); e.dying = True; e.w = ''; e.stun = 9; e.vx = 0
    if g.tg is e: g.tg = None
    if imm: launch(e, name, big)
    else: h.pend = (IMP[name], lambda: launch(e, name, big))
def ultimate():
    if g.rage < 100 or g.ultq: return
    D['st']['ults'] += 1; g.rage = 0; g.ultq = list(alive()); g.inv = 3; g.ult_t = 0; say(SW / 2, GY - 220 * FS, 'ULTIMATE!', C('cy'), 1.3, 40); snd('ultimate'); g.shake = 14
def unlock():
    if g.tg: g.tg.i = 0
    g.tg = None
def wrongkey(c, tgt=False):
    g.bad += 1; g.cb = 0; g.wrong = (bk(c)[0], .3); snd('wrong')
    if tgt: g.rage = max(0, g.rage - 4)
    if lesson_now().get('strict') and g.mode != 'test' and g.hero.hp > 0: g.hero.hp -= 2.2 * DM() / g.assist; g.hit_taken = True; g.hero.flash = .12
def typekey(c):
    h = g.hero; h.stun = 0
    if g.mode == 'bn' and not D['bn_native'] and c.isupper(): c = c.lower()
    if g.tg is None or g.tg.dead or g.tg.dying:
        cand = [e for e in alive() if e.w and 0 < e.i < len(e.w) and e.w[e.i] == c] or [e for e in alive() if e.w and e.i == 0 and e.w[0] == c]; g.tg = min(cand, key=lambda e: abs(e.x - h.x)) if cand else None
    e = g.tg; D['keys'] += 1
    if e is None:
        if c != ' ': wrongkey(c)
        return
    x = e.w[e.i]
    if c == ' ' and x != ' ': return
    att[x] = att.get(x, 0) + 1
    if c != x: miss[x] = miss.get(x, 0) + 1; wrongkey(c, True); return
    e.i += 1; g.ok += 1; g.cb += 1; g.mc = max(g.mc, g.cb); D['st']['combo'] = max(D['st']['combo'], g.cb); g.ct = 0; g.rage = min(100, g.rage + 1.2); dash(e)
    if e.i >= len(e.w): finish(e)
    else:
        m = chain()[(e.i - 1) % len(chain())]; h.play(m, max(ldur(), MINDUR.get(m, 0))); e.x += h.face * 7 * FS; e.stun = .22 if e.kind == 'ninja' else .5 if e.kind == 'boss' else .8; e.flash = .08; hit_fx(e, m); g.hs = .02; g.shake = max(g.shake, 2 + (2 if h.wp == 'greatsword' else 0))
        spark(e.x, e.y - 50 * e.sc, '#ffffff' if D['theme'] == 'dark' else '#ff9f1c', 4); hit_sound(m); snd('tick%d' % min(7, e.i - 1))
    if g.cb and g.cb % 10 == 0: h.hp = min(100, h.hp + 6); say(h.x, h.y - 140 * FS, '+HP', C('good')); snd('heal')
    if g.cb in (10, 25, 50, 100): toast(f'COMBO x{g.cb}!'); snd('combo')

HURT = dict(grunt=None, fast=3, tank=5, boss=None, ninja=4, archer=3.5, shield=4, bomber=11, healer=0)
def hurt(e, blockable=True, dmg=None):
    h = g.hero
    if g.inv > 0: return
    base = dmg if dmg is not None else ((2.5 + min(g.cl, 40) * .07) if e.kind == 'grunt' else (3 + min(g.cl, 40) * .06) if e.kind == 'boss' else HURT[e.kind]) * (DM() if dmg is None else 1)
    base *= HEROES[h.hk]['ar'] / g.assist * (.42 + .36 * min(1, g.cl / 100))
    if g.mode in ('prac', 'test', 'weak', 'custom'): base = 0
    if h.guard and not h.mv: h.block = .3; base *= .15; say(h.x, h.y - 140 * FS, 'GUARD', C('cy'), .6, 18); snd('clang' if (h.wp or e.wp) else 'block')
    elif blockable and not h.mv and random.random() < .35: h.block = .3; base *= .25; say(h.x, h.y - 140 * FS, 'BLOCK', C('cy'), .6, 18); snd('clang' if (h.wp or e.wp) else 'block')
    else: h.stun = .2; g.cb = 0; snd('hurt')
    if base > 0: g.hit_taken = True
    h.hp -= base; g.hs = .05; g.shake = max(g.shake, 6)
def dodged(msg='DODGE!'):
    h = g.hero; D['st']['dodges'] += 1; g.rage = min(100, g.rage + 6); say(h.x, h.y - 150 * FS, msg, '#7dff9a', .8, 24); snd('dodge')
def phase2(e):
    e.ph2 = True; e.spd *= 1.25; e.cd2 = 1.6; g.flash = .25; g.shake = max(g.shake, 22); g.hs = .12; snd('phase'); toast(f'{BOSSES[e.bt]["name"]} IS ENRAGED!')
    for r_ in range(3): g.rings.append([e.x, e.y - 60 * e.sc, 6 + r_ * 8, .6 + r_ * .15, '#ff4d4d'])
    spark(e.x, e.y - 60 * e.sc, '#ff4d4d', 30); say(e.x, e.y - 170 * e.sc, 'PHASE 2!', '#ff4d4d', 1.4, 38)
def boss_special(e):
    spec = random.choice(BOSSES[e.bt]['s2' if e.ph2 else 's1']); h = g.hero; col = BOSSES[e.bt]['col']
    if spec in ('shock', 'firewave', 'stomp'):
        for dr in ([-1, 1] if spec == 'stomp' else [e.face]): g.haz.append(dict(t='wave', x=e.x + dr * 40 * FS, v=dr * (640 if spec == 'firewave' else 520) * FS, w=34 * FS, life=3.2, col='#ff6a1a' if spec == 'firewave' else col, dmg=5, hit=False, dod=False))
        e.play('sw_chop', .6); say(h.x, h.y - 180 * FS, 'JUMP!', '#ffd24a', .9, 28); snd('wave'); g.shake = max(g.shake, 8)
    elif spec in ('bolt', 'icicle', 'rocks'):
        for k in range(3 if e.ph2 else 2): x = h.x + (0 if k == 0 else random.uniform(-280, 280) * FS); g.haz.append(dict(t='bolt', x=min(max(x, 40), SW - 40), warn=1.1 + .2 * k, life=0, col={'bolt': '#ffe14a', 'icicle': '#9be8ff', 'rocks': '#c9ad7a'}[spec], dmg=6, hit=False, near=abs(x - h.x) < 130 * FS))
        say(h.x, h.y - 180 * FS, 'MOVE!', '#ffd24a', .9, 28); snd('boltw')
    elif spec == 'blink':
        nx = h.x - e.face * 150 * FS; nx = nx if 60 < nx < SW - 60 else h.x + e.face * 150 * FS; puff(e.x, e.y - 40, '#7c5cff', 5, 9); e.x = min(max(nx, 60), SW - 60); puff(e.x, e.y - 40, '#7c5cff', 5, 9); e.cd = .2; snd('dash')
    elif spec == 'stars':
        for k in range(3): g.sched.append([.45 * k, (lambda y_=(20 if k == 1 else 64): (g.proj.append([e.x + e.face * 30 * FS, e.y - y_ * e.sc, e.face * 640 * FS, 3.5 * DM(), 4.0, e]), snd('arrow')))])
        say(h.x, h.y - 180 * FS, 'JUMP!', '#ffd24a', .9, 28); e.play('sw_thrust', .6)
    elif spec in ('summon', 'clone'):
        for _ in range(2 if spec == 'summon' else 1): spawn(False, 'ninja' if spec == 'clone' else 'grunt')
        say(e.x, e.y - 170 * e.sc, 'BACKUP!', col, 1.0, 26); snd('warn')
    elif spec == 'iai': e.tele = .6; e.flash = .6; say(h.x, h.y - 180 * FS, 'JUMP!', '#ffd24a', .9, 28); snd('warn')
def end(win):
    w = wpm(); a = acc(); L = g.lv; g.passed = False; g.new_rec = False; g.sub = ''; bonus = 0; S = D['st']; today = str(datetime.date.today()); sub = []; chap = False
    if g.mode == 'camp':
        g.passed = win and a >= 80
        g.title = 'LEVEL CLEAR!' if g.passed else ('NEED 80% ACCURACY' if win else 'DEFEATED')
        g.stars = (1 + (a >= 92) + (w >= tgt_wpm(L))) if g.passed else 0
        if g.passed:
            D['unlocked'] = max(D['unlocked'], min(TOTAL, L + 1)); D['stars'][str(L)] = max(D['stars'].get(str(L), 0), g.stars); bonus = 20 + 3 * L + g.stars * 15; D['fails'][str(L)] = 0
            if a == 100: S['perfect'] += 1
            gf = GIFT.get(L)
            if gf and gf not in D['owned']: D['owned'].append(gf); D['weapon'] = gf; sub.append(f'NEW WEAPON: {WP[gf]["name"]} (equipped)')
            sg = SGIFT.get(L)
            if sg and sg not in D['own_styles']: D['own_styles'].append(sg); D['style'] = sg; sub.append(f'NEW STYLE: {STY[sg]["name"]}')
            hg = HGIFT.get(L)
            if hg and hg not in D['own_heroes']: D['own_heroes'].append(hg); sub.append(f'NEW HERO: {HEROES[hg]["name"]} (pick in Heroes)')
            if L % 10 == 0: chap = True; bonus += 100 + 20 * (L // 10); sub.append(f'CHAPTER COMPLETE: {KD.CHAPTERS[(L - 1) // 10]}!')
            if L >= TOTAL: g.title = 'YOU ARE A GRANDMASTER!'
        else:
            D['fails'][str(L)] = D['fails'].get(str(L), 0) + 1
            if win: sub.append('You won, but too many mistakes. Slow down and aim for clean typing.')
            elif D['fails'][str(L)] >= 2: sub.append('Assist mode is ON for the next try: enemies are slower and hit softer.')
    elif g.mode == 'prac': g.passed = True; g.title = 'PRACTICE COMPLETE'
    elif g.mode == 'daily':
        g.passed = win and a >= 75; g.title = f'{g.les["name"].upper()} COMPLETE!' if g.passed else ('NEED 75% ACCURACY' if win else 'DEFEATED'); g.stars = (1 + (a >= 90) + (w >= 20)) if g.passed else 0
        if g.passed:
            if today not in D['daily']:
                bonus = 100 + min(D['streak'], 30) * 5; D['daily'][today] = g.score; S['daily'] += 1; sub.append('DAILY REWARD COLLECTED!')
                for k_ in sorted(D['daily'])[:-40]: del D['daily'][k_]
            else: D['daily'][today] = max(D['daily'][today], g.score); sub.append('Already completed today - this was a practice run (no reward).')
    elif g.mode == 'bn':
        g.passed = win and a >= 80; g.title = 'BANGLA LEVEL CLEAR!' if g.passed else ('NEED 80% ACCURACY' if win else 'DEFEATED'); g.stars = (1 + (a >= 92) + (w >= 10 + L)) if g.passed else 0
        if g.passed:
            D['bn_unlocked'] = max(D['bn_unlocked'], min(KD.BN_LEVELS, L + 1)); D['bn_stars'][str(L)] = max(D['bn_stars'].get(str(L), 0), g.stars); bonus = 25 + 6 * L + g.stars * 15; S['bn'] = sum(1 for v in D['bn_stars'].values() if v > 0)
    elif g.mode == 'rush':
        done_ = g.wv - 1 + (1 if win else 0); g.passed = True; g.title = 'BOSS RUSH CLEARED!' if win else f'FELL AT BOSS {g.wv} OF 8'; bonus = 40 * done_ + (250 if win else 0); S['rush'] = max(S.get('rush', 0), done_)
        if done_ > D['rush']: D['rush'] = done_; g.new_rec = True
    elif g.mode == 'weak': g.passed = win and a >= 70; g.title = 'TRAINING COMPLETE' if g.passed else 'KEEP TRAINING'; bonus = 10 + w // 2; S['weak'] = S.get('weak', 0) + (1 if g.passed else 0)
    elif g.mode == 'custom': g.passed = True; g.title = 'CUSTOM TEXT DONE'; bonus = 5
    elif g.mode == 'surv':
        g.passed = True; g.title = f'SURVIVED {g.wv - 1} WAVES' if g.wv > 1 else 'SURVIVAL OVER'; bonus = g.wv * 10; S['surv'] = max(S['surv'], g.wv - 1)
        if g.score > D['surv']: D['surv'] = g.score; g.new_rec = True
    elif g.mode == 'chal':
        g.passed = True; g.title = f'CHALLENGE: {g.wv - 1} WAVES CLEARED' if g.wv > 1 else 'CHALLENGE OVER'; bonus = (g.wv - 1) * 15
        if g.wv - 1 > D['chal']: D['chal'] = g.wv - 1; g.new_rec = True
    else:
        g.passed = True; g.title = 'TIME UP!'; bonus = w
        if w > D['test']: D['test'] = w; g.new_rec = True
    g.sub = '   |   '.join(sub); g.earned = g.coins + bonus; D['coins'] += g.earned; S['earned'] += g.earned
    if g.ok > 10: D['best_wpm'] = max(D['best_wpm'], w); D['hist'] = (D['hist'] + [w])[-40:]
    D['sessions'] += 1; bump_streak(); ach_check()
    r = sorted(((miss.get(k, 0) / att[k], k) for k in att if att[k] >= 5 and miss.get(k, 0) > 0), reverse=True)[:4]; g.wk = [disp(k) for _, k in r]
    g.state = 'done' if g.passed else 'fail'; save(); snd('chapter' if chap else 'win' if g.passed else 'lose')
def ach_check():
    S = D['st']; S['nweap'] = len(WORDER); S['nsty'] = len(SORDER)
    for aid, name, desc, coins, fn in ACH:
        if aid in D['ach']: continue
        try: ok = bool(fn(D, S))
        except Exception: ok = False
        if ok: D['ach'][aid] = str(datetime.date.today()); D['coins'] += coins; S['earned'] += coins; g.achq.append((name, coins))
def ach_tick(dt):
    if g.ach_show:
        g.ach_t -= dt
        if g.ach_t <= 0: g.ach_show = None
    if g.ach_show is None and g.achq: g.ach_show = g.achq.pop(0); g.ach_t = 3.4; snd('ach'); save()
SRC = NS(kind='boss', wp=None)
def do_jump():
    h = g.hero; nw_ = time.perf_counter()
    if g.state != 'play' or h.stun > 0 or h.dead or nw_ - JT[0] < .12: return
    JT[0] = nw_
    jv = 600 * FS * HEROES[h.hk]['jv']
    if h.y >= GY - 2: h.vy = -jv; h.jumps = 1; snd('jump'); dust(h.x, GY, 3); D['st']['jumps'] += 1
    elif h.jumps < 2: h.vy = -jv * .92; h.jumps = 2; h.flipt = .5; snd('jump'); spark(h.x, h.y - 20 * FS, '#ffffff' if D['theme'] == 'dark' else '#ff9f1c', 6); D['st']['jumps'] += 1

def explode(e):
    h = g.hero; e.dead = .001; e.ds = 1; e.vy = -420; e.vx = 0; e.w = ''; e.fuse = 0
    if g.tg is e: g.tg = None
    spark(e.x, e.y - 40 * e.sc, '#ffd24a', 40); spark(e.x, e.y - 40 * e.sc, '#ff6a00', 30)
    for r_ in range(3): g.rings.append([e.x, e.y - 30 * e.sc, 6 + r_ * 8, .55 + r_ * .12, '#ff8a3d'])
    say(e.x, e.y - 130 * e.sc, 'BOOM!', '#ff8a3d', 1.0, 34); g.shake = max(g.shake, 16); g.hs = .05; snd('boom')
    if abs(h.x - e.x) < 170 * FS: hurt(e, False)
def shoot(e): g.proj.append([e.x + e.face * 34 * FS, e.y - 64 * e.sc, e.face * 720 * FS, 3.5 * DM(), 4.0, e]); snd('arrow')
def heal_ally(e):
    c = [a for a in g.en if a is not e and not a.dead and not a.dying and a.kind in ('tank', 'shield', 'boss') and a.hpw < a.mh]
    if not c: return
    a = min(c, key=lambda a: abs(a.x - e.x)); a.hpw += 1; a.shield = a.shield or (a.kind == 'shield' and a.hpw == a.mh); g.beams.append([e, a, .6])
    say(a.x, a.y - 150 * a.sc, '+1', '#63e6be', .8, 24); snd('heal'); e.play('sw_rise', .5); e.hd = True
def emove(e):
    ch = [m for m in WP[e.wp]['chain'] if m != 'sw_leap'] if (e.wp and WP[e.wp]['chain']) else ATK[e.kind]
    return random.choice(ch)
def ai(e, dt, dx):
    k = e.kind; ad = abs(dx); h = g.hero
    if e.mv:
        e.vx = 0
        if not e.hd and e.mp >= IMP[e.mv]:
            e.hd = True
            if k == 'archer': shoot(e)
            elif ad < gap(e) * 1.5 and h.y >= GY - 46 * FS: hurt(e)
            elif g.manual > 0 or h.y < GY - 46 * FS: dodged('JUMPED!' if h.y < GY - 46 * FS else 'DODGE!')
        return
    if k == 'boss' and e.bt:
        if e.tele > 0:
            e.tele -= dt; e.vx = 0; e.flash = .05
            if e.tele <= 0: e.dsh = .34; e.dhit = False; snd('dash')
            return
        if e.dsh > 0:
            e.dsh -= dt; e.vx = e.face * max(e.spd * 5, 760 * FS); g.lines.append([e.x, e.y - 60 * FS, e.x - e.face * 70 * FS, e.y - 60 * FS, .15])
            if not e.dhit and abs(h.x - e.x) < 50 * FS:
                e.dhit = True
                if h.y >= GY - 50 * FS: hurt(e, False, 6 * DM())
                else: dodged('JUMPED!')
            return
        e.cd2 -= dt
        if e.cd2 <= 0 and ad > gap(e) * .8: boss_special(e); e.cd2 = random.uniform(4.5, 6.5) * (.75 if e.ph2 else 1) / (1 if g.assist == 1 else 1.2)
    if k == 'archer':
        want = 440 * FS; e.vx = e.face * e.spd if ad > want + 60 * FS else (-e.face * e.spd * .9 if ad < want - 100 * FS else 0)
        if e.cd <= 0 and ad < 800 * FS: e.play('sw_thrust', .62); e.aim = .62; e.cd = random.uniform(2.4, 3.4); snd('swing')
        return
    if k == 'healer':
        want = 520 * FS; e.vx = e.face * e.spd if ad > want + 80 * FS else (-e.face * e.spd if ad < want - 120 * FS else 0)
        if e.cd <= 0: heal_ally(e); e.cd = random.uniform(3.2, 4.2)
        return
    if k == 'bomber':
        if e.fuse > 0:
            e.vx = 0; e.fuse -= dt
            if e.fuse <= 0: explode(e)
        elif ad > gap(e) * 1.6: e.vx = e.face * e.spd
        else: e.fuse = 2.2; e.vx = 0; snd('fuse')
        return
    if k == 'ninja':
        e.dcd -= dt
        if e.dsh > 0:
            e.dsh -= dt; e.vx = e.face * e.spd * 3.4; g.lines.append([e.x, e.y - 40 * FS, e.x - e.face * 50 * FS, e.y - 40 * FS, .15])
            return
        if e.dcd <= 0 and ad > gap(e) * 2: e.dsh = .26; e.dcd = random.uniform(1.6, 2.8); snd('whoosh'); return
    if ad > gap(e) * 1.15: e.vx = e.face * e.spd
    else:
        e.vx = 0
        if e.cd <= 0:
            e.play(emove(e), (.8 if k == 'boss' else .7) if e.wp else (.42 if k == 'ninja' else .75 if k in ('tank', 'boss') else .55)); e.cd = random.uniform(*CDR[k]); snd('swing')
def update(dt):
    h = g.hero
    if g.hs > 0: g.hs -= dt; dt *= .05
    elif g.slow > 0: g.slow -= dt; dt *= .35
    g.flash = max(0, g.flash - dt); g.manual = max(0, g.manual - dt); g.t += dt; g.ct += dt; g.ban = max(0, g.ban - dt); g.inv = max(0, g.inv - dt); g.wrong = (g.wrong[0], max(0, g.wrong[1] - dt)); g.toast[1] = max(0, g.toast[1] - dt)
    g.shake *= .85; g.sx = random.uniform(-1, 1) * g.shake; g.sy = random.uniform(-1, 1) * g.shake
    h.step(dt); gnd = h.y >= GY - 1; al = alive()
    if g.ct > 3.5 and g.cb: g.cb = 0
    if h.hp < 25 and g.mode in ('camp', 'surv'):
        g.warn -= dt
        if g.warn <= 0: snd('warn'); g.warn = 1.1
    if al and not h.mv: h.face = 1 if min(al, key=lambda e: abs(e.x - h.x)).x > h.x else -1
    ax = (1 if (HELD['Right'] or down(0x27)) else 0) - (1 if (HELD['Left'] or down(0x25)) else 0); h.guard = bool(HELD['Down'] or down(0x28)) and gnd and not h.mv
    if ax and h.stun <= 0 and not h.guard:
        g.manual = .6; h.vx = ax * 360 * FS * HEROES[h.hk]['sp'] * (.5 if h.mv else 1) * (1 if gnd else .85)
        if not al and not h.mv: h.face = ax
    elif gnd: h.vx = (1 if SW / 2 > h.x else -1) * 140 * FS if (not h.mv and g.tg is None and g.manual <= 0 and abs(h.x - SW / 2) > 30) else 0
    if h.hp < 100 and all(abs(e.x - h.x) > gap(e) * 2.5 for e in al): h.hp = min(100, h.hp + 3.5 * dt)
    h.phys(dt)
    if g.ultq:
        g.ult_t -= dt
        if g.ult_t <= 0:
            e = g.ultq.pop(0)
            if not e.dead:
                e.dying = False; g.tg = e; dash(e); h.face = 1 if e.x > h.x else -1
                for _ in range(e.hpw): finish(e, True); e.dying = False
            g.ult_t = .14
    les_ = lesson_now(); m_ = les_['mode']; g.sp -= dt
    ma = max_alive()
    if g.ban <= 0 and g.sp <= 0 and len(al) < ma:
        if g.to > 0: spawn(); g.to -= 1; g.sp = max(1.5, 3.6 - min(g.cl, 40) * .05) * (1.35 if m_ in LONGM else 1) / DM() / (1.5 if g.mod == 'swarm' else 1)
        elif g.bq and not al: spawn(True); g.bq = False
    for e in g.en:
        e.step(dt)
        if e.dead: e.dead += dt; e.phys(dt); continue
        if e.dying: e.phys(dt); continue
        e.cd -= dt; dx = h.x - e.x; e.face = 1 if dx > 0 else -1
        if e.y >= GY - 1 and e.stun <= 0 and not e.dead: ai(e, dt, dx)
        e.phys(dt)
    for a in g.proj:
        a[0] += a[2] * dt; a[4] -= dt
        if abs(a[0] - h.x) < 30 * FS and abs(a[1] - (h.y - 60 * FS)) < 80 * FS and g.inv <= 0: a[4] = 0; hurt(a[5], True, a[3])
    g.proj = [a for a in g.proj if a[4] > 0 and -60 < a[0] < SW + 60]
    for z in g.haz:
        if z['t'] == 'wave':
            z['x'] += z['v'] * dt; z['life'] -= dt
            if not z['hit'] and not z['dod'] and abs(z['x'] - h.x) < z['w'] + 24 * FS:
                if h.y >= GY - 52 * FS: z['hit'] = True; hurt(SRC, False, z['dmg'] * DM())
                else: z['dod'] = True; dodged('JUMPED!')
        else:
            if z['warn'] > 0:
                z['warn'] -= dt
                if z['warn'] <= 0:
                    z['life'] = .3; bolt(z['x'], 0, z['x'], GY, z['col'], 10, 22); snd('bolth'); g.shake = max(g.shake, 8); spark(z['x'], GY - 6, z['col'], 12)
                    if abs(h.x - z['x']) < 50 * FS: hurt(SRC, False, z['dmg'] * DM())
                    elif z['near']: dodged('MOVED!')
            else: z['life'] -= dt
    g.haz = [z for z in g.haz if (z['t'] == 'wave' and z['life'] > 0 and -80 < z['x'] < SW + 80) or (z['t'] == 'bolt' and (z['warn'] > 0 or z['life'] > 0))]
    for q in g.sched:
        q[0] -= dt
        if q[0] <= 0: q[1](); q.append(1)
    g.sched = [q for q in g.sched if len(q) == 2]
    for b in g.beams: b[2] -= dt
    g.beams = [b for b in g.beams if b[2] > 0]
    for sl in g.slashes: sl[5] -= dt
    g.slashes = [sl for sl in g.slashes if sl[5] > 0][-40:]
    g.en = [e for e in g.en if not e.dead or e.dead < (3.4 if e.kind == 'boss' else 2)]
    if g.tg and (g.tg.dead or g.tg.dying): g.tg = None
    for p in g.fx: p[0] += p[2] * dt; p[1] += p[3] * dt; p[3] += (p[8] if len(p) > 8 else 900) * dt; p[4] -= dt
    for b_ in g.bolts: b_[1] -= dt
    g.bolts = [b_ for b_ in g.bolts if b_[1] > 0]
    g.fx = [p for p in g.fx if p[4] > 0]
    for q in g.tx: q[1] -= 40 * dt; q[3] -= dt
    g.tx = [q for q in g.tx if q[3] > 0]
    for r in g.rings: r[2] += 320 * dt; r[3] -= dt
    g.rings = [r for r in g.rings if r[3] > 0]
    for l in g.lines: l[4] -= dt
    g.lines = [l for l in g.lines if l[4] > 0][-60:]
    al = alive()
    if h.hp <= 0: end(False); return
    flying = any(e.kind == 'boss' and e.dead and (not e.crashed or e.dead < 2.4) for e in g.en)
    if g.mode in ('camp', 'prac', 'daily', 'bn', 'weak', 'custom'):
        if g.to == 0 and not g.bq and not al and not g.ultq and not flying and not any(e.dying for e in g.en): end(True)
    elif g.mode in ('surv', 'chal', 'rush'):
        if g.to == 0 and not g.bq and not al and not g.ultq and not flying and g.mode == 'rush' and g.wv >= 8: end(True)
        elif g.to == 0 and not g.bq and not al and not g.ultq and not flying: g.wv += 1; h.hp = min(100, h.hp + (40 if g.mode == 'rush' else 15)); nextwave(); say(SW / 2, SH * .3, f'WAVE {g.wv}', C('acc'), 1.4, 40)
    elif g.t >= 60: end(True)

# ---- armory preview (a live training demo of the selected weapon / style)
def items(): return [WORDER, SORDER, HORDER][g.tab]
def pv_setup():
    g.pv = F('hero', 0, 0); g.pvd = F('grunt', 0, 0); g.pvd.face = -1; g.pv.zoom = g.pvd.zoom = 1.75; g.pvt = .4; g.pvi = 0; g.pvh = 0
def pv_update(dt):
    if g.pv is None: pv_setup()
    pv, dm = g.pv, g.pvd; key = items()[min(g.si, len(items()) - 1)]; pv.hk = key if g.tab == 2 else D['hero']
    if g.tab == 0: pv.wp = None if key == 'fists' else key; ch = WP[key]['chain'] if key != 'fists' else STY[skey()]['chain']; du = WP[key].get('dur', STY[skey()]['dur'])
    elif g.tab == 1: pv.wp = None; ch = STY[key]['chain']; du = STY[key]['dur']
    else: wk = wkey(); pv.wp = None if wk == 'fists' else wk; ch = WP[wk]['chain'] if wk != 'fists' else STY[skey()]['chain']; du = WP[wk]['dur'] if wk != 'fists' else STY[skey()]['dur']
    pv.step(dt); dm.step(dt); g.pvt -= dt
    if g.pvt <= 0:
        m = ch[g.pvi % len(ch)]; g.pvi += 1; pv.play(m, max(du, MINDUR.get(m, 0)) * 1.5); g.pvt = max(du, MINDUR.get(m, 0)) * 1.5 + .22; g.pvh = IMP[m] * max(du, MINDUR.get(m, 0)) * 1.5
    if g.pvh > 0:
        g.pvh -= dt
        if g.pvh <= 0: dm.stun = .22; dm.x += 5
    dm.x += (dm.hx - dm.x) * min(1, dt * 6) if hasattr(dm, 'hx') else 0
def shop_enter():
    k = items()[g.si]
    if g.tab == 0:
        if k in D['owned']: D['weapon'] = k; snd('select')
        elif D['coins'] >= WP[k]['price']: D['coins'] -= WP[k]['price']; D['owned'].append(k); D['weapon'] = k; snd('buy'); toast(f'Bought {WP[k]["name"]}!')
        else: snd('wrong'); toast('Not enough coins')
    elif g.tab == 1:
        if k in D['own_styles']: D['style'] = k; snd('select')
        elif D['coins'] >= STY[k]['price']: D['coins'] -= STY[k]['price']; D['own_styles'].append(k); D['style'] = k; snd('buy'); toast(f'Learned {STY[k]["name"]}!')
        else: snd('wrong'); toast('Not enough coins')
    else:
        if k in D['own_heroes']: D['hero'] = k; snd('select'); toast(f'{HEROES[k]["name"]} selected!')
        elif D['coins'] >= HEROES[k]['price']: D['coins'] -= HEROES[k]['price']; D['own_heroes'].append(k); D['hero'] = k; snd('buy'); toast(f'{HEROES[k]["name"]} joined you!')
        else: snd('wrong'); toast('Not enough coins')
    ach_check(); save()

# ============================================================== drawing
def T(s, x, y, z=14, c=None, a='c', f=None, w='bold'):
    cv.create_text(x, y, text=s, fill=c or C('tx'), anchor={'c': 'center', 'l': 'w', 'r': 'e'}[a], font=(f or UIF, -max(8, int(z * FS)), w))
def rr(x0, y0, x1, y1, r=10, fill='', out='', w=1):
    r = min(r * FS, (x1 - x0) / 2, (y1 - y0) / 2)
    cv.create_polygon([x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y1 - r, x1, y1, x1 - r, y1, x0 + r, y1, x0, y1, x0, y1 - r, x0, y0 + r, x0, y0], smooth=True, fill=fill, outline=out, width=w)
def panel(x0, y0, x1, y1):
    rr(x0 + 6 * FS, y0 + 9 * FS, x1 + 6 * FS, y1 + 9 * FS, 16, mix(C('pan'), '#000000', .6), '', 0); rr(x0, y0, x1, y1, 16, C('pan'), C('edge'), 2)
def bar(x, y, w, h, fr, col, label):
    rr(x, y, x + w, y + h, 6, C('pan'), C('edge'), 1)
    if fr > .02: rr(x + 2, y + 2, x + 2 + (w - 4) * min(1, fr), y + h - 2, 4, col, '', 0)
    T(label, x + 8 * FS, y + h / 2, 9, C('tx'), 'l')
def heat(k):
    a_ = att.get(k, 0)
    if a_ < 3: return None
    r = miss.get(k, 0) / a_; return '#2f9e44' if r < .06 else '#e0a800' if r < .16 else '#d6303a'
def keyboard(A_, nw, hint, hm=False):
    ks = KS; ox = SW / 2 - 6.9 * ks; oy = KBY; base = {bk(c)[0] for c in A_}; hk, hs = bk(hint) if hint else (None, False)
    for r, (row, off) in enumerate((('`1234567890-=', 0), ('qwertyuiop[]\\', .5), ("asdfghjkl;'", .75), ('zxcvbnm,./', 1.25))):
        for j, c in enumerate(row):
            x = ox + (j + off) * ks; y = oy + r * (ks + 4); col = fc(FGM[c]); on = c in base or hm; hc = heat(c) if hm else None
            fill = hc or (col if c == hk else C('bad') if (g.wrong[0] == c and g.wrong[1] > 0) else C('key'))
            rr(x + 1, y + 1, x + ks - 3, y + ks - 3, 6, fill, col if on else C('off'), 3 if c in nw else 1)
            T(c, x + ks / 2 - 1, y + ks / 2, 14, '#000000' if (c == hk or hc) else (col if on else C('off')), f=MONOF)
    yy = oy + 3 * (ks + 4); lsh = bool(hs) and FGM.get(hk, 0) >= 4; rsh = bool(hs) and FGM.get(hk, 4) < 4
    rr(ox + 1, yy + 1, ox + 1.2 * ks, yy + ks - 3, 6, fc(0) if lsh else C('key'), C('off'), 1); T('Shift', ox + .6 * ks, yy + ks / 2, 9, '#000000' if lsh else C('off'))
    rr(ox + 11.3 * ks, yy + 1, ox + 13.2 * ks, yy + ks - 3, 6, fc(7) if rsh else C('key'), C('off'), 1); T('Shift', ox + 12.25 * ks, yy + ks / 2, 9, '#000000' if rsh else C('off'))
    sp_ = hint == ' '; rr(ox + 3 * ks, yy + ks + 4, ox + 8.2 * ks, yy + 2 * ks + 1, 6, fc(8) if sp_ else C('key'), C('off'), 1); T('Space', ox + 5.6 * ks, yy + 1.5 * ks + 3, 10, '#000000' if sp_ else C('off'))
    if hint and not hm:
        i = FGM.get(hk, 8); T(f'{disp(hint)}   ->   {FN[i]}' + ('  (+ Shift)' if hs else ''), SW / 2, oy - 16 * FS, 15, fc(i))
_BN_CONS = set(chr(c) for c in range(0x0995, 0x09BA)) | set('\u09dc\u09dd\u09df\u09ce')
_BN_AFTER = set('\u09be\u09bf\u09c0\u09c1\u09c2\u09c3\u09c4\u09c7\u09c8\u09cb\u09cc\u09d7\u0981\u0982\u0983')
def bn_visual(t):
    """Tk on Linux does not reorder Bangla: put the left-side vowel signs (i, e, ai, o, au) in front of their consonant by hand."""
    out = []; i = 0; n = len(t)
    while i < n:
        if t[i] in _BN_CONS:
            j = i + 1
            while j < n and t[j] == '\u09bc': j += 1
            while j + 1 < n and t[j] == '\u09cd' and t[j + 1] in _BN_CONS:
                j += 2
                while j < n and t[j] == '\u09bc': j += 1
            k = j; pre = ''; post = ''
            while k < n and t[k] in _BN_AFTER:
                v = t[k]
                if v in '\u09bf\u09c7\u09c8': pre += v
                elif v == '\u09cb': pre += '\u09c7'; post += '\u09be'
                elif v == '\u09cc': pre += '\u09c7'; post += '\u09d7'
                else: post += v
                k += 1
            out.append(pre + t[i:j] + post); i = k
        else: out.append(t[i]); i += 1
    return ''.join(out)
def bn_fix_on(): v = D['bn_fix']; return (not BN_SHAPES[0]) if v in (None, 'auto') else bool(v)
def bnt(t): return bn_visual(t) if (t and bn_fix_on()) else t
def lab_font(w):
    mw = FL.measure(w); lim = SW * .92
    if mw <= lim: return FL, mw
    sz = max(9, int(max(12, int(19 * FS)) * lim / mw))
    if sz not in FCACHE: FCACHE[sz] = tkf.Font(root, family=MONOF, size=-sz, weight='bold')
    return FCACHE[sz], FCACHE[sz].measure(w)
def bn_native(): return D['bn_native'] and (g.mode == 'bn' or bool(g.les and g.les.get('mode') == 'bn'))
def label(e, slot=0):
    if e.dead or e.dying or not e.w: return
    w = e.w; nat = bn_native(); show = w if g.mod != 'blind' else w[:e.i + 2] + '.' * max(0, len(w) - e.i - 2)
    f_, mw = (FB, FB.measure(bnt(show))) if nat else lab_font(show); idx = KD.bn_split(show, e.i) if nat else e.i; two = bool(e.disp); hh = 17 * FS * (1.9 if two else 1)
    ly = e.y - 95 * e.sc - 16 * FS - (hh - 17 * FS) - slot * (2 * hh + 14 * FS); bw = max(mw, FB.measure(bnt(e.disp)) if two else 0); x0 = min(max(e.x - bw / 2, 22), SW - bw - 24)
    rr(x0 - 8, ly - hh, x0 + bw + 8, ly + hh, 8, C('pan'), C('acc') if e is g.tg else C('edge'), 2)
    ty = ly + (hh * .42 if two else 0)
    if two: cv.create_text(x0 + bw / 2, ly - hh * .42, text=bnt(e.disp), fill=C('acc'), font=FB)
    ts_, tr_ = (bnt(show[:idx]), bnt(show[idx:])) if nat else (show[:idx], show[idx:]); tx0 = x0 + (bw - mw) / 2 if two else x0; tw = f_.measure(ts_); cv.create_text(tx0, ty, text=ts_, anchor='w', fill=C('good'), font=f_); cv.create_text(tx0 + tw, ty, text=tr_, anchor='w', fill=C('tx'), font=f_)
    if e.hpw > 1: T(('<3 ' * e.hpw) if e.kind != 'boss' else ('PHASE 2   ' if e.ph2 else '') + '<3 ' * e.hpw, e.x, ly - hh - 9 * FS, 12, C('bad'))
def gear_name(): return (WP[wkey()]['name'] if wkey() != 'fists' else STY[skey()]['name'])
def rankline(): return f'{rank(D["best_wpm"])}   -   best {D["best_wpm"]} WPM'
def coin_icon(x, y, r=8):
    cv.create_oval(x - r * FS, y - r * FS, x + r * FS, y + r * FS, fill='#ffd24a', outline='#b88a00', width=2); cv.create_oval(x - r * .4 * FS, y - r * .4 * FS, x + r * .4 * FS, y + r * .4 * FS, outline='#b88a00')

BT = []; MOUSE = [-1, -1]
def hover(x0, y0, x1, y1): return x0 <= MOUSE[0] <= x1 and y0 <= MOUSE[1] <= y1
def button(x0, y0, x1, y1, label, act, style='n', z=16):
    hv = hover(x0, y0, x1, y1)
    if act: BT.append((x0, y0, x1, y1, act))
    if style == 'p': fill = mix(C('sel'), '#ffffff', .22) if hv else C('sel'); tc = C('seltx'); out = mix(fill, '#000000', .35)
    elif style == 'd': fill = C('pan'); tc = C('dim'); out = C('edge')
    else: fill = mix(C('key'), C('sel'), .3) if hv else C('key'); tc = C('tx'); out = C('acc') if hv else C('edge')
    rr(x0, y0, x1, y1, 10, fill, out, 2); T(label, (x0 + x1) / 2, (y0 + y1) / 2, z, tc); return hv
def row_button(x0, y0, x1, y1, sel, act):
    hv = hover(x0, y0, x1, y1); BT.append((x0, y0, x1, y1, act))
    rr(x0, y0, x1, y1, 9, C('sel') if sel else (mix(C('key'), C('sel'), .25) if hv else C('key')), C('edge') if not sel else '', 1 if not sel else 0); return hv
def draw_hud():
    h = g.hero; bcol = 140 * FS; w = min(SW - 2 * (bcol + 16 * FS), 900 * FS); x0 = (SW - w) / 2; y0 = 10 * FS; hh = 62 * FS; panel(x0, y0, x0 + w, y0 + hh)
    lt = g.to + (1 if g.bq else 0) + len(alive()); mode = {'camp': f'LV {g.lv}', 'prac': f'PRAC {g.lv}', 'surv': f'WAVE {g.wv}', 'test': 'TEST', 'daily': 'DAILY', 'chal': f'WAVE {g.wv}', 'bn': f'BN {g.lv}', 'rush': f'BOSS {g.wv} / 8', 'weak': 'WEAK KEYS', 'custom': 'CUSTOM'}[g.mode]
    last = ('TIME', f'{max(0, 60 - int(g.t))}s') if g.mode == 'test' else ('ENEMIES', lt)
    cols = [('MODE', mode), ('SCORE', g.score), ('WPM', wpm()), ('ACCURACY', f'{acc()}%'), ('COMBO', f'{g.cb}x'), last]; cw = w / 6
    for i, (a_, b_) in enumerate(cols): cx = x0 + cw * (i + .5); T(a_, cx, y0 + 16 * FS, 9, C('dim')); T(str(b_), cx, y0 + 41 * FS, 20, C('acc') if (a_ == 'COMBO' and g.cb >= 5) else C('tx'))
    bw = min(300 * FS, w * .34); by = y0 + hh + 12 * FS
    bar(x0, by, bw, 20 * FS, h.hp / 100, C('good') if h.hp > 35 else C('bad'), 'HP'); bar(x0 + w - bw, by, bw, 20 * FS, g.rage / 100, C('cy'), 'RAGE')
    T(gear_name(), x0 + 4 * FS, by + 42 * FS, 12, C('dim'), 'l'); coin_icon(x0 + w - 80 * FS, by + 42 * FS, 7); T(str(D['coins'] + g.coins), x0 + w - 64 * FS, by + 42 * FS, 14, C('acc'), 'l')
    if g.rage >= 100: T('PRESS ENTER  -  ULTIMATE!', SW / 2, by + 10 * FS, 18, C('cy') if int(time.perf_counter() * 4) % 2 else C('acc'))
    elif g.cb >= 3: T(f'{g.cb}x COMBO', SW / 2, by + 10 * FS, 18 + min(g.cb, 12), C('acc'))
    if g.toast[1] > 0: T(g.toast[0], SW / 2, by + 62 * FS, 20, C('good'))
    bs_ = next((e for e in g.en if e.kind == 'boss' and e.bt and not e.dead and not e.dying), None)
    if bs_:
        bw2 = w * .7; bx = SW / 2 - bw2 / 2; byy = by + 84 * FS; bd = BOSSES[bs_.bt]; rr(bx, byy, bx + bw2, byy + 22 * FS, 7, C('pan'), bd['col'], 2); fr = bs_.hpw / max(1, bs_.mh)
        rr(bx + 3, byy + 3, bx + 3 + (bw2 - 6) * fr, byy + 22 * FS - 3, 5, mix(bd['col'], '#ff2a2a', .4 if bs_.ph2 else 0), '', 0)
        if 0 < bs_.p2at < bs_.mh: xm = bx + 3 + (bw2 - 6) * bs_.p2at / bs_.mh; cv.create_line(xm, byy + 2, xm, byy + 22 * FS - 2, fill=C('tx'), width=2)
        T(bd['name'].upper() + ('  -  ENRAGED' if bs_.ph2 else ''), SW / 2, byy + 11 * FS, 11, '#ffffff' if bs_.ph2 else C('tx'))
    for i, (lb, a) in enumerate((('Pause', 'k:Escape'), ('Keys', 'k:F1'), ('Theme', 'k:F2'), ('Sound', 'k:F3'))):
        button(SW - bcol - 12 * FS, 12 * FS + i * 42 * FS, SW - 12 * FS, 12 * FS + i * 42 * FS + 34 * FS, lb, a, 'n', 12)
    T('Arrows: Left/Right move   Up jump (twice = flip)   Down guard      Tab next target   Backspace unlock   Esc pause   Enter ULTIMATE', SW / 2, SH - 12 * FS if not OVERLAY else SH - 34 * KB, 11, C('dim'))
def draw_game():
    cv.create_line(0, GY + 4, SW, GY + 4, fill=C('gnd'), width=max(2, int(3 * FS)))
    for l in g.lines: cv.create_line(l[0], l[1], l[2], l[3], fill=C('cy'), width=2)
    for e in sorted(g.en, key=lambda e: e.sc):
        if e.kind == 'archer' and e.aim > 0 and not e.dead: cv.create_line(e.x, e.y - 64 * e.sc, g.hero.x, g.hero.y - 60 * FS, fill='#ff6b6b', width=2, dash=(6, 6))
        e.draw()
    g.hero.draw()
    for z in g.haz:
        x_ = z['x']
        if z['t'] == 'wave':
            hh_ = 46 * FS * (.75 + .25 * math.sin(time.perf_counter() * 20)); sg_ = 1 if z['v'] > 0 else -1
            cv.create_polygon(x_ - 30 * FS * sg_, GY + 3, x_, GY - hh_, x_ + 12 * FS * sg_, GY + 3, fill=z['col'], outline=''); cv.create_polygon(x_ - 16 * FS * sg_, GY + 3, x_ - 2 * FS * sg_, GY - hh_ * .55, x_ + 6 * FS * sg_, GY + 3, fill='#ffffff', outline='')
        elif z['warn'] > 0:
            cv.create_rectangle(x_ - 40 * FS, 0, x_ + 40 * FS, GY, outline=z['col'], width=2, dash=(8, 8)); T('!', x_, GY - 40 * FS, 34 if int(time.perf_counter() * 8) % 2 else 28, z['col'])
        else:
            wd_ = 26 * FS * z['life'] / .3 + 3; cv.create_rectangle(x_ - wd_, 0, x_ + wd_, GY, fill=z['col'], outline='', stipple='gray50')
    for b in g.beams: cv.create_line(b[0].x, b[0].y - 80 * b[0].sc, b[1].x, b[1].y - 70 * b[1].sc, fill=ec('healer'), width=max(2, int(5 * FS * b[2] / .6)), dash=(5, 4))
    for sl in g.slashes:
        k = sl[5] / sl[6]; hl = sl[4] / 2; x0, y0, x1, y1 = sl[0] - sl[2] * hl, sl[1] - sl[3] * hl, sl[0] + sl[2] * hl, sl[1] + sl[3] * hl
        cv.create_line(x0, y0, x1, y1, width=max(1, int(sl[8] * FS * k * 1.6)), fill=sl[7], capstyle='round'); cv.create_line(x0, y0, x1, y1, width=max(1, int(sl[8] * FS * k * .6)), fill='#ffffff', capstyle='round')
    for a in g.proj:
        sg = 1 if a[2] > 0 else -1; cv.create_line(a[0] - sg * 28 * FS, a[1], a[0] + sg * 10 * FS, a[1], fill='#f0e6c0', width=max(2, int(3 * FS)), capstyle='round'); cv.create_oval(a[0] + sg * 6 * FS - 3 * FS, a[1] - 3 * FS, a[0] + sg * 6 * FS + 5 * FS, a[1] + 3 * FS, fill='#c9c9d6', outline='')
    for r in g.rings: cv.create_oval(r[0] - r[2], r[1] - r[2], r[0] + r[2], r[1] + r[2], outline=r[4], width=3)
    for p in g.fx:
        if len(p) < 10: cv.create_rectangle(p[0], p[1], p[0] + 4 * FS, p[1] + 4 * FS, fill=p[5], outline=''); continue
        k_ = max(.05, p[4] / p[9]); z = p[6] * FS; sh = p[7]; x_, y_ = p[0], p[1]
        if sh == 's': cv.create_rectangle(x_, y_, x_ + z * (.4 + k_), y_ + z * (.4 + k_), fill=p[5], outline='')
        elif sh in ('o', 'f'): r_ = z * (k_ if sh == 'f' else 1.8 - k_); cv.create_oval(x_ - r_, y_ - r_, x_ + r_, y_ + r_, fill=p[5], outline='')
        elif sh == 'l': cv.create_line(x_, y_, x_ - p[2] * .04, y_ - p[3] * .04, width=max(1, int(2 * FS)), fill=p[5], capstyle='round')
        elif sh == 'p': cv.create_oval(x_ - z * 1.4, y_ - z * .6, x_ + z * 1.4, y_ + z * .6, fill=p[5], outline='')
        elif sh == 't': cv.create_polygon(x_, y_ - z * 1.6 * k_ - 1, x_ - z * k_ - 1, y_ + z * k_ + 1, x_ + z * k_ + 1, y_ + z * k_ + 1, fill=p[5], outline='')
        elif sh == '*': zz = z * (.5 + k_); cv.create_polygon(x_, y_ - zz * 1.6, x_ + zz * .4, y_ - zz * .4, x_ + zz * 1.6, y_, x_ + zz * .4, y_ + zz * .4, x_, y_ + zz * 1.6, x_ - zz * .4, y_ + zz * .4, x_ - zz * 1.6, y_, x_ - zz * .4, y_ - zz * .4, fill=p[5], outline='')
    for b_ in g.bolts:
        q_ = [v for p in b_[0] for v in p]; cv.create_line(*q_, width=max(3, int(5 * FS * b_[1] / .28)), fill=b_[2], joinstyle='round'); cv.create_line(*q_, width=max(1, int(2 * FS)), fill='#ffffff', joinstyle='round')
    for q in g.tx: T(q[2], q[0], q[1], q[5], q[4], f=DISPF, w='normal')
    order_ = {id(e): i for i, e in enumerate(sorted(alive(), key=lambda e: e.x))}
    for e in g.en:
        label(e, order_.get(id(e), 0) % 2)
        if e.dead or e.dying: continue
        top = e.y - 95 * e.sc - 52 * FS
        if e.kind == 'bomber' and e.fuse > 0: T(f'{e.fuse:.1f}', e.x, top, 26, '#ff6a00' if int(e.fuse * 6) % 2 else '#ffd24a')
        elif e.mv and not e.hd and e.kind not in ('archer', 'healer') and e.mp < IMP[e.mv]: T('!', e.x, top, 28, '#ffcf33')
    if g.help:
        e = g.tg if (g.tg and not g.tg.dead and not g.tg.dying) else min(alive(), key=lambda e: abs(e.x - g.hero.x), default=None)
        if not bn_native():
            les_ = lesson_now(); camp_ = g.mode in ('camp', 'prac'); keyboard(allowed(les_['n'] if camp_ else (11 if g.mode == 'bn' else 100)), set(les_['new']) if camp_ else set(), e.w[e.i] if (e and e.i < len(e.w)) else None)
    if g.flash > 0: cv.create_rectangle(0, 0, SW, SH, fill='#ffffff' if D['theme'] == 'dark' else '#fff3c0', outline='', stipple='gray12' if g.flash < .15 else 'gray25')
    draw_hud()
    if g.ban > 0 and g.state == 'play': T('GO!' if g.mode in ('camp', 'prac', 'bn', 'daily') else (f'WAVE {g.wv}' if g.mode in ('surv', 'chal') else 'TYPE!'), SW / 2, SH * .3, 60, C('acc'))
def stars_total(): return sum(D['stars'].values())
def cleared(): return sum(1 for v in D['stars'].values() if v > 0)
def level_node(x, y, n, sz):
    bn = g.mmode == 'bn'; stars, ul, cur = mapctx()
    st = stars.get(str(n), 0); lock = n > ul; sel = n == cur; hv = hover(x, y, x + sz, y + sz)
    if not lock: BT.append((x, y, x + sz, y + sz, f'sel:{n}'))
    fill = mix(C('key'), '#000000', .35) if lock else {0: C('key'), 1: '#b07a52', 2: '#b8c2d4', 3: '#ffd24a'}[st]
    if hv and not lock: fill = mix(fill, '#ffffff', .25)
    rr(x, y, x + sz, y + sz, 8, fill, C('acc') if sel else C('edge'), 3 if sel else 1); T(str(n), x + sz / 2, y + sz * .42, 17, C('off') if lock else ('#000000' if st else C('tx')))
    if st: T('*' * st, x + sz / 2, y + sz * .78, 11, '#000000')
    if not bn and KD.lesson(n)['boss']: T('BOSS', x + sz / 2, y + sz * (.2 if st else .78), 9, '#9b2c2c' if st else C('bad'))
def menu_card(x0, y0, x1, y1, L):
    d = KD.lesson(L); cx = (x0 + x1) / 2; T(f'Level {L}: {d["title"]}', cx, y0 + 28 * FS, 18, C('acc')); T(f'Chapter {d["ch"] + 1}: {KD.CHAPTERS[d["ch"]]}', cx, y0 + 58 * FS, 13, C('dim')); T(MODEDESC[d['mode']], cx, y0 + 84 * FS, 14, C('tx'))
    T(f'3 stars: 92% accuracy and {tgt_wpm(L)} WPM', cx, y0 + 108 * FS, 12, C('dim'))
    line = ('New keys: ' + '  '.join(d['new'].upper())) if (d['new'] and L <= 10) else (f'Clear it to win: {WP[GIFT[L]]["name"]}!' if L in GIFT else f'Clear it to unlock: {STY[SGIFT[L]]["name"]}!' if L in SGIFT else f'Clear it to unlock hero {HEROES[HGIFT[L]]["name"]}!' if L in HGIFT else 'BOSS FIGHT!' if d['boss'] else '')
    if line: T(line, cx, y0 + 134 * FS, 14, C('good'))
    pg = cleared() / KD.TOTAL; rr(x0 + 40 * FS, y0 + 170 * FS, x1 - 40 * FS, y0 + 192 * FS, 7, C('pan'), C('edge'), 1)
    if pg > .01: rr(x0 + 42 * FS, y0 + 172 * FS, x0 + 42 * FS + (x1 - x0 - 84 * FS) * pg, y0 + 190 * FS, 5, C('good'), '', 0)
    T(f'Progress: {cleared()} / {KD.TOTAL} levels cleared      Stars: {stars_total()} / {KD.TOTAL * 3}', cx, y0 + 208 * FS, 12, C('dim'))
    T('SAMPLE TEXT', cx, y0 + 244 * FS, 11, C('dim'))
    for i, sm in enumerate(KD.samples(L, 3)): T(sm if len(sm) < 70 else sm[:67] + '...', cx, y0 + (272 + i * 28) * FS, 13, C('cy'), f=MONOF)
    T('Press Enter to open the level map', cx, y1 - 24 * FS, 13, C('good'))
def menu_text(i):
    nm = MENU[i]; td = datetime.date.today(); done = str(td) in D['daily']; dl = KD.DAILY[td.weekday()]
    return {'Typing Tutor': f'TYPING TUTOR\nLearn touch typing step by step -\nkey by key, with a finger guide.\nNo enemies, no pressure.\nLessons done: {sum(1 for v in D["tutor_stars"].values() if v > 0)} / {KD.TOTAL}',
            'Daily Challenge': f'DAILY CHALLENGE\n{dl["name"]}\n{dl["desc"]}\n\nToday: ' + (f'DONE  (score {D["daily"][str(td)]})' if done else 'not done yet - bonus coins!') + f'\nDaily streak: {D["streak"]} days',
            'Challenge Mode': f'CHALLENGE MODE\nNon-stop waves that remix everything\nyou have learned. Speed rises every\nwave, with modifiers and bosses.\nBest: wave {D["chal"]}', 'Bangla Typing': f'BANGLA TYPING\nType Bangla words with English\nletters (phonetic) - or with a real\nBangla keyboard.\nLevels cleared: {sum(1 for v in D["bn_stars"].values() if v > 0)} / {KD.BN_LEVELS}',
            'Survival': 'SURVIVAL\nEndless waves, a boss every 5th.\nContent grows from words to sentences.\nBest score: ' + str(D['surv']), 'Boss Rush': f'BOSS RUSH\nFight all 8 bosses back to back.\nHealth refills a little between bosses.\nBest: {D["rush"]} / 8 bosses',
            'Weak-Key Trainer': 'WEAK-KEY TRAINER\nWords built from the keys YOU miss most.\nNo damage - pure training.\nThe fastest way to fix your weak spots.', 'Custom Text': 'CUSTOM TEXT\nPractice your own lines (notes, code,\nanything). Edit custom.txt in the\nTypeStrike data folder: ' + DATA,
            'Speed Test  60s': 'SPEED TEST\n60 seconds, no damage.\nPure WPM.\nBest: ' + str(D['test']) + ' WPM', 'Heroes': f'HEROES\nChoose your fighter: {HEROES[D["hero"]]["name"]}\n{HEROES[D["hero"]]["perk"]}\n{len(D["own_heroes"])} / {len(HEROES)} unlocked',
            'Armory': 'ARMORY\nBuy weapons and learn new\nfighting styles - each has its own\nmoves and effects.\nCoins: ' + str(D['coins']), 'Achievements': f'ACHIEVEMENTS\n{len(D["ach"])} / {len(ACH)} unlocked\nEvery one gives bonus coins.', 'Stats': 'STATS\nKey accuracy heatmap, WPM history\nand your totals.', 'Quit': 'QUIT\nSee you soon, warrior!'}.get(nm, nm)
def draw_menu():
    pw, ph = min(SW - 30, 1020 * FS), min(SH - 24, 720 * FS); x0, y0 = (SW - pw) / 2, max(12, (SH - ph) / 2); panel(x0, y0, x0 + pw, y0 + ph)
    T('TYPESTRIKE', SW / 2 + 3 * FS, y0 + 49 * FS, 44, mix(C('pan'), '#000000', .5)); T('TYPESTRIKE', SW / 2, y0 + 46 * FS, 44, C('acc'))
    T('Typing Tutor  -  150 lessons, 8 heroes, 19 weapons, 11 fighting styles', SW / 2, y0 + 88 * FS, 15, C('dim')); T('v1.2.0', x0 + pw - 24 * FS, y0 + 22 * FS, 11, C('dim'), 'r')
    n = len(MENU); top = 116 * FS; rh = min(54 * FS, (ph - top - 96 * FS) / n); done_today = str(datetime.date.today()) in D['daily']
    for i, nm in enumerate(MENU):
        y = y0 + top + i * rh; xa, xb = x0 + 30 * FS, x0 + 410 * FS; bh = rh - 5 * FS; hv = hover(xa, y, xb, y + bh)
        if g.mmoved and hv: g.mi = i
        sel = i == g.mi; row_button(xa, y, xb, y + bh, sel, f'm:{i}'); T(nm, xa + 20 * FS, y + bh / 2, 17, C('seltx') if sel else C('tx'), 'l')
        if nm in LVROWS:
            for k_, (lb, dl) in enumerate((('<', -1), ('>', 1))): button(xb - 112 * FS + k_ * 80 * FS, y + 3 * FS, xb - 112 * FS + k_ * 80 * FS + 32 * FS, y + bh - 3 * FS, lb, f'lv:{i}:{dl}', 'n', 14)
            T(str(g.sel), xb - 112 * FS + 56 * FS, y + bh / 2, 15, C('seltx') if sel else C('acc'))
        elif nm == 'Daily Challenge' and not done_today: T('NEW!', xb - 20 * FS, y + bh / 2, 13, C('seltx') if sel else C('bad'), 'r')
    cx0 = x0 + 440 * FS; cx1 = x0 + pw - 28 * FS; cy0 = y0 + top; cy1 = y0 + top + n * rh - 5 * FS; rr(cx0, cy0, cx1, cy1, 12, C('key'), C('edge'), 1)
    if MENU[g.mi] in LVROWS: menu_card(cx0, cy0, cx1, cy1, g.sel)
    else: T(menu_text(g.mi), (cx0 + cx1) / 2, (cy0 + cy1) / 2, 16, C('tx'))
    T(rankline() + f'      Daily streak: {D["streak"]}', SW / 2 - 60 * FS, y0 + ph - 66 * FS, 15, C('good')); coin_icon(x0 + pw - 250 * FS, y0 + ph - 66 * FS, 8); T(f'{D["coins"]} coins   {gear_name()}', x0 + pw - 234 * FS, y0 + ph - 66 * FS, 14, C('acc'), 'l')
    chips = [(f'Theme: {D["theme"]}', 'k:F2'), (f'Sound: {VOLN[D["vol"]]}', 'k:F3'), (f'Difficulty: {["Easy", "Normal", "Hard"][D["diff"] - 1]}', 'k:F4'), (f'Enemy speed: {SPD():g}x {spd_label()}', 'k:F5')] + ([('Fullscreen', 'k:F11')] if not OVERLAY else [])
    cwid = (pw - 60 * FS - (len(chips) - 1) * 10 * FS) / len(chips)
    for i, (lb, a) in enumerate(chips): button(x0 + 30 * FS + i * (cwid + 10 * FS), y0 + ph - 46 * FS, x0 + 30 * FS + i * (cwid + 10 * FS) + cwid, y0 + ph - 14 * FS, lb, a, 'n', 12)
    if g.err: T(g.err, SW / 2, y0 + ph + 14 * FS, 12, C('bad'))
def draw_map():
    mm = g.mmode; bn = mm == 'bn'; pw, ph = min(SW - 30, 1100 * FS), min(SH - 24, 720 * FS); x0, y0 = (SW - pw) / 2, max(12, (SH - ph) / 2); panel(x0, y0, x0 + pw, y0 + ph)
    T({'camp': 'CAMPAIGN  -  150 LESSONS', 'prac': 'FREE PRACTICE  (no damage, no coins)', 'bn': 'BANGLA TYPING', 'tutor': 'TYPING TUTOR  -  learn every key step by step'}[mm], x0 + 30 * FS, y0 + 38 * FS, 26, C('acc'), 'l')
    L = mapctx()[2]; gx0 = x0 + 30 * FS
    if not bn:
        rh_ = (ph - 150 * FS) / 15
        for i, name in enumerate(KD.CHAPTERS):
            y = y0 + 70 * FS + i * rh_; sel = i == g.mch; row_button(x0 + 24 * FS, y, x0 + 300 * FS, y + rh_ - 3 * FS, sel, f'ch:{i}'); n_ok = sum(1 for k in range(i * 10 + 1, i * 10 + 11) if mapctx()[0].get(str(k), 0) > 0)
            T(f'{i + 1}. {name}', x0 + 36 * FS, y + (rh_ - 3 * FS) / 2, 12, C('seltx') if sel else (C('dim') if i * 10 + 1 > mapctx()[1] else C('tx')), 'l'); T(f'{n_ok}/10', x0 + 290 * FS, y + (rh_ - 3 * FS) / 2, 11, C('seltx') if sel else C('good'), 'r')
        gx0 = x0 + 330 * FS; cols = 5; ids = [g.mch * 10 + 1 + k for k in range(10)]; T(f'Chapter {g.mch + 1}: {KD.CHAPTERS[g.mch]}', gx0, y0 + 74 * FS, 18, C('tx'), 'l')
    else: cols = 4; ids = list(range(1, KD.BN_LEVELS + 1)); T('Type the Bangla word using English letters (phonetic).', gx0, y0 + 74 * FS, 14, C('tx'), 'l')
    gap_ = 10 * FS; sz = min(78 * FS, (x0 + pw - 30 * FS - gx0 - (cols - 1) * gap_) / cols); gy0 = y0 + 100 * FS
    for k, n in enumerate(ids): level_node(gx0 + (k % cols) * (sz + gap_), gy0 + (k // cols) * (sz + gap_), n, sz)
    dy = gy0 + ((len(ids) + cols - 1) // cols) * (sz + gap_) + 14 * FS; cw = int((x0 + pw - 30 * FS - gx0) / (7.2 * FS))
    if bn:
        T(f'Level {L}: {KD.bn_title(L)}', gx0, dy, 19, C('acc'), 'l'); lines = textwrap.wrap(BNL(L)['text'], cw)[:3]
        for i, ln_ in enumerate(lines): T(ln_, gx0, dy + (30 + i * 20) * FS, 13, C('tx'), 'l')
        bx = KD.BN[KD.bn_tier(L)][:3]
        for i, (b, p) in enumerate(bx): T(f'{bnt(b)}   =   {p}', gx0 + (i * 190) * FS, dy + 100 * FS, 18, C('cy'), 'l', f=BNF)
        button(gx0, dy + 130 * FS, gx0 + 440 * FS, dy + 170 * FS, 'Input: Native Bangla keyboard (switch Windows layout)' if D['bn_native'] else 'Input: Phonetic (English letters)  -  click to change', 'bntog:', 'n', 13)
        if not BN_FONT_OK: T('No Bengali font found: Bangla letters may show as boxes. Linux: install fonts-noto (or fonts-beng). If letters look jumbled, toggle the display fix.', gx0, dy + 214 * FS, 12, C('bad'), 'l')
        button(gx0 + 460 * FS, dy + 130 * FS, gx0 + 800 * FS, dy + 170 * FS, 'Bangla display fix: ' + (('AUTO (' + ('ON' if bn_fix_on() else 'OFF') + ')') if D['bn_fix'] in (None, 'auto') else ('ON' if D['bn_fix'] else 'OFF')), 'bnfix:', 'n', 13)
        T('Tab = toggle input mode.   Native mode: press Win+Space and pick the Bangla keyboard first.', gx0, dy + 190 * FS, 11, C('dim'), 'l')
    else:
        d = KD.lesson(L); T(f'Level {L}: {d["title"]}', gx0, dy, 19, C('acc'), 'l'); T(f'{MODEDESC[d["mode"]]}      3 stars: 92% accuracy + {tgt_wpm(L)} WPM' + ('      BOSS FIGHT' if d['boss'] else ''), gx0, dy + 28 * FS, 12, C('dim'), 'l')
        for i, ln_ in enumerate(textwrap.wrap(d['text'], cw)[:3]): T(ln_, gx0, dy + (56 + i * 20) * FS, 13, C('tx'), 'l')
        T('Sample: ' + KD.samples(L, 1)[0][:60], gx0, dy + 128 * FS, 13, C('cy'), 'l', f=MONOF)
        if mm == 'tutor': T('5 exercise lines.  Pass with 90% accuracy to unlock the next lesson.  A wrong key does not move on - find the right one.', gx0, dy + 152 * FS, 12, C('good'), 'l')
        if D['fails'].get(str(L), 0) >= 2 and mm == 'camp': T('Assist mode is on for this level (slower enemies, softer hits).', gx0, dy + 152 * FS, 12, C('good'), 'l')
    button(x0 + 30 * FS, y0 + ph - 62 * FS, x0 + 200 * FS, y0 + ph - 18 * FS, 'Back  (Esc)', 'k:Escape', 'n', 15); button(x0 + pw - 330 * FS, y0 + ph - 62 * FS, x0 + pw - 30 * FS, y0 + ph - 18 * FS, 'START  (Enter)', 'k:Return', 'p', 18)
    T('Arrows: choose level     PageUp / PageDown: chapter', x0 + pw / 2 - 20 * FS, y0 + ph - 40 * FS, 12, C('dim'))
HAND_H = {0: 58, 1: 78, 2: 88, 3: 78, 4: 78, 5: 88, 6: 78, 7: 58}
def hands(ytop, hs, tf):
    """two hands, the finger that must press the next key lights up"""
    gap = 170 * hs; hw = 34 * hs; step = hw * 1.15; base = ytop + 96 * hs; cx = SW / 2
    for side in (0, 1):
        x_a = cx - gap / 2 - 4 * step if side == 0 else cx + gap / 2; rr(x_a - 4 * hs, base - 6 * hs, x_a + 4 * step + 2 * hs, base + 44 * hs, 16 * hs, C('key'), C('edge'), 1)
    for i in range(8):
        k = i if i < 4 else i - 4; xx = cx - gap / 2 - (4 - k) * step if i < 4 else cx + gap / 2 + k * step; h_ = HAND_H[i] * hs; on = i == tf
        rr(xx, base - h_, xx + hw, base + 2 * hs, 12 * hs, fc(i) if on else mix(C('key'), fc(i), .3), '#ffffff' if on else C('edge'), 3 if on else 1)
    for sg in (-1, 1): cv.create_oval(cx + sg * 46 * hs - 28 * hs, base + 26 * hs, cx + sg * 46 * hs + 28 * hs, base + 58 * hs, fill=fc(8) if tf == 8 else mix(C('key'), fc(8), .3), outline='#ffffff' if tf == 8 else C('edge'), width=3 if tf == 8 else 1)
def tfont(n, avail):
    sz = max(12, int(34 * FS))
    while True:
        f = FCACHE.get(('t', sz)) or FCACHE.setdefault(('t', sz), tkf.Font(root, family=MONOF, size=-sz, weight='bold')); cw = f.measure('M')
        if cw * max(1, n) <= avail or sz <= 11: return f, cw, sz
        sz -= 2
def tutor_line(L):
    les = KD.lesson(L)
    if les['mode'] in ('sent', 'para', 'code', 'office') or les['hi'] > 30: return KD.gen(L, WR)[:90]
    parts = []
    while len(' '.join(parts)) < 34 and len(parts) < 9: parts.append(KD.gen(L, WR, (), 'grunt'))
    return ' '.join(parts)
def begin_tutor(L):
    WR.seed(); les = KD.lesson(L); n = 4 if (les['mode'] in ('para',) or les['hi'] > 60) else 5
    g.tu = NS(L=L, les=les, lines=[tutor_line(L) for _ in range(n)], li=0, ci=0, ok=0, err=0, t0=None, t1=None, flash=0, res=None, bad={}); g.state = 'tintro'; g.hero = None if False else g.hero; activate()
def tutor_stats(tu):
    now = time.perf_counter(); el = ((tu.t1 or now) - tu.t0) if tu.t0 else 0; wpm = int((tu.ok / 5) / (el / 60)) if el > 2 else 0; acc = int(100 * tu.ok / max(1, tu.ok + tu.err)); return el, wpm, acc
def tutor_key(c):
    tu = g.tu; exp = tu.lines[tu.li][tu.ci]
    if tu.t0 is None: tu.t0 = time.perf_counter()
    att[exp] = att.get(exp, 0) + 1
    if c == exp:
        tu.ok += 1; tu.ci += 1; D['keys'] += 1; snd('tick%d' % (tu.ok % 8))
        if tu.ci >= len(tu.lines[tu.li]):
            tu.li += 1; tu.ci = 0; snd('select')
            if tu.li >= len(tu.lines): tutor_finish()
    else:
        tu.err += 1; tu.flash = time.perf_counter() + .3; miss[exp] = miss.get(exp, 0) + 1; tu.bad[exp] = tu.bad.get(exp, 0) + 1; snd('wrong')
def tutor_finish():
    tu = g.tu; tu.t1 = time.perf_counter(); el, wpm, acc = tutor_stats(tu); L = tu.L; passed = acc >= 90
    stars = (1 + (acc >= 95) + (acc >= 98 and wpm >= max(5, int(tgt_wpm(L) * .7)))) if passed else 0; first = str(L) not in D['tutor_stars']
    if passed:
        D['tutor_stars'][str(L)] = max(D['tutor_stars'].get(str(L), 0), stars); D['tutor_ul'] = max(D['tutor_ul'], min(KD.TOTAL, L + 1))
        if first: D['coins'] += 10 + stars * 10; D['st']['earned'] += 10 + stars * 10
    tu.res = dict(el=el, wpm=wpm, acc=acc, stars=stars, passed=passed, first=first); D['best_wpm'] = max(D['best_wpm'], wpm) if tu.ok > 30 else D['best_wpm']; D['sessions'] += 1; bump_streak(); ach_check(); g.state = 'tdone'; save(); snd('win' if passed else 'lose')
def draw_tintro():
    tu = g.tu; les = tu.les; L = tu.L; nk = les['new']; pw, ph = min(SW - 30, 900 * FS), min(SH - 30 * FS - 5 * (KS + 4) - 150 * FS, 470 * FS); x0, y0 = (SW - pw) / 2, 18 * FS; panel(x0, y0, x0 + pw, y0 + ph)
    T(f'Lesson {L}: {les["title"]}', SW / 2, y0 + 36 * FS, 26, C('acc')); T(f'Chapter {les["ch"] + 1}: {KD.CHAPTERS[les["ch"]]}   -   {MODEDESC[les["mode"]]}', SW / 2, y0 + 66 * FS, 13, C('dim')); y = y0 + 96 * FS
    if nk:
        T('NEW KEYS', SW / 2, y, 12, C('dim')); y += 22 * FS
        for i, c in enumerate(nk[:10]):
            if len(nk) < 5: T(f'{disp(c).upper()}  =  {FN[fgi(c)]}' + ('  (+ Shift)' if bk(c)[1] else ''), SW / 2, y + i * 22 * FS, 15, fc(fgi(c)))
            else: T(f'{disp(c).upper()}: {FN[fgi(c)]}', x0 + (pw / 2 - 200 * FS if i % 2 == 0 else pw / 2 + 20 * FS), y + (i // 2) * 22 * FS, 14, fc(fgi(c)), 'l')
        y += (len(nk) * 22 if len(nk) < 5 else ((min(len(nk), 10) + 1) // 2) * 22) * FS + 6 * FS
    cw = int((pw - 80 * FS) / (7.4 * FS)); T('LESSON', SW / 2, y, 12, C('dim')); y += 22 * FS
    for ln_ in textwrap.wrap(les['text'], cw)[:4]: T(ln_, SW / 2, y, 14, C('tx')); y += 21 * FS
    T('Sit straight, keep your wrists floating, look at the screen - not at your fingers.', SW / 2, y + 12 * FS, 13, C('good')); T('EXERCISE PREVIEW', SW / 2, y + 48 * FS, 11, C('dim'))
    for i_, sm in enumerate(tu.lines[:2]): T(sm if len(sm) < 80 else sm[:77] + '...', SW / 2, y + (72 + i_ * 24) * FS, 13, C('cy'), f=MONOF)
    T(f'{len(tu.lines)} exercise lines.  Pass with 90% accuracy.  A wrong key does not move on.', SW / 2, y0 + ph - 78 * FS, 13, C('cy'))
    button(x0 + 30 * FS, y0 + ph - 54 * FS, x0 + 200 * FS, y0 + ph - 10 * FS, 'Back', 'k:Escape', 'n', 15); button(x0 + pw - 330 * FS, y0 + ph - 54 * FS, x0 + pw - 30 * FS, y0 + ph - 10 * FS, 'START  (Enter)', 'k:Return', 'p', 17)
    keyboard(allowed(L), set(nk), None); hs = max(.5, min(1.0, (KBY - (y0 + ph) - 20 * FS) / 120)) if KBY - (y0 + ph) > 70 else 0
    if hs: hands(y0 + ph + 6 * FS, hs, fgi(nk[0]) if nk else -1)
def draw_tutor():
    tu = g.tu; now = time.perf_counter(); pw = min(SW - 30, 1200 * FS); x0 = (SW - pw) / 2; y0 = 12 * FS; el, wpm, acc = tutor_stats(tu)
    T(f'Lesson {tu.L}: {tu.les["title"]}', SW / 2, y0 + 20 * FS, 20, C('acc')); cw_ = pw / 5
    for i, (lb, val, col) in enumerate((('WPM', str(wpm), C('tx')), ('ACCURACY', f'{acc}%', C('good') if acc >= 90 else C('bad')), ('ERRORS', str(tu.err), C('tx')), ('TIME', f'{int(el) // 60}:{int(el) % 60:02d}', C('tx')), ('LINE', f'{min(tu.li + 1, len(tu.lines))} / {len(tu.lines)}', C('tx')))):
        rr(x0 + i * cw_ + 4 * FS, y0 + 40 * FS, x0 + (i + 1) * cw_ - 4 * FS, y0 + 92 * FS, 9, C('pan'), C('edge'), 1); T(lb, x0 + i * cw_ + cw_ / 2, y0 + 54 * FS, 10, C('dim')); T(val, x0 + i * cw_ + cw_ / 2, y0 + 76 * FS, 20, col)
    py0 = y0 + 104 * FS; ph_ = 170 * FS; rr(x0, py0, x0 + pw, py0 + ph_, 12, C('pan'), C('edge'), 2)
    line = tu.lines[tu.li]; f_, cw, sz = tfont(len(line), pw - 70 * FS); lh = sz * 1.5; ty = py0 + 56 * FS; bad = now < tu.flash; m_ = lambda t: f_.measure(t) if t else 0
    tx = SW / 2 - m_(line) / 2; xa = tx + m_(line[:tu.ci]); xb = tx + m_(line[:tu.ci + 1])
    rr(xa - 3, ty - lh / 2, xb + 3, ty + lh / 2, 5, '#ff5a5a' if bad else C('acc'), '', 0)
    if tu.ci: cv.create_text(tx, ty, text=line[:tu.ci], anchor='w', fill=C('good'), font=f_)
    cv.create_text(xa, ty, text=line[tu.ci] if line[tu.ci] != ' ' else '_', anchor='w', fill='#101010', font=f_)
    if tu.ci + 1 < len(line): cv.create_text(xb, ty, text=line[tu.ci + 1:], anchor='w', fill=C('tx'), font=f_)
    if tu.li + 1 < len(tu.lines):
        nl = tu.lines[tu.li + 1]; f2, cw2, _z = tfont(len(nl) * 1.7, pw - 70 * FS); cv.create_text(SW / 2, py0 + 128 * FS, text=nl, fill=C('dim'), font=f2)
    rr(x0 + 20 * FS, py0 + ph_ - 20 * FS, x0 + pw - 20 * FS, py0 + ph_ - 10 * FS, 4, C('key'), '', 0); fr = (tu.li + tu.ci / max(1, len(line))) / len(tu.lines)
    if fr > .005: rr(x0 + 20 * FS, py0 + ph_ - 20 * FS, x0 + 20 * FS + (pw - 40 * FS) * fr, py0 + ph_ - 10 * FS, 4, C('good'), '', 0)
    exp = line[tu.ci]; keyboard(allowed(tu.L), set(tu.les['new']), exp); ytop = py0 + ph_ + 10 * FS
    if KBY - ytop > 70: hands(ytop, max(.5, min(1.0, (KBY - ytop - 24 * FS) / 120)), fgi(exp))
    T('Esc = back to the lesson list', SW / 2, SH - 12 * FS, 12, C('dim'))
def draw_tdone():
    tu = g.tu; r = tu.res; pw, ph = min(SW - 30, 760 * FS), 470 * FS; x0, y0 = (SW - pw) / 2, 40 * FS; panel(x0, y0, x0 + pw, y0 + ph)
    T('LESSON COMPLETE!' if r['passed'] else 'ALMOST - TRY AGAIN', SW / 2, y0 + 52 * FS, 34, C('good') if r['passed'] else C('bad'))
    if r['passed']: T('*' * r['stars'] + '-' * (3 - r['stars']), SW / 2, y0 + 106 * FS, 40, C('acc'))
    else: T('You need 90% accuracy. Slow down a little - accuracy first, speed comes later.', SW / 2, y0 + 106 * FS, 14, C('tx'))
    T(f'WPM {r["wpm"]}     Accuracy {r["acc"]}%     Errors {tu.err}     Time {int(r["el"]) // 60}:{int(r["el"]) % 60:02d}', SW / 2, y0 + 170 * FS, 20)
    wk = sorted(tu.bad.items(), key=lambda kv: -kv[1])[:5]; T('Keys to practise: ' + ('  '.join(disp(k) for k, _ in wk) if wk else 'none - perfect!'), SW / 2, y0 + 220 * FS, 17, C('acc'))
    if r['passed'] and r['first']: T(f'+{10 + r["stars"] * 10} coins', SW / 2, y0 + 256 * FS, 16, C('acc'))
    if r['passed'] and tu.L % 10 == 0: T(f'CHAPTER DONE: {KD.CHAPTERS[(tu.L - 1) // 10]}!', SW / 2, y0 + 290 * FS, 16, C('cy'))
    T('TIP: ' + TIPS[(tu.L + 2) % len(TIPS)], SW / 2, y0 + 340 * FS, 13, C('tx'))
    nxt = r['passed'] and tu.L < KD.TOTAL
    button(x0 + 30 * FS, y0 + ph - 78 * FS, x0 + 230 * FS, y0 + ph - 24 * FS, 'Lesson list', 'k:Escape', 'n', 16); button(x0 + 250 * FS, y0 + ph - 78 * FS, x0 + 400 * FS, y0 + ph - 24 * FS, 'Retry', 'k:r', 'n', 16)
    button(x0 + pw - 340 * FS, y0 + ph - 78 * FS, x0 + pw - 30 * FS, y0 + ph - 24 * FS, 'Next lesson  (Enter)' if nxt else 'Retry  (Enter)', 'k:Return', 'p', 17)
def draw_armory():
    if g.pv is None: pv_setup()
    pw, ph = min(SW - 30, 1120 * FS), min(SH - 24, 700 * FS); x0, y0 = (SW - pw) / 2, max(12, (SH - ph) / 2); panel(x0, y0, x0 + pw, y0 + ph)
    T('ARMORY', x0 + 30 * FS, y0 + 38 * FS, 30, C('acc'), 'l'); coin_icon(x0 + pw - 150 * FS, y0 + 38 * FS, 10); T(str(D['coins']), x0 + pw - 130 * FS, y0 + 38 * FS, 22, C('acc'), 'l')
    for i, n in enumerate(['Weapons', 'Fighting Styles', 'Heroes']): button(x0 + 30 * FS + i * 190 * FS, y0 + 66 * FS, x0 + 210 * FS + i * 190 * FS, y0 + 106 * FS, n, f'tab:{i}', 'p' if i == g.tab else 'n', 15)
    its = items(); lh = 47 * FS; vis = max(5, int((ph - 230 * FS) / lh)); off = max(0, min(len(its) - vis, g.si - vis // 2)) if len(its) > vis else 0
    def nm_(k): return (WP[k]['name'] if g.tab == 0 else STY[k]['name'] if g.tab == 1 else HEROES[k]['name'])
    def pr_(k): return (WP[k]['price'] if g.tab == 0 else STY[k]['price'] if g.tab == 1 else HEROES[k]['price'])
    def own_(k): return (k in D['owned']) if g.tab == 0 else (k in D['own_styles']) if g.tab == 1 else (k in D['own_heroes'])
    def eq_(k): return (k == wkey()) if g.tab == 0 else (k == skey()) if g.tab == 1 else (k == D['hero'])
    for j, k in enumerate(its[off:off + vis]):
        i = off + j; y = y0 + 122 * FS + j * lh; sel = i == g.si; own = own_(k); eq = eq_(k)
        row_button(x0 + 26 * FS, y, x0 + 410 * FS, y + lh - 5 * FS, sel, f'item:{i}'); T(nm_(k), x0 + 44 * FS, y + (lh - 5 * FS) / 2, 17, C('seltx') if sel else C('tx'), 'l')
        T('EQUIPPED' if eq else 'OWNED' if own else f'{pr_(k)}', x0 + 392 * FS, y + (lh - 5 * FS) / 2, 14, C('seltx') if sel else (C('good') if own else C('acc')), 'r')
    if len(its) > vis: T(f'{g.si + 1} / {len(its)}   (Up / Down to scroll)', x0 + 218 * FS, y0 + 122 * FS + vis * lh + 4 * FS, 11, C('dim'))
    k = its[min(g.si, len(its) - 1)]; px0, px1 = x0 + 440 * FS, x0 + pw - 28 * FS; py0, py1 = y0 + 118 * FS, y0 + ph - 205 * FS; rr(px0, py0, px1, py1, 12, C('key'), C('edge'), 1)
    pgy = py1 - 36 * FS; cv.create_line(px0 + 16 * FS, pgy + 4, px1 - 16 * FS, pgy + 4, fill=C('gnd'), width=max(2, int(3 * FS)))
    pv, dm = g.pv, g.pvd; pv._gy = dm._gy = pgy; pv.x = px0 + (px1 - px0) * .36; pv.y = pgy; pv.face = 1; dm.x = px0 + (px1 - px0) * .66; dm.y = pgy; dm.face = -1; dm.draw(); pv.draw()
    ds = WP[k]['desc'] if g.tab == 0 else STY[k]['desc'] if g.tab == 1 else HEROES[k]['perk']; cx = (px0 + px1) / 2
    T(nm_(k), cx, y0 + ph - 172 * FS, 24, C('acc')); T(ds, cx, y0 + ph - 142 * FS, 14, C('tx'))
    if g.tab == 0 and k != 'fists': T(f'Reach {WP[k]["reach"]}    Speed {int(.3 / WP[k]["dur"] * 10)}    Power {int(WP[k]["power"] * 10)}    {"Two-handed" if WP[k]["two"] else "Dual blades" if WP[k]["dual"] else "One-handed"}    Effect: {FXP[k][0]}', cx, y0 + ph - 114 * FS, 13, C('dim'))
    elif g.tab == 1: T(f'Speed {int(.3 / STY[k]["dur"] * 10)}    Power {int(STY[k]["power"] * 10)}    Effect: {FXP[k][0]}', cx, y0 + ph - 114 * FS, 13, C('dim'))
    elif g.tab == 2: T(f'Power x{HEROES[k]["pw"]:.2f}    Speed x{HEROES[k]["sp"]:.2f}    Damage taken x{HEROES[k]["ar"]:.2f}    Jump x{HEROES[k]["jv"]:.2f}    Coins x{HEROES[k]["lk"]:.2f}', cx, y0 + ph - 114 * FS, 12, C('dim'))
    own = own_(k); eq = eq_(k); pr = pr_(k)
    button(px1 - 260 * FS, y0 + ph - 82 * FS, px1, y0 + ph - 28 * FS, 'Equipped' if eq else ('Equip' if own else f'Buy  ({pr} coins)'), None if eq else 'k:Return', 'd' if eq else ('p' if (own or D['coins'] >= pr) else 'n'), 17)
    button(px0, y0 + ph - 82 * FS, px0 + 150 * FS, y0 + ph - 28 * FS, 'Back', 'k:Escape', 'n', 16)
    if g.toast[1] > 0: T(g.toast[0], cx, y0 + ph - 54 * FS, 16, C('good'))
def draw_intro():
    del BT[:]; les = lesson_now(); camp = g.mode in ('camp', 'prac'); L = les['n'] if camp else (11 if g.mode == 'bn' else 100); nk = les['new'] if camp else ''
    pw, ph = min(SW - 30, 900 * FS), min(SH - 60 * FS - 5 * (KS + 4) - 20, 520 * FS); x0, y0 = (SW - pw) / 2, 30 * FS; panel(x0, y0, x0 + pw, y0 + ph)
    ttl = f'Level {g.lv}: {les["title"]}' if camp else (les['name'] if g.mode == 'daily' else les['title'] if g.mode == 'bn' else les['title']); T(ttl, SW / 2, y0 + 38 * FS, 28, C('acc'))
    T((f'Chapter {les["ch"] + 1}: {KD.CHAPTERS[les["ch"]]}   -   ' if camp else '') + MODEDESC[les['mode']] + ('   (practice: no damage, no coins)' if g.mode == 'prac' else ''), SW / 2, y0 + 72 * FS, 13, C('dim'))
    y = y0 + 102 * FS
    if nk:
        T('NEW KEYS', SW / 2, y, 12, C('dim')); y += 22 * FS
        for i, c in enumerate(nk[:10]):
            if len(nk) < 5: T(f'{disp(c).upper()}  =  {FN[fgi(c)]}' + ('  (+ Shift)' if bk(c)[1] else ''), SW / 2, y + i * 24 * FS, 15, fc(fgi(c)))
            else: T(f'{disp(c).upper()}: {FN[fgi(c)]}', x0 + (pw / 2 - 200 * FS if i % 2 == 0 else pw / 2 + 20 * FS), y + (i // 2) * 24 * FS, 14, fc(fgi(c)), 'l')
        y += (len(nk) * 24 if len(nk) < 5 else ((min(len(nk), 10) + 1) // 2) * 24) * FS + 8 * FS
    cw = int((pw - 80 * FS) / (7.4 * FS)); T('LESSON', SW / 2, y, 12, C('dim')); y += 22 * FS
    for ln_ in textwrap.wrap(les['text'], cw)[:4]: T(ln_, SW / 2, y, 14, C('tx')); y += 21 * FS
    y += 8 * FS
    if camp:
        T('WARM-UP SAMPLES', SW / 2, y, 12, C('dim')); y += 22 * FS
        for sm in KD.samples(L if g.mode != 'x' else g.lv, 3)[:2]: T(sm if len(sm) < 78 else sm[:75] + '...', SW / 2, y, 13, C('cy'), f=MONOF); y += 22 * FS
    elif g.mode == 'bn':
        for b, p in KD.BN[KD.bn_tier(g.lv)][:3]: T(f'{bnt(b)}   =   {p}', SW / 2, y, 18, C('cy'), f=BNF); y += 28 * FS
        T('Input: ' + ('NATIVE Bangla keyboard' if D['bn_native'] else 'PHONETIC (English letters)'), SW / 2, y + 4 * FS, 12, C('good'))
    elif g.mode == 'weak':
        a_, m_ = att, miss; wk = sorted((k for k in a_ if k.isalpha() and a_[k] >= 3 and m_.get(k, 0) > 0), key=lambda k: -m_[k] / a_[k])[:5]; T('Your weakest keys: ' + ('  '.join(k.upper() for k in wk) if wk else 'not enough data yet - the trainer starts with common letters'), SW / 2, y, 14, C('cy'))
    elif g.mode == 'custom': T('File: ' + os.path.join(DATA, 'custom.txt'), SW / 2, y, 12, C('cy')); T(f'{len(g.cust)} lines loaded.', SW / 2, y + 22 * FS, 13, C('good'))
    elif g.mode == 'daily':
        td = str(datetime.date.today()); T('Same challenge for everyone today.  Streak: %d days.' % D['streak'], SW / 2, y, 13, C('cy')); y += 22 * FS; T('Reward: %s' % ('already collected today (practice run)' if td in D['daily'] else '100 bonus coins + streak bonus'), SW / 2, y, 13, C('good'))
    T('TIP: ' + TIPS[g.tip % len(TIPS)], SW / 2, y0 + ph - 118 * FS, 13, C('tx')); T(f'Enemies get faster with every level - speed at this level: x{level_speed(g.cl) / level_speed(1) * SPD():.1f}', SW / 2, y0 + ph - 96 * FS, 13, C('cy')); T(f'YOUR SPEED SETTING: {SPD():g}x  {spd_label()}   (Left / Right keys)', SW / 2, y0 + ph - 72 * FS, 14, C('acc'))
    button(SW / 2 - 300 * FS, y0 + ph - 86 * FS, SW / 2 - 262 * FS, y0 + ph - 58 * FS, '-', 'spd:-1', 'n', 16); button(SW / 2 + 262 * FS, y0 + ph - 86 * FS, SW / 2 + 300 * FS, y0 + ph - 58 * FS, '+', 'spd:1', 'n', 16)
    goal = f'GOAL: 80% accuracy to pass.   3 stars: 92% accuracy and {tgt_wpm(g.cl)} WPM.' if g.mode in ('camp', 'bn') else 'GOAL: finish with at least 75% accuracy.' if g.mode == 'daily' else 'Practice as long as you like.'
    if les.get('strict'): goal += '   ACCURACY LEVEL: mistakes cost HP!'
    T(goal, SW / 2, y0 + ph - 76 * FS, 13, C('good'))
    if g.assist > 1: T('ASSIST MODE ON: slower enemies and softer hits (you failed this level before).', SW / 2, y0 + ph - 54 * FS, 12, C('cy'))
    button(x0 + 30 * FS, y0 + ph - 48 * FS, x0 + 200 * FS, y0 + ph - 8 * FS, 'Back', 'k:Escape', 'n', 15); button(x0 + pw - 330 * FS, y0 + ph - 48 * FS, x0 + pw - 30 * FS, y0 + ph - 8 * FS, 'START  (Enter)', 'k:Return', 'p', 17)
    if not bn_native(): keyboard(allowed(L), set(nk), None)
def draw_end():
    del BT[:]; pw, ph = min(SW - 30, 820 * FS), 540 * FS; x0, y0 = (SW - pw) / 2, 40 * FS; panel(x0, y0, x0 + pw, y0 + ph); good = g.state == 'done'
    T(g.title, SW / 2, y0 + 48 * FS, 34 if len(g.title) < 28 else 26, C('good') if good else C('bad'))
    if g.mode in ('camp', 'bn', 'daily') and good: T('*' * g.stars + '-' * (3 - g.stars), SW / 2, y0 + 98 * FS, 40, C('acc'))
    T(f'WPM {wpm()}     Accuracy {acc()}%     Score {g.score}', SW / 2, y0 + 150 * FS, 24); T(f'Kills {g.kills}     Max combo {g.mc}     Rank: {rank(wpm())}', SW / 2, y0 + 188 * FS, 16, C('dim'))
    coin_icon(SW / 2 - 78 * FS, y0 + 224 * FS, 9); T(f'+{g.earned} coins   (total {D["coins"]})', SW / 2 - 60 * FS, y0 + 224 * FS, 17, C('acc'), 'l')
    if g.new_rec: T('NEW RECORD!', SW / 2, y0 + 256 * FS, 19, C('acc'))
    for i, ln_ in enumerate(textwrap.wrap(g.sub, 92)[:2]): T(ln_, SW / 2, y0 + (282 + i * 20) * FS, 13, C('cy') if g.passed else C('bad'))
    T('Weak keys: ' + ('  '.join(g.wk) if g.wk else 'none yet - great!'), SW / 2, y0 + 336 * FS, 17, C('acc')); T('They will appear more often in your next drills.', SW / 2, y0 + 362 * FS, 13, C('dim'))
    T('TIP: ' + TIPS[(g.tip + 3) % len(TIPS)], SW / 2, y0 + 404 * FS, 14, C('tx'))
    nxt = good and ((g.mode == 'camp' and g.lv < TOTAL) or (g.mode == 'bn' and g.lv < KD.BN_LEVELS))
    button(x0 + 30 * FS, y0 + ph - 78 * FS, x0 + 230 * FS, y0 + ph - 24 * FS, 'Level map' if g.mode in ('camp', 'prac', 'bn') else 'Menu', 'k:Escape', 'n', 17)
    button(x0 + pw - 400 * FS, y0 + ph - 78 * FS, x0 + pw - 30 * FS, y0 + ph - 24 * FS, 'Next Level  (Enter)' if nxt else 'Play Again  (Enter)', 'k:Return', 'p', 18)
def draw_ach():
    del BT[:]; pw, ph = min(SW - 30, 1040 * FS), min(SH - 24, 700 * FS); x0, y0 = (SW - pw) / 2, max(12, (SH - ph) / 2); panel(x0, y0, x0 + pw, y0 + ph)
    T('ACHIEVEMENTS', x0 + 30 * FS, y0 + 38 * FS, 28, C('acc'), 'l'); T(f'{len(D["ach"])} / {len(ACH)} unlocked', x0 + pw - 30 * FS, y0 + 38 * FS, 18, C('good'), 'r')
    per = 12; pages = (len(ACH) + per - 1) // per; g.ap = max(0, min(pages - 1, g.ap)); bw = pw / 2 - 45 * FS
    for j, (aid, name, desc, coins, fn) in enumerate(ACH[g.ap * per:(g.ap + 1) * per]):
        bx = x0 + 30 * FS + (j % 2) * (bw + 30 * FS); by = y0 + 80 * FS + (j // 2) * 68 * FS; done = aid in D['ach']
        rr(bx, by, bx + bw, by + 60 * FS, 9, C('key'), C('good') if done else C('edge'), 2 if done else 1)
        T(('[x] ' if done else '[ ] ') + name, bx + 14 * FS, by + 20 * FS, 15, C('good') if done else C('tx'), 'l'); T(desc, bx + 14 * FS, by + 43 * FS, 12, C('dim'), 'l'); T(f'+{coins}', bx + bw - 14 * FS, by + 20 * FS, 14, C('acc'), 'r')
    button(x0 + 30 * FS, y0 + ph - 62 * FS, x0 + 200 * FS, y0 + ph - 18 * FS, 'Back', 'k:Escape', 'n', 16); button(x0 + pw / 2 - 150 * FS, y0 + ph - 62 * FS, x0 + pw / 2 - 60 * FS, y0 + ph - 18 * FS, '<', 'ap:-1', 'n', 18)
    T(f'Page {g.ap + 1} / {pages}', x0 + pw / 2, y0 + ph - 40 * FS, 14, C('tx')); button(x0 + pw / 2 + 60 * FS, y0 + ph - 62 * FS, x0 + pw / 2 + 150 * FS, y0 + ph - 18 * FS, '>', 'ap:1', 'n', 18)
def draw_stats():
    pw, ph = min(SW - 30, 980 * FS), 470 * FS; x0, y0 = (SW - pw) / 2, 24 * FS; panel(x0, y0, x0 + pw, y0 + ph); T('YOUR STATS', SW / 2, y0 + 40 * FS, 32, C('acc')); S = D['st']
    T(rankline(), SW / 2, y0 + 78 * FS, 17, C('good')); T(f'Sessions {D["sessions"]}     Keys typed {D["keys"]}     Survival best {D["surv"]}     Speed test best {D["test"]} WPM     Challenge best wave {D["chal"]}', SW / 2, y0 + 106 * FS, 13, C('dim'))
    T(f'Levels cleared {cleared()}/{KD.TOTAL}   Stars {stars_total()}   Enemies {S["kills"]}   Bosses {S["bosses"]}   Dodges {S["dodges"]}   Jumps {S["jumps"]}   Achievements {len(D["ach"])}/{len(ACH)}', SW / 2, y0 + 128 * FS, 13, C('dim'))
    gx0, gy0, gx1, gy1 = x0 + 40 * FS, y0 + 150 * FS, x0 + pw - 40 * FS, y0 + ph - 70 * FS; rr(gx0, gy0, gx1, gy1, 8, C('key'), C('edge'), 1); hs = D['hist'][-30:]; T('WPM history (recent sessions)', SW / 2, gy0 + 18 * FS, 13, C('dim'))
    if len(hs) >= 2:
        mx = max(max(hs), 10); pts = []
        for i, v in enumerate(hs): pts += [gx0 + 24 * FS + (gx1 - gx0 - 48 * FS) * i / (len(hs) - 1), gy1 - 16 * FS - (gy1 - gy0 - 56 * FS) * v / mx]
        cv.create_line(*pts, fill=C('cy'), width=3, smooth=True)
    else: T('Play a few sessions to see your progress here.', SW / 2, (gy0 + gy1) / 2, 15, C('dim'))
    button(x0 + pw / 2 - 90 * FS, y0 + ph - 56 * FS, x0 + pw / 2 + 90 * FS, y0 + ph - 14 * FS, 'Back', 'k:Escape', 'p', 17); T('Keyboard: green = accurate keys, red = weak keys', SW / 2, y0 + ph + 16 * FS, 12, C('dim')); keyboard(set(), set(), None, True)
def draw_pause():
    del BT[:]; pw, ph = min(SW - 30, 560 * FS), 450 * FS; x0, y0 = (SW - pw) / 2, SH * .12; panel(x0, y0, x0 + pw, y0 + ph); T('PAUSED', SW / 2, y0 + 54 * FS, 40, C('acc'))
    for i, (lb, a, st_) in enumerate((('Resume  (Enter)', 'k:Return', 'p'), ('Restart level', 'r:', 'n'), ('Main menu  (Esc)', 'k:Escape', 'n'), ('Quit game', 'q:', 'n'))): button(x0 + 60 * FS, y0 + 100 * FS + i * 68 * FS, x0 + pw - 60 * FS, y0 + 100 * FS + i * 68 * FS + 54 * FS, lb, a, st_, 18)
    button(x0 + 60 * FS, y0 + 100 * FS + 4 * 68 * FS, x0 + pw - 60 * FS, y0 + 100 * FS + 4 * 68 * FS + 40 * FS, f'Enemy speed: {SPD():g}x {spd_label()}   (click or F5)', 'k:F5', 'n', 14)
def draw():
    cv.delete('all'); del BT[:]; st = g.state
    if BG is not None: cv.create_image(0, 0, image=BG, anchor='nw')
    if st == 'menu': draw_menu()
    elif st == 'map': draw_map()
    elif st == 'ach': draw_ach()
    elif st == 'stats': draw_stats()
    elif st == 'armory': draw_armory()
    elif st == 'tintro': draw_tintro()
    elif st == 'tutor': draw_tutor()
    elif st == 'tdone': draw_tdone()
    else:
        draw_game()
        if st == 'intro': draw_intro()
        elif st == 'pause': draw_pause()
        elif st in ('done', 'fail'): draw_end()
    if g.ach_show:
        w_ = 340 * FS; ty_ = SH - 84 * FS; rr(10 * FS, ty_, 10 * FS + w_, ty_ + 60 * FS, 10, C('pan'), C('acc'), 3); T('ACHIEVEMENT UNLOCKED', 10 * FS + w_ / 2, ty_ + 16 * FS, 11, C('acc')); T(f'{g.ach_show[0]}   +{g.ach_show[1]}', 10 * FS + w_ / 2, ty_ + 40 * FS, 15, C('tx'))
    cur = 'hand2' if any(x0 <= MOUSE[0] <= x1 and y0 <= MOUSE[1] <= y1 for x0, y0, x1, y1, _ in BT) else ''
    if cur != g.cursor:
        g.cursor = cur
        try: cv.config(cursor=cur)
        except Exception: pass
    g.mmoved = False

# ============================================================== input (keyboard + mouse)
def mapctx():
    m = g.mmode
    if m == 'bn': return D['bn_stars'], D['bn_unlocked'], g.bsel
    if m == 'tutor': return D['tutor_stars'], D['tutor_ul'], g.tsel
    return D['stars'], D['unlocked'], g.sel
def pick_level(n):
    st_, ul, _c = mapctx(); n = max(1, min(ul, n))
    if g.mmode == 'bn': g.bsel = n
    elif g.mmode == 'tutor': g.tsel = n; g.mch = (n - 1) // 10
    else: g.sel = n; g.mch = (n - 1) // 10
def menu_go(i):
    nm = MENU[i]
    if nm == 'Typing Tutor': g.mmode = 'tutor'; g.tsel = max(1, min(D['tutor_ul'], g.tsel)); g.mch = (g.tsel - 1) // 10; g.state = 'map'
    elif nm in LVROWS: g.mmode = 'camp' if nm == 'Campaign' else 'prac'; g.mch = (g.sel - 1) // 10; g.state = 'map'
    elif nm == 'Daily Challenge': begin('daily', 0)
    elif nm == 'Challenge Mode': begin('chal')
    elif nm == 'Bangla Typing': g.mmode = 'bn'; g.bsel = max(1, min(D['bn_unlocked'], g.bsel)); g.state = 'map'
    elif nm == 'Survival': begin('surv')
    elif nm == 'Boss Rush': begin('rush')
    elif nm == 'Weak-Key Trainer': begin('weak')
    elif nm == 'Custom Text': begin('custom')
    elif nm.startswith('Speed Test'): begin('test')
    elif nm == 'Heroes': g.state = 'armory'; g.tab = 2; g.si = HORDER.index(D['hero']) if D['hero'] in HORDER else 0; pv_setup()
    elif nm == 'Armory': g.state = 'armory'; g.tab = 0; g.si = 0; pv_setup()
    elif nm == 'Achievements': g.state = 'ach'; g.ap = 0
    elif nm == 'Stats': g.state = 'stats'
    else: quit_()
def do_act(a):
    t, _, v = a.partition(':')
    if t == 'k': onkey(NS(keysym=v, char=''))
    elif t == 'm': g.mi = int(v); onkey(NS(keysym='Return', char=''))
    elif t == 'lv': i, d_ = v.split(':'); g.mi = int(i); g.sel = max(1, min(D['unlocked'], g.sel + int(d_))); snd('move')
    elif t == 'sel':
        pick_level(int(v)); snd('move')
    elif t == 'ch':
        g.mch = int(v); snd('move')
        if g.mch * 10 + 1 <= mapctx()[1]: pick_level(g.mch * 10 + 1)
    elif t == 'spd': step_speed(int(v))
    elif t == 'bnfix': D['bn_fix'] = {'auto': True, None: True, True: False, False: 'auto'}[D['bn_fix']]; save(); snd('select')
    elif t == 'bntog': D['bn_native'] = not D['bn_native']; save(); snd('select')
    elif t == 'ap': g.ap += int(v); snd('move')
    elif t == 'item':
        i = int(v)
        if g.si == i: shop_enter()
        else: g.si = i; snd('move')
    elif t == 'tab': g.tab = int(v); g.si = 0; snd('move')
    elif t == 'r': begin(g.mode, g.lv)
    elif t == 'q': quit_()
def onrelease(ev):
    if ev.keysym in HELD: HELD[ev.keysym] = 0
def onkey(ev):
    try:
        k, st = ev.keysym, g.state
        if k == 'KP_Enter': k = 'Return'
        if k == 'F2': D['theme'] = 'light' if D['theme'] == 'dark' else 'dark'; save(); layout(); return
        if k == 'F3': D['vol'] = (D['vol'] + 1) % 4; SND.reload(); snd('select'); save(); return
        if k == 'F4': D['diff'] = D['diff'] % 3 + 1; save(); return
        if k == 'F5': i = min(range(len(SPEEDS)), key=lambda q: abs(SPEEDS[q] - SPD())); D['speed'] = SPEEDS[(i + 1) % len(SPEEDS)]; save(); snd('select'); toast(f'Enemy speed: {SPD():g}x ({spd_label()}) - applies to new enemies'); return
        if k == 'F11' and not OVERLAY:
            FULL[0] = not FULL[0]
            try: root.attributes('-fullscreen', FULL[0])
            except Exception: pass
            return
        if st == 'menu':
            if k in ('Up', 'Down', 'Left', 'Right'): snd('move')
            if k == 'Escape': quit_()
            elif k == 'Up': g.mi = (g.mi - 1) % len(MENU)
            elif k == 'Down': g.mi = (g.mi + 1) % len(MENU)
            elif k == 'Left' and MENU[g.mi] in LVROWS: g.sel = max(1, g.sel - 1)
            elif k == 'Right' and MENU[g.mi] in LVROWS: g.sel = min(D['unlocked'], g.sel + 1)
            elif k == 'Return': menu_go(g.mi)
            return
        if st == 'map':
            bn = g.mmode == 'bn'; _s, ul, cur = mapctx(); per = 4 if bn else 5
            if k == 'Escape': g.state = 'menu'; snd('pause')
            elif k in ('Left', 'Right', 'Up', 'Down'):
                pick_level(cur + {'Left': -1, 'Right': 1, 'Up': -per, 'Down': per}[k]); snd('move')
            elif k in ('Prior', 'Next') and not bn:
                g.mch = max(0, min(14, g.mch + (1 if k == 'Next' else -1))); snd('move')
                if g.mch * 10 + 1 <= ul: pick_level(g.mch * 10 + 1)
            elif k == 'Tab' and bn: D['bn_native'] = not D['bn_native']; save(); snd('select')
            elif k == 'Return':
                if g.mmode == 'tutor': begin_tutor(g.tsel)
                else: begin('bn' if bn else g.mmode, g.bsel if bn else g.sel)
            return
        if st == 'ach':
            if k == 'Escape': g.state = 'menu'; snd('pause')
            elif k in ('Left', 'Right', 'Up', 'Down'): g.ap += 1 if k in ('Right', 'Down') else -1; snd('move')
            return
        if st == 'tintro':
            if k == 'Return': g.state = 'tutor'; snd('go')
            elif k == 'Escape': g.state = 'map'; g.mmode = 'tutor'
            return
        if st == 'tutor':
            if k == 'Escape': g.state = 'map'; g.mmode = 'tutor'; return
            c = ev.char or (' ' if k == 'space' else '')
            if len(c) == 1 and c.isprintable(): tutor_key(c)
            return
        if st == 'tdone':
            if k == 'Return': begin_tutor(g.tu.L + 1 if (g.tu.res['passed'] and g.tu.L < KD.TOTAL) else g.tu.L)
            elif k in ('r', 'R'): begin_tutor(g.tu.L)
            elif k == 'Escape': g.state = 'map'; g.mmode = 'tutor'; g.tsel = max(1, min(D['tutor_ul'], g.tu.L + (1 if g.tu.res['passed'] else 0))); g.mch = (g.tsel - 1) // 10
            return
        if st == 'armory':
            if k == 'Escape': g.state = 'menu'; snd('pause')
            elif k == 'Up': g.si = (g.si - 1) % len(items()); snd('move')
            elif k == 'Down': g.si = (g.si + 1) % len(items()); snd('move')
            elif k in ('Left', 'Right', 'Tab'): g.tab = (g.tab + (1 if k != 'Left' else -1)) % 3; g.si = 0; snd('move')
            elif k == 'Return': shop_enter()
            return
        if st == 'stats':
            if k in ('Escape', 'Return'): g.state = 'menu'
            return
        if st == 'intro':
            if k == 'Return': g.state = 'play'; g.ban = 1.4; g.last = time.perf_counter(); snd('go')
            elif k == 'Escape': g.state = 'map' if g.mode in ('camp', 'prac', 'bn') else 'menu'; g.mmode = g.mode if g.mode in ('camp', 'prac', 'bn') else g.mmode
            elif k == 'Tab' and g.mode == 'bn': D['bn_native'] = not D['bn_native']; save(); snd('select')
            elif k == 'Left': step_speed(-1)
            elif k == 'Right': step_speed(1)
            return
        if st in ('done', 'fail'):
            if k == 'Return':
                if g.mode == 'camp' and st == 'done' and g.lv < TOTAL: begin('camp', g.lv + 1)
                elif g.mode == 'bn' and st == 'done' and g.lv < KD.BN_LEVELS: begin('bn', g.lv + 1)
                elif g.mode in ('camp', 'bn') and st == 'done': g.state = 'menu'
                else: begin(g.mode, g.lv)
            elif k == 'Escape':
                if g.mode in ('camp', 'prac', 'bn'):
                    g.mmode = g.mode; g.state = 'map'
                    if g.mode == 'bn': g.bsel = max(1, min(D['bn_unlocked'], g.lv + (1 if st == 'done' else 0)))
                    else: g.sel = max(1, min(D['unlocked'], g.lv + (1 if (g.mode == 'camp' and st == 'done') else 0))); g.mch = (g.sel - 1) // 10
                else: g.state = 'menu'
            return
        if st == 'pause':
            if k == 'Return': g.state = 'play'; g.last = time.perf_counter()
            elif k == 'Escape': g.state = 'menu'
            return
        if k in ('Left', 'Right', 'Down'): HELD[k] = 1; return
        if k == 'Up': do_jump(); return
        if k == 'Escape': g.state = 'pause'; snd('pause'); return
        if k == 'F1': g.help = not g.help; return
        if k == 'BackSpace': unlock(); return
        if k == 'Return': ultimate(); return
        if k in ('Tab', 'ISO_Left_Tab'):
            al = sorted((e for e in alive() if e.w), key=lambda e: abs(e.x - g.hero.x))
            if al:
                nx = al[(al.index(g.tg) + 1) % len(al)] if g.tg in al else al[0]; unlock(); g.tg = nx
            return
        c = ev.char or (' ' if k == 'space' else '')
        if len(c) == 1 and c.isprintable(): typekey(c)
        elif len(c) > 1 and bn_native():
            for ch_ in c:
                if ch_.isprintable(): typekey(ch_)
    except Exception:
        log(traceback.format_exc())
        if DEBUG: raise
def onclick(ev):
    try:
        activate(); MOUSE[:] = [ev.x, ev.y]
        for x0, y0, x1, y1, a in reversed(BT):
            if x0 <= ev.x <= x1 and y0 <= ev.y <= y1: do_act(a); return
    except Exception:
        log(traceback.format_exc())
        if DEBUG: raise
def onmotion(ev):
    if abs(ev.x - MOUSE[0]) + abs(ev.y - MOUSE[1]) > 2: g.mmoved = True
    MOUSE[:] = [ev.x, ev.y]
def onwheel(ev):
    up = getattr(ev, 'num', 0) == 4 or getattr(ev, 'delta', 0) > 0
    if g.state in ('menu', 'armory', 'ach'): onkey(NS(keysym='Up' if up else 'Down', char=''))
root.bind('<Key>', onkey); root.bind('<KeyRelease>', onrelease); root.bind('<FocusOut>', lambda e: [HELD.__setitem__(k_, 0) for k_ in HELD]); cv.bind('<Button-1>', onclick); cv.bind('<Motion>', onmotion); cv.bind('<MouseWheel>', onwheel); cv.bind('<Button-4>', onwheel); cv.bind('<Button-5>', onwheel)
try:
    if not OVERLAY:
        _ic = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.png')
        if os.path.exists(_ic): ICON = tk.PhotoImage(file=_ic); root.iconphoto(True, ICON)
except Exception: pass
root.report_callback_exception = lambda *a: log(''.join(traceback.format_exception(*a)))
if not OVERLAY: root.protocol('WM_DELETE_WINDOW', quit_)

def loop():
    if g.quit: return
    t_start = time.perf_counter()
    try:
        now = t_start; dt = min(.05, now - g.last); g.last = now
        if down(0x11) and down(0x10) and down(0x51): quit_(); return
        if PEND[0] and now - PEND[1] > .12:
            global SW, SH
            SW, SH = PEND[0]; PEND[0] = None; layout(); g.hero.x = min(g.hero.x, SW - 30)
        ach_tick(dt); g.flash = max(0, g.flash - dt); g.act = getattr(g, 'act', 0) + dt
        if g.act > 1: g.act = 0; ach_check()
        if g.state != 'play':
            for k_ in HELD: HELD[k_] = 0
        if g.state == 'play':
            try: foc = root.focus_displayof() is not None
            except Exception: foc = True
            if foc: g.unf = 0
            else:
                g.unf += dt
                if g.unf > .8: g.state = 'pause'; g.unf = 0; activate()
            if g.state == 'play': update(dt)
        elif g.state == 'armory': g.toast[1] = max(0, g.toast[1] - dt); pv_update(dt)
        draw()
    except Exception:
        log(traceback.format_exc())
        if DEBUG: raise
        g.state = 'menu'; g.err = 'Recovered from an error (see ~/.typestrike/error.log)'
    if not g.quit:
        try: root.after(max(1, 15 - int((time.perf_counter() - t_start) * 1000)), loop)
        except Exception: pass
if __name__ == '__main__':
    activate(); loop(); root.mainloop()
