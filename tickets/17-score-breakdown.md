# 17 — Score-Breakdown anzeigen ("Warum X/100?")

**Priorität:** P1
**Kategorie:** UX

## Problem

Training-Score (0–100) wird in `run_trend/analytics/training_score.py` aus 4
gewichteten Komponenten berechnet:

- 30% Volumen (Distanz/Woche)
- 20% Konsistenz (Trainingseinheiten/Woche)
- 30% Intensität (HR/Pace)
- 20% Effizienz (EF)

Der Endwert wird angezeigt, aber **nicht der Breakdown**. Nutzer sieht „72/100" und
weiß nicht, was er verbessern müsste, um auf 80 zu kommen.

## Lösungsansatz

Im Score-Chart oder als separate Karte ein Breakdown-Widget:

- Vier Mini-Bars oder ein gestapelter Balken: 0–30, 0–20, 0–30, 0–20
- Tooltip pro Komponente: aktueller Wert + Hinweis („increase weekly distance to gain
  more here")

Optional: kleine **Trend-Pfeile** (↑/↓) zeigen, welche Komponenten sich gegenüber der
letzten Periode geändert haben.

## Acceptance

- [x] Score-Chart oder dazugehöriges Panel zeigt Komponenten-Breakdown
- [x] Hover/Tooltip erklärt, wie die Komponente zustande kommt
- [x] Breakdown wird mit Date-Range / Aggregation aktualisiert
- [x] Übersetzt (DE/EN)

## Annahmen

- **Ort des Breakdowns:** im `SummaryPanel` (Karte „Training Status")
  unterhalb des Score-Werts, nicht im `ScoreChart`. Begründung: das
  Panel ist immer sichtbar, das Chart liegt in einem Tab, in dem
  der User den Wert sucht. Außerdem ist der Breakdown ein
  „Snapshot"-Wert für die aktuelle Periode — eine Zeitreihen-
  Darstellung im Chart wäre semantisch unklar (welcher Punkt zeigt
  welche Komponente?). Das Ticket erlaubt explizit beides
  („Im Score-Chart oder als separate Karte").
- **Darstellung:** vier kleine Text-Zeilen `Komponente: Beitrag /
  Maximum` (z.B. „Distanz: 18.0 / 30"). Statt Mini-Bars oder
  gestapeltem Balken — minimaler Scope, sofort lesbar, robust gegen
  Theming. Eine separate `?`-Help-Icon-Spalte erklärt pro
  Komponente, was sie misst und wie sie verbessert wird.
- **Skalierung:** jede Komponente trägt mit ihrem gewichteten,
  auf 50 skalierten Wert bei (`weight × normalized × 50`); die
  Maxima (30/20/30/20 mit HF, sonst 37.5/25/37.5/0 ohne HF)
  summieren sich zu 100. Die Summe der aktuellen Beiträge
  entspricht exakt dem `training_score` — verifiziert per
  `test_score_contributions_with_hr`.
- **Ohne HF-Daten:** Efficiency wird als „Effizienz: keine
  HF-Daten" angezeigt; die anderen drei Komponenten verwenden die
  rebalancierten Gewichte (37.5 % / 25 % / 37.5 %), damit der
  Maximalwert weiter bei 100 bleibt.
- **Öffentliche API:** `TrainingScoreCalculator.get_score_contributions()`
  als statische Methode hinzugefügt — nimmt das bereits berechnete
  `score_components`-Dict und liefert pro Komponente
  `{contribution, max, has_data}`. Damit muss die UI die
  Gewichtungs-Logik nicht duplizieren.
- **Trend-Pfeile** (↑/↓ vs. Vorperiode) wurden im Ticket als
  optional gekennzeichnet und sind hier nicht umgesetzt. Begründung:
  brauchen einen weiteren Vergleichs-Aggregate-Lookup; passt besser
  zu Ticket 14 (Year-over-Year). Aktuelle AC verlangt sie nicht.
- **Tests:** drei neue Tests in `tests/test_analytics.py`
  (`test_score_contributions_with_hr`,
  `test_score_contributions_without_hr`,
  `test_score_contributions_empty`) bestätigen
  Beitrags-/Max-Konsistenz und Empty-/None-Handling.
  `pytest tests/` 117 passed.
- Übersetzungen für 14 neue Strings in beiden `.ts`-Dateien;
  `lrelease` regeneriert beide `.qm`-Dateien (259 DE / 254 EN
  finished).

## Dateien

- `run_trend/analytics/training_score.py` (neue Methode
  `get_score_contributions`)
- `run_trend/ui/summary_panel.py` (Breakdown-UI im Training-Status-
  Block + `_set_breakdown_label`-Helper)
- `run_trend/ui/main_window.py` (`score_components` ins Summary-Dict)
- `tests/test_analytics.py` (3 neue Tests)
- `run_trend/translations/runtrend_de.ts`, `runtrend_en.ts` (+14
  Einträge)
- `run_trend/translations/runtrend_de.qm`, `runtrend_en.qm`
  (regeneriert via `lrelease`)
