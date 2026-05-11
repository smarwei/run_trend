# 31 — Debug-Skripte und Streamer aus dem Repo-Root räumen

**Priorität:** P0
**Kategorie:** Hygiene

## Problem

Im Projektwurzelverzeichnis liegen Entwickler-Artefakte mit gemischtem
Tracking-Status:

- `debug_hr_actual.py` — getrackt seit `b2b0b4e`
- `debug_hr_zones.py` — getrackt seit `b2b0b4e`
- `debug_race_predictions.py` — getrackt seit `b2b0b4e`
- `resume` — untracked, lokaler Scratchpad
- `tmp_resume` — untracked, lokaler Scratchpad

Die drei `debug_*.py` haben außerdem stale `from app.*`-Imports aus der
Zeit vor dem Repo-Rename `app/` → `run_trend/`, würden also beim
Aufruf sofort mit `ModuleNotFoundError` knallen. Fünf Dateien
Wurzelrauschen für jeden Reader, der das Repo zum ersten Mal öffnet —
und Risiko, dass beim nächsten `git add .` etwas mitwandert, was nicht
soll.

## Lösungsansatz

Zwei Optionen kombinieren:

1. **Verschieben in `scripts/dev/`** falls die Debug-Skripte als Werkzeug
   weiter nützlich sind (Reproduktion von HR-Edge-Cases, Race-Predictor-
   Plausibilität). Repo-Root bleibt sauber, Werkzeug bleibt versioniert.
2. **In `.gitignore`** für die `resume`/`tmp_resume`-Dateien, die nach
   reinen Lokal-Scratchpads aussehen.

Falls die Debug-Skripte schon erledigt und obsolet sind: ersatzlos löschen.

## Acceptance

- [x] `debug_*.py`-Skripte in `scripts/dev/` einsortiert (verschoben,
      nicht gelöscht — Tracking-Historie bleibt)
- [x] `resume` / `tmp_resume` per `.gitignore` ausgeblendet
- [x] `git status` zeigt keine unbeabsichtigt untracked Files im Root mehr
- [x] `scripts/dev/README.md` neu, dokumentiert Zweck und Aufruf der
      Skripte

## Annahmen

- Keine CI-Pipeline ruft die Debug-Skripte auf (Grep zeigt keine
  Referenzen in `flake.nix`, `de.arneweiss.RunTrend.json` etc.).
- `resume` / `tmp_resume` sind keine Bewerbungs-PDFs sondern Scratchpads;
  falls doch versehentlich abgelegt: ignorieren, nicht committen.

## Dateien

- Repo-Root: 5 Files (3× `mv` nach `scripts/dev/`, 2× per `.gitignore`)
- `.gitignore`
- `scripts/dev/README.md` (neu)
- `tests/test_repo_hygiene.py` (neu)

## Status / Fortschritt

**Vollständig umgesetzt.**

- ✅ `scripts/dev/` angelegt; `debug_hr_actual.py`, `debug_hr_zones.py`,
  `debug_race_predictions.py` per `mv` dorthin verschoben. Git sieht das
  als Rename (`D` an alter Stelle plus untracked an neuer); beim Commit
  detektiert `git diff -M` die Verschiebung automatisch und behält die
  Historie.
- ✅ Stale `from app.*`-Imports per `sed` auf `from run_trend.*`
  umgestellt. AST-Smoke-Test (`ast.parse`) bestätigt syntaktisch
  korrektes Python; tiefer reichende API-Drift seit dem ursprünglichen
  Commit ist Sache eines Folge-Tickets oder einer Maintenance-Session.
- ✅ `scripts/dev/README.md` neu: erklärt Zweck (Diagnose-Werkzeuge,
  nicht App-Bestandteil), Aufruf via `nix develop -c python …` und
  Maintenance-Hinweis ("Treat any error as needs maintenance").
- ✅ `.gitignore` um zwei Zeilen `resume` und `tmp_resume` erweitert
  (oberhalb des Python-Blocks, mit Ticket-Verweis im Kommentar).
- ✅ `git status` zeigt am Root jetzt nur noch erwartete WIP-Files (die
  bestehenden T22-Charts plus T23–T31-Änderungen) und `scripts/`,
  `tickets/`, `tests/` mit den neuen Files — keinen versehentlichen
  Scratchpad mehr.
- ✅ Neuer `tests/test_repo_hygiene.py` mit 4 Cases: kein `debug_*.py`
  im Root, `scripts/dev/` existiert mit README, alle drei verschobenen
  Skripte parsen syntaktisch, `resume`/`tmp_resume` als Whole-Line-
  Entries in `.gitignore`. `pytest tests/` 290 grün (286 + 4 neue).

### Annahmen

- Die drei Debug-Skripte haben Wert als versionierte Werkzeuge (sie
  spiegeln nachvollziehbar, wie HR-Edge-Cases früher debuggt wurden) —
  daher Verschieben statt Löschen. Sollten sie beim nächsten echten
  Debug-Lauf vollständig nutzlos sein, kann ein Folge-Cleanup sie
  ersatzlos kippen.
- `resume`/`tmp_resume` enthalten je nur eine Zeile mit einem
  `claude --resume <id>`-Kommando — eindeutig persönliche Helper, keine
  Bewerbungs-PDFs. `.gitignore` statt `git rm` belässt sie lokal, falls
  Arne sie weiterhin nutzt.
