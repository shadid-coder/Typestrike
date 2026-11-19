"""Keyboard Warrior - curriculum (150 lessons), text generators, Bangla bank, daily themes."""
import random, re, string, unicodedata
from ts_words import WORDS

TOTAL = 150
LONG_MODES = ('sent', 'para', 'code', 'office')
WEAK = {'miss': {}, 'att': {}}          # filled in by the game (shared dicts)
UP = string.ascii_uppercase
CHAPTERS = ['Home Row Heroes', 'Word Warriors', 'Number Ninjas', 'Capital Commanders', 'Punctuation Pirates', 'Sentence Samurai', 'Rhythm Masters', 'Symbol Sorcerers',
            'Speed Demons', 'Accuracy Legends', 'Paragraph Paladins', 'Office Champions', 'Code Knights', 'Endurance Titans', 'Grandmaster Trials']
MODEDESC = dict(drill='Letter drills and short words', words='Type the words', frag='Word patterns and endings', nums='Number drills', caps='Capital letters with Shift', punc='Punctuation practice',
                sent='Type the sentences', sym='Symbols and special keys', weak='Your weakest keys', custom='Your own text',  code='Type real code', office='Office and email typing', mixed='Mixed mastery', para='Long lines - endurance', bn='Bangla typing')
GR = ['asdfjkl;', 'gh', 'ei', 'ro', 'tu', 'wy', 'qp', 'vn', 'bm', 'cxz']
# (first level, characters unlocked at that level)
ADD = [(1, ' asdfjkl'), (2, 'gh'), (3, 'ei'), (4, 'ro'), (5, 'tu'), (6, 'wy'), (7, 'qp'), (8, 'vn'), (9, 'bm'), (10, 'cxz'), (21, '123'), (22, '456'), (23, '7890'), (31, UP),
       (41, '.,'), (42, "'"), (43, '?!'), (44, '"'), (46, ';:'), (47, '-'), (48, '()'), (71, '@#'), (72, '$%'), (73, '&*'), (74, '_=+'), (76, '[]{}'), (77, '/\\|'), (78, '<>~^`')]
_AL = {}
def allowed(L):
    L = max(1, min(TOTAL, L))
    if L not in _AL: _AL[L] = frozenset(''.join(c for n, c in ADD if n <= L))
    return _AL[L]

V = dict(
    A='brave quiet swift clever old happy tiny bright calm gentle proud wise busy strong sleepy curious kind young golden silver lucky red blue green'.split(),
    N='tiger farmer student teacher river dragon mountain baker sailor dancer robot garden village bird cat dog child artist doctor pilot warrior monkey fisher traveler market lion horse'.split(),
    V='watches follows finds builds paints carries trains visits helps reads draws climbs cleans greets protects'.split(),
    V2='sings rests smiles waits works travels sleeps dreams wanders laughs'.split(), VP='walk run sing laugh jump wait rest travel smile work'.split(),
    VB='bring check clean send open close repair paint find read'.split(), VBP='visit like help follow watch meet'.split(),
    ADV='slowly quietly happily bravely softly quickly carefully gladly'.split(), PL='garden village market forest school river city library park harbor'.split(),
    NAME='Ana Ben Chloe Dan Emma Farid Grace Hasan Ivy Jack Kate Liam Mia Noor Omar Ruby Sam Tina Uma Zain Rafi Nila Tania Arif'.split(),
    DAY='Monday Tuesday Wednesday Thursday Friday Saturday Sunday'.split(), ADJP='quiet crowded empty warm cold ready late busy'.split(),
    HYP='well-known brand-new top-secret ice-cold long-term hard-working kind-hearted part-time high-speed one-way'.split(),
    DOC='report invoice letter plan menu schedule contract'.split(), DEPT='sales design support finance'.split(), MONTH='January March May June August October December'.split())
V['Ns'] = [n + 's' for n in V['N']]
def fill(t, R): return re.sub(r'\{(\w+)\}', lambda m: R.choice(V[m.group(1)]) if m.group(1) in V else m.group(0), t)
def _num(R, a, b): return str(R.randint(a, b))
T_SIMPLE = ['The {A} {N} {V} the {N}.', '{NAME} {V} a {A} {N}.', 'Every {N} {V2} in the {PL}.', '{NAME} and {NAME} {VP} near the {PL}.', 'A {A} {N} {V2} {ADV}.', 'Today the {N} {V} the {A} {N}.',
            'We {VBP} the {PL} {ADV}.', 'You can {VB} the {N} before {DAY}.', 'The {N} is {ADJP} today.', 'My {N} {V2} {ADV} every day.', 'Every {N} needs a {A} {PL}.']
T_COMMA = ['First, the {N} {V} the {N}, then the {N} {V2}.', '{NAME}, {NAME}, and {NAME} {VP} {ADV}.', 'When it rains, the {N} {V2} in the {PL}.', 'In the morning, {NAME} {V} the {A} {N}.', 'Yes, the {N} {V} the {A} {N}, and it is {ADJP}.']
T_APOS = ["{NAME}'s {N} {V} the {N}.", "Don't forget the {A} {N}.", "I can't find {NAME}'s {N}.", "We're {ADJP} because the {N} isn't {ADJP}.", "That's the {A} {N} I've seen.", "It's a {A} {N}, and it doesn't {VB} the {N}."]
T_QE = ['Where is the {A} {N}?', 'Who {V} the {N}?', 'Can you {VB} the {N}?', 'What a {A} {N}!', 'Watch out for the {A} {N}!', 'Is the {N} {ADJP}?', "Isn't the {N} {ADJP}?", 'Look, the {N} {V2}!', 'Do you {VBP} the {PL}?']
T_QUOTE = ['"I {VBP} the {N}," said {NAME}.', '"We {VP} {ADV}," said {NAME}.', '{NAME} said, "The {N} is {ADJP}."', '"Can you {VB} the {N}?" asked {NAME}.', '"The {A} {N} {V} the {N}!" shouted {NAME}.']
T_SEMI = ['The {N} {V2}; the {N} {V2}.', 'Remember this: the {A} {N} {V} the {N}.', '{NAME} {V} the {N}; {NAME} {V} the {A} {N}.', 'We need three things: a {N}, a {N}, and a {N}.', 'Note: the {PL} is {ADJP}.']
T_HYPH = ['This is a {HYP} {N}.', '{NAME} found a {HYP} {N}.', 'It was a {HYP} {PL}.']
T_PAREN = ['The {N} (a {A} one) {V} the {N}.', '{NAME} (age {n2}) {V} the {N}.', 'We {VBP} the {N} (and the {N}) {ADV}.', 'The {PL} (see page {n2}) is {ADJP}.']
T_LIST = ['We need {Ns}, {Ns}, and {Ns}.', 'Bring a {N}, a {N}, and a {N}.', 'There are {Ns}, {Ns}, {Ns}, and {Ns}.']
T_LONG = ['{NAME} said that the {A} {N} {V} the {N} because the {PL} was {ADJP}, and nobody wanted to {VB} the {A} {N} {ADV}.',
          'When the {A} {N} {V} the {N}, the whole {PL} became {ADJP}; {NAME} and {NAME} decided to {VB} the {N} before {DAY}.',
          'Every {DAY}, {NAME} {V} the {A} {N} near the {PL}, while {NAME} {V2} {ADV} and the {N} {V} the {A} {N}.']
T_OFFICE = ['Meeting at {t} on {DAY}, room {n3}.', 'Please send the {DOC} to {NAME} by {DAY}.', 'Invoice #{n4} totals ${n3}.{n2} (due {d}).', 'Dear {NAME}, thank you for your email of {d}.',
            'Our {DEPT} team grew by {n2}% in {MONTH} {y}.', 'Contact {name}@{co}.com about order #{n4}.', 'The {DOC} is due {DAY} at {t}; please reply to {name}@{co}.com.', 'Budget: ${n4} for {DEPT}, {n2}% approved.',
            'Call {NAME} at 555-{n4} before {t}.', 'Update: the {DOC} for {DEPT} moved to {d}.', 'Agenda: 1) {DEPT} review, 2) {DOC} approval, 3) questions.']
SENT_PROV = ['Practice makes perfect.', 'A journey of a thousand miles begins with a single step.', 'Actions speak louder than words.', 'Better late than never.', 'Slow and steady wins the race.',
             'Where there is a will, there is a way.', 'Rome was not built in a day.', 'Knowledge is power.', 'Time is money, so use it well.', 'Every expert was once a beginner.',
             'The early bird catches the worm.', 'Do not count your chickens before they hatch.', 'A friend in need is a friend indeed.', 'Many hands make light work.',
             'Fall seven times, stand up eight.', 'Patience is bitter, but its fruit is sweet.', 'Hard work beats talent when talent does not work hard.', 'The best time to start is now.',
             'Small steps every day lead to big results.', 'Accuracy first, speed will follow.', 'Mistakes are proof that you are trying.', 'Type with rhythm, not with panic.']
SENT_PAN = ['The quick brown fox jumps over the lazy dog.', 'Pack my box with five dozen liquor jugs.', 'How vexingly quick daft zebras jump!', 'Sphinx of black quartz, judge my vow.',
            'Jackdaws love my big sphinx of quartz.', 'The five boxing wizards jump quickly.', 'Waltz, bad nymph, for quick jigs vex.', 'Bright vixens jump; dozy fowl quack.']
SENT_LONG = ['Good typists keep their eyes on the screen, their wrists relaxed, and their fingers curved above the home row.',
             'Speed is a side effect of accuracy: type each key correctly, and the rhythm will build by itself over time.',
             'A calm mind, a straight back, and steady breathing help your fingers move faster than you would ever expect.',
             'Every lesson in this game is a small battle, and every clean word you type makes your hero a little stronger.',
             'Do not look down at the keyboard; trust your fingers, because they remember more than your eyes ever will.']
CODE = {'py': ['def add(a, b): return a + b', 'for i in range(10): print(i)', 'if x > 0 and y < 5:', 'names = ["Ann", "Bob", "Cy"]', 'print(f"Total: {total}")', 'import os, sys', 'class Hero: pass',
               'd = {"a": 1, "b": 2}', 'x = [i * 2 for i in range(5)]', 'while True: break', 'result = sum(nums) / len(nums)', 'with open("a.txt") as f: data = f.read()', 'return x if x else None'],
        'js': ['const sum = (a, b) => a + b;', 'console.log("Hello, world!");', 'let items = [1, 2, 3].map(n => n * 2);', 'if (x === 10 && y !== 5) { go(); }', 'document.getElementById("app").innerHTML = "";',
               'for (let i = 0; i < 10; i++) { total += i; }', 'const user = { name: "Sam", age: 20 };', 'fetch("/api/data").then(r => r.json());', 'function greet(n) { return `Hi ${n}`; }'],
        'html': ['<div class="box"><p>Hello</p></div>', '<a href="index.html">Home</a>', '<img src="a.png" alt="logo">', '<ul><li>One</li><li>Two</li></ul>', 'body { margin: 0; color: #333; }', '.btn:hover { background: #f90; }',
                 '<input type="text" id="name">', 'h1 { font-size: 2rem; text-align: center; }'],
        'sql': ['SELECT name, age FROM users WHERE age > 18;', 'INSERT INTO items (id, title) VALUES (1, "pen");', 'UPDATE users SET score = score + 10 WHERE id = 7;', 'DELETE FROM logs WHERE day < "2026-01-01";'],
        'sh': ['cd ~/projects && ls -la', 'git commit -m "Fix bug #12"', 'python3 main.py --level 5', 'mkdir -p src/assets && cd src', 'echo "done" > out.txt', 'pip install requests']}
def _wl(lo, hi, _c={}):
    k = (lo, hi)
    if k not in _c: _c[k] = [w for w in WORDS if lo <= len(w) <= hi]
    return _c[k]
def _wgt(R, pool, avoid=()):
    if not pool: return 'type'
    cand = [w for w in pool if w[0] not in avoid] or pool; m, a = WEAK['miss'], WEAK['att']
    ws = [1 + sum(4 * m.get(c, 0) / max(1, a.get(c, 1)) for c in set(w)) for w in cand]
    return R.choices(cand, ws)[0]
def _trim(s, hi): return s if len(s) <= hi else s[:hi].rsplit(' ', 1)[0]
def _ranged(f, R, lo, hi, tries=24):
    best = ''
    for _ in range(tries):
        s = f()
        if lo <= len(s) <= hi: return s
        if not best or abs(len(s) - (lo + hi) / 2) < abs(len(best) - (lo + hi) / 2): best = s
    return best
def _sent_pool(style, R, les):
    L = les['n']; ok = allowed(L)
    def one():
        t = {'simple': T_SIMPLE, 'comma': T_COMMA + T_SIMPLE, 'apos': T_APOS, 'qe': T_QE, 'quote': T_QUOTE, 'semi': T_SEMI, 'hyph': T_HYPH, 'paren': T_PAREN, 'list': T_LIST, 'long': T_LONG, 'all': T_SIMPLE + T_COMMA + T_QE + T_APOS + T_QUOTE + T_SEMI}[style]
        s = fill(R.choice(t), R).replace('{n2}', _num(R, 10, 99)); s = s.replace('{n2}', _num(R, 10, 99))
        return s
    for _ in range(40):
        s = one()
        if all(c in ok for c in s): return s
    return 'The quick brown fox jumps.'
def _any_sentence(R, lo, hi, les):
    L = les['n']
    def f():
        k = R.random()
        if hi > 90: return ' '.join(fill(R.choice(T_SIMPLE + T_COMMA), R) for _ in range(R.randint(2, 3))) if k < .5 else R.choice(T_LONG + SENT_LONG)
        if k < .25: return R.choice(SENT_PROV + SENT_PAN)
        return fill(R.choice(T_SIMPLE + T_COMMA + T_QE + T_APOS + T_QUOTE + T_SEMI + (T_LONG if hi > 60 else [])), R).replace('{n2}', '42')
    return fill(_ranged(f, R, lo, hi), R)
def _tok(R, style):
    nm = R.choice(['sam', 'anna', 'tom', 'rafi', 'nila', 'max', 'lina', 'zed']); w = R.choice(WORDS[::7]); dom = R.choice(['mail', 'site', 'corp', 'game', 'school'])
    if style == 'email': return f'{nm}@{dom}.{R.choice(["com", "net", "org", "edu"])}'
    if style == 'hash': return '#' + w + ((' #' + R.choice(WORDS[::11])) if R.random() < .5 else '')
    if style == 'money': return '$%d.%02d' % (R.randint(1, 999), R.randint(0, 99)) if R.random() < .6 else '$%d,%03d' % (R.randint(1, 99), R.randint(0, 999))
    if style == 'pct': return '%d%% of %s' % (R.randint(5, 99), w)
    if style == 'amp': return R.choice(['Tom & Jerry', 'R&D', 'salt & pepper', 'rock & roll', 'Q&A', '5 * 4 = 20', 'a * b', '2 * (3 + 4)'])
    if style == 'math': a, b, c = R.randint(2, 9), R.randint(2, 9), R.randint(2, 9); return R.choice([f'({a} + {b}) * {c} = {(a + b) * c}', f'{a} * {b} = {a * b}', f'x = {a} + {b} - {c}', f'{a}_{b} + {c}'])
    if style == 'user': return f'{nm}_{w}_{R.randint(1, 99)}'
    if style == 'pass': return ''.join(R.choice(string.ascii_letters + string.digits + '!@#$%&*_=+-') for _ in range(R.randint(8, 12)))
    if style == 'brackets': return R.choice([f'[{R.randint(1, 9)}, {R.randint(1, 9)}, {R.randint(1, 9)}]', '{name: "%s"}' % nm, f'[{w}] {{{nm}}}', f'items[{R.randint(0, 9)}] = {{{w}}}'])
    if style == 'slash': return R.choice(['and/or', f'{R.randint(1, 28)}/{R.randint(1, 12)}/2026', 'C:\\Users\\' + nm, 'a | b', f'/home/{nm}/{w}', 'yes/no', 'path\\to\\file'])
    if style == 'misc': return R.choice(['<tag>', 'x ^ 2', '~/docs', '`code`', '<div>', 'a < b > c', '5 > 3', f'~{nm}', 'x^2 + y^2'])
    if style == 'url': return f'https://www.{dom}.com/{w}?id={R.randint(1, 99)}'
    return _tok(R, R.choice(['email', 'hash', 'money', 'pct', 'amp', 'math', 'user', 'pass', 'brackets', 'slash', 'misc', 'url']))
def _bn_native(): return False
def _weak(R, lo, hi):
    a, m_ = WEAK['att'], WEAK['miss']
    ks = sorted((k for k in a if k.isalpha() and k.islower() and a[k] >= 3 and m_.get(k, 0) > 0), key=lambda k: -m_.get(k, 0) / a[k])[:5]
    if len(ks) < 3: ks = list('etaoin')
    ws = [w for w in WORDS if lo <= len(w) <= hi and sum(w.count(k) for k in ks) >= 2] or _wl(lo, hi)
    ws = sorted(ws, key=lambda w: -sum(w.count(k) for k in ks))[:60]; w1 = R.choice(ws)
    return w1 if R.random() < .6 else w1 + ' ' + R.choice(ws)
def gen(L, R, avoid=(), kind='grunt'):
    """text for one enemy at lesson L"""
    les = lesson(L); L = les['n']; m = les['mode']; lo, hi = les['lo'], les['hi']; st = les.get('style', '')
    if m == 'weak': return _weak(R, lo, hi)
    if m == 'mixed':
        pool = [n for n in range(11, max(12, L)) if LS_[n]['mode'] != 'mixed' and not LS_[n].get('boss')]; return gen(R.choice(pool), R, avoid, kind)
    if m == 'drill':
        A_ = allowed(L) - {' '}; base = [w for w in WORDS if lo <= len(w) <= hi and set(w) <= A_]; nk = set(les['new'])
        if kind == 'fast': base = [w for w in base if len(w) <= 4] or base
        if len(base) < 12:
            k = sorted(A_); base += [''.join(R.choice(k) for _ in range(R.randint(lo, hi))) for _ in range(30)]
        pri = [w for w in base if nk & set(w)] or base
        return _wgt(R, pri if R.random() < .75 else base, avoid)
    if m == 'words':
        a, b = (3, min(hi, 4)) if kind == 'fast' else (min(hi, lo + 1), min(13, hi + 2)) if kind == 'tank' else (lo, hi)
        return _wgt(R, _wl(a, b) or _wl(3, 5), avoid)
    if m == 'frag':
        fr = les['frag']; pool = [w for w in WORDS if lo <= len(w) <= hi + 3 and any(f in w for f in fr)]
        if len(pool) < 8: pool += [R.choice(WORDS[::5])[:3] + R.choice(fr) for _ in range(20)]
        return _wgt(R, pool, avoid)
    if m == 'nums':
        dg = les.get('dg', '0123456789'); 
        if st == 'phone': return ' '.join([_num(R, 100, 999), _num(R, 1000, 9999)] + ([_num(R, 1000, 9999)] if R.random() < .4 else []))
        if st == 'date': return f'{R.randint(1, 28)} {R.choice(["jan", "feb", "mar", "may", "jun", "aug", "oct", "dec"])} {R.randint(1950, 2030)}'
        if st == 'count': return f'{R.randint(2, 99)} {R.choice(V["A"][:7])} {R.choice(V["Ns"])}'
        if st == 'mix' and R.random() < .5: return R.choice(WORDS[::9])[:5] + ' ' + ''.join(R.choice(dg) for _ in range(R.randint(2, 3)))
        return ''.join(R.choice(dg) for _ in range(R.randint(lo, hi)))
    if m == 'caps':
        if st in ('L', 'R'):
            s = 'qwertasdfgzxcvb' if st == 'L' else 'yuiophjklnm'; w = _wgt(R, [w for w in WORDS if w[0] in s and 3 <= len(w) <= 7], avoid); return w.capitalize()
        if st == 'names': return R.choice(V['NAME'] + ['Alvee', 'Imon', 'Shadid', 'Karim', 'Rahim', 'Fatima', 'Ayesha', 'Leo', 'Peter', 'Quinn', 'Victor', 'Wendy', 'Xavier', 'Yara'])
        if st == 'places': return R.choice(['Dhaka', 'Sylhet', 'Khulna', 'Rajshahi', 'Barisal', 'Rangpur', 'Comilla', 'Paris', 'London', 'Tokyo', 'Cairo', 'Rome', 'Delhi', 'Dubai', 'Berlin', 'Madrid', 'Sydney', 'Toronto', 'Lisbon', 'Oslo', 'Seoul', 'Lima', 'Nepal', 'Japan', 'Brazil', 'Kenya', 'Spain'])
        if st == 'title': return ' '.join(w.capitalize() for w in [R.choice(V['A']), R.choice(V['N'])] + ([R.choice(V['PL'])] if R.random() < .5 else []))
        if st == 'allcaps': return _wgt(R, _wl(3, 7), avoid).upper()
        if st == 'cs': return _ranged(lambda: fill(R.choice(T_SIMPLE), R).rstrip('.'), R, lo, hi)
        return gen(R.choice([31, 32, 33, 36]) if L > 34 else 31, R, avoid, kind)
    if m == 'punc':
        return _ranged(lambda: _sent_pool(st, R, les), R, lo, hi)
    if m == 'sent':
        if les.get('pool') == 'prov': return R.choice(SENT_PROV)
        if les.get('pool') == 'pan': return R.choice(SENT_PAN)
        return _any_sentence(R, lo, hi, les) if not st else _ranged(lambda: _sent_pool(st, R, les), R, lo, hi)
    if m == 'para': return _any_sentence(R, lo, hi, les)
    if m == 'sym':
        ok = allowed(L)
        for _ in range(30):
            s = _tok(R, st or 'soup')
            if les.get('two'): s += ' ' + _tok(R, st or 'soup')
            if all(c in ok for c in s): return s
        return 'a@b.com'
    if m == 'code':
        lang = st or R.choice(list(CODE)); return _ranged(lambda: R.choice(CODE[lang if lang in CODE else R.choice(list(CODE))]), R, lo, hi)
    if m == 'office':
        return _ranged(lambda: fill(R.choice(T_OFFICE), R).replace('{t}', f'{R.randint(1, 12)}:{R.choice(["00", "15", "30", "45"])}').replace('{n2}', _num(R, 10, 99)).replace('{n3}', _num(R, 100, 999)).replace('{n4}', _num(R, 1000, 9999)).replace('{d}', f'{R.randint(1, 28)}/{R.randint(1, 12)}/2026').replace('{y}', '2026').replace('{name}', R.choice(['sam', 'nila', 'rafi', 'anna'])).replace('{co}', R.choice(['corp', 'mail', 'work'])), R, lo, hi)
    return 'type fast'
def boss_text(L, R):
    les = lesson(L); L = les['n']; m = les['mode']
    if m in ('words', 'drill', 'frag', 'nums', 'caps') or (m == 'mixed' and les['hi'] < 20): n = 2 if L < 30 else 3; s = ' '.join(gen(L, R, (), 'grunt') for _ in range(n)); return _trim(s, 40)
    return _trim(gen(L, R, (), 'grunt'), max(30, min(70, les['hi'])))

# ---------------------------------------------------------------- lesson table
LS_ = {}
def _add(n, title, mode, lo, hi, text, new='', **kw):
    d = dict(n=n, title=title, mode=mode, lo=lo, hi=hi, text=text, new=new, boss=False, spd=1.0, strict=False, ch=(n - 1) // 10); d.update(kw); LS_[n] = d
TXT1 = ['Rest your fingers on the home row: A S D F on the left, J K L ; on the right. Feel the bumps on F and J - they guide your index fingers. Thumbs hover over Space.',
        'Your index fingers also reach G and H. Stretch the finger, press, then bring it straight back home.', 'E and I belong to the middle fingers. Keep the other fingers resting on the home row.',
        'R is the left index finger, O is the right ring finger. Move only the finger that types.', 'T and U: both index fingers reach up and inward. Keep your wrists still.',
        'W is the left ring finger, Y is the right index finger. Say each letter softly as you type it.', 'Q and P belong to the pinkies. Pinkies are weak - go slowly and stay accurate.',
        'V and N: index fingers reach down. Curve your fingers, do not flatten them.', 'B and M: index fingers again, reaching down and inward. Almost there!', 'C, X and Z finish the alphabet: C middle, X ring, Z pinky. You now know every letter!']
T1 = ['Home Row: A S D F J K L ;', 'Index Reach: G H', 'Middle Fingers: E I', 'R and O', 'T and U', 'W and Y', 'Pinkies: Q and P', 'Reach Down: V and N', 'B and M', 'Bottom Row: C X Z']
for i in range(10): _add(i + 1, T1[i], 'drill', 3, 4 + (i + 1) // 3, TXT1[i], new=GR[i], boss=False)
def _chap(start, rows, tip=None):
    for i, r in enumerate(rows):
        n = start + i; title, mode, lo, hi, text = r[:5]; kw = dict(r[5]) if len(r) > 5 else {}
        _add(n, title, mode, lo, hi, text, **kw)
_chap(11, [('Full Alphabet', 'words', 3, 5, 'Every letter is yours now. Eyes on the screen, not on the keys.'), ('Everyday Words', 'words', 4, 6, 'Common words appear in everything you write. Find a steady rhythm: one key per beat.'),
           ('Quick Short Words', 'words', 3, 4, 'Short words train speed. Never rush at the cost of mistakes.', dict(spd=1.1)), ('Longer Words', 'words', 5, 8, 'Long words teach your fingers to flow from key to key.'),
           ('BOSS: Word Marathon', 'words', 5, 9, 'Boss fight! Breathe, relax your shoulders and type the phrase calmly.', dict(boss=True)),
           ('Letter Pairs: th he in er an', 'frag', 3, 6, 'Some pairs show up constantly. Train them until they feel like one motion.', dict(frag=['th', 'he', 'in', 'er', 'an'])),
           ('Endings: ing ed er ly', 'frag', 4, 8, 'Word endings are easy speed: lock them into muscle memory.', dict(frag=['ing', 'ed', 'er', 'ly'])),
           ('Double Letters', 'frag', 3, 7, 'Press the same key twice, evenly. Do not hurry the second press.', dict(frag=['ll', 'ee', 'ss', 'oo', 'tt', 'ff', 'pp'])),
           ('Tricky Clusters', 'frag', 4, 8, 'Clusters like tion, ight and ough look odd but are typed the same way every time.', dict(frag=['tion', 'ight', 'ough', 'ound', 'ould'])),
           ('BOSS: Word Gauntlet', 'words', 4, 9, 'Boss fight! A mix of everything from this chapter.', dict(boss=True))])
_chap(21, [('Numbers 1 2 3', 'nums', 2, 4, 'Reach up from the home row: 1 pinky, 2 ring, 3 middle. Return home after every digit.', dict(new='123', dg='123', style='mix')),
           ('Numbers 4 5 6', 'nums', 2, 4, '4 and 5 are the left index finger, 6 is the right index finger. Keep your hand still.', dict(new='456', dg='123456', style='mix')),
           ('Numbers 7 8 9 0', 'nums', 2, 4, '7 right index, 8 middle, 9 ring, 0 pinky.', dict(new='7890', dg='0123456789', style='mix')),
           ('Whole Number Row', 'nums', 3, 6, 'Now the full number row. Do not look - feel the distance from the home row.', dict(style='rand')),
           ('BOSS: Number Crunch', 'nums', 4, 7, 'Boss fight! Long numbers need patience.', dict(boss=True)), ('Phone Numbers', 'nums', 7, 14, 'Group digits in chunks, like a rhythm: 555 - 0142.', dict(style='phone')),
           ('Years and Dates', 'nums', 8, 14, 'Dates mix numbers and short words. Switch smoothly between them.', dict(style='date')), ('Counting Things', 'nums', 6, 16, 'Numbers with words: 12 red apples.', dict(style='count')),
           ('Number Sprint', 'nums', 4, 8, 'Fast digits! Keep your accuracy above 90%.', dict(style='rand', spd=1.1)), ('BOSS: Number Master', 'nums', 4, 9, 'Boss fight! Numbers, dates and phone numbers together.', dict(boss=True, style='rand'))])
_chap(31, [('Shift: Left-Hand Letters', 'caps', 3, 7, 'To capitalize a left-hand letter use the RIGHT Shift key (pinky). Hold Shift, tap the letter, release.', dict(style='L')),
           ('Shift: Right-Hand Letters', 'caps', 3, 7, 'For right-hand letters, use the LEFT Shift key. Opposite hands make it easy.', dict(style='R')), ('Names', 'caps', 3, 8, 'Names always start with a capital letter.', dict(style='names')),
           ('Two-Word Titles', 'caps', 6, 20, 'Titles capitalize each word. Shift, letter, release - repeat.', dict(style='title')), ('BOSS: Capital Chaos', 'caps', 5, 20, 'Boss fight! Capitals everywhere.', dict(boss=True, style='mix')),
           ('Places', 'caps', 4, 9, 'Cities and countries need capitals too.', dict(style='places')), ('ALL CAPS', 'caps', 3, 7, 'Hold Shift for the whole word, release after the last letter.', dict(style='allcaps')),
           ('Title Case', 'caps', 8, 26, 'Three or four capitalized words in a row.', dict(style='title')), ('Sentences with Capitals', 'caps', 14, 34, 'A sentence starts with a capital letter. No punctuation yet.', dict(style='cs')),
           ('BOSS: Capital Master', 'caps', 6, 30, 'Boss fight! Show your Shift skills.', dict(boss=True, style='mix'))])
_chap(41, [('Period and Comma', 'punc', 16, 44, 'The comma and period are on the right hand: middle finger and ring finger on the bottom row.', dict(style='comma', new='.,')), ("Apostrophes", 'punc', 14, 40, "The apostrophe is next to Enter - use the right pinky. It makes contractions: don't, can't.", dict(style='apos', new="'")),
           ('Questions and Shouts', 'punc', 12, 34, 'Question mark and exclamation need Shift. Use the opposite pinky!', dict(style='qe', new='?!')), ('Quotation Marks', 'punc', 20, 48, 'Quotes are Shift + apostrophe. Open and close every pair.', dict(style='quote', new='"')),
           ('BOSS: Punctuation Mix', 'punc', 18, 44, 'Boss fight! Commas, quotes and question marks.', dict(boss=True, style='all')), ('Colon and Semicolon', 'punc', 18, 48, 'Semicolon is on the home row. Colon is Shift + semicolon.', dict(style='semi', new=';:')),
           ('Hyphens', 'punc', 16, 40, 'The hyphen is the right pinky reaching up-right. Take it slowly.', dict(style='hyph', new='-')), ('Parentheses', 'punc', 20, 48, 'Parentheses are Shift + 9 and Shift + 0.', dict(style='paren', new='()')),
           ('Lists', 'punc', 20, 50, 'Commas in lists: apples, pears, and plums.', dict(style='list')), ('BOSS: Punctuation Master', 'punc', 20, 50, 'Boss fight! Every punctuation mark you know.', dict(boss=True, style='all'))])
SENT_TIPS = ['Type the sentence as one flowing line. Do not stop at spaces.', 'Space is typed with the thumb. Use whichever thumb feels natural, but always the same one.', 'Look ahead one word while your fingers finish the last one.',
             'Keep your wrists floating and relaxed. Tension makes you slower.', 'Read a few words ahead. Your eyes lead, your fingers follow.', 'Aim for a steady pace: a smooth 30 WPM beats a shaky 40.']
_chap(51, [('Short Sentences I', 'sent', 14, 24, SENT_TIPS[0], dict(style='simple')), ('Short Sentences II', 'sent', 18, 30, SENT_TIPS[1], dict(style='simple')), ('Short Sentences III', 'sent', 22, 36, SENT_TIPS[2], dict(style='comma')),
           ('Short Sentences IV', 'sent', 26, 40, SENT_TIPS[3], dict(style='all')), ('BOSS: Sentence Duel', 'sent', 28, 44, 'Boss fight! A full sentence for every phase.', dict(boss=True)),
           ('Medium Sentences I', 'sent', 30, 46, SENT_TIPS[4], dict()), ('Medium Sentences II', 'sent', 34, 50, SENT_TIPS[5], dict()), ('Medium Sentences III', 'sent', 38, 54, SENT_TIPS[0], dict()),
           ('Medium Sentences IV', 'sent', 40, 58, SENT_TIPS[2], dict()), ('BOSS: Samurai Challenge', 'sent', 36, 56, 'Boss fight! Stay calm and keep the rhythm.', dict(boss=True))])
_chap(61, [('Proverbs', 'sent', 20, 60, 'Old wisdom is great practice text: short, rhythmic and meaningful.', dict(style='', pool='prov')), ('Pangrams', 'sent', 30, 60, 'A pangram uses every letter of the alphabet. Perfect for a full workout.', dict(pool='pan')),
           ('Flowing Text I', 'sent', 44, 60, 'Let the sentences flow like water. Do not tense up.', dict()), ('Flowing Text II', 'sent', 46, 64, 'Rhythm matters more than raw speed.', dict()), ('BOSS: Rhythm Lord', 'sent', 44, 64, 'Boss fight! Keep a drum-beat rhythm.', dict(boss=True)),
           ('Longer Lines I', 'sent', 50, 70, 'Longer lines test your focus.', dict()), ('Longer Lines II', 'sent', 54, 74, 'Stay relaxed, keep your eyes ahead.', dict()), ('Longer Lines III', 'sent', 56, 78, 'Quality first.', dict()),
           ('Longer Lines IV', 'sent', 58, 80, 'You are building real endurance now.', dict()), ('BOSS: Master of Rhythm', 'sent', 56, 80, 'Boss fight! Long phrases, steady hands.', dict(boss=True))])
_chap(71, [('At and Hash: @ #', 'sym', 6, 30, 'Both are Shift + number: @ is Shift 2, # is Shift 3. Use the opposite-hand Shift.', dict(style='email', new='@#')), ('Hashtags', 'sym', 6, 30, 'Hashtags: #word. Shift + 3, then a word.', dict(style='hash')),
           ('Money and Percent: $ %', 'sym', 5, 30, '$ is Shift 4, % is Shift 5. Left hand digits - use the right Shift.', dict(style='money', new='$%')), ('Percent Facts', 'sym', 8, 30, 'Percentages in sentences.', dict(style='pct')),
           ('BOSS: Symbol Duel', 'sym', 6, 30, 'Boss fight! Emails, hashtags and money.', dict(boss=True, style='soup')), ('Ampersand and Star: & *', 'sym', 5, 30, '& is Shift 7, * is Shift 8.', dict(style='amp', new='&*')),
           ('Math Lines', 'sym', 6, 30, 'Minus, equals and plus: - = +.', dict(style='math', new='_=+')), ('Usernames and Passwords', 'sym', 8, 14, 'Underscores need Shift + hyphen. Passwords mix everything.', dict(style='user')),
           ('Brackets: [ ] { }', 'sym', 6, 30, 'Brackets are right pinky territory. Curly braces need Shift.', dict(style='brackets', new='[]{}')), ('BOSS: Bracket King', 'sym', 6, 30, 'Boss fight! Brackets, math and symbols.', dict(boss=True, style='soup'))])
_chap(81, [('Slashes: / \\ |', 'sym', 6, 30, 'Slash is right-hand bottom row. Backslash and pipe live above Enter.', dict(style='slash', new='/\\|')), ('Angles: < > ~ ^ `', 'sym', 5, 30, 'Angle brackets are Shift + comma and period.', dict(style='misc', new='<>~^`')),
           ('URLs', 'sym', 20, 40, 'Web addresses mix letters, slashes and numbers.', dict(style='url')), ('Symbol Soup', 'sym', 8, 40, 'Everything mixed together!', dict(style='soup')), ('BOSS: Symbol Sorcerer', 'sym', 8, 40, 'Boss fight! The whole symbol set.', dict(boss=True, style='soup', two=True)),
           ('Speed Words I', 'words', 3, 5, 'Speed round! The enemies move faster. Stay accurate!', dict(spd=1.25)), ('Speed Words II', 'words', 4, 7, 'Fast and clean. Do not let mistakes pile up.', dict(spd=1.3)),
           ('Speed Sentences I', 'sent', 20, 40, 'Short sentences at high speed.', dict(spd=1.25)), ('Speed Sentences II', 'sent', 30, 50, 'Keep calm under pressure.', dict(spd=1.3)), ('BOSS: Speed Demon', 'sent', 26, 46, 'Boss fight! This one is quick.', dict(boss=True, spd=1.3))])
_chap(91, [('Careful Words', 'words', 6, 10, 'Accuracy training: every mistake costs you HP. Slow down to speed up.', dict(strict=True)), ('Careful Numbers', 'nums', 5, 9, 'Zero tolerance for wrong digits.', dict(strict=True, style='rand')),
           ('Careful Capitals', 'caps', 6, 30, 'Capitals are easy to get wrong. Be deliberate.', dict(strict=True, style='mix')), ('Careful Punctuation', 'punc', 20, 50, 'Every comma matters.', dict(strict=True, style='all')),
           ('BOSS: Accuracy Duel', 'sent', 30, 56, 'Boss fight! Mistakes hurt more here.', dict(boss=True, strict=True)), ('Careful Symbols', 'sym', 8, 40, 'Symbols are easy to mix up. Take your time.', dict(strict=True, style='soup')),
           ('Careful Sentences', 'sent', 40, 70, 'Long and clean.', dict(strict=True)), ('Careful Mix I', 'mixed', 8, 50, 'A bit of everything you learned.', dict(strict=True)),
           ('Careful Mix II', 'mixed', 8, 60, 'Stay sharp.', dict(strict=True)), ('FINAL BOSS: The Century Colossus', 'mixed', 10, 56, 'The first great trial. Everything you have learned, in one fight.', dict(boss=True, strict=True))])
_chap(101, [('Paragraph Lines I', 'para', 70, 100, 'Longer lines now. Keep your breathing slow and your shoulders relaxed.', dict()), ('Paragraph Lines II', 'para', 74, 104, 'Look ahead and keep moving.', dict()),
            ('Paragraph Lines III', 'para', 80, 110, 'Do not stop at the end of a word - flow into the next.', dict()), ('Paragraph Lines IV', 'para', 84, 114, 'Endurance builds speed.', dict()),
            ('BOSS: Paragraph Paladin', 'para', 70, 100, 'Boss fight! Long phrases for every phase.', dict(boss=True)), ('Quotes and Wisdom I', 'para', 70, 110, 'Longer wise lines.', dict()), ('Quotes and Wisdom II', 'para', 74, 114, 'Keep calm.', dict()),
            ('Quotes and Wisdom III', 'para', 80, 118, 'Keep going.', dict()), ('Quotes and Wisdom IV', 'para', 84, 120, 'Almost a chapter done.', dict()), ('BOSS: Paladin King', 'para', 76, 110, 'Boss fight!', dict(boss=True))])
_chap(111, [('Office Basics I', 'office', 24, 44, 'Real-life typing: meetings, invoices, emails.', dict()), ('Office Basics II', 'office', 26, 48, 'Numbers inside sentences.', dict()), ('Emails', 'office', 28, 52, 'Email addresses are full of symbols.', dict()),
            ('Invoices and Dates', 'office', 28, 52, 'Dates, dollar signs and hash marks.', dict()), ('BOSS: Boss of the Office', 'office', 30, 56, 'Boss fight!', dict(boss=True)), ('Business Sentences I', 'sent', 50, 80, 'Professional writing.', dict()),
            ('Business Sentences II', 'sent', 54, 84, 'Stay steady.', dict()), ('Office Mix I', 'office', 34, 60, 'Mixed office tasks.', dict(spd=1.1)), ('Office Mix II', 'mixed', 10, 60, 'Everything mixed.', dict(spd=1.1)), ('BOSS: CEO Showdown', 'office', 34, 60, 'Boss fight!', dict(boss=True, spd=1.1))])
_chap(121, [('Python Lines', 'code', 14, 40, 'Code is full of symbols. Take your time with brackets and quotes.', dict(style='py')), ('JavaScript Lines', 'code', 20, 50, 'Arrows, braces and semicolons.', dict(style='js')), ('HTML and CSS', 'code', 20, 42, 'Angle brackets and quotes.', dict(style='html')),
            ('SQL and Shell', 'code', 20, 52, 'Commands in capitals.', dict(style='sql')), ('BOSS: Bug Boss', 'code', 20, 50, 'Boss fight! Squash the bug.', dict(boss=True, style='')), ('Python Mix', 'code', 24, 60, 'Longer Python.', dict(style='py')),
            ('JS Mix', 'code', 28, 60, 'Longer JavaScript.', dict(style='js')), ('Shell Mix', 'code', 18, 40, 'Command lines.', dict(style='sh')), ('Code Mix', 'code', 20, 60, 'All languages.', dict(style='')), ('BOSS: Code Knight', 'code', 20, 60, 'Boss fight!', dict(boss=True, style=''))])
_chap(131, [('Endurance I', 'para', 70, 110, 'Endurance: more enemies on screen. Stay calm.', dict(ma=3, nmul=1.5)), ('Endurance II', 'mixed', 10, 70, 'Mixed content, longer fight.', dict(ma=3, nmul=1.5)), ('Endurance III', 'para', 80, 116, 'Keep your rhythm.', dict(ma=3, nmul=1.5)),
            ('Endurance IV', 'mixed', 10, 70, 'Everything again.', dict(ma=3, nmul=1.5)), ('BOSS: Titan I', 'para', 76, 110, 'Boss fight!', dict(boss=True, ma=3)), ('Endurance V', 'para', 84, 120, 'Long lines, long fight.', dict(ma=3, nmul=1.6)),
            ('Endurance VI', 'mixed', 10, 70, 'Mixed again.', dict(ma=3, nmul=1.6)), ('Endurance VII', 'para', 90, 124, 'Nearly there.', dict(ma=3, nmul=1.6)), ('Endurance VIII', 'mixed', 10, 70, 'Last warm-up.', dict(ma=3, nmul=1.6)),
            ('BOSS: Titan II', 'mixed', 10, 70, 'Boss fight!', dict(boss=True, ma=3))])
_chap(141, [('Grandmaster I', 'mixed', 10, 70, 'Top speed, everything mixed. Show what you learned!', dict(spd=1.2, ma=3)), ('Grandmaster II', 'mixed', 10, 70, 'Fast.', dict(spd=1.25, ma=3)), ('Grandmaster III', 'para', 80, 120, 'Fast long lines.', dict(spd=1.2, ma=3)),
            ('Grandmaster IV', 'mixed', 10, 70, 'Faster.', dict(spd=1.3, ma=3)), ('BOSS: Grandmaster Duel', 'mixed', 10, 70, 'Boss fight!', dict(boss=True, spd=1.2, ma=3)), ('Grandmaster VI', 'mixed', 10, 70, 'Never stop.', dict(spd=1.3, ma=3)),
            ('Grandmaster VII', 'para', 90, 124, 'Concentrate.', dict(spd=1.3, ma=3)), ('Grandmaster VIII', 'mixed', 10, 70, 'Almost the end.', dict(spd=1.35, ma=3)), ('Grandmaster IX', 'mixed', 10, 70, 'The last climb.', dict(spd=1.35, ma=3)),
            ('FINAL BOSS: The Dragon Emperor', 'mixed', 10, 70, 'The ultimate trial. Everything you have ever learned.', dict(boss=True, spd=1.3, ma=3))])
BOSS_ORDER = ['brute', 'ninja', 'samurai', 'frost', 'thunder', 'twin', 'golem']
for n, d in LS_.items():
    if d['boss']: d['bt'] = 'dragon' if n % 50 == 0 or n == 150 else BOSS_ORDER[(n // 5 - 1) % len(BOSS_ORDER)]
def lesson(L): return L if isinstance(L, dict) else LS_[max(1, min(TOTAL, L))]
def info(L): d = lesson(L); return d['title'], d['new'], d['mode'], d['lo'], d['hi']
def tgt_wpm(L): return int(min(60, 8 + L * .34))
def enemies(L):
    d = lesson(L); L = d['n']; m = d['mode']; n = {'drill': 5 + min(L, 6), 'words': 8, 'frag': 8, 'nums': 8, 'caps': 8, 'punc': 7, 'sent': 5, 'sym': 6, 'code': 6, 'office': 5, 'mixed': 6, 'para': 4}[m]
    if d['hi'] > 90: n = 4
    return max(3, int(n * d.get('nmul', 1)) + L // 50) - (3 if d['boss'] else 0)
def samples(L, k=3):
    R = random.Random(L * 7 + 1); d = lesson(L); return [boss_text(L, R) if d['boss'] and i == 0 else gen(L, R) for i in range(k)]

# ---------------------------------------------------------------- Bangla bank: (bangla, phonetic, tier)
BN = [
 [('মা', 'ma'), ('বাবা', 'baba'), ('ভাই', 'bhai'), ('আমি', 'ami'), ('তুমি', 'tumi'), ('সে', 'se'), ('কে', 'ke'), ('না', 'na'), ('ফুল', 'phul'), ('গান', 'gan'), ('জল', 'jol'), ('ভাত', 'bhat'), ('দেশ', 'desh'), ('ঘর', 'ghor'), ('এক', 'ek'), ('দুই', 'dui'), ('তিন', 'tin'), ('চার', 'char'), ('সাত', 'sat'), ('আট', 'at'), ('দশ', 'dosh')],
 [('গাছ', 'gachh'), ('পাখি', 'pakhi'), ('আকাশ', 'akash'), ('তারা', 'tara'), ('মেঘ', 'megh'), ('লাল', 'lal'), ('কালো', 'kalo'), ('সাদা', 'shada'), ('সবুজ', 'sobuj'), ('হলুদ', 'holud'), ('কলম', 'kolom'), ('বই', 'boi'), ('খাতা', 'khata'), ('স্কুল', 'skul'), ('বন্ধু', 'bondhu'), ('নাম', 'nam'), ('দাদা', 'dada'), ('নানা', 'nana'), ('মামা', 'mama'), ('চাচা', 'chacha'), ('খালা', 'khala')],
 [('বাজার', 'bajar'), ('দোকান', 'dokan'), ('রাস্তা', 'rasta'), ('নদী', 'nodi'), ('পাহাড়', 'pahar'), ('সাগর', 'sagor'), ('শহর', 'shohor'), ('গ্রাম', 'gram'), ('মাঠ', 'math'), ('আলো', 'alo'), ('রাত', 'rat'), ('দিন', 'din'), ('সকাল', 'shokal'), ('দুপুর', 'dupur'), ('বিকাল', 'bikal'), ('ডাক্তার', 'daktar'), ('শিক্ষক', 'shikkhok'), ('ছাত্র', 'chhatro'), ('সূর্য', 'surjo'), ('বাতাস', 'batash'), ('আগুন', 'agun')],
 [('রুটি', 'ruti'), ('মাছ', 'machh'), ('মাংস', 'mangsho'), ('ডিম', 'dim'), ('দুধ', 'dudh'), ('চা', 'cha'), ('ফল', 'phol'), ('আম', 'am'), ('কলা', 'kola'), ('লেবু', 'lebu'), ('চিনি', 'chini'), ('লবণ', 'lobon'), ('পানি', 'pani'), ('মিষ্টি', 'mishti'), ('বাঘ', 'bagh'), ('হাতি', 'hati'), ('ঘোড়া', 'ghora'), ('গরু', 'goru'), ('ছাগল', 'chhagol'), ('কুকুর', 'kukur'), ('বিড়াল', 'biral')],
 [('খাই', 'khai'), ('যাই', 'jai'), ('আসি', 'ashi'), ('দেখি', 'dekhi'), ('লিখি', 'likhi'), ('পড়ি', 'pori'), ('গাই', 'gai'), ('নাচি', 'nachi'), ('হাসি', 'hasi'), ('খেলি', 'kheli'), ('ভালো', 'bhalo'), ('খারাপ', 'kharap'), ('সুন্দর', 'shundor'), ('নতুন', 'notun'), ('দ্রুত', 'druto'), ('ধীরে', 'dhire'), ('গরম', 'gorom'), ('ঠান্ডা', 'thanda'), ('ঠিক', 'thik'), ('ভুল', 'bhul'), ('আজ', 'aj')],
 [('আমি ভাত খাই', 'ami bhat khai'), ('তুমি কেমন আছো', 'tumi kemon acho'), ('আমার নাম রফিক', 'amar nam rafik'), ('সে স্কুলে যায়', 'se skule jay'), ('আজ আকাশ নীল', 'aj akash nil'), ('আমি বই পড়ি', 'ami boi pori'), ('আমরা মাঠে খেলি', 'amra mathe kheli'),
  ('মা ভাত রান্না করেন', 'ma bhat ranna koren'), ('পাখি গান গায়', 'pakhi gan gay'), ('আমি ভালো আছি', 'ami bhalo achi'), ('বাবা বাজারে যান', 'baba bajare jan'), ('নদীতে নৌকা চলে', 'nodite nouka chole')],
 [('আমাদের দেশের নাম বাংলাদেশ', 'amader desher nam bangladesh'), ('ঢাকা আমাদের রাজধানী', 'dhaka amader rajdhani'), ('আমি প্রতিদিন টাইপিং শিখি', 'ami protidin typing shikhi'), ('সময়ের কাজ সময়ে করো', 'shomoyer kaj shomoye koro'),
  ('সত্য কথা বলো', 'shotyo kotha bolo'), ('পরিশ্রম সফলতার চাবি', 'porishrom shofolotar chabi'), ('আমরা সবাই বন্ধু', 'amra sobai bondhu'), ('বই আমাদের সেরা বন্ধু', 'boi amader shera bondhu'),
  ('আজ আমি নতুন কিছু শিখেছি', 'aj ami notun kichhu shikhechhi'), ('সকালে ঘুম থেকে উঠো', 'shokale ghum theke utho')]]
BN_TITLES = ['Bangla Basics', 'Bangla Words I', 'Bangla Words II', 'Food and Animals', 'Verbs and Feelings', 'Short Phrases', 'Sentences']
BN_LEVELS = 12   # tiers 1..6 each have a normal level; levels 7,8,..: repeats at higher speed, 12 = boss
def bn_tier(L): return min(len(BN) - 1, (L - 1) // 2 if L < 12 else 6)
def bn_title(L): return ('BOSS: ' if L % 6 == 0 else '') + BN_TITLES[min(len(BN_TITLES) - 1, bn_tier(L))] + (' - Round 2' if L % 2 == 0 and L % 6 != 0 else '')
def bn_gen(L, R, native=False, avoid=()):
    t = bn_tier(L); pool = list(BN[t]) + (list(BN[t - 1]) if t > 0 and R.random() < .3 else []); b, p = R.choice(pool); return (b, b) if native else (b, p)
def bn_split(s, i):
    """move i forward so that it never cuts a Bangla letter from its vowel sign / conjunct"""
    n = len(s)
    while 0 < i < n and (unicodedata.category(s[i]) in ('Mn', 'Mc') or s[i - 1] == '\u09cd'): i += 1
    return i

# ---------------------------------------------------------------- daily challenge
DAILY = [dict(name='Speed Monday', mode='words', lo=3, hi=6, spd=1.3, desc='Fast words. Enemies move 30% faster.', strict=False),
         dict(name='Accuracy Tuesday', mode='sent', lo=24, hi=44, spd=1.0, desc='Every mistake costs HP. Stay clean.', strict=True),
         dict(name='Word Wednesday', mode='words', lo=7, hi=12, spd=1.0, desc='Long words only.', strict=False),
         dict(name='Number Thursday', mode='nums', lo=4, hi=9, spd=1.1, desc='Digits, dates and phone numbers.', strict=False, style='rand'),
         dict(name='Sentence Friday', mode='sent', lo=36, hi=70, spd=1.0, desc='Long sentences.', strict=False),
         dict(name='Symbol Saturday', mode='sym', lo=6, hi=30, spd=1.0, desc='Emails, math, brackets and more.', strict=False, style='soup'),
         dict(name='Bangla Sunday', mode='bn', lo=3, hi=20, spd=1.0, desc='Bangla phrases (phonetic or native keyboard).', strict=False)]
def daily_lesson(wd):
    d = dict(DAILY[wd]); d.update(n=min(TOTAL, 100), new='', title=d['name'], text=d['desc'], boss=False, ch=0); return d
