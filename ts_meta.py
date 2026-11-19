"""Keyboard Warrior - heroes, bosses and achievements (pure data)."""
HEROES = dict(
    kai=dict(name='Kai', price=0, col='#ffffff', lcol='#16214a', belt='#ffd24a', acc=['band'], sc=1.0, pw=1.0, sp=1.0, ar=1.0, lk=1.0, jv=1.0, perk='Balanced fighter - no weaknesses.'),
    ryu=dict(name='Ryu', price=300, col='#ff8a7a', lcol='#b3261e', belt='#ffffff', acc=['band', 'spike'], sc=1.0, pw=1.12, sp=1.0, ar=1.0, lk=1.0, jv=1.0, perk='+12% attack power. Hot-headed.'),
    mei=dict(name='Mei', price=450, col='#ffa6d5', lcol='#c2185b', belt='#ffffff', acc=['pony', 'ribbon'], sc=.97, pw=1.0, sp=1.1, ar=1.0, lk=1.0, jv=1.15, perk='+10% strike speed and a higher jump.'),
    ren=dict(name='Ren', price=600, col='#8fdcff', lcol='#0b5d8a', belt='#ff5a5a', acc=['topknot', 'band'], sc=1.03, pw=1.06, sp=1.06, ar=1.0, lk=1.0, jv=1.0, perk='Samurai discipline: +6% power, +6% speed.'),
    shadow=dict(name='Shadow', price=800, col='#c3b2ff', lcol='#3b2a8c', belt='#7c5cff', acc=['mask', 'scarf'], sc=1.0, pw=1.0, sp=1.1, ar=.88, lk=1.0, jv=1.1, perk='Ninja: takes 12% less damage, +10% speed.'),
    bjorn=dict(name='Bjorn', price=1000, col='#ffbf80', lcol='#8a4b12', belt='#a05a1a', acc=['helm', 'beard'], sc=1.1, pw=1.1, sp=.95, ar=.8, lk=1.0, jv=.9, perk='Viking: takes 20% less damage, +10% power, slower.'),
    robo=dict(name='Robo-X', price=1200, col='#a9ecff', lcol='#1b6a85', belt='#00e5ff', acc=['visor', 'antenna'], sc=1.04, pw=1.0, sp=1.0, ar=1.0, lk=1.3, jv=1.0, perk='Coin magnet: +30% coins from fights.'),
    neon=dict(name='Neon', price=1600, col='#79ffc0', lcol='#0a8f5b', belt='#ff4fd8', acc=['halo', 'cape'], sc=1.0, pw=1.06, sp=1.06, ar=.94, lk=1.1, jv=1.06, perk='Legend: small bonus to everything.'))
HORDER = ['kai', 'ryu', 'mei', 'ren', 'shadow', 'bjorn', 'robo', 'neon']
HGIFT = {20: 'ryu', 40: 'mei', 60: 'ren', 80: 'shadow', 100: 'bjorn', 125: 'robo', 150: 'neon'}
BOSSES = dict(
    brute=dict(name='Iron Brute', col='#ff9f43', wp='warhammer', sc=1.65, s1=['shock'], s2=['shock', 'summon'], line='"You type like a child!"'),
    ninja=dict(name='Shadow Lord', col='#b18cff', wp='daggers', sc=1.45, s1=['blink'], s2=['blink', 'stars'], line='"You cannot catch a shadow."'),
    samurai=dict(name='Flame Samurai', col='#ff6b4a', wp='katana', sc=1.55, s1=['iai'], s2=['iai', 'firewave'], line='"My blade burns brighter."'),
    frost=dict(name='Frost Queen', col='#7fd8ff', wp='rapier', sc=1.5, s1=['icicle'], s2=['icicle', 'shock'], line='"Everything freezes."'),
    thunder=dict(name='Thunder Monk', col='#ffe14a', wp='bostaff', sc=1.5, s1=['bolt'], s2=['bolt', 'bolt', 'shock'], line='"Feel the storm!"'),
    twin=dict(name='Twin Blades', col='#ff7ab8', wp='twinswords', sc=1.5, s1=['blink', 'stars'], s2=['clone', 'stars'], line='"Two blades, no mercy."'),
    golem=dict(name='Stone Golem', col='#c9ad7a', wp=None, sc=1.8, s1=['stomp'], s2=['stomp', 'summon', 'bolt'], line='"Grrrrr..."'),
    dragon=dict(name='Dragon Emperor', col='#ff4d4d', wp='greatsword', sc=1.85, s1=['firewave', 'bolt'], s2=['firewave', 'bolt', 'summon', 'stars'], line='"Kneel before the Emperor!"'))
def _cl(D): return sum(1 for v in D['stars'].values() if v > 0)
def _st(D): return sum(D['stars'].values())
# id, name, description, coins, test(D, S)
ACH = [
    ('first', 'First Blood', 'Defeat your first enemy.', 20, lambda D, S: S['kills'] >= 1), ('k100', 'Warrior', 'Defeat 100 enemies.', 50, lambda D, S: S['kills'] >= 100), ('k1000', 'Veteran', 'Defeat 1,000 enemies.', 200, lambda D, S: S['kills'] >= 1000),
    ('keys100', 'Warm-Up', 'Type 100 keys.', 20, lambda D, S: D['keys'] >= 100), ('keys1k', 'Finger Fitness', 'Type 1,000 keys.', 40, lambda D, S: D['keys'] >= 1000), ('keys10k', 'Keyboard Crusher', 'Type 10,000 keys.', 120, lambda D, S: D['keys'] >= 10000),
    ('keys50k', 'Typing Machine', 'Type 50,000 keys.', 400, lambda D, S: D['keys'] >= 50000),
    ('c25', 'Combo Starter', 'Reach a 25x combo.', 30, lambda D, S: S['combo'] >= 25), ('c50', 'Combo Master', 'Reach a 50x combo.', 60, lambda D, S: S['combo'] >= 50), ('c100', 'Combo Legend', 'Reach a 100x combo.', 150, lambda D, S: S['combo'] >= 100),
    ('c250', 'Unstoppable', 'Reach a 250x combo.', 400, lambda D, S: S['combo'] >= 250),
    ('w20', 'Getting Faster', 'Reach 20 WPM.', 30, lambda D, S: D['best_wpm'] >= 20), ('w30', 'Quick Fingers', 'Reach 30 WPM.', 60, lambda D, S: D['best_wpm'] >= 30), ('w40', 'Fast Typist', 'Reach 40 WPM.', 100, lambda D, S: D['best_wpm'] >= 40),
    ('w60', 'Speed Demon', 'Reach 60 WPM.', 250, lambda D, S: D['best_wpm'] >= 60), ('w80', 'Lightning', 'Reach 80 WPM.', 500, lambda D, S: D['best_wpm'] >= 80),
    ('l10', 'Apprentice', 'Clear 10 levels.', 50, lambda D, S: _cl(D) >= 10), ('l25', 'Fighter', 'Clear 25 levels.', 100, lambda D, S: _cl(D) >= 25), ('l50', 'Champion', 'Clear 50 levels.', 200, lambda D, S: _cl(D) >= 50),
    ('l100', 'Century', 'Clear 100 levels.', 500, lambda D, S: _cl(D) >= 100), ('l150', 'Grandmaster', 'Clear all 150 levels.', 1500, lambda D, S: _cl(D) >= 150),
    ('s30', 'Star Collector', 'Earn 30 stars.', 60, lambda D, S: _st(D) >= 30), ('s150', 'Star Hunter', 'Earn 150 stars.', 250, lambda D, S: _st(D) >= 150), ('s400', 'Star Master', 'Earn 400 stars.', 800, lambda D, S: _st(D) >= 400),
    ('perf', 'Flawless', 'Clear a level with 100% accuracy.', 60, lambda D, S: S['perfect'] >= 1), ('perf10', 'Perfectionist', 'Clear 10 levels with 100% accuracy.', 250, lambda D, S: S['perfect'] >= 10),
    ('b1', 'Boss Slayer', 'Defeat a boss.', 50, lambda D, S: S['bosses'] >= 1), ('b10', 'Boss Hunter', 'Defeat 10 bosses.', 200, lambda D, S: S['bosses'] >= 10), ('b30', 'Boss Legend', 'Defeat 30 bosses.', 600, lambda D, S: S['bosses'] >= 30),
    ('noscratch', 'No Scratch', 'Defeat a boss without taking damage.', 200, lambda D, S: S['flawless'] >= 1),
    ('d1', 'Nimble', 'Dodge an attack (jump or step back).', 20, lambda D, S: S['dodges'] >= 1), ('d25', 'Matador', 'Dodge 25 attacks.', 80, lambda D, S: S['dodges'] >= 25), ('d100', 'Untouchable', 'Dodge 100 attacks.', 250, lambda D, S: S['dodges'] >= 100),
    ('j50', 'Hop Hop', 'Jump 50 times.', 30, lambda D, S: S['jumps'] >= 50), ('j500', 'Sky Warrior', 'Jump 500 times.', 150, lambda D, S: S['jumps'] >= 500),
    ('daily1', 'Daily Hero', 'Finish a Daily Challenge.', 60, lambda D, S: S['daily'] >= 1), ('daily7', 'Week Warrior', 'Finish 7 Daily Challenges.', 250, lambda D, S: S['daily'] >= 7), ('streak7', 'On Fire', 'Reach a 7-day streak.', 200, lambda D, S: D['streak'] >= 7),
    ('ch5', 'Challenger', 'Reach wave 5 in Challenge mode.', 60, lambda D, S: D.get('chal', 0) >= 5), ('ch15', 'Gauntlet Runner', 'Reach wave 15 in Challenge mode.', 250, lambda D, S: D.get('chal', 0) >= 15),
    ('ch30', 'Gauntlet King', 'Reach wave 30 in Challenge mode.', 800, lambda D, S: D.get('chal', 0) >= 30), ('sv10', 'Survivor', 'Survive 10 waves in Survival.', 100, lambda D, S: S['surv'] >= 10),
    ('bn1', 'Bangla Beginner', 'Clear a Bangla level.', 40, lambda D, S: S['bn'] >= 1), ('bn6', 'Bangla Scholar', 'Clear 6 Bangla levels.', 150, lambda D, S: S['bn'] >= 6), ('bn12', 'Bangla Master', 'Clear all 12 Bangla levels.', 400, lambda D, S: S['bn'] >= 12),
    ('ult10', 'Ultimate Power', 'Use the Ultimate 10 times.', 60, lambda D, S: S['ults'] >= 10),
    ('arsenal', 'Arsenal', 'Own every weapon.', 400, lambda D, S: len(D['owned']) >= S.get('nweap', 99)), ('styles', 'Master of Styles', 'Learn every fighting style.', 400, lambda D, S: len(D['own_styles']) >= S.get('nsty', 99)),
    ('roster', 'Hero Roster', 'Unlock every hero.', 400, lambda D, S: len(D['own_heroes']) >= len(HEROES)),
    ('rush3', 'Boss Breaker', 'Defeat 3 bosses in one Boss Rush.', 120, lambda D, S: D.get('rush', 0) >= 3), ('rush8', 'Boss Rush Champion', 'Clear the whole Boss Rush.', 600, lambda D, S: D.get('rush', 0) >= 8),
    ('weak5', 'Fixing Weaknesses', 'Finish 5 Weak-Key Trainer sessions.', 100, lambda D, S: S.get('weak', 0) >= 5),
    ('tut10', 'Diligent Student', 'Finish 10 Typing Tutor lessons.', 100, lambda D, S: sum(1 for v in D.get('tutor_stars', {}).values() if v > 0) >= 10), ('tut50', 'Touch Typist', 'Finish 50 Typing Tutor lessons.', 300, lambda D, S: sum(1 for v in D.get('tutor_stars', {}).values() if v > 0) >= 50),
    ('tut150', 'Typing Graduate', 'Finish all 150 Typing Tutor lessons.', 1000, lambda D, S: sum(1 for v in D.get('tutor_stars', {}).values() if v > 0) >= 150),
    ('rich', 'Coin Collector', 'Earn 5,000 coins in total.', 100, lambda D, S: S['earned'] >= 5000)]
