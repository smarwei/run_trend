# 13 — Onboarding-Wizard beim ersten Start

**Priorität:** P1
**Kategorie:** UX

## Problem

Erstnutzer-Erfahrung: leere Charts, kein Hinweis wie weiter. Settings-Dialog ist
versteckt im Menü. „Trainingsstart-Datum" ist eine wichtige Konfiguration, die der
Nutzer beim ersten Start nicht kennt.

## Auswirkung auf Nutzer

Hohe Drop-off-Rate beim ersten Start. Auch Nutzer, die durchhalten, brauchen mehrere
Klicks bis zum ersten Sync.

## Lösungsansatz

`QWizard` mit 3 Schritten beim ersten Start (wenn keine Auth + keine Daten):

1. **Welcome** — Was die App macht, kurz und in einem Satz.
2. **Connect to Strava** — „Connect"-Button, OAuth-Flow direkt im Wizard.
3. **Trainingsstart wählen** — Date-Picker mit Default „1 Jahr zurück"; Hinweis,
   dass das später im Settings-Dialog änderbar ist.

Nach Finish: Sync starten, Wizard schließen, Hauptfenster zeigt Daten.

Bedingung für Anzeige: `auth.is_authenticated() == False AND db.get_activity_count() == 0`.

## Acceptance

- [x] Wizard erscheint nur beim ersten Start oder explizit über „Help → First-Run Wizard"
- [x] Schritte können vor- und zurück
- [x] Wizard kann mit „Skip" abgebrochen werden, ohne dass die App kaputt ist
- [x] Übersetzt (DE/EN)
- [x] Nach Finish: automatischer Sync und Daten erscheinen

## Annahmen

- **Trigger-Hook:** First-Run-Erkennung sitzt nicht in `main.py`,
  sondern in `MainWindow._check_authentication`. Grund: dort wird
  bereits `auth.is_authenticated()` und `db.get_activity_count()`
  geprüft; eine zweite Stelle in `main.py` würde die Bedingung
  duplizieren. Der bisherige `QTimer.singleShot(100, _show_settings)`
  beim ersten Start wird durch `_show_onboarding_wizard` ersetzt,
  wenn die DB leer ist (Legacy-Installs ohne Auth, aber mit Daten,
  bekommen weiterhin den Settings-Dialog).
- **Skip = Cancel:** statt eines zusätzlichen `CustomButton` wird der
  vorhandene `QWizard.CancelButton` per `setButtonText` zu „Skip"
  umbenannt. Ergebnis: ein Klick ruft `reject()` auf, die App läuft
  ohne Auth/Daten weiter — entspricht dem AC „ohne dass die App
  kaputt ist".
- **OAuth-Integration:** der Connect-Button im Wizard delegiert an
  `MainWindow._authenticate_strava()` (kein doppelter OAuth-Flow).
  Damit der Wizard Auth-Erfolg/-Misserfolg erfährt, exponiert
  `MainWindow` ein neues Signal `auth_finished = Signal(bool)`,
  das in `_on_auth_finished` emittiert wird. Der Wizard verbindet
  sich mit `connect_page.mark_result`. Während des Wizards werden
  die normalen Follow-up-`QMessageBox`es (Sync-Ja/Nein, Auth-Failure)
  unterdrückt — das Wizard-Status-Label übernimmt die Rückmeldung.
- **Date-Default:** Default für „Training Start Date" ist genau
  ein Jahr vor heute (`QDate.currentDate().addYears(-1)`). Ticket
  sagt „1 Jahr zurück" — exakte Implementierung. Für 2026-04-30
  also 2025-04-30.
- **Persistenz:** nach Finish wird das Datum in
  `settings['ui_start_date']` (Format `YYYY-MM-DD`) abgelegt — der
  gleiche Key, den `_restore_ui_settings` beim nächsten Start liest.
  Außerdem wird `start_date_edit` direkt aktualisiert, damit das
  Datum sofort als Sync-Startpunkt benutzt werden kann.
- **Auto-Sync nach Finish:** läuft nur, wenn nach Wizard-Ende
  `auth.is_authenticated() == True` UND
  `db.get_activity_count() == 0`. Skip auf Connect-Page → kein
  Sync; Re-Open des Wizards bei vorhandenen Daten → kein Sync.
- **Help-Menü:** das `&Help`-Menü (Alt+H / Alt+H) wird in
  `_setup_menu` neben `&File` initialisiert; Eintrag „First-Run
  Wizard" → `_show_onboarding_wizard`. Der bestehende „Help"-Button
  in der Toolbar (öffnet das Manual) bleibt unverändert.
- **Translation-Kontext:** alle Wizard-Strings nutzen
  `QCoreApplication.translate("OnboardingWizard", …)` über einen
  Modul-Helper `_tr()`. Damit landet der Wizard-Text in einem
  einzigen `<context>OnboardingWizard</context>`-Block in den
  `.ts`-Dateien (15 Strings); die zwei neuen MainWindow-Strings
  („&Help", „First-Run Wizard") landen im MainWindow-Block.
  `lrelease`: 289 DE / 284 EN finished.
- **Tests:** keine neuen Unit-Tests — der Wizard ist UI-lastig und
  hängt am OAuth-Flow + Browser. Bestehende `pytest tests/`
  (124 passed) bleiben grün.

## Dateien

- neuer `run_trend/ui/onboarding_wizard.py`
- `run_trend/ui/main_window.py` (`auth_finished`-Signal,
  `_setup_menu`, `_check_authentication`, `_on_auth_finished`,
  `_show_onboarding_wizard`)
- `run_trend/translations/runtrend_de.ts`, `runtrend_en.ts`,
  regenerated `.qm`
