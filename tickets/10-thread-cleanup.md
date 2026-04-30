# 10 — QThread-Cleanup (Memory-Leak bei wiederholten Syncs)

**Priorität:** P0
**Kategorie:** Bug / Memory-Hygiene

## Problem

`run_trend/ui/main_window.py:369-371, 448-451, 456-458` überschreibt:

- `self._auth_thread`
- `self.sync_thread`
- `self.silent_sync_thread`

bei wiederholten Sync-/Auth-Versuchen einfach mit neuen `QThread`-Instanzen. Alte
Threads mit aktiven Signal-Slot-Verbindungen bleiben am Leben, bis Python sie GC-ed
— bei zyklischen Qt-Refs verzögert.

## Auswirkung auf Nutzer

Bei langer Laufzeit / vielen Syncs Memory-Leak. Nicht sofort sichtbar, aber bei
Daily-Use über Wochen messbar.

## Lösungsansatz

Vor jedem neuen Thread-Start:

```python
if self.sync_thread is not None:
    self.sync_thread.quit()
    self.sync_thread.wait()
    self.sync_thread.deleteLater()
```

Alternativ: `finished.connect(self.sync_thread.deleteLater)` direkt nach Erzeugung
setzen — räumt automatisch auf, wenn der Thread fertig ist.

## Acceptance

- [x] Alle drei Thread-Felder werden vor Re-Use ordentlich beendet & gelöscht
- [x] `finished.connect(deleteLater)` als Default-Pattern
- [x] Kein Crash bei schnell aufeinanderfolgenden Sync-Klicks

## Annahmen

- Umsetzung erfolgte im Architektur-Refactor (`61f3387`) durch die im Ticket
  vorgeschlagene Alternative — `finished.connect(<thread>.deleteLater)`
  direkt nach Erzeugung. Aktuelle Treffer:
  - `_auth_thread`        → `main_window.py:474`
  - `sync_thread`         → `main_window.py:567`
  - `silent_sync_thread`  → `main_window.py:575`
  Damit räumt jeder Thread sich selbst auf, sobald `finished` feuert; eine
  spätere Reassignment-Linie kann das Python-Attribut gefahrlos überschreiben,
  weil der C++-`QThread` über die aktive Signal-Verbindung weiterlebt, sein
  `_on_*_finished` ausführt, und anschließend `deleteLater` durchläuft.
- AC #3 ("schnell aufeinanderfolgende Sync-Klicks") ist zusätzlich durch
  `self.sync_action.setEnabled(False)` (`main_window.py:556`, wieder
  freigeschaltet in `_on_sync_finished:589`) abgesichert — eine zweite
  Sync-Aktion kann während des Laufs nicht ausgelöst werden.
- `silent_sync_thread` wird ausschließlich aus `_check_authentication`
  beim App-Start aufgerufen (`main_window.py:379`); ein Re-Entry-Pfad
  existiert nicht, daher reicht das `deleteLater`-Pattern.
- `pytest tests/` 114 passed (kein Regress); App startet ohne Fehler.

## Dateien

- `run_trend/ui/main_window.py:474, 567, 575` (Cleanup bereits da, keine
  weitere Änderung nötig)
