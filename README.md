# Curators

Curators lists the music that eight curators put forward by other artists, ranks those artists and presses VHS cassettes for the deck of [Insert Koin](https://mauktenieb.github.io/insertkoin/), row CURATORS.

By Mauk Tenieb & Korhogo. Page: https://mauktenieb.github.io/curators/ · method, in French: [METHODE.md](METHODE.md)

## Curators and sources

| Code | Curator | Sources |
|---|---|---|
| `pag` | Dominique Pagani | the workshops, *Pagani Parle Musique*, *Musicosophie* (dominiquepagani.fr) |
| `nab` | Marc-Édouard Nabe | wikinabia.com, the indexed captions of his TikTok videos |
| `wya` | Wyattxhim | the YouTube channel, its icebergs and tops on albumoftheyear.org |
| `ida` | Ida B. (Sly Ida) | her KALX shows on Spinitron, WRIR, the Spotify playlist of her Instagram picks |
| `mau` | Mauk Tenieb | Openwhyd, the Top 40 and its side paths |
| `alp` | Alpha-27 | the *Alpha-27 Essentials* and *Alpha-27 Review* videos |
| `sig` | Adam Sigmund | *The Lowdown on Mad Wasp Radio* (archive.org), the sub65 netlabel |
| `mic` | Microchip.ufo | *The Micro Archives* |

Ranks and genres come from Rate Your Music's top 10,000 albums ([sameraslan/recmyrecord](https://github.com/sameraslan/recmyrecord)). A curator's own books, playlists and videos count as provenance; the listening link leads to the other artist's music.

## Ranking

1. number of curators who put the artist forward;
2. best rank in Rate Your Music's top 10,000;
3. number of entries.

## Monday watch

1. The workflow `veille` starts on Monday at 6:49 UTC. Claude Code follows [veille/PROMPT.md](veille/PROMPT.md): it reads each source since the last watch, adds one entry per new mention and finds a YouTube video for each.
2. `tools/recalcule.py` recomputes the catalogue; `tools/cassettes.py` presses the cassettes.
3. The workflow commits « Veille du … » and publishes a release with the new videos and links that play them as YouTube playlists.
4. At 9:19 UTC, the workflow `curators` of Insert Koin copies `data/kg-vhs-curations.js` into its VHS deck.

The workflow `controle` runs both programs on every change.

## Cassettes

- Top 60: one track per artist, the first 60 artists of the ranking with a video.
- One compilation per genre: 99 videos at most, in ranking order; Pot-pourri gathers the genres under 4 videos.
- The 10 latest dated cassettes: one per genre and per watch.

Each label names a genre and a date of the French Republican calendar, in an ink for each genre.

## Files

| File | Content |
|---|---|
| `data/catalogue.json` | every entry: one piece of another artist's music, put forward by one curator |
| `data/veille.json` | log of the watches |
| `data/vhs-cassettes.json`, `data/kg-vhs-curations.js` | the cassettes for Insert Koin's deck |
| `data/rym.json` | Rate Your Music's top 10,000 albums, with YouTube, Bandcamp and Spotify links |
| `index.html` | the page: general ranking, Top 40, Rate Your Music by genre, tag clouds, catalogue, cassettes |
| `tools/recalcule.py` | cleans and recomputes the catalogue |
| `tools/cassettes.py` | presses the cassettes |
| `tools/self_ids.json` | the curators' own videos, kept out of the listening links |
| `veille/PROMPT.md` | instructions of the Monday watch |

## Run by hand

```
python3 -I tools/recalcule.py data
python3 -I tools/cassettes.py data YYYY-MM-DD
```

## Setup

The workflow `veille` reads one repository secret, `CLAUDE_CODE_OAUTH_TOKEN`, made with `claude setup-token`. GitHub Pages serves `index.html` from the branch `main`.

## Rights

Code (`tools/`, workflows): MIT. Data and method (`data/`, README, METHODE.md, PROMPT.md): CC BY 4.0. Credit: Mauk Tenieb & Korhogo. Titles, artist names and linked works belong to their rights holders. Training of AI models on this repository: reserved. Details: [LICENSE](LICENSE).
