# MTMIS — Loop Tool (GitHub Pages)

MTMIS Punjab vehicle lookup loop tool — number loop + date loop, aik dafa captcha.

## Live URL (GitHub Pages on karne ke baad)

`https://<tumhara-username>.github.io/<repo-ka-naam>/`

## GitHub Pages on karne ke steps (sirf pehli dafa)

1. GitHub par naya repository banao (naam jaise `mtmis-loop-tool`, Public).
2. Is folder ki saari files upload karo (Add file → Upload files).
3. Repository → **Settings** → **Pages** → Source: **Deploy from a branch** → Branch: **main**, folder **/ (root)** → Save.
4. 1–2 minute wait karo — phir upar wala URL khul jaye ga.

## Zaroori baat — bridge

- GitHub Pages **PHP nahi chalata**, is liye `mtmis-proxy.php` yahan kaam nahi kare ga
  (wo sirf PHP hosting jaise InfinityFree par chalta hai).
- Is liye **fresh captcha aur loop ke liye local bridge** chahiye:
  `mtmis-bridge.bat` double-click karo (is repo mein hai) — kaali window khuli
  rahe, phir tool page par **"Fresh Captcha Lao"** dabao.
- Bridge tumhare PC se MTMIS ko dekh sakta hai; server nahi dekh sakta.

## Files

- `mtmis-loop-tool.html` — asal tool
- `index.html` — root URL ko tool par bhejta hai
- `mtmis-bridge.py` + `mtmis-bridge.bat` — local bridge (PC par chalao)
- `mtmis-proxy.php` — NOT included; sirf PHP hosting ke liye hai
