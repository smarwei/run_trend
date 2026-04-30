# 01 — Sync- und Connect-Buttons in der Toolbar

**Priorität:** P0
**Kategorie:** Spec-Konformität / UX

## Problem

Spec §13.1 verlangt in der Top-Toolbar Buttons für „Connect to Strava" und „Sync".
Aktuell: nur Auto-Sync beim App-Start, manuelles Triggern nur über Settings-Dialog.

## Auswirkung auf Nutzer

Nach einem Lauf kann der Nutzer die App nicht selbst aktualisieren ohne Neustart oder
Settings-Dialog zu öffnen. Auch nach einem Token-Verlust ist „Connect" unauffindbar.

## Lösungsansatz

Toolbar in `_setup_toolbar` um zwei Aktionen erweitern:

- **Sync** → bindet `_sync_activities()` (existiert bereits)
- **Connect to Strava** → bindet `_authenticate_strava()` (existiert bereits)
  Sichtbar nur wenn nicht authentifiziert; nach Verbindung ausblenden oder durch
  „Re-authenticate" ersetzen.

## Acceptance

- [x] Sync-Button in Toolbar, links neben Date-Selector
- [x] Connect-Button sichtbar wenn `auth.is_authenticated() == False`
- [x] Beide haben Icon + Übersetzungs-Strings (DE/EN)
- [x] Sync-Button während laufendem Sync deaktiviert (verhindert Doppel-Trigger)

## Annahmen

- Icons via `QIcon.fromTheme(name, fallback)` mit Qt-Standard-Pixmap als Fallback
  (`SP_FileDialogDetailedView`, `SP_DriveNetIcon`, `SP_BrowserReload`) — funktioniert
  cross-platform auch ohne installiertes Icon-Theme.
- Connect-Button wird nicht durch „Re-authenticate" ersetzt sondern komplett
  ausgeblendet, sobald `auth.is_authenticated()` true ist. Re-Auth läuft über den
  Settings-Dialog.

## Dateien

- `run_trend/ui/main_window.py` (`_setup_toolbar`)
- `run_trend/translations/runtrend_*.ts`
