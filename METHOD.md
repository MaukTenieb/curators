# Curators: method

Curators lists the music that eight curators put forward by other artists. Every Monday a watch reads their public sources, adds the new picks to the catalogue, ranks the artists and presses VHS cassettes for the deck of Insert Koin (https://mauktenieb.github.io/insertkoin/). By Mauk Tenieb & Korhogo. In French: [METHODE.md](METHODE.md).

## Curators and sources

| Code | Curator | Sources | Read by |
|---|---|---|---|
| `pag` | Dominique Pagani | workshops, *Pagani Parle Musique*, *Musicosophie* (dominiquepagani.fr, pages of the names cited) | Claude Code |
| `nab` | Marc-Édouard Nabe | wikinabia.com, indexed captions of his TikTok videos | Claude Code |
| `wya` | Wyattxhim | YouTube channel; icebergs and tops on albumoftheyear.org; last.fm | Claude Code |
| `ida` | Ida B. (Sly Ida) | KALX shows on Spinitron, WRIR, the Spotify playlist of her Instagram picks | program |
| `mau` | Mauk Tenieb | Openwhyd (program); Top 40 and Side paths, a public document (Claude Code) | program, Claude Code |
| `alp` | Alpha-27 | *Alpha-27 Essentials* and *Alpha-27 Review* videos | Claude Code |
| `sig` | Adam Sigmund | *The Lowdown on Mad Wasp Radio* (archive.org), the sub65 netlabel | program |
| `mic` | Microchip.ufo | *The Micro Archives* (tiktok.com/@microchip.ufo) | Claude Code |

Rate Your Music's top 10,000 albums (repo sameraslan/recmyrecord) gives ranks and genres.

## What an entry records

One entry = one piece of another artist's music that one curator puts forward: a track played, an album ranked, reviewed or cited, an iceberg tier, a release picked for a label. Each entry names its artist.

The watch leaves out three things:

- containers: profile, interview, show, channel, account, playlist with zero artist named;
- self-promotion: a curator's books, texts, readings, playlists and own videos. A playlist given to one artist becomes an entry under that artist; a book or text becomes an entry under the artist it deals with; a curator's video counts as provenance (`src`); the listening link (`yt`) leads to the other artist's music. `tools/self_ids.json` lists the curators' videos;
- duplicates: same curator, same title. The watch merges the mentions.

## Entry fields

`data/catalogue.json` holds an array of entries:

| Field | Content |
|---|---|
| `c` | curator code |
| `type` | kind of mention (« Played on The Lowdown », « Iceberg », « Top 40 », « Commented on »…) |
| `title` | « Artist · Title » |
| `artist` | artist, required |
| `meta` | context: show, rank, date, video where the artist comes up |
| `src` | source page of the mention |
| `yt`, `direct` | YouTube link; `direct` true for a checked video, false for a search |
| `ytvia` | album the video comes from, when it comes from the RYM ranking |
| `bc`, `bcdirect`, `sp` | Bandcamp (page or search), Spotify |
| `rym`, `rymArtist`, `rr` | RYM rank of the album, of the artist, best rank kept |
| `genres`, `fam` | genres, genre family |
| `key`, `cross` | normalised artist, codes of the curators who share this artist |
| `added`, `ep`, `rank` | date added, show number, rank in a list |

`data/veille.json` logs each watch: date, number of entries added, count per curator.

## The Monday watch

The workflow `.github/workflows/veille.yml` starts every Monday at 6:49 UTC.

1. `tools/veille.py` reads, with zero secret: the new episodes of The Lowdown on archive.org, the new KALX shows of Ida B. on Spinitron, her Spotify playlist, Mauk Tenieb's Openwhyd. It adds one entry per new mention, takes the YouTube id the source gives or the video of the artist's best-ranked album in `rym.json`, else a YouTube search link.
2. When the repo has the secret `CLAUDE_CODE_OAUTH_TOKEN`, Claude Code follows [veille/PROMPT.md](veille/PROMPT.md) for the other curators.
3. `tools/recalcule.py`, then `tools/cassettes.py`.
4. The workflow commits « Watch of … » and publishes a release with the new videos and their YouTube playlists.

At 9:19 UTC, the workflow `curators` of Insert Koin copies `data/kg-vhs-curations.js` into its VHS deck. The workflow `controle` checks the programs on every change. The page https://mauktenieb.github.io/curators/ shows the catalogue, the rankings and the cassettes.

## General ranking

1. number of curators who put the artist forward;
2. best rank in Rate Your Music's top 10,000;
3. number of entries.

## Genre families

`tools/recalcule.py` puts each entry in one family: lo-bit netlabels; game and film music; jazz; classical and early music; metal; industrial, noise and experimental; hip-hop; electronic; rock and punk; pop, soul and R&B; folk, chanson and world music. The first genre of an entry counts double. An entry with zero genre takes its artist's RYM genres; the rest goes to the Pot-pourri cassette.

## Cassettes

`tools/cassettes.py` writes `data/vhs-cassettes.json` and `data/kg-vhs-curations.js`, which the VHS deck of Insert Koin loads in its CURATORS row. Labels name genres and dates only.

- Top 60: one track per artist, the first 60 artists of the ranking with a video.
- One compilation per genre: every video of a genre, 99 at most, in ranking order; Pot-pourri gathers the genres under 4 videos.
- Dated cassettes: one per genre and per watch; the shelf keeps the latest 10.

Each label shows, in marker, a genre and a date of the French Republican calendar (the day the cassette last changed), in an ink for each genre. Each cassette exports to CSV, JSON, XLSX, TXT and MD, with its criteria, and opens as YouTube playlists of 50 videos, YouTube's limit.

## Run by hand

```
python3 -I tools/veille.py data YYYY-MM-DD
python3 -I tools/recalcule.py data
python3 -I tools/cassettes.py data YYYY-MM-DD
```

## Rights

Code (`tools/`, workflows): MIT. Data and method: CC BY 4.0. Credit: Mauk Tenieb & Korhogo. Titles, artist names and linked works belong to their rights holders. Training of AI models: reserved. See [LICENSE](LICENSE).
