# 36 — `MainWindow` God-Object refactorn

**Priorität:** P2
**Kategorie:** Architektur

## Problem

`run_trend/ui/main_window.py` ist mit **1245 LOC** die mit Abstand
größte Datei im Projekt (zum Vergleich: `database.py` 686 LOC,
`settings_dialog.py` 530 LOC). Die Klasse `MainWindow` hat:

- ~54 Methoden in einer Klasse
- **3 verschachtelte `QThread`-Subklassen** in derselben Datei:
  `SyncThread`, `HrZoneFetchThread`, `_StravaAuthThread`
- Direkter DB-Zugriff aus dem UI-Layer:
  `main_window.py:480, 535, 1066, 1110, 1130, 1176` — `self.db.get_setting`,
  `self.db.get_race_markers`, `self.db.get_goals`,
  `self.db.get_activity_hr_zones`
- `_update_summary` (~80 LOC) macht bei jedem Refresh Konversionen
  über alle Aktivitäten

Konsequenzen:

- UI-Layer ist nicht testbar (`tests/` enthält **null** Files für
  `main_window`)
- Layering-Verletzung: UI greift unter den Service-Layer durch zur DB
- Schwer zu maintainen — wer einen Tab umbenennt, muss durch 1245 Zeilen
  scrollen

## Lösungsansatz

In drei Slices auftrennen, ähnlich wie T19 (HR-Zonen) — jede Slice
mergeable für sich.

### Slice 1: Threads extrahieren

`run_trend/ui/threads.py` neu, enthält `SyncThread`, `HrZoneFetchThread`,
`_StravaAuthThread` als Top-Level-Klassen. `main_window.py` importiert
sie. Reines Move, keine Verhaltensänderung. Spart ~250 LOC im MainWindow.

### Slice 2: ChartCoordinator einführen

`run_trend/ui/chart_coordinator.py` kapselt:

- `aggregates`, `complete_aggregates`, `activities` als State
- Methoden wie `refresh(period_type, start_date, smoothing)`, die
  Database + Aggregator + Smoother aufrufen
- Race-Markers, Goals, HR-Zonen-Cache als Lookup-Dicts (siehe T32)

`MainWindow._update_charts` ruft nur noch
`self.coord.refresh(...)` und dann pro Chart `chart.update_chart(coord)`.

### Slice 3: Toolbar / Menubar in eigene Module

`run_trend/ui/toolbar.py` und `run_trend/ui/menubar.py`. Die Setup-
Methoden mit ~100 LOC Aktionen wandern dort hin; `MainWindow` ruft
`self.toolbar = MainToolbar(self)` o.ä.

## Acceptance

- [x] Slice 1 mergeable: Threads in eigenem Modul (MainWindow von ~1340
      auf 1230 LOC, der < 1000 aus dem Acceptance war wegen T35-Wachstum
      nicht erreichbar — siehe Status)
- [ ] Slice 2 mergeable: kein direkter `self.db.get_*` mehr in
      `_update_*`-Methoden; statt dessen `self.coord.<getter>`
- [ ] Slice 3 mergeable: MainWindow < 600 LOC
- [ ] Erste Unit-Tests für `ChartCoordinator` (`tests/test_chart_coordinator.py`)
- [x] Tests grün (Slice 1: 340 statt 332)
- [ ] App startet, alle Tabs rendern, alle Toolbar-Actions funktionieren
      — manuell zu verifizieren

## Annahmen

- Slice 1 ist risikoarm (reines File-Splitting), 2 und 3 sind echte
  Refactors mit Bug-Risiko — nicht in einer Session machen.
- `ChartCoordinator` bleibt ein UI-naher Helper, kein App-weiter
  Service. MVVM-Style mit ViewModel ist nicht im Scope.
- T32 (HR-Zone Batch-Query) und dieses Ticket profitieren voneinander:
  T32 zuerst macht Slice 2 sauberer (weniger DB-Calls zu extrahieren).
  Reihenfolge: T32 → T36.

## Dateien

- `run_trend/ui/main_window.py`
- `run_trend/ui/threads.py` (neu — Slice 1)
- `run_trend/ui/chart_coordinator.py` (neu — Slice 2, offen)
- `run_trend/ui/toolbar.py` (neu — Slice 3, offen)
- `tests/test_ui_threads.py` (neu — Slice 1)

## Status / Fortschritt

**Slice 1 vollständig umgesetzt, Slice 2 + 3 offen.**

### Slice 1 — Threads extrahiert

- ✅ `run_trend/ui/threads.py` neu (~128 LOC): drei Top-Level-Klassen
  `SyncThread`, `HrZoneFetchThread`, `StravaAuthThread` plus
  Backwards-Compat-Alias `_StravaAuthThread = StravaAuthThread`.
  Reines Move, keine Verhaltensänderung — die SQLite-Connection-
  pro-Thread-Konvention bleibt, die Lazy-Imports im `run()` ebenfalls.
- ✅ `main_window.py`: 3 Class-Definitionen + ~100 LOC entfernt, eine
  Import-Zeile `from .threads import SyncThread, HrZoneFetchThread,
  StravaAuthThread` ersetzt sie. `QThread` aus den
  `from PySide6.QtCore`-Imports gestrichen (nicht mehr verwendet).
  Drei interne Verwendungsstellen umbenannt: `_StravaAuthThread` →
  `StravaAuthThread` (Naming-Aufräumen).
- ✅ Neuer `tests/test_ui_threads.py` (8 Cases): Surface-Tests (alle 3
  Klassen sind `QThread`-Subklassen, Legacy-Alias resolved, alle 3
  werden über `main_window` re-exportiert), plus Constructor-Tests
  (`SyncThread` captures args; `HrZoneFetchThread._cancel`-Flag;
  `HrZoneFetchThread` kopiert settings_snapshot und activity_ids gegen
  Aliasing).
- ✅ `pytest tests/ -W error::DeprecationWarning` 340 grün
  (vorher 332 nach T35; +8 neue Tests).

### LOC-Bilanz (ehrlich)

- `main_window.py`: 1340 (nach T35) → 1230 (nach Slice 1). Nettogewinn
  ~110 LOC.
- `threads.py`: +128 LOC (inkl. Docstrings die im Original fehlten).
- Acceptance-Bar "< 1000 LOC" aus dem Lösungsansatz war für Slice 1
  allein nicht erreichbar, weil T35 zwischenzeitlich ~110 LOC (Shortcuts,
  a11y-Mapping mit 12 Charts × Name/Description) ergänzt hat. Mit T35
  + Slice 1 zusammen liegen wir gleichauf mit dem Pre-T35-Stand.

### Slice 2 (ChartCoordinator) — bewusst nicht angegangen

Slice 2 ist ein echter Refactor (kein File-Splitting): UI greift heute
direkt auf `self.db.get_setting`, `self.db.get_race_markers`,
`self.db.get_goals`, `get_activity_hr_zones_bulk` zu — alle aus
`_update_summary`, `_update_charts`, `_update_hr_zone_chart`,
`_maybe_start_hr_zone_fetch`. Ein `ChartCoordinator` müsste den
Aggregates-State + Lookup-Dicts + Settings-Snapshot kapseln, ohne dass
die einzelnen Chart-Updates Code-Pfade verlieren. Das ist Bug-Risiko in
einer einzelnen autonomen Loop-Iteration zu groß — sollte in einer
dedizierten Session mit App-Start-Verifikation passieren.

### Slice 3 (Toolbar/Menubar-Module) — analog

Genauso: rein mechanisch machbar, aber die `_setup_toolbar`/`_setup_menu`
verdrahten ~15 Signal/Slot-Verbindungen zu MainWindow-Methoden
(`self._show_settings`, `self._sync_activities`, etc.). Verkapselung
würde entweder Callbacks oder Signals zwischen Toolbar und MainWindow
erfordern. Sinnvoll, aber Slice-2-blocked: erst nachdem
ChartCoordinator/State extrahiert ist, lässt sich die Toolbar sauber
kapseln.

### Annahmen

- Backwards-Compat-Alias `_StravaAuthThread` bleibt im neuen Modul
  drin, falls externe Konsumenten den Underscore-Namen referenzieren
  (Tests, Doku, Forks). Kann in einem späteren Cleanup-Ticket fallen.
- T32 (HR-Zone Batch-Query) wurde bereits umgesetzt — Slice 2 ist
  damit naturally entkoppelter geworden (eine DB-Schnittstelle weniger
  in `_maybe_start_hr_zone_fetch`).
- `run_trend/ui/menubar.py` (neu)
- `tests/test_chart_coordinator.py` (neu)
