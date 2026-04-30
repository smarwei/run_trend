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
- [ ] Rechtsklick-Aktion in RunsTable
- [ ] Marker auf allen Zeitachsen-Charts (Distance, Pace, Frequency, Duration, Score,
      Training-Load)
- [ ] Race-Manager-Dialog für Edit/Delete
- [ ] Übersetzt (DE/EN)

## Dateien

- `run_trend/storage/database.py` (neue Tabelle + Migration)
- neuer `run_trend/ui/race_dialog.py`
- `run_trend/ui/runs_table.py` (Kontextmenü)
- alle relevanten Chart-Klassen

## Status / Fortschritt

**Teilweise umgesetzt — DB-Layer fertig, UI noch offen.**

Da T15 mehrere Schichten umfasst (DB, Dialoge, Kontextmenü, Chart-Annotationen),
wird die kleinste zwingende Vorstufe — der DB-Layer — als eigene Iteration
gemerged. Folgeiterationen ergänzen die UI-Teile:

- ✅ DB-Schema `race_markers` + Index `idx_race_markers_date` in
  `_initialize_schema` (idempotent via `CREATE TABLE IF NOT EXISTS`)
- ✅ CRUD: `add_race_marker`, `get_race_markers`, `update_race_marker`,
  `delete_race_marker` mit `created_at`/`updated_at`-Timestamps
- ✅ Tests in `tests/test_database.py` (10 Tests, inkl. Idempotenz, Reihenfolge,
  Partial-Update, NULL-Defaults für optionale Felder)
- ⏳ `RaceDialog` (Name + Distanz + Zielzeit) — Folge-Ticket
- ⏳ Kontextmenü „Mark as Race…" in `RunsTable` — Folge-Ticket
- ⏳ Race-Manager-Dialog (Liste + Edit/Delete) — Folge-Ticket
- ⏳ Vertikale Marker auf allen Zeitachsen-Charts — Folge-Ticket
- ⏳ Übersetzungen DE/EN — mit UI-Teilen

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
