# 35 — Keyboard-Shortcuts und Accessibility-Attribute

**Priorität:** P1
**Kategorie:** UX / Barrierefreiheit

## Problem

Die App hat aktuell genau **einen** Keyboard-Shortcut: `Ctrl+F` im
Manual-Dialog (`run_trend/ui/manual_dialog.py:65`). Sonst nichts —
weder F5 für Sync, noch Ctrl+, für Settings, noch Ctrl+1..9 für
Tab-Wechsel, noch Ctrl+Q für Quit.

Zusätzlich gibt es **null** `setAccessibleName`/`setAccessibleDescription`-
Aufrufe quer durch das Projekt. Screenreader (Orca auf Linux,
Narrator auf Windows) bekommen damit keine sinnvolle Beschreibung der
Charts, Toolbar-Buttons oder Auswahl-Combos.

## Auswirkung auf Nutzer

- Power-User klicken sich durch das UI statt Tastenkürzel zu nutzen
- Sehbehinderte Nutzer bekommen unverständliche „QChartView 1",
  „QChartView 2"-Labels vom Screenreader
- Flathub-Bewertungen haben in der Vergangenheit explizit Tastenkürzel-
  Lücken bemängelt (Quelle: ähnliche Sport-Tracker-Reviews)

## Lösungsansatz

### Keyboard-Shortcuts

In `MainWindow._setup_toolbar` / `_setup_menubar`:

| Shortcut       | Aktion                             |
|----------------|------------------------------------|
| `F5`           | Sync triggern                      |
| `Ctrl+,`       | Settings öffnen                    |
| `Ctrl+1..9`    | Tab wechseln (Overview..Projection)|
| `F1`           | Manual / Help öffnen               |
| `Ctrl+Q`       | Quit (Standard)                    |
| `Ctrl+E`       | Export-Menü (siehe T12)            |

Implementierung über `QAction.setShortcut(QKeySequence(...))` an
existierenden Actions. Tab-Switch über `QShortcut(QKeySequence("Ctrl+1"),
self, lambda: self.tabs.setCurrentIndex(0))`.

### Accessibility

`setAccessibleName` und `setAccessibleDescription` an:

- Jedem `QChartView` (z. B. „Distance progression chart", Beschreibung
  „Shows weekly distance totals from training start to today")
- Toolbar-Actions (vom `QAction.text()` automatisch übernommen — nur
  sicherstellen, dass die Texte aussagekräftig sind)
- Combos / Date-Picker im Toolbar (Period-Select, Start-Date)
- Tab-Reiter (i. d. R. automatisch aus `QTabWidget.addTab(title)`)

## Acceptance

- [x] Globale Shortcuts: F5 Sync, Ctrl+, Settings, F1 Help, Ctrl+E
      Export CSV, Ctrl+R Manage Races, Ctrl+G Manage Goals,
      Ctrl+Q Quit, Ctrl+1..9 + Ctrl+0 Tab-Switch
- [x] Tooltip-Anzeige der Shortcuts (Sync, Settings, Help mit
      eingebettetem Shortcut-Hinweis)
- [x] `setAccessibleName` an allen 12 Charts (sowohl auf der
      Chart-Widget-Instanz als auch — wenn vorhanden — auf
      `chart_view`)
- [x] `setAccessibleDescription` analog
- [x] Übersetzte Shortcut-Tooltips + Quit-Label + a11y-Strings
      (DE 421 / EN 416, vorher 393/388)
- [ ] Manuell mit Tastatur navigierbar: Sync auslösen, Tab wechseln,
      Settings öffnen, ohne Maus — manuell zu verifizieren
      (Automated-Tests bestätigen Shortcut-Wiring; reale Aktivierung
      hängt am Qt-Event-Loop)

## Annahmen

- `Ctrl+,` ist auf macOS Standard-Shortcut für Settings; auf Linux/Windows
  weniger etabliert, aber konsistent und kollisionsfrei.
- `F5` reserviert Browser-Reload, aber in Desktop-Apps üblich für
  „Aktualisieren" (z. B. File-Manager). Konsistent für unsere
  „Sync"-Semantik.
- Detail-Audit der vollständigen WCAG-2.1-Compliance ist nicht im Scope —
  separates Ticket falls gewünscht.

## Dateien

- `run_trend/ui/main_window.py` (Toolbar-Shortcuts, Menu-Shortcuts,
  Tab-Wechsel-Shortcuts, Chart-a11y)
- `run_trend/translations/runtrend_de.ts` + `runtrend_en.ts` (28 neue
  Strings: Tooltips, &Quit, 12 a11y-Names, 12 a11y-Descriptions)
- `run_trend/translations/*.qm` (regeneriert)
- `tests/test_keyboard_a11y.py` (neu)

## Status / Fortschritt

**Vollständig umgesetzt.**

- ✅ Import-Erweiterung: `QKeySequence`, `QShortcut` aus `PySide6.QtGui`.
- ✅ `_setup_toolbar`-Erweiterungen: `settings_action.setShortcut("Ctrl+,")`,
  `sync_action.setShortcut("F5")`, `help_action.setShortcut("F1")` plus
  passende `setToolTip("… (Shortcut)")`-Texte. Actions als
  Instanz-Attribute exponiert (`self.settings_action`, `self.help_action`),
  damit Tests sie finden.
- ✅ `_setup_menu`-Erweiterungen: `Ctrl+E` (Export CSV), `Ctrl+R`
  (Manage Races), `Ctrl+G` (Manage Goals), plus neue `&Quit`-Action mit
  `QKeySequence.Quit` (= Ctrl+Q auf Linux/Windows, ⌘Q auf macOS),
  triggered `self.close()`.
- ✅ Neuer Helper `_setup_tab_shortcuts()`: erzeugt `QShortcut`s für
  Ctrl+1..9 plus Ctrl+0; Default-Arg-Trick im Lambda schützt vor dem
  Loop-Variable-Capture-Bug. Aufruf nach `_setup_statusbar` in
  `__init__`.
- ✅ Neuer Helper `_setup_chart_a11y()`: setzt
  `setAccessibleName` + `setAccessibleDescription` auf alle 12 Charts
  (Distance, Pace, Frequency, HeartRate, HrZone, Endurance, Duration,
  Structure, Score, TrainingLoad, Projection, PaceDistance). Sowohl
  auf der Chart-Widget-Instanz selbst als auch — wenn vorhanden — auf
  `chart.chart_view`. HrZoneChart hat in `__init__` (noch) kein
  `chart_view`-Attribut (das wird lazy beim Context-Menu gesetzt), das
  ist mit dem widget-Level-Fallback korrekt abgedeckt.
- ✅ Übersetzungen ergänzt in `MainWindow`-Context beider .ts-Dateien:
  3 Tooltip-Strings, `&Quit` (→ `&Beenden`), 12 a11y-Names und 12
  a11y-Descriptions. `lrelease` produziert DE 421 / EN 416 (vorher 393
  / 388).
- ✅ `tests/test_keyboard_a11y.py` neu mit 11 Cases in 4 Klassen
  (TestToolbarShortcuts × 3, TestMenuShortcuts × 4, TestTabShortcuts ×
  2, TestChartAccessibility × 2). Nutzt eine `_MainWindowFixture`-
  Mixin-Klasse mit XDG_*-Env-Redirect auf `tempfile.mkdtemp()`, damit
  AppSettings/Database nicht ins echte $HOME schreiben. Event-Loop
  wird bewusst NICHT gespint, damit der `QTimer.singleShot(100,
  …)`-Onboarding-Trigger nicht feuert.
- ✅ `pytest tests/ -W error::DeprecationWarning` 332 grün
  (vorher 321 + 11 neue).

### Annahmen (Umsetzung)

- a11y wird **doppelt** gesetzt (auf Chart-Widget UND auf chart_view),
  weil Screen-Reader je nach Implementierung den fokussierten
  Descendant oder das Top-Level-Widget abfragen. Doppelte Pflege ist
  vernachlässigbar; im Test wird nur die Widget-Ebene geprüft, weil sie
  immer existiert (chart_view bei HrZoneChart lazy).
- Ctrl+0 für Tab 10 (Runs) statt Ctrl+10, weil QKeySequence kein
  zweistelliges Modifier-Pair akzeptiert. Browser-Konvention.
- Tooltips bekommen den Shortcut-Hinweis textuell mitgegeben, nicht
  über die Qt-Auto-Magic des Status-Tips. Sichtbar bleibt das in
  beiden UI-Sprachen.
- Echte E2E-Verifikation per Tastatur ist nur manuell sinnvoll — der
  Test bestätigt nur, dass das Wiring stimmt und die activations das
  erwartete Verhalten triggern.
