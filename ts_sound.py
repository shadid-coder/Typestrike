"""Keyboard Warrior - sound synthesis (pure Python, no files, no dependencies).
Every effect is built from layers: a low 'body' thump, a mid 'slap', a bright 'click', metallic partials, filtered-noise sweeps and a little room reverb.
Run:  python keyboard_warrior.py --sounds   to hear every effect one after another."""
import math, random
SR = 22050; TAU = 6.283185307179586
def N(d): return max(1, int(SR * d))
def _nrm(x, g=1.):
    pk = max(1e-9, max(abs(v) for v in x)); return [v / pk * g for v in x]
def sine(f0, f1, dur, decay=6., attack=.002, g=1.):
    n = N(dur); ph = 0.; out = []; r = (f1 / f0) if f0 > 0 else 1.
    for i in range(n):
        t = i / n; ph += TAU * f0 * (r ** t) / SR; out.append(math.sin(ph) * math.exp(-decay * t * dur * 5 / max(dur, .01) / 5) * min(1., i / (SR * attack + 1)) * g)
    return out
def noise(dur, seed=1, g=1.):
    r = random.Random(seed); return [r.uniform(-1, 1) * g for _ in range(N(dur))]
def lp(x, fc):
    a = 1 - math.exp(-TAU * fc / SR); y = 0.; out = []
    for v in x: y += (v - y) * a; out.append(y)
    return out
def hp(x, fc):
    a = math.exp(-TAU * fc / SR); h = 0.; px = 0.; out = []
    for v in x: h = a * (h + v - px); px = v; out.append(h)
    return out
def bp(x, lo, hi): return hp(lp(lp(x, hi), hi), lo)
def sweep(x, lo0, lo1, hi0, hi1):
    n = len(x); y1 = y2 = h = px = 0.; out = []
    for i, v in enumerate(x):
        t = i / n; ah = 1 - math.exp(-TAU * (hi0 + (hi1 - hi0) * t) / SR); al = math.exp(-TAU * (lo0 + (lo1 - lo0) * t) / SR)
        y1 += (v - y1) * ah; y2 += (y1 - y2) * ah; h = al * (h + y2 - px); px = y2; out.append(h)
    return out
def env(x, decay=8., attack=.003, shape=None):
    n = len(x); out = []
    for i, v in enumerate(x):
        t = i / n; e = math.exp(-decay * t) * min(1., i / (SR * attack + 1))
        if shape == 'swell': e = math.sin(3.14159 * t) ** 1.5
        elif shape == 'rise': e = (t ** 2) * min(1., (1 - t) * 14)
        out.append(v * e)
    return out
def sat(x, k=2.): return [math.tanh(v * k) / math.tanh(k) for v in x]
def mix(*layers):
    """layers: (signal, delay_seconds, gain) or just a signal"""
    ls = [(l, 0., 1.) if isinstance(l, list) else tuple(l) + (0., 1.)[len(l) - 1:] for l in layers]
    n = max(int(SR * d) + len(s) for s, d, g in ls); out = [0.] * n
    for s, d, g in ls:
        o = int(SR * d)
        for i, v in enumerate(s): out[o + i] += v * g
    return out
def reverb(x, wet=.25, room=1.0, tail=.35):
    ext = x + [0.] * N(tail); n = len(ext); out = list(ext)
    for dly, fb in ((int(SR * .0297 * room), .62), (int(SR * .0371 * room), .58), (int(SR * .0411 * room), .54), (int(SR * .0437 * room), .5)):
        buf = [0.] * dly; j = 0
        for i in range(n):
            y = ext[i] + buf[j] * fb; buf[j] = y; j = j + 1 if j + 1 < dly else 0; out[i] += y * wet * .35
    return out
def partials(freqs, dur, decay=8., g=1., amps=None, jitter=0):
    amps = amps or [1. / (1 + .4 * i) for i in range(len(freqs))]; n = N(dur); out = [0.] * n
    for f, a in zip(freqs, amps):
        w = TAU * f / SR; d = decay * (1 + .25 * freqs.index(f))
        for i in range(n): out[i] += math.sin(w * i) * math.exp(-d * i / n * (dur * 1.0 / dur)) * a * g
    return out
def bell(f, dur=.5, g=1., dec=6.):
    n = N(dur); out = [0.] * n
    for r, a, d in ((1, 1., 1.), (2.01, .45, 1.6), (3.0, .25, 2.2), (4.2, .12, 3.0)):
        w = TAU * f * r / SR
        for i in range(n): out[i] += math.sin(w * i) * math.exp(-dec * d * i / n) * a * min(1., i / (SR * .002 + 1))
    return [v * g for v in out]
def voice(f0, f1, dur, forms, g=1., breath=.15, seed=3):
    n = N(dur); ph = 0.; r = random.Random(seed); mid = (f0 + f1) / 2; hs = []
    for k in range(1, int(4200 / mid)):
        fk = k * mid; hs.append((k, sum(math.exp(-((fk - fc) / bw) ** 2) for fc, bw in forms)))
    out = []
    for i in range(n):
        t = i / n; f = f0 + (f1 - f0) * t; ph += TAU * f / SR
        v = sum(a * math.sin(k * ph) for k, a in hs) * .25 + r.uniform(-1, 1) * breath
        out.append(v * math.sin(3.14159 * min(1, t * 1.4)) * math.exp(-2.5 * t) * g)
    return lp(out, 3500)
def crackle(dur, rate=60, seed=5, g=1., lo=1500):
    r = random.Random(seed); n = N(dur); out = [0.] * n; i = 0
    while i < n:
        i += int(r.expovariate(rate) * SR) + 1
        if i < n:
            a = r.uniform(.3, 1.); L = int(SR * r.uniform(.001, .004))
            for k in range(L):
                if i + k < n: out[i + k] += a * (1 - k / L) * r.uniform(-1, 1)
    return hp([v * g for v in out], lo)
def fade(x, a=.002, b=.012):
    n = len(x); fa = int(SR * a); fb = int(SR * b)
    for i in range(min(fa, n)): x[i] *= i / fa
    for i in range(min(fb, n)): x[n - 1 - i] *= i / fb
    return x

PENTA = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5, 1174.7, 1318.5]
def S_tick(k):
    f = PENTA[k]; return mix(sine(f, f * .995, .09, 9, g=.55), sine(f * 3.98, f * 3.9, .05, 14, g=.12), (_nrm(env(hp(noise(.012, 40 + k), 4000), 3), .16), 0., 1.))
def S_punch(v):
    f0, f1 = (150, 48) if v == 0 else (180, 55) if v == 1 else (120, 38)
    body = sat(sine(f0, f1, .16, 7, g=1.), 1.6); slap = _nrm(env(bp(noise(.07, 11 + v), 500, 2600), 7), .6); click = _nrm(env(hp(noise(.012, 21 + v), 3500), 3), .35)
    return mix(body, slap, click)
def S_kick(v):
    body = sat(sine(170 + v * 25, 42, .22, 6), 1.5); whip = _nrm(env(sweep(noise(.1, 31 + v), 900, 1500, 6500, 2200), 6), .7); crack = _nrm(env(hp(noise(.02, 41), 4500), 3), .4)
    return mix(body, (whip, 0., 1.), (crack, .015, 1.))
def S_whoosh(dur, a, b, g=.9, seed=7, shape='swell'): return _nrm(env(sweep(noise(dur, seed), a * .35, b * .5, a, b), 0, shape=shape), g)
def S_slash(v):
    f = [1, 1.12, .92][v]; sw = S_whoosh(.13, 2200 * f, 8500 * f, .8, 50 + v); ring = _nrm(env(partials([2900 * f, 4100 * f, 6200 * f], .3, 5), 6), .28); return mix(sw, (ring, .05, 1.), (_nrm(env(hp(noise(.008, 60 + v), 5000), 3), .3), .06, 1.))
def S_shing():
    sw = S_whoosh(.16, 1500, 9500, .8, 71, 'rise'); ring = _nrm(env(partials([2400, 3210, 4710, 6350, 8100], .8, 3), 3.2), .55); return reverb(mix(sw, (ring, .1, 1.)), .22, 1.0, .2)
def S_stab(v):
    th = sat(sine(220 - v * 30, 70, .1, 9), 1.4); hiss = _nrm(env(bp(noise(.07, 81 + v), 2800, 8000), 6), .6); ring = _nrm(env(partials([3100, 4600], .14, 6), 7), .2)
    return mix(th, (hiss, 0., 1.), (ring, .02, 1.))
def S_knife():
    sl = S_whoosh(.08, 3000, 10000, .8, 91); ring = _nrm(env(partials([4200, 5600, 7300], .13, 6), 8), .3); return mix(sl, (ring, .03, 1.))
def S_axe():
    th = sat(sine(115, 42, .24, 6), 1.8); crack = _nrm(env(bp(noise(.05, 92), 700, 3200), 8), .8); ring = _nrm(env(partials([900, 1700, 2900], .25, 5), 8), .3); return mix(th, crack, (ring, .01, 1.))
def S_hammer():
    bo = sat(sine(72, 26, .55, 4), 2.); rub = _nrm(env(lp(noise(.4, 93), 700), 7), .6); cl = _nrm(env(partials([520, 1130, 1700, 2600], .5, 5), 6), .45); return reverb(mix(bo, rub, (cl, .01, 1.)), .25, 1.1, .25)
def S_clang(): return reverb(mix(_nrm(env(partials([1180, 1760, 2650, 3400, 4900], .55, 4), 5), .9), (_nrm(env(hp(noise(.02, 94), 3000), 4), .5), 0., 1.)), .18, .9, .15)
def S_wood():
    return mix(sine(520, 360, .09, 28, g=.9), sine(1150, 900, .06, 40, g=.35), _nrm(env(bp(noise(.015, 95), 1500, 5500), 4), .5))
def S_fire(): return mix(_nrm(env(sweep(noise(.35, 96), 120, 200, 900, 2600), 3, shape=None), .6), _nrm(env(crackle(.35, 110, 97, lo=1800), 2), .8))
def S_ice():
    r = random.Random(98); ls = [(_nrm(env(partials([r.uniform(2200, 6200)], .22, 9), 5), .45), i * .035, 1.) for i in range(6)]
    return mix(*ls, _nrm(env(hp(noise(.06, 99), 6000), 7), .3))
def S_zap():
    return mix(_nrm(env(crackle(.28, 260, 100, lo=900), 3), .9), _nrm(env(sine(2200, 500, .25, 5), 0), .35), _nrm(env(sweep(noise(.2, 101), 500, 900, 3000, 8000), 5), .4))
def S_finish():
    ri = S_whoosh(.16, 300, 4500, .55, 102, 'rise'); th = sat(sine(95, 28, .55, 4.5), 2.2); sl = _nrm(env(bp(noise(.28, 103), 200, 4200), 11), .75); rg = _nrm(env(partials([1180, 1760, 2650], .7, 3), 4), .3)
    return reverb(mix(ri, (th, .15, 1.), (sl, .15, 1.), (rg, .17, 1.)), .3, 1.1, .35)
def S_break():
    return reverb(mix(_nrm(env(hp(noise(.16, 104), 2500), 22), .8), _nrm(env(partials([2100, 3300, 5100], .35, 6), 7), .5), sat(sine(160, 55, .16, 8), 1.4)), .18, .8, .15)
def S_hurt():
    gr = voice(170, 105, .2, [(480, 140), (850, 180)], 1., .12, 6); th = sat(sine(130, 48, .14, 8), 1.6); return mix(_nrm(gr, .65), (th, 0., 1.), (_nrm(env(lp(noise(.08, 105), 900), 9), .4), 0., 1.))
def S_block(): return mix(_nrm(env(partials([880, 1320, 2150], .3, 6), 7), .6), sat(sine(200, 80, .07, 10), 1.3), _nrm(env(hp(noise(.02, 106), 3000), 5), .4))
def S_wrong(): return fade(mix(sine(196, 170, .1, 14, g=.5), (sine(185, 160, .12, 14, g=.5), .06, 1.), _nrm(env(lp(noise(.03, 107), 800), 5), .2)))
def S_ultimate():
    ri = S_whoosh(.7, 200, 7000, .8, 108, 'rise'); ch = [(_nrm(env(sine(f, f, .9, 2.5, attack=.15), 0), .28), 0.1, 1.) for f in (261.6, 329.6, 392, 523.3)]
    boom = mix(sat(sine(100, 26, .7, 4), 2.), _nrm(env(bp(noise(.4, 109), 150, 5000), 8), .8))
    return reverb(mix(ri, *ch, (boom, .68, 1.), (bell(1046.5, .8, .35), .7, 1.)), .3, 1.2, .5)
def S_combo(): return mix(bell(784, .4, .5), (bell(988, .4, .5), .07, 1.), (bell(1175, .5, .55), .14, 1.))
def S_heal():
    ls = [(_nrm(env(partials([f, f * 2, f * 3], .35, 5), 6), .4), i * .055, 1.) for i, f in enumerate([523, 659, 784, 1047])]; return reverb(mix(*ls), .15, .8, .2)
def S_win():
    ls = [(bell(f, .6, .5), i * .11, 1.) for i, f in enumerate([523, 659, 784, 1047])] + [(_nrm(env(mix(*[sine(f, f, .9, 2.5, attack=.05) for f in (523, 659, 784, 1047)]), 0), .35), .45, 1.)]; return reverb(mix(*ls), .22, 1.1, .4)
def S_lose():
    ls = [(lp(_nrm(env(partials([f, f * 2, f * 3], .38, 3), 4), .45), 2000), i * .2, 1.) for i, f in enumerate([392, 349, 311, 262, 196])]; return reverb(mix(*ls), .2, 1.2, .35)
def S_move(): return fade(mix(sine(900, 880, .03, 25, g=.5), _nrm(env(hp(noise(.01, 110), 3000), 3), .15)))
def S_select(): return mix(bell(784, .2, .5, 8), (bell(1175, .25, .5, 8), .05, 1.))
def S_go(): return reverb(mix(_nrm(env(sine(300, 900, .3, 1.5, attack=.1), 0), .45), (bell(1175, .45, .55), .22, 1.), (bell(1568, .5, .5), .3, 1.)), .15, .9, .2)
def S_pause(): return mix(sine(620, 380, .1, 7, g=.5), (sine(440, 300, .1, 7, g=.4), .06, 1.))
def S_thud(): return mix(sat(sine(85, 34, .2, 9), 1.5), _nrm(env(lp(noise(.1, 111), 450), 9), .4))
def S_land(): return mix(sat(sine(120, 55, .1, 12), 1.3), _nrm(env(lp(noise(.08, 112), 1500), 14), .35))
def S_boss():
    n = N(1.4); out = [0.] * n; ph = [0.] * 6
    for i in range(n):
        t = i / n; f = 55 * (1 + .03 * math.sin(i * .0004)); s = 0.
        for k in range(6): ph[k] += TAU * f * (k + 1) * (1 + (k % 2) * .004) / SR; s += math.sin(ph[k]) / (k + 1)
        out[i] = s * math.sin(3.14159 * min(1, t * 1.15)) ** 1.2
    return reverb(mix(lp(_nrm(out, .8), 900), _nrm(env(lp(noise(1.0, 113), 130), 2), .5)), .3, 1.3, .5)
def S_warn(): return mix(sat(sine(75, 55, .14, 6), 1.5), (sat(sine(70, 50, .16, 6), 1.5), .2, 1.))
def S_coin(): return mix(bell(1568, .25, .5, 9), (bell(2093, .4, .55, 7), .06, 1.))
def S_buy(): return reverb(mix(*[(bell(f, .35, .5, 8), i * .07, 1.) for i, f in enumerate([1047, 1319, 1568, 2093])], (_nrm(env(hp(noise(.03, 114), 5000), 6), .2), 0., 1.)), .12, .8, .15)
def S_crash():
    return reverb(mix(_nrm(env(bp(noise(1., 115), 300, 7000), 3.5), .8), sat(sine(80, 24, .9, 3), 2.), (_nrm(env(partials([180, 470, 900, 1500], .9, 3), 3), .35), 0., 1.)), .35, 1.4, .5)
def S_arrow(): return mix(S_whoosh(.11, 1500, 5000, .6, 116), (_nrm(env(sine(380, 300, .16, 22), 0), .35), 0., 1.))
def S_boom():
    ns = sweep(noise(.8, 117), 30, 30, 4000, 250); return reverb(mix(sat(sine(75, 24, .85, 3.2), 2.2), _nrm(env(ns, 3.2), .9)), .3, 1.2, .4)
def S_fuse(): return fade(mix(_nrm(env(hp(noise(.5, 118), 3500), 1.2), .25), _nrm(env(crackle(.5, 90, 119, lo=2500), 1.), .5)))
def S_jump(): return mix(S_whoosh(.13, 300, 1400, .5, 120), sat(sine(140, 90, .06, 20), 1.2))
def S_dodge(): return mix(S_whoosh(.1, 800, 4500, .65, 121), (bell(2400, .12, .3, 12), .02, 1.))
def S_dash(): return S_whoosh(.15, 600, 3500, .6, 122)
def S_ach(): return reverb(mix(*[(bell(f, .6, .5), i * .09, 1.) for i, f in enumerate([1047, 1319, 1568, 2093])], (_nrm(env(hp(noise(.2, 123), 6000), 5), .15), .3, 1.)), .22, 1., .3)
def S_phase():
    rr = voice(70, 140, .8, [(300, 120), (700, 200)], 1., .3, 8); gong = _nrm(env(partials([100, 230, 430, 640, 910], 1.2, 2), 2), .6); return reverb(mix(_nrm(rr, .7), (gong, .45, 1.), (sat(sine(90, 30, .6, 4), 2.), .45, 1.)), .3, 1.3, .5)
def S_wave(): return _nrm(env(lp(noise(.5, 124), 260), 0, shape='swell'), .9)
def S_boltw(): return mix(_nrm(env(sine(200, 900, .4, 0.5, attack=.05), 0), .35), _nrm(env(crackle(.4, 120, 125, lo=1500), 0, shape='rise'), .5))
def S_bolth(): return reverb(mix(S_zap(), (sat(sine(90, 28, .5, 5), 2.), .02, 1.)), .2, 1., .3)
def S_chapter(): return reverb(mix(*[(bell(f, .9, .5), i * .14, 1.) for i, f in enumerate([523, 659, 784, 1047, 1319, 1568])]), .3, 1.2, .6)

BUILD = {}
for _k in range(8): BUILD[f'tick{_k}'] = (lambda k: (lambda: S_tick(k)))(_k)
for _v, _n in enumerate(['punch', 'punch2', 'punch3']): BUILD[_n] = (lambda v: (lambda: S_punch(v)))(_v)
for _v, _n in enumerate(['kick', 'kick2']): BUILD[_n] = (lambda v: (lambda: S_kick(v)))(_v)
for _v, _n in enumerate(['slash', 'slash2', 'slash3']): BUILD[_n] = (lambda v: (lambda: S_slash(v)))(_v)
for _v, _n in enumerate(['stab', 'stab2']): BUILD[_n] = (lambda v: (lambda: S_stab(v)))(_v)
BUILD.update(whoosh=lambda: S_whoosh(.17, 400, 3000, .8, 7), swing=lambda: S_whoosh(.22, 250, 1800, .6, 8), shing=S_shing, knife=S_knife, axe=S_axe, hammer=S_hammer, clang=S_clang, wood=S_wood, fire=S_fire, ice=S_ice, zap=S_zap,
             finish=S_finish, hurt=S_hurt, block=S_block, wrong=S_wrong, ultimate=S_ultimate, combo=S_combo, heal=S_heal, win=S_win, lose=S_lose, move=S_move, select=S_select, go=S_go, pause=S_pause, thud=S_thud, land=S_land, boss=S_boss,
             warn=S_warn, coin=S_coin, buy=S_buy, crash=S_crash, arrow=S_arrow, boom=S_boom, fuse=S_fuse, jump=S_jump, dodge=S_dodge, dash=S_dash, ach=S_ach, phase=S_phase, wave=S_wave, boltw=S_boltw, bolth=S_bolth, chapter=S_chapter)
BUILD['break'] = S_break
SOUND_NAMES = list(BUILD)
GAIN = {n: .8 for n in SOUND_NAMES}
GAIN.update(dict(punch=.85, punch2=.8, punch3=.9, kick=.9, kick2=.9, whoosh=.45, swing=.35, finish=1.0, hurt=.85, block=.65, wrong=.38, ultimate=.95, combo=.5, heal=.4, win=.65, lose=.6, move=.28, select=.42, go=.5, pause=.35, thud=.5,
                 land=.4, boss=.85, warn=.55, slash=.6, slash2=.6, slash3=.6, stab=.6, stab2=.6, shing=.65, knife=.55, axe=.9, hammer=1.0, clang=.7, wood=.6, fire=.65, ice=.5, zap=.65, coin=.35, buy=.5, crash=1.0, arrow=.45, boom=1.0, fuse=.25,
                 jump=.35, dodge=.45, dash=.4, ach=.55, phase=1.0, wave=.55, boltw=.45, bolth=.9, chapter=.7))
GAIN['break'] = .85
for _k in range(8): GAIN[f'tick{_k}'] = .26
def build_sounds(progress=None):
    out = {}
    for i, (name, fn) in enumerate(BUILD.items()):
        sig = fn(); out[name] = fade(sig); 
        if progress: progress(i + 1, len(BUILD), name)
    return out
