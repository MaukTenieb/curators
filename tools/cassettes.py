"""Cassettes de la rubrique CURATORS : aucune source, aucun curateur, seulement des vidéos YouTube.
Chaque étiquette porte un genre et une date du calendrier républicain, au feutre, d'une encre propre au genre.
Le meuble garde le Top 60, les compilations par genre et les 10 dernières cassettes datées (une par genre et par veille).
usage : python3 -I tools/cassettes.py data AAAA-MM-JJ"""
import json,re,sys,collections,datetime
D=sys.argv[1]; TODAY=sys.argv[2]
c=json.load(open(D+'/catalogue.json'))
veille=json.load(open(D+'/veille.json'))
SELF=set(json.load(open(sys.argv[0].rsplit('/',1)[0]+'/self_ids.json')))
KEEP_DATED=10

# --- calendrier républicain (même règle que ik-name.js : an III, VII, XI, XV sextiles, puis Romme) ---
MOIS=['vendémiaire','brumaire','frimaire','nivôse','pluviôse','ventôse','germinal','floréal','prairial','messidor','thermidor','fructidor','jour complémentaire']
def sextile(y): return y in (3,7,11,15) if y<20 else (y%4==0 and (y%100!=0 or y%400==0) and y%4000!=0)
def rep(iso):
  n=(datetime.date.fromisoformat(iso)-datetime.date(1792,9,22)).days; y=1
  while True:
    L=366 if sextile(y) else 365
    if n<L: break
    n-=L; y+=1
  m,d=n//30+1,n%30+1
  return (f"{d} {MOIS[m-1]} an {y}" if m<13 else f"{d}e {MOIS[12]} an {y}"), (f"{d} {MOIS[m-1].capitalize()} Year {y}" if m<13 else f"Complementary day {d}, Year {y}")

FAM_EN={'Netlabels lo-bit':'Lo-bit netlabels','Musiques de jeux et de films':'Game & film music','Jazz':'Jazz',
 'Classique et musique ancienne':'Classical & early music','Metal':'Metal','Industriel, bruit et expérimental':'Industrial, noise & experimental',
 'Hip-hop':'Hip-hop','Électronique':'Electronic','Rock et punk':'Rock & punk','Pop, soul et R&B':'Pop, soul & R&B',
 'Folk, chanson et musiques du monde':'Folk, chanson & world'}
def vid(x):
  m=re.search(r'[?&]v=([\w-]{11})',x.get('yt') or '')
  return m.group(1) if (m and x.get('direct') and m.group(1) not in SELF) else None
def label(x):
  t=re.sub(r'^s\d{5}\s*·\s*','',x['title']).replace(' – ',' · ')
  if x['artist'] and not t.lower().startswith(x['artist'].lower()[:4]): t=x['artist']+' · '+t
  return t

# --- classement général (même règle que la page) : curateurs desc, rang RYM asc, fiches desc ---
A={}
for x in c:
  if not x['key']: continue
  a=A.setdefault(x['key'],{'cs':set(),'n':0,'rr':None,'name':x['artist'],'pick':None})
  a['cs'].add(x['c']);a['n']+=1
  if x['rr'] and (a['rr'] is None or x['rr']<a['rr']): a['rr']=x['rr']
  if vid(x) and (a['pick'] is None or (x['type']=='Top 40' and a['pick']['type']!='Top 40')): a['pick']=x
order=sorted(A,key=lambda k:(-len(A[k]['cs']),A[k]['rr'] or 1e9,-A[k]['n'],A[k]['name']))
pos={k:i for i,k in enumerate(order)}
byrank=lambda x:(pos.get(x['key'],1e9),x.get('rank') or 99)

# --- compilations thématiques : genre, encre du feutre ---
COMP=[('Black metal','Black metal',r'black metal|dsbm|blackgaze|war metal','#1b1b1b'),
 ('Death metal','Death metal',r'death metal|slam|death \'n\' roll','#8b1a1a'),
 ('Doom & sludge','Doom & sludge',r'doom|sludge|stoner|drone metal','#4a2f1a'),
 ('Grind & mathcore','Grind & mathcore',r'grind|mathcore|powerviolence|metalcore|post-hardcore|emoviolence|hardcore|crust|d-beat','#c0391b'),
 ('Thrash & heavy','Thrash & heavy',r'thrash|heavy metal|power metal|speed metal|groove metal|crossover','#b02060'),
 ('Post-metal & post-rock','Post-metal & post-rock',r'post-metal|post-rock','#2f4f6f'),
 ("Métal d'avant-garde",'Avant-garde metal',r'avant-garde metal|avant-metal|progressive metal|gothic metal|industrial metal|symphonic metal|neoclassical metal|alternative metal|nu metal|funk metal','#5b2a86'),
 ('Musique de jeux vidéo','Video game music',r'video game|\bost\b','#0a7f6f'),
 ('Musique de films','Film music',r'film score|bande originale|soundtrack|western','#6b5a00'),
 ('Industriel & bruit','Industrial & noise',r'industri|noise|power electronics|death industrial|harsh|japanoise|gorenoise','#3d3d3d'),
 ('Ambient & drone','Ambient & drone',r'ambient|drone|fourth world|ethereal|neoclassical darkwave','#2a6f97'),
 ('Free jazz & avant-garde','Free jazz & avant-garde',r'avant-garde jazz|free jazz|spiritual jazz|free improvisation|avant-garde$|experimental$|avant-jazz|plunderphonics|electroacoustic','#d35400'),
 ('Jazz','Jazz',r'jazz|bop|big band|third stream|standards|dixieland','#1f3a93'),
 ('Électronique','Electronic',r'idm|electro|électro|techno|house|trip hop|illbient|digital fusion|glitch|breakcore|synth|downtempo|dub|footwork|hardcore breaks|darkwave|left-field','#007a8a'),
 ('Hip-hop','Hip-hop',r'hip.?hop|rap|turntabl|horrorcore','#7a3e00'),
 ('Rock psyché & bruitiste','Psych & noise rock',r'noise rock|psych|krautrock|zeuhl|space rock|shoegaze|math rock|avant-rock|rock in opposition|experimental rock|art rock|prog','#7d3c98'),
 ('Rock & punk','Rock & punk',r'rock|punk|grunge|post-punk|slowcore|emo|goth|lo-fi','#a93226'),
 ('Folk & chanson','Folk & chanson',r'folk|chanson|singer|country|americana|blues|neofolk','#196f3d'),
 ('Musiques du monde','World music',r'bossa|mpb|cumbia|qawwali|arab|klezmer|palm wine|reggae|traditionnel|hawaï|afro|anatolian|turkish|filmi|kayōkyoku|indonésienne|brésil','#b9770e'),
 ('Pop & soul','Pop & soul',r'pop|soul|r&b|funk|disco|girl group','#c2185b'),
 ('Classique','Classical',r'classi|romantic|opera|opéra|baroque|symphon|concerto|oratorio|chamber|requiem|serialism|expressionism|minimalism|ancienne|polyphon|orchestral|contemporary','#154360')]
EN={fr:en for fr,en,_,_ in COMP}; EN.update(FAM_EN); EN['Pot-pourri']='Mixed bag'; EN['Top 60']='Top 60'
INK={fr:ink for fr,_,_,ink in COMP}; INK['Pot-pourri']='#444'; INK['Top 60']='#1d2a6b'
def comp_of(x):
  for g in x['genres']:
    for fr,en,rx,_ in COMP:
      if re.search(rx,g.lower()): return fr
  return x['fam']

def tape(slug,genre,fiches,kind,crit_fr,crit_en,cap=None,date=None):
  seen=set();tr=[];last='0000'
  for x in fiches:
    i=vid(x)
    if i and i not in seen:
      seen.add(i); tr.append({'id':i,'title':label(x)}); last=max(last,x['added'])
    if cap and len(tr)>=cap: break
  if not tr: return None
  d=date or last
  rfr,ren=rep(d)
  return {'channel':'Curators · '+slug,'channel_url':'','shelf':'Curators','kind':kind,
          'label':genre,'label_en':EN.get(genre,genre),'genre':genre,'date':d,'rep':rfr,'rep_en':ren,
          'ink':INK.get(genre,'#1d2a6b'),'criteria':crit_fr,'criteria_en':crit_en,'count':len(tr),'tracks':tr}

ORDER_FR="ordre du classement général : nombre de curateurs, puis meilleur rang Rate Your Music, puis nombre de mentions"
ORDER_EN="general ranking order: number of curators, then best Rate Your Music rank, then number of mentions"
tapes=[]
tapes.append(tape('Top','Top 60',[A[k]['pick'] for k in order if A[k]['pick']],'top',
  "Top 60 : un morceau par artiste, les 60 premiers artistes du classement général disposant d'une vidéo ; "+ORDER_FR,
  "Top 60: one track per artist, the first 60 artists of the general ranking with a video; "+ORDER_EN,60))

# cassettes datées : une par genre et par veille ; le meuble garde les 10 dernières
dates=sorted({v['date'] for v in veille if v['date']!='2026-10-08'})   # la moisson fondatrice nourrit les compilations
dated=[]
for d in reversed(dates):
  prev=max([x for x in [v['date'] for v in veille] if x<d] or ['0000'])
  week=[x for x in c if prev<x['added']<=d and vid(x)]
  g=collections.defaultdict(list)
  for x in week: g[comp_of(x)].append(x)
  for genre,fs in sorted(g.items(),key=lambda t:-len(t[1])):
    if genre=='Inclassé': continue   # entries with zero genre go to the Pot-pourri
    rfr,_=rep(d)
    t=tape('Veille '+d+' · '+genre,genre,sorted(fs,key=byrank),'veille',
      f"Veille du {rfr} ({d}) : vidéos trouvées depuis la veille précédente, genre « {genre} » ; "+ORDER_FR,
      f"Watch of {d}: videos found since the previous watch, genre “{EN.get(genre,genre)}”; "+ORDER_EN,None,d)
    if t: dated.append(t)
  if len(dated)>=KEEP_DATED: break
tapes+=dated[:KEEP_DATED]

# compilations permanentes par genre
groups=collections.defaultdict(list)
for x in c:
  if vid(x): groups[comp_of(x)].append(x)
rest=[]
for genre,fs in sorted(groups.items(),key=lambda t:-len(t[1])):
  fs.sort(key=byrank)
  t=tape(genre,genre,fs,'genre',f"Compilation « {genre} » : toutes les vidéos de ce genre au catalogue, 99 au plus ; "+ORDER_FR,
         f"“{EN.get(genre,genre)}” compilation: every video of this genre in the catalogue, 99 at most; "+ORDER_EN,99)
  if t and t['count']>=4 and genre!='Inclassé': tapes.append(t)
  elif t: rest+=fs
t=tape('Pot-pourri','Pot-pourri',sorted(rest,key=byrank),'genre',"Pot-pourri : les genres qui comptent moins de 4 vidéos ; "+ORDER_FR,
       "Mixed bag: genres with fewer than 4 videos; "+ORDER_EN,99)
if t: tapes.append(t)

v={'generated':TODAY,'generated_rep':rep(TODAY)[0],'tapes':tapes}
json.dump(v,open(D+'/vhs-cassettes.json','w'),ensure_ascii=False)
open(D+'/kg-vhs-curations.js','w').write("/* CURATORS — cassettes pour le magnétoscope d'Insert Koin. Généré le "+rep(TODAY)[0]+" ("+TODAY+"). */\nwindow.KG_VHS_LIBRARY_SNAPSHOT = "+json.dumps(v,ensure_ascii=False)+";\n")
print(len(tapes),[(t['label'],t['rep'],t['count']) for t in tapes][:6])
