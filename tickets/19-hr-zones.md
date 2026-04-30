# 19 — HR-Zonen-Auswertung mit Zeit-in-Zone

**Priorität:** P2
**Kategorie:** Feature

## Problem

Heart-Rate-Daten werden importiert (avg, max), aber nicht in **Zonen** ausgewertet.
Eine zentrale Trainingsmetrik („80/20-Regel": 80% Zeit in Zone 1–2, 20% in Zone 4–5)
fehlt komplett.

## Lösungsansatz

### Konfiguration

Settings-Dialog → Tab „Connection" oder neuer Tab „Profile":
- Geburtsdatum oder direkt **HR-Max** (Default: 220 - Alter)
- Zonen-Schema (5 Zonen klassisch oder Karvonen)
- Optional: Resting-HR

### Berechnung

Pro Lauf: Streamfetch über Strava-API (`/activities/{id}/streams?keys=heartrate,time`)
und Aggregation in Sekunden pro Zone. Cache pro Aktivität in DB.

**Hinweis**: Streams-Endpoint braucht zusätzliche OAuth-Scope `activity:read_all` (haben
wir schon) — pro Activity ein extra API-Call. Bei initial-sync potenziell teuer →
Lazy-Fetch nur wenn HR-Zonen-Tab geöffnet wird.

### UI

Neuer Tab oder Karte:
- **Pro Lauf**: Stacked-Bar mit Sekunden in jeder Zone
- **Aggregiert**: Wochen-/Monatssumme als Stacked-Bar oder Pie-Chart
- 80/20-Indikator: prozentualer Anteil in Z1–Z2 vs. Z3–Z5

## Acceptance

- [ ] HR-Max konfigurierbar
- [ ] Streams werden nachgeladen und gecached (kein Re-Fetch beim erneuten Öffnen)
- [ ] Pro-Lauf und aggregierte Ansicht
- [ ] 80/20-Indikator
- [ ] Funktioniert auch ohne HR-Daten (Empty-State)
- [ ] Übersetzt (DE/EN)

## Dateien

- `run_trend/strava/client.py` (Streams-Endpoint)
- `run_trend/storage/database.py` (HR-Zonen-Tabelle/Cache)
- `run_trend/analytics/hr_zones.py` (neu)
- neuer Chart in `run_trend/charts/`
- `run_trend/ui/settings_dialog.py` (HR-Max-Config)

## Status / Fortschritt

**Teilweise umgesetzt — Analytics-Kern fertig, Strava-Streams + DB-Cache + UI
noch offen.**

Das Ticket wird in Slices gemerged. Erste Iteration: pure Analytics-Funktionen
ohne I/O.

- ✅ `run_trend/analytics/hr_zones.py`: 5-Zonen-Klassik (`% × HR-Max`) +
  Karvonen (`pct × (HR-Max − HR-Rest) + HR-Rest`), `compute_zone_bounds`,
  `zone_for_bpm` (low inclusive, high exclusive, top-zone clamp),
  `time_in_zones` aus paired heartrate/time streams (left-edge dt-Aggregation,
  konsistent mit Strava-Stream-Semantik), `aggregate_zone_seconds` für
  Wochen-/Monatssummen, `polarized_ratio` (80/20-Indikator: low=Z1+Z2,
  middle=Z3, high=Z4+Z5).
- ✅ `tests/test_hr_zones.py`: 16 Tests (Bounds, Karvonen-Validierung,
  Zone-Klassifikation, Below-Z1-Drop, Mismatched-Length-Raise, Aggregation,
  Polarized-Fraktion, Empty-Safe).
- ⏳ Strava-Streams-Endpoint (`get_activity_streams`) — Folgeiteration
- ⏳ DB-Cache-Tabelle `activity_hr_zones` — Folgeiteration
- ⏳ Settings-UI für HR-Max + HR-Rest + Schema-Wahl — Folgeiteration
- ⏳ Chart + Aggregations-Ansicht + 80/20-Indikator — Folgeiteration

### Annahmen Analytics-Kern

- Klassisches 5-Zonen-Modell als Default; Karvonen optional via
  `scheme="karvonen"` + `hr_rest`. Kein dynamisches Per-User-Schema (Zonen-
  Anzahl bleibt 5) — vereinfacht Chart-Aggregation in späteren Slices.
- Boundary-Konvention: low inclusive, high exclusive (`bpm < high`), oberste
  Zone klemmt nach oben (`bpm ≥ Z5_low ⇒ Z5`). Damit landen kurze Spikes
  über HR-Max nicht in Z-1, sondern bleiben in Z5.
- Stream-Aggregation: Sample i belegt das Intervall `[t_i, t_{i+1})`
  vollständig. Strava liefert Streams mit `time` in Sekunden ab Start; das
  Modul ist davon agnostisch (akzeptiert beliebige monoton-wachsende Time-
  Streams) und gibt Sekunden zurück.
- Samples mit `bpm` unterhalb der untersten Zone (Idle/Pause) werden
  ausgelassen, statt sie auf Z1 zu klemmen — sonst würden Pausen die
  Endurance-Quote künstlich erhöhen.
