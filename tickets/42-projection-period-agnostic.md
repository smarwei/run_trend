# 42 — Prognose periodenagnostisch + robust + ehrlich

**Priorität:** P1
**Kategorie:** Methodische Korrektheit / UX-Honesty

## Problem

Der bestehende `Forecaster.project_trend` und das davon abgeleitete
Marathon-Milestone-Datum + die Linie im Prognose-Tab geben in
Wochen- und Monats-Aggregation **deutlich unterschiedliche
Datums-Prognosen** für denselben Meilenstein (z. B. 30 km Long Run):

- Wochenmodus: Marathon-Ready ≈ Ende November
- Monatsmodus: Marathon-Ready ≈ August

Die zugrundeliegenden Aktivitäten sind dieselben. Dass zwei UI-Sichten
denselben Sachverhalt unterschiedlich „prognostizieren", ist ein
Modell-Artefakt, kein zulässiges Lesarten-Spektrum.

Ursachen identifiziert:

1. **Regression auf Perioden-Indizes** (`0, 1, 2, ...`) statt auf Zeit.
   Slope-Einheit wird damit „km / Indexschritt" und ändert ihre
   Bedeutung mit der Periodenwahl.
2. **`max()` als Periodenaggregation** verstärkt Outlier
   unterschiedlich — bei 11 Wochenmaxima mit Within-Period-Rauschen
   bekommt der Slope weniger Gewicht pro Punkt als bei 4
   Monatsmaxima.
3. **Lineare Extrapolation** spiegelt die nicht-lineare Trainings­
   adaption (frühe Gewinne, dann Plateau) nicht wider.
4. **Keine Robustheits-Behandlung** — ein einzelner PR-Lauf zieht den
   ganzen Trend in die Höhe.
5. **Keine Kommunikation der Unsicherheit** — der Nutzer sieht ein
   punktgenaues Datum ohne Konfidenz-Range.
6. **Keine Plateau-Erkennung** — ein Läufer mit konstantem Long-Run
   bekommt trotzdem eine „bald 30 km!"-Prognose.

Im Garmin-Vergleich (siehe Gesprächs­verlauf 2026-05-17): Garmin macht
**Zustands**-Schätzungen (VO2max → Race-Zeit-Heute), keine
**Zeit-Distanz-Extrapolation**, weil Letztere ein schlecht
gestelltes Problem ist. RunTrend muss entweder ebenso aufhören das zu
versprechen, oder das Modell so verbessern, dass es ehrlicher wird.

## Lösungsansatz

Zwei Slices.

### Slice 1 — Periodenagnostik + Robustheit (P1)

Refactor `Forecaster.project_trend` (oder ein neues
`project_milestone_date`):

- **Input**: rohe Aktivitäten (`activities`), nicht Periodenaggregate
- **Filter**: nur Läufe ≥ Long-Run-Threshold (z. B. ≥ 1,5×
  Median-Distanz der letzten 8 Wochen) — reduziert Rauschen aus
  kurzen Erholungsläufen
- **X-Achse**: Tage seit erstem gefilterten Lauf — periodenagnostisch
- **Y**: Distanz in km
- **Regression**: Theil-Sen (Median aller Slopes zwischen
  Datenpunktpaaren) statt OLS — toleranter gegen Outlier
- **Recency-Weighting**: optional, exponentiell (e^(-Tage/τ) mit τ ≈
  60 Tage), in Slice 1 vermutlich noch nicht nötig wenn der
  Long-Run-Filter schon greift

Datums-Prognose: `days_to_milestone = (milestone − intercept) / slope`,
in `date` umgerechnet → eine einzige Antwort, egal welcher UI-Modus.

### Slice 2 — Unsicherheit + Plateau + Caveats (P2)

- **Konfidenz-Intervall**: Bootstrap (z. B. 500 Resamples der Aktivitäten)
  → 95-% CI für die Milestone-Datums-Prognose. Anzeige als
  „Sept 14 ± 3 Wochen" oder als visuelles Band um die Prognose-Linie.
- **Plateau-Detektor**: wenn der Theil-Sen-Slope der letzten 4 Wochen
  ≤ 0,1 km/Tag ist → keine Datums-Vorhersage, sondern Label
  „Trend stagniert — Long-Run-Wachstum < 1 km/Woche".
- **Horizont-Kappung**: wenn das CI breiter als ± 8 Wochen wird, gar
  nicht mehr extrapolieren, sondern Hinweis „Datengrundlage zu dünn
  für verlässliche Prognose".
- **Tooltip-Caveat** auf der Linie *und* auf dem Summary-Panel-Feld
  „Marathon Milestone":
  > Robuste Trend-Extrapolation (Theil-Sen) auf den jüngsten
  > Long-Runs. Eine Heuristik, kein Trainingsplan. Trainings­
  > adaption ist non-linear; das Datum sagt „wenn dein Trend so
  > weiterläuft" und ignoriert Erholungs-, Verletzungs-, Lebens­
  > variable. Mit Vorsicht lesen.
- **Manual-Update**: Eintrag in der „Methodische Caveats"-Tabelle
  (`MANUAL_de.md` / `MANUAL_en.md`):

  ```
  | Marathon Milestone Datum + Prognose-Tab | RunTrend-eigene Trend-
  | Extrapolation (Theil-Sen-Slope auf Long-Runs) | selbst zusammen-
  | gestellt | Keine physiologische Modellierung — kein peer-reviewed
  | „wann erreicht Läufer X km"-Modell existiert. Trainings­adaption ist
  | non-linear; Datum ignoriert Erholung/Verletzung/Lebensplan. CI ist
  | breit, vor allem bei < 8 Wochen Datengrundlage. |
  ```

- **Optionale Umbenennung**: Tab „Prognose" → „Trend-Extrapolation",
  Feldlabel „Estimated Date" → „Extrapolated Date" oder
  „Trend-Projektion". (Diskutieren — eventuell zu invasiv.)

## Acceptance

### Slice 1 (Inkonsistenz beheben)

- [ ] Neue/refaktorierte Funktion in `run_trend/projection/forecaster.py`,
      die Aktivitäten + Distanz-Threshold als Input nimmt, Theil-Sen
      auf Tage-Achse macht und ein einziges Datum zurückgibt
- [ ] `ProjectionChart` ruft sie auf, sowohl in Wochen- als auch
      Monatsmodus → selbe Linie/Datum in beiden Modi
- [ ] `_update_summary` in `main_window.py` ruft denselben Pfad für
      das Marathon-Milestone-Feld
- [ ] Test `tests/test_projection_period_agnostic.py`:
  - Gleiche Aktivitäten, Wochen- vs. Monatsaggregation → identisches
    Datum (Toleranz ± 1 Tag)
  - Outlier-PR-Lauf eingefügt → Slope ändert sich weniger als bei OLS
  - Long-Run-Filter funktioniert (kurze Erholungsläufe werden ignoriert)
- [ ] Full-Suite weiterhin grün

### Slice 2 (Honesty)

- [ ] Bootstrap-CI für Datums-Prognose
- [ ] Plateau-Detektor; bei flachem Trend → kein Datum, sondern Hinweis
- [ ] Horizont-Cap (CI > ±8 Wochen → kein Datum)
- [ ] Tooltip-Caveats auf Linie + Marathon-Milestone-Feld
- [ ] Manual-Update DE/EN (Caveat-Tabelle erweitert)
- [ ] Test für Plateau-Detektion + CI-Bandbreite

## Methodische Punkte (vor Code klären)

1. **Theil-Sen vs. Huber vs. RANSAC**: Theil-Sen ist einfach
   (median aller pairwise slopes), keine externe Lib nötig, robust
   gegen ~30 % Outlier-Anteil. Bei wenigen Punkten (< 5) numerisch
   weniger stabil als Huber, aber kein Tuning-Parameter. **Empfehlung:
   Theil-Sen.**
2. **Long-Run-Threshold**: fix bei 1,5× Median-der-letzten-N-Wochen,
   oder einfacher 75. Percentile der letzten N Läufe? Empfehlung:
   das gleitende 75. Percentile der letzten 12 Wochen, mindestens
   8 km Floor.
3. **Bootstrap-Resamples**: 500 reicht für eine 95-%-CI bei n = 30
   Long-Runs. Schneller als 1000, robust genug.
4. **Plateau-Schwelle**: Slope < 0,1 km/Tag entspricht < 0,7
   km/Woche-Wachstum. Plausibler Cut-off.
5. **Horizont-Kappung**: CI > ± 8 Wochen = mehr als 4 Monate Spanne;
   ab da nicht mehr seriös vorhersagbar.

## Slice-Plan

1. **Pure Theil-Sen + Tage-Achse + Long-Run-Filter** als neue
   Forecaster-Funktion, ohne UI-Anbindung. Unit-Tests.
2. **UI-Anbindung**: Marathon-Milestone-Feld + Prognose-Tab nutzen
   neue Funktion. Visual-Smoke-Test.
3. **CI + Plateau-Detektor + Caveats** (Slice 2).
4. **Manual-Eintrag + Übersetzungen**.

## Dateien

- `run_trend/projection/forecaster.py` (Refactor / neue Funktion)
- `run_trend/charts/projection_chart.py` (Anbindung)
- `run_trend/ui/main_window.py` (`_update_summary`)
- `run_trend/ui/summary_panel.py` (Tooltip auf Marathon-Milestone)
- `MANUAL_de.md` / `MANUAL_en.md` (Caveat-Tabelle)
- `run_trend/translations/runtrend_*.ts` (neue Strings)
- `tests/test_projection_period_agnostic.py` (neu)
- `tests/test_projection.py` (alte Erwartungen ggf. anpassen)

## Out of Scope

- Non-lineares Wachstumsmodell (Logistic/Plateau): zu invasiv, erst
  evaluieren wenn Slice 1+2 die offensichtlichsten Probleme behoben
  haben
- VO2max-Schätzung aus HF/Pace (Garmin-Style) — eigenes Ticket wert
  und braucht Forschungs-Vorarbeit
- Race-Time-Predictions (McMillan-basiert) — separate Pipeline,
  T41-Caveat reicht

## Quellen

**Robuste Regression:**
- Theil, H. (1950) / Sen, P.K. (1968): „A rank-invariant method of
  linear and polynomial regression analysis", J. Am. Stat. Assoc.

**Trainings-Adaption (Non-Linearität):**
- Bompa, T.O. / Haff, G.G. (2009): „Periodization: Theory and
  Methodology of Training", 5th ed.
- Daniels, J. (2014): „Daniels' Running Formula", 3rd ed. — VDOT
  als Zustandsschätzung, kein Zeit-Extrapolations-Modell

**Vorhandene RunTrend-Komponenten:**
- T20 (Pace-als-ACWR-Komponente überdenken — methodischer Vorläufer)
- T41 (Caveats in Tooltips + Manual)
