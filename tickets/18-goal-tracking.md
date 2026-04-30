# 18 — Goal-Tracking mit Ist/Ziel-Linie auf Projection-Chart

**Priorität:** P2
**Kategorie:** Feature

## Problem

`ProjectionChart` zeigt aktuell eine Hochrechnung der aktuellen Form auf
Zielwettkampf-Distanzen. Der Nutzer kann aber kein konkretes Ziel hinterlegen
(„Ich will in 12 Wochen einen Halbmarathon unter 1:50 laufen").

## Lösungsansatz

### Datenmodell

Neue Tabelle `goals`:

```sql
CREATE TABLE goals (
    id INTEGER PRIMARY KEY,
    target_distance_km REAL NOT NULL,
    target_time_seconds INTEGER NOT NULL,
    target_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    achieved INTEGER DEFAULT 0
);
```

### UI

- **Goal-Setter** in Settings oder als eigener Dialog: Distanz + Zielzeit + Zieldatum
- **Projection-Chart erweitern**:
  - Aktuelle (gestrichelte) Projektion: weiterhin
  - Zielpunkt: Marker auf Zieldatum
  - Linie vom Heute-Punkt zum Zielpunkt zeigt benötigte Verbesserung
  - Farbe Grün wenn auf Kurs, Rot wenn nicht

### Acceptance-Indikator

- ATM Pace projection (z.B. 5:30) vs. Ziel-Pace (5:12) → Differenz pro Woche

## Acceptance

- [ ] Goal kann gesetzt, bearbeitet, gelöscht werden
- [ ] Projection-Chart zeigt Ziel-Linie bei aktivem Goal
- [ ] Visuelle Unterscheidung „on track" / „off track"
- [ ] Mehrere Goals möglich (z.B. 5K, 10K, HM parallel)
- [ ] Übersetzt (DE/EN)

## Dateien

- `run_trend/storage/database.py` (Tabelle + Migration)
- neuer `run_trend/ui/goal_dialog.py`
- `run_trend/charts/projection_chart.py`
- `run_trend/analytics/race_predictor.py` (ggf. Diff-Berechnung)

## Status / Fortschritt

**Teilweise umgesetzt — DB-Layer fertig, UI noch offen.**

Wie bei T15 wird das Multi-Layer-Ticket in Slices gemerged. Die kleinste
zwingende Vorstufe — der DB-Layer — ist als eigene Iteration drin:

- ✅ DB-Schema `goals` + Index `idx_goals_target_date` in `_initialize_schema`
  (idempotent via `CREATE TABLE IF NOT EXISTS`).
- ✅ CRUD: `add_goal`, `get_goals(include_achieved=True)`, `update_goal`,
  `delete_goal` mit `created_at`/`updated_at`-Timestamps und 0/1 für
  `achieved`.
- ✅ Tests in `tests/test_database.py::TestGoals` (10 Tests, inkl. Idempotenz,
  Reihenfolge nach `target_date`, Partial-Update, `achieved`-Filter,
  Unknown-ID-Fälle).
- ✅ `GoalDialog` (`run_trend/ui/goal_dialog.py`): Distanz-Combo mit Presets
  (5K/10K/15K/Half/Marathon + Custom), QTimeEdit für Zielzeit (HH:mm:ss),
  QDateEdit für Zieldatum (Default: +3 Monate). Edit-Modus prefillt aus
  bestehendem Goal-Dict; bei Custom-Distanz wird automatisch der Combo-Slot
  gewechselt und das Spin-Feld editierbar. `get_data()` liefert das
  serialisierungsfertige Dict.
- ✅ Übersetzungen für GoalDialog (DE/EN, `.ts` + `.qm` regeneriert).
- ⏳ Goal-Manager-Dialog (Liste mit Add/Edit/Delete + Achieved-Toggle) —
  Folgeiteration
- ⏳ MainWindow-Integration (Menüeintrag, Wiring) — Folgeiteration
- ⏳ Projection-Chart-Erweiterung (Zielpunkt + on-track/off-track-Farbe) —
  Folgeiteration

### Annahmen DB-Layer

- `target_distance_km` als `REAL` (nicht Meter), konsistent mit
  `aggregates.total_distance_km` und `race_markers.distance_km`.
- `target_time_seconds` als `INTEGER` Sekunden, konsistent mit
  `Activity.moving_time` und `race_markers.result_time`.
- `achieved` als `INTEGER 0/1` (kein BOOLEAN-Type in SQLite); Default `0` per
  Schema.
- `target_date` als ISO-String — Konsistenz mit `start_date` /
  `race_markers.date`. Validierung erfolgt im UI-Layer.
- `update_goal(id)` ohne weitere Felder gibt `False` zurück (kein
  No-op-UPDATE auf DB) — gleiche Konvention wie `update_race_marker`.
- Sortierung in `get_goals()` aufsteigend nach `target_date`, weil das
  Projection-Chart ohnehin auf der Zeitachse zeichnet.
- Kein `replace_goal` analog zu `replace_race_marker`: alle Goal-Felder sind
  `NOT NULL`, also kein „leeren via Edit"-Fall.
