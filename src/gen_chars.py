import json
words=json.load(open('/home/claude/app/words.json',encoding='utf8'))
src={}
for l in (1,2,3,4):
    for w in json.load(open('/home/claude/data/complete-hsk-vocabulary/wordlists/exclusive/newest/%d.json'%l)): src[w['simplified']]=w
g=dict(l.strip().split('=',1) for l in open('/home/claude/app/chars.txt',encoding='utf8') if l.strip())
single={w[0]:w for w in words if len(w[0])==1}
C={}
def syl(hz):
    ps=[f['transcriptions']['pinyin'] for f in src[hz]['forms']]
    low=[p for p in ps if p[0].islower()] or ps
    return low[0].lower().split()
for w in words:
    hz=w[0]; s=syl(hz)
    for i,c in enumerate(hz):
        if c in C: continue
        if c in single: C[c]=[single[c][1],single[c][2]]
        elif c in g: C[c]=[s[i] if len(s)==len(hz) else '',g[c]]
json.dump(C,open('/home/claude/app/chars.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
print('chars',len(C))
