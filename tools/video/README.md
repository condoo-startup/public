# Video Condoo (reel)

Due stili di reel 9:16 (1080×1920, 30 fps, ~20-22 s), con musica generata dal codice (nessun brano di terzi). Anteprime in `social/video-stili/`.

## K · Momenti in pixel (`pixel/`)
Pixel art originale (nessun personaggio o schermata di giochi esistenti). Un momento di vita del condominio raccontato con il palazzo in sezione, didascalie in alto (font Press Start 2P, OFL) e una funzione vera di Condoo.
- `story2.py` è l'episodio di esempio "Il giorno dell'assemblea". Per un nuovo episodio copia il file (es. `story_ascensore.py`), cambia scene in `frame(t)`, didascalie `cap(...)`, eventi sonori in `audio()` e `DUR`.
- `reel.py` contiene i mattoni comuni: `txt`, `sprite` (persone 16×16 con capelli e maglia), sintetizzatore (`sq`, `tri`, `add`, `note_f`).
- Anteprime: `python3 story_x.py stills` (crea `sheet2.png`), video: `python3 story_x.py full` (serve ffmpeg). Logica 180×320 ingrandita ×6 con NEAREST.

## L · Palazzo in 3D (`palazzo-3d/`)
Palazzo in three.js (r160) con camera che si muove tra tetto, piani e portone, schede dell'app che compaiono collegate a un punto del palazzo, passaggio dal giorno alla sera con le finestre che si accendono.
- `scene.html`: scena, camera (`KF` = [tempo, posizione, punto guardato]), punti (`A`), schede (`.card` + array `seg` = [id scheda, punto, inizio, fine]), didascalie, schermata finale.
- `render.js`: `node render.js stills 1 4 7` per i fotogrammi di controllo, `node render.js full 22` per il video (crea `v3d_tmp.mp4`, ~7 minuti con WebGL software). Usa Playwright già installato.
- `audio3d.py`: musica (accordi morbidi + arpeggio) e suoni su schede e movimenti. Poi `ffmpeg -i v3d_tmp.mp4 -i a3d.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest out.mp4`.

## Regole di contenuto
Solo funzioni reali (bacheca, segnalazioni con stati Bozza/Aperta/In lavorazione/Risolta/Chiusa visibili solo ad autore e amministratore, documenti per categoria, calendario con promemoria via email, ruoli per condominio). Esempi marcati "Esempio". Niente leggi, importi, date. Ultima schermata: logo e "Registrati gratis su condoo.eu".
