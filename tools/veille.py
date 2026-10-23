"""Monday watch, with zero secret and zero AI: reads the curators' sources a program can read,
adds one entry per new mention, finds a YouTube video for each, logs the watch.
Sources: Adam Sigmund (The Lowdown on Mad Wasp Radio, archive.org), Ida B. (KALX on Spinitron,
her Instagram picks on Spotify), Mauk Tenieb (Openwhyd). The other curators wait for the optional
Claude Code step of the workflow (secret CLAUDE_CODE_OAUTH_TOKEN), or for a hand edit.
usage: python3 -I tools/veille.py data YYYY-MM-DD
Code: MIT, Mauk Tenieb & Korhogo."""
import json, re, sys, html, os, unicodedata, urllib.request, urllib.parse

D, TODAY = sys.argv[1], sys.argv[2]
CAT = os.path.join(D, 'catalogue.json')
c = json.load(open(CAT, encoding='utf-8'))
R = json.load(open(os.path.join(D, 'rym.json'), encoding='utf-8')) if os.path.exists(os.path.join(D, 'rym.json')) else {'albums': {}}
SELF = set(json.load(open(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'self_ids.json'), encoding='utf-8')))
UA = {'User-Agent': 'Mozilla/5.0 (curators watch; https://github.com/MaukTenieb/curators)'}
seen = {(x['c'], x['title']) for x in c}
seen_yt = {(x['c'], m.group(1)) for x in c for m in [re.search(r'v=([\w-]{11})', x.get('yt') or '')] if m}
LAST = max(v['date'] for v in json.load(open(os.path.join(D, 'veille.json'), encoding='utf-8')))
srcs = {x['src'] for x in c}
new = []
log = {}


def get(url, tries=3):
    for _ in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception:
            continue
    return None


def norm(a):
    a = unicodedata.normalize('NFKD', a.lower()); a = ''.join(ch for ch in a if not unicodedata.combining(ch))
    a = a.replace('&', ' and '); a = re.sub(r'\([^)]*\)', '', a); a = re.sub(r'^\s*the\s+', '', a.strip())
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', a)).strip()


BEST = {}
for rk, a in R['albums'].items():
    BEST.setdefault(norm(a[0]), []).append((int(rk), a))
for k in BEST: BEST[k].sort(key=lambda t: t[0])
q = urllib.parse.quote


def add(cur, typ, artist, title, meta, src, yt=None, extra=None):
    artist = re.sub(r'\s+', ' ', (artist or '').replace(' ', ' ')).strip()
    title = re.sub(r'\s+', ' ', (title or '').replace(' ', ' ')).strip()
    if not artist: return
    t = artist + ' · ' + title if title else artist
    if (cur, t) in seen or (yt and (cur, yt) in seen_yt): return
    seen.add((cur, t))
    if yt: seen_yt.add((cur, yt))
    x = {'c': cur, 'type': typ, 'title': t, 'meta': meta, 'src': src, 'artist': artist, 'added': TODAY, 'genres': []}
    hit = BEST.get(norm(artist), [])
    if hit:
        x['genres'] = [g.strip() for g in hit[0][1][4].split(',')][:2]
    else:
        same = next((y for y in c if y.get('key') == norm(artist) and y.get('genres')), None)
        if same: x['genres'] = list(same['genres'])
    if yt and yt not in SELF:
        x['yt'] = 'https://www.youtube.com/watch?v=' + yt; x['direct'] = True
    else:
        v = next(((rk, a) for rk, a in hit if a[5] and a[5] not in SELF), None)
        if v:
            x['yt'] = 'https://www.youtube.com/watch?v=' + v[1][5]; x['direct'] = True
            x['ytvia'] = f"{v[1][1]} ({v[1][2]}), the artist's best-ranked album on RYM with a YouTube link"
        else:
            x['yt'] = 'https://www.youtube.com/results?search_query=' + q(artist + ' ' + title); x['direct'] = False
    x['bc'] = 'https://bandcamp.com/search?q=' + q(artist + ' ' + title)
    if extra: x.update(extra)
    new.append(x); log[cur] = log.get(cur, 0) + 1


def split_at(s):
    m = re.match(r'\s*(.+?)\s+[-–—]\s+(.+)$', s)
    return (m.group(1), m.group(2)) if m else (s, '')


# --- Adam Sigmund: The Lowdown on Mad Wasp Radio, one archive.org item per episode ---
def lowdown():
    s = get('https://archive.org/advancedsearch.php?q=title%3A%28%22the+lowdown+on+mad+wasp+radio%22%29&fl%5B%5D=identifier&rows=1000&output=json&sort%5B%5D=identifier+asc')
    if not s: return
    for d in json.loads(s)['response']['docs']:
        ident = d['identifier']; src = 'https://archive.org/details/' + ident
        if src in srcs: continue
        m = get('https://archive.org/metadata/' + ident + '/metadata')
        if not m: continue
        md = json.loads(m).get('result', {})
        title = md.get('title', ''); desc = md.get('description', '')
        if isinstance(desc, list): desc = '\n'.join(desc)
        ep = re.search(r'(\d+)\s*$', title) or re.search(r'(\d+)', ident)
        n = int(ep.group(1)) if ep else 0
        text = html.unescape(re.sub(r'<br\s*/?>|</div>|</p>', '\n', desc))
        for line in re.sub(r'<[^>]+>', '', text).split('\n'):
            line = line.strip().strip(' ')
            if not line or line.lower().startswith('episode') or ' - ' not in line and ' – ' not in line: continue
            a, t = split_at(line)
            add('sig', 'Played on The Lowdown', a, t, f'The Lowdown no. {n:03d}', src, extra={'ep': n})


# --- Ida B.: her shows on KALX, read on Spinitron ---
MONTHS = {'Jan': 'Jan.', 'Feb': 'Feb.', 'Mar': 'Mar.', 'Apr': 'Apr.', 'May': 'May', 'Jun': 'June', 'Jul': 'July', 'Aug': 'Aug.', 'Sep': 'Sep.', 'Oct': 'Oct.', 'Nov': 'Nov.', 'Dec': 'Dec.'}


def spinitron():
    s = get('https://spinitron.com/KALX/dj/169739/Sly-Ida')
    if not s: return
    for pl in dict.fromkeys(re.findall(r'href="(/KALX/pl/\d+/[^"]+)"', s)):
        src = 'https://spinitron.com' + pl
        if src in srcs: continue
        p = get(src)
        if not p: continue
        dm = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d+),\s+(20\d\d)\s+\d', p)
        if not dm: continue
        iso = '%s-%02d-%02d' % (dm.group(3), list(MONTHS).index(dm.group(1)) + 1, int(dm.group(2)))
        if iso <= LAST: continue   # shows before the last watch: the founding harvest chose among them
        when = f'KALX, {MONTHS[dm.group(1)]} {dm.group(2)}, {dm.group(3)}'
        for a, t, r in re.findall(r'<span class="artist">([^<]*)</span>.*?<span class="song">([^<]*)</span>(?:.*?<span class="release">([^<]*)</span>)?', p, re.S):
            a, t, r = html.unescape(a), html.unescape(t), html.unescape(r or '')
            add('ida', 'Track', a, t, (r + ' — ' if r else '') + when, src)


# --- Ida B.: the Spotify playlist of her Instagram picks ---
def spotify():
    s = get('https://open.spotify.com/embed/playlist/3WJi0pV9ETXTjLNrzRauTs')
    m = re.search(r'"trackList":(\[.*?\])\s*,\s*"', s or '', re.S)
    if not m: return
    try: tl = json.loads(m.group(1))
    except Exception: return
    for t in tl:
        add('ida', 'Instagram', t.get('subtitle', ''), t.get('title', ''),
            'In the Spotify compilation of her Instagram posts (unofficial)', 'https://open.spotify.com/playlist/3WJi0pV9ETXTjLNrzRauTs')


# --- Mauk Tenieb: Openwhyd ---
def openwhyd():
    s = get('https://openwhyd.org/mauktenieb?format=json&limit=2000')
    if not s: return
    try: posts = json.loads(s)
    except Exception: return
    for p in posts:
        e = p.get('eId', '')
        if not e.startswith('/yt/'): continue
        a, t = split_at(p.get('name', ''))
        pl = p.get('pl') or {}
        add('mau', 'Track', a, t, f"Openwhyd playlist « {pl.get('name', '')} »" if pl else 'Openwhyd',
            f"https://openwhyd.org/mauktenieb/playlist/{pl.get('id')}" if pl else 'https://openwhyd.org/mauktenieb', yt=e[4:15])


for f in (lowdown, spinitron, spotify, openwhyd):
    try: f()
    except Exception as e: print('source failed:', f.__name__, e)

c.extend(new)
json.dump(c, open(CAT, 'w', encoding='utf-8'), ensure_ascii=False)
V = os.path.join(D, 'veille.json')
v = json.load(open(V, encoding='utf-8'))
codes = ['pag', 'nab', 'wya', 'ida', 'mau', 'sig', 'alp', 'mic']
v.append({'date': TODAY, 'ajouts': len(new), 'bilan': ', '.join(f'{k} {log.get(k, 0)}' for k in codes)})
json.dump(v, open(V, 'w', encoding='utf-8'), ensure_ascii=False)

# the release note: new videos and playlists of 50
vids = [(x['title'], re.search(r'v=([\w-]{11})', x['yt']).group(1)) for x in new if x.get('direct')]
ids = [i for _, i in vids]
note = os.path.join(D, 'derniere-veille.md')
if ids:
    lines = [f'# Watch of {TODAY}', '', f'{len(ids)} new videos', '']
    lines += [f'- {t}: https://youtu.be/{i}' for t, i in vids]
    lines += [''] + ['Play all: https://www.youtube.com/watch_videos?video_ids=' + ','.join(ids[i:i + 50]) for i in range(0, len(ids), 50)]
    open(note, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
elif os.path.exists(note):
    os.remove(note)
print(len(new), 'new entries', log)
