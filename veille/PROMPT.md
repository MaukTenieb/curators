# Instructions of the Monday watch (optional Claude Code step)

The workflow `.github/workflows/veille.yml` runs `tools/veille.py` every Monday: it reads Adam Sigmund, Ida B. and Mauk Tenieb's Openwhyd with zero secret. When the repo has the secret `CLAUDE_CODE_OAUTH_TOKEN`, Claude Code then follows this text for the other curators. The workflow recomputes the ranking, presses the cassettes, commits and publishes the release note; Claude Code edits `data/` and `tools/self_ids.json` only, and leaves the commit to the workflow.

---

You run the Curators watch: the catalogue of the music that eight curators put forward by other artists. Work alone, in English. Read METHOD.md first.

## Rules

- One entry = the music of ANOTHER artist put forward by a curator (a track played, an album ranked, reviewed or cited, an iceberg tier, a release picked for a label). Every entry names its artist (`artist`). Zero « container » entry (profile, interview, show, channel, account, playlist with zero artist named).
- Zero self-promotion: what a curator publishes about their own work (Marc-Édouard Nabe's books, texts and readings; Dominique Pagani's playlists, where a playlist given to one artist becomes an « In a playlist » entry under that artist; the curators' own videos: Pagani Parle Musique, Musicosophie, Alpha-27 Essentials and Review, Wyattxhim's videos). Those videos go in `src`; `yt` leads to the other artist's music. Add every new curator video id to `tools/self_ids.json`.
- A curator's music picked by ANOTHER curator stays in.
- One entry per curator and title: same `c` and same `title` → merge the `meta`.
- A site that refuses programs: move to the next one; one try per site.
- Types and comments in English; curators under their full names (Dominique Pagani, Marc-Édouard Nabe); titles of works as their authors wrote them.

## 1. Read

`data/catalogue.json` (entries), `data/veille.json` (log), `data/rym.json` (Rate Your Music top 10,000: `albums` = {rank: [artist, title, year, rating, genres, YouTube id, Bandcamp, Spotify, RYM URL]}). Entry: {c,type,title,meta,src,yt,direct,ytvia?,bc,bcdirect?,sp?,rym?,rymArtist?,rank?,artist,key,genres,fam,rr,cross,added,ep?}. Codes: pag Dominique Pagani, nab Marc-Édouard Nabe, wya Wyattxhim, ida Ida B. (Sly Ida), mau Mauk Tenieb, alp Alpha-27, sig Adam Sigmund, mic Microchip.ufo.

## 2. Harvest since the last date of `data/veille.json` (tools/veille.py already read sig, ida and Openwhyd)

- wya: Wyattxhim's iceberg and top lists on albumoftheyear.org, https://www.last.fm/music/Wyattxhim/+tracks ; types « Iceberg », « Top », « Video subject ».
- alp: search « site:youtube.com Alpha-27 Essentials » and « [Alpha-27 Review] », checked through https://www.youtube.com/oembed?url=<video>&format=json (author Alpha-27); type « Essentials », src = Alpha-27's video, yt = the artist's music.
- pag: https://www.dominiquepagani.fr/videos/?vue=toutes and /noms/<slug>/ ; types « Cited in the workshops », « Work cited », « Commented on » (title = artist, meta = the video where Dominique Pagani comments on them, src = the video).
- nab: wikinabia.com and the indexed captions of his TikTok videos; a book or text by Marc-Édouard Nabe → a « Subject of a book or text » entry under the artist it deals with.
- mic: tiktok.com/@microchip.ufo, through what search engines index; type « Archived ».
- mau: https://docs.google.com/document/d/1t64ZGJEhTHis_Dwh3UIIMFIJU5kkDx2Wi_a8fSENHhU/export?format=txt (follow the redirect; update « Top 40 » and « Side paths »).

## 3. Links

- `bc`: the Bandcamp page when known (`bcdirect` true), else https://bandcamp.com/search?q=<artist title> (empty for classical music). Artist in `rym.json`: `genres` = its first 2 primary genres, `rym` = {rank,url} when the album is there, Bandcamp and Spotify links of its best-ranked album. `added` = today.
- A YouTube video for each new entry: `yt` = https://www.youtube.com/watch?v=ID, `direct` true. Order: the id given by the source (when it belongs to someone other than a curator); else the YouTube id of `rym.json` for that album, or of the artist's best-ranked album (`ytvia` = « <album> (<year>), the artist's best-ranked album on RYM with a YouTube link »); else a search « site:youtube.com <artist> <title> », then https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=<ID>&format=json: keep the video when its title contains the artist or the title and its author is someone other than a curator. Zero video to check → `yt` = YouTube search, `direct` false.
- An entry with zero genre after all this: give it 2 realistic genres.

## 4. Write

- `data/catalogue.json`: the new entries added to the array.
- `data/veille.json`: add your count to today's line written by tools/veille.py (« code n » per curator).
- First Monday of the month: refresh `data/rym.json` from the repo sameraslan/recmyrecord (data-pipeline/catalog/source/rym10k_sheet.csv), same structure, every curator video id taken out.
- `data/derniere-veille.md` (written by tools/veille.py): add your new videos in the same form, « - Artist · Title: https://youtu.be/ID », and the « Play all » links, 50 ids at most per link.
