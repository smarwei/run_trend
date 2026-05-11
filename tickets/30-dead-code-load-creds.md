# 30 — Toten Code `load_strava_credentials_from_file` entfernen

**Priorität:** P0
**Kategorie:** Code-Quality

## Problem

`run_trend/settings/config.py:104-128`:

```python
@staticmethod
def load_strava_credentials_from_file(token_file: Optional[str] = None) -> tuple:
    ...
    return (None, None)
```

Wird nirgendwo aufgerufen:

```
$ grep -rn "load_strava_credentials_from_file" run_trend/
run_trend/settings/config.py:105:    def load_strava_credentials_from_file(...)
```

Suggeriert einen alternativen Credential-Pfad, der real nicht existiert
(`settings.json` ist die einzige Quelle). Verwirrt zukünftige Maintainer
und erhöht die API-Oberfläche von `AppSettings`.

## Lösungsansatz

Methode komplett entfernen. Falls der `Optional`-Import nur dafür da war,
gleich mit aufräumen. Auch die Importliste am Dateianfang prüfen.

## Acceptance

- [x] Methode `load_strava_credentials_from_file` entfernt
- [x] Imports am Dateianfang aufgeräumt (alle bleiben — werden von
      `__init__`/`_save_settings`/`_load_settings` weiter genutzt)
- [x] `grep -rn "load_strava_credentials_from_file"` liefert keine
      Treffer mehr (außer in diesem Ticket selbst)
- [x] Tests grün

## Annahmen

- Sollte sich später herausstellen, dass eine Externe-Credential-Datei
  doch sinnvoll ist (z. B. für CI), wird die Methode in einem eigenen
  Ticket mit Tests und Aufruf-Pfad wieder eingeführt.

## Dateien

- `run_trend/settings/config.py`
- `tests/test_config.py` (Regression-Guard hinzugefügt)

## Status / Fortschritt

**Vollständig umgesetzt.**

- ✅ `AppSettings.load_strava_credentials_from_file` (Zeilen 140-164)
  vollständig entfernt, inkl. Docstring und Default-Path-Logik.
- ✅ Importliste am Dateianfang unverändert: `os`, `logging`, `tempfile`,
  `threading`, `pathlib.Path`, `typing.Any`/`Optional`, `json` — alle
  bleiben aktiv genutzt von `__init__` (XDG-Pfad), `_load_settings`,
  `_save_settings` (T24-Atomic-Write) und Type-Hints.
- ✅ Backward-Compat-Alias `SettingsManager = AppSettings` bleibt
  unangetastet (außerhalb des Scopes — könnte aber in einem Folge-Ticket
  ebenfalls fallen, falls `git grep SettingsManager` nur die
  Alias-Definition findet).
- ✅ Neuer Regression-Test `TestDeadCodeRemoved` in
  `tests/test_config.py`: prüft `hasattr(AppSettings,
  'load_strava_credentials_from_file') is False` — schlägt fehl, falls
  jemand die Methode versehentlich zurückbringt ohne expliziten Aufruf-
  Pfad zu etablieren.
- ✅ `pytest tests/` 286 grün (285 + 1 neue). `grep` über
  `run_trend/`/`tests/` zeigt keinen verbleibenden Treffer.
