# Running Progress Tracker - Benutzerhandbuch

## Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Erste Schritte](#erste-schritte)
3. [Benutzeroberfläche](#benutzeroberfläche)
4. [Metriken-Erklärungen](#metriken-erklärungen)
5. [Charts und Visualisierungen](#charts-und-visualisierungen)
6. [Einstellungen](#einstellungen)
7. [Über diese Software](#über-diese-software)

---

## Übersicht

Running Progress Tracker ist eine Desktop-Anwendung zur Analyse deines Lauftrainings. Sie synchronisiert deine Aktivitäten von Strava und bietet umfassende Analysen für:

- Distanzfortschritt und Trainingsvolumen
- Pace- und Geschwindigkeitsentwicklung
- Trainingshäufigkeit und Konsistenz
- Langstreckenfähigkeit (Long Runs)
- Trainingsstruktur und -muster
- **Herzfrequenz und aerobe Fitness (Efficiency Factor)**
- Trendprognosen und Meilenstein-Schätzungen

Die Anwendung ist besonders hilfreich für die Vorbereitung auf Langstreckenläufe wie Halbmarathon und Marathon.

---

## Erste Schritte

### 1. Strava-Verbindung einrichten

1. Klicke auf **"Settings"** in der Toolbar
2. Trage deine Strava API Credentials ein:
   - **Client ID**: Von https://www.strava.com/settings/api
   - **Client Secret**: Von https://www.strava.com/settings/api
3. Klicke auf **"Save"**
4. Klicke auf **"Connect to Strava"** (im Settings Dialog)
5. Autorisiere die Anwendung im Browser

### 2. Aktivitäten synchronisieren

**Erster Sync (beim ersten Start):**

1. Der Settings Dialog öffnet sich automatisch
2. Gib deine Strava API Credentials ein und klicke **"Connect to Strava"**
3. Autorisiere im Browser
4. Du wirst gefragt, ob du jetzt synchronisieren möchtest → Klicke **"Yes"**
5. Alle Läufe seit 1. Januar 2000 werden importiert (erfasst garantiert alle Strava-Aktivitäten)

**Hinweis:** Das Start-Datum in der Toolbar bestimmt beim ersten Sync, ab wann importiert wird. Standard ist 1. Januar 2000, was alle möglichen Strava-Aktivitäten abdeckt (Strava wurde 2009 gegründet).

**Weitere Syncs (automatisch):**

Nach dem ersten Sync läuft die Synchronisation automatisch:
- Beim App-Start: Stille Prüfung auf neue Aktivitäten im Hintergrund
- Nur neue/geänderte Aktivitäten werden geladen (inkrementell)

Nur **Outdoor-Läufe** werden importiert. Folgende Aktivitäten werden ausgeschlossen:
- Laufband/VirtualRun
- Gehen/Walk
- Radfahren/Ride
- Krafttraining/WeightTraining
- Yoga, Schwimmen, etc.

### 3. Daten analysieren

Nach der Synchronisation werden deine Läufe automatisch aggregiert und visualisiert:
- Wähle die **Period** (Week/Month) in der Toolbar
- Passe das **Start Date** an, um nur einen bestimmten Zeitraum anzuzeigen
- Nutze **Smoothing** um Trends besser zu erkennen
- Wechsle zwischen den verschiedenen Chart-Tabs (Overview, Endurance, Score, Projection)

---

## Benutzeroberfläche

### Toolbar

- **Settings**: Strava API Credentials verwalten, mit Strava verbinden, Aktivitäten synchronisieren
- **Start Date**: Startdatum für Datenfilterung (ab wann werden Läufe in Charts angezeigt)
- **Period**: Aggregationszeitraum (Week/Month)
- **Metric**: Pace oder Speed für Geschwindigkeits-Charts
- **Smoothing**: Glättungsstärke für Charts (Off/Light/Medium/Strong)
- **Help**: Dieses Handbuch öffnen (ganz rechts in der Toolbar)

### Zusammenfassungspanel (links)

Zeigt aktuelle KPIs basierend auf deinen Daten:

**Volumen-Metriken:**
- **Gesamtzahl der Läufe**: Alle aufgezeichneten Läufe
- **Gesamtdistanz**: Summe aller Läufe (lifetime)
- **Period Distance**: Durchschnittliche Distanz pro Periode (z.B. ~27 km/Woche)

**Performance-Metriken:**
- **Aktuelles durchschnittliches Pace**: Gewichteter Durchschnittspace

**Herzfrequenz-Metriken** (wenn HR-Daten vorhanden):
- **Durchschnittliche Herzfrequenz**: Durchschnitt der aktuellen Periode
- **Maximale Herzfrequenz (Lifetime)**: Höchster jemals gemessener Wert
- **Efficiency Factor**: Pace-normalisierte Herzfrequenz (aerobe Fitness)

**Fortschrittsindikatoren:**
- **Training Score**: Kombinierte Metrik aus Volumen, Frequenz, Pace und Effizienz (0-100)
- **Marathon-Meilenstein**: Geschätztes Datum für 32 km Long Run / Marathon-Ready (oder "Milestone Reached!")
- **Race Time Predictions**: Geschätzte Wettkampfzeiten für 5K, 10K, Half und Marathon (HR-basiert)

### Charts (rechts)

Die Charts sind in 5 Hauptkategorien organisiert:

#### 1. Overview Tab
- **Distance**: Gesamtdistanz pro Periode
- **Pace/Speed**: Pace oder Geschwindigkeit
- **Frequency**: Anzahl der Läufe

#### 2. Heart Rate Tab
- **Heart Rate Range**: Min-Max Herzfrequenz-Bereich pro Periode
- **Average HR**: Durchschnittliche Herzfrequenz
- **Efficiency Factor**: Pace-normalisierte Herzfrequenz

#### 3. Endurance Tab
- **Longest Run**: Längster Lauf pro Periode
- **Avg Distance/Run**: Durchschnittliche Distanz pro Lauf

#### 4. Score Tab
- **Training Score**: Kombinierter Trainingsfortschritt

#### 5. Projection Tab
- **Projection**: Trendprognosen für Volume oder Long Runs

---

## Metriken-Erklärungen

### Total Load Metrics (Gesamtbelastung)

#### Total Distance per Period
**Was es ist:** Summe aller Laufdistanzen in der gewählten Periode (Woche/Monat).

**Berechnung:** `sum(alle Läufe in der Periode)`

**Interpretation:**
- Zeigt das Trainingsvolumen
- Höhere Werte = mehr Gesamtbelastung
- Wichtig für Ausdauerentwicklung

**Beispiel:** 3 Läufe à 10km, 8km, 5km = 23 km total

#### Period Distance (Aktuelle Periodendistanz)
**Was es ist:** Durchschnittliche Gesamtdistanz pro Periode für die aktuelle Aggregation.

**Berechnung:** `average(total_distance der letzten 12 Perioden)`

**Interpretation:**
- Zeigt dein **aktuelles durchschnittliches Wochenvolumen** (bei wöchentlicher Ansicht)
- Zeigt dein **aktuelles durchschnittliches Monatsvolumen** (bei monatlicher Ansicht)
- Wird im Summary Panel angezeigt
- Baseline für die Training Score Normalisierung

**Beispiel:**
- Letzte 12 Wochen: 20, 25, 30, 28, 22, 27, 30, 32, 28, 25, 30, 33 km
- **Period Distance**: ~27.5 km/Woche
- Dies ist dein aktueller "Normalzustand"

**Unterschied zu Total Distance:**
- **Total Distance**: Spezifische Distanz einer einzelnen Periode (z.B. "Diese Woche: 30 km")
- **Period Distance**: Durchschnittliche Distanz über viele Perioden (z.B. "Durchschnitt: 27.5 km/Woche")

#### Total Moving Time
**Was es ist:** Gesamte Bewegungszeit aller Läufe in der Periode.

**Berechnung:** `sum(moving_time aller Läufe)`

**Interpretation:**
- Zeigt die investierte Trainingszeit
- Unabhängig von der Geschwindigkeit

#### Number of Runs
**Was es ist:** Anzahl der Läufe in der Periode.

**Berechnung:** `count(Läufe)`

**Interpretation:**
- Zeigt Trainingskonsistenz
- Mehr Läufe = häufigeres Training
- Nicht zwingend höhere Distanz

### Training Structure Metrics (Trainingsstruktur)

#### Average Distance per Run
**Was es ist:** Durchschnittliche Länge eines Laufs in der Periode.

**Berechnung:** `total_distance / number_of_runs`

**Interpretation:**
- Zeigt die typische Lauflänge
- **Nicht immer "höher ist besser"**
- Kann sinken, wenn du mehr kürzere Läufe machst
- Kann steigen, wenn du weniger, aber längere Läufe machst

**Wichtiger Unterschied:**
- **Gleiche Gesamtdistanz** kann durch verschiedene Strukturen entstehen:
  - 30 km = 3 × 10 km (Avg: 10 km)
  - 30 km = 6 × 5 km (Avg: 5 km)

**Beispiel:**
- Woche A: 5 Läufe, 50 km total → Avg: 10 km/Lauf
- Woche B: 10 Läufe, 50 km total → Avg: 5 km/Lauf

Beide haben gleiches Volumen, aber unterschiedliche Struktur!

#### Longest Run per Period
**Was es ist:** Die maximale Einzellaufdistanz in der Periode.

**Berechnung:** `max(distance aller Läufe in der Periode)`

**Interpretation:**
- **Wichtigste Metrik für Langstreckenvorbereitung**
- Zeigt spezifische Ausdauerfähigkeit
- Kritisch für Marathon/Halbmarathon-Training
- Kann nicht aus Gesamtdistanz abgeleitet werden

**Warum wichtig:**
Zwei Perioden mit gleicher Gesamtdistanz können völlig unterschiedliche Ausdauerfähigkeiten zeigen:

- **Periode A**: 50 km total, längster Lauf: 12 km
- **Periode B**: 50 km total, längster Lauf: 28 km

Periode B zeigt deutlich höhere Langstreckenausdauer!

### Performance Metrics (Leistung)

#### Weighted Average Pace
**Was es ist:** Gewichteter Durchschnittspace der Periode.

**Berechnung:** `total_moving_time / total_distance`

**Wichtig:** Dies ist NICHT der einfache Durchschnitt aller Paces!

**Warum gewichtet:**
Längere Läufe beeinflussen den Durchschnitt stärker.

**Beispiel:**
- Lauf 1: 10 km in 50 min = 5:00 min/km
- Lauf 2: 5 km in 30 min = 6:00 min/km
- Einfacher Durchschnitt: (5:00 + 6:00) / 2 = 5:30 min/km
- **Gewichteter Durchschnitt**: 80 min / 15 km = 5:20 min/km ✓

#### Average Speed
**Was es ist:** Durchschnittsgeschwindigkeit in km/h.

**Berechnung:** `total_distance / total_moving_time`

**Beziehung zu Pace:** Kehrwert des Pace, in km/h statt min/km

#### Training Score (0-100)
**Was es ist:** Kombinierte Metrik aus Volumen, Frequenz, Pace-Fortschritt und aerober Fitness.

**Berechnung (mit HR-Daten):**
```
training_score = (
    0.30 × normalized_distance +
    0.20 × normalized_frequency +
    0.30 × normalized_pace +
    0.20 × normalized_efficiency
) × 50
```

**Komponenten (mit HR-Daten):**
- **30% Distanz**: Trainingsvolumen
- **30% Pace**: Geschwindigkeitsverbesserung
- **20% Efficiency Factor**: Aerobe Fitness (pace-normalisierte HR)
- **20% Frequenz**: Trainingskonsistenz

**Berechnung (ohne HR-Daten):**
```
training_score = (
    0.375 × normalized_distance +
    0.250 × normalized_frequency +
    0.375 × normalized_pace
) × 50
```

**Komponenten (ohne HR-Daten):**
- **37.5% Distanz**: Trainingsvolumen
- **37.5% Pace**: Geschwindigkeitsverbesserung
- **25% Frequenz**: Trainingskonsistenz

**Wichtig:** Die Gewichte passen sich automatisch an, wenn für eine Periode keine Herzfrequenz-Daten verfügbar sind.

**Interpretation:**
- 0-25: Niedriges Trainingsniveau
- 25-50: Moderates Training
- 50-75: Gutes Trainingsniveau
- 75-100: Sehr hohes Trainingsniveau

**Wichtig:** Der Score ist eine Zusammenfassung. Er ersetzt NICHT die strukturellen Metriken wie Longest Run oder Average Distance per Run, die separat betrachtet werden sollten.

### Heart Rate Metrics (Herzfrequenz)

#### Average Heart Rate per Period
**Was es ist:** Durchschnittliche Herzfrequenz aller Läufe mit HR-Daten in der Periode.

**Berechnung:** `sum(average_heartrate aller HR-Läufe) / count(HR-Läufe)`

**Interpretation:**
- Zeigt die typische Herzfrequenz während des Trainings
- **Niedriger Wert bei gleichem Pace** = bessere aerobe Fitness
- Wichtig: Nur Läufe mit HR-Daten werden berücksichtigt

**Hinweis:** Läufe ohne Herzfrequenz-Monitor werden nicht in diese Metrik einbezogen.

#### Min/Max Heart Rate Range
**Was es ist:** Bereich der Herzfrequenzen in der Periode.

**Min Average HR:** Niedrigster Durchschnittswert eines einzelnen Laufs
**Max HR:** Höchster gemessener Herzfrequenz-Peak über alle Läufe

**Berechnung:**
- `min_avg_hr = min(average_heartrate aller HR-Läufe)`
- `max_hr = max(max_heartrate aller HR-Läufe)`

**Interpretation:**
- Zeigt die Bandbreite der Trainingsintensitäten
- Großer Bereich = verschiedene Trainingsintensitäten
- **Min Average HR**: Zeigt entspanntes Tempo (z.B. Recovery Runs)
- **Max HR**: Zeigt Spitzenbelastung (z.B. Intervalle, Wettkämpfe)

**Beispiel:**
- Woche mit 4 Läufen:
  - Recovery Run: Avg 135 bpm, Max 145 bpm
  - Easy Run: Avg 145 bpm, Max 155 bpm
  - Tempo Run: Avg 165 bpm, Max 175 bpm
  - Long Run: Avg 150 bpm, Max 170 bpm
- **Min Average HR**: 135 bpm (Recovery Run)
- **Max HR**: 175 bpm (Peak aus Tempo Run)
- **Range**: 135-175 bpm

#### Lifetime Max Heart Rate
**Was es ist:** Höchste jemals gemessene Herzfrequenz über ALLE Läufe hinweg.

**Berechnung:** `max(max_heartrate aller Läufe in der Datenbank)`

**Interpretation:**
- Zeigt deine maximale Herzfrequenz-Kapazität
- Wird im Summary Panel angezeigt (konstanter Wert)
- Ändert sich nur, wenn ein neuer Höchstwert erreicht wird
- Wichtig für die Berechnung von HR-Zonen

**Unterschied zur Period Max HR:**
- **Period Max HR**: Höchster Wert in einer bestimmten Woche/Monat
- **Lifetime Max HR**: Höchster Wert EVER (über alle Zeiten)

**Beispiel:**
- Lifetime Max HR: 192 bpm (erreicht in einem Wettkampf im Juni 2024)
- Aktuelle Woche Max HR: 178 bpm (normale Trainingsintensität)

**Hinweis:** Wird nur angezeigt, wenn mindestens ein Lauf mit HR-Daten vorhanden ist.

#### Efficiency Factor (EF)

**Was es ist:** Verhältnis von Geschwindigkeit zur Herzfrequenz - ein Maß für aerobe Effizienz.

**Formel:**
```
Efficiency Factor = Geschwindigkeit (m/s) / Durchschnittliche Herzfrequenz (bpm)
```

**Herkunft:** Industry-Standard Metrik von TrainingPeaks/Joe Friel

**Was es misst:**
- Wie viele Meter du pro Herzschlag zurücklegst
- **Höherer Wert = bessere aerobe Fitness**
- Normalisiert die Herzfrequenz für unterschiedliche Geschwindigkeiten

**Warum wichtig:**
Die rohe Herzfrequenz allein ist nicht aussagekräftig, weil:
- Schnelleres Tempo → natürlich höhere HR
- Langsameres Tempo → natürlich niedrigere HR

Der Efficiency Factor erlaubt einen fairen Vergleich!

**Beispiel 1: Fitness-Verbesserung**

**Vor 3 Monaten:**
- Pace: 6:00 min/km (2.78 m/s)
- Avg HR: 155 bpm
- **EF = 2.78 / 155 = 0.0179**

**Heute:**
- Pace: 5:30 min/km (3.03 m/s)
- Avg HR: 150 bpm
- **EF = 3.03 / 150 = 0.0202**

**Interpretation:** EF ist gestiegen → aerobe Fitness hat sich verbessert! Du läufst schneller bei niedrigerer Herzfrequenz.

**Beispiel 2: Warum EF besser ist als rohe HR**

**Athlet A:**
- Tempo Run: 5:00 min/km (3.33 m/s), HR: 165 bpm
- **EF = 3.33 / 165 = 0.0202**

**Athlet B:**
- Easy Run: 6:30 min/km (2.56 m/s), HR: 140 bpm
- **EF = 2.56 / 140 = 0.0183**

Athlet B hat eine niedrigere HR, aber Athlet A hat die bessere aerobe Effizienz!

**Visualisierung:**
- Im Chart wird EF mit Faktor 1000 dargestellt für bessere Lesbarkeit
- EF = 0.0179 → angezeigt als 17.9
- EF = 0.0202 → angezeigt als 20.2

**Langfristiger Nutzen:**
Verfolge deinen EF über Monate, um aerobe Fitness-Verbesserungen zu sehen:
- Steigender EF = bessere Ausdauer
- Konstanter EF trotz höherem Volumen = gute Erholung
- Fallender EF = mögliche Übertraining oder Ermüdung

**Wichtig:** Vergleiche EF nur mit deinen eigenen Werten, nicht mit anderen Athleten (individuelle HR-Bereiche variieren stark).

### Progress Indicators (Fortschrittsindikatoren)

#### Marathon Milestone (Marathon-Meilenstein)
**Was es ist:** Geschätztes Datum, wann du voraussichtlich einen 32 km Long Run laufen kannst - der Standard-Trainingslauf für Marathon-Vorbereitung.

**Berechnung:** Basiert auf der **Long Run Projektion** (lineare Regression der letzten 12 Perioden).

**Warum 32 km und nicht 42 km?**
- **32 km = 20 Meilen**: Standard in allen professionellen Marathon-Trainingsplänen (Hal Higdon, Pete Pfitzinger, FIRST)
- **Nicht 42 km im Training**: Zu hohes Verletzungsrisiko, zu lange Regeneration (2-3 Wochen)
- **Marathon-Ready bedeutet**: Die letzten 10 km schafft man am Renntag durch Wettkampfbedingungen

**Im Summary Panel angezeigte Status:**
- **"Estimated: YYYY-MM-DD"**: Geschätztes Datum für 32 km Long Run (Marathon-Ready!)
- **"Milestone Reached!"**: Du hast bereits einen 32+ km Lauf absolviert
- **"Keep training!"**: Aktueller Trend erreicht 32 km nicht (Projektion negativ oder zu flach)

**Interpretation:**
- Dies ist eine **Long Run Milestone**, NICHT eine Volumen-Milestone
- Beantwortet die Frage: "Wann bin ich Marathon-Ready?" (32 km Long Run)
- Basiert nur auf deiner Longest Run Progression

**Wichtiger Unterschied:**
Die Marathon Milestone im Summary Panel zeigt NUR die 32 km Long Run Projektion. Im Projection Tab kannst du zusätzliche Milestones sehen:
- **Volume Mode**: 5K, 10K, Half Marathon, Marathon Ready (32K) Wochenvolumen
- **Long Run Mode**: 10K, 15K, Half Marathon, 30K, Marathon Ready (32K) Long Runs

**Beispiel:**
```
Longest Runs letzte 12 Wochen:
Woche 1: 15 km
Woche 6: 20 km
Woche 12: 28 km

Trend: +1 km pro Woche
→ Marathon Milestone: "Estimated: 2025-04-21"
(in ~4 Wochen erreichst du 32 km - Marathon Ready!)
```

**Warum wichtig:**
- Marathon-Vorbereitung erfordert Long Run Ausdauer
- Ein 32 km Long Run zeigt Marathon-Readiness
- Wichtiger als hohes Wochenvolumen
- Siehe auch: Projection Tab → Long Run Mode für detaillierte Progression

**Trainings-Tipp:**
Nach Erreichen von 32 km bist du Marathon-Ready! Typischer Trainingsplan danach:
- 3 Wochen vor Marathon: 32 km Long Run
- 2 Wochen vor Marathon: Tapering (20-25 km)
- 1 Woche vor Marathon: Tapering (10-15 km)
- Renntag: 42.195 km (mit Adrenalin + Wettkampfenergie!)

**Hinweis:** Die Schätzung ist nur so gut wie dein aktueller Trend. Änderungen im Trainingsplan beeinflussen das Datum.

#### Race Time Predictions (Wettkampfzeit-Vorhersagen)
**Was es ist:** Geschätzte Wettkampfzeiten für 5K, 10K, Halbmarathon und Marathon basierend auf deinem Easy Run Pace.

**Wissenschaftliche Basis:** McMillan Calculator (trainingszonbasierte Vorhersage)

**Methode:**
1. **Easy Runs identifizieren** (HR-basiert):
   - Läufe mit 60-75% von HRmax (Zone 2 / Aerobic Zone)
   - Mindestens 5 km Distanz
   - Nur letzte 6 Monate

2. **Median Easy Pace berechnen**:
   - Aus allen identifizierten Easy Runs
   - Median (nicht Average) = robust gegen Ausreißer

3. **McMillan Formula anwenden**:
   ```
   5K Pace         = Easy Pace - 75 sec/km
   10K Pace        = Easy Pace - 60 sec/km
   Half Marathon   = Easy Pace - 45 sec/km
   Marathon Pace   = Easy Pace - 30 sec/km
   ```

**Beispiel:**
```
Easy Runs identifiziert:
- 10 km @ 6:00/km, HR 140 bpm (70% von 200)
- 8 km @ 6:10/km, HR 138 bpm (69% von 200)
- 12 km @ 5:50/km, HR 142 bpm (71% von 200)

Median Easy Pace: 6:00/km

Predictions:
- 5K:      4:45/km → 23:45 Minuten
- 10K:     5:00/km → 50:00 Minuten
- Half:    5:15/km → 1:50:34
- Marathon: 5:30/km → 3:52:04
```

**Voraussetzungen:**
- ✅ Herzfrequenz-Daten vorhanden
- ✅ HRmax bekannt (aus Daten geschätzt)
- ✅ Mindestens 3 Easy Runs (5+ km) in letzten 6 Monaten
- ✅ Läufe in Zone 2 (60-75% HRmax)

**Anzeige im Summary Panel:**
- **5K: 23:45 (4:45/km)** - Zeit und Pace
- **10K: 50:00 (5:00/km)**
- **Half: 1:50:34 (5:15/km)**
- **Marathon: 3:52:04 (5:30/km)**
- Info: "Based on X easy runs (pace: Y/km). McMillan formula with HR zones."

**Wichtige Hinweise:**

⚠️ **Dies sind SCHÄTZUNGEN!** Tatsächliche Race-Zeiten können abweichen durch:
- **Wettkampf-Erfahrung**: Erste Rennen sind oft langsamer
- **Tapering**: Ausgeruhte Beine laufen schneller
- **Kurs & Wetter**: Hügel, Wind, Hitze beeinflussen stark
- **Renn-Fitness vs. Training-Fitness**: Manche laufen schneller im Wettkampf

⚠️ **Nur für Endurance-Ready Athleten:**
- **5K Prediction**: Sinnvoll ab ~5 km Longest Run
- **10K Prediction**: Sinnvoll ab ~8 km Longest Run
- **Half Prediction**: Sinnvoll ab ~15 km Longest Run
- **Marathon Prediction**: Nur nach "Marathon Ready" (32 km Long Run!)

**Warum HR-basiert besser ist als nur Pace:**

❌ **Nur Training-Pace**: Vermischt Easy/Tempo/Long Runs → ungenau
✅ **HR-basierte Easy-Run-Erkennung**: Filtert echte Zone-2-Läufe → genauer

**Beispiel für Ungenauigkeit ohne HR:**
- Athlet A: Trainiert mit 6:00/km (Easy)
- Athlet B: Trainiert mit 6:00/km (Tempo - zu hart!)

Beide haben gleichen Training-Pace, aber Athlet B ist schneller im Rennen! HR erkennt den Unterschied.

**Wissenschaftliche Quellen:**
- **McMillan Running Calculator**: Industry-Standard seit 20+ Jahren
- **Jack Daniels VDOT**: VO2max-basierte Predictions (ähnliche Methode)
- **Heart Rate Zones**: Karvonen Formula, 60-75% = Zone 2

**Verbesserung der Genauigkeit:**

1. **Mehr Easy Runs**: Je mehr Daten, desto genauer
2. **Konsistentes Training**: Schwankende Fitness → schwankende Predictions
3. **Echter Race als Referenz**: Nach einem Wettkampf wird die Schätzung präziser (zukünftige Feature-Möglichkeit)

### Smoothing (Glättung)

**Was es ist:** Mathematische Glättung der Daten zur besseren Trenddarstellung.

**Methode:** Simple Moving Average (SMA)

**Optionen:**
- **Off**: Rohdaten ohne Glättung
- **Light**: 3-Perioden-Fenster
- **Medium**: 5-Perioden-Fenster
- **Strong**: 7-Perioden-Fenster

**Wann verwenden:**
- Bei vielen Schwankungen in den Daten
- Um langfristige Trends zu erkennen
- Wenn einzelne Ausreißer stören

---

## Charts und Visualisierungen

### Overview Tab

#### Distance Chart
**Zeigt:** Gesamtdistanz pro Periode

**Features:**
- Rohdaten und optional geglättete Linie
- **Interaktive Legende:**
  - Klicke auf Legendeneinträge, um Serien ein-/auszublenden
  - **Total Distance**: Hauptmetrik
  - **Moving Time**: Bewegungszeit (initial ausgeblendet)
  - **Run Count**: Laufanzahl (initial ausgeblendet)

**Nutzen der zusätzlichen Serien:**
Du kannst erkennen, ob eine Distanzsteigerung kam durch:
- Mehr Läufe (Run Count steigt)
- Längere Läufe (Run Count konstant, aber Distance steigt)
- Beides

**Beispiel:**
- Distance steigt von 20 km → 30 km
- Run Count steigt von 2 → 3: **Mehr Läufe**
- Run Count bleibt bei 2: **Längere Läufe**

**Tipp:** Klicke in der Legende auf "Moving Time" oder "Run Count" um diese Serien einzublenden.

#### Pace/Speed Chart
**Zeigt:** Pace (min/km) oder Speed (km/h) pro Periode

**Umschaltung:** Toolbar → Metric: "Pace" oder "Speed"

**Interpretation:**
- **Pace sinkt** = Geschwindigkeit wird besser
- **Speed steigt** = Geschwindigkeit wird besser

#### Frequency Chart
**Zeigt:** Anzahl der Läufe pro Periode

**Interpretation:**
- Zeigt Trainingskonsistenz
- Höhere Werte = regelmäßigeres Training
- Kombiniere mit Distance Chart für Gesamtbild

### Heart Rate Tab

Der Heart Rate Tab visualisiert deine Herzfrequenz-Daten und aerobe Fitness-Entwicklung. **Wichtig:** Dieser Tab zeigt nur Daten von Läufen, bei denen ein Herzfrequenz-Monitor verwendet wurde.

**Hinweis bei fehlenden HR-Daten:** Falls keine HR-Daten verfügbar sind, erscheint die Meldung "No HR data available" im Chart. Dies passiert wenn:
- Du noch keinen Herzfrequenz-Monitor verwendet hast
- Der gewählte Zeitraum (Start Date) keine HR-Läufe enthält
- Strava keine HR-Daten für deine Aktivitäten hat

#### Heart Rate Range (Area Chart)
**Zeigt:** Min-Max Herzfrequenz-Bereich pro Periode als blaue Fläche

**Visualisierung:**
- **Blaue Fläche**: Zeigt den Bereich von niedrigster durchschnittlicher HR bis höchster maximaler HR in der Periode
- **Untere Grenze**: Niedrigste Durchschnitts-HR eines einzelnen Laufs (z.B. Recovery Run)
- **Obere Grenze**: Höchste maximale HR über alle Läufe (z.B. Tempo Run oder Wettkampf)

**Interpretation:**
- **Breite Fläche**: Verschiedene Trainingsintensitäten (gut für ausgewogenes Training!)
- **Schmale Fläche**: Ähnliche Intensitäten bei allen Läufen
- **Fläche steigt**: Höhere Intensitäten im Training
- **Fläche sinkt**: Niedrigere Intensitäten (z.B. nach intensiver Phase, Regenerationswoche)

**Beispiel:**
Woche mit 4 Läufen:
- Recovery: Avg 135 bpm, Max 145 bpm
- Easy: Avg 145 bpm, Max 155 bpm
- Tempo: Avg 165 bpm, Max 175 bpm
- Long: Avg 150 bpm, Max 170 bpm

→ **Fläche von 135 bpm (untere Grenze) bis 175 bpm (obere Grenze)**

**Nutzen:**
- Erkenne, ob du verschiedene Trainingszonen nutzt
- Sieh, ob du zu monoton trainierst (schmale Fläche)
- Identifiziere Wochen mit hoher Intensität (hohe obere Grenze)

#### Average Heart Rate Line
**Zeigt:** Durchschnittliche Herzfrequenz pro Periode als rote Linie

**Berechnung:** Mittelwert aller Durchschnitts-HR-Werte der Läufe mit HR-Daten in der Periode

**Interpretation:**
- **Konstante Linie**: Gleichbleibende durchschnittliche Intensität
- **Sinkende Linie bei gleichem Pace**: Bessere aerobe Fitness!
- **Steigende Linie**: Höhere Trainingsintensität oder mögliche Ermüdung

**Wichtig:** Eine sinkende Average HR allein bedeutet NICHT automatisch bessere Fitness. Du musst dies in Kombination mit deinem Pace/Speed betrachten!

**Beispiel - Fitness-Verbesserung:**
- Monat 1: Avg HR 155 bpm bei 6:00 min/km
- Monat 3: Avg HR 150 bpm bei 5:45 min/km
→ **HR sinkt UND Pace verbessert sich = echte Fitness-Verbesserung!**

**Beispiel - Kein Fitness-Fortschritt:**
- Monat 1: Avg HR 155 bpm bei 6:00 min/km
- Monat 3: Avg HR 150 bpm bei 6:30 min/km
→ HR sinkt, aber Pace ist langsamer = wahrscheinlich nur langsameres Training

**Genau deshalb gibt es den Efficiency Factor!**

#### Efficiency Factor (EF) Line
**Zeigt:** Pace-normalisierte Herzfrequenz als grüne Linie - DIE Schlüssel-Metrik für aerobe Fitness

**Was es ist:**
Der Efficiency Factor (EF) ist das Verhältnis von Geschwindigkeit zu Herzfrequenz. Er zeigt, wie effizient dein Herz-Kreislauf-System arbeitet.

**Formel:**
```
EF = Geschwindigkeit (m/s) / Durchschnittliche Herzfrequenz (bpm)
```

**Display:** Multipliziert mit 1000 für bessere Lesbarkeit (z.B. 0.0179 → 17.9)

**Warum ist EF besser als rohe HR?**

Die rohe Herzfrequenz allein ist irreführend:
- Tempo Run mit 165 bpm: Ist das gut oder schlecht?
- Easy Run mit 140 bpm: Ist das effizienter?

**→ Ohne den Pace zu kennen, ist HR wertlos!**

Der EF normalisiert die HR für unterschiedliche Geschwindigkeiten und macht sie vergleichbar.

**Interpretation:**
- **Höherer EF = bessere aerobe Fitness**
- **Steigender EF über Monate** = Fitness verbessert sich
- **Konstanter EF trotz höherem Volumen** = gute Erholung und Anpassung
- **Fallender EF** = mögliches Übertraining, Ermüdung, oder Krankheit

**Beispiel - EF zeigt echten Fortschritt:**

**Monat 1:**
- Pace: 6:00 min/km = 2.78 m/s
- Avg HR: 155 bpm
- **EF = 2.78 / 155 = 0.0179 (angezeigt: 17.9)**

**Monat 3:**
- Pace: 5:30 min/km = 3.03 m/s
- Avg HR: 150 bpm
- **EF = 3.03 / 150 = 0.0202 (angezeigt: 20.2)**

**→ EF stieg von 17.9 auf 20.2 = deutliche Fitness-Verbesserung!**

Du läufst schneller bei niedrigerer Herzfrequenz - das ist echte aerobe Entwicklung!

**Langfristige EF-Entwicklung:**

**Anfänger-Phase (Monate 1-3):**
- EF steigt schnell (z.B. 15 → 18)
- Große aerobe Anpassungen

**Fortgeschrittenen-Phase (Monate 4-12):**
- EF steigt langsamer (z.B. 18 → 20)
- Feintuning der aeroben Kapazität

**Elite-Phase:**
- EF stabilisiert sich auf hohem Niveau (z.B. 22-25)
- Kleine Schwankungen durch Training Load

**Praktische Nutzung:**

1. **Fitness-Check**: Vergleiche EF alle 4-6 Wochen
2. **Trainingsanpassung**: Fallender EF → mehr Erholung einplanen
3. **Wettkampf-Readiness**: Steigender/stabiler EF → gute Form
4. **Übertraining-Warnung**: Konstant fallender EF über Wochen → Pause!

**Interaktive Legende:**
Klicke auf Legendeneinträge um Serien ein-/auszublenden:
- **HR Range (Min-Max)**: Blaue Fläche
- **Average HR**: Rote Linie
- **Efficiency Factor (×1000)**: Grüne Linie

**Smoothing:**
Der Smoothing-Filter aus der Toolbar wird auf Average HR und EF angewendet. Nutze Smoothing (Light/Medium/Strong) um Trends bei schwankenden Daten besser zu erkennen.

**Dual Y-Achsen:**
- **Linke Y-Achse**: Herzfrequenz in bpm (für HR Range und Average HR)
- **Rechte Y-Achse**: Efficiency Factor ×1000 (für EF Line)

**Tipp für Marathon-Training:**
Verfolge deinen EF während der Aufbauphase. Ein steigender oder stabiler EF zeigt, dass dein Körper gut mit dem erhöhten Trainingsvolumen umgeht. Ein fallender EF kann ein Warnsignal für Übertraining sein - baue dann mehr Erholungswochen ein!

### Endurance Tab

#### Longest Run Chart
**Zeigt:** Längster Einzellauf pro Periode

**Warum wichtig:**
- **Kermetrik für Marathon-Vorbereitung**
- Zeigt Langstreckenausdauer
- Kann nicht aus Gesamtdistanz abgeleitet werden

**Beispiel-Nutzung:**
Verfolge deinen Long Run Fortschritt:
- Woche 1: 15 km
- Woche 4: 18 km
- Woche 8: 21 km (Halbmarathon-Distanz erreicht!)
- Woche 12: 25 km
- Woche 16: 30 km (Marathon-Vorbereitung auf Kurs)

#### Avg Distance/Run Chart
**Zeigt:** Durchschnittliche Distanz pro Lauf

**Interpretation:**
- Zeigt typische Laufstruktur
- **Nicht immer "höher ist besser"**
- Kann sinken, wenn du mehr kürzere Regenerationsläufe machst
- Kombiniere mit Total Distance für vollständiges Bild

**Beispiel-Szenarien:**

**Szenario 1: Volumenaufbau durch Frequenz**
- Avg Distance sinkt: 10 km → 7 km
- Total Distance steigt: 20 km → 28 km
- Run Count steigt: 2 → 4
- **Interpretation**: Mehr Läufe, stabile Struktur

**Szenario 2: Spezialisierung auf Long Runs**
- Avg Distance konstant: 10 km
- Total Distance konstant: 30 km
- Longest Run steigt: 12 km → 20 km
- **Interpretation**: Fokus auf wöchentlichen Long Run

### Score Tab

#### Training Score Chart
**Zeigt:** Kombinierter Trainingsfortschritt (0-100)

**Komponenten (mit HR-Daten):**
- 30% Distanz
- 30% Pace
- 20% Efficiency Factor (aerobe Fitness)
- 20% Frequenz

**Komponenten (ohne HR-Daten):**
- 37.5% Distanz
- 37.5% Pace
- 25% Frequenz

**Adaptive Gewichtung:**
Der Score passt sich automatisch an verfügbare Daten an:
- **Mit HR-Daten**: Efficiency Factor fließt mit 20% ein
- **Ohne HR-Daten**: Die Gewichte werden proportional angepasst

Dies ermöglicht konsistente Score-Berechnung auch bei gemischten Daten (manche Perioden mit HR, manche ohne).

**Interpretation:**
- 0-30: Unter Baseline-Niveau
- 30-60: Im Baseline-Bereich
- 60-80: Über Baseline, guter Fortschritt
- 80-100: Deutlich über Baseline, exzellenter Fortschritt

**Was der Score misst:**
- **Volumen**: Gesamtdistanz im Vergleich zu deinem Durchschnitt
- **Qualität**: Pace-Verbesserung im Vergleich zu deinem Durchschnitt
- **Effizienz**: Aerobe Fitness (wenn HR-Daten verfügbar)
- **Konsistenz**: Regelmäßigkeit des Trainings

**Wichtige Hinweise:**
- Der Score ist eine Zusammenfassung. Er ersetzt NICHT die strukturellen Details!
- Für Marathon-Vorbereitung schaue auch auf Longest Run im Endurance Tab
- Der Score reagiert auf langfristige Trends, nicht auf einzelne Workouts
- Baseline wird als rollierender Durchschnitt berechnet (anpassungsfähig)

**Beispiel - Score-Entwicklung:**
- **Woche 1**: Score 45 (Baseline-Niveau)
- **Woche 4**: Score 62 (Volumen gestiegen, Pace verbessert)
- **Woche 8**: Score 75 (Efficiency Factor gestiegen, konstantes Volumen)
- **Woche 12**: Score 58 (Erholungswoche, niedriger Score ist OK!)

Ein sinkender Score ist nicht immer schlecht - Erholungswochen sind wichtig!

### Projection Tab

#### Einstellungen

**Projection Mode:**
- **Volume (Total Distance)**: Projiziert die wöchentliche/monatliche Gesamtdistanz
- **Long Run**: Projiziert den längsten Lauf pro Periode

**Periods Ahead:**
- Wähle, wie weit in die Zukunft projiziert werden soll
- **Wochen-Modus**: 1-104 Wochen (2 Jahre)
- **Monats-Modus**: 1-24 Monate (2 Jahre)
- Standard: 12 Perioden

**Hinweis:** Die Einstellungen werden automatisch gespeichert und beim nächsten Start wiederhergestellt.

#### Projection Modes

**Volume Projection Mode:**
- Projiziert die wöchentliche/monatliche Gesamtdistanz
- Zeigt Milestones:
  - 5K gesamt
  - 10K gesamt
  - Half Marathon (21.1 km) gesamt
  - Marathon (42.195 km) gesamt

**Frage beantwortet:** "Wann erreicht mein wöchentliches Volumen 42 km?"

**Long Run Projection Mode:**
- Projiziert den längsten Lauf pro Periode
- Zeigt Endurance-Milestones:
  - 10K Long Run
  - 15K Long Run
  - Half Marathon (21.1 km) Long Run
  - 30K Long Run
  - **Marathon Ready (32 km) Long Run** - Standard für Marathon-Vorbereitung

**Frage beantwortet:** "Wann bin ich Marathon-Ready?" (32 km Long Run schaffbar)

**Wichtiger Unterschied:**
Diese beiden Fragen sind NICHT gleich für Marathon-Vorbereitung!

- Wöchentliches Volumen von 42 km bedeutet NICHT, dass du 42 km am Stück laufen kannst
- Ein 32 km Long Run zeigt Marathon-Readiness (Standard in professionellen Trainingsplänen)
- Die vollen 42 km schafft man am Renntag durch Wettkampfenergie

**Beispiel:**
- Athlet A: 50 km/Woche mit 5 × 10 km Läufen, längster: 10 km
- Athlet B: 40 km/Woche mit 1 × 30 km + 2 × 5 km, längster: 30 km

Athlet B ist näher am Marathon-Ziel (braucht nur noch 2 km bis 32 km = Marathon Ready), obwohl weniger Wochenvolumen!

#### Projektion verstehen

**Methode:** Lineare Regression auf Basis der letzten 12 Perioden

**Interpretation:**
- **Durchgehende Linie**: Historische Daten
- **Gestrichelte Linie**: Projektion in die Zukunft
- **Orangene Punkte**: Geschätzte Meilenstein-Zeitpunkte
- **X-Achse**: Zeigt tatsächliche Kalenderdaten (z.B. "Jan 2024", "Feb 2024")
- **Interaktive Legende**: Klicke auf Legendeneinträge zum Ein-/Ausblenden

**Chart-Bedienung:**
- Verwende die **Periods Ahead** Einstellung um weiter/weniger weit in die Zukunft zu schauen
- Wechsle zwischen **Volume** und **Long Run** Mode für unterschiedliche Perspektiven
- Die Meilenstein-Punkte zeigen dir, WANN du voraussichtlich ein bestimmtes Ziel erreichst

**Wichtig:** Projektionen sind Schätzungen basierend auf bisherigem Fortschritt. Tatsächliche Ergebnisse können variieren durch:
- Trainingspausen
- Verletzungen
- Änderungen im Trainingsplan
- Saisonale Schwankungen

---

## Einstellungen

### Settings Dialog

Der Settings Dialog enthält alle wichtigen Konfigurationen und Aktionen:

**Strava API Configuration:**
1. Gehe zu https://www.strava.com/settings/api
2. Erstelle eine neue API Application (falls noch nicht vorhanden)
3. Kopiere **Client ID** und **Client Secret**
4. Trage sie im Settings Dialog ein
5. Klicke **Save**

**Strava Actions:**
- **Connect to Strava**: Verbindung zu Strava herstellen (öffnet Browser für OAuth)
  - Nach erfolgreicher Verbindung wirst du gefragt, ob sofort synchronisiert werden soll
- **Disconnect from Strava**: Verbindung trennen
- **Sync Activities**: Aktivitäten von Strava herunterladen
- **Status**: Zeigt aktuellen Verbindungsstatus (Grün = verbunden, Grau = nicht verbunden)

**Heart Rate Configuration:**
- **Max Heart Rate**: Optionale manuelle HRmax-Einstellung
  - **Auto-detect** (Standard): Die App erkennt deine HRmax automatisch aus deinen Aktivitäten
    - Wendet automatisch einen 10% Safety Margin an (da die meisten Läufer ihre echte HRmax nie im Training erreichen)
  - **Manuell setzen**: Wenn du deine echte HRmax kennst, kannst du sie hier eingeben (100-220 bpm)
    - Verbessert die Genauigkeit der Race Time Predictions
    - Nutze die Warnung im Summary Panel als Hinweis, falls die Auto-Detection unplausibel ist
    - **Nach dem Speichern**: Das Summary Panel wird automatisch aktualisiert mit neuen Race Predictions
    - Du erhältst eine Bestätigung wie "Manual HRmax set to 190 bpm. Race predictions will be updated."
  - **Wann manual einstellen?**
    - Du hast einen HRmax-Test gemacht (z.B. beim Sportarzt)
    - Das Summary Panel zeigt eine orangene Warnung mit Vorschlag
    - Deine Race Time Predictions erscheinen unrealistisch
  - **Kontextabhängige Meldungen**: Die App erkennt automatisch, was du geändert hast:
    - Nur HRmax geändert → Hinweis zu Race Predictions
    - Nur Strava Credentials geändert → Hinweis zum Verbinden
    - Beides geändert → Kombinierte Meldung

**Automatische Synchronisation:**
- **Beim Start**: Die App prüft automatisch beim Start, ob neue Aktivitäten vorliegen (silent sync)
- **Nach Connect**: Du wirst nach erfolgreicher OAuth-Verbindung gefragt, ob du synchronisieren möchtest
- **Token-Refresh**: Access Tokens werden automatisch erneuert (alle ~6 Stunden) - keine manuelle Aktion nötig

### Datenmanagement

- **Start Date** (Toolbar): Filtert, ab wann Daten in Charts angezeigt werden
  - Beim ersten Sync: Bestimmt, ab wann Aktivitäten importiert werden (Standard: 1. Januar 2000)
  - Nach dem ersten Sync: Filtert nur die Anzeige, Daten bleiben in der Datenbank
- **Period** (Toolbar): Week = ISO-Wochenkalender (Montag-Sonntag), Month = Kalendermonat
- **Sync**: Inkrementelle Synchronisation (nur neue/geänderte Aktivitäten)

### Gespeicherte Einstellungen

Die Anwendung speichert automatisch:
- Start Date
- Period (Week/Month)
- Metric (Pace/Speed)
- Smoothing Level
- Projection Mode
- Projection Periods Ahead

Beim nächsten Start werden diese Einstellungen wiederhergestellt.

### Tipps

- **Erste Synchronisation**: Standard (seit 2000) importiert garantiert alle Strava-Aktivitäten
- **Start-Datum als Filter**: Nach dem Import kannst du das Start-Datum nutzen, um z.B. nur die aktuelle Trainingsphase anzuzeigen
- **Regelmäßig synchronisieren**: Sync nach neuen Läufen für aktuelle Daten (oder nutze die automatische Sync beim App-Start)
- **Smoothing anpassen**: Bei vielen Schwankungen stärkeres Smoothing verwenden

---

## Häufige Fragen

### Warum werden meine Laufband-Läufe nicht angezeigt?

Laufband-Läufe (VirtualRun) werden bewusst ausgeschlossen, da die Anwendung auf Outdoor-Training fokussiert ist.

### Wie wird der gewichtete Pace berechnet?

Gewichteter Pace = Gesamt-Bewegungszeit / Gesamt-Distanz

Dies gibt einen genaueren Durchschnitt, da längere Läufe stärker gewichtet werden.

### Was ist der Unterschied zwischen Total Distance und Longest Run?

- **Total Distance**: Summe aller Läufe (Volumen)
- **Longest Run**: Längster Einzellauf (Ausdauerfähigkeit)

Beides sind wichtige, aber unterschiedliche Metriken. Für Marathon-Vorbereitung ist Longest Run besonders wichtig.

### Warum sinkt meine Average Distance per Run, obwohl ich mehr trainiere?

Das ist normal! Wenn du häufiger läufst, aber kürzere Einheiten einbaust (z.B. Recovery Runs), sinkt der Durchschnitt. Wichtig ist die Gesamtdistanz UND die strukturelle Balance.

### Wie nutze ich die interaktive Legende in den Charts?

Alle Charts haben eine interaktive Legende am unteren Rand. Klicke auf einen Legendeneintrag um die entsprechende Serie ein-/auszublenden.

**Beispiel Distance Chart:**
Klicke auf "Run Count" in der Legende um zu sehen:
- Distance steigt + Run Count steigt = Mehr Läufe
- Distance steigt + Run Count konstant = Längere Läufe
- Distance konstant + Run Count steigt = Mehr kurze Läufe

**Tipp:** Deaktivierte Serien werden grau dargestellt. Klicke erneut um sie wieder zu aktivieren.

### Sind die Projektionen zuverlässig?

Projektionen sind Schätzungen basierend auf linearer Regression deiner bisherigen Daten. Sie sind hilfreich für Trendanalyse, aber nicht exakt. Reale Ergebnisse können durch viele Faktoren variieren.

### Muss ich manuell synchronisieren oder passiert das automatisch?

Die App synchronisiert teilweise automatisch:

**Automatisch:**
- Beim App-Start wird eine stille Hintergrund-Synchronisation durchgeführt (falls bereits Daten vorhanden)
- Status-Nachrichten erscheinen nur bei neuen Aktivitäten oder Fehlern
- Access Tokens werden automatisch erneuert ohne Benutzerinteraktion

**Manuell:**
- Nach dem ersten "Connect to Strava" wirst du gefragt ob du synchronisieren möchtest
- Du kannst jederzeit manuell "Sync Activities" in den Settings klicken für sofortige Synchronisation mit Fortschritts-Dialog

**Tipp:** Für regelmäßige Updates einfach die App täglich/wöchentlich starten - die automatische Sync im Hintergrund hält deine Daten aktuell!

### Warum zeigt der Heart Rate Tab "No HR data available"?

Der Heart Rate Tab zeigt nur Daten von Läufen, bei denen ein Herzfrequenz-Monitor verwendet wurde. "No HR data available" erscheint wenn:

1. **Du noch keinen HR-Monitor verwendet hast**: Läufe ohne HR-Messgerät haben keine Herzfrequenz-Daten
2. **Zeitraum-Filter**: Das gewählte Start Date filtert alle HR-Läufe heraus
3. **Strava hat keine HR-Daten**: Ältere Läufe oder manuell eingetragene Aktivitäten

**Lösung:**
- Nutze einen Herzfrequenz-Monitor (Brustgurt oder optischer Sensor an der Uhr)
- Passe das Start Date in der Toolbar an, um Läufe mit HR-Daten einzubeziehen
- Synchronisiere neuere Läufe mit HR-Monitor

### Was ist der Efficiency Factor und warum ist er wichtig?

Der Efficiency Factor (EF) ist das Verhältnis von Geschwindigkeit zu Herzfrequenz:

```
EF = Geschwindigkeit (m/s) / Durchschnittliche Herzfrequenz (bpm)
```

**Warum wichtig:**
- Die rohe Herzfrequenz allein ist irreführend (schneller Pace = natürlich höhere HR)
- EF normalisiert HR für unterschiedliche Geschwindigkeiten
- **Höherer EF = bessere aerobe Fitness**
- Ermöglicht fairen Vergleich zwischen verschiedenen Läufen

**Beispiel:**
- Vor 3 Monaten: 6:00 min/km bei 155 bpm → EF = 17.9
- Heute: 5:30 min/km bei 150 bpm → EF = 20.2
- **→ EF ist gestiegen = echte Fitness-Verbesserung!**

Du läufst schneller bei niedrigerer Herzfrequenz - das ist aerobe Entwicklung!

### Wie interpretiere ich die HR Range (blaue Fläche)?

Die blaue Fläche im Heart Rate Chart zeigt den Bereich zwischen:
- **Untere Grenze**: Niedrigste Durchschnitts-HR eines Laufs (z.B. Recovery Run mit 135 bpm)
- **Obere Grenze**: Höchste maximale HR über alle Läufe (z.B. Tempo Run Peak bei 175 bpm)

**Interpretation:**
- **Breite Fläche**: Verschiedene Trainingsintensitäten → gut für ausgewogenes Training!
- **Schmale Fläche**: Alle Läufe ähnliche Intensität → eventuell zu monoton
- **Fläche steigt**: Training wird intensiver
- **Fläche sinkt**: Mehr Easy Runs / Regeneration

### Warum sinkt mein Efficiency Factor?

Ein sinkender EF über mehrere Wochen kann verschiedene Ursachen haben:

1. **Übertraining**: Zu viel Belastung, zu wenig Erholung
2. **Krankheit**: Beginnende Erkältung oder Infektion
3. **Hitze/Wetter**: Hohe Temperaturen erhöhen HR bei gleichem Pace
4. **Ermüdung**: Akkumulierte Müdigkeit aus intensiven Training
5. **Stress**: Beruflicher/privater Stress beeinflusst HR

**Was tun:**
- **Kurzfristige Schwankung** (1-2 Wochen): Wahrscheinlich normal (Wetter, Stress)
- **Konstant fallend** (3+ Wochen): Erholungswoche einlegen!
- Vergleiche mit Training Score und Gefühl beim Laufen
- Mehr Easy Runs einbauen

**Tipp:** Nutze den EF als Frühwarnsystem für Übertraining!

### Kann ich Läufe ohne HR-Monitor nachträglich mit HR-Daten versehen?

Nein, Herzfrequenz-Daten müssen während des Laufs mit einem HR-Monitor aufgezeichnet werden. Eine nachträgliche Ergänzung ist technisch nicht möglich.

**Empfehlung:**
- Investiere in einen Herzfrequenz-Monitor (Brustgurt oder optischer Sensor)
- Viele moderne Sportuhren haben eingebaute optische HR-Sensoren
- Brustgurte sind meist genauer als optische Sensoren
- Strava übernimmt HR-Daten automatisch von kompatiblen Geräten

### Ist ein steigender Efficiency Factor immer gut?

**Meistens ja**, aber mit Nuancen:

**Gut (echte Fitness-Verbesserung):**
- EF steigt bei gleichbleibendem oder steigendem Volumen
- Du fühlst dich gut beim Training
- Training Score ist stabil oder steigend

**Vorsicht (mögliche Probleme):**
- EF steigt, aber nur weil du langsamer läufst (niedrigere HR bei langsamem Pace)
- Vergleiche immer mit Pace/Speed Chart!
- EF steigt plötzlich stark → könnte Messungenauigkeit sein

**Tipp:** Schaue immer auf die Kombination aus EF UND Pace. Idealer Fortschritt:
- Pace wird schneller ✓
- HR bleibt gleich oder sinkt ✓
- → EF steigt = echte Fitness-Verbesserung! ✓

### Fließt der Efficiency Factor in den Training Score ein?

**Ja!** Seit der neuesten Version berücksichtigt der Training Score den Efficiency Factor.

**Mit HR-Daten:**
- 30% Distanz
- 30% Pace
- 20% Efficiency Factor
- 20% Frequenz

**Ohne HR-Daten:**
Die Gewichte passen sich automatisch an:
- 37.5% Distanz
- 37.5% Pace
- 25% Frequenz

**Warum diese Gewichtung?**
- **Distanz & Pace gleich wichtig** (je 30%): Volumen und Qualität sind gleichwertig
- **Efficiency Factor** (20%): Aerobe Fitness als wichtiger Indikator
- **Frequency** (20%): Konsistenz ist wichtig, aber weniger als Leistung

**Vorteile:**
- Der Score reflektiert jetzt echte Fitness-Verbesserung (nicht nur Volume)
- EF-Verbesserung führt zu höherem Score
- Warnung bei Übertraining: Fallender EF = niedrigerer Score
- Funktioniert auch mit gemischten Daten (manche Läufe mit HR, manche ohne)

### Warum ist mein Training Score gesunken, obwohl ich mehr laufe?

Das kann mehrere Gründe haben:

**1. Pace hat sich verschlechtert**
- Mehr Volumen, aber langsameres Tempo
- Pace hat 30% Gewichtung im Score

**2. Efficiency Factor ist gefallen** (wenn HR-Daten vorhanden)
- Höhere HR bei gleichem oder langsamerem Pace
- Mögliches Übertraining
- EF hat 20% Gewichtung

**3. Erholungswoche**
- Bewusst weniger Distanz/Intensität
- Niedriger Score ist hier GEWOLLT und gut!

**4. Rolling Baseline hat sich angepasst**
- Der Score vergleicht mit deinem rollierenden Durchschnitt
- Wenn dein Durchschnitt steigt, muss aktuelles Training noch höher sein für gleichen Score

**Beispiel:**
- **Vor 2 Monaten**: 20 km/Woche = Score 60
- **Jetzt**: 25 km/Woche = Score 55

→ Dein Baseline ist jetzt ~23 km/Woche (wegen konstantem Anstieg)
→ 25 km ist nur leicht über dem neuen Baseline
→ Gleichzeitig ist Pace langsamer geworden (-10%)
→ **Ergebnis**: Score sinkt trotz höherem Volumen

### Was bedeutet "Marathon Milestone: Keep training!" im Summary Panel?

Das bedeutet, dass die aktuelle Projektion NICHT zeigt, dass du 32 km Long Run (Marathon-Ready) in absehbarer Zeit erreichen wirst.

**Mögliche Gründe:**

**1. Zu wenig Daten**
- Weniger als 3-4 Perioden mit Long Runs
- Projektion kann noch nicht berechnet werden

**2. Negativer Trend**
- Deine Longest Runs werden kürzer
- Beispiel: 18 km → 15 km → 12 km
- Projektion zeigt abwärts

**3. Sehr flacher oder stagnierrender Trend**
- Longest Run bleibt konstant (z.B. immer ~10 km)
- Kein Wachstum sichtbar

**4. Lange Zeitspanne bis zum Ziel**
- Projektion würde >2 Jahre dauern
- App zeigt "Keep training!" statt unrealistischem Datum

**Was tun?**

**Für Marathon-Vorbereitung:**
1. Erhöhe deinen Long Run schrittweise (z.B. +10% pro Woche)
2. Schaue im **Projection Tab** → **Long Run Mode**
3. Setze dir Zwischenziele: 15K, Half Marathon (21.1 km), 30K
4. Nutze den **Endurance Tab** → **Longest Run Chart** um Progression zu tracken

**Beispiel:**
```
Aktuell: Longest Run ~12 km
Ziel: 32 km Long Run (Marathon Ready)

Realistische Progression:
- Woche 1-4: 12 km → 15 km (+0.75 km/Woche)
- Woche 5-8: 15 km → 18 km
- Woche 9-12: 18 km → 21 km (Half Marathon!)
- Woche 13-20: 21 km → 28 km
- Woche 21-24: 28 km → 32 km (Marathon Ready!)

Nach ~12 Wochen mit konstantem Trend zeigt die Milestone ein Datum an!
```

**Wichtig:** Dies ist NORMAL! Marathon-Vorbereitung dauert Monate. Fokussiere dich auf konsistente Long Run Steigerungen.

**Was tun?**
- Checke den Pace Chart: Ist dein Tempo langsamer geworden?
- Checke den EF Chart (falls HR-Daten): Ist deine aerobe Effizienz gesunken?
- Analysiere ob du zu viel Volumen zu schnell aufgebaut hast (Übertraining)
- Plane ggf. eine Erholungswoche ein

### Wie genau sind die Race Time Predictions?

Die Predictions sind **Schätzungen** basierend auf wissenschaftlich fundierter Methodik (McMillan Calculator), aber individuelle Ergebnisse variieren.

**Typische Genauigkeit:**

- **Gut trainierte Athleten**: ±2-5% Abweichung
- **Anfänger/wenig Wettkampf-Erfahrung**: ±5-10% Abweichung
- **Extreme Bedingungen** (Hitze, Hügel): Höhere Abweichung

**Beispiel:**
- Prediction: Marathon 3:50:00
- Mögliche Range: 3:40-4:05 (±7%)

**Faktoren für bessere Genauigkeit:**

✅ **Hilft:**
- Viele Easy Runs (10+) in letzten 6 Monaten
- Konsistente HR-Daten
- Ähnliche Trainingsbedingungen zum Wettkampf
- Erfahrung im Pace-Management

❌ **Reduziert Genauigkeit:**
- Wenige Easy Runs (<5)
- Schwankende Fitness
- Erster Wettkampf auf der Distanz
- Sehr hügelige/heiße Bedingungen

**Vergleich mit anderen Methoden:**

| Methode | Genauigkeit | Voraussetzung |
|---------|-------------|---------------|
| **McMillan (HR-basiert)** | Gut | HR-Daten, Easy Runs |
| Riegel's Formula | Sehr gut | Echte Race-Zeit als Referenz |
| VDOT (Jack Daniels) | Sehr gut | VO2max Test oder Race-Zeit |
| Nur Training-Pace | Schlecht | Vermischt Intensitäten |

**Warum Abweichungen normal sind:**

1. **Wettkampf-Psychologie**: Rennen laufen sich oft schneller als Training
2. **Taper-Effekt**: Ausgeruhte Beine sind 2-3% schneller
3. **Adrenalin**: Kann 1-2% Performance-Boost geben
4. **Kurs & Wetter**: -10% bei Hitze, +5% bei Hügeln möglich

**Empfehlung:**

Nutze die Predictions als **Ausgangspunkt** für Race-Pace-Planung:
- **Konservativ**: Starte 5% langsamer als Prediction
- **Erfahren**: Starte bei Prediction-Pace
- **Aggressiv**: Starte 2-3% schneller (Risiko!)

**Praxis-Tipp:**

Nach deinem ersten Rennen: Vergleiche Prediction vs. Actual Time!
- Schneller als erwartet → Dein Easy Pace ist sehr konservativ
- Langsamer als erwartet → Prüfe Tapering, Wettkampf-Strategie

Die App lernt nicht automatisch, aber du kannst die Erkenntnisse für zukünftige Rennen nutzen.

### Warum zeigt das Summary Panel eine orangene HRmax-Warnung?

Die App führt eine **Plausibilitätsprüfung** deiner automatisch erkannten HRmax durch. Eine Warnung erscheint, wenn:

**1. Erkannte HRmax zu niedrig (<150 bpm)**
- Für Läufer ist eine HRmax unter 150 bpm extrem ungewöhnlich
- Selbst 60-jährige haben typischerweise HRmax ~160-170 bpm

**2. Durchschnitts-HR durchgehend zu hoch (>85% der erkannten HRmax)**
- Wenn >50% deiner Läufe über 85% der erkannten HRmax liegen
- Deutet darauf hin, dass deine echte HRmax höher ist

**Beispiel:**
```
Erkannte HRmax: 169 bpm
Deine typischen Easy Runs: 135-148 bpm (80-88% von 169)
→ Das ist zu hoch für "Easy Runs"!

Vorschlag: HRmax ~190 bpm setzen
→ Easy Runs wären dann 114-143 bpm (60-75% von 190) ✅
```

**Was tun?**

1. **Prüfe die Warnung**: Das Summary Panel zeigt einen Vorschlagswert
2. **Gehe zu Settings**: Öffne den Settings Dialog
3. **Setze manuelle HRmax**: Trage den vorgeschlagenen Wert ein (oder deinen bekannten Wert)
4. **Speichern**: Klicke Save

**Woher weiß ich meine echte HRmax?**

- **HRmax-Test beim Sportarzt** (genaueste Methode)
- **Selbst-Test**: All-out 5min Berglauf (max HR in letzter Minute)
- **Formel (ungenau)**: 220 - Alter (nur grobe Schätzung, ±10-15 bpm Varianz!)
- **Strava-Daten**: Höchster jemals gemessener Wert bei einem sehr harten Intervall/Rennen

**Wichtig:**
- Die meisten Läufer erreichen ihre echte HRmax NIE im normalen Training
- Deshalb wendet die Auto-Detection einen 10% Safety Margin an
- Manual-Eingabe umgeht diesen Margin (nutzt exakten Wert)

---

## Über diese Software

**Running Progress Tracker** (Run Trend)
Version 0.1.0

**Entwickler:** Arne Weiß
**Kontakt:** run-trend@arne-weiss.de

### Lizenz

Diese Software ist lizenziert unter **MIT License mit Commons Clause**.

**Was bedeutet das?**

✅ **Erlaubt:**
- Private Nutzung
- Nicht-kommerzielle Nutzung
- Code anschauen, modifizieren und teilen
- Beiträge und Weiterentwicklungen

❌ **Nicht erlaubt:**
- Kommerzielle Vermarktung der Software
- Verkauf der Software oder abgeleiteter Versionen

Die vollständige Lizenz findest du in der LICENSE-Datei im Projekt-Repository.

### Datenschutz

- Alle Daten werden lokal auf deinem Computer gespeichert
- Keine externe Übertragung außer zur Strava API (nach deiner Autorisierung)
- Keine Telemetrie oder Analytics
- Du kannst die Verbindung zu Strava jederzeit widerrufen

### Open Source

Der Quellcode ist öffentlich verfügbar. Informationen zum Repository findest du im About-Dialog (Toolbar → About).

---

## Weitere Hilfe

Bei Fragen oder Problemen:
- Prüfe die Strava API Credentials in Settings
- Stelle sicher, dass die Strava-Verbindung aktiv ist
- Versuche eine erneute Synchronisation
- Kontaktiere: run-trend@arne-weiss.de

Viel Erfolg beim Training! 🏃‍♂️
