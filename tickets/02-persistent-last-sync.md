# 02 — Letzte Sync-Zeit persistent in Statusleiste

**Priorität:** P0
**Kategorie:** Spec-Konformität / UX

## Problem

Spec §13.1 verlangt in der unteren Statusleiste persistente Anzeige von „last sync time,
token/auth status, API sync messages, data refresh errors".
Aktuell: nur transiente `QStatusBar.showMessage()`-Pings, die nach 3 s verschwinden.

## Auswirkung auf Nutzer

Nutzer hat keine Möglichkeit zu sehen, wie aktuell die angezeigten Daten sind.

## Lösungsansatz

Statusleiste in zwei Bereiche aufteilen:

- **Permanenter Bereich (rechts)**: `Last sync: 2 min ago` + Auth-Indikator (✓ verbunden /
  ✗ nicht verbunden). Aus `db.get_setting('last_sync')` + `auth.is_authenticated()`.
- **Transienter Bereich (links)**: aktuelle `showMessage()`-Stream (wie bisher)

Permanenter Status wird nach jedem Sync, nach Auth-Change und beim Start aktualisiert.
Relative Zeit über kleinen QTimer (z.B. alle 60 s neu rechnen).

## Acceptance

- [x] Letzte Sync-Zeit dauerhaft sichtbar, in relativer Form ("2 min ago", "1 hr ago")
- [x] Auth-Status visuell unterscheidbar (Icon oder Farbe)
- [x] Transiente Messages überschreiben den persistenten Bereich nicht
- [x] „Never synced" wenn `last_sync` leer

## Annahmen

- Umsetzung erfolgte im Architektur-Refactor (`61f3387`):
  - Permanente `QLabel`s für Auth + Last-Sync via `addPermanentWidget`
    (`main_window.py:298-301`) — Qt hält diese rechts und lässt sie von
    `showMessage()` (transienter linker Bereich) unangetastet.
  - `_update_persistent_status` (`main_window.py:312-327`) liest
    `auth.is_authenticated()` und `db.get_setting('last_sync')` und setzt
    Text + Tooltip.
  - Auth-Indikator als Unicode-Bullet (`●` Connected / `○` Not connected,
    Zeilen 315/318) — keine Custom-Stylesheets nötig.
  - Relative-Time-Helper `_format_relative_time` (`main_window.py:338-363`)
    mit Bucketing ("just now", "{} min ago", "{} hr ago", "{} days ago").
    UTC/naive-Aware: `iso_str.replace('Z', '+00:00')` + Fallback auf
    `datetime.utcnow()` weil `sync_manager` ohne tz-Info schreibt.
  - QTimer (`main_window.py:305-308`) feuert minütlich
    `_update_persistent_status`, damit „N min ago" lebendig bleibt.
  - Update-Hooks: `_setup_statusbar`, `_check_authentication:386`,
    `_authenticate_strava:442`, `_on_auth_finished:478`,
    `_show_settings:512`, `_on_sync_finished:602`,
    `_on_silent_sync_finished:619`.
- Übersetzungen in `runtrend_de.ts` Zeilen 482-514 vorhanden
  (`● Connected`, `○ Not connected`, `Never synced`, `Last sync: {}`,
  `just now`, `{} min ago`, `{} hr ago`, `{} days ago`).
- AC #3 ist Qt-natives Verhalten: `addPermanentWidget` reserviert einen
  separaten Bereich, den `showMessage` nicht überschreibt — bestätigt
  durch Smoke-Run (Sync-Toast bleibt links, Permanentlabel rechts).
- `pytest tests/` 114 passed (kein Regress).

## Dateien

- `run_trend/ui/main_window.py:295-363, 386, 442, 478, 512, 602, 619`
  (Implementierung bereits da, keine weitere Änderung nötig)
- `run_trend/translations/runtrend_de.ts` und `runtrend_en.ts`
  (Strings bereits da)
