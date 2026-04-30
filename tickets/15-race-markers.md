# 15 — Race-Marker auf Zeitachsen-Charts

**Priorität:** P1
**Kategorie:** Erweiterung

## Problem

Nutzer wollen Wettkampftage als Anker auf den Trend-Charts sehen — um Zusammenhänge
zwischen Trainingslast und Performance zu erkennen.

## Lösungsansatz

### Datenmodell

Neue SQLite-Tabelle `race_markers`:

```sql
CREATE TABLE race_markers (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    name TEXT NOT NULL,
    distance_km REAL,
    result_time INTEGER,  -- Sekunden
    notes TEXT
);
```

### UI

- **Hinzufügen**: Rechtsklick auf einen Lauf in `RunsTable` → „Mark as Race…" →
  Dialog mit Name + Distanz + Zielzeit
- **Bearbeiten/Löschen**: separater Race-Manager-Dialog (Menü „Manage Races…")
- **Anzeige**: vertikale gedimmte Linien auf allen Zeitachsen-Charts mit
  Tooltip: „Hannover Marathon — 2026-04-12 — 3:45:22"

## Acceptance

- [x] Race-Tabelle wird automatisch migriert (idempotent, wie für trainer/manual gemacht)
- [x] Rechtsklick-Aktion in RunsTable
- [x] Marker auf allen Zeitachsen-Charts (Distance, Pace, Frequency, Duration, Score,
      Training-Load)
- [x] Race-Manager-Dialog für Edit/Delete
- [x] Übersetzt (DE/EN) für alle UI-Teile außer Chart-Marker

## Dateien

- `run_trend/storage/database.py` (neue Tabelle + Migration)
- neuer `run_trend/ui/race_dialog.py`
- `run_trend/ui/runs_table.py` (Kontextmenü)
- alle relevanten Chart-Klassen

## Status / Fortschritt

**Vollständig umgesetzt.**

Da T15 mehrere Schichten umfasst (DB, Dialoge, Kontextmenü, Chart-Annotationen),
wird die kleinste zwingende Vorstufe — der DB-Layer — als eigene Iteration
gemerged. Folgeiterationen ergänzen die UI-Teile:

- ✅ DB-Schema `race_markers` + Index `idx_race_markers_date` in
  `_initialize_schema` (idempotent via `CREATE TABLE IF NOT EXISTS`)
- ✅ CRUD: `add_race_marker`, `get_race_markers`, `update_race_marker`,
  `delete_race_marker` mit `created_at`/`updated_at`-Timestamps
- ✅ Tests in `tests/test_database.py` (10 Tests, inkl. Idempotenz, Reihenfolge,
  Partial-Update, NULL-Defaults für optionale Felder)
- ✅ `RaceDialog` (`run_trend/ui/race_dialog.py`): Name, Datum, Distanz,
  Zielzeit (HH:mm:ss), Notizen — Prefill aus Activity oder Marker, optionale
  Felder werden als `None` zurückgegeben.
- ✅ Kontextmenü „Mark as Race…" in `RunsTable` (rechte-Maus auf Lauf-Reihe)
  emittiert `race_requested(activity)` mit dem Original-Activity-Dict
  (sortierungs-stabil über `Qt.UserRole+1` auf der Date-Zelle).
- ✅ Wiring in `MainWindow._mark_activity_as_race`: öffnet `RaceDialog`,
  persistiert via `db.add_race_marker(...)`, zeigt Status-Toast.
- ✅ Race-Manager-Dialog (`run_trend/ui/race_manager_dialog.py`): Liste aller
  Marker + Add/Edit/Delete-Buttons; Doppelklick öffnet Edit; löschen erfordert
  Bestätigung. Erreichbar über File → „Manage Races…".
- ✅ Neue DB-Methode `replace_race_marker(id, ...)` schreibt alle Felder inkl.
  expliziter NULLs (für Edit-Dialog, der optionale Felder leeren kann);
  `update_race_marker` bleibt unverändert (kompatibel zu bisherigen Tests).
- ✅ Vertikale gedimmte Linien auf allen sechs Zeitachsen-Charts (Distance,
  Pace, Frequency, Duration, Score, Training-Load) via
  `BaseChart.set_race_markers` + `_add_race_markers(axis_x, axis_y)`. Marker
  werden als 1px-`QLineSeries` zwischen `axis_y.min()` und `axis_y.max()`
  gezeichnet — der Race-Name landet automatisch in der Legende, Klick auf
  den Legenden-Eintrag blendet die Linie aus.
- ✅ MainWindow pusht aktuelle Marker bei jedem `_update_charts()` und
  refresht die Charts nach Mark-as-Race / Race-Manager-Aktionen.
- ✅ Übersetzungen für RaceDialog + Kontextmenü + Manager-Dialog (DE/EN,
  `.ts` + `.qm`). Race-Namen sind DB-Inhalt, nicht zu übersetzen.

### Annahmen DB-Layer

- `result_time` als `INTEGER` in Sekunden (konsistent mit `Activity.duration`).
- `distance_km` als `REAL` (nicht Meter), konsistent mit anderen
  `*_km`-Feldern in `aggregates`.
- `notes` ist optional; `distance_km` und `result_time` ebenfalls (manche
  Marker — z.B. „Verletzungspause-Ende" — haben keine Distanz/Zeit).
- `update_race_marker(id)` ohne weitere Felder gibt `False` zurück (kein
  No-op-UPDATE auf DB).
- Sortierung in `get_race_markers()` aufsteigend nach `date`, weil Charts
  von links nach rechts zeichnen.
