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
- ✅ `StravaClient.get_activity_streams(activity_id, keys=['heartrate','time'])`:
  ruft `/activities/{id}/streams?key_by_type=true` auf, verlangt Scope
  `activity:read_all` (haben wir bereits), gibt
  `{stream_key: [datapoints…]}` zurück oder `None` (bei API-Fehler oder
  fehlendem Stream). Malformed Einträge werden silenced gedroppt.
- ✅ DB-Cache-Tabelle `activity_hr_zones` mit Spalten
  `strava_id PK, z1..z5_seconds, hr_max_used, hr_rest_used (NULL),
  scheme, computed_at`. CRUD: `upsert_activity_hr_zones`,
  `get_activity_hr_zones`, `invalidate_activity_hr_zones(hr_max=,
  hr_rest=, scheme=)` — letzteres droppt Rows, deren gespeicherte Config
  vom übergebenen Soll-Wert abweicht (Strategie für Settings-Änderungen
  in der nächsten Slice).
- ✅ Tests: `tests/test_strava_streams.py` (6 Tests, gepatcht über
  `_make_request`-Mock) und `tests/test_hr_zones_storage.py` (8 Tests
  inkl. Idempotenz-Reopen, Replace-Verhalten, Karvonen-Persistenz,
  Length-Validation, Invalidate-Pfade).
- ✅ Settings-UI: General-Tab erweitert um Resting-HR-Spinbox (0 = unset),
  Zonenschema-Combo (Classic / Karvonen). Save validiert Karvonen
  (`hr_rest > 0 AND hr_max > 0 AND hr_rest < hr_max`) mit
  QMessageBox.warning + Early-Return. Bei Änderung von HR-Max/HR-Rest/Scheme
  wird `Database.invalidate_activity_hr_zones(...)` über das MainWindow
  getriggert — Lazy-Refill bei der nächsten Cache-Anfrage.
- ✅ Settings-Defaults: `hr_rest=0`, `hr_zone_scheme='classic'` werden über
  `AppSettings.get(..., default)` aufgelöst (ohne neue DEFAULTS-Einträge —
  konsistent mit `manual_hrmax`, das ebenfalls implizit per `get(..., 0)`
  aufgelöst wird).
- ✅ Übersetzungen: 9 neue Strings (Resting Heart Rate / Ruhepuls,
  Not set / Nicht gesetzt, Tooltips, Zone Scheme / Zonenschema,
  Classic + Karvonen Combo-Items, Karvonen-Validation-Messagebox).
  `.qm` regeneriert (356 DE / 351 EN).
- ✅ Tests in `tests/test_settings_dialog_hr.py` (7 Tests: Defaults,
  Persistenz-Roundtrip, Karvonen-Block bei fehlendem HR-Rest,
  Karvonen-Block bei `hr_rest >= hr_max`, Cache-Invalidation,
  Cache-Persistenz wenn unverändert, Classic-Save-Pfad).
- ⏳ Chart + Aggregations-Ansicht + 80/20-Indikator + Lazy-Fetch-Pipeline —
  Folgeiteration

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

### Annahmen Streams + Cache

- `key_by_type=true` an Strava: liefert `{key: {data: [...]}}`-Dict statt
  Liste — spart Client-seitiges Reshaping.
- Cache-Schlüssel ist `strava_id` (PRIMARY KEY); pro Aktivität existiert
  also höchstens eine Zeile. Re-Compute bei Settings-Änderung wird über
  `invalidate_activity_hr_zones(...)` getriggert, das Rows mit nicht
  passendem `hr_max_used`/`hr_rest_used`/`scheme` löscht — kein
  Bulk-Recompute, sondern Lazy-Refill bei nächstem Request.
- `hr_rest_used` ist NULLABLE: `classic`-Zonen brauchen keinen Wert. In
  `invalidate(hr_rest=X)` matched eine Zeile mit `NULL` immer
  „inkonsistent" und wird gelöscht — sicherer Default.
- Kein Foreign-Key-Constraint auf `activities.strava_id`: löschende
  Sync-Pfade müssen den Cache nicht explizit pflegen, und Stale-Rows ohne
  zugehörige Aktivität schaden nichts (werden auf Read ignoriert).

### Annahmen Settings-UI

- HR-Rest-Range 0..200 (statt der ursprünglich gedachten 0..120): Validation
  erfolgt im Save-Pfad, nicht hart über die Spinbox. Damit lässt sich auch
  ein bewusst falscher Wert testen, ohne dass die UI ihn vorab clampt.
- HR-Zonen-Settings sind Single-User-Properties — sie werden im
  `AppSettings`-JSON persistiert, nicht in der DB. Konsistent mit
  `manual_hrmax`. Damit greift `invalidate_activity_hr_zones` weiterhin als
  zentraler Cache-Refresh-Punkt, ohne Settings-Trigger in der DB selbst.
- Karvonen-Validation greift nur auf dem Save-Pfad. Wer das Schema während
  einer Sitzung im Combo wechselt, bekommt keinen Inline-Hint — der
  „Save"-Button ist die natürliche Commit-Grenze, dort ist die Warnung
  reichhaltig genug.
