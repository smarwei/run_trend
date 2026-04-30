# 03 — RunsTable: fehlende HR sortiert ans Ende

**Priorität:** P0
**Kategorie:** Bug

## Problem

`run_trend/ui/runs_table.py:141, 148` setzt fehlende HR mit Sortierwert `-1`.
Beim Aufsteigend-Sortieren landen Läufe ohne HR-Daten **ganz oben** statt unten —
verwirrt Nutzer, der nach niedrigster HR suchen will.

`_format_pace` (Zeile 86) macht es bei fehlender Distanz richtig: `float("inf")`.

## Auswirkung auf Nutzer

Sortierte Tabelle zeigt erst alle Läufe ohne HR-Daten, dann erst die echten Werte.
Wirkt wie ein Bug, ist auch einer.

## Lösungsansatz

Konsistent mit `_format_pace`: fehlende HR mit `float("inf")` als Sortierwert.

Für DescendingOrder ist `inf` ebenfalls korrekt — landet dann oben, was passt
(Nutzer sucht in absteigender Sortierung höchste Werte; „kein Wert" gehört nicht in
die Treffermenge und steht visuell als Trennlinie oben).

## Acceptance

- [x] Aufsteigend sortiert: Läufe ohne HR am Ende
- [x] Test in `tests/` ergänzen: Tabelle mit gemischten HR-Daten, Sortierung verifiziert
- [x] Gleiches Pattern für Pace bei `distance == 0` schon korrekt (keine Änderung)

## Annahmen

- Code-Fix war bereits in `runs_table.py:141, 148` (Commit `61f3387` vom Refactor)
  vorhanden — `float("inf")` als Sortierwert für fehlende avg/max HR. Diese
  Iteration ergänzt nur die fehlenden Tests, damit die Akzeptanzkriterien
  vollständig erfüllt sind.
- Tests werden mit `QT_QPA_PLATFORM=offscreen` und einer einzelnen
  `QApplication`-Instanz pro Modul ausgeführt — kein Display nötig, lokal und in
  CI portabel.
- `has_heartrate` von Strava hat Vorrang vor numerisch vorhandenen
  HR-Werten — wenn das Flag `False` ist, gilt die HR als fehlend, auch wenn
  `average_heartrate` befüllt ist (siehe `test_has_heartrate_false_treated_as_missing`).

## Dateien

- `run_trend/ui/runs_table.py:141, 148` (Fix bereits da, kein erneuter Edit nötig)
- `tests/test_runs_table.py` (neu)
