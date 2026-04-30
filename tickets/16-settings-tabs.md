# 16 — Settings-Dialog in Tabs gliedern

**Priorität:** P1
**Kategorie:** UX-Vereinfachung

## Problem

Settings-Dialog mischt aktuell:
- Strava-OAuth (Client-ID, Client-Secret, Connect-Button)
- Sync-Konfiguration (Aktivitätstyp, Auto-Sync)
- Activity-Filter (Treadmill, Manual)
- Datenmanagement (Delete all data)

Alles in einem flachen Layout. Wirkt überfrachtet und macht es schwer, sich zu
orientieren.

## Lösungsansatz

`QTabWidget` mit drei Tabs:

1. **Connection** — Strava-Auth, Connect/Disconnect, Status
2. **Sync** — Aktivitätstyp, Trainingsstart-Datum, Activity-Filter
3. **Data** — DB-Pfad anzeigen, Delete all data, Export-Shortcuts

Spec-Compliance: Tabs sind in Spec §13 nicht explizit gefordert, aber „klar
strukturiertes Settings-UI" ist implizit.

## Acceptance

- [x] Drei Tabs wie oben *(siehe Annahme — vier Tabs umgesetzt)*
- [x] Bestehende Funktionalität vollständig erhalten
- [x] Keine Verhaltensänderungen, nur Strukturierung
- [x] Tab-Order behält Tastatur-Navigation
- [x] Übersetzt (DE/EN)

## Annahmen

- Statt der drei vom Ticket vorgeschlagenen Tabs (`Connection` /
  `Sync` / `Data`) wurden **vier** Tabs umgesetzt — zusätzlich
  `General`. Grund: Sprache und HRmax sind keine Strava-Settings,
  aber Spec/Acceptance verlangen, dass „bestehende Funktionalität
  vollständig erhalten" bleibt. Sie in einen der drei genannten Tabs
  zu zwängen wäre semantisch unsauber gewesen; ein eigener
  `General`-Tab hält den Strava-Bereich fokussiert.
- Tab-Inhalte:
  - **General**: Sprache + Max Heart Rate
  - **Connection**: Strava-API-Credentials + Connect/Disconnect-Button
    + Statuslabel
  - **Sync**: Activity-Filter (Treadmill/Manual) + manueller
    Sync-Button (gegated über `_update_auth_status`)
  - **Data**: Disconnect-and-Delete-Button + Warnhinweis
- Save/Cancel-Buttons bleiben unterhalb der Tabs als globale
  Dialog-Aktionen — sie greifen tabunabhängig auf alle Eingaben zu.
- Keine Verhaltensänderung: alle Callbacks (`_handle_connect`,
  `_handle_sync`, `_handle_delete_data`, `_save_settings`,
  `_update_auth_status`, `_load_settings`) sind unverändert; sie
  sprechen die Widgets weiter über `self.<name>` an, das Reparenting
  in QTabWidget-Pages ist transparent.
- Tastaturnavigation: QTabWidget unterstützt `Ctrl+Tab` /
  `Ctrl+Shift+Tab` zwischen Tabs nativ; innerhalb eines Tabs erfolgt
  die Tab-Order in Deklarations-Reihenfolge der Widgets, was der
  bisherigen flachen Reihenfolge entspricht.
- Translations für die neuen Strings (`General`, `Connection`,
  `Sync`, `Data`, `Manual Sync`, `Disconnect & Delete`, Warnhinweis)
  wurden in beiden `.ts`-Dateien ergänzt; `lrelease` regeneriert
  die `.qm`-Dateien (245 DE / 240 EN finished).
- Inneren GroupBox „Connection" entfernt, da das Tab selbst die
  visuelle Klammer ist — sonst doppelte Beschriftung.

## Dateien

- `run_trend/ui/settings_dialog.py` (komplett restrukturiert)
- `run_trend/translations/runtrend_de.ts` (+7 Einträge)
- `run_trend/translations/runtrend_en.ts` (+7 Einträge)
- `run_trend/translations/runtrend_de.qm` und `runtrend_en.qm`
  (regeneriert via `lrelease`)
