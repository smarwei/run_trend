# 07 — `consistency_ratio` im UI sichtbar machen

**Priorität:** P0
**Kategorie:** Spec-Konformität

## Problem

`run_trend/analytics/aggregator.py:253, 277` berechnet `consistency_ratio` für jedes
Aggregat (Anzahl Runs in Periode / Soll-Anzahl).

Spec §6.2 listet das als Pflicht-Aggregatmetrik. Aktuell wird das Feld populated, aber
**nirgends gelesen** (verifiziert mit `grep consistency_ratio`).

## Auswirkung auf Nutzer

Eine vorgesehene Metrik fehlt im UI. Nutzer kann nicht sehen, ob er konsistent
trainiert hat.

## Lösungsansatz

Zwei Möglichkeiten:

1. **Im Summary-Panel** als Kennzahl mit Trend-Pfeil
2. **Im StructureOverviewChart** als zusätzliche Linie/Bar pro Periode

Empfehlung: 1 (kompakter, sofort sichtbar). Format z.B. „Consistency: 4/5 weeks (80%)"
mit Tooltip „Geplante vs. tatsächliche Trainingseinheiten je Woche".

## Acceptance

- [x] `consistency_ratio` im Summary-Panel sichtbar
- [x] Tooltip erklärt die Metrik (siehe Ticket 05)
- [x] Aggregations-Granularität (Woche/Monat) wird respektiert

## Annahmen

- Anzeige als „Active Days: N (XX%)" in der „Current Period"-Box im
  `SummaryPanel` (`summary_panel.py:241-244`). Beide Werte (`active_days`,
  `consistency_ratio`) kommen über `MainWindow._update_summary` aus dem
  zuletzt-aggregierten Periodenobjekt — also automatisch konsistent mit dem
  in der Toolbar gewählten Zeitraum.
- Die Tooltip-Erklärung ist Teil der T05-Help-Icon-Reihe (`summary_panel.py:67-75`)
  und beschreibt sowohl `active_days` als auch das Verhältnis.
- Granularität (Woche/Monat): `aggregator.py:240-253` setzt `days_in_period`
  je nach `period_type` (7 für Woche, kalendergenau für den Monat des
  Periodenanfangs). Die Prozent-Anzeige im Summary-Panel reflektiert diese
  Skalierung dadurch automatisch.
- Empfehlung Variante 1 (Summary-Panel) wurde umgesetzt; Variante 2
  (zusätzliche Linie im StructureOverviewChart) bleibt out of scope, da der
  KPI im Summary kompakter und sofort sichtbar ist — Spec §6.2 ist damit
  erfüllt.

## Dateien

- `run_trend/ui/summary_panel.py:56,67-75,239-246` (Anzeige + Tooltip)
- `run_trend/ui/main_window.py:782` (Daten-Pipeline ins Summary)
- `run_trend/analytics/aggregator.py:240-253,277` (Berechnung pro Periode)
