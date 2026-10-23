"""Recomputes the Curators catalogue: takes out the curators' self-promotion, replaces listening links that lead to a curator's
own video, normalises the artist keys, computes the best RYM rank (rr), the genre family (fam) and the shared names (cross).
Idempotent. usage: python3 -I tools/recalcule.py data
"""
import json,unicodedata,re,collections,sys
from urllib.parse import quote
D=sys.argv[1]
import os
c=json.load(open(D+'/catalogue.json'))
# rym.json (top 10 000 de Rate Your Music) : facultatif ; sans lui, les rangs et liens déjà inscrits dans les fiches servent
R=json.load(open(D+'/rym.json')) if os.path.exists(D+'/rym.json') else {'albums':{}}
def norm(a):
  a=unicodedata.normalize('NFKD',a.lower()); a=''.join(ch for ch in a if not unicodedata.combining(ch))
  a=a.replace('&',' and '); a=re.sub(r'\([^)]*\)','',a); a=re.sub(r'^\s*the\s+','',a.strip())
  return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9]+',' ',a)).strip()
best={}
for rk,a in R['albums'].items():
  k=norm(a[0]); rk=int(rk)
  best.setdefault(k,[]).append((rk,a))
for k in best: best[k].sort(key=lambda t:t[0])
def relink(x):
  """listening link -> the other artist's music, never the curator's own video"""
  k=norm(x['artist']); hit=next(((rk,a) for rk,a in best.get(k,[]) if a[5]),None)
  x.pop('ytvia',None)
  if hit:
    rk,a=hit; x['yt']='https://www.youtube.com/watch?v='+a[5]; x['direct']=True
    x['ytvia']=f"{a[1]} ({a[2]}), the artist's best-ranked album on RYM with a YouTube link"
  else:
    q=x['artist']+(' '+x['title'].split(' · ',1)[1] if ' · ' in x['title'] else '')
    x['yt']='https://www.youtube.com/results?search_query='+quote(q); x['direct']=False
log=collections.Counter(); removed=[]
out=[]
for x in c:
  t=x['type']
  if x['c']=='pag' and t=='Playlist' and 'Furtw' in x['meta']: x['artist']='Wilhelm Furtwängler'
  if (x['c']=='nab' and t in('Livre','Texte')) or (x['c']=='pag' and t=='Playlist' and x['artist'].strip()):
    work=x['title']; kind={'Livre':'book','Texte':'text','Playlist':'playlist'}[t]
    x['meta']=(f"subject of Marc-Édouard Nabe's {kind} « {work} »" if x['c']=='nab' else f"kept in Dominique Pagani's playlist « {work} » ({x['meta']})")
    x['type']='Subject of a book or text' if x['c']=='nab' else 'In a playlist'
    x['title']=x['artist']; x['_conv']=1
    dup=next((y for y in out if y['c']==x['c'] and y['title']==x['title']),None)
    if dup: dup['meta']=(dup['meta']+' ; ' if dup['meta'] else '')+x['meta']; log['fusionnées '+x['c']]+=1; continue
    log['converties '+x['c']]+=1; out.append(x); continue
  if (x['c']=='nab' and t=='Lecture') or (x['c']=='pag' and t=='Playlist') or (x['c']=='ida' and x['artist']=='Podcast Kill The Computer'):
    removed.append(x); log['retirées '+x['c']]+=1; continue
  out.append(x)
for x in out:
  if x.pop('_conv',0): relink(x)
c=out
seen={(x['c'],x['title']) for x in c}
out=[]
for x in c:
  if x['c']=='pag' and x['type'].startswith('Commenté ('):
    serie=x['type'][len('Commenté ('):-1]
    old=x['title']; 
    if 'youtube.com/watch' in x['yt']: x['src']=x['yt']
    x['meta']=f"commented on by Dominique Pagani in « {old} » ({serie})"
    x['title']=x['artist']; x['type']='Commented on'
    if (x['c'],x['title']) in seen:
      ex=next(y for y in c if y['c']=='pag' and y['title']==x['title'] and y is not x)
      ex['meta']=(ex['meta']+' ; ' if ex['meta'] else '')+x['meta']; log['fusionnées pag']+=1; continue
    seen.add((x['c'],x['title'])); relink(x); log['converties pag']+=1
  elif x['c']=='alp' and x['type']=='Essentials' and 'Alpha-27 Essentials' not in x['meta']:
    x['src']=x['yt']; x['meta']=(x['meta']+' · ' if x['meta'] else '')+'shown in an « Alpha-27 Essentials » episode'
    relink(x); log['reliées alp']+=1
  out.append(x)
c=out
SELF=set(json.load(open(sys.argv[0].rsplit('/',1)[0]+'/self_ids.json')))
for x in c:
  m=re.search(r'[?&]v=([\w-]{11})',x['yt'])
  if m and m.group(1) in SELF: relink(x); log['lien perso remplacé '+x['c']]+=1
# families
FAM=[('Netlabels lo-bit',r'lobit|lo-bit|chiptune|tracker'),
 ('Musiques de jeux et de films',r'video game|film score|bande originale|\bost\b|soundtrack|musical comedy'),
 ('Jazz',r'jazz|bop|big band|swing|dixieland|third stream|standards|modern creative'),
 ('Classique et musique ancienne',r'classi|romantic|opera|opéra|baroque|symphon(y|ie)|concerto|oratorio|chamber|requiem|serialism|expressionism|minimalism|sonorism|musique ancienne|orchestral|contemporary$|polyphon|lied'),
 ('Metal',r'metal|grind|thrash|doom|dsbm|deathcore|metalcore|mathcore|sludge|blackgaze|doomgaze|gothenburg|powerviolence|emoviolence|death \'n\' roll|neue deutsche'),
 ('Industriel, bruit et expérimental',r'industri|noise|drone|harsh|japanoise|power electronics|death industrial|experimental$|expérimental$|avant-garde$|electroacoustic|plunderphonics|free improvisation|musique concr|spoken word|audio documentary|beat poetry|punk poetry|platinisme'),
 ('Hip-hop',r'hip.?hop|rap|turntabl|horrorcore'),
 ('Électronique',r'ambient|electro|électro|idm|techno|house|trance|dub|trip hop|downtempo|breakcore|footwork|glitch|synth|illbient|wonky|club|acid|dance|drill and bass|hardcore breaks|darkwave|hauntology|fourth world|digital fusion|ethereal|progressive electronic|left-field|lounge|exotica'),
 ('Rock et punk',r'rock|punk|grunge|shoegaze|post-hardcore|hardcore|krautrock|zeuhl|slowcore|psych|stoner|emo|jam band|skiffle|lo-fi|slacker|goth|crust|d-beat|stenchcore|rock in opposition|prog'),
 ('Pop, soul et R&B',r'pop|soul|r&b|funk|girl group|disco|minneapolis|shibuya|kayōkyoku|filmi'),
 ('Folk, chanson et musiques du monde',r'folk|chanson|singer|country|americana|bossa|mpb|brésil|cumbia|qawwali|arab|klezmer|palm wine|reggae|traditionnel|hawaï|afro|anatolian|turkish|ethno|tribal|blues|american primitiv|religieux|ethnotronica|western')]
def fam_of(genres):
  sc=collections.Counter()
  for i,g in enumerate(genres):
    for f,rx in FAM:
      if re.search(rx,g.lower()): sc[f]+=2 if i==0 else 1; break
  return sc.most_common(1)[0][0] if sc else None
ICE={'death-metal':'Metal','doom-metal':'Metal','black':'Metal','thrash':'Metal','grindcore':'Metal','industrial':'Industriel, bruit et expérimental','disturbing':'Industriel, bruit et expérimental'}
for x in c:
  k=norm(x['artist']); x['key']=k
  rr=[r for r in [(x.get('rym') or {}).get('rank'),(x.get('rymArtist') or {}).get('rank')] if r]
  if best.get(k): rr.append(best[k][0][0])
  if not R['albums'] and x.get('rr'): rr.append(x['rr'])   # sans rym.json : garder le rang déjà inscrit
  x['rr']=min(rr) if rr else None
  f=fam_of(x['genres'])
  if not f and best.get(k): f=fam_of([g.strip() for g in best[k][0][1][4].split(',')])
  if not f and x['c']=='sig': f='Netlabels lo-bit'
  if not f and x['c']=='wya':
    f=next((v for s,v in ICE.items() if s in x['src'].lower()),None) or ('Metal' if 'metal' in x['src'].lower() else None)
  x['fam']=f or 'Inclassé'
# cross
g=collections.defaultdict(set)
for x in c: g[x['key']].add(x['c'])
for x in c: s=g[x['key']]; x['cross']=sorted(s) if len(s)>=2 and x['key'] else []
json.dump(c,open(D+'/catalogue.json','w'),ensure_ascii=False)
print(dict(log)); print(len(c)); print(collections.Counter(x['fam'] for x in c))
print([ (x['c'],x['type'],x['title']) for x in removed])
