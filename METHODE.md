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
| `type` | nature de la mention (« Diffusé dans The Lowdown », « Iceberg », « Top 40 », « Commenté »…) |
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

Le flux GitHub Actions `.github/workflows/veille.yml` lance Claude Code chaque lundi à 6 h 49 UTC. `veille/PROMPT.md` contient ses consignes exactes. Chaque lundi, la veille :

1. relit les sources de chaque curateur depuis la veille précédente ;
2. crée une fiche par nouvelle mention ;
3. cherche la vidéo YouTube de chaque nouveauté : identifiant donné par la source, sinon vidéo de l'album dans le classement RYM, sinon recherche web vérifiée par l'oEmbed de YouTube (titre de la vidéo conforme à l'artiste ou au titre, auteur extérieur aux curateurs) ;
4. lance `tools/recalcule.py`, puis `tools/cassettes.py` ;
5. commite « Veille du … » et publie une note de veille (release GitHub) qui liste les nouvelles vidéos et leurs listes de lecture YouTube, sans nommer de source.

Deux heures plus tard, le flux `curators` d'Insert Koin copie `data/kg-vhs-curations.js` dans le magnétoscope et renouvelle le cache du site. Le flux `controle` vérifie les programmes à chaque modification du dépôt. La page https://mauktenieb.github.io/curators/ affiche le catalogue, le classement général et les cassettes.

Un site qui refuse la lecture automatique sort de la veille de la semaine. TikTok refuse les robots : la veille lit Nabe et Microchip.ufo par ce que les moteurs de recherche en indexent.

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
