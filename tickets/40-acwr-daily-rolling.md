# 40 — ACWR auf tägliche 7:28-Tage-Rolling-Sums umstellen

**Priorität:** P2
**Kategorie:** Refactor / Methodische Korrektheit

## Problem

Der bestehende ACWR-Chart (`run_trend/analytics/training_load.py`,
`TrainingLoadCalculator.calculate_acwr`) implementiert Acute:Chronic-
Workload-Ratio mit **Wochen-Aggregat-Granularität**:

```python
# Aus training_load.py:50-71 (vereinfacht)
acute_value = aggregates[-1].get(metric_key, 0.0)
chronic_values = [agg.get(metric_key, 0.0) for agg in aggregates[-5:-1]]
chronic_avg = np.mean(chronic_values)
acwr = acute_value / chronic_avg
```

Das hat zwei Probleme gegenüber der Gabbett-Standard-Methodik:

1. **Granularität**: Gabbett (2016) definiert ACWR als
   *7-Tage-rollende-Summe / 28-Tage-rollender-Mittelwert*, täglich
   aktualisiert. Unser 1:4-Wochen-Ratio ist eine grobe Approximation,
   die nur an Periodengrenzen aktualisiert — der Wert „springt"
   jeden Sonntag und ist innerhalb der Woche statisch.
2. **Last-Metrik**: Wir verwenden beliebige Aggregate-Spalten
   (`total_distance_km`, `weighted_avg_pace_min_per_km`, etc.) als
   „Load". Korrekt wäre eine echte Trainingslast wie TRIMP. Seit T38
   haben wir `daily_trimp_series` — der korrekte Eingang liegt schon
   herum.

**Zusätzlich** gibt es seit ~2020 eine massive Forschungs-Kontroverse
über ACWR als Verletzungs-Indikator. **Impellizzeri et al. 2020**
(„Acute:chronic workload ratio: conceptual issues and fundamental
pitfalls", *Int J Sports Physiol Perform* 15(6): 907-913) zeigen
mehrere methodische Mängel auf:

- ACWR ist ein mathematischer Quotient mit Artefakten bei kleinem
  Nenner: nach einer Verletzungs-Pause kann ein normales Training
  einen ACWR > 1,5 erzeugen, obwohl absolut wenig trainiert wurde.
- Die „Sweet-Spot 0,8–1,3"-Schwelle aus Gabbett's Original-Paper ist
  korrelativ, nicht kausal validiert. Folgestudien zeigen schwache
  oder keine Verletzungs-Korrelation.
- ACWR ignoriert die *Trainings-Historie* (chronische Belastung als
  Resilienz-Faktor) und behandelt 80 km/Woche wie 30 km/Woche, wenn
  beide auf identischem Ratio sitzen.

Wir sollten **die Korrektheit der Berechnung verbessern** und
gleichzeitig **die Limitationen ehrlich kommunizieren**.

## Lösungsansatz

### Berechnungs-Refactor: tägliche TRIMP-Rolling-Sums

Das T38-Modul `run_trend/analytics/trimp.py` liefert bereits eine
`daily_trimp_series(activities, ...) → {date: float}`-Funktion. Auf
deren Basis:

```python
def daily_acwr_series(
    daily_loads: dict[date, float],
    acute_window: int = 7,
    chronic_window: int = 28,
    start: date | None = None,
    end: date | None = None,
) -> list[dict]:
    """Pro Tag t:
        acute_t   = sum(load[t-6 ... t])
        chronic_t = sum(load[t-27 ... t]) / 4
        acwr_t    = acute_t / chronic_t   (None, wenn chronic_t == 0)
    Liefert pro Tag {'date', 'acute', 'chronic', 'acwr', 'status'}.
    """
```

Vorteile:
- Tägliche Aktualisierung; Chart-Linie wird glatter / aussage­kräftiger
- TRIMP statt Distance-only → bessere physiologische Repräsentation
- Konsistent mit T38 (CTL/ATL benutzt dieselbe Daten-Quelle)

### Status-Bänder umbenannt, gleiche Schwellen

Bestehende Klassen-Konstanten in `TrainingLoadCalculator`
(`ACWR_SAFE_MIN = 0.8`, `ACWR_SAFE_MAX = 1.3`, `ACWR_CAUTION_MAX = 1.5`)
bleiben — die Schwellen sind empirisch verbreitet, auch wenn nicht
mehr unstrittig. Aber die Tooltip-Erklärung muss die Limitations
ansprechen (siehe T41).

### Chart-Update

`TrainingLoadChart` plottet aktuell den Wochen-ACWR aus dem Aggregator.
Umstellen auf:
- Tägliche ACWR-Werte als Linie (statt einem Wert pro Aggregate)
- Hintergrund-Bänder bei 0,8 / 1,3 / 1,5 bleiben
- Statusbar im Summary-Panel: zeigt den **heutigen** ACWR-Wert plus
  den 7-Tage-Trend (steigend/fallend)

## Acceptance

- [ ] **`run_trend/analytics/training_load.py`**: neue Funktion
      `daily_acwr_series(daily_loads, ...) → list[dict]`
- [ ] Bestehende `calculate_acwr(aggregates, metric_key)` als
      **deprecated** markiert (Docstring-Hinweis, bleibt funktional
      damit Charts nicht brechen) ODER ersetzt
- [ ] **Test-Erweiterung** in `tests/test_training_load.py`:
  - Konstante 50 TRIMP/Tag → ACWR konvergiert auf 1,0
  - Plötzlicher Anstieg (Spike) → ACWR > 1,5 am Tag des Spikes
  - Pause: zero-Tage hintereinander → chronic decay korrekt
  - Cold-Start: < 28 Tage Historie → `None` für ACWR mit
    `'has_acwr': False`
- [ ] **`TrainingLoadChart`** plottet die tägliche Serie statt
      Wochen-Aggregate; Hintergrund-Bänder unverändert
- [ ] **Summary-Panel**: ACWR-Wert zeigt **heutigen** ACWR, nicht
      Wochen-Aggregat
- [ ] **Tooltip-Erweiterung** (in Koordination mit T41):
      Gabbett-2016-Quelle, Impellizzeri-2020-Caveat, was die
      Sweet-Spot-Bänder wirklich bedeuten
- [ ] **Manual-Update DE/EN**: methodische Erläuterung der
      tagesweisen Berechnung + Gabbett-vs-Impellizzeri-Kontroverse

## Methodische Punkte (vor Code klären)

1. **TRIMP als Load-Metrik** vs. **Distance**: TRIMP ist physiologisch
   korrekter (Intensität × Dauer), erfordert aber HR-Daten + Settings
   (hr_rest, gender, hr_max) wie bei T38. Empfehlung: TRIMP als
   Primary, Distance als Fallback bei fehlenden HR-Daten. Tooltip
   sagt welche Variante gerade angezeigt wird.
2. **Acute/Chronic-Fenster**: 7:28 ist Gabbett-Standard. Manche Studien
   nutzen 7:21 oder 7:42. **Empfehlung: 7:28**, dokumentiert.
3. **Backward-Compatibility**: Wochen-Aggregat-ACWR-Daten in
   bestehenden DBs bleiben erhalten, werden aber nicht mehr generiert.
   Charts und Summary lesen ab T40 die tägliche Serie. Keine
   DB-Migration nötig.
4. **Display-Granularität**: tägliche Punkte können bei 1-Jahres-
   Charts überfüllt wirken. Vermutlich Filter auf jeden N-ten Tag
   oder Smoothing-Anwendung. T33-RoC-Logik adaptierbar.
5. **Verschiebung zu „EWMA-ACWR"** (Williams et al. 2017)? Statt
   simpler Rolling-Sums die EWMA-Variante? Empfehlung: **nein** —
   Gabbett-Standard ist verbreiteter und einfacher kommunizierbar.
   Optionaler Folge-Ticket.

## Slice-Plan

1. `daily_acwr_series(...)` Pure-Function + Tests (isoliert).
2. Summary-Panel: heutiger ACWR statt Wochen-ACWR.
3. `TrainingLoadChart`: tagesweise Linie statt Aggregate-Stichproben.
4. Tooltip-Erweiterung + Manual + i18n.

Slice 1 ist Voraussetzung; 2-4 können in beliebiger Reihenfolge.

## Dateien

- `run_trend/analytics/training_load.py` (neue `daily_acwr_series`)
- `run_trend/charts/training_load_chart.py` (Daten-Quelle umstellen)
- `run_trend/ui/main_window.py` (`_update_summary` ruft neue Funktion)
- `run_trend/ui/summary_panel.py` (heutiger ACWR-Wert)
- `tests/test_training_load.py` (Test-Erweiterung)
- `run_trend/translations/runtrend_de.ts` / `runtrend_en.ts` (+ `.qm`)
- `MANUAL_de.md` / `MANUAL_en.md`

## Out of Scope

- **EWMA-ACWR** (Williams 2017) — als Folge-Ticket falls gewünscht.
- **Verletzungs-Risiko-Empfehlungen** (eigene Komponente) — ACWR ist
  als *Indikator*, nicht als Diagnose-Tool zu lesen.
- **Multi-Sport-Aggregation** — RunTrend ist Lauf-only.

## Quellen

**ACWR Original-Methodik:**
- Gabbett, T. J. (2016). „The training-injury prevention paradox:
  should athletes be training smarter and harder?"
  *Br J Sports Med* 50(5): 273-280.
  <https://bjsm.bmj.com/content/50/5/273>

**ACWR-Kritik:**
- Impellizzeri, F. M., Wolfgang, J., Coutts, A. J., et al. (2020).
  „Acute:chronic workload ratio: an obvious limitation in clinical
  context." *Int J Sports Physiol Perform* 15(6): 907-913.
  <https://journals.humankinetics.com/view/journals/ijspp/15/6/article-p907.xml>
- Wang, C., et al. (2020). „The Acute:Chronic Workload Ratio:
  Challenges and Prospects for Investigation and Implementation in
  Sport." *Int J Sports Physiol Perform* 15(8): 1142-1150.

**Bestehende RunTrend-Komponenten:**
- T20 (Pace als ACWR-Komponente überdenken — methodischer Vorläufer)
- T38 (`trimp.py` liefert `daily_trimp_series`)
