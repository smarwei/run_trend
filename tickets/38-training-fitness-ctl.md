# 38 — Training-Fitness via CTL/ATL/TSB (absolute Skala neben Training-Score)

**Priorität:** P2
**Kategorie:** Feature / Analytics

## Problem

Der bestehende Training-Score (`run_trend/analytics/training_score.py`) ist
**explizit selbstrelativ** definiert (`specification.md` §10): jede
Komponente wird gegen das eigene rollende Baseline normalisiert und auf
2× gekappt. Konsequenz, die ein Nutzer am 2026-05-12 aufgedeckt hat:

> „Ich dachte, es wäre seltsam, wenn ich irgendwann super leistungsfähig
> bin und mein Wert sinkt dann auf 50%. Eine Verdopplung der
> Trainingshäufigkeit ist weder realistisch noch erstrebenswert."

Stimmt — bei stabiler 7×/Woche-Routine läuft die Baseline der Häufigkeit
ebenfalls auf ~7, der normalisierte Wert geht auf 1,0, der
Frequency-Beitrag bleibt bei **10/20**. Das obere Ende von 20/20 (=2×
Baseline) ist nur in echten Ramp-up-Phasen erreichbar. Der Gesamt-Score
eines konsistenten Hochvolumen-Läufers pendelt damit konstruktionsbedingt
bei ~50/100 — was als „nur die halbe maximale Leistungsfähigkeit"
fehlinterpretiert wird.

Das ist **kein Bug**, sondern die Folge der Spec-Wahl „rolling baseline".
Aber dem Nutzer fehlt eine **absolute Größe**, die im Steady-State hoch
bleiben darf.

## Lösungsansatz

Eine zweite, **absolute** Trainingsfitness-Größe nach dem etablierten
Coggan-Performance-Manager-Modell ergänzen, **ohne** den bestehenden
Training-Score zu brechen.

### Modell: Banister-TRIMP → CTL → ATL → TSB

**Banister-TRIMP pro Lauf** (Banister 1991, gold-standard für HF-basierte
Trainings-Last):

```
TRIMP = duration_min × HRr × 0.64 × e^(b × HRr)
```

mit
- `HRr = (HR_avg − HR_rest) / (HR_max − HR_rest)` (HF-Reserve-Fraktion)
- `b = 1.92` (Männer) / `1.67` (Frauen) — geschlechtsspezifischer
  Exponent, gewichtet hochintensives Training relativ stärker

Die 0.64-Konstante kompensiert das Basisniveau; der Exponentialterm
sorgt dafür, dass z. B. 60 min @ Easy nicht denselben Load erzeugen wie
60 min @ Tempo.

**CTL (Chronic Training Load) / ATL (Acute Training Load):**

Tägliche TRIMP-Summe → exponentiell gewichteter gleitender Mittelwert:

```
CTL_t = CTL_{t−1} × (1 − 1/42) + daily_TRIMP × (1/42)
ATL_t = ATL_{t−1} × (1 − 1/7)  + daily_TRIMP × (1/7)
```

CTL = Fitness (langsam wachsende absolute Größe).
ATL = Akut-Last (kurzfristige Ermüdung).

**TSB (Training Stress Balance) = CTL − ATL:** Form-Indikator.

### Skala und Einordnung

Da wir TRIMP (HF-basiert) statt TSS (Watt-basiert) verwenden, sind die
Absolutwerte nicht 1:1 zu cycling-orientierter Literatur. Aber die
Form-Bänder gelten analog:

| TSB-Wert    | Bedeutung                                             |
|-------------|-------------------------------------------------------|
| > +25       | „transitional" — länger ausgeruht, Fitness verloren   |
| +10 bis +25 | „race fresh" — Tapering hat gewirkt                   |
| −10 bis +5  | neutral                                               |
| −10 bis −20 | „productive overload" — Aufbau-Phase                  |
| −20 bis −30 | Belastungsgrenze, Deload nötig                        |
| < −30       | Übertrainings-Risiko                                  |

CTL-Ramp-up-Empfehlung (Run-spezifisch, deckt sich mit der 10 %-Regel):
- Anfänger: +2–4 pro Woche
- Fortgeschritten: +3–5 pro Woche
- Wettkampf-orientiert: +5–7 pro Woche

## Voraussetzungen

Beide Bausteine sind teilweise vorhanden, eine Anforderung ist neu:

- **`hr_rest`** (Settings-Feld, T19): nötig für HF-Reserve-Berechnung.
  Ohne `hr_rest` kein TRIMP → Empty-State mit Hint.
- **`gender`** (Settings-Feld, T37): nötig für den b-Faktor.
- **`manual_hrmax`** ODER Tanaka-Schätzung aus Geburtsdatum: nötig für
  HF-Reserve. Tanaka als Fallback OK, da gender-unabhängig.
- **Aktivitäten mit `average_heartrate` + `moving_time`**: bestehend.
  Aktivitäten ohne HF beitragen 0 zu daily_TRIMP (kein Skip, sondern
  „nicht-messbar-also-null").

## Anzeige

### Summary-Panel (Pflicht-Slice)

Im „Training Status"-Block neben dem bestehenden Score:

```
┌────────────── Training Status ──────────────┐
│  Score:          63   (selbst-relativ)      │
│  Training Fit:   78   (absolut, CTL)        │
│  Form (TSB):    −12   productive overload   │
│  Breakdown: …                                │
└──────────────────────────────────────────────┘
```

- **Score** bleibt unverändert (selbst-relativ — Trending-Signal)
- **Training Fitness** = aktueller CTL-Wert, gerundet auf eine Stelle
- **Form (TSB)** = CTL − ATL, mit Text-Annotation laut Tabelle oben
- Beide neuen Werte mit eigenem Help-Icon-Tooltip — kein Klartext-
  Klammer-Suffix (siehe Feedback zu Score-Label).

### Performance-Manager-Chart (optionaler Slice 4)

Neuer Tab oder Sub-Tab im Score-/Performance-Bereich mit drei Zeitreihen:

- CTL (Fitness) — durchgezogen blau
- ATL (Fatigue) — durchgezogen rot
- TSB (Form) — gestrichelt grau, separate rechte Achse

Hintergrund-Bänder bei TSB für die fünf Form-Zonen (transitional / race
fresh / neutral / productive / overreaching).

## Acceptance

- [ ] **`run_trend/analytics/trimp.py`** (neu) mit pure-functions:
  - `banister_trimp(duration_min, avg_hr, hr_rest, hr_max, gender) → float`
  - `daily_trimp_series(activities, hr_rest, hr_max, gender) → dict[date, float]`
  - `compute_ctl_atl(daily_loads, ctl_window=42, atl_window=7) → list[(date, ctl, atl, tsb)]`
  - `tsb_zone(tsb) → str` (eine der 6 Klassen)
- [ ] Tests in `tests/test_trimp.py` (≥ 8 Cases): bekannter TRIMP für
      Banister-Beispielwerte, gender-Unterschied (M vs F), CTL-EWMA-
      Decay nach 42-Tage-Pause, Cold-Start (< 42 Tage Daten), CTL-Anstieg
      bei stetigem Training, TSB-Zonen-Boundaries
- [ ] **Summary-Panel-Erweiterung** in `run_trend/ui/summary_panel.py`:
      neue Labels `training_fitness_label` und `form_label`
- [ ] **MainWindow-`_update_summary`**: berechnet CTL/ATL/TSB aus
      `self.activities` und reicht durch (kein direkter DB-Zugriff aus
      summary_panel)
- [ ] **Settings-Validation**: wenn `hr_rest` oder `gender` fehlt,
      zeigen die neuen Labels einen klaren „Setze … in den
      Einstellungen"-Hinweis statt einer Null
- [ ] **Translations** (DE/EN), `.qm` regeneriert
- [ ] **Manual-Update** (DE+EN): Erklärung TRIMP, CTL, ATL, TSB, die
      Form-Tabelle, „selbst-relativer Score vs. absolute Fitness"-
      Abgrenzung
- [ ] Optional: Slice 4 — Performance-Manager-Chart als eigener Tab

## Methodische Punkte (vor Code klären)

1. **TRIMP-Variante**: Banister (gender-spezifisch, braucht HR-rest) vs.
   Edwards' Zone-TRIMP (`sum(time_in_zone_i × i)`, braucht nur HR-Zonen).
   Edwards ist einfacher und braucht kein hr_rest, ist aber weniger
   physiologisch fundiert. **Empfehlung: Banister** — der HR-Zone-Mapper
   aus T19 hat hr_rest ohnehin oft schon gesetzt, und Banister ist der
   wissenschaftliche Standard. Edwards optional als Fallback?

2. **HRmax-Quelle**: `manual_hrmax` aus Settings hat Priorität, sonst
   `tanaka_hrmax(age)` aus T37-Modul (208 − 0,7 × Alter). Sollte
   `manual_hrmax` nicht-gesetzt sein, hängt CTL implizit am Geburtsdatum.

3. **CTL/ATL Cold-Start**: bei < 42 Tage Trainings-Historie ist CTL noch
   nicht eingeschwungen. Optionen:
   - (a) Trotzdem berechnen — der EWMA „startet bei 0" und steigt von
     Tag 1 an. Für die ersten ~6 Wochen sind die Werte tiefer als „echt"
     wäre.
   - (b) Erst nach Mindest-Historie zeigen (z. B. ≥ 42 Tage) — saubere
     Werte, aber Empty-State über mehrere Wochen.
   - **Empfehlung: (a)**, mit Tooltip-Caveat. Praktisch nützlicher.

4. **Tage ohne Lauf**: daily_TRIMP = 0. EWMA-Decay sorgt automatisch
   dafür, dass CTL/ATL „im Verlauf" sinken. Korrekt — keine Sonderfall-
   Logik nötig.

5. **Doppel-Display Score + Fitness**: Spec sagt „neben dem bestehenden
   Score". Risiko: User sieht zwei verschiedene Werte und ist verwirrt.
   Tooltips müssen den Unterschied (relative vs. absolute) klar
   benennen. Eventuell sogar zwei Reihen mit Mini-Header:
   `Trend` / `Fitness` / `Form`.

6. **Gender-Default**: wenn nicht gesetzt, könnte Banister einen
   geschlechtsunabhängigen Mittelwert (b = 1.795) verwenden — oder
   ähnlich zu T37 das Feld als „erforderlich" markieren. Im Sinne
   konsistenter UX: gleicher Handhabung wie bei WMA (expliziter Hint
   statt stiller Default).

## Slice-Plan

1. **`trimp.py` analytics + Tests** (isoliert mergeable, keine UI).
2. **Summary-Panel-Integration** (CTL/TSB-Werte sichtbar, Tooltips,
   Empty-States bei fehlendem hr_rest/gender).
3. **Translations + Manual** (DE/EN).
4. *Optional:* **Performance-Manager-Chart** als neuer Tab unter
   „Performance" (neben WMA / Aerobic Capacity).

Slice 1 ist Voraussetzung für 2; 3 und 4 sind unabhängig.

## Dateien (neu)

- `run_trend/analytics/trimp.py`
- `tests/test_trimp.py`
- optional: `run_trend/charts/performance_manager_chart.py`
- optional: `tests/test_performance_manager_chart.py`

## Dateien (geändert)

- `run_trend/ui/summary_panel.py` (neue Labels)
- `run_trend/ui/main_window.py` (CTL-Pipeline-Aufruf in `_update_summary`)
- `run_trend/translations/runtrend_de.ts` / `runtrend_en.ts` (+ `.qm`)
- `MANUAL_de.md` / `MANUAL_en.md`

## Out of Scope

- **rTSS (Running TSS)** — bräuchte eine konfigurierbare Threshold-Pace
  (LTHR-Pace / FTP-Pace). Banister-TRIMP deckt die HF-basierte Last
  bereits ab. Falls jemand power-meter-äquivalentes Granularität will,
  separates Folge-Ticket.
- **Predictive-Performance** (Form vs. Race-Goal-Date) — Tapering-
  Empfehlungen sind ein eigenes Thema.
- **Multi-Sport-Aggregation** — RunTrend ist Lauf-only.

## Quellen

**Banister-TRIMP:**
- Banister, E. W. (1991). „Modeling Elite Athletic Performance." In:
  *Physiological Testing of Elite Athletes*. Human Kinetics.
  Original-Paper hinter Paywall; gute Sekundärquelle:
  <https://fellrnr.com/wiki/TRIMP>
- Global Performance Insights, Übersicht zur Formel:
  <https://www.globalperformanceinsights.com/post/understanding-trimp-a-guide-to-heart-rate-training-impulse>
- Gender-spezifischer Exponent (b=1.92 / 1.67):
  <https://www.veohtu.com/trimp.html>

**CTL/ATL/TSB:**
- Coggan, A., „The Science of the TrainingPeaks Performance Manager":
  <https://www.trainingpeaks.com/learn/articles/the-science-of-the-performance-manager/>
- TrainingPeaks Coach Guide:
  <https://www.trainingpeaks.com/coach-blog/a-coachs-guide-to-atl-ctl-tsb/>
- Running-spezifische CTL-Anstiegs-Empfehlungen (2-4 / 3-5 / 5-7 pro
  Woche): <https://run.analyticszone.app/en/training-load/>

**Tanaka HRmax (Fallback ohne manual_hrmax):**
- Tanaka, H., Monahan, K. D., Seals, D. R. (2001). *J Am Coll Cardiol*
  37(1): 153–156. PubMed: <https://pubmed.ncbi.nlm.nih.gov/11153730/>
  (bereits in `age_grading.py` aus T37 implementiert).

**Bestehender Spec-Bezug:**
- `specification.md` §10 „Training Status Score" — definiert den
  vorhandenen, selbstrelativen Score. T38 ergänzt, nicht ersetzt.
- T20 (Pace als ACWR-Komponente) — methodische Diskussion zum
  bestehenden Training-Load-Chart, gleiches Spannungsfeld
  „selbstrelativ vs. absolut".
