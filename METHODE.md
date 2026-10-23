# Curators — méthode

Curators recense la musique que huit curateurs mettent en avant, chez d'autres artistes. Une veille automatique relit leurs sources publiques chaque lundi, ajoute les nouveautés au catalogue, classe les artistes et presse des cassettes VHS pour le magnétoscope d'Insert Koin (https://mauktenieb.github.io/insertkoin/).

## Les curateurs et leurs sources

| Code | Curateur | Sources lues |
|---|---|---|
| `pag` | Dominique Pagani | ateliers, *Pagani Parle Musique*, *Musicosophie* (dominiquepagani.fr, pages des noms cités) |
| `nab` | Marc-Édouard Nabe | wikinabia.com, légendes indexées de ses vidéos TikTok |
| `wya` | Wyattxhim | chaîne YouTube ; icebergs et tops sur albumoftheyear.org ; sonichits.com, last.fm |
| `ida` | Ida B. (Sly Ida) | émissions KALX sur Spinitron, WRIR, playlist Spotify de ses choix Instagram |
| `mau` | Mauk Tenieb | Openwhyd, Top 40 et Chemins de traverse (document public) |
| `alp` | Alpha-27 | vidéos *Alpha-27 Essentials* et *Alpha-27 Review* |
| `sig` | Adam Sigmund | *The Lowdown on Mad Wasp Radio* (archive.org), netlabel sub65 |
| `mic` | Microchip.ufo | *The Micro Archives* (tiktok.com/@microchip.ufo) |

Le top 10 000 des albums de Rate Your Music (dépôt sameraslan/recmyrecord) fournit les rangs et les genres.

## Ce qu'une fiche recense

Une fiche correspond à la musique d'un autre artiste qu'un curateur propose : un morceau diffusé, un album classé, critiqué ou cité, une case d'iceberg, une sortie choisie pour un label. Chaque fiche nomme son artiste.

La veille écarte trois choses :

- les conteneurs : profil, entretien, émission, chaîne, compte, playlist sans artiste ;
- l'autopromotion : livres, textes et lectures d'un curateur, ses playlists, ses propres vidéos. Une playlist consacrée à un artiste devient une fiche au nom de cet artiste ; un livre ou un texte devient une fiche au nom de l'artiste qu'il traite ; la vidéo d'un curateur sert de provenance (`src`), jamais de lien d'écoute (`yt`). La liste `tools/self_ids.json` recense les vidéos de curateurs ;
- les doublons : même curateur et même titre. La veille fusionne alors les mentions.

La musique d'un curateur choisie par un autre curateur reste au catalogue.

## Le format d'une fiche

`data/catalogue.json` contient un tableau de fiches :

| Champ | Contenu |
|---|---|
| `c` | code du curateur |
| `type` | nature de la mention, en anglais (« Played on The Lowdown », « Iceberg », « Top 40 », « Commented on »…) |
| `title` | « Artiste · Titre » |
| `artist` | artiste, obligatoire |
| `meta` | contexte : émission, rang, date, vidéo où l'artiste est commenté |
| `src` | page source de la mention |
| `yt`, `direct` | lien YouTube ; `direct` vaut `true` pour une vidéo vérifiée, `false` pour une recherche |
| `ytvia` | album d'où provient la vidéo quand elle vient du classement RYM |
| `bc`, `bcdirect`, `sp` | Bandcamp (page ou recherche), Spotify |
| `rym`, `rymArtist`, `rr` | rang RYM de l'album, de l'artiste, meilleur rang retenu |
| `genres`, `fam` | genres, famille de genres |
| `key`, `cross` | artiste normalisé, codes des curateurs qui partagent cet artiste |
| `added`, `ep`, `rank` | date d'ajout, numéro d'émission, rang dans une liste |

`data/veille.json` consigne chaque veille : date, nombre d'ajouts, bilan par curateur.

## La veille du lundi

Le flux `.github/workflows/veille.yml` part chaque lundi à 6 h 49 UTC.

1. `tools/veille.py` lit, sans aucun secret : les nouveaux épisodes de The Lowdown sur archive.org, les nouvelles émissions KALX d'Ida B. sur Spinitron, sa playlist Spotify, l'Openwhyd de Mauk Tenieb. Il ajoute une fiche par nouvelle mention et prend l'identifiant YouTube donné par la source, sinon la vidéo de l'album de l'artiste le mieux classé dans `rym.json`, sinon un lien de recherche YouTube.
2. Quand le dépôt a le secret `CLAUDE_CODE_OAUTH_TOKEN`, Claude Code suit `veille/PROMPT.md` pour les autres curateurs (Dominique Pagani, Marc-Édouard Nabe, Wyattxhim, Alpha-27, Microchip.ufo).
3. `tools/recalcule.py`, puis `tools/cassettes.py`.
4. Le flux commite « Watch of … » et publie une note de veille (release) avec les nouvelles vidéos et leurs listes de lecture YouTube.

À 9 h 19 UTC, le flux `curators` d'Insert Koin copie `data/kg-vhs-curations.js` dans le magnétoscope. Le flux `controle` vérifie les programmes à chaque modification. La page https://mauktenieb.github.io/curators/ affiche le catalogue, les classements et les cassettes. Version anglaise : [METHOD.md](METHOD.md).

## Le classement général

Le classement range les artistes selon trois critères successifs :

1. le nombre de curateurs qui les proposent ;
2. leur meilleur rang dans le top 10 000 de Rate Your Music ;
3. leur nombre de fiches.

## Les familles de genres

`tools/recalcule.py` range chaque fiche dans une famille : Netlabels lo-bit ; Musiques de jeux et de films ; Jazz ; Classique et musique ancienne ; Metal ; Industriel, bruit et expérimental ; Hip-hop ; Électronique ; Rock et punk ; Pop, soul et R&B ; Folk, chanson et musiques du monde. Le premier genre d'une fiche compte double. Une fiche sans genre reçoit les genres RYM de son artiste, puis une famille propre à sa source.

## Les cassettes

`tools/cassettes.py` écrit `data/vhs-cassettes.json` et `data/kg-vhs-curations.js`, que le magnétoscope d'Insert Koin charge dans sa rangée CURATORS. Les étiquettes nomment des genres et des dates, jamais un curateur.

- Top 60 : un morceau par artiste, les 60 premiers artistes du classement disposant d'une vidéo.
- Compilations par genre : toutes les vidéos d'un genre, 99 au plus, dans l'ordre du classement ; Pot-pourri regroupe les genres de moins de 4 vidéos.
- Cassettes datées : une par genre et par veille ; le meuble garde les 10 dernières.

Chaque étiquette porte au feutre un genre et une date du calendrier républicain, celle du dernier changement de la cassette, d'une encre propre au genre. Le calendrier suit la règle d'Insert Koin : années III, VII, XI et XV sextiles, puis règle de Romme.

Chaque cassette s'exporte depuis le magnétoscope en CSV, JSON, XLSX, TXT et MD, avec ses critères, et s'ouvre en liste de lecture YouTube (50 vidéos par liste, limite de YouTube).

## Reproduire

```
python3 -I tools/recalcule.py data
python3 -I tools/cassettes.py data AAAA-MM-JJ
```

`data/rym.json`, facultatif, ajoute les rangs et les vidéos du classement RYM ; sans lui, les scripts gardent les rangs déjà inscrits dans les fiches.

## Licences

Code (`tools/`) : licence MIT. Données (`data/`) : CC BY 4.0. Les titres, artistes et liens restent la propriété de leurs ayants droit.
