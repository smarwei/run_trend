# 32 — N+1 DB-Queries beim HR-Zonen-Render eliminieren

**Priorität:** P1
**Kategorie:** Performance

## Problem

`run_trend/ui/main_window.py:1130`:

```python
for a in hr_activities:
    cached = self.db.get_activity_hr_zones(a['strava_id'])
    ...
```

…und analog in `_maybe_start_hr_zone_fetch` bei `main_window.py:1176`
(`if self.db.get_activity_hr_zones(a['strava_id']) is None: targets.append(...)`).

Bei 500 HR-Aktivitäten ergibt das 500 SQL-Roundtrips pro Render-Pass — und
`_update_hr_zone_chart` wird aus `_update_charts` aufgerufen, das bei
jedem Period-Wechsel, Smoothing-Toggle oder Settings-Save komplett
durchläuft. Aktuell merkbar, sobald die Datenbank > 1 Jahr Aktivitäten hat.

## Lösungsansatz

Neue Bulk-Methode in `Database`:

```python
def get_activity_hr_zones_bulk(
    self, strava_ids: list[int]
) -> dict[int, dict]:
    """Return {strava_id: row_dict} für alle gegebenen IDs, die einen
    Cache-Eintrag haben. IDs ohne Cache fehlen im Ergebnis."""
```

Implementierung: ein einziges `SELECT ... WHERE strava_id IN (?, ?, ...)`,
Chunking falls > 999 IDs (SQLite-Limit). MainWindow holt das Dict einmal
und macht in der Schleife reines Dict-Lookup.

`_maybe_start_hr_zone_fetch` analog: einmal das Dict holen, dann
`if strava_id not in zones_dict: targets.append(...)`.

## Acceptance

- [x] `Database.get_activity_hr_zones_bulk(ids)` mit Tests in
      `tests/test_hr_zones_storage.py` (leere Liste, partielle Treffer,
      > 999 IDs Chunking)
- [x] `_update_hr_zone_chart` ruft `get_activity_hr_zones_bulk` einmal auf
- [x] `_maybe_start_hr_zone_fetch` analog umgestellt
- [ ] Manueller Perf-Check: 500 HR-Aktivitäten, Period-Switch fühlt sich
      visuell instant an (vorher: spürbare Verzögerung) — manuell zu
      verifizieren (automatisierter Test mickrig im O-Sinn nicht beweisbar)
- [x] Bestehender Test `test_hr_zone_chart.py` weiterhin grün

## Annahmen

- SQLite-Limit für Parameter-Anzahl: bis Python 3.11/SQLite 3.32 default
  999, ab SQLite 3.32 (Python 3.12) 32766. Chunking-Logik hardcoded
  auf 900er Chunks reicht weit jenseits realistischer Daten.
- Alternative wäre ein In-Memory-Cache im MainWindow, der bei
  Settings-Change invalidiert wird; aber Bulk-Query ist einfacher und
  vermeidet Cache-Konsistenz-Bugs.

## Dateien

- `run_trend/storage/database.py`
- `run_trend/ui/main_window.py`
- `tests/test_hr_zones_storage.py`

## Status / Fortschritt

**Vollständig umgesetzt.**

- ✅ `Database.get_activity_hr_zones_bulk(strava_ids)`: einzelner
  `SELECT ... WHERE strava_id IN (?, ?, ...)` pro Chunk à 900 IDs,
  Ergebnis als `{strava_id: row_dict}`. IDs ohne Cache-Eintrag fehlen
  schlicht im Dict — Callers prüfen Membership.
- ✅ `_update_hr_zone_chart` (`main_window.py:~1130`): genau eine
  Bulk-Query vor der Aktivitäten-Schleife, danach `zone_rows.get(...)`
  als reines Dict-Lookup. Aus N+1 wird `1`.
- ✅ `_maybe_start_hr_zone_fetch` (`main_window.py:~1176`): collected
  alle HR-Aktivitäts-IDs, einmal Bulk-Query, dann via `cached_ids`-Set
  die Targets bestimmen.
- ✅ `tests/test_hr_zones_storage.py`: neue `TestActivityHrZonesBulk`-
  Klasse mit 4 Cases — leere Liste → leeres Dict, partielle Treffer,
  voller Row-Payload identisch zu single-row API, Chunking bei 1500
  Query-IDs (50 hits → 50 Treffer im Ergebnis).
- ✅ Bestehender `test_hr_zone_chart.py` (9 Cases) weiterhin grün —
  MainWindow-Verhalten unverändert.
- ✅ `pytest tests/` 294 grün (290 + 4 neue).

### Annahmen (Implementierung)

- Chunk-Größe 900 statt knapp unter dem 999er-Limit (Python < 3.12 /
  SQLite < 3.32): minimale Sicherheits-Marge gegen SQLite-Builds, die
  weniger als 999 Parameter erlauben (z. B. einige eingebettete Builds).
- Kein In-Memory-Cache im MainWindow — die bestehende
  `invalidate_activity_hr_zones`-Logik bleibt der einzige Konsistenz-
  Punkt. Bulk-Query ist auch ohne Cache schnell genug.
- `cached_ids = set(...)`: `set(dict)` enthält die Keys; bei den
  realistischen Größenordnungen (< 5k Aktivitäten) ist Set-Lookup so
  schnell wie In-Dict.
