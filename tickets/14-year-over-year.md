# 14 — Year-over-Year-Vergleichslinie auf Charts

**Priorität:** P1
**Kategorie:** Erweiterung

## Problem

Nutzer wollen wissen: „Bin ich dieses Jahr schneller/öfter/weiter unterwegs als letztes
Jahr um diese Zeit?" Aktuell muss man Date-Range manuell umstellen und kann nur
sequenziell vergleichen.

## Lösungsansatz

Auf Distanz-, Pace-, Frequency- und Duration-Chart eine Toggle-Option:
„Show previous year" → zweite Linie in gedimmter Farbe mit Daten aus
`current_range - 1 Jahr`.

X-Achse bleibt aktuelles Jahr, Vorjahres-Werte werden auf gleiche Position projiziert
(z.B. Vorjahres-KW 17 wird an aktueller KW 17 angezeigt).

## Acceptance

- [x] Toggle in Toolbar oder Settings („Compare to previous year")
- [x] Vorjahres-Linie mit klar unterschiedlicher Farbe + dashed Style
- [x] Legende zeigt beide Linien
- [x] Nur aktiv wenn genug historische Daten vorhanden (`>= 1 Jahr` zurück)
- [x] Funktioniert auf Distanz-, Pace-, Frequency- und Duration-Chart

## Dateien

- `run_trend/charts/distance_chart.py`, `pace_chart.py`, `frequency_chart.py`,
  `duration_chart.py`
- `run_trend/charts/base_chart.py` (`_add_previous_year_series`-Helper)
- `run_trend/analytics/data_manager.py` (`align_previous_year_aggregates`)
- `run_trend/ui/main_window.py` (Toolbar-Toggle, Vorjahres-Aktivitäten-Fetch)
- `run_trend/translations/runtrend_{de,en}.ts` + `runtrend_de.qm`
- `tests/test_data_manager.py` (Unit-Tests für Date-Shift)

## Annahmen

- Vorjahres-Aggregation läuft über `Database.get_activities_since(start - 1 Jahr)`
  und filtert anschließend in der UI-Schicht auf das genaue Vorjahres-Fenster.
  Eigener Aggregator-Modus war nicht nötig, weil `DataManager.build_aggregates`
  bereits beliebige Activity-Listen verarbeitet.
- Datums-Mapping: Wochen werden um exakt 52 Wochen verschoben (preserves Monday
  alignment mit ISO-Wochen); Monate per `.replace(year=year+1)`. 29.02. fällt
  in Nicht-Schaltjahren auf den 28.02.
- Gewähltes Primär-Mapping pro Chart:
  - Distance → `total_distance_km`
  - Pace/Speed → `weighted_avg_pace_min_per_km` bzw. `avg_speed_kmh`
  - Frequency → `num_runs`
  - Duration → `avg_duration_per_run_min` (auf Minuten-Achse, weil Total-Time
    bereits dashed ist)
- Heart-Rate-Chart bewusst ausgeklammert: AC nennt nur Distanz/Pace/Frequency/Duration.
- Visuelle Unterscheidung: Farbe `#95a5a6` (gedämpftes Grau) + `Qt.DashLine`,
  Width 2 — passt zu allen Theme-Farben und unterscheidet sich von allen
  bestehenden Series-Farben.
- Toggle-Persistenz via `Database`-Setting `ui_compare_prev_year`. Auto-Uncheck
  beim Datenmangel verwendet `blockSignals`, damit das gespeicherte Setting des
  Nutzers nicht überschrieben wird.
