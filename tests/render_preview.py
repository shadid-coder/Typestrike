"""Dev tool: renders the game's screens to PNG files using Pillow (no Tk needed) so the layout can be reviewed anywhere.
    python tests/render_preview.py [outdir] [WIDTHxHEIGHT]
The output approximates Tk's look (fonts differ slightly)."""
import sys, os, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mock_env as me
from PIL import Image, ImageDraw, ImageFont
from types import SimpleNamespace as NS
FONT = ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf']
FONTR = ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf']
MONO = ['/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf']
_fc = {}
def font(spec):
    fam, px, wt = (list(spec) + ['bold'])[:3] if isinstance(spec, (tuple, list)) else (spec.family if hasattr(spec, 'family') else 'x', 16, 'bold')
    px = abs(int(px)); key = (fam, px, wt)
    if key not in _fc:
        cands = MONO if fam in ('Consolas', 'Menlo') else (FONT if wt == 'bold' else FONTR)
        for p in cands:
            try: _fc[key] = ImageFont.truetype(p, px); break
            except Exception: pass
        else: _fc[key] = ImageFont.load_default()
    return _fc[key]
class PCanvas:
    def __init__(s, w, h): s.img = Image.new('RGB', (w, h), (20, 22, 40)); s.dr = ImageDraw.Draw(s.img, 'RGBA'); s.w, s.h = w, h
    def pack(s, *a, **k): pass
    def bind(s, *a, **k): pass
    def config(s, *a, **k): pass
    def winfo_width(s): return s.w
    def winfo_height(s): return s.h
    def delete(s, *a): s.dr.rectangle([0, 0, s.w, s.h], fill=(20, 22, 40))
    def _pts(s, a):
        flat = []
        for v in a: flat += list(v) if isinstance(v, (list, tuple)) else [v]
        return [(flat[i], flat[i + 1]) for i in range(0, len(flat) - 1, 2)]
    def create_line(s, *a, width=1, fill='#fff', **k):
        if fill: s.dr.line(s._pts(a), fill=fill, width=max(1, int(width)), joint='curve')
    def create_polygon(s, *a, fill='', outline='', width=1, **k):
        p = s._pts(a)
        if k.get('smooth') and len(p) > 6: p = p
        if fill: s.dr.polygon(p, fill=fill)
        if outline and width: s.dr.line(p + [p[0]], fill=outline, width=max(1, int(width)))
    def create_oval(s, x0, y0, x1, y1, fill='', outline='', width=1, **k):
        if k.get('stipple'): return
        s.dr.ellipse([x0, y0, x1, y1], fill=fill or None, outline=outline or None, width=max(1, int(width)))
    def create_rectangle(s, x0, y0, x1, y1, fill='', outline='', width=1, **k): s.dr.rectangle([x0, y0, x1, y1], fill=fill or None, outline=outline or None, width=max(0, int(width)))
    def create_image(s, x, y, image=None, **k):
        if image is not None and getattr(image, 'pil', None) is not None: s.img.paste(image.pil, (int(x), int(y)))
    def create_text(s, x, y, text='', fill='#fff', anchor='center', font=None, **k):
        f = font_(font); lines = str(text).split('\n'); lh = f.size * 1.25; y0 = y - lh * (len(lines) - 1) / 2
        for i, ln in enumerate(lines):
            w = s.dr.textlength(ln, font=f); xx = x - w / 2 if anchor == 'center' else (x if anchor == 'w' else x - w)
            s.dr.text((xx, y0 + i * lh - f.size * .62), ln, fill=fill, font=f)
def font_(spec): return font(spec) if isinstance(spec, (tuple, list)) else font(('x', 18, 'bold'))
class PPhoto:
    def __init__(s, width=1, height=1, **k): s.pil = Image.new('RGB', (max(1, width), max(1, height)), (0, 0, 0)) if width > 1 else None
    def put(s, c, to=None):
        if s.pil is not None and to and to[2] > to[0] and to[3] > to[1]: ImageDraw.Draw(s.pil).rectangle([to[0], to[1], to[2] - 1, to[3] - 1], fill=c)
class PFont:
    def __init__(s, *a, family='Consolas', size=-19, weight='bold', **k): s.size = abs(size); s.f = font((family, abs(size), 'bold'))
    def measure(s, t): return int(ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(t, font=s.f))
    @property
    def family(s): return 'Consolas'
def render(outdir='/tmp/kw_preview', size=(1920, 1080), plat='win32', theme='dark'):
    os.makedirs(outdir, exist_ok=True)
    E = me.load(os.path.join(HERE, '..', 'typestrike.py'), plat, size)
    M, g, D, root, T = E.M, E.g, E.D, E.root, E.T; G = M['layout'].__globals__
    pc = PCanvas(G['SW'], G['SH']); G['cv'] = pc; G['FL'] = PFont(family='Consolas', size=-max(12, int(19 * G['FS']))); G['tkf'] = NS(Font=lambda *a, **k: PFont(**k), families=lambda *a: ())
    D['theme'] = theme; M['layout']()
    if G['BG'] is not None: G['BG'] = PPhoto(); 
    G['tk'] = NS(PhotoImage=PPhoto, Tk=None, Canvas=None)
    if not G['OVERLAY']:
        G['BG'] = G['make_bg']()
    key = lambda k, ch='': M['onkey'](NS(keysym=k, char=ch))
    def frame(n=1):
        for _ in range(n): T[0] += .016; root.cb()
    def shot(name):
        frame(2); pc.img.save(os.path.join(outdir, name + '.png')); print('saved', name)
    random.seed(3); D['unlocked'] = 30; D['coins'] = 1234; D['owned'] = ['fists', 'knife', 'katana']; D['stars'] = {'1': 3, '2': 3, '3': 2, '4': 1, '5': 3, '6': 2, '7': 1}
    if G['OVERLAY']:   # overlay: show a fake desktop behind it
        pass
    g.state = 'menu'; shot('1_menu'); g.mi = 2; shot('1b_menu_survival')
    g.state = 'armory'; g.tab = 0; g.si = 5; M['pv_setup'](); frame(120); shot('2_armory_weapons'); g.tab = 1; g.si = 6; frame(80); shot('2b_armory_styles')
    g.state = 'stats'; D['hist'] = [12, 15, 14, 19, 22, 21, 26, 30, 29, 34]; shot('3_stats')
    D['weapon'] = 'katana'; D['style'] = 'taekwondo'; D['own_styles'] = ['boxing', 'taekwondo']
    M['begin']('camp', 4); shot('4_intro')
    def fight(L, name, kinds, mode='camp', moves=0):
        M['begin'](mode, L); key('Return'); frame(130); g.en.clear(); g.to = 0; g.bq = False; h = g.hero
        for i, k in enumerate(kinds):
            e = M['E'](k, G['SW'] * (.2 + .6 * i / max(1, len(kinds) - 1)) if len(kinds) > 1 else G['SW'] * .8, G['GY']); e.wp = M['armed_for'](k, L) if k != 'boss' else 'greatsword'; e.w = M['pick_word'](min(L, 14), (), 'fast') if k != 'boss' else 'keep your wrists relaxed'
            e.hpw = e.mh = 2 if k in ('tank', 'shield', 'boss') else 1; e.shield = k == 'shield'; e.spd = 0; e.x = G['SW'] * (.15 + .7 * i / max(1, len(kinds) - 1)) if len(kinds) > 1 else G['SW'] * .8; e.face = 1 if e.x < h.x else -1; g.en.append(e)
        if 'archer' in kinds: [setattr(e, 'aim', .5) for e in g.en if e.kind == 'archer']
        for e in g.en:
            if e.kind == 'bomber': e.fuse = 1.7
        frame(10); shot(name)
    fight(14, '5_game_enemies', ['grunt', 'shield', 'ninja', 'archer', 'bomber', 'boss'])
    for _ in range(3): M['typec'] if False else None
    # mid-attack hero
    e = g.en[1]; g.tg = e; e.i = 2; h = g.hero; h.x = e.x - 90; h.play('sw_slash', .5); h.mp = .5; frame(1); h.cur = M['interp'](M['MOVES']['sw_slash'], .52, M['IMP']['sw_slash']); M['hit_fx'](e, 'sw_slash', True); shot('5b_game_slash')
    g.state = 'pause'; shot('6_pause')
    g.state = 'done'; g.title = 'LEVEL CLEAR!'; g.passed = True; g.stars = 3; g.earned = 128; g.wk = ['k', 'p']; g.sub = 'NEW WEAPON: Katana  (equipped - change it in the Armory)'; shot('7_end')
    return outdir
if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/kw_preview'; sz = tuple(int(v) for v in sys.argv[2].split('x')) if len(sys.argv) > 2 else (1920, 1080)
    render(out, sz, sys.argv[3] if len(sys.argv) > 3 else 'win32')
