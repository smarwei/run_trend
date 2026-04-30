# 08 — `PaceDistanceChart` auf `BaseChart` umstellen

**Priorität:** P0
**Kategorie:** Refactoring / Konsistenz

## Problem

`run_trend/charts/pace_distance_chart.py:11` erbt von `QWidget`:

```python
class PaceDistanceChart(QWidget):  # alle anderen Charts erben von BaseChart
```

`BaseChart` (`run_trend/charts/base_chart.py:14`) wurde gerade neu eingeführt, um genau
diese Duplizierung zu reduzieren. `PaceDistanceChart` dupliziert in Zeilen 18–29 und
36–38 die Helper, die in `_setup_chart_view` und `_clear_chart` schon vorhanden sind.

## Auswirkung auf Nutzer

Keine direkte. Aber: Spätere Änderungen an `BaseChart` (z.B. Empty-States aus Ticket 04,
Theme-Support) müssen für dieses Chart doppelt gemacht werden — oder werden vergessen.

## Lösungsansatz

```python
class PaceDistanceChart(BaseChart):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_chart_view(self.tr("Pace vs. Distance"))

    def update_data(self, ...):
        self._clear_chart()
        # ... bestehende Plot-Logik
```

## Acceptance

- [x] `PaceDistanceChart` erbt von `BaseChart`
- [x] Manuelles Setup-Boilerplate entfernt
- [x] Visuell identisches Verhalten (Smoke-Test im UI)
- [x] Alle Tests grün

## Annahmen

- Umstellung erfolgte im Architektur-Refactor (`61f3387`):
  `pace_distance_chart.py:12` lautet `class PaceDistanceChart(BaseChart)`,
  `_setup_ui` ruft nur noch `self._setup_chart_view(self.tr("Pace vs. Distance"))`
  und `update_chart` startet mit `self._clear_chart()` — alle Helper kommen aus
  `BaseChart` (`_create_value_axis`, `_create_pace_axis`).
- Da T04 (Empty-State) auf `_setup_chart_view` aufsetzt, profitiert dieses
  Chart automatisch vom Empty-State-Overlay — der Hauptgrund für T08, künftige
  Querschnittsänderungen nur einmal zu pflegen, ist damit eingelöst.
- `pytest tests/` 112 passed; visuell identisches Scatter-Diagramm
  (umgekehrte Pace-Achse, blau gefüllte Punkte) bestätigt durch Code-Vergleich
  mit `pace_chart.py` und durch Smoke-Run der App.

## Dateien

- `run_trend/charts/pace_distance_chart.py` (Umstellung bereits da, keine
  weitere Änderung nötig)
