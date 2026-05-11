# Running Progress Tracker - Benutzerhandbuch

## Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Erste Schritte](#erste-schritte)
3. [Benutzeroberfläche](#benutzeroberfläche)
4. [Metriken-Erklärungen](#metriken-erklärungen)
5. [Charts und Visualisierungen](#charts-und-visualisierungen)
6. [Einstellungen](#einstellungen)
7. [Häufig gestellte Fragen](#häufig-gestellte-fragen)
8. [Über diese Software](#über-diese-software)

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
- **Training Load (ACWR)**: Übertrainings-Risikoerkennung basierend auf Acute:Chronic Workload Ratio
- **Marathon-Meilenstein**: Geschätztes Datum für 32 km Long Run / Marathon-Ready (oder "Milestone Reached!")
- **Race Time Predictions**: Geschätzte Wettkampfzeiten für 5K, 10K, Half und Marathon (HR-basiert)

**Training Load (ACWR):**
- **Load Score**: 0-100 Skala zeigt Übertrainings-Risiko basierend auf Acute:Chronic Workload Ratio
- **Status**: Aktuelle Belastungsklassifikation (SICHER, VORSICHT, WARNUNG, GEFAHR)
- **Warnmeldung**: Erscheint bei Score ≥ 80 mit spezifischen Empfehlungen zur Verletzungsrisiko-Reduzierung

### Charts (rechts)

Die Charts sind in 6 Hauptkategorien organisiert:

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

#### 5. Training Load Tab
- **Training Load (ACWR)**: Übertrainings-Risikoerkennung mit farbigen Sicherheitszonen

#### 6. Projection Tab
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

### Training Load (ACWR)

#### Was ist ACWR?

**ACWR** = **Acute:Chronic Workload Ratio** - eine wissenschaftlich validierte Metrik zur Erkennung von Übertraining und Verletzungsrisiko.

**Die Kernidee:**
Dein Körper passt sich am besten an, wenn die Trainingsbelastung schrittweise steigt. ACWR vergleicht deine **aktuelle Belastung** (akut) mit deiner **Grundbelastung** (chronisch), um gefährliche Spitzen oder Einbrüche zu erkennen.

**Zentrale Formel:**
```
ACWR = Akute Belastung / Chronische Durchschnittsbelastung

Wobei:
- Akute Belastung = Trainingsbelastung der letzten Woche
- Chronische Belastung = Durchschnittliche Trainingsbelastung der 4 Wochen VOR der akuten Woche
```

**Visuelles Beispiel:**
```
Woche:       -4    -3    -2    -1    Akut (Aktuell)
Distanz:     20km  22km  21km  23km  | 26km  ← Aktuelle Woche

Chronischer Ø = (20 + 22 + 21 + 23) / 4 = 21,5 km
Akute Belastung = 26 km
ACWR = 26 / 21,5 = 1,21 (SICHER - schrittweiser Anstieg)
```

**Warum ACWR wichtig ist:**
- **ACWR > 1,5**: Scharfe Spitze = Hohes Verletzungsrisiko (2-4x höher laut Forschung)
- **ACWR 0,8-1,3**: Sichere Zone = Körper kann sich anpassen
- **ACWR < 0,8**: Detraining = Fitnessverlust

**Wichtig:** ACWR ist NICHT nur Distanz. Es berücksichtigt **Distanz**, **Pace** und **Herzfrequenz** zusammen für ein vollständiges Bild.

---

#### Wie wird Training Load berechnet?

RunTrend berechnet einen **kombinierten Training Load Score (0-100)** durch Kombination von drei ACWR-Komponenten:

**1. Komponenten-ACWRs:**
```
Distanz-ACWR = Akute Distanz / Chronische Ø-Distanz
Pace-ACWR = Akute Geschwindigkeit / Chronische Ø-Geschwindigkeit (Pace invertiert)
HF-ACWR = Akute HF / Chronische Ø-HF
```

**2. Gewichtete Kombination:**
```
Kombiniertes ACWR = (Distanz-ACWR × 40%) +
                    (Pace-ACWR × 30%) +
                    (HF-ACWR × 30%)
```

**Warum diese Gewichtung?**
- **Distanz (40%)**: Primärer Belastungsindikator - wie viel du läufst
- **Pace (30%)**: Intensitätsindikator - wie hart du trainierst
- **Herzfrequenz (30%)**: Physiologischer Stress - wie dein Körper reagiert

**Wenn HF-Daten fehlen**: HF-ACWR wird auf 1,0 (neutral) gesetzt, und der Score wird nur mit Distanz und Pace berechnet.

**3. Score-Mapping (0-100):**
Das kombinierte ACWR wird auf eine 0-100 Skala für einfache Interpretation gemappt:

```
ACWR-Bereich      Training Load Score
──────────────────────────────────────
0,00 - 0,80  →   0-40   (Untertraining)
0,80 - 1,30  →   40-65  (SICHER)
1,30 - 1,50  →   65-80  (VORSICHT)
1,50 - 1,80  →   80-90  (WARNUNG)
1,80+        →   90-100 (GEFAHR)
```

**Beispielberechnung:**
```
Aktuelle Woche:  Distanz: 30 km, Pace: 5:30/km, HF: 155 bpm
4 Wochen vorher: Distanz: 25 km, Pace: 5:45/km, HF: 150 bpm

Distanz-ACWR = 30 / 25 = 1,20
Pace-ACWR = (60/5,30) / (60/5,75) = 10,91 / 10,43 = 1,05
HF-ACWR = 155 / 150 = 1,03

Kombiniertes ACWR = (1,20 × 0,4) + (1,05 × 0,3) + (1,03 × 0,3)
                  = 0,48 + 0,315 + 0,309
                  = 1,10

Training Load Score = ~52 (SICHER Zone)
Status: "SICHER - Schrittweise progressive Überlastung"
```

---

#### Score-Interpretation

| **Score** | **Status** | **ACWR-Bereich** | **Bedeutung** | **Aktion** |
|-----------|------------|------------------|---------------|------------|
| **0-40** | Untertraining | < 0,8 | Signifikanter Rückgang der Trainingsbelastung. Risiko von Detraining und Fitnessverlust. | Erwäge schrittweise Erhöhung von Volumen/Intensität, falls du dich von Verletzung erholst. Ansonsten Konsistenz beibehalten. |
| **40-65** | **SICHER** | 0,8-1,3 | **Optimale Trainingszone**. Dein Körper kann sich an die aktuelle Belastung anpassen. Progressive Überlastung ohne übermäßiges Risiko. | Setze Training wie geplant fort. Das ist die optimale Zone für langfristigen Fortschritt. |
| **65-80** | VORSICHT | 1,3-1,5 | Moderate Spitze in der Trainingsbelastung. Erhöhtes Verletzungsrisiko. Genau beobachten. | Sei extra vorsichtig mit Erholung. Erwäge, aktuelle Belastung für 1-2 Wochen zu halten statt weiter zu erhöhen. |
| **80-90** | **WARNUNG** | 1,5-1,8 | Scharfe Spitze. Hohes Verletzungsrisiko (2-4x normal). Aktion erforderlich. | **Reduziere Volumen der nächsten Woche um 20-30%**. Priorisiere Schlaf, Ernährung und Ruhetage. |
| **90-100** | **GEFAHR** | > 1,8 | Extreme Spitze. Sehr hohes Verletzungsrisiko. Sofortige Aktion erforderlich. | **Reduziere Volumen SOFORT um 40-50%**. Erwäge 2-3 leichte Tage. Risiko eines Übertrainingssyndroms. |

**Visuelle Anleitung:**
```
    0        40              65        80   90    100
    ├─────────┼───────────────┼─────────┼────┼─────┤
  Unter-   SICHER ZONE    VORSICHT  WARNUNG GEFAHR
 training   (ideal)
```

---

#### Wissenschaftliche Grundlage

Das ACWR-Konzept basiert auf peer-reviewed sportwissenschaftlicher Forschung:

**Primärquelle:**
> Gabbett, T.J. (2016). "The training-injury prevention paradox: should athletes be training smarter AND harder?" *British Journal of Sports Medicine*, 50(5), 273-280.

**Wichtigste Erkenntnisse:**
- **ACWR 0,8-1,3**: Niedrigstes Verletzungsrisiko (Baseline)
- **ACWR 1,0-1,25**: "Sweet Spot" für Leistungssteigerung
- **ACWR > 1,5**: Verletzungsrisiko steigt 2-4x
- **ACWR < 0,8**: Detraining und Fitnessverlust

**Anwendung auf Laufsport:**
ACWR wurde ursprünglich für Mannschaftssportarten (Rugby, Fußball) entwickelt, ist aber für Ausdauersport weitgehend validiert:
- Erkennt Übertraining durch plötzliche Volumenspitzen
- Berücksichtigt Fitnessabbau während Niedrigvolumen-Phasen
- Kombiniert Volumen UND Intensität für vollständiges Bild

**Einschränkungen der Forschung:**
- Die meisten Studien verwenden 7-Tage akut / 28-Tage chronische Fenster (RunTrend verwendet diesen Standard)
- Individuelle Variation existiert - manche Athleten tolerieren höhere Ratios
- ACWR ist ein **Risikoindikator**, keine Verletzungsgarantie
- Funktioniert am besten mit konsistentem Tracking über 8+ Wochen

**Warum RunTrend kombiniertes ACWR verwendet:**
Traditionelles ACWR berücksichtigt nur Distanz. RunTrend verbessert dies durch:
- **Pace-Komponente**: Erkennt Intensitätsspitzen (Speedwork, Tempоläufe)
- **HF-Komponente**: Erfasst physiologischen Stress (Hitze, Ermüdung, Krankheit)
- **Gewichtete Formel**: Balanciert alle drei Faktoren wissenschaftlich

---

#### Praktische Beispiele

**Beispiel 1: Sichere progressive Überlastung**
```
Szenario: Läufer erhöht schrittweise wöchentliches Volumen

Woche | Distanz | Pace    | HF  | Distanz-ACWR | Kombiniertes ACWR | Score | Status
──────|─────────|─────────|─────|──────────────|───────────────────|───────|────────
-4    | 20 km   | 6:00/km | 145 | -            | -                 | -     | -
-3    | 22 km   | 5:55/km | 147 | -            | -                 | -     | -
-2    | 24 km   | 5:50/km | 148 | -            | -                 | -     | -
-1    | 26 km   | 5:48/km | 149 | -            | -                 | -     | -
Jetzt | 28 km   | 5:45/km | 150 | 1,17         | 1,12              | 54    | SICHER

Chronischer Ø Distanz = (20+22+24+26)/4 = 23 km
Akute Distanz = 28 km
Distanz-ACWR = 28/23 = 1,17

Interpretation:
✓ Schrittweise 10% wöchentliche Erhöhung
✓ ACWR in sicherer Zone (0,8-1,3)
✓ Training Load Score 54 - weiter so!
```

**Beispiel 2: Gefährliche Spitze (Wettkampf + Hohes Volumen)**
```
Szenario: Läufer absolviert harten Wettkampf nach stetigem Grundlagentraining

Woche | Distanz | Pace    | HF  | Distanz-ACWR | Kombiniertes ACWR | Score | Status
──────|─────────|─────────|─────|──────────────|───────────────────|───────|────────
-4    | 30 km   | 5:30/km | 150 | -            | -                 | -     | -
-3    | 32 km   | 5:28/km | 151 | -            | -                 | -     | -
-2    | 31 km   | 5:32/km | 149 | -            | -                 | -     | -
-1    | 30 km   | 5:30/km | 150 | -            | -                 | -     | -
Jetzt | 50 km   | 5:00/km | 165 | 1,63         | 1,71              | 87    | WARNUNG

Chronischer Ø = 30,75 km bei 5:30/km, HF 150
Akut = 50 km bei 5:00/km, HF 165

Warum so hoch?
- Distanz-ACWR: 50/30,75 = 1,63 (63% Erhöhung!)
- Pace-ACWR: Viel schnelleres Tempo = hohe Intensitätsspitze
- HF-ACWR: 165/150 = 1,10 (physiologischer Stress)

Kombiniertes ACWR = 1,71 → Score 87 (WARNUNG)

Interpretation:
⚠ Wettkampfaufwand + hohes Volumen = gefährliche Kombination
⚠ Score 87 - HOHES Verletzungsrisiko
→ Aktion: Reduziere nächste Woche auf 30-35 km, nur leichtes Tempo
→ Erlaube 7-10 Tage Erholung vor Wiederaufnahme normalem Training
```

**Beispiel 3: Untertraining (Verletzungserholung)**
```
Szenario: Läufer kehrt nach 2-wöchiger Verletzungspause zurück

Woche | Distanz | Pace    | HF  | Distanz-ACWR | Kombiniertes ACWR | Score | Status
──────|─────────|─────────|─────|──────────────|───────────────────|───────|────────
-4    | 40 km   | 5:20/km | 155 | -            | -                 | -     | -
-3    | 42 km   | 5:18/km | 154 | -            | -                 | -     | -
-2    | 0 km    | -       | -   | -            | -                 | -     | Pause
-1    | 0 km    | -       | -   | -            | -                 | -     | Pause
Jetzt | 15 km   | 6:00/km | 145 | 0,37         | 0,42              | 18    | Unter

Chronischer Ø Distanz = (40+42+0+0)/4 = 20,5 km
Akute Distanz = 15 km
Distanz-ACWR = 15/20,5 = 0,73

Interpretation:
↓ ACWR < 0,8 = Detraining Zone
↓ Score 18 (Untertraining)
→ Dies ist ERWARTET nach Verletzungserholung
→ Schrittweiser Wiederaufbau: Woche 2: 20km, Woche 3: 25km, Woche 4: 30km
→ Benötigt 3-4 Wochen zur sicheren Rückkehr zur chronischen Baseline
```

---

#### Anforderungen

Um ACWR genau zu berechnen, benötigt RunTrend:

**Mindestdaten:**
- **Mindestens 5 vollständige Perioden** (Wochen oder Monate)
  - 1 akute Periode (letzte)
  - 4 chronische Perioden (Baseline-Durchschnitt)

**Nur vollständige Perioden:**
- ACWR verwendet **nur vollständig abgeschlossene Perioden**, um Verzerrungen zu vermeiden
- Unvollständige aktuelle Woche ist NICHT in Berechnung enthalten
- Beispiel: Wenn heute Mittwoch ist, wird ACWR aus letzter abgeschlossener Woche berechnet

**Warum 5 Wochen Minimum?**
```
Woche:   -4    -3    -2    -1   | Akut (Jetzt)
Status:  ✓     ✓     ✓     ✓   | ✓
         └──── Chronischer Ø ──┘  Aktuell

Benötigt: 4 Wochen für chronische Baseline + 1 akute Woche = 5 gesamt
```

**Datenqualität:**
- **Distanz**: Erforderlich (Kernmetrik)
- **Pace**: Erforderlich (darf nicht 0 oder fehlend sein)
- **Herzfrequenz**: Optional (wird auf neutral 1,0 gesetzt, wenn fehlend)

**Was passiert bei unzureichenden Daten?**
```
Anzeige:
Training Load: --
Status: "Unzureichende Daten (benötige 5 vollständige Wochen)"
Meldung: "Schließe mindestens 5 Wochen Training ab, um ACWR zu berechnen"
```

**Best Practices:**
- ✓ Tracke konsistent für 8+ Wochen für stabiles ACWR
- ✓ Stelle sicher, dass GPS-Uhren genaue Distanz und Pace aufzeichnen
- ✓ Verwende Herzfrequenzmesser für vollständiges Bild
- ✓ Lösche keine alten Aktivitäten - historische Daten verbessern Genauigkeit

---

#### Wann handeln?

Nutze den Training Load Score zur Steuerung deiner Trainingsentscheidungen:

**Score 0-40 (Untertraining):**
```
Was es bedeutet: Signifikanter Rückgang der Trainingsbelastung
Häufige Ursachen:
- Verletzungserholung / Rückkehr nach Pause
- Urlaub / Reise
- Krankheitserholung
- Absichtliches Tapering vor Wettkampf

Aktion:
✓ Falls Erholung: Schrittweise Rückkehr ist GUT (Score steigt natürlich)
✓ Falls ungeplant: Erhöhe Volumen um 10-15% pro Woche
✓ Beobachte: Sollte innerhalb 2-3 Wochen in 40-65 Bereich zurückkehren
✗ Nicht: Sofort zurück zum alten Volumen springen (Verletzungsrisiko)
```

**Score 40-65 (SICHER) ✓**
```
Was es bedeutet: Optimale Trainingszone - progressive Überlastung ohne übermäßiges Risiko
Häufige Ursachen:
- Konsistentes Woche-für-Woche Training
- Schrittweise Volumenerhöhungen (5-10% pro Woche)
- Gut geplante Trainingszyklen

Aktion:
✓ Setze aktuellen Trainingsplan fort
✓ Dies ist das ZIEL für nachhaltige langfristige Verbesserung
✓ Kleine Woche-für-Woche Variationen (45→55→50) sind normal
✓ Fokus auf Konsistenz, Schlaf, Ernährung
```

**Score 65-80 (VORSICHT):**
```
Was es bedeutet: Moderate Spitze - erhöhtes Verletzungsrisiko
Häufige Ursachen:
- Schnellere als geplante Volumenerhöhung
- Hinzugefügtes Speedwork + hohes Volumen
- Wettkampfaufwand ohne Reduzierung des Wochenvolumens

Aktion:
⚠ Halte aktuelles Volumen für 1-2 Wochen (erhöhe nicht weiter)
⚠ Priorisiere Erholung: 8+ Stunden Schlaf, richtige Ernährung
⚠ Beobachte Verletzungszeichen: ungewöhnlicher Muskelkater, Schmerz, Ermüdung
✓ Kannst weiter trainieren, aber sei konservativ
✓ Nächste Erhöhung: Warte bis Score auf 50-60 Bereich fällt
```

**Score 80-90 (WARNUNG) ⚠:**
```
Was es bedeutet: Scharfe Spitze - HOHES Verletzungsrisiko (2-4x normal)
Häufige Ursachen:
- Wettkampf + hohes Trainingsvolumen gleiche Woche
- Plötzliche 30-50% Volumenerhöhung
- High-Intensity Woche nach leichten Wochen

Aktion:
→ REDUZIERE Volumen der nächsten Woche um 20-30%
→ Nächste 3-5 Tage: Nur leichte Läufe (kein Speedwork, kein Tempo)
→ Tägliche Beobachtung: Bei Schmerz/Ermüdung sofort Ruhetag einlegen
→ Erholungswoche: Niedrige Intensität, Fokus auf Schlaf/Ernährung
→ Nach 1 Woche: Score neu bewerten vor Wiederaufnahme normalen Trainings

Beispiel:
Aktuelle Woche: 50km → Score 85 (WARNUNG)
Nächste Woche: 35km leichtes Tempo → Score fällt auf ~55
Woche danach: 40-45km fortsetzen → Schrittweiser Wiederaufbau
```

**Score 90-100 (GEFAHR) 🚨:**
```
Was es bedeutet: EXTREME Spitze - sehr hohes Verletzungsrisiko, Übertrainingssyndrom-Risiko
Häufige Ursachen:
- Ultra-Wettkampf + weiterhin hohes Volumen
- Verdopplung des Volumens der Vorwoche
- Hohes Volumen + hohe Intensität + unzureichende Erholung

Aktion:
🚨 SOFORTIGE Reduzierung: Schneide Volumen um 40-50%
🚨 Nächste 2-3 Tage: Vollständige Ruhe ODER sehr leichte 20-30min Läufe
🚨 Achte auf Übertrainings-Symptome:
   - Anhaltende Ermüdung trotz Ruhe
   - Erhöhte Ruhe-HF (+5-10 bpm)
   - Schlafprobleme
   - Motivationsverlust
   - Häufiges Krankwerden
🚨 Falls Symptome auftreten: Volle Ruhewoche, erwäge ärztliche Konsultation
→ Erholung: 1-2 Wochen niedriges Volumen vor Wiederaufnahme normalem Training

Beispiel:
Aktuelle Woche: 80km harter Aufwand → Score 95
Nächste Woche: 30-40km NUR leichtes Tempo
Woche 2: 45km leicht (falls gutes Gefühl)
Woche 3: 55km (normales Training fortsetzen falls Score < 70)
```

**Allgemeine Richtlinien:**
- **Grüne Zone (40-65)**: Normal trainieren
- **Gelbe Zone (65-80)**: Aktuelle Belastung halten, nicht erhöhen
- **Orange Zone (80-90)**: Belastung um 20-30% reduzieren, leichte Woche
- **Rote Zone (90-100)**: Belastung um 40-50% reduzieren, mögliche Ruhetage

---

#### Ergänzende Metriken

Training Load (ACWR) funktioniert am besten in Kombination mit anderen RunTrend-Metriken:

**1. Training Score**
```
Was: Langfristiger Fortschritt (Distanz, Pace, Frequenz kombiniert)
ACWR: Kurzfristiges Verletzungsrisiko (akut vs. chronische Belastung)

Zusammen verwenden:
✓ Training Score steigt + ACWR 40-65 = Ausgezeichnet (sichere Verbesserung)
⚠ Training Score steigt + ACWR 80+ = Gefahr (zu schnelle Verbesserung)
✓ Training Score stabil + ACWR 40-65 = Erhaltungsphase (OK)
↓ Training Score fällt + ACWR 0-40 = Detraining (erwartet)

Beispiel:
Training Score: 78 (steigender Trend)
Training Load: 82 (WARNUNG)
→ Du verbesserst dich, aber ZU SCHNELL - Verletzungsrisiko
→ Aktion: Halte aktuelles Volumen für 2 Wochen, lass Körper anpassen
```

**2. Efficiency Factor**
```
Was: Aerobe Fitness (Pace normalisiert durch Herzfrequenz)
ACWR: Trainingsbelastungs-Balance

Zusammen verwenden:
✓ EF steigt + ACWR 40-65 = Optimal (Fitness verbessert sich, sichere Belastung)
⚠ EF fällt + ACWR 80+ = Übertraining (Körper erholt sich nicht)
⚠ EF fällt + ACWR 40-65 = Mögliche Ermüdung, Krankheit oder Hitze

Beispiel:
Efficiency Factor: 11,2 → 10,8 (fallend)
Training Load: 75 (VORSICHT)
→ Körper ist gestresst trotz "nur" Vorsichtszone
→ Aktion: Extra Ruhetage, prüfe auf Krankheit/Ermüdung
```

**3. Durchschnittliche Herzfrequenz**
```
Was: Kardiovaskulärer Stress pro Lauf
ACWR: Kombinierte Belastung inkl. HF

Zusammen verwenden:
↑ Avg HF steigt + ACWR 80+ = Hoher physiologischer Stress
↑ Avg HF steigt + gleiche Pace = Mögliche Ermüdung/Übertraining
✓ Avg HF stabil + ACWR 40-65 = Gute Erholung

Beispiel:
Avg HF: 155 → 165 (gleiche Pace)
Training Load: 78 (VORSICHT)
→ Herz arbeitet härter für gleichen Aufwand = Ermüdung
→ Aktion: Leichte Woche, Erholung priorisieren
```

**4. Längster Lauf**
```
Was: Ausdauerkapazität (einzelne Laufdistanz)
ACWR: Wöchentliche Belastungsbalance

Zusammen verwenden:
✓ Long Run schrittweise steigend + ACWR 40-65 = Sicherer Ausdaueraufbau
⚠ Long Run Spitze (15km → 30km) = Wird hohes ACWR auslösen
→ Erhöhe Long Run um 10-15% pro Woche um ACWR sicher zu halten

Beispiel:
Längster Lauf: 20km → 32km (60% Sprung)
Training Load: 85 (WARNUNG)
→ Long Run Spitze verursachte ACWR Warnung
→ Aktion: Nächste Woche Long Run: 25km (Schritt zurück)
```

**5. Rate of Change (RoC)**
```
Was: Trendrichtung (steigend/fallend/stabil)
ACWR: Spitzenerkennung

Zusammen verwenden:
✓ Distanz-RoC positiv + ACWR 40-65 = Nachhaltiges Wachstum
⚠ Distanz-RoC steil + ACWR 80+ = Zu aggressive Progression
↓ Pace-RoC negativ (schneller werdend) + ACWR 80+ = Intensitätsspitze

Beispiel:
Distanz-RoC: +3 km/Woche (steiler positiver Trend)
Training Load: 82 (WARNUNG)
→ Konsistente steile Progression verursachte Spitze
→ Aktion: Progression auf +1-2 km/Woche abflachen
```

**Zusammenfassungstabelle:**

| **Metrik** | **Was sie misst** | **Zeitrahmen** | **Ergänzt ACWR durch** |
|------------|-------------------|----------------|------------------------|
| Training Score | Gesamtfitness-Fortschritt | Langfristig (Monate) | Zeigt ob Verbesserungen nachhaltig sind |
| Efficiency Factor | Aerobe Fitness | Mittelfristig (Wochen) | Erkennt Ermüdung/Übertraining |
| Avg HR | Kardiovaskulärer Stress | Pro Periode (Woche/Monat) | Zeigt physiologische Reaktion |
| Längster Lauf | Ausdauerkapazität | Pro Periode | Identifiziert Long Run Spitzen |
| Rate of Change | Trendrichtung | Rollierend 8-Perioden | Zeigt ob Progression zu steil ist |

**Best Practice:**
Überprüfe alle Metriken zusammen im Zusammenfassungspanel für vollständiges Bild:
- ✓ Alles grün = Weiter trainieren
- ⚠ Eine Metrik Warnung = Genau beobachten, bei Bedarf anpassen
- 🚨 Mehrere Metriken Warnung = Sofort handeln (Belastung reduzieren)

---

#### Einschränkungen

ACWR ist ein mächtiges Werkzeug, hat aber wichtige Einschränkungen:

**1. Individuelle Variation**
```
Einschränkung: Jeder toleriert Trainingsbelastung unterschiedlich
- Erfahrene Läufer: Können ACWR 1,4-1,5 sicher handhaben
- Anfänger: Können sich bei ACWR 1,2-1,3 verletzen
- Alter, Genetik, Erholungsfähigkeit: Alles beeinflusst Toleranz

Was das bedeutet:
✓ Nutze ACWR als LEITFADEN, nicht absolute Regel
✓ Lerne deine persönlichen Grenzen über Monate des Trackings
✓ Falls verletzungsanfällig: Bleibe näher am 0,8-1,2 Bereich
✗ Ignoriere nicht Schmerz/Ermüdung nur weil ACWR "sicher" ist
```

**2. Nachlaufender Indikator**
```
Einschränkung: ACWR erkennt Spitzen NACHDEM sie passiert sind
- Zeigt Spitze DIESER Woche
- Sagt nicht NÄCHSTE Woche Risiko voraus
- Zu dem Zeitpunkt wenn Score hoch ist, hast du bereits riskant trainiert

Was das bedeutet:
✓ Nutze ACWR für NÄCHSTE Woche Planung (reduziere Belastung bei hohem Score)
✓ Plane voraus: Erstelle keine Spitzen von vornherein
✓ Kombiniere mit vorausschauenden Metriken (RoC Trends)
✗ Reagiere nicht nur - plane auch konservativ
```

**3. Erfasst nicht alles**
```
Einschränkung: ACWR nutzt Distanz, Pace, HF - verpasst aber:
- Gelände (Trail vs. Straße, Hügel vs. flach)
- Wetter (Hitze, Kälte, Wind fügen Stress hinzu)
- Lebensstress (Arbeit, Schlaf, Ernährung)
- Muskuläre vs. kardiovaskuläre Ermüdung
- Kumulative Ermüdung über Monate

Was das bedeutet:
✓ ACWR ist ein Werkzeug unter vielen
✓ Höre auf deinen Körper - Ermüdung, Muskelkater, Motivation
✓ Berücksichtige externe Faktoren bei Score-Interpretation
⚠ Beispiel: ACWR 55 (SICHER) aber Laufen bei 35°C = Trotzdem riskant
```

**4. Erfordert konsistentes Tracking**
```
Einschränkung: ACWR-Genauigkeit hängt von vollständigen Daten ab
- Fehlende Wochen: Verzerrt chronische Baseline
- Inkonsistentes Tracking: Unzuverlässige Berechnungen
- Manuelle Einträge: Können Fehler haben

Was das bedeutet:
✓ Tracke jeden Lauf (GPS-Uhr oder manuelle Eingabe)
✓ Lösche keine alten Aktivitäten
✓ 8+ Wochen Daten = Zuverlässigeres ACWR
⚠ Nach Pause: ACWR wird für 4-5 Wochen verzerrt sein
```

**5. Nicht verletzungssicher**
```
Einschränkung: Niedriges ACWR ≠ Garantierte Sicherheit
- ACWR 0,9 erlaubt noch Verletzungen (Biomechanik, Schuhe, Gelände)
- Plötzliche Intensitätsänderungen können auch bei niedrigem ACWR verletzen
- Überlastungsverletzungen entwickeln sich über Wochen/Monate (nicht nur akute Spitzen)

Was das bedeutet:
✓ ACWR reduziert Risiko, eliminiert es nicht
✓ Benötigst noch richtige Schuhe, Krafttraining, Ruhetage
✓ Gehe Schmerz früh an, auch wenn ACWR "sicher" ist
✗ Trainiere nicht durch Schmerz weil Score grün ist
```

**6. Wettkampfwochen sind schwierig**
```
Einschränkung: Wettkämpfe spitzen ACWR aber sind notwendig für Leistung
- Wettkampfaufwand = Hohe Intensität + hohe HF
- Oft kombiniert mit hohem Wochenvolumen
- Wird WARNUNG/GEFAHR Scores auslösen

Was das bedeutet:
✓ Erwarte hohes ACWR während Wettkampfwochen
✓ Plane Erholungswoche NACH Wettkampf (reduziere Volumen 30-50%)
✓ Wettkämpfe nicht jede Woche (ACWR bleibt gefährlich hoch)
→ Strategie: Wettkampf → Erholungswoche → Schrittweiser Wiederaufbau → Wettkampf
```

**7. Unvollständige aktuelle Periode**
```
Einschränkung: ACWR nicht gezeigt bis Periode vollständig ist
- Bei Ansicht mitten in Woche: Kein ACWR für aktuelle Woche
- Sieht nur abgeschlossene Wochen/Monate
- Kann Score der aktuellen Woche nicht vorhersagen bis sie fertig ist

Was das bedeutet:
✓ Nutze Score der letzten Woche zur Steuerung DIESER Woche
✓ Falls letzte Woche 75 (VORSICHT) war, halte diese Woche konservativ
✗ Kannst kein Echtzeit-ACWR während der Woche sehen
```

**Wie ACWR trotz Einschränkungen effektiv nutzen:**

1. **Kombiniere mit subjektivem Feedback:**
   - Morgen-Ruhe-HF (erhöht = Ermüdung)
   - Schlafqualität
   - Motivationsniveau
   - Muskelkater

2. **Nutze konservative Schwellenwerte falls:**
   - Du verletzungsanfällig bist
   - Du Anfänger bist (< 1 Jahr Laufen)
   - Du über 45 Jahre alt bist
   - Du frühere Verletzungen hast

3. **Plane voraus:**
   - Baue Volumen schrittweise auf (10% Regel)
   - Plane Erholungswochen (alle 3-4 Wochen, reduziere 20-30%)
   - Nach Wettkämpfen: Plane IMMER Erholungswoche

4. **Keine Panik über einzelnen Datenpunkt:**
   - Ein hoher Score ≠ garantierte Verletzung
   - Betrachte Trends über 3-4 Wochen
   - Passe an falls Scores erhöht bleiben

**Denke daran:** ACWR ist ein Risikomanagement-Werkzeug, keine Kristallkugel. Nutze es für klügere Trainingsentscheidungen, aber höre immer auf deinen Körper.

---

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

**Rate of Change (RoC) Overlay:**
- **Aktivieren:** Aktiviere "Show Rate of Change" Checkbox über dem Chart
- **Zeigt:** Rollierend 8-Perioden lineare Regressions-Steigung (lila gestrichelte Linie)
- **Misst:** Wie schnell sich deine Distanz pro Periode ändert (km/Woche oder km/Monat)
- **Rechte Y-Achse:** RoC-Skala zeigt Rate in km pro Periode

**Interpretation:**
- **Positiver RoC** (Linie über Null): Distanz steigt
  - Beispiel: +2 km/Woche = durchschnittlich 2 km pro Woche hinzufügen
- **Negativer RoC** (Linie unter Null): Distanz sinkt
- **Steile positive Steigung**: Aggressive Volumenerhöhung (kann hohen Training Load auslösen)
- **Flache Linie nahe Null**: Stabiles Volumen (Erhaltungsphase)

**Nutzung mit Training Load:**
```
Steiler Distanz-RoC (+3 km/Woche) + Training Load 82 (WARNUNG)
→ Volumenerhöhung ist zu aggressiv
→ Aktion: Progression auf +1-2 km/Woche abflachen
```

**Tipp:** Nutze RoC um zu sehen, ob deine Volumenprogression nachhaltig ist, bevor sie Training Load Warnungen auslöst.

---

#### Pace/Speed Chart
**Zeigt:** Pace (min/km) oder Speed (km/h) pro Periode

**Umschaltung:** Toolbar → Metric: "Pace" oder "Speed"

**Interpretation:**
- **Pace sinkt** = Geschwindigkeit wird besser
- **Speed steigt** = Geschwindigkeit wird besser

**Rate of Change (RoC) Overlay:**
- **Aktivieren:** Aktiviere "Show Rate of Change" Checkbox über dem Chart
- **Zeigt:** Rollierend 8-Perioden lineare Regressions-Steigung (lila gestrichelte Linie)
- **Misst:** Wie schnell sich dein Pace/Speed pro Periode ändert
- **Rechte Y-Achse:** RoC-Skala zeigt Rate in min/km pro Woche (Pace) oder km/h pro Woche (Speed)

**Interpretation (Pace-Modus):**
- **Negativer RoC** (Linie unter Null): Wirst schneller (Pace sinkt) ✓
  - Beispiel: -0,05 min/km pro Woche = 3 Sekunden schneller pro km jede Woche
- **Positiver RoC** (Linie über Null): Wirst langsamer (Pace steigt)
- **Flache Linie nahe Null**: Stabiles Pace

**Interpretation (Speed-Modus):**
- **Positiver RoC** (Linie über Null): Wirst schneller (Speed steigt) ✓
  - Beispiel: +0,1 km/h pro Woche = 0,1 km/h Speed-Zuwachs jede Woche
- **Negativer RoC** (Linie unter Null): Wirst langsamer
- **Flache Linie nahe Null**: Stabile Geschwindigkeit

**Nutzung mit Training Load:**
```
Pace-RoC: -0,10 min/km pro Woche (viel schneller werdend)
Training Load: 78 (VORSICHT)
→ Intensitätserhöhung ist signifikant
→ Kombination mit Volumenerhöhung = höheres Verletzungsrisiko
→ Aktion: Stabilisiere Pace während Volumenaufbau
```

**Tipp:** Scharfe Pace-Verbesserungen können zum Training Load beitragen, selbst wenn Volumen stabil ist. Überwache beide Metriken zusammen.

---

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
- **Rechte Y-Achse**: Efficiency Factor ×1000 (für EF Line) ODER HR-RoC wenn RoC-Overlay aktiviert

---

#### Rate of Change (RoC) Overlay

**Aktivieren:** Aktiviere "Show Rate of Change" Checkbox über dem Chart

**Zeigt:** Rollierend 8-Perioden lineare Regressions-Steigung für durchschnittliche Herzfrequenz (lila gestrichelte Linie)

**Misst:** Wie schnell sich deine durchschnittliche HF pro Periode ändert (bpm/Woche oder bpm/Monat)

**Rechte Y-Achse:** Wenn RoC aktiviert ist, zeigt die rechte Achse HF-RoC Skala (bpm pro Periode) anstelle von EF

**Interpretation:**
- **Positiver RoC** (Linie über Null): HF steigt
  - Beispiel: +2 bpm/Woche = Herzfrequenz steigt um 2 Schläge pro Woche
  - **Mögliche Ursachen:**
    - Erhöhung der Trainingsintensität
    - Ermüdungsansammlung
    - Übertraining
    - Hitzestress (Sommertraining)
    - Sich entwickelnde Krankheit
- **Negativer RoC** (Linie unter Null): HF sinkt ✓
  - Beispiel: -1 bpm/Woche = Herzfrequenz fällt um 1 Schlag pro Woche
  - **Mögliche Ursachen:**
    - Verbesserte aerobe Fitness
    - Bessere Trainingsanpassung
    - Erholungsphase funktioniert gut
- **Flache Linie nahe Null**: Stabile HF (Erhaltungsphase)

**Nutzung mit Training Load:**
```
Avg HF-RoC: +3 bpm/Woche (steigender Trend)
Training Load: 75 (VORSICHT)
Pace: Stabil (keine Verbesserung)
→ Herz arbeitet härter für gleiche Pace = Ermüdung
→ Aktion: Extra Erholungstage, prüfe auf Krankheit/Übertraining
```

**Nutzung mit Efficiency Factor:**
```
Szenario 1: HF steigt, EF stabil
→ HF-RoC: +2 bpm/Woche
→ EF: Stabil bei 18,5
→ Interpretation: Möglicherweise nur höhere Trainingsintensität (OK wenn geplant)

Szenario 2: HF steigt, EF fällt
→ HF-RoC: +2 bpm/Woche
→ EF: Fällt von 18,5 → 17,2
→ Interpretation: Warnsignal für Übertraining/Ermüdung
→ Aktion: Plane Erholungswoche, reduziere Intensität
```

**Wichtiger Hinweis:**
- HF-RoC ist besonders nützlich zur Erkennung **schleichender Ermüdungsansammlung**
- Ein einzelner hoher HF-Tag ist nicht besorgniserregend, aber ein **steigender Trend über Wochen** signalisiert ein Problem
- Kombiniere immer mit EF und subjektivem Feedback (Schlaf, Motivation, Muskelkater)

**Tipp:** Aktiviere RoC wenn du Übertraining vermutest oder validieren möchtest, dass deine Erholungswochen funktionieren (RoC sollte sich während Erholung abflachen oder negativ werden).

---

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

### Training Load Tab

#### Training Load (ACWR) Chart

**Zeigt:** Training Load Score (0-100) über Zeit mit farbigen Sicherheitszonen zur Erkennung von Übertrainings-Risiko.

**Was ist ACWR?**
ACWR (Acute:Chronic Workload Ratio) vergleicht deine aktuelle Trainingsbelastung mit deiner Baseline-Belastung. Diese wissenschaftlich validierte Metrik hilft dir, sicher zu trainieren, indem sie gefährliche Spitzen oder Einbrüche in Trainingsvolumen, Intensität und physiologischem Stress erkennt.

**Für detaillierte Erklärung** siehe: **Metriken-Erklärungen → Training Load (ACWR)**

---

#### Visualisierungs-Features

**1. Training Load Linie (Blau)**
- Zeigt deinen kombinierten Training Load Score (0-100) pro Periode
- Kombiniert Distanz (40%), Pace (30%) und Herzfrequenz (30%) in einen einzigen Übertrainings-Risiko-Indikator
- Höhere Werte = höheres Verletzungsrisiko durch Trainingsspitzen
- Niedrigere Werte = Detraining-Risiko durch unzureichende Belastung

**2. Farbige Hintergrund-Zonen**
Der Chart zeigt farbige Zonen zur schnellen Beurteilung der Trainingssicherheit:

```
Zonen-Farbe  Score-Bereich  Status          Risikoniveau
──────────────────────────────────────────────────────────
Hellgrau     0-40           Untertraining   Detraining-Risiko
Grün         40-65          SICHER          Optimale Zone ✓
Gelb         65-80          VORSICHT        Moderates Risiko
Orange       80-90          WARNUNG         Hohes Risiko ⚠
Rot          90-100         GEFAHR          Sehr hohes Risiko 🚨
```

**Visuelle Anleitung:**
```
100 ┤                                    ╔═══════════╗
 90 ┤                                    ║  GEFAHR   ║ ROT
 80 ┤                            ╔═══════╩═══════════╝
 70 ┤                            ║    WARNUNG         ORANGE
 65 ┤                    ╔═══════╩═══════╗
 60 ┤                    ║    VORSICHT    ║ GELB
 50 ┤        ╔═══════════╩════════════════╝
 40 ┤        ║      SICHER ZONE           ║ GRÜN ✓
 30 ┤        ║                            ║
 20 ┤╔═══════╩════════════════════════════╝
 10 ┤║    UNTERTRAINING                   ║ GRAU
  0 ┴╚════════════════════════════════════╝
```

**3. Interaktive Legende**
- Klicke auf Legendeneinträge zum Ein-/Ausblenden der Training Load Linie
- Alle Serien können ein-/ausgeschaltet werden

---

#### Wie den Chart interpretieren

**Linie in GRÜNER Zone (40-65) - SICHER ✓**
```
Was es bedeutet:
✓ Optimale Trainingszone
✓ Progressive Überlastung ohne übermäßiges Verletzungsrisiko
✓ Körper kann sich an aktuelle Belastung anpassen

Aktion:
→ Setze Training wie geplant fort
→ Dies ist das ZIEL für nachhaltige langfristige Verbesserung
```

**Linie betritt GELBE Zone (65-80) - VORSICHT**
```
Was es bedeutet:
⚠ Moderate Spitze in Trainingsbelastung
⚠ Erhöhtes Verletzungsrisiko
⚠ Trainingsprogression könnte zu aggressiv sein

Aktion:
→ Halte aktuelles Volumen für 1-2 Wochen (nicht weiter erhöhen)
→ Priorisiere Erholung: Schlaf, Ernährung, Ruhetage
→ Beobachte Verletzungszeichen: ungewöhnlicher Muskelkater, Schmerz, Ermüdung
```

**Linie betritt ORANGE Zone (80-90) - WARNUNG ⚠**
```
Was es bedeutet:
🚨 Scharfe Spitze - HOHES Verletzungsrisiko (2-4x normal)
🚨 Gefährliche Kombination aus Volumen, Intensität oder physiologischem Stress
🚨 Sofortige Aktion erforderlich

Aktion:
→ REDUZIERE Volumen der nächsten Woche um 20-30%
→ Nächste 3-5 Tage: Nur leichte Läufe (kein Speedwork, kein Tempo)
→ Fokus auf Erholungswoche mit niedriger Intensität
→ Score neu bewerten vor Wiederaufnahme normalen Trainings
```

**Linie betritt ROTE Zone (90-100) - GEFAHR 🚨**
```
Was es bedeutet:
🔴 EXTREME Spitze - sehr hohes Verletzungsrisiko
🔴 Risiko eines Übertrainingssyndroms
🔴 Sofortige Reduzierung erforderlich

Aktion:
→ SOFORTIGE Reduzierung: Schneide Volumen um 40-50%
→ Nächste 2-3 Tage: Vollständige Ruhe ODER sehr leichte 20-30min Läufe
→ Achte auf Übertrainings-Symptome:
   - Anhaltende Ermüdung trotz Ruhe
   - Erhöhte Ruhe-HF (+5-10 bpm)
   - Schlafprobleme
   - Motivationsverlust
→ Falls Symptome auftreten: Volle Ruhewoche, erwäge ärztliche Konsultation
```

**Linie in GRAUER Zone (0-40) - Untertraining**
```
Was es bedeutet:
↓ Signifikanter Rückgang der Trainingsbelastung
↓ Risiko von Detraining und Fitnessverlust

Häufige Ursachen:
- Verletzungserholung / Rückkehr nach Pause
- Urlaub / Reise
- Krankheitserholung
- Absichtliches Tapering vor Wettkampf

Aktion:
✓ Falls Erholung: Schrittweise Rückkehr ist GUT (Score steigt natürlich)
✓ Falls ungeplant: Erhöhe Volumen um 10-15% pro Woche
✗ Nicht sofort zurück zum alten Volumen springen (Verletzungsrisiko)
```

---

#### Praktische Anwendungsfälle

**Anwendungsfall 1: Wettkampfwochen-Spitzen erkennen**
```
Szenario: Du hast einen Halbmarathon-Wettkampf gelaufen

Woche 1-4:  Score 52-58 (GRÜN - konsistentes Training)
Woche 5:    Score 85 (ORANGE - Wettkampfaufwand + Wettkampfvolumen)
           ⚠ WARNUNG: Hohes Verletzungsrisiko

Aktion:
→ Woche 6: Erholungswoche (30-50% Volumenreduzierung)
→ Score fällt zurück in GRÜNE Zone
→ Woche 7: Schrittweise Rückkehr zu normalem Training
```

**Anwendungsfall 2: Trainingsprogression überwachen**
```
Szenario: Volumenaufbau für Marathon-Training

Woche 1:  30 km, Score 48 (GRÜN)
Woche 2:  33 km, Score 52 (GRÜN) ✓ Sichere Erhöhung
Woche 3:  36 km, Score 56 (GRÜN) ✓ Sichere Erhöhung
Woche 4:  40 km, Score 61 (GRÜN) ✓ Sichere Erhöhung
Woche 5:  55 km, Score 78 (GELB) ⚠ Zu aggressiv!

Aktion:
→ Woche 6: Halte bei 40-42 km (nicht weiter erhöhen)
→ Lass Körper für 1-2 Wochen anpassen
→ Score stabilisiert sich zurück zu GRÜN
→ Dann schrittweise Progression fortsetzen
```

**Anwendungsfall 3: Rückkehr nach Verletzung**
```
Szenario: Rückkehr nach 2-wöchiger Laufpause

Woche -2 bis -1:  0 km (Verletzungspause)
Woche 1:         15 km, Score 18 (GRAU - Untertraining)
                 ✓ Erwartet nach Pause

Woche 2:         20 km, Score 28 (GRAU)
Woche 3:         25 km, Score 42 (GRÜN) ✓ Zurück in sichere Zone
Woche 4:         30 km, Score 55 (GRÜN) ✓ Vollständig erholt

Interpretation:
→ Schrittweiser Wiederaufbau über 3-4 Wochen ist KORREKT
→ Score steigt natürlich während chronische Baseline sich anpasst
→ Geduld verhindert erneute Verletzung
```

---

#### Datenanforderungen

Zur Anzeige des Training Load Charts:
- **Minimum 5 vollständige Perioden** (Wochen oder Monate)
  - 1 akute Periode (letzte)
  - 4 chronische Perioden (Baseline-Durchschnitt)

**Bei unzureichenden Daten:**
```
Anzeige: Leerer Chart mit Meldung
"Training Load benötigt mindestens 5 vollständige Perioden"

Lösung:
→ Setze Training und Tracking fort
→ Chart erscheint sobald 5 Perioden abgeschlossen sind
```

**Nur vollständige Perioden:**
- Nur vollständig abgeschlossene Wochen/Monate werden verwendet
- Unvollständige aktuelle Periode wird NICHT gezeigt (verhindert irreführende Daten)
- Beispiel: Wenn heute Mittwoch ist, zeigt Chart bis letzte abgeschlossene Woche

---

#### Tipps zur Nutzung des Training Load Charts

**1. Prüfe nach jeder Woche/Monat**
Überprüfe deinen neuesten Training Load Score zur Planung der nächsten Periode:
- GRÜN (40-65): Wie geplant fortsetzen
- GELB (65-80): Volumen halten, nicht erhöhen
- ORANGE/ROT (80-100): Volumen reduzieren, Erholung nötig

**2. Plane Erholungswochen**
Nutze den Chart zur strategischen Erholungsplanung:
- Alle 3-4 Wochen: Volumen um 20-30% reduzieren
- Nach Wettkämpfen: Erwarte ORANGE/ROT Scores → plane Erholungswoche
- Falls Score Richtung GELB steigt: Halte Belastung statt zu erhöhen

**3. Vergleiche mit Training Score**
Betrachte beide Charts zusammen für vollständiges Bild:
- **Training Score**: Langfristiger Fortschritt (verbessere ich mich?)
- **Training Load**: Kurzfristiges Risiko (trainiere ich sicher?)

**Ideales Szenario:**
✓ Training Score steigt (Fortschritte machen)
✓ Training Load in GRÜNER Zone (sicher fortschreiten)

**Warn-Szenario:**
⚠ Training Score steigt (Fortschritte machen)
⚠ Training Load in ORANGE/ROT (zu schneller Fortschritt)
→ Du verbesserst dich, riskierst aber Verletzung - verlangsame Progression

**4. Nutze mit Rate of Change (RoC)**
Aktiviere RoC-Overlays auf Distanz/Pace/HF-Charts um zu sehen:
- Ob Trends zu steil sind (verursacht hohen Training Load)
- Ob Progressionsrate nachhaltig ist
- Wann Progression abgeflacht werden sollte um Spitzen zu vermeiden

**5. Verfolge Muster über Monate**
Suche nach Mustern in deinem Training Load:
- Spitzen konsistent nach Wettkämpfen?
- Lösen bestimmte Trainingsblöcke GELB/ORANGE Zonen aus?
- Wie lange dauert Erholung von Spitzen?
- Lerne deine persönliche Toleranz und passe Training entsprechend an

---

#### Wichtige Hinweise

**Training Load vs Training Score:**

| Metrik | Zweck | Zeitrahmen | Interpretation |
|--------|-------|------------|----------------|
| **Training Score** | Misst Fortschritt/Fitness | Langfristig (Monate) | Höher = bessere Fitness |
| **Training Load (ACWR)** | Erkennt Verletzungsrisiko | Kurzfristig (akut vs. chronisch) | GRÜNE Zone = optimal, HOHE Scores = Gefahr |

Sie messen UNTERSCHIEDLICHE Dinge:
- ✓ Training Score 75 + Training Load 52 (GRÜN) = Ausgezeichnet (fit UND sicher)
- ⚠ Training Score 75 + Training Load 85 (ORANGE) = Riskant (fit ABER unsichere Progression)

**Einschränkungen:**
- ACWR ist ein **Risikoindikator**, keine Garantie
- Individuelle Toleranz variiert (Erfahrung, Alter, Verletzungsgeschichte)
- Erfasst nicht Gelände, Wetter, Lebensstress oder Ernährung
- Nutze als **ein Werkzeug unter vielen** - höre immer auf deinen Körper
- Siehe **Metriken-Erklärungen → Training Load (ACWR) → Einschränkungen** für vollständige Details

**Best Practice:**
Kombiniere Training Load Chart mit:
- Zusammenfassungspanel (schneller Status-Überblick)
- Efficiency Factor (erkenne Ermüdung/Übertraining)
- Durchschnittliche Herzfrequenz (physiologischer Stress-Indikator)
- Subjektives Feedback (Ermüdung, Muskelkater, Motivation, Schlafqualität)

---

### Performance Tab

Vergleicht deine aktuelle Form mit einer **altersadjustierten Referenz** —
zwei wissenschaftlich unterschiedliche Sichten in einem Tab.

#### Wann ist dieser Chart sinnvoll?

Wenn du wissen willst, *wie weit du von deiner möglichen Höchstform für
dein Alter entfernt bist* — anders als der Score-Chart, der dich nur
mit deinem eigenen rollenden Baseline vergleicht.

#### Voraussetzungen

In **Einstellungen → Allgemein → Profil** brauchst du:

- **Geburtsdatum** (für beide Sichten)
- **Geschlecht** (nur für die WMA-Sicht — die Tabellen sind
  geschlechtsspezifisch)

Beides ist optional gespeichert; ohne Geburtsdatum bleibt der Tab leer
mit einem entsprechenden Hinweis. „Keine Angabe" beim Geschlecht
deaktiviert nur die WMA-Sicht, nicht die HF-Sicht.

#### Sicht 1: WMA Age-Graded %

**Datengrundlage:** [World Masters Athletics 2023](https://world-masters-athletics.org/wp-content/uploads/2023/02/2023-Age-Factors-WMA.pdf)
Altersfaktor-Tabellen (seit 1. Januar 2023 verbindlich, aus über 2,8 Mio
Wettkampfzeiten abgeleitet, mit Faktoren pro einzelnem Lebensjahr von
30 bis 110).

**Formel:**
```
Age-graded % = (Weltrekord-Zeit × Altersfaktor) ÷ Deine Zeit × 100
```

**Einordnung der Prozentwerte:**

| Bereich       | Klassifikation       |
|---------------|----------------------|
| ≥ 90 %        | International class  |
| 80–90 %       | National class       |
| 70–80 %       | Regional class       |
| 60–70 %       | Local class          |
| < 60 %        | Recreational         |

**Chart-Inhalt:**
- Vier farbige Linien für 5K, 10K, Halbmarathon, Marathon
- Jeder Datenpunkt = HR-basierte McMillan-Vorhersage aus einem rollenden
  3-Monats-Fenster (gleicher Mechanismus wie die Race-Time-Vorhersagen
  in der Summary-Panel)
- Punktierte Referenzlinien bei 60/70/80/90/100 %
- Tatsächlich gelaufene Rennen (per Rechtsklick auf einen Lauf →
  „Als Rennen markieren") erscheinen als größere Scatter-Punkte mit
  dunklerer Farbe auf ihrer jeweiligen Distanz-Linie — reale Zeiten
  sind belastbarer als die Predictions

**Hinweis:** Die Faktoren sind alters-spezifisch, das Diagramm rechnet
also dein Alter zum jeweiligen Zeitpunkt aus. Ein 5K vor zwei Jahren mit
demselben Tempo erscheint mit *anderem* %-Wert als heute.

#### Sicht 2: Aerobic Capacity %

**Datengrundlage:** Dein eigener Efficiency Factor (EF) über Zeit plus
eine altersbasierte Decline-Modellierung aus der Literatur.

**Methodische Vorabhinweise:**

- Friel (Joe Friel Training) und TrainingPeaks raten **ausdrücklich
  davon ab**, den EF zwischen Athleten zu vergleichen. Wir tun das
  daher *nicht* — die Referenzlinie ist ausschließlich dein eigener
  Bestwert.
- HRmax wird via **Tanaka (2001):** `208 − 0,7 × Alter` geschätzt
  (Meta-Analyse über 351 Studien, n=18.712, gender-unabhängig). Genauer
  als das alte `220 − Alter` ab ungefähr Alter 40.

**Personal-Peak-EF:**
- Bestes 4-Wochen-Mittel deines EF in den letzten 12 Monaten
- Diese Linie ist horizontal eingeblendet (dotted grau)
- Solange dein Trainingsvolumen aufrecht bleibt, sollte der EF in deren
  Nähe pendeln

**Expected-EF-Kurve (gestrichelt orange):**
Fortschreibung vom Peak in die Zukunft mit alters-bedingter
Decline-Rate. Die Rate hängt von deinem aktuellen Trainingsvolumen ab:

| Trainingsstatus                   | Decline pro Jahr |
|-----------------------------------|------------------|
| Volumen aufrechterhalten          | 0,5–0,65 %       |
| Moderate Reduktion (11–20 %)      | 0,8–2,6 %        |
| Sedentär (Reduktion > 20 %)       | 1,5–4,6 %        |

Quelle: [Coppola et al. 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9517884/),
Meta-Analyse longitudinaler Masters-Athleten-Studien. Trainingsvolumen
erklärt 54 %/39 % (Männer/Frauen) der individuellen Decline-Varianz.

**Caveat:** Linearer Decline ist eine **erste Näherung**. Ab ca. 70
Jahren beschleunigt sich der Decline, weil mitochondriale Mechanismen
gegenüber kardialer Output-Reduktion dominanter werden
([Review PMC9975246](https://pmc.ncbi.nlm.nih.gov/articles/PMC9975246/)).
Der lineare Pfad ist unter 70 belastbar.

**Header-Zeile:**
```
Current EF: 24.3 • 96% of age-adjusted peak • Decline rate ~0.7%/yr (vol ratio 0.95)
```

- **Current EF:** Dein aktueller EF × 1000 (gleiche Einheit wie der
  Heart-Rate-Tab)
- **% of age-adjusted peak:** Wie nahe du an deinem alters-adjustierten
  Peak bist
- **Decline rate:** Die aktuell angewandte Decline-Rate (kommt aus
  deinem Volumen-Verhältnis)
- **Vol ratio:** Aktuelles Volumen ÷ Peak-Volumen

#### Interpretation

- Beide Sichten **rangieren** Form über Zeit — keine ist „besser".
- WMA ist gut für **Wettkampf-Vergleich** (Wie würde ich in einer
  Masters-Klasse abschneiden?).
- HF ist gut für **Trainings-Response** (Reagiere ich gerade auf mein
  Training? Hänge ich hinter meinem Potenzial zurück?).

#### Quellen

- [WMA 2023 Age Factors PDF](https://world-masters-athletics.org/wp-content/uploads/2023/02/2023-Age-Factors-WMA.pdf)
- [Howard Grubb's WMA-2023-Calculator + Excel-Daten](https://howardgrubb.co.uk/athletics/wmatnf23.html)
- [Tanaka et al. (2001), „Age-predicted maximal heart rate revisited"](https://pubmed.ncbi.nlm.nih.gov/11153730/) — *J Am Coll Cardiol* 37(1)
- [Coppola et al. (2022), „Impact of Training on the Loss of CRF in Aging Masters Endurance Athletes"](https://pmc.ncbi.nlm.nih.gov/articles/PMC9517884/) — *Int J Environ Res Public Health* 19(17)
- [Joe Friel — Efficiency Factor in Running](https://joefrieltraining.com/the-efficiency-factor-in-running-2/)

---

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
- **Sync Activities**: Aktivitäten von Strava herunterladen (aktiviert wenn verbunden)
- **Disconnect Strava & Delete All Data**: Vollständige Trennung und Datenlöschung (aktiviert wenn verbunden)
  - **Was wird gemacht:**
    - Entfernt RunTrend aus deinen autorisierten Strava-Apps (ruft Stravas Deautorisierungs-Endpunkt auf)
    - Löscht alle synchronisierten Aktivitäten von deinem Gerät
    - Löscht alle OAuth-Tokens
    - Behält deine API-Anmeldedaten, damit du dich später wieder verbinden kannst
  - **Warnung**: Diese Aktion kann nicht rückgängig gemacht werden! Du erhältst einen Bestätigungsdialog, der genau zeigt, was gelöscht wird
  - **Datenschutz**: Deine Daten werden nur lokal gespeichert. Diese Löschung entfernt sie vollständig von deinem Gerät
  - **Wiederherstellen**: Nach der Löschung kannst du dich jederzeit wieder verbinden. Deine Strava-Daten bleiben auf Stravas Servern erhalten
  - **Manuelle Alternative**: Du kannst RunTrends Zugriff auch unter https://www.strava.com/settings/apps widerrufen
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

## Häufig gestellte Fragen

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

### Was ist ACWR und warum ist es wichtig?

**ACWR** = **Acute:Chronic Workload Ratio** - eine wissenschaftlich validierte Metrik, die deine aktuelle Trainingsbelastung (akut) mit deiner Baseline-Trainingsbelastung (chronisch) vergleicht, um Übertrainings-Risiko zu erkennen.

**Warum es wichtig ist:**
- **Verhindert Verletzungen**: ACWR > 1,5 = 2-4x höheres Verletzungsrisiko
- **Optimiert Training**: Halte ACWR im 0,8-1,3 Bereich (sichere Zone)
- **Erkennt Spitzen früh**: Warnt dich BEVOR Verletzung auftritt
- **Wissenschaftlich validiert**: Basiert auf peer-reviewed Forschung (Gabbett et al. 2016)

**Wie es funktioniert:**
```
ACWR = Akute Belastung (letzte Woche) / Chronische Ø-Belastung (vorherige 4 Wochen)

Beispiel:
Letzte Woche: 30 km
Vorherige 4 Wochen: 22, 24, 23, 25 km (Ø: 23,5 km)
ACWR = 30 / 23,5 = 1,28 (SICHER Zone)
```

**RunTrends Verbesserung:**
Statt nur Distanz berechnet RunTrend ein **kombiniertes ACWR** mit:
- Distanz (40%)
- Pace (30%)
- Herzfrequenz (30%)

Dies gibt dir ein vollständiges Bild des Trainingsstresses.

**Wo du es findest:**
- **Zusammenfassungspanel**: Zeigt aktuellen Training Load Score (0-100) und Status
- **Training Load Tab**: Chart mit farbigen Sicherheitszonen
- **Metriken-Erklärungen**: Vollständige Erklärung von Berechnung und Interpretation

**Siehe auch:** Metriken-Erklärungen → Training Load (ACWR) für detaillierte Erklärung.

### Warum ist mein Training Load Score hoch, obwohl ich die gleiche Distanz laufe?

Training Load (ACWR) berücksichtigt **mehr als nur Distanz**. Ein hoher Score kann auch bei stabiler Distanz auftreten durch:

**1. Pace-Intensität erhöht**
```
Letzte 4 Wochen: 30 km/Woche bei 6:00 min/km
Diese Woche: 30 km/Woche bei 5:30 min/km
→ Gleiche Distanz, aber VIEL höhere Intensität
→ Pace-ACWR = 1,55 (Spitze!)
→ Training Load Score: 78 (VORSICHT)
```

**2. Herzfrequenz erhöht** (Ermüdung/Hitze/Krankheit)
```
Letzte 4 Wochen: Ø HF 150 bpm
Diese Woche: Ø HF 165 bpm (gleiche Pace!)
→ Herz arbeitet härter = höherer physiologischer Stress
→ HF-ACWR = 1,10
→ Kombiniert mit anderen Faktoren → höherer Training Load
```

**3. Kombination mehrerer Faktoren**
```
Kleine Distanzerhöhung (+10%) +
Etwas schnelleres Pace (+5%) +
Leicht erhöhte HF (+3%)
= Kombiniertes ACWR 1,42 → Score 72 (VORSICHT)

Jeder Faktor allein ist klein, aber kombiniert = Spitze!
```

**4. Wettkampfaufwand**
```
Woche 1-4: 35 km leichtes Tempo
Woche 5: 35 km inkl. 10K Wettkampfaufwand
→ Distanz gleich, aber Wettkampf = HOHE Intensität + HF-Spitze
→ Training Load Score: 85 (WARNUNG)
```

**Was tun:**
- Prüfe **Training Load Chart** um zu sehen, welche Komponente gestiegen ist
- Betrachte **Pace Chart**: Hat sich Pace zu schnell verbessert?
- Betrachte **HF Chart**: Steigt durchschnittliche HF?
- Nutze **RoC-Overlays** um zu sehen, ob Trends zu steil sind
- Falls Score hoch: Halte aktuelle Belastung, priorisiere Erholung

**Denke daran:** Training Load schützt dich durch Erkennung ALLER Formen von Trainingsstress, nicht nur Volumen.

### Was soll ich tun, wenn mein Training Load in der WARNUNG Zone ist?

Ein **WARNUNG Zone** Score (80-90) zeigt HOHES Verletzungsrisiko - sofortige Aktion erforderlich!

**Schritt 1: Keine Panik**
- Ein WARNUNG Score ≠ garantierte Verletzung
- Es ist ein Frühwarnsystem
- Du hast es rechtzeitig erkannt - das ist der Sinn!

**Schritt 2: Sofortige Aktion (Nächste 3-5 Tage)**
```
✓ Reduziere Volumen der nächsten Woche um 20-30%
✓ Nur leichte Läufe (kein Speedwork, kein Tempo)
✓ Bei Schmerz/ungewöhnlichem Muskelkater: Sofort Ruhetag einlegen
✗ Setze geplante Progression nicht fort
✗ Keine Wettkämpfe oder harten Workouts
```

**Beispiel:**
```
Aktuelle Woche: 50km → Score 85 (WARNUNG)
Nächste Woche Plan: 55km → STOPP! Zu riskant

Besser:
Nächste Woche: 35-40km leichtes Tempo
Woche danach: 40-45km (falls Score auf GRÜN fällt)
Dann: Schrittweiser Wiederaufbau fortsetzen
```

**Schritt 3: Erholungswochen-Strategie**
```
Fokus auf:
✓ Schlaf: 8+ Stunden pro Nacht
✓ Ernährung: Ausreichend Protein, Hydration
✓ Ruhetage: 1-2 extra Ruhetage einplanen
✓ Leichtes Tempo: Alle Läufe konversationsfähig (kannst normal reden)
✓ Stressreduzierung: Minimiere Lebensstress falls möglich
```

**Schritt 4: Fortschritt überwachen**
```
Nach Erholungswoche:
- Prüfe Training Load im Zusammenfassungspanel
- Score auf 50-65 (GRÜN) gefallen? → Training fortsetzen
- Score noch 70+? → Weitere leichte Woche nötig
```

**Schritt 5: Zukünftige Spitzen verhindern**
```
Künftig:
✓ Plane Erholungswochen alle 3-4 Wochen (20-30% Volumenreduzierung)
✓ Nach Wettkämpfen: IMMER Erholungswoche einplanen
✓ Nutze RoC-Overlays um zu sehen, ob Progression zu steil ist
✓ Höre auf Körper: Ermüdung + hoher Training Load = extra Ruhe
```

**Wann zum Arzt:**
```
🚨 Anhaltender Schmerz, der sich mit Ruhe nicht verbessert
🚨 Erhöhte Ruhe-HF (+10 bpm) für mehrere Tage
🚨 Extreme Ermüdung trotz ausreichend Ruhe
🚨 Häufige Krankheiten/wiederholt krank werden
🚨 Motivationsverlust länger als 2 Wochen
→ Dies sind Übertrainings-Syndrom Symptome - suche ärztlichen Rat
```

**Erfolgsgeschichte Beispiel:**
```
Woche 1-4: Score 52-58 (GRÜN)
Woche 5: Score 82 (WARNUNG) - früh erkannt!
Woche 6: Auf 30 km leicht reduziert → Score 54 (GRÜN)
Woche 7: 38 km → Score 58 (GRÜN)
Woche 8: 42 km → Score 62 (GRÜN) - zurück auf Kurs!

Ergebnis: Verletzung durch Reaktion auf Warnung vermieden
```

**Siehe auch:** Training Load Tab → Wie den Chart interpretieren für detaillierte Anleitung.

### Warum wird ACWR nicht für die aktuelle Woche angezeigt?

ACWR wird nur für **vollständige Perioden** berechnet um Genauigkeit sicherzustellen. Du siehst keinen Training Load Score für die aktuelle Woche/Monat bis sie abgeschlossen ist.

**Warum nur vollständige Perioden?**
```
Beispiel (Ansicht am Mittwoch):
Mo-Di: 15 km bisher gelaufen
Verbleibend Mi-So: Unbekannt

Würden wir ACWR jetzt berechnen:
→ Akute Belastung = 15 km (unvollständig!)
→ ACWR würde 15/23 = 0,65 (Untertraining) zeigen
→ Irreführend! Du könntest bis Sonntag 30 km gesamt laufen

Lösung: Warte bis Sonntag um tatsächliches wöchentliches ACWR zu berechnen
```

**Was du stattdessen siehst:**
```
Im Zusammenfassungspanel:
Training Load: 52 (SICHER) ← Letzte abgeschlossene Woche
Status: "SICHER - Schrittweise progressive Überlastung"

Im Training Load Chart:
Graph zeigt bis letzten Sonntag (abgeschlossene Woche)
Aktuelle Woche (Mo-heute) wird NOCH NICHT gezeigt
```

**Wie dies nutzen:**
Nutze **Score der letzten Woche** zur Steuerung **DIESER Woche**:

```
Letzte Woche: Score 75 (VORSICHT)
Diese Woche: Halte Volumen konservativ, erhöhe nicht
Nächste Woche: Prüfe ob Score gefallen ist vor Fortsetzung Progression

Letzte Woche: Score 52 (SICHER)
Diese Woche: Kannst geplante Progression fortsetzen
```

**Wann sehe ich ACWR der aktuellen Woche?**
```
Wöchentliche Aggregation:
- Montag 00:00: Letzte Woche wird "vollständig"
- Zusammenfassungspanel aktualisiert mit Score letzter Woche
- Chart fügt Datenpunkt letzter Woche hinzu

Monatliche Aggregation:
- 1. des Monats 00:00: Letzter Monat wird "vollständig"
- Scores aktualisieren mit Daten letzten Monats
```

**Workaround für Bewusstsein während der Woche:**
Nutze **RoC-Overlays** auf Distanz/Pace/HF-Charts:
- Zeigt ob aktueller Trend zu steil ist
- Vorausschauender Indikator (im Gegensatz zu ACWR, das nachlaufend ist)
- Beispiel: Distanz-RoC +4 km/Woche = aggressiv (wird wahrscheinlich hohes ACWR auslösen)

**Best Practice:**
```
✓ Überprüfe Training Load jeden Montagmorgen (wöchentlich)
✓ Überprüfe Training Load jeden 1. des Monats (monatlich)
✓ Nutze Score letzter Woche zur Planung DIESER Woche
✓ Nutze RoC-Trends um steile Progressionen früh zu erkennen
✗ Erwarte kein Echtzeit-ACWR während der Woche
```

**Siehe auch:** Metriken-Erklärungen → Training Load (ACWR) → Anforderungen

### Was ist Rate of Change (RoC) und wie nutze ich es?

**Rate of Change (RoC)** ist ein Trendindikator, der zeigt wie schnell sich eine Metrik über Zeit ändert durch rollierend 8-Perioden lineare Regression.

**Wo du es findest:**
- Distance Chart: "Show Rate of Change" Checkbox
- Pace Chart: "Show Rate of Change" Checkbox
- Heart Rate Chart: "Show Rate of Change" Checkbox

**Was es zeigt:**
```
Distanz-RoC: Wie schnell sich deine wöchentliche/monatliche Distanz ändert
- Beispiel: +2 km/Woche = durchschnittlich 2 km pro Woche hinzufügen

Pace-RoC: Wie schnell sich dein Pace verbessert/verschlechtert
- Beispiel: -0,05 min/km pro Woche = 3 Sek/km schneller jede Woche

HF-RoC: Wie schnell sich deine durchschnittliche Herzfrequenz ändert
- Beispiel: +2 bpm/Woche = HF steigt um 2 Schläge pro Woche
```

**Wie es lesen:**
```
Lila gestrichelte Linie im Chart:
- Linie über Null: Metrik steigt
- Linie unter Null: Metrik sinkt
- Flache Linie nahe Null: Metrik ist stabil
- Steile Steigung: Schnelle Änderung
- Sanfte Steigung: Graduelle Änderung
```

**Praktische Beispiele:**

**Beispiel 1: Nachhaltiger Volumenaufbau**
```
Distance Chart mit RoC aktiviert:
Wochen 1-8: Distanz steigt von 20→34 km
RoC-Linie: +1,5 km/Woche (graduelle positive Steigung)
Training Load: 55 (SICHER)
→ Interpretation: Nachhaltige Progression ✓
```

**Beispiel 2: Zu aggressive Progression**
```
Distance Chart mit RoC aktiviert:
Wochen 1-4: Distanz springt von 25→45 km
RoC-Linie: +4 km/Woche (steile positive Steigung)
Training Load: 82 (WARNUNG)
→ Interpretation: Zu aggressiv! ⚠
→ Aktion: Progression auf +1-2 km/Woche abflachen
```

**Beispiel 3: Pace-Verbesserung**
```
Pace Chart mit RoC aktiviert:
Monate 1-6: Pace verbessert sich von 6:00→5:30/km
RoC-Linie: -0,08 min/km pro Monat (negativ = schneller werdend)
Training Load: 58 (SICHER)
→ Interpretation: Schöne stetige Verbesserung ✓
```

**Beispiel 4: HF-Ermüdungswarnung**
```
HR Chart mit RoC aktiviert:
Wochen 1-8: Avg HF steigt von 150→158 bpm (gleiche Pace!)
RoC-Linie: +1 bpm/Woche (positive Steigung)
Training Load: 72 (VORSICHT)
→ Interpretation: Ermüdung sammelt sich an ⚠
→ Aktion: Erholungswoche nötig
```

**Nutzung mit Training Load:**
```
RoC ist VORAUSSCHAUEND:
- Zeigt Trends BEVOR sie Training Load Warnungen auslösen
- Steiler Distanz-RoC → Wird wahrscheinlich bald hohen Training Load verursachen
- Nutze RoC um Progression anzupassen bevor ACWR steigt

Training Load ist RÜCKSCHAUEND:
- Zeigt Spitze NACHDEM sie passiert ist
- Sagt dir, Belastung als Reaktion zu reduzieren

Best Practice: Nutze BEIDE
1. Überwache RoC-Trends wöchentlich
2. Falls RoC zu steil → passe Progression proaktiv an
3. Falls Training Load trotzdem steigt → Erholungswoche
```

**Wann RoC am nützlichsten ist:**
```
✓ Planung von Volumenprogression (ist +3 km/Woche zu viel?)
✓ Verfolgung von Pace-Verbesserungs-Trends (stagniere ich?)
✓ Erkennung schleichender HF-Ermüdung (subtiles Warnsignal)
✓ Validierung von Erholungswochen (RoC sollte sich abflachen/umkehren)
✓ Verstehen warum Training Load gestiegen ist (steiler RoC = Ursache)
```

**Einschränkungen:**
```
- Benötigt 8+ vollständige Perioden für Berechnung
- Ersten 7 Perioden zeigen keinen RoC (nicht genug Daten)
- Empfindlich gegenüber Ausreißern (ein Wettkampf kann Trend verzerren)
- Zeigt Rate, nicht absolute Werte (nutze mit Hauptmetrik)
```

**Tipp:** Aktiviere RoC wenn du die "Geschichte" hinter deinen Trainingstrends verstehen möchtest - baust du zu schnell auf, stagnierst du, oder progressierst du ideal?

**Siehe auch:**
- Distance Chart → Rate of Change Overlay
- Pace Chart → Rate of Change Overlay
- Heart Rate Chart → Rate of Change Overlay

### Kann ich RunTrend ohne Herzfrequenzmesser nutzen?

**Ja!** RunTrend funktioniert hervorragend ohne Herzfrequenzdaten - viele Features benötigen keine HF.

**Features die OHNE HF funktionieren:**

**✓ Zusammenfassungspanel:**
- Gesamtdistanz, Pace, Frequenz, Längster Lauf
- Training Score (angepasste Gewichtung ohne EF-Komponente)
- Training Load (ACWR) - nutzt nur Distanz + Pace (HF wird auf 1,0 gesetzt)
- Marathon-Meilenstein
- Race Time Predictions (nur auf Pace basierend)

**✓ Charts - Overview Tab:**
- Distance Chart (mit RoC-Overlay)
- Pace/Speed Chart (mit RoC-Overlay)
- Frequency Chart

**✓ Charts - Endurance Tab:**
- Longest Run Chart
- Average Distance per Run Chart

**✓ Charts - Score Tab:**
- Training Score (angepasste Formel)

**✓ Charts - Training Load Tab:**
- Training Load Chart (nur Distanz + Pace Komponenten)
- Farbige Sicherheitszonen funktionieren noch

**✓ Charts - Projection Tab:**
- Volume Projection
- Long Run Projection
- Meilenstein-Vorhersagen

**Features die HF-Daten BENÖTIGEN:**

**✗ Heart Rate Tab:**
- Zeigt "No HR data available" Meldung
- HR Range, Average HR, Efficiency Factor nicht verfügbar

**✗ Efficiency Factor:**
- Wird ohne HF nicht berechnet
- Training Score nutzt angepasste Gewichtung (keine EF-Komponente)

**✗ HF-spezifische Training Load Komponente:**
- ACWR HF-Komponente wird auf 1,0 (neutral) gesetzt
- Training Load funktioniert noch, ist aber etwas weniger genau

**Angepasste Metriken ohne HF:**

**Training Score Gewichtung:**
```
Mit HF:
- 30% Distanz
- 30% Pace
- 20% Efficiency Factor
- 20% Frequenz

Ohne HF (automatische Anpassung):
- 37,5% Distanz
- 37,5% Pace
- 0% Efficiency Factor (nicht berechnet)
- 25% Frequenz
→ Gesamt noch 100%, Gewichte proportional angepasst
```

**Training Load (ACWR) ohne HF:**
```
Kombiniertes ACWR = (Distanz-ACWR × 50%) +
                    (Pace-ACWR × 50%) +
                    (1,0 × 0%)  ← HF wird auf neutral gesetzt

Erkennt noch:
✓ Volumenspitzen (Distanz-ACWR)
✓ Intensitätsspitzen (Pace-ACWR)
✗ Physiologischer Stress (HF-ACWR fehlt)

Noch nützlich! Erkennt die meisten Übertrainings-Risiken.
```

**Vorteile durch Hinzufügen eines HF-Messers:**
```
Mit HF-Messer gewinnst du:
✓ Efficiency Factor (bester Indikator für aerobe Fitness)
✓ HR Range Visualisierung (Trainingsintensitäts-Verteilung)
✓ Genauerer Training Load (beinhaltet physiologischen Stress)
✓ Frühe Ermüdungserkennung (steigende HF bei gleicher Pace)
✓ Besserer Training Score (beinhaltet Fitness-Komponente)

Empfohlene Geräte:
- Brustgurt: Am genauesten (Garmin HRM-Dual, Polar H10)
- Optisch am Handgelenk: Bequem aber weniger genau (in den meisten Sportuhren eingebaut)
- Strava importiert HF automatisch von kompatiblen Geräten
```

**Empfehlung:**
```
Anfänger (0-6 Monate Laufen):
→ Starte ohne HF-Messer, fokussiere auf Konsistenz
→ RunTrend bietet viele Einblicke nur aus Distanz/Pace

Fortgeschritten (6-12 Monate):
→ Erwäge Hinzufügen eines HF-Messers
→ Efficiency Factor wird sehr wertvoll
→ Bessere Übertrainings-Erkennung

Erfahren/Marathon-Training:
→ HF-Messer sehr empfohlen
→ Training Load mit HF = viel genauer
→ Erkenne Ermüdung früher
```

**Fazit:** RunTrend ist voll funktionsfähig ohne HF, aber HF-Daten fügen signifikanten Wert für seriöse Trainingsoptimierung hinzu.

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
