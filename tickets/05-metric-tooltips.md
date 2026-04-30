# 05 — Tooltips für Fachbegriffe (ACWR, TRIMP, EF, Score)

**Priorität:** P0
**Kategorie:** UX

## Problem

Charts und Panels zeigen Metriken wie:

- **ACWR** (Acute:Chronic Workload Ratio)
- **TRIMP** (Training Impulse)
- **EF** (Efficiency Factor)
- **Training Score** (0–100)
- **Consistency Ratio**

…ohne Erklärung, was sie bedeuten oder welcher Bereich „gut" ist.

## Auswirkung auf Nutzer

Werte sind ohne Domänenwissen schwer zu interpretieren. Nutzer ohne Hintergrund in
Sportwissenschaft sehen Zahlen, aber keine Aussage.

## Lösungsansatz

`?`-Icon neben jedem Metrik-Label oder Chart-Titel mit Hover-Tooltip:

- **Definition** (1 Satz)
- **Formel** in Kurzform
- **Bereiche**, falls relevant (z.B. ACWR: 0.8–1.3 = sweet spot, > 1.5 = injury risk)
- **Quelle** (z.B. „Banister TRIMP, 1991")

Implementierung: Helper `make_help_label(text, tooltip)` in `ui/utils/`, wiederverwendbar.

## Acceptance

- [x] `?`-Icons in: Score-Chart, Training-Load-Chart, Heartrate-Chart, Summary-Panel
- [x] Tooltips übersetzt (DE/EN)
- [x] Mindestens diese Metriken erklärt: ACWR, TRIMP, EF, Training Score,
      Consistency Ratio, Pace, Race Predictor

## Annahmen

- Helper liegt direkt unter `run_trend/ui/help_label.py` statt in einem neuen
  `run_trend/ui/utils/`-Subpaket — kleinere Dateioberfläche, gleiche Wiederverwendbarkeit.
- Discovery erfolgt über ein „?"-Badge mit Tooltip (Hover/WhatsThis-Cursor) — wie im
  Lösungsansatz vorgesehen, ohne Click-to-open-Dialog.
- Für `TrainingLoadChart` gibt es bisher gar keinen Übersetzungskontext im `.ts`;
  ich habe einen neuen `<context>TrainingLoadChart</context>` mit dem Tooltip
  angelegt und die übrigen, bereits unübersetzten Strings unangetastet gelassen
  (separate Aufgabe).

## Dateien

- neuer Helper in `run_trend/ui/`
- alle Chart- und Panel-Module
- `run_trend/translations/runtrend_*.ts`
