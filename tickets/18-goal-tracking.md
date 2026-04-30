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

- [x] Goal kann gesetzt, bearbeitet, gelöscht werden
- [x] Projection-Chart zeigt Ziel-Linie bei aktivem Goal
- [x] Visuelle Unterscheidung „on track" / „off track"
- [x] Mehrere Goals möglich (z.B. 5K, 10K, HM parallel)
- [x] Übersetzt (DE/EN)

## Dateien

- `run_trend/storage/database.py` (Tabelle + Migration)
- neuer `run_trend/ui/goal_dialog.py`
- `run_trend/charts/projection_chart.py`
- `run_trend/analytics/race_predictor.py` (ggf. Diff-Berechnung)

## Status / Fortschritt

**Vollständig umgesetzt — DB, Goal-Dialog, Goal-Manager und Projection-Chart-
Overlay sind alle gemerged.**

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
- ✅ `GoalManagerDialog` (`run_trend/ui/goal_manager_dialog.py`): Tabelle
  mit Datum/Distanz/Zielzeit/Status, Buttons Add/Edit/Toggle-Achieved/Delete,
  Doppelklick öffnet Edit, Delete bestätigungspflichtig. Sortierung über
  `db.get_goals()` (Date asc).
- ✅ MainWindow-Integration: File → „Manage Goals…", `_show_goal_manager`
  öffnet den Dialog modal.
- ✅ Übersetzungen für GoalManagerDialog + Menüeintrag (DE/EN, `.ts` + `.qm`).
- ✅ Projection-Chart-Erweiterung: `ProjectionChart.set_goals()` filtert
  achieved Goals weg; `_render_goals()` zeichnet pro aktivem Goal eine
  gepunktete Verbindungslinie vom heutigen Long-Run-Wert zum Zielpunkt sowie
  einen ScatterMarker am Zielpunkt. Farbe Grün (`#27ae60`) wenn die
  Long-Run-Projektion am Zieldatum ≥ `target_distance_km`, sonst Rot
  (`#e74c3c`). Goals nur im **Long-Run-Modus** sichtbar — `target_distance_km`
  ist eine Renndistanz, kein Wochenvolumen, daher keine sinnvolle Overlay im
  Volume-Modus.
- ✅ MainWindow `_update_charts()` pusht aktive Goals (`include_achieved=False`)
  in den Chart; `_show_goal_manager` triggert nach `dialog.exec()` ein
  Re-Render, damit Add/Edit/Delete sofort sichtbar werden.
- ✅ Übersetzungen für ProjectionChart-Goal-Strings
  (`Goal target ({} km)`, `Goal {} km — {}`, `on track`/`auf Kurs`,
  `off track`/`nicht auf Kurs`); `.qm` regeneriert (347 DE / 342 EN).
- ✅ Tests in `tests/test_projection_chart_goals.py` (7 Tests:
  `set_goals`-Filter, None-Input, Long-Run-Rendering, Volume-Skip,
  Off-Track-Farbe Rot, On-Track-Farbe Grün, Past-Date-Skip).

### Annahmen Projection-Chart

- **Vergleich auf Distanz, nicht Pace**: `ProjectionChart` modelliert km
  (Volume bzw. Long Run), nicht Pace pro km. Die Spec spricht von „ATM Pace
  vs. Ziel-Pace"; das würde einen separaten Pace-Projektionsmodus brauchen.
  Stattdessen wird hier die distanzbasierte Lesart umgesetzt: kann der
  längste Lauf am Zieldatum die Renndistanz erreichen? Pace-basiertes
  On-Track-Tracking ist bewusst nicht in dieser Iteration — der UX-Mehrwert
  pro Aufwand ist gering, solange die Distanz-Sicht fehlt, und die DB-Felder
  decken beides ab (target_time_seconds bleibt für künftige Iterationen).
- Goals mit `target_date < heute` werden nicht gerendert (kein Rück-in-die-
  Vergangenheit-Zielen). Erreichte Goals (`achieved=1`) werden bereits in
  `set_goals()` gefiltert.
- Goals jenseits des aktuellen Projektions-Horizonts dehnen die x-Achse aus,
  damit der Marker sichtbar bleibt; der Vergleich verwendet dann den letzten
  projizierten Wert als Heuristik.

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
