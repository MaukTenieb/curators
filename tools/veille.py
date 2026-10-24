"""Monday watch, with zero secret and zero AI: reads the curators' sources a program can read,
adds one entry per new mention, finds a YouTube video for each, logs the watch.
Sources: Adam Sigmund (The Lowdown on Mad Wasp Radio, archive.org), Ida B. (KALX on Spinitron, her Instagram
picks on Spotify), Mauk Tenieb (Openwhyd), Alpha-27 and Wyattxhim (their YouTube channels, video descriptions),
Marc-Édouard Nabe (WikiNabia, MediaWiki API), Dominique Pagani (his index of names, domain « musique »),
Microchip.ufo (The Micro Archives on TikTok, through the DuckDuckGo index). Then a real YouTube video
replaces the search link of up to VEILLE_RESOLVE entries (default 400), best-ranked first.
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



# --- the five other curators, read by program ---
BROWSER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
           'Accept-Language': 'en-US,en;q=0.8', 'Cookie': 'CONSENT=YES+1; SOCS=CAI'}


def getb(url, data=None, tries=3):
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers=BROWSER, data=data)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception:
            continue
    return None


def oembed(vid):
    s = get('https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v=' + vid, tries=2)
    try: return json.loads(s) if s else None
    except Exception: return None


def channel_videos(cid):
    """the latest videos of a YouTube channel (about 30), newest first"""
    s = getb(f'https://www.youtube.com/channel/{cid}/videos') or ''
    return list(dict.fromkeys(re.findall(r'"videoId":"([\w-]{11})"', s)))


def watch(vid):
    """title and description of a YouTube video"""
    s = getb('https://www.youtube.com/watch?v=' + vid) or ''
    m = re.search(r'ytInitialPlayerResponse\s*=\s*(\{.*?\});(?:var |</script>)', s, re.S)
    try:
        vd = json.loads(m.group(1))['videoDetails']
        if vd.get('shortDescription'): return vd.get('title', ''), vd['shortDescription']
    except Exception:
        pass
    # the page of a server address may hold a bot check: the player API (web client) still gives title and description
    body = json.dumps({'context': {'client': {'clientName': 'WEB', 'clientVersion': '2.20250101.00.00', 'hl': 'en'}}, 'videoId': vid}).encode()
    try:
        req = urllib.request.Request('https://www.youtube.com/youtubei/v1/player?prettyPrint=false', data=body,
                                     headers={'Content-Type': 'application/json', 'User-Agent': BROWSER['User-Agent']})
        with urllib.request.urlopen(req, timeout=30) as r:
            vd = json.loads(r.read().decode('utf-8', 'replace')).get('videoDetails', {})
        if vd.get('title'): return vd['title'], vd.get('shortDescription', '')
    except Exception:
        pass
    # the watch-next API: the description, its links as runs over the text
    try:
        req = urllib.request.Request('https://www.youtube.com/youtubei/v1/next?prettyPrint=false', data=body,
                                     headers={'Content-Type': 'application/json', 'User-Agent': BROWSER['User-Agent']})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode('utf-8', 'replace'))
        found = []

        def walk(o):
            if isinstance(o, dict):
                if 'attributedDescription' in o and isinstance(o['attributedDescription'], dict): found.append(o['attributedDescription'])
                for v in o.values(): walk(v)
            elif isinstance(o, list):
                for v in o: walk(v)
        walk(d)
        if found:
            ad = found[0]
            u16 = ad.get('content', '').encode('utf-16-le')
            runs = []
            for cr in ad.get('commandRuns', []):
                ep = (cr.get('onTap', {}).get('innertubeCommand', {}) or {}).get('watchEndpoint', {})
                if ep.get('videoId'): runs.append((cr['startIndex'], cr['length'], ep['videoId']))
            for st, ln, v in sorted(runs, reverse=True):
                u16 = u16[:st * 2] + ('https://youtu.be/' + v).encode('utf-16-le') + u16[(st + ln) * 2:]
            text = u16.decode('utf-16-le')
            o = oembed(vid)
            return (o or {}).get('title', ''), text
    except Exception:
        pass
    o = oembed(vid)
    return (o or {}).get('title', ''), ''


CURATOR_CHANNELS = {'UCHTbTDtqLarvm62J83beZQA', 'UC0ZGpaIfJX8xJ_gHI9Zqaww'}


def new_self(vid):
    """a curator's own video: provenance only, kept out of the listening links"""
    if vid not in SELF:
        SELF.add(vid)
        NEW_SELF.append(vid)


NEW_SELF = []
NAMES = {}
for rk, a in R['albums'].items():
    if len(a[0]) >= 4: NAMES.setdefault(a[0], 1)
for x in c:
    if len(x.get('artist', '')) >= 4: NAMES.setdefault(x['artist'], 1)
GENRES = {norm(g) for a in R['albums'].values() for g in a[4].split(',')}
for n in [n for n in NAMES if norm(n) in GENRES or len(n) < 5]: NAMES.pop(n)
for k in ('Alpha-27', 'Wyattxhim', 'Mauk Tenieb', 'Dominique Pagani', 'Marc-Édouard Nabe', 'Microchip.ufo', 'Ida B.', 'Adam Sigmund'):
    NAMES.pop(k, None)


def names_in(text):
    """artists of the catalogue or of the RYM top 10,000 named in a text"""
    found = []
    for n in NAMES:
        if n in text and re.search(r'(?<![\w])' + re.escape(n) + r'(?![\w])', text):
            found.append(n)
    found.sort(key=len, reverse=True)
    out = []
    for n in found:
        if not any(n in o for o in out): out.append(n)
    return out


# Alpha-27: the « Alpha-27 Essentials » and review episodes of his channel
def alpha27():
    for vid in channel_videos('UCHTbTDtqLarvm62J83beZQA'):
        src = 'https://www.youtube.com/watch?v=' + vid
        new_self(vid)
        if src in srcs: continue
        title, desc = watch(vid)
        if not re.search(r'essentials|review|top \d+', title, re.I): continue
        head = re.sub(r'\[.*?\]|\(.*?\)', '', title).strip()
        names = []
        m = re.match(r'(.+?)\s+[-–]\s+(.+?)(?:\s+(?:REDUX\s+)?REVIEW)?$', head, re.I)
        if m and not re.match(r'alpha-27$', m.group(1), re.I):
            names = [(m.group(1).strip(), m.group(2).strip())]
        else:
            names = [(n, '') for n in names_in(title + '\n' + desc.split('My Bandcamp')[0])][:6]
        for a, t in names:
            add('alp', 'Essentials', a, t, f'In the Alpha-27 video « {title} »', src)


# Wyattxhim: each video description lists the music it plays, with a YouTube link per piece
def wyattxhim():
    for vid in channel_videos('UC0ZGpaIfJX8xJ_gHI9Zqaww'):
        src = 'https://www.youtube.com/watch?v=' + vid
        new_self(vid)
        if src in srcs: continue
        title, desc = watch(vid)
        label = ''
        for line in desc.split('\n'):
            line = line.strip()
            if not line: continue
            m = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})', line)
            if not m:
                label = line
                continue
            lab, label = label, ''
            if re.match(r'background music|patreon|merch|other ', lab, re.I): continue
            yid = m.group(1)
            if yid in SELF: continue
            o = oembed(yid)
            if not o: continue
            otitle = o.get('title', '')
            clean = re.sub(r'\s*[\(\[][^\)\]]*(full|album|official|remaster|hq|hd|\d{4})[^\)\]]*[\)\]]', '', otitle, flags=re.I)
            clean = re.sub(r'\s+full\s+album.*$', '', clean, flags=re.I).strip()
            a, t = split_at(clean)
            mq = re.match(r'^(.+?)\s*"(.+?)"', clean)
            if not t and mq:
                a, t = re.sub(r'\(.*?\)', '', mq.group(1)).strip(), mq.group(2)
            t = re.sub(r'\s+(HD|HQ)$', '', t)
            if not t:
                a = lab.rstrip(' :') if lab and not re.match(r'^\d+\.?$', lab) else o.get('author_name', '').replace(' - Topic', '')
                t = clean
            add('wya', 'Video subject', a, t, f'Played in the Wyattxhim video « {title} »', src, yt=yid)


# Marc-Édouard Nabe: the musicians of WikiNabia (MediaWiki API)
def nabe():
    for cat in ('Jazzmen', 'Batteurs', 'Inspirations'):
        cont = ''
        while True:
            s = get('https://wikinabia.com/api.php?action=query&list=categorymembers&cmlimit=500&format=json&cmtitle='
                    + q('Catégorie:' + cat) + cont)
            if not s: break
            d = json.loads(s)
            for p in d['query']['categorymembers']:
                if p['ns'] != 0: continue
                t = p['title']
                src = 'https://wikinabia.com/' + t.replace(' ', '_')
                if src in srcs: continue
                if cat == 'Inspirations' and t not in NAMES: continue   # Inspirations mixes writers and painters: musicians only
                add('nab', 'Pantheon', re.sub(r'\s*\(.*?\)\s*$', '', t), '', f'WikiNabia entry « {cat} »', src)
            if 'continue' not in d: break
            cont = '&cmcontinue=' + q(d['continue']['cmcontinue'])


# Dominique Pagani: the musicians of his index of names (domain « musique »)
def pagani():
    s = getb('https://www.dominiquepagani.fr/noms/') or ''
    for path, name, n in re.findall(r'data-dom="musique" href="(/noms/[^"]+/)" title="([^"]+)">[^<]*<small>(\d+)</small>', s):
        src = 'https://www.dominiquepagani.fr' + path
        if src in srcs: continue
        name = html.unescape(name)
        n = int(n)
        add('pag', 'Cited in the workshops', re.sub(r'\s*\(.*?\)\s*$', '', name), '',
            f"Cited {n} time{'s' if n > 1 else ''} in Dominique Pagani's workshops", src)


# Microchip.ufo: The Micro Archives on TikTok, read through the search engine's index
def microchip():
    seen_v = set()
    for off in range(0, 300, 30):
        body = urllib.parse.urlencode({'q': 'site:tiktok.com/@microchip.ufo', 's': str(off)}).encode()
        s = getb('https://html.duckduckgo.com/html/', data=body) or ''
        hits = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?class="result__snippet"[^>]*>(.*?)</a>', s, re.S)
        if not hits:   # the lite page of the same index
            s = getb('https://lite.duckduckgo.com/lite/', data=body) or ''
            hits = re.findall(r'class=.result-link.[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?class=.result-snippet.[^>]*>(.*?)</td>', s, re.S)
        if not hits: break
        for href, ht, sn in hits:
            href = urllib.parse.unquote(href)
            m = re.search(r'tiktok\.com/@microchip\.ufo/video/(\d+)', href)
            if not m or m.group(1) in seen_v: continue
            seen_v.add(m.group(1))
            src = 'https://www.tiktok.com/@microchip.ufo/video/' + m.group(1)
            if src in srcs: continue
            text = html.unescape(re.sub(r'<[^>]+>', '', sn))
            mm = re.search(r'"+([^"]+?)" by (.+?) from the (?:album|EP|single) (.+?)\.(?:\s|$|")', text)
            if not mm: continue
            tags = [t for t in re.findall(r'#(\w+)', text) if t.lower() not in ('california',) and t.lower() != norm(mm.group(2)).replace(' ', '')]
            g = {} if BEST.get(norm(mm.group(2))) else {'genres': tags[:3]}
            add('mic', 'Archived', mm.group(2), mm.group(1), f'The Micro Archives, from the album « {mm.group(3)} »', src, extra=g)


# a real YouTube video for each entry that still has only a search link
def resolve(limit):
    todo = [x for x in c + new if not x.get('direct') and x.get('artist')]
    todo.sort(key=lambda x: (-len(x.get('cross') or []), x.get('rr') or 1e9))
    done = 0
    for x in todo[:limit]:
        a = x['artist']
        t = x['title'].split(' · ', 1)[1] if ' · ' in x['title'] else ''
        t = re.sub(r'^s\d{5}\s*', '', t)
        s = getb('https://www.youtube.com/results?search_query=' + q((a + ' ' + t).strip()))
        if not s: continue
        for vid in list(dict.fromkeys(re.findall(r'"videoId":"([\w-]{11})"', s)))[:5]:
            if vid in SELF: continue
            o = oembed(vid)
            if not o: continue
            ot, au = norm(o.get('title', '')), norm(o.get('author_name', ''))
            if norm(a) and (norm(a) in ot or norm(a) in au) and (not t or norm(t)[:12] in ot or norm(a) in au):
                x['yt'] = 'https://www.youtube.com/watch?v=' + vid
                x['direct'] = True
                x.pop('ytvia', None)
                done += 1
                break
    return done


for f in (lowdown, spinitron, spotify, openwhyd, alpha27, wyattxhim, nabe, pagani, microchip):
    n0 = len(new)
    try: f()
    except Exception as e: print('source failed:', f.__name__, e)
    print(f.__name__, len(new) - n0, 'new entries')

try: found = resolve(int(os.environ.get('VEILLE_RESOLVE', '400')))
except Exception as e: found = 0; print('resolve failed:', e)
print(found, 'search links replaced by a checked video')
c.extend(new)
if NEW_SELF:
    P = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'self_ids.json')
    json.dump(sorted(SELF), open(P, 'w', encoding='utf-8'), ensure_ascii=False)
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
