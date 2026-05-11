# 33 — RoC-Toggle in `BaseChart` deduplizieren

**Priorität:** P1
**Kategorie:** Code-Quality

## Problem

Die „Rate of Change"-Linie (RoC) wird in drei Charts 1:1 kopiert
implementiert:

- `run_trend/charts/distance_chart.py:22-30, 105-128`
- `run_trend/charts/pace_chart.py:22-30, 121-144`
- `run_trend/charts/heartrate_chart.py:28-32, 116-131, 155-163`

In jedem Chart:

1. `roc_checkbox = QCheckBox("Rate of Change")` im UI-Setup
2. `_on_roc_toggle` Slot, der `update_chart` re-triggert
3. ein ~25-Zeilen-Block in `update_chart`, der `QLineSeries` aufbaut,
   gefilterte RoC-Werte aus `complete_aggregates` zieht, eigene rechte
   Achse (`QValueAxis`) mit Margin-Berechnung anhängt

Wer das RoC-Label, die Achsen-Formatierung oder die Margin-Logik ändert,
muss es dreimal anfassen.

## Lösungsansatz

Helper-Methode in `BaseChart`:

```python
def _render_roc(
    self,
    chart: QChart,
    axis_x: QDateTimeAxis,
    period_dates: list[date],
    complete_aggregates: list[dict],
    metric_key: str,
    axis_title: str,
) -> tuple[QLineSeries, QValueAxis]:
    """Build a Rate-of-Change line series and a right-side value axis.

    Returns both so the subclass can keep references (for cleanup or
    later styling tweaks). Both series and axis are already attached
    to the chart.
    """
```

Die Margin-Berechnung (`max(abs(values)) + 0.5` o.ä.) wandert mit nach
`BaseChart`, identisch zu T09 für `PaceDistanceChart`. Die Charts rufen
nur noch:

```python
if self.roc_checkbox.isChecked():
    self._render_roc(self.chart, self.axis_x, ...)
```

Optional: auch die Checkbox-Erstellung (`_make_roc_checkbox`) und der
`_on_roc_toggle`-Slot wandern als Mixin-Methode in `BaseChart`.

## Acceptance

- [x] `BaseChart._make_roc_checkbox`, `_build_roc_series`,
      `_create_roc_axis` implementiert + Tests in
      `tests/test_base_chart.py` (neu): zu wenige Punkte → None,
      Linear-Ramp-Daten → slope 1.0, Margin-Berechnung, collapsed-range
      Fallback.
- [x] `distance_chart.py`, `pace_chart.py`, `heartrate_chart.py` rufen
      die Helper auf, eigene Implementierungen entfernt
- [x] Bestehende Chart-Tests grün (`test_race_chart_markers.py`,
      `test_projection_chart_goals.py`, etc.)
- [x] RoC sieht visuell identisch zur jetzigen Variante aus
      (verhaltensgleicher Refactor; Tests ohne Pixel-Diff aussagekräftig)
- [ ] Code-Diff zeigt ~70 LOC Netto-Einsparung — **siehe Status: nicht
      eingehalten, dafür weniger Drift-Surface und HR-Chart spart einen
      doppelten RoC-Compute pro Render.**

## Annahmen

- `PaceChart` invertiert die RoC-Logik (negativer Pace-Delta = bessere
  Form). Das bleibt im Subklassen-Wrapper (Sign-Flip vor dem Aufruf),
  Helper selbst rechnet vorzeichen-agnostisch.
- Achsen-Label-String pro Chart unterschiedlich („Δ km/Woche", „Δ s/km",
  „Δ bpm/Woche") — kommt als Parameter rein.

## Dateien

- `run_trend/charts/base_chart.py`
- `run_trend/charts/distance_chart.py`
- `run_trend/charts/pace_chart.py`
- `run_trend/charts/heartrate_chart.py`
- `tests/test_base_chart.py` (neu)

## Status / Fortschritt

**Vollständig umgesetzt.**

- ✅ Drei neue `BaseChart`-Methoden (T33-Block ab Zeile ~308 in
  `base_chart.py`):
  - `_make_roc_checkbox(label_override=None)` — wired QCheckBox mit
    `_on_roc_toggle`-Connect; Subklassen liefern den Slot.
  - `_build_roc_series(aggregates, metric_key, period_dates, *, label,
    color="#9b59b6")` — gibt `(QLineSeries, valid_values)` oder `None`,
    falls alle Werte NaN.
  - `_create_roc_axis(valid_values, title, fmt="%.2f", margin_floor=0.1)`
    — gibt `QValueAxis` mit auto-Margin (`(hi-lo)*0.2` bzw. `margin_floor`
    bei kollabiertem Range).
- ✅ Refactor in allen drei Charts: Checkbox-Setup verkürzt sich auf
  eine Zeile, der ~25-Zeilen-RoC-Block in `update_chart` schrumpft auf
  ~9 Zeilen (build → addSeries → axis → attach).
- ✅ HR-Chart-Bonus: vorher rief `update_chart` `_calculate_rate_of_change`
  **zweimal** (einmal für die Series, einmal für die Axis-Margin). Der
  Helper liefert beides aus einem Call.
- ✅ Imports in den 3 Subklassen aufgeräumt: `QCheckBox` (drei Files)
  und `math` (zwei Files) sind weggefallen.
- ✅ Tests `tests/test_base_chart.py` (6 neu) für die drei Helpers in
  Isolation, durch DistanceChart instanziiert.
- ✅ `pytest tests/` 300 grün (294 + 6 neue). `test_race_chart_markers.py`
  und `test_projection_chart_goals.py` (beide verwenden DistanceChart
  bzw. ProjectionChart) weiterhin grün → keine sichtbare
  Verhaltensänderung.

### Honest LOC-Bilanz

- distance_chart.py: 140 → 127 (−13)
- pace_chart.py: 157 → 143 (−14)
- heartrate_chart.py: 193 → 181 (−12)
- base_chart.py: 424 → 492 (+68)
- **Netto: +29 LOC** statt der im Acceptance veranschlagten ~70 LOC
  Ersparnis.

Grund: die Helpers haben Docstrings + Type-Hints, und die Margin-
Berechnung war im Original sehr knapp. Der Wert liegt im
**Deduplications-Gewinn** (eine Stelle zum Ändern statt drei), nicht in
der reinen Code-Reduktion. HR-Chart spart außerdem den doppelten RoC-
Compute pro Render.

### Annahmen

- DistanceChart bekommt das Margin-Floor von 0.1 statt vorher 0.0 — bei
  Daten mit identischem RoC quer durch das Fenster (extrem
  unwahrscheinlich bei echten gesmootheten Distanzdaten) ergibt sich
  jetzt eine 0.2er-Achsenspanne statt einer kollabierten. Defensiver
  Default, kein realistischer Behavior-Drift.
- Alle drei `_on_roc_toggle`-Slots bleiben in den Subklassen, weil sie
  jeweils mit chart-spezifischen Argumenten (`_last_metric`,
  `_last_prev_year` etc.) `update_chart` neu aufrufen. Eine
  Standard-Implementierung in BaseChart wäre zu starr.
- Die `_render_roc(...)`-One-Shot-API aus dem Lösungsansatz wurde in
  zwei kleinere Helpers aufgespalten (`_build_roc_series` +
  `_create_roc_axis`), damit HR-Chart sie unabhängig nutzen kann (das
  Chart juggelt zwei rechte Y-Achsen).
