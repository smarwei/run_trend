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

**Datenquelle:** WMA-2020-Tabellen (publiziert, gemeinfrei verfügbar
als CSV). Müssen ins Repo als embedded data:
`run_trend/analytics/wma_data/wma_2020.csv` mit Spalten
`distance_m, gender, age, factor, wr_time_s`.

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

### Variante B — HF-Physiologie / EF-Decline

Klassisches HF-Modell:
- **Tanaka (2001):** `HRmax ≈ 208 − 0.7 × Alter` (genauer als
  220 − Alter, gerade für Masters relevant)
- **Aerobic-Decline:** VO2max sinkt nach Alter 30 um ~0.5 %/Jahr bei
  trainierten, ~1 %/Jahr bei sedentär (Fitzgerald 2018, Pollock 1997)

Daraus eine **theoretische-Peak-EF-Kurve**:

```
EF_peak(age) = EF_peak_25 × (1 − 0.005 × max(0, age − 30))     # trained
EF_peak(age) = EF_peak_25 × (1 − 0.010 × max(0, age − 30))     # untrained
```

Mit `EF_peak_25 ≈ 0.025` für „gut trainiert, nicht-elite" und
`EF_peak_25 ≈ 0.035` für Elite-Niveau.

**Chart:**
- X-Achse: Zeit (Datum)
- Y-Achse: Efficiency Factor × 1000 (gleich wie HeartRate-Chart)
- Gemessene EF aus den Aggregates (durchgezogene Linie)
- Referenz-Peak-EF für aktuelles Alter (gestrichelte Linie, „Trained-
  Peak fürs Alter")
- Optionale obere Linie: „Elite-Peak fürs Alter" (dünn, gepunktet)
- Aerobic-Capacity-% = `gemessene_EF / EF_peak(age) × 100` als
  Header-Label

## Voraussetzungen — Settings-Erweiterung

Beide Varianten brauchen:

- **Geburtsdatum** (`QDateEdit` im Settings → General-Tab, neue
  „Profile"-Section über dem bestehenden HR-Block)
- **Geschlecht** (`QComboBox`: Male / Female / Prefer not to say —
  letzteres mappt intern auf „male" als konservativer Default;
  WMA-Tabellen brauchen ein Geschlecht)

Storage: in `AppSettings` als `birth_date` (ISO-String) und `gender`
(`'male'`/`'female'`). Default beide unset; Empty-State im Performance-
Chart wenn nicht konfiguriert.

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
- [ ] **`run_trend/analytics/age_grading.py`** mit den pure-functions
      `age_on_date(birth_date, on_date) → int`,
      `wma_factor(distance_m, age, gender) → float`,
      `wma_percent(time_s, distance_m, age, gender) → float`,
      `tanaka_hrmax(age) → int`,
      `peak_ef(age, gender, level='trained') → float`,
      `aerobic_capacity_percent(measured_ef, age, gender) → float`
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

1. **WMA-Tabellen-Version**: WMA 2020 ist die aktuell publizierte
   Version. WMA 2023 ist angekündigt aber zum Stand 2026-05 nicht
   final. Default = 2020, in Code mit Versions-Konstante markiert,
   damit ein Update später einfach ist.
2. **„Prefer not to say" → male**: Standard-Konvention bei Age-Grading-
   Rechnern. Liefert konservativeren (niedrigeren) Prozentsatz, weil
   männliche WR-Zeiten schneller sind. Alternative: keinen Wert
   anzeigen → noch konservativer, aber unbefriedigend für den Nutzer.
3. **Trained-vs-Untrained-Decline**: Default 0.5 %/Jahr (trained), weil
   die App per Definition Trainings-Daten anschaut. Über einen
   Settings-Toggle änderbar?
4. **EF_peak_25-Baseline**: 0.025 ist „gut trainiert Hobby". Sollte
   benutzer-kalibrierbar sein — z. B. „Best-ever-EF in den letzten
   12 Monaten" als persönliches Peak. Frage: hardcoded vs.
   self-calibrated?
5. **Race-Marker als Datenpunkte**: nutzen wir tatsächlich gelaufene
   Rennen (echte Zeiten) zusätzlich zu Vorhersagen? Empfehlung: ja —
   Vorhersagen als Linie, Marker als Scatter-Overlay (visuell anders),
   weil reale Zeiten die belastbarsten Datenpunkte sind.

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

- WMA Age-Grading Tables 2020: <https://world-masters-athletics.org>
- Tanaka, H., Monahan, K. D., Seals, D. R. (2001). „Age-predicted
  maximal heart rate revisited." *J Am Coll Cardiol* 37(1): 153–156.
- Pollock, M. L., et al. (1997). „Twenty-year follow-up of aerobic
  power and body composition of older track athletes." *J Appl
  Physiol* 82: 1508–1516.
- McMillan Running Calculator (für die bestehenden Race-Predictions)
