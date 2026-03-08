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

Zeigt aktuelle KPIs:
- Gesamtzahl der Läufe
- Gesamtdistanz
- Aktuelle durchschnittliche Distanz
- Aktuelles durchschnittliches Pace
- Aktueller Training Score
- Marathon-Meilenstein-Schätzung

### Charts (rechts)

Die Charts sind in 4 Hauptkategorien organisiert:

#### 1. Overview Tab
- **Distance**: Gesamtdistanz pro Periode
- **Pace/Speed**: Pace oder Geschwindigkeit
- **Frequency**: Anzahl der Läufe

#### 2. Endurance Tab
- **Longest Run**: Längster Lauf pro Periode
- **Avg Distance/Run**: Durchschnittliche Distanz pro Lauf

#### 3. Score Tab
- **Training Score**: Kombinierter Trainingsfortschritt

#### 4. Projection Tab
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
**Was es ist:** Kombinierte Metrik aus Volumen, Frequenz und Pace-Fortschritt.

**Berechnung:**
```
training_score = (
    0.50 × normalized_distance +
    0.25 × normalized_frequency +
    0.25 × normalized_pace_improvement
) × 50
```

**Komponenten:**
- **50% Distanz**: Trainingsvolumen
- **25% Frequenz**: Trainingskonsistenz
- **25% Pace**: Geschwindigkeitsverbesserung

**Interpretation:**
- 0-25: Niedriges Trainingsniveau
- 25-50: Moderates Training
- 50-75: Gutes Trainingsniveau
- 75-100: Sehr hohes Trainingsniveau

**Wichtig:** Der Score ist eine Zusammenfassung. Er ersetzt NICHT die strukturellen Metriken wie Longest Run oder Average Distance per Run, die separat betrachtet werden sollten.

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

**Komponenten:**
- 50% Distanz
- 25% Frequenz
- 25% Pace-Verbesserung

**Interpretation:**
- Zusammenfassende Metrik
- Zeigt Gesamttrainingsfortschritt
- **Ersetzt NICHT die strukturellen Details**

**Hinweis:** Für Marathon-Vorbereitung schaue auch auf Longest Run und strukturelle Metriken im Endurance Tab.

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
  - **Marathon (42.195 km) Long Run**

**Frage beantwortet:** "Wann kann ich einen Marathon-Distanz-Long-Run laufen?"

**Wichtiger Unterschied:**
Diese beiden Fragen sind NICHT gleich für Marathon-Vorbereitung!

- Wöchentliches Volumen von 42 km bedeutet NICHT, dass du 42 km am Stück laufen kannst
- Ein 30 km Long Run ist spezifischer für Marathon-Readiness

**Beispiel:**
- Athlet A: 50 km/Woche mit 5 × 10 km Läufen, längster: 10 km
- Athlet B: 40 km/Woche mit 1 × 28 km + 2 × 6 km, längster: 28 km

Athlet B ist näher am Marathon-Ziel, obwohl weniger Wochenvolumen!

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
