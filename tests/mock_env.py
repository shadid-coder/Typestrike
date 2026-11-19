"""Headless test helpers for TypeStrike: a fake Tk + fake Windows API so the whole game logic and every
drawing call can be exercised on any machine (CI) without a display."""
import sys, types, ctypes, os, time, random, runpy, tempfile
from types import SimpleNamespace as NS

class Cv:
    def __init__(s, root=None, width=1920, height=1080, **k): s.w, s.h, s.calls = width, height, 0
    def pack(s, *a, **k): pass
    def bind(s, *a, **k): pass
    def delete(s, *a): s.calls = 0
    def config(s, *a, **k): pass
    def winfo_width(s): return s.w
    def winfo_height(s): return s.h
    def __getattr__(s, name):
        if not name.startswith('create_'): raise AttributeError(name)
        def f(*a, **k):
            s.calls += 1
            flat = []
            for v in a: flat += list(v) if isinstance(v, (list, tuple)) else [v]
            flat = [v for v in flat if isinstance(v, (int, float))]
            if name in ('create_line', 'create_polygon') and len(flat) < 4: raise ValueError(f'{name}: need >=2 points, got {a}')
            if name in ('create_oval', 'create_rectangle') and len(flat) != 4: raise ValueError(f'{name}: need 4 coords, got {a}')
            if any(v != v or abs(v) > 1e7 for v in flat): raise ValueError(f'{name}: bad number {a}')
            return 1
        return f
class Root:
    def __init__(s): s.cb = None; s.dead = False; s.sw, s.sh = 1920, 1080
    def winfo_screenwidth(s): return s.sw
    def winfo_screenheight(s): return s.sh
    def winfo_id(s): return 5
    def focus_displayof(s): return object()
    def after(s, ms, fn): s.cb = fn
    def destroy(s): s.dead = True
    def __getattr__(s, n): return lambda *a, **k: None
class Photo:
    def __init__(s, *a, **k): s.puts = 0
    def put(s, c, to=None): s.puts += 1; assert len(c) == 7 and to and len(to) == 4
class Font:
    def __init__(s, *a, **k): pass
    def measure(s, t): return len(t) * 11

def load(path, plat='win32', size=(1920, 1080), argv=()):
    os.environ['KW_DEBUG'] = '1'; os.environ['HOME'] = os.environ['USERPROFILE'] = tempfile.mkdtemp()
    tkm = types.ModuleType('tkinter'); fm = types.ModuleType('tkinter.font')
    R = Root(); R.sw, R.sh = size
    tkm.Tk = lambda: R; tkm.Canvas = Cv; tkm.PhotoImage = Photo; fm.Font = Font; fm.families = lambda *a: ('Segoe UI', 'Consolas', 'Impact', 'DejaVu Sans'); tkm.font = fm
    sys.modules['tkinter'] = tkm; sys.modules['tkinter.font'] = fm
    sys.platform = plat; sys.argv = ['kw'] + list(argv)
    CM = []; PROC = []
    if plat == 'win32':
        u = NS(GetSystemMetrics=lambda i: size[i], GetParent=lambda h: h, GetWindowLongW=lambda h, i: 0, SetWindowLongW=lambda *a: 0, SetForegroundWindow=lambda h: 1, GetAsyncKeyState=lambda v: 0, SetProcessDPIAware=lambda: 1)
        ctypes.windll = NS(winmm=NS(mciSendStringW=lambda c, a, b, d: (CM.append(c), 0)[1]), shcore=NS(SetProcessDpiAwareness=lambda x: 0), user32=u)
    else:
        if hasattr(ctypes, 'windll'): del ctypes.windll
    import subprocess, shutil
    class P:
        def __init__(s, cmd, **k): PROC.append(cmd)
        def poll(s): return 0
    subprocess.Popen = P; shutil.which = lambda n: '/usr/bin/' + n
    T = [1000.0]; time.perf_counter = lambda: T[0]
    M = runpy.run_path(path, run_name='__main__')
    return NS(M=M, g=M['g'], D=M['D'], root=R, T=T, CM=CM, PROC=PROC)
