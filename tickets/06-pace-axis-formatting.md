# 06 — Pace-Achsen einheitlich als MM:SS formatieren

**Priorität:** P0
**Kategorie:** UX-Konsistenz

## Problem

Tabelle und Summary-Panel zeigen Pace als `MM:SS` (z.B. `5:30`), Chart-Achsen aber als
Dezimalzahl (`5.50` oder `5.5`). Mathematisch identisch, optisch verwirrend.

Betroffen:
- `run_trend/charts/pace_chart.py:90` (`%.2f`)
- `run_trend/charts/pace_distance_chart.py:74` (`%.1f`)

## Auswirkung auf Nutzer

Nutzer denkt, Werte stimmen nicht überein („Tabelle 5:30, Chart 5.50?"). Mentaler
Übersetzungsschritt bei jedem Blick aufs Chart.

## Lösungsansatz

Custom Tick-Formatter für Pace-Achsen. Optionen:

1. `QValueAxis::setLabelFormat("%.2f")` durch eigene Logik ersetzen — Tick-Werte
   manuell mit `setLabelsAngle`+`setTickInterval`+manuell gesetzten Labels.
2. Pace intern in Sekunden speichern, Achse als `QCategoryAxis` mit
   `QTime`-formatierten Labels.

Einfacher: Helper `format_pace_minutes(value: float) -> str` zentral — und Chart-Achse
über `axis.labelsEditable=False` + `setLabelFormat` mit benutzerdefinierter Funktion
versehen.

## Acceptance

- [x] Beide Pace-Charts zeigen Achsen-Labels als `MM:SS`
- [x] Tooltips/Hover-Werte ebenfalls als `MM:SS` *(siehe Annahme unten — kein
      Hover-Tooltip vorhanden, Achsen-Labels decken die Hover-Sichtbarkeit ab)*
- [x] Konsistent zur Tabelle und zum Summary-Panel

## Annahmen

- Es gibt aktuell keine eigenen Hover-Tooltips auf `PaceChart`/`PaceDistanceChart`
  (kein `series.hovered`-Handler vorhanden). Die Achsen-Labels sind die
  einzige Hover-Information, die der Nutzer sieht — sie zeigen jetzt `MM:SS`.

## Dateien

- `run_trend/charts/base_chart.py` (Helper `format_pace_minutes`,
  Factory `_create_pace_axis`)
- `run_trend/charts/pace_chart.py`
- `run_trend/charts/pace_distance_chart.py`
