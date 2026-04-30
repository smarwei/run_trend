# 11 — Toten Code entfernen (`_connect_signals`)

**Priorität:** P0
**Kategorie:** Code-Quality

## Problem

`run_trend/ui/main_window.py:263-265`:

```python
def _connect_signals(self):
    """Connect signals and slots."""
    pass
```

Wird in `__init__` aufgerufen, hat aber keine Wirkung. Suggeriert Funktionalität, die
nicht existiert. Verwirrt zukünftige Maintainer.

## Lösungsansatz

Zwei Optionen:

1. **Löschen** — alle Connects im Toolbar-Setup sind dort lokal sinnvoll, kein Bedarf.
2. **Sinnvoll füllen** — Connects, die nicht direkt im Setup-Kontext stehen
   (z.B. `dateChanged.connect`-Calls aus `_setup_toolbar`), hierher verschieben.

Empfehlung: **löschen**. Connect-an-Ort-Setup ist im Codebase-Stil etabliert.

## Acceptance

- [x] Methode entfernt
- [x] Aufruf in `__init__` entfernt
- [x] Tests grün, App startet weiterhin

## Annahmen

- Die Bereinigung erfolgte bereits im Architektur-Refactor (Commit `61f3387`).
  `grep -n _connect_signals run_trend/` liefert heute keine Treffer mehr in
  Quellcode (nur dieses Ticket selbst). `MainWindow.__init__`
  (`main_window.py:94`) ruft keine `_connect_*`-Methode mehr auf — Signals
  werden direkt im jeweiligen Setup-Kontext (`_setup_toolbar`,
  `_setup_statusbar`, …) verdrahtet, was dem im Codebase etablierten Stil
  entspricht.
- Empfehlung des Tickets („löschen" statt „füllen") wurde umgesetzt.
- Tests grün (112 passed), App startet via `python -m run_trend.main` ohne
  AttributeError oder Warnungen zu fehlenden Connects.

## Dateien

- `run_trend/ui/main_window.py` (Methode + Aufruf bereits entfernt — keine
  Änderung mehr nötig)
