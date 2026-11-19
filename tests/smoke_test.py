"""Headless smoke test for TypeStrike (fake Tk, no display or sound card needed).
    python tests/smoke_test.py            quick run (about 1-2 minutes)
    python tests/smoke_test.py full       also plays every one of the 150 levels
"""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); GAME = os.path.join(ROOT, 'typestrike.py')
sys.path.insert(0, HERE); sys.path.insert(0, ROOT)
import mock_env as me, ts_data as KD, string
from types import SimpleNamespace as NS
E = me.load(GAME, 'win32', (1920, 1080)); M, g, D, root, T = E.M, E.g, E.D, E.root, E.T
key = lambda k, ch='': M['onkey'](NS(keysym=k, char=ch))
def frame(n=1):
    for _ in range(n): T[0] += .016; root.cb()
def play(mode, L=1, wpm=40, err=.03, maxf=40000, moves=False):
    random.seed(L * 31 + 7); M['begin'](mode, L); f = 0; bud = 0.; cps = wpm * 5 / 60; mt = 0
    while g.state not in ('done', 'fail') and f < maxf:
        frame(); f += 1
        if g.state == 'intro': key('Return')
        if g.state != 'play': continue
        if moves:
            mt -= 1
            if mt <= 0:
                mt = random.randint(20, 80); a = random.choice(['Left', 'Right', 'Up', 'Down', None])
                for k in ('Left', 'Right', 'Down'): M['onrelease'](NS(keysym=k))
                if a: key(a)
        bud += cps * .016
        while bud >= 1 and g.state == 'play':
            bud -= 1; al = M['alive'](); e = g.tg if (g.tg and not g.tg.dead and not g.tg.dying and g.tg.w) else None
            if e is None:
                c = [x for x in al if x.w and x.i < len(x.w)]; e = min(c, key=lambda x: (-x.i, abs(x.x - g.hero.x))) if c else None
            if e is None: break
            ch = e.w[e.i]; key('a', 'a' if ch != 'a' else 'b') if random.random() < err else key('space' if ch == ' ' else 'x', ch)
            if g.rage >= 100: key('Return')
    assert g.state in ('done', 'fail') or mode in ('surv', 'chal', 'rush'), f'{mode} {L} did not finish'
    return g.state
def main(full):
    # 1. curriculum: every lesson produces typeable text
    for L in range(1, 151):
        R = random.Random(L)
        for i in range(40):
            t = KD.gen(L, R, (), ['grunt', 'fast', 'tank'][i % 3]); assert t and all(c in string.printable and c not in '\t\n\r\x0b\x0c' for c in t), (L, t)
            if L <= 78 and KD.lesson(L)['mode'] != 'mixed': assert all(c in KD.allowed(L) for c in t), (L, t)
    print('curriculum ok (150 lessons)')
    # Bangla display fix (left-side vowel signs moved in front of their consonant)
    bv = M['bn_visual']; assert bv('\u0996\u09c7\u09b2\u09bf') == '\u09c7\u0996\u09bf\u09b2' and bv('\u0998\u09cb\u09dc\u09be')[:2] == '\u09c7\u0998' and bv('\u09ac\u0987') == '\u09ac\u0987'
    for sp in M['SPEEDS']: assert sp > 0
    print('bangla fix + speed ok')
    # Bangla display helper + speed setting
    assert M['bn_visual']('\u0996\u09c7\u09b2\u09bf') == '\u09c7\u0996\u09bf\u09b2'; assert M['bn_visual']('\u09ad\u09be\u09b2\u09cb') == '\u09ad\u09be\u09c7\u09b2\u09be'
    for _ in range(len(M['SPEEDS'])): key('F5'); frame(1)
    D['speed'] = 1.0; M['step_speed'](-1); assert D['speed'] < 1.0; M['step_speed'](2); assert D['speed'] > 1.0; D['speed'] = 1.0; print('bangla helper + speed ok')
    # typing tutor: type whole lessons (with a few mistakes) and check progress is saved
    for L in (1, 11, 31, 61, 111, 150):
        random.seed(L); M['begin_tutor'](L); assert g.state == 'tintro'; frame(2); key('Return'); assert g.state == 'tutor'; n = 0
        while g.state == 'tutor' and n < 6000:
            tu = g.tu; ex = tu.lines[tu.li][tu.ci]
            key('a', 'a' if ex != 'a' else 'b') if random.random() < .03 else key('space' if ex == ' ' else 'x', ex); n += 1
            if n % 9 == 0: frame(1)
        assert g.state == 'tdone' and g.tu.res['passed'], ('tutor', L)
    assert D['tutor_ul'] >= 2; print('typing tutor ok')
    # 2. screens
    for st in ('menu', 'map', 'ach', 'armory', 'stats'):
        g.state = st
        for tab in range(3): g.tab = tab; g.si = 1; frame(5)
    print('screens ok')
    # 3. campaign levels, including the old trouble spots 14-16
    D['unlocked'] = 150; D['coins'] = 10 ** 6
    for L in ((1, 5, 10, 14, 15, 16, 25, 50, 100, 150) if not full else range(1, 151)): print('level', L, play('camp', L, 45))
    # 4. every mode
    for mode, L in (('prac', 20), ('surv', 1), ('test', 1), ('chal', 1), ('daily', 0), ('bn', 1), ('bn', 12), ('weak', 1), ('custom', 1), ('rush', 1)): print(mode, play(mode, L, 40, maxf=4000 if mode in ('surv', 'chal', 'rush') else 30000))
    D['bn_native'] = True; print('bn native', play('bn', 3, 40)); D['bn_native'] = False
    for sd in range(6): random.seed(sd); assert play('weak', 1, 40, maxf=20000) in ('done', 'fail')
    print('weak-key trainer ok')
    print('movement', play('camp', 31, 40, moves=True))
    # 5. heroes x weapons
    D['own_heroes'] = list(M['HORDER']); D['owned'] = list(M['WORDER']); D['own_styles'] = list(M['SORDER'])
    for hk in M['HORDER']:
        for wk in M['WORDER']:
            D['hero'] = hk; D['weapon'] = wk; D['style'] = random.choice(M['SORDER']); M['begin']('prac', 11); key('Return'); frame(60)
            for _ in range(6):
                al = [e for e in M['alive']() if e.w]
                if al: key('x', al[0].w[al[0].i]); frame(3)
    print('all heroes and weapons ok')
    # 6. bosses and hazards
    M['begin']('camp', 100); key('Return'); frame(60)
    for bt in M['BOSSES']:
        g.en = []; g.haz = []; e = M['spawn'](True); e.bt = bt; e.x = 1500
        for ph in (False, True):
            e.ph2 = ph
            if ph: M['phase2'](e)
            for _ in range(6): M['boss_special'](e); frame(20)
        g.hero.hp = 100
    print('bosses ok\nALL OK')
if __name__ == '__main__': main(len(sys.argv) > 1 and sys.argv[1] == 'full')
