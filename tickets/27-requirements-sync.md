# 27 — `requirements.txt` mit `pyproject.toml` synchronisieren

**Priorität:** P0
**Kategorie:** Build / Packaging

## Problem

`requirements.txt` listet drei Dependencies:

```
PySide6>=6.6.0
requests>=2.31.0
numpy>=1.24.0
```

`pyproject.toml` listet vier:

```toml
dependencies = [
    "PySide6>=6.6.0",
    "requests>=2.31.0",
    "numpy>=1.24.0",
    "markdown>=3.4.0",
]
```

`markdown` fehlt in `requirements.txt`, wird aber von
`run_trend/ui/manual_dialog.py` importiert. Wer die App per
`pip install -r requirements.txt` aufsetzt (statt `pip install .`), bekommt
einen `ImportError` beim Öffnen des Manuals.

## Auswirkung auf Nutzer

Betrifft Entwickler/Kontributoren, die via `pip` und nicht via `nix` arbeiten,
sowie CI-Pipelines die `requirements.txt` als Source-of-Truth nehmen.
Endnutzer auf Flathub sind nicht betroffen (`pyproject.toml` ist dort
maßgeblich).

## Lösungsansatz

Zwei Optionen:

1. **`requirements.txt` nachpflegen** — `markdown>=3.4.0` ergänzen.
   Pflege-Aufwand bleibt, dafür funktioniert `pip install -r ...` weiter.
2. **`requirements.txt` durch generierten Snapshot ersetzen** — z. B.
   `pip-compile pyproject.toml --output requirements.txt` (mit Pin-Versionen
   für reproducible Builds). Größerer Setup-Aufwand, dafür kein Drift mehr.

Empfehlung: **Option 1** für den Quick-Win-Fix, separates Follow-up-Ticket
falls Pin-Lockfile gewünscht.

## Acceptance

- [x] `markdown>=3.4.0` in `requirements.txt`
- [x] `pip install -r requirements.txt && python -m run_trend.main`
      startet ohne `ImportError`
- [x] Regression-Guard-Test ersetzt die README-Notiz (siehe unten)

## Annahmen

- `flake.nix` zieht ohnehin direkt aus `pyproject.toml` über
  `python3-requirements.json` (Flatpak-Build-Pfad), also dort kein Drift.
- Keine Version-Pinning-Strategie im Scope.

## Dateien

- `requirements.txt`
- `tests/test_requirements_sync.py` (neu)

## Status / Fortschritt

**Vollständig umgesetzt (Option 1).**

- ✅ `requirements.txt` ergänzt um `markdown>=3.4.0`. Reihenfolge folgt
  `pyproject.toml`.
- ✅ Neuer Regression-Test `tests/test_requirements_sync.py` (2 Cases):
  parst `pyproject.toml` mit `tomllib` (Python-3.11+-stdlib), parst
  `requirements.txt` mit kleinem PEP-508-Mini-Parser, und assertet
  bidirektional: (a) jede pyproject-Dependency ist in requirements.txt
  vorhanden, (b) keine extra Dependencies in requirements.txt, die nicht
  in pyproject deklariert sind.
- ✅ `pytest tests/` 282 grün (280 + 2 neue).
- ✅ Der separate README-Hinweis aus dem ursprünglichen Acceptance-
  Vorschlag wurde durch den Sync-Test ersetzt: der Test schlägt jetzt
  immer fehl, wenn jemand pyproject.toml ergänzt aber requirements.txt
  vergisst — also wirksamer als eine Doku-Zeile, die Maintainer
  möglicherweise übersehen.

### Annahmen

- Mini-Parser für PEP-508 reicht hier aus (`split(r'[<>=!~ ]', maxsplit=1)`),
  weil die requirements.txt nur einfache `name>=version`-Specs enthält
  und keine Extras (`pkg[extra]`), Environment-Marker oder URLs.
- Optional-Deps (`[project.optional-dependencies].dev` mit
  `pytest`/`pytest-cov`) gehören **nicht** in `requirements.txt` —
  separates `requirements-dev.txt` wäre saubererer Stil, aber außerhalb
  des Scopes dieses Tickets.
