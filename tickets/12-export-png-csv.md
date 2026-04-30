# 12 — Export: Charts als PNG, Daten als CSV

**Priorität:** P1
**Kategorie:** Erweiterung

## Problem

Nutzer möchten ihre Trends teilen (Trainingspartner, Coach) oder selbst weiterverarbeiten
(Excel, externe Analyse). Aktuell gibt es keinen Export.

## Auswirkung auf Nutzer

- Screenshots als Workaround sind qualitativ schlecht und unvollständig
- Daten-Export aus SQLite manuell ist zu technisch für Endnutzer

## Lösungsansatz

### Chart-Export (PNG)

Kontextmenü auf jedem Chart oder Button in Toolbar:
- „Export Chart as PNG…" → File-Dialog
- `QChart::grab()` (oder `QChartView::grab()`) gibt `QPixmap`, dann `pixmap.save(path)`

### Daten-Export (CSV)

Datei-Menü → „Export Activities as CSV…"
- Nutzt aktuellen Date-Filter und Activity-Filter (Treadmill/Manual)
- Spalten: Datum, Distanz, Dauer, Pace, Avg-HR, Max-HR, Höhenmeter, Trainer, Manual

Optional: zusätzlich PDF mit allen Charts auf einer Seite („Trend Report").

## Acceptance

- [x] Rechtsklick auf Chart → „Export as PNG"
- [x] Datei-Menü „Export Data as CSV…" exportiert gefilterte Aktivitäten
- [x] Default-Dateiname mit Datum (`runtrend_export_2026-04-30.csv`)
- [x] Übersetzt (DE/EN)

## Annahmen

- **PNG-Export-Hook:** Kontextmenü-Wiring liegt in
  `BaseChart._wrap_chart_view_with_empty_state`, nicht in
  `_setup_chart_view`. Grund: nicht alle Chart-Subklassen rufen
  `_setup_chart_view` (z.B. `DistanceChart`, `PaceChart`,
  `HeartRateChart`, `ProjectionChart` etc. bauen `chart_view`
  selbst). `_wrap_chart_view_with_empty_state` wird aber von jeder
  Chart aufgerufen — eine einzige Touchpoint-Stelle versorgt damit
  alle 13 Chart-Klassen ohne Subklassen-Änderungen.
- **PNG-Dateiname:** `runtrend_<chart-slug>_<YYYY-MM-DD>.png`,
  Slug aus `chart.title()` mit nicht-alphanumerischen Zeichen
  durch `_` ersetzt und lowercase. Beispiel: „Distance Progress"
  → `runtrend_distance_progress_2026-04-30.png`. Nutzer kann den
  Vorschlag im FileDialog überschreiben; fehlende `.png`-Endung
  wird ergänzt.
- **PNG-Methode:** `QChartView.grab()` liefert ein `QPixmap` mit
  dem aktuell sichtbaren Chart inkl. Legende und Achsen — exakt
  wie auf dem Bildschirm. Keine separate Render-Auflösung; das
  Ticket fordert sie nicht.
- **Datei-Menü:** wirklich ein neues `QMenuBar` mit `&File` /
  `&Datei` (Tastatur-Shortcut Alt+F / Alt+D). Bisher hatte
  `MainWindow` keine Menüleiste — das Menü wird in
  `_setup_menu` vor `_setup_toolbar` initialisiert.
- **CSV-Spalten** (fester Reihenfolge per `CSV_COLUMNS`):
  `date, distance_km, duration_s, pace_min_per_km, avg_hr_bpm,
  max_hr_bpm, elevation_gain_m, trainer, manual`. Spec-Mapping:
  „Datum"=date (ISO), „Distanz"=distance_km (3 Nachkommastellen),
  „Dauer"=duration_s (Sekunden statt HH:MM:SS — maschinen-
  freundlicher), „Pace"=pace_min_per_km (3 Nachkommastellen, leer
  bei distance=0), „Avg-HR"/„Max-HR"=`average_heartrate` /
  `max_heartrate` (leer bei None), „Höhenmeter"=elevation_gain_m
  (0 bei None — damit Tabellen-Summen funktionieren),
  „Trainer"/„Manual"=0/1.
- **Filter-Beachtung:** `_export_activities_csv` exportiert
  `self.activities`, das bereits durch `start_date_edit` und die
  Treadmill-/Manual-Settings vorgefiltert ist (siehe
  `_load_data:632-636`) — entspricht dem Ticket-Wortlaut „Nutzt
  aktuellen Date-Filter und Activity-Filter".
- **Empty-State:** Klick auf „Export Data as CSV…" ohne geladene
  Aktivitäten zeigt einen Info-Dialog statt einer leeren CSV.
- **PDF-Optional:** das Ticket erwähnt PDF-„Trend Report" als
  Optional. Nicht umgesetzt — gehört nicht zur AC. Eigenes
  späteres Ticket bei Bedarf.
- **Tests:** `tests/test_exporter.py` mit 7 Tests deckt
  Header/Spalten-Reihenfolge, Pace-Berechnung, fehlende HR/Höhe,
  Zero-Distanz, Mehrzeiligkeit, Trainer/Manual-Flags und den
  Default-Dateinamen ab. PySide-freier Unit-Test, läuft offline.
  `pytest tests/` 124 passed.
- Übersetzungen für 13 neue Strings in beiden `.ts`-Dateien;
  `lrelease` regeneriert beide `.qm` (272 DE / 267 EN finished).

## Dateien

- `run_trend/ui/main_window.py` (Menüleiste, `_setup_menu`,
  `_export_activities_csv`)
- `run_trend/charts/base_chart.py` (Kontextmenü +
  `_export_chart_png`)
- `run_trend/io/__init__.py`, `run_trend/io/exporter.py` (CSV)
- `tests/test_exporter.py` (neuer Test-File)
- `run_trend/translations/runtrend_de.ts`, `runtrend_en.ts`,
  `runtrend_de.qm`, `runtrend_en.qm`
