import json
words = json.load(open('/home/claude/app/words.json', encoding='utf8'))
tm = {}
for line in open('/home/claude/app/themes.txt', encoding='utf8'):
    c, ws = line.strip().split('|')
    for x in ws.split(): tm[x] = c
for w in words: w[3] = tm.get(w[0], w[3])
known = {w[0]: w for w in words}
patch = dict(l.strip().split('|') for l in open('/home/claude/app/ru_patch.txt', encoding='utf8') if l.strip())
used = set()
fix = {}
for l in open('/home/claude/app/fix.txt', encoding='utf8'):
    if l.strip():
        a, b, c = l.strip().split('|'); fix[a] = (b, c)
fixed = set()
sents, bad = [], []
import itertools
for line in itertools.chain(open('/home/claude/app/sent.txt', encoding='utf8'), open('/home/claude/app/sent2.txt', encoding='utf8'), open('/home/claude/app/sent4.txt', encoding='utf8')):
    line = line.strip()
    if not line: continue
    zh, ru = line.split('|')
    if zh in fix: fixed.add(zh); zh, ru = fix[zh]
    elif zh in patch: ru = patch[zh]; used.add(zh)
    toks = zh.split()
    miss = [t for t in toks if t not in known]
    if miss: bad.append((zh, miss)); continue
    sents.append([toks, ru])
print('fixes not applied:', set(fix)-fixed)
print(len(sents), 'sentences; bad:', bad, 'unused patches:', set(patch)-used)
from collections import Counter
print(Counter(max(known[t][4] for t in s[0]) for s in sents))
cov = set()
for s in sents:
    m = max(known[t][4] for t in s[0])
    cov |= {t for t in s[0] if known[t][4] >= m}
print('uncovered:', ' '.join(w[0] for w in words if w[0] not in cov))
print('words covered by sentences:', len(cov), 'of', len(words))
dlg, cur, dbad = [], None, []
for line in open('/home/claude/app/dialogs.txt', encoding='utf8'):
    line = line.strip()
    if not line: continue
    if line[0] == '@':
        _, th, title = line.split(' ', 2); cur = {'id': 'd%d' % len(dlg), 'th': th, 't': title, 'l': []}; dlg.append(cur)
    else:
        sp, rest = line.split(':', 1); zh, ru = rest.split('|'); toks = zh.split()
        dbad += [t for t in toks if t not in known]
        cur['l'].append([sp, toks, ru])
for d in dlg: d['lv'] = max(known[t][4] for l in d['l'] for t in l[1] if t in known)
gr, gbad = [], []
for line in open('/home/claude/app/grammar.txt', encoding='utf8'):
    if not line.strip(): continue
    k, title, rule, zh, ru = line.strip().split('|'); ks = k.split(','); toks = zh.split()
    gbad += [t for t in toks + ks if t not in known]
    gr.append({'k': ks, 't': title, 'r': rule, 'zh': toks, 'ru': ru, 'lv': min(known[x][4] for x in ks if x in known)})
g2 = {}
for line in open('/home/claude/app/grammar2.txt', encoding='utf8'):
    if not line.strip(): continue
    k, f, pts, err, exs = line.strip().split('|'); g2[k] = (f, pts.split(';'), err, [e.split('=') for e in exs.split(';')])
for i, g in enumerate(gr):
    g['id'] = 'g%d' % i
    f, pts, err, exs = g2.pop(g['k'][0])
    g['f'], g['p'], g['e'] = f, pts, err
    g['x'] = [[g['zh'], g['ru']]]
    for zh, ru in exs:
        toks = zh.split(); gbad += [t for t in toks if t not in known]
        if toks != g['zh']: g['x'].append([toks, ru])
    del g['zh'], g['ru']
print('grammar2 unused', list(g2), 'examples', sum(len(g['x']) for g in gr))
sim, sbad = [], []
for i, line in enumerate(l for l in open('/home/claude/app/sim.txt', encoding='utf8') if l.strip()):
    k, title, pts, exs = line.strip().split('|'); ks = k.split()
    P = [x.split(': ', 1) for x in pts.split(';')]
    X = [[e.split('=')[0].split(), e.split('=')[1]] for e in exs.split(';')]
    sbad += [t for t in ks if t not in known] + [t for x in X for t in x[0] if t not in known] + [x[0] for x in P if x[0] not in ks] + [k2 for k2 in ks if k2 not in [x[0] for x in P]]
    sim.append({'id': 's%d' % i, 'k': ks, 't': title, 'p': P, 'x': X, 'lv': max(known[x][4] for x in ks if x in known)})
print('sim', len(sim), 'bad', sbad)
print('dialogs', len(dlg), Counter(d['lv'] for d in dlg), 'bad', dbad, '| grammar', len(gr), Counter(g['lv'] for g in gr), 'bad', gbad)
import subprocess; subprocess.run(['python3','/home/claude/app/gen_chars.py'],check=True)
t = open('/home/claude/app/template.html', encoding='utf8').read()
js = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
out = t.replace('__WORDS__', js(words)).replace('__SENTS__', js(sents))
out = out.replace('__SIM__', js(sim)).replace('__DLG__', js(dlg)).replace('__GR__', js(gr))
out = out.replace('__CHARS__', open('/home/claude/app/chars.json', encoding='utf8').read()).replace('__STROKES__', open('/home/claude/app/strokes.json', encoding='utf8').read())
out = out.replace('__HW__', open('/home/claude/hw/node_modules/hanzi-writer/dist/hanzi-writer.min.js', encoding='utf8').read())
ver, vdate = open('/home/claude/app/VERSION').read().split()
out = out.replace('__VER__', ver).replace('__VDATE__', vdate)
open('/home/claude/app/index.html', 'w', encoding='utf8').write(out)
import glob, os
for f in glob.glob('/home/claude/app/hsk-trainer*.html'): os.remove(f)
open('/home/claude/app/hsk-trainer-v%s.html' % ver, 'w', encoding='utf8').write(out)
print('version', ver, vdate)
print(len(out.encode('utf8')), 'bytes')
