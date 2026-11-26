import json, re, sys
SRC = '/home/claude/data/complete-hsk-vocabulary/wordlists/exclusive/newest/%d.json'
KEEP_CAP = {'汉语', '中国', '中文'}
VOW = 'aāáǎàeēéěèoōóǒò'

def join(p, hz):
    syl = p.split()
    out = ''
    for i, s in enumerate(syl):
        if i and s[0].lower() in VOW and s != 'r':
            out += "'"
        out += s
    return out if hz in KEEP_CAP else out.lower()

words, bad = [], []
for lvl in (1, 2, 3, 4):
    src = {w['simplified']: w for w in json.load(open(SRC % lvl))}
    seen = set()
    for line in open('/home/claude/app/v%d.txt' % lvl, encoding='utf8'):
        line = line.strip()
        if not line: continue
        parts = line.split('=')
        hz, ru, th = parts[0], parts[1], parts[2]
        if hz not in src: bad.append(('not in list', lvl, hz)); continue
        if hz in seen: bad.append(('dup', lvl, hz))
        seen.add(hz)
        if len(parts) > 3: py = parts[3]
        else:
            ps = [f['transcriptions']['pinyin'] for f in src[hz]['forms']]
            low = [p for p in ps if p[0].islower()] or ps
            py = join(low[0], hz)
        words.append([hz, py, ru, th, lvl, src[hz].get('frequency') or 99999])
    for hz in src:
        if hz not in seen: bad.append(('missing', lvl, hz))
print(len(words), 'words;', 'problems:', bad)
json.dump(words, open('/home/claude/app/words.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
from collections import Counter
print(Counter((w[4], w[3]) for w in words))
