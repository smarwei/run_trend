# 09 — `PaceDistanceChart`: Margin-Berechnung robust machen

**Priorität:** P0
**Kategorie:** Bug

## Problem

`run_trend/charts/pace_distance_chart.py:76`:

```python
margin = (max(paces) - min(paces)) * 0.1 or 0.5
```

Bei identischen Paces wird `0.0 or 0.5` → `0.5`. Funktioniert. Aber bei minimalen
Float-Differenzen (z.B. `1e-9`) wird `0.0 or 0.5` zu fast Null, was die Achse
visuell auf einen Punkt kollabieren lässt.

## Auswirkung auf Nutzer

Selten, aber bei sehr konstanten Paces (oder nur einem Lauf) wird das Chart
unbrauchbar.

## Lösungsansatz

```python
margin = max((max(paces) - min(paces)) * 0.1, 0.5)
```

Garantiert ≥ 0.5, unabhängig von Float-Rauschen.

## Acceptance

- [x] Margin ist immer ≥ 0.5
- [x] Test mit identischen Paces (gleiche Werte für alle Läufe) zeigt sichtbares Chart

## Annahmen

- Code-Fix war bereits in `pace_distance_chart.py:59` (Architektur-Refactor
  `61f3387`) eingespielt: `margin = max((max(paces) - min(paces)) * 0.1, 0.5)`
  ersetzt das ursprüngliche `... or 0.5` und liefert damit auch bei
  Float-Jitter (`1e-9`-Differenzen) eine sichtbare Achse.
- Diese Iteration ergänzt die fehlende Test-Abdeckung in
  `tests/test_pace_distance_chart.py` mit zwei Fällen:
  1. Identische Paces → y-Achse spannt ≥ 1.0 (Acceptance #2 wörtlich).
  2. Mikro-Jitter (`1e-6` an `moving_time`) → ebenfalls ≥ 1.0
     (fängt die ursprünglich beschriebene Regression ab und sichert
     Acceptance #1 als Property ab).
- `pytest tests/`: 114 passed (vorher 112 + 2 neue).

## Dateien

- `run_trend/charts/pace_distance_chart.py:59` (Fix bereits da, keine
  Änderung mehr nötig)
- `tests/test_pace_distance_chart.py` (neu)
