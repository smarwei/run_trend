# 28 — `datetime.utcnow()` → `datetime.now(timezone.utc)`

**Priorität:** P0
**Kategorie:** Code-Quality / Forward-Compat

## Problem

`datetime.utcnow()` ist seit Python 3.12 deprecated (`DeprecationWarning`)
und liefert ein **naives** Datetime, das fälschlicherweise als UTC
interpretiert wird — Quelle subtiler Timezone-Bugs. Ab Python 3.13/3.14
wird die Warnung lauter, irgendwann verschwindet die Methode.

13 Vorkommen im Code:

- `run_trend/sync/sync_manager.py:89, 138, 176` (last_sync persisten,
  incremental-Fenster, last_sync update)
- `run_trend/storage/database.py:172, 333, 411, 451, 480, 518, 567, 604`
  (Insert-/Update-Timestamps in `activities`, `race_markers`, `goals`)
- `run_trend/ui/main_window.py:506` (Vergleich `now` vs. `last_sync`-Wert
  für Anzeige in der Statusbar; Kommentar Zeile 505 nennt das Format
  explizit: „Stored as naive UTC by sync_manager")

## Lösungsansatz

Drop-in: `datetime.utcnow()` → `datetime.now(timezone.utc).replace(tzinfo=None)`
**Format und Bedeutung der gespeicherten ISO-Strings bleiben unverändert**
(naive UTC), keine DB-Migration nötig.

Falls langfristig timezone-aware durchgehalten werden soll, ist das ein
separates Ticket — der Hauptkonsument der Strings ist
`datetime.fromisoformat(...)` in MainWindow und Charts, die alle naive
Datetimes erwarten.

## Acceptance

- [x] Alle 13 `datetime.utcnow()`-Aufrufe ersetzt durch
      `datetime.now(timezone.utc).replace(tzinfo=None)`
- [x] `from datetime import datetime, timezone, timedelta` in den
      betroffenen Modulen (Imports ggf. erweitern)
- [x] Tests grün, keine Behavior-Änderung
- [x] `pytest -W error::DeprecationWarning` löst nicht mehr auf
      `utcnow`-Aufrufen aus

## Annahmen

- Naive-UTC-Datenformat in der DB bleibt erhalten — Migration zu
  aware-Datetimes wäre eine ganz andere Diskussion (DB-Schema, ISO-Format,
  alle `fromisoformat`-Konsumenten anpassen).
- Keine zusätzlichen `freezegun`-Tests im Scope.

## Dateien

- `run_trend/sync/sync_manager.py`
- `run_trend/storage/database.py`
- `run_trend/ui/main_window.py`
- `tests/test_no_datetime_utcnow.py` (neu — Regression-Guard)

## Status / Fortschritt

**Vollständig umgesetzt.**

- ✅ `sync/sync_manager.py:5`: Import um `timezone` erweitert; 3
  Call-Sites (`utcnow()` an Zeilen 89/138/176) per `replace_all` ersetzt.
- ✅ `storage/database.py:9`: Import um `timezone` erweitert; 8
  Call-Sites per `replace_all` ersetzt.
- ✅ `ui/main_window.py:12`: Import um `timezone` erweitert; 1 Call-Site
  ersetzt. Kommentar in Zeile 505 entwöhnt vom API-Namen
  (`"naive UTC ISO string"` statt `"datetime.utcnow().isoformat()"`),
  damit der Kommentar nicht erneut driftet.
- ✅ Format der ISO-Strings unverändert: `.replace(tzinfo=None)` macht
  den UTC-aware Datetime wieder naive, sodass `isoformat()` keinen
  `+00:00`-Suffix anhängt und die bestehenden `fromisoformat`-Konsumenten
  (MainWindow, Charts) keine Änderung sehen.
- ✅ Neuer Regression-Test `tests/test_no_datetime_utcnow.py`: greppt
  rekursiv über `run_trend/`, ignoriert Kommentare, schlägt bei
  irgendwelchem `datetime.utcnow(`-Vorkommen fehl.
- ✅ `pytest tests/ -W error::DeprecationWarning` 283 grün (vorher 282
  + 1 neu); die vorher 65 DeprecationWarnings zu `utcnow` sind weg.

### Annahmen

- `replace_all` war risikolos, weil `datetime.utcnow()` nirgends in
  Strings, Tests oder Kommentaren vorkam (außer dem einen Kommentar, der
  bewusst aktualisiert wurde).
- Der Regression-Guard prüft Source-Code-Pattern statt Laufzeit-
  Verhalten — zuverlässig auch wenn neue Tests ohne Time-Mocking
  geschrieben werden.
