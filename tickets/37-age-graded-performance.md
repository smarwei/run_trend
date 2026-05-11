# 37 — Age-Graded Performance Chart (WMA + HF-Physiologie)

**Priorität:** P2
**Kategorie:** Feature / Analytics

## Problem

Die App zeigt aktuell **keinen** Vergleich zwischen aktueller Leistung und
„Höchstform fürs Alter". Sämtliche bestehenden Kennzahlen sind
selbst-relativ:

- **Training-Score** (0–100): vergleicht aktuelle Periode gegen
  rollendes Eigen-Baseline — keine externe Referenz.
- **Race-Time-Vorhersagen** (5K/10K/HM/Marathon): absolute Zeiten ohne
  Altersbezug.
- **Efficiency Factor** (EF): Trend über Zeit, kein „theoretisches
  Optimum für mein Alter" sichtbar.

Spec §3 listet sogar „VO2max estimation" als Non-Goal — das Alters-
Grading-Thema wurde bislang umgangen.

Frage des Nutzers, die das Ticket auslöst:

> Gibt es einen Chart, der mir zeigt, wie sich meine Leistung im
> Zeitverlauf entwickelt? Also aktuell vs. ich in maximal möglicher
> Höchstform (Alter berücksichtigt)?

Antwort: nein. Dieses Ticket liefert ihn.

## Lösungsansatz

Neuer Top-Level-Tab **„Performance"**, eingehängt zwischen *Training
Load* und *Projection*. Innerer QTabWidget mit zwei Ansichten:

### Variante A — WMA Age-Grading (etabliert, tabellen-basiert)

[World Masters Athletics](https://world-masters-athletics.org)
veröffentlicht Tabellen, die für jede Kombination (Distanz, Alter,
Geschlecht) einen Faktor liefern. Daraus:

```
age_graded_percent = (world_record_time × age_factor) / your_time
```

Skala: 100 % = Weltrekord-Äquivalent. Übliche Einordnung:
- ≥ 90 %: international class
- 80–90 %: national class
- 70–80 %: regional class
- 60–70 %: local class
- < 60 %: recreational

**Datenquelle:** Aktuelle Version sind die **WMA-2023-Faktoren**
(seit 1. Januar 2023 weltweit verbindlich, abgeleitet aus > 2,8 Mio
historischen Wettkampfzeiten — Vorläufer 1989/1994/2002/2006/2010/2015).
Stand 2026-05 ist das immer noch die aktuelle Version.

Bezugsquellen:
- Original-PDF: <https://world-masters-athletics.org/wp-content/uploads/2023/02/2023-Age-Factors-WMA.pdf>
- Excel-Transkript bei Howard Grubb:
  <https://howardgrubb.co.uk/athletics/data/Appendix-B_2023.xlsx>
  (bewährter Drittanbieter, gleicher Datenbestand)

Im Repo abzulegen als:
`run_trend/analytics/wma_data/wma_2023.csv` mit Spalten
`distance_m, gender, age, factor, wr_time_s`. Ages 30–100, Faktoren
pro Einzeljahr (eines der wichtigsten Updates 2023 gegenüber den
früheren 5-Jahres-Bändern). Für age < 30 → factor = 1.0 (open class).

**Chart:**
- X-Achse: Zeit (Datum)
- Y-Achse: Age-graded % (0–100)
- Linien: 5K, 10K, HM, Marathon (eine pro Distanz)
- Datenpunkte: pro Periode aus den **bestehenden HR-basierten
  Race-Predictions** (`race_predictor.py`)
- Optional-Overlay: tatsächlich gelaufene Rennen aus `race_markers`
  (T15) als Scatter-Punkte — beste Datenpunkte, weil real
- Horizontale Hilfsbänder bei 90/80/70/60 % (international/national/
  regional/local-class), zart eingefärbt

### Variante B — HF-Physiologie / Personal-Peak-Decline

**Wichtige methodische Vorab-Notiz** (aus der Quellen-Recherche
bestätigt): Es gibt **keine publizierten absoluten Referenzwerte**
für EF zwischen „trainiert" und „Elite". Friel selbst betont, EF
ausschließlich gegen die eigene Historie zu vergleichen, nicht gegen
externe Benchmarks. Mein erster Entwurf mit hardcoded
`EF_peak_25 ≈ 0.025/0.035` war wissenschaftlich nicht sauber haltbar.
Stattdessen daher:

**Self-calibrated Personal-Peak-Modell.** Der Peak wird aus der eigenen
Historie ermittelt; die alters-physiologische Komponente macht
*explizit* eine quantifizierte Prognose, wie viel davon im aktuellen
Alter noch erreichbar wäre.

#### Bausteine

1. **HRmax-Schätzung — Tanaka (2001):**
   ```
   HRmax ≈ 208 − 0.7 × Alter
   ```
   Bestätigt aus Meta-Analyse über 351 Studien (n=18.712) + Labor-
   Validierung (n=514). Korrelation r=−0,90. **Gender-unabhängig**
   und unabhängig vom Trainingsstatus. Genauer als `220 − Alter`
   speziell für Masters: bei 70 Jahren weichen die beiden Formeln
   um ca. 10 bpm voneinander ab.

2. **VO2max-Decline-Rate — volumengekoppelt** (Coppola et al. 2022,
   PMC9517884, Meta-Analyse longitudinaler Studien an Masters-
   Athleten):

   | Trainingsstatus                       | Decline / Dekade | Decline / Jahr |
   |---------------------------------------|------------------|----------------|
   | Volumen aufrechterhalten              | 5 – 6,5 %        | 0,5 – 0,65 %   |
   | Moderate Volumen-Reduktion (11–20 %)  | 8 – 26 %         | 0,8 – 2,6 %    |
   | Sedentär (Volumen-Reduktion > 20 %)   | 15 – 46 %        | 1,5 – 4,6 %    |

   **Schlüssel-Insight:** Trainingsvolumen erklärt **54 % (Männer) /
   39 % (Frauen)** der Varianz der individuellen Decline-Rate; mit
   Alter als zusätzlichem Faktor steigt das auf 70 %. Eine
   gemittelte Rate „0,5 %/Jahr für Trainierte" ist daher OK als
   erste Näherung, aber RunTrend hat die Volumen-Daten und kann
   genauer sein.

   **Nicht-Linearität:** Über alle Studien hinweg beschleunigt der
   Decline ab ca. 70 Jahren (Mitochondriale Dysfunktion wird
   dominanter Mechanismus). Linear-Modell als erste Näherung
   akzeptabel, aber Caveat im Tooltip nötig.

3. **Personal-Peak-EF:** Rolling-Best-N-Wochen-Mittel der letzten 12
   Monate (default N = 4 Wochen). „Das war dein bestes 4-Wochen-
   Fenster im letzten Jahr — das ist deine Referenz."

4. **Expected-EF-Curve:** Aus dem Personal-Peak wird via gewichtetem
   Trainings-Volumen pro Periode (`total_distance_km` /
   12-Wochen-Schnitt) der Decline-Pfad geschätzt:
   ```
   expected_ef(t) = personal_peak × (1 − annual_rate(volume_ratio_t) × years_since_peak(t))
   ```
   mit `annual_rate` linear interpoliert in der Tabelle oben
   abhängig vom aktuellen Volumen-Verhältnis.

#### Chart-Layout Variante B

- **X-Achse:** Zeit (Datum)
- **Y-Achse:** Efficiency Factor × 1000 (gleich wie HeartRate-Chart)
- **Gemessene EF** (durchgezogene Linie) — wie bisher
- **Personal-Peak-EF** (horizontale Referenzlinie, „Dein bestes
  4-Wochen-Fenster: NN.NN")
- **Expected-EF-curve** (gestrichelt, ab Peak-Datum nach rechts):
  altersphysiologischer Erwartungspfad bei aktuellem Trainingsvolumen
- **Header-Label:** „Aktuelles EF: NN.NN — N % deines persönlichen
  Peaks (alters-adjustiert)"

## Voraussetzungen — Settings-Erweiterung

Beide Varianten brauchen:

- **Geburtsdatum** (`QDateEdit` im Settings → General-Tab, neue
  „Profile"-Section über dem bestehenden HR-Block)
- **Geschlecht** für Variante A (`QComboBox`: Male / Female / Prefer
  not to say): WMA-Tabellen sind nach Geschlecht getrennt. Variante B
  braucht es **nicht** (Tanaka ist gender-unabhängig, der
  Volumen-gekoppelte Decline ist es auch).

Storage: in `AppSettings` als `birth_date` (ISO-String) und `gender`
(`'male'`/`'female'`/`null`). Default beide unset.

**Empty-State-Verhalten:**
- Variante A ohne `birth_date` ODER ohne `gender`: Hint mit Link zu
  Settings. „Prefer not to say" zeigt einen separaten Hint, *keinen*
  stillen Fallback auf „male" — das verschleiert dem Nutzer, was die
  angezeigte Zahl bedeutet (frühere Annahme im Spec-Entwurf war hier
  unsauber).
- Variante B ohne `birth_date`: Hint. Ohne HR-Daten in den Aggregates:
  separater Hint.

## Datenfluss

```
                       ┌──────────────────────────────┐
                       │  AppSettings                 │
                       │  • birth_date                │
                       │  • gender                    │
                       └──────────┬───────────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                ▼                 ▼                 ▼
        ┌──────────────┐ ┌────────────────┐ ┌─────────────────┐
        │ WMA tables   │ │ Aggregates +   │ │ race_markers    │
        │ (embedded)   │ │ EF per period  │ │ (T15)           │
        └──────┬───────┘ └────┬───────────┘ └─────┬───────────┘
               │              │                   │
               ▼              ▼                   ▼
        ┌──────────────────────────────────────────────────┐
        │  AgeGrading service                              │
        │  • age_at(date)                                  │
        │  • wma_percent(distance, time_s, age, gender)    │
        │  • peak_ef(age, gender, level)                   │
        └────────────────────────┬─────────────────────────┘
                                 ▼
                       ┌──────────────────┐
                       │  AgeGradingChart │
                       │  (WMA tab + HF)  │
                       └──────────────────┘
```

## Acceptance

- [ ] **Settings:** Birth-date-QDateEdit + Gender-Combo in General-Tab,
      persistiert, Default beide unset
- [ ] **WMA-Tabellen** als CSV im Repo (`run_trend/analytics/wma_data/`),
      Lizenz-Hinweis im Header
- [ ] **`run_trend/analytics/age_grading.py`** mit den pure-functions:
  - `age_on_date(birth_date, on_date) → int` (inkl. Schaltjahr-29.02.)
  - `wma_factor(distance_m, age, gender) → float`
  - `wma_percent(time_s, distance_m, age, gender) → float`
  - `tanaka_hrmax(age) → int`
  - `vo2max_annual_decline_rate(volume_ratio: float) → float`
    — lineare Interpolation der Volumen→Decline-Tabelle aus
    Variante B Baustein 2
  - `personal_peak_ef(ef_history: list[float], window_weeks=4) → tuple[float, datetime]`
    — bestes Rolling-Mittel der letzten 12 Monate + zugehöriges Datum
  - `expected_ef(peak, peak_date, current_date, volume_ratio) → float`
- [ ] **`run_trend/charts/age_grading_chart.py`** neu, mit innerem
      QTabWidget „WMA Age-Graded %" + „Aerobic Capacity %"
- [ ] **MainWindow-Integration:** neuer Tab „Performance" zwischen
      „Training Load" und „Projection"
- [ ] **Empty-States:** Geburtsdatum fehlt → Hint mit Link zu Settings;
      Geschlecht fehlt analog; keine HR-Daten → HF-Tab leer mit Hint
- [ ] **Tests** (jeweils ≥ 4 Cases):
  - `tests/test_age_grading.py`: WMA-Lookup an publizierten Werten
    sanity-prüfen, Alters-Berechnung inkl. Schaltjahr-29.02.,
    Tanaka-HRmax, Peak-EF-Decline
  - `tests/test_age_grading_chart.py`: 2 Empty-States, Variante-A-Render
    mit Mock-Aggregates, Variante-B-Render mit Mock-EF-Werten
- [ ] **i18n:** Alle Strings durch `self.tr(...)`, DE/EN-Übersetzungen
- [ ] **Manual** (`MANUAL_de.md` / `MANUAL_en.md`): kurzer Abschnitt
      „Performance-Tab" mit Erklärung beider Skalen und Quellenangabe

## Methodische Punkte (vor Code klären)

1. **WMA-Tabellen-Version**: **WMA 2023** ist Stand 2026-05 die
   verbindliche, aktuelle Version (seit 1. Jan 2023 in Kraft). Im Code
   mit Versions-Konstante `WMA_VERSION = "2023"` markieren, damit
   spätere Updates einfach bleiben.
2. **„Prefer not to say"**: Ergibt keinen sinnvollen Age-Graded-Wert
   in Variante A — WMA-Tabellen sind geschlechts-getrennt. UI zeigt
   in dem Fall einen expliziten Hint („Bitte Geschlecht setzen, damit
   die Tabelle angewandt werden kann"), **kein** stiller Default auf
   „male" (war im ersten Spec-Entwurf vorgesehen, ist intransparent).
3. **VO2max-Decline-Rate**: Volumen-gekoppelt (siehe Variante B
   Baustein 2). Kein Toggle, kein User-Input — die App rechnet aus
   `total_distance_km` der letzten 12 Wochen vs. Peak-Volumen.
4. **EF-Baseline**: **Self-calibrated** (Rolling-Best der letzten 12
   Monate), nicht hardcoded. Friel selbst und alle Quellen warnen vor
   absoluten EF-Benchmarks zwischen Athleten. Wir respektieren das.
   Cold-Start-Problem: < 12 Monate Datenhistorie → Variante B zeigt
   Hint „Mindestens 12 Monate Daten nötig für Personal-Peak".
5. **Non-Linearität nach 70**: Linearer Decline ist über Alter 70
   hinaus zu optimistisch (Mitochondriale-Dysfunktion-Mechanismus
   gewinnt). Default: linearer Decline, plus Tooltip-Caveat im
   Chart-Help-Icon. Wer betroffen ist, kann den Hinweis lesen.
6. **Race-Marker als Datenpunkte (Variante A)**: ja — Race-Predictions
   als Linie, `race_markers`-Einträge mit echten Zeiten als Scatter-
   Overlay. Reale Zeiten sind belastbarer als HR-basierte Predictions.

## Slice-Plan

Empfohlene Mergreihenfolge (analog T19):

- **Slice 1** — `age_grading.py` (pure functions, getestet) +
  WMA-CSV im Repo. Kein UI.
- **Slice 2** — Settings-Erweiterung (Birth-Date + Gender im
  General-Tab) + Tests.
- **Slice 3** — `AgeGradingChart` Variante A (WMA), MainWindow-Tab,
  i18n.
- **Slice 4** — `AgeGradingChart` Variante B (HF-Physiologie),
  Empty-States, i18n.
- **Slice 5** — Race-Marker-Overlay auf Variante A.
- **Slice 6** — Manual-Update DE/EN.

Slice 1 ist isoliert mergeable; Slice 2 ist Voraussetzung für 3 und 4.

## Dateien (neu)

- `run_trend/analytics/age_grading.py`
- `run_trend/analytics/wma_data/wma_2020.csv` (+ LICENSE-Note)
- `run_trend/charts/age_grading_chart.py`
- `tests/test_age_grading.py`
- `tests/test_age_grading_chart.py`

## Dateien (geändert)

- `run_trend/ui/settings_dialog.py` (Profile-Section)
- `run_trend/ui/main_window.py` (Tab-Insertion + a11y-Eintrag)
- `run_trend/translations/runtrend_de.ts` / `runtrend_en.ts` (+ `.qm`)
- `MANUAL_de.md` / `MANUAL_en.md`

## Out of Scope

- VO2max-Schätzung im engeren Sinn (Spec-§3-Non-Goal bleibt) — wir
  berechnen *kein* VO2max, sondern nutzen EF als Proxy.
- Distanzen jenseits Marathon (50K, Ultra) — WMA-Tabellen haben sie,
  aber UI-Nutzen ist gering. Folge-Ticket falls gewünscht.
- Spirometrie-Daten / Wahoo-/Garmin-FTP-Import.
- Bayesian-Confidence-Bänder um die WMA-Linien.

## Quellen

**WMA Age-Grading:**
- WMA Age Factors 2023 (offiziell):
  <https://world-masters-athletics.org/wp-content/uploads/2023/02/2023-Age-Factors-WMA.pdf>
- WMA News „Age Grading Leaps Forward" (Herleitung aus 2,8 Mio
  Performances): <https://world-masters-athletics.org/news/age-grading-leaps-forward/>
- Howard Grubb's WMA-2023-Calculator + Excel-Daten:
  <https://howardgrubb.co.uk/athletics/wmatnf23.html>

**HRmax:**
- Tanaka, H., Monahan, K. D., Seals, D. R. (2001). „Age-predicted
  maximal heart rate revisited." *J Am Coll Cardiol* 37(1): 153–156.
  PubMed: <https://pubmed.ncbi.nlm.nih.gov/11153730/>
  ScienceDirect: <https://www.sciencedirect.com/science/article/pii/S0735109700010548>

**VO2max-Decline (volumen-gekoppelt):**
- Coppola, A., et al. (2022). „The Impact of Training on the Loss of
  Cardiorespiratory Fitness in Aging Masters Endurance Athletes."
  *Int J Environ Res Public Health* 19(17): 11050.
  PMC: <https://pmc.ncbi.nlm.nih.gov/articles/PMC9517884/>
- Pimentel, A. E., et al. (2003). „Greater rate of decline in maximal
  aerobic capacity with age in endurance-trained than in sedentary men."
  *J Appl Physiol* 94(6): 2406–2413 (referenziert im obigen Review).
- Pollock, M. L., et al. (1997). „Twenty-year follow-up of aerobic
  power and body composition of older track athletes." *J Appl
  Physiol* 82: 1508–1516.

**Efficiency Factor:**
- Joe Friel, „The Efficiency Factor in Running":
  <https://joefrieltraining.com/the-efficiency-factor-in-running-2/>
- TrainingPeaks, „Aerobic Decoupling and EF":
  <https://www.trainingpeaks.com/blog/efficiency-factor-and-decoupling/>
- (Beide Quellen empfehlen ausdrücklich Self-Comparison über Zeit,
  nicht absolute Cross-Athlete-Benchmarks.)

**Bestehende App-Komponenten:**
- McMillan Running Calculator (Basis der Race-Predictions in
  `race_predictor.py`)
- T15 Race-Markers (DB-Tabelle, Quelle für Variante-A-Overlay)
