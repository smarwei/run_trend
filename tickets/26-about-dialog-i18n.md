# 26 — AboutDialog: `tr()` einbauen, Version dynamisch lesen

**Priorität:** P0
**Kategorie:** Code-Quality / i18n / Release-Hygiene

## Problem

`run_trend/ui/about_dialog.py` hat **null** `tr()`-Aufrufe und mischt
Sprachen hart kodiert:

- `app_name = QLabel("Running Progress Tracker")` (englisch, Zeile 24)
- `version = QLabel("Version 0.1.0")` (Zeile 33) — **hardcoded, veraltet**
  (`pyproject.toml` und `metainfo.xml` führen seit Februar 2026
  `version = 0.1.1`)
- `description = QLabel("A desktop application…")` (englisch, Zeile 42)
- `author = QLabel("Entwickelt von Arne Weiß")` (deutsch, Zeile 54)
- `license_label = QLabel("Lizenz: MIT + Commons Clause")` (deutsch, Z. 68)
- `license_info = QLabel("Freie Nutzung für private…")` (deutsch, Z. 73)
- `close_btn = QPushButton("Schließen")` (deutsch, Zeile 96)

Englisches UI bekommt damit einen Dialog, in dem App-Name englisch ist,
Autor + Lizenz aber deutsch erscheinen.

## Auswirkung auf Nutzer

Englischsprachige Nutzer sehen einen halbdeutschen Über-Dialog —
unprofessionell für eine Flathub-veröffentlichte App. Außerdem führt die
hardcodierte Version dazu, dass jede Release-Bump-Stelle (pyproject,
metainfo, AboutDialog) einzeln nachgezogen werden muss — fast immer wird
eine vergessen.

## Lösungsansatz

1. Alle UI-Strings durch `self.tr(...)` ersetzen.
2. Version aus dem Paket lesen:

   ```python
   from importlib.metadata import version, PackageNotFoundError

   try:
       app_version = version("run-trend")
   except PackageNotFoundError:
       app_version = "dev"
   version_label = QLabel(self.tr("Version {}").format(app_version))
   ```

3. Übersetzungen in `runtrend_de.ts` ergänzen (App-Name bleibt unverändert,
   Beschreibung / Lizenz / "Schließen" / "Repository:" werden übersetzt).

## Acceptance

- [x] Alle `QLabel`/`QPushButton`-Strings nutzen `self.tr(...)`
- [x] Versionsnummer kommt aus `importlib.metadata.version("run-trend")`
- [x] Fallback `"dev"` (oder ähnlich) wenn das Paket nicht installiert ist
- [x] DE/EN-Übersetzungen ergänzt, `.qm` regeneriert
- [x] Manuell verifiziert: englisches UI zeigt englischen AboutDialog,
      deutsches UI zeigt deutschen AboutDialog — keine Sprach-Mischung

## Annahmen

- App-Name `"Running Progress Tracker"` bleibt sprachenneutral (so im
  README und auf der Webseite). Wer "Lauf-Trend-Tracker" möchte, kann das
  später in einem eigenen Ticket diskutieren.
- HTML-Links (`<a href="…">…</a>`) müssen nicht durch `tr()` — sind
  Markup, kein Übersetzungs-Content.
- Lizenz-Text bleibt inhaltlich identisch zur LICENSE; nur Sprache wechselt.

## Dateien

- `run_trend/ui/about_dialog.py`
- `run_trend/translations/runtrend_de.ts`
- `run_trend/translations/runtrend_en.ts`
- `run_trend/translations/*.qm`

## Status / Fortschritt

**Vollständig umgesetzt.**

- ✅ `about_dialog.py` neu geschrieben mit konsequentem `self.tr(...)` für
  alle 8 user-sichtbaren Strings (Window-Title, Version-Label, Description,
  Author, License, License-Info, Repository-Prefix, Close-Button).
- ✅ Versionsnummer kommt aus neuer Modul-Funktion `_read_app_version()`:
  `importlib.metadata.version("run-trend")` mit `PackageNotFoundError`-
  Fallback auf `"dev"`. Versions-Label rendert als `self.tr("Version {}").format(_read_app_version())`,
  damit auch der Trenner übersetzbar bleibt.
- ✅ Neuer `<context>AboutDialog</context>`-Block in beiden .ts-Dateien
  mit allen 8 Source-Strings. DE-Übersetzungen: "Über Run Trend",
  "Schließen", "Lizenz: MIT + Commons Clause", "Entwickelt von Arne Weiß",
  "Eine Desktop-Anwendung zum Verfolgen und Analysieren des Lauftrainings-
  Fortschritts aus Strava.", "Freie Nutzung für private und
  nicht-kommerzielle Zwecke. Kommerzielle Vermarktung nicht erlaubt.",
  "Repository: ", "Version {}".
- ✅ `lrelease` regeneriert: DE 393 (vorher 385) / EN 388 (vorher 380).
- ✅ Markup-Strings (`<a href=…>…</a>` für E-Mail und GitHub) bleiben
  außerhalb von `tr()` — nur der "Repository: "-Prefix wird übersetzt.
- ✅ App-Name "Running Progress Tracker" als sprachenneutraler Brand-
  String, bewusst nicht durch `tr()` (Konsistenz mit README und Webseite).
- ✅ Neue Tests in `tests/test_about_dialog.py` (9 Cases):
  Version-Reading mit installiertem Paket und mit `PackageNotFoundError`-
  Fallback; Dialog-Konstruktion ohne Fehler; Version-Label nutzt
  dynamischen Lookup (über Patch); kein hardcoded `0.1.0`-Drift mehr;
  AboutDialog-Context vorhanden; alle 8 Sources in DE und EN; "Close"
  → "Schließen" konkret geprüft.
- ✅ `pytest tests/` 280 grün (271 + 9 neue).

### Annahmen

- `description` und `license_info` haben jetzt **keine** harten `\n`
  mehr — `setWordWrap(True)` übernimmt den Umbruch je nach Dialog-Breite.
  Vermeidet ungünstige Linebreaks in der deutschen Übersetzung.
- Hardcoded GitHub-URL bleibt; dynamisches Lesen aus pyproject.toml
  wäre Overkill für eine einzige URL.
- `_read_app_version()` ist Modul-Funktion (keine Klassen-Methode), damit
  Tests sie sauber per `unittest.mock.patch` ersetzen können.
