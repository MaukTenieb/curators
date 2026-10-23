# Consignes de la veille du lundi

Claude Code suit ce texte chaque lundi, dans le flux GitHub Actions `.github/workflows/veille.yml`. Le flux recalcule ensuite le classement, presse les cassettes, commite et publie la note de veille ; Claude Code modifie seulement les fichiers de `data/` et `tools/self_ids.json`, sans commit.

---

Tu tiens la veille de Curators : le catalogue de la musique que huit curateurs mettent en avant chez d'autres artistes. Avance seul, sans question, en français. Lis d'abord METHODE.md.

## Règles

- Une fiche = la musique D'UN AUTRE ARTISTE proposée par un curateur (morceau diffusé, album classé, critiqué, cité, case d'iceberg, sortie choisie pour un label). Champ `artist` obligatoire. Jamais de fiche « conteneur » (profil, entretien, émission, chaîne, compte, playlist sans artiste).
- Pas d'autopromotion : rien de ce qu'un curateur publie sur son propre travail (livres, textes, lectures de Nabe ; playlists de Pagani — une playlist consacrée à un artiste devient une fiche « Mis en playlist » au nom de cet artiste ; vidéos du curateur lui-même : Pagani Parle Musique, Musicosophie, Alpha-27 Essentials/Review, vidéos Wyattxhim). Ces vidéos servent de `src`, jamais de `yt`. Ajoute tout nouvel identifiant de vidéo de curateur à `tools/self_ids.json`.
- La musique d'un curateur choisie par un AUTRE curateur reste admise.
- Pas de doublon : même `c` et même `title` → fusionne la `meta`.
- Un site qui refuse la lecture automatique : passe au suivant, sans le relancer ni le contourner.

## 1. Lire

`data/catalogue.json` (fiches), `data/veille.json` (journal), `data/rym.json` (top 10 000 de Rate Your Music : `albums` = {rang: [artiste, titre, année, note, genres, id YouTube, Bandcamp, Spotify, URL RYM]}). Fiche : {c,type,title,meta,src,yt,direct,ytvia?,bc,bcdirect?,sp?,rym?,rymArtist?,rank?,artist,key,genres,fam,rr,cross,added,ep?}. Codes : pag Pagani, nab Nabe, wya Wyattxhim, ida Sly Ida, mau Mauk Tenieb, alp Alpha-27, sig Adam Sigmund, mic Microchip.ufo.

## 2. Moissonner depuis la dernière date de `data/veille.json`

- sig : https://archive.org/advancedsearch.php?q=title%3A%28%22the+lowdown+on+mad+wasp+radio%22%29&fl%5B%5D=identifier&rows=400&output=json&sort%5B%5D=identifier+asc ; pour chaque identifiant dont aucune fiche n'a src=https://archive.org/details/<id>, lis https://archive.org/metadata/<id>/metadata (repli : /details/<id>) et extrais chaque titre : type « Diffusé dans The Lowdown », title « Artiste · Titre », meta « The Lowdown n° NNN », ep. Sorties d'autres artistes sur https://bbis.us/~newform/sub65/ (identifiant sNNNNN vérifié par https://archive.org/metadata/sNNNNN/metadata) : type « Sortie sub65 ».
- ida : https://spinitron.com/KALX/dj/169739/Sly-Ida (chaque titre des nouvelles émissions : type « Morceau ») ; https://open.spotify.com/embed/playlist/3WJi0pV9ETXTjLNrzRauTs (type « Instagram »).
- mau : https://openwhyd.org/mauktenieb et /playlist/1 à /10 ; https://docs.google.com/document/d/1t64ZGJEhTHis_Dwh3UIIMFIJU5kkDx2Wi_a8fSENHhU/export?format=txt (suis la redirection ; mets à jour « Top 40 » et « Chemins de traverse »).
- wya : listes albumoftheyear.org des icebergs et tops de Wyattxhim, https://www.last.fm/music/Wyattxhim/+tracks ; types « Iceberg », « Top », « Sujet de vidéo ».
- alp : recherche « site:youtube.com Alpha-27 Essentials » et « [Alpha-27 Review] », vérification par https://www.youtube.com/oembed?url=<vidéo>&format=json (auteur Alpha-27) ; type « Essentials », src = la vidéo d'Alpha-27, yt = musique de l'artiste.
- pag : https://www.dominiquepagani.fr/videos/?vue=toutes et /noms/<slug>/ ; types « Cité dans les ateliers », « Œuvre citée », « Commenté » (title = artiste, meta = vidéo où il est commenté, src = la vidéo).
- nab : wikinabia.com et légendes indexées de ses vidéos TikTok ; un livre ou un texte de Nabe → fiche « Sujet d'un livre ou texte » au nom de l'artiste qu'il traite.
- mic : tiktok.com/@microchip.ufo, par ce que les moteurs de recherche en indexent ; type « Archivé ».

## 3. Liens

- `bc` : page Bandcamp si connue (`bcdirect` true), sinon https://bandcamp.com/search?q=<artiste titre> (vide pour le classique). Artiste présent dans `rym.json` : `genres` = ses 2 premiers genres primaires, `rym` = {rank,url} si l'album y figure, liens Bandcamp et Spotify de son album le mieux classé. `added` = date du jour.
- Vidéo YouTube obligatoire pour chaque nouvelle fiche : `yt` = https://www.youtube.com/watch?v=ID, `direct` true. Ordre : identifiant donné par la source (s'il n'est pas d'un curateur) ; sinon id YouTube de `rym.json` pour cet album, ou de l'album le mieux classé de l'artiste (`ytvia` = « <album> (<année>), album de l'artiste le mieux classé sur RYM disposant d'un lien YouTube ») ; sinon recherche « site:youtube.com <artiste> <titre> » puis https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=<ID>&format=json : garde la vidéo si son titre contient l'artiste ou le titre et si son auteur reste extérieur aux curateurs. Rien de vérifiable → `yt` = recherche YouTube, `direct` false.
- Fiche restée sans genre après tout cela : donne-lui 2 genres réalistes.

## 4. Écrire

- `data/catalogue.json` : les nouvelles fiches ajoutées au tableau.
- `data/veille.json` : ajoute {date, ajouts, bilan}, bilan = « code n » par curateur (« pag 0, nab 2, … »).
- Premier lundi du mois : rafraîchis `data/rym.json` depuis le dépôt sameraslan/recmyrecord (data-pipeline/catalog/source/rym10k_sheet.csv) en gardant sa structure et en retirant tout identifiant de vidéo de curateur.
- `data/derniere-veille.md`, réécrit à chaque veille, sans nom de curateur ni de source :
  - ligne 1 : « # Veille du <date du calendrier républicain> » (règle d'Insert Koin, ex. 29 vendémiaire an 235 pour le 2026-10-20) ;
  - puis « N nouvelles vidéos » ;
  - puis une ligne par nouvelle vidéo : « - Artiste · Titre — https://youtu.be/ID » ;
  - puis « Tout lire : https://www.youtube.com/watch_videos?video_ids=ID1,ID2,… » (50 identifiants au plus par lien, un lien par tranche de 50).
  Aucune nouvelle vidéo → supprime `data/derniere-veille.md`.
