# 04 — Empty-States für leere Charts und unverbundene Konten

**Priorität:** P0
**Kategorie:** UX

## Problem

Wenn der Nutzer noch nicht mit Strava verbunden ist oder keine Daten im gewählten
Zeitraum hat, zeigen die Charts ein leeres Plot-Area ohne Hinweis.

## Auswirkung auf Nutzer

- Erstnutzer denkt, die App sei kaputt
- Nutzer mit zu engem Date-Filter weiß nicht, dass es Daten außerhalb des Fensters gibt
- Keine Call-to-Action zum „Connect to Strava"

## Lösungsansatz

In `BaseChart` einen Empty-State-Mechanismus ergänzen:

- Methode `_show_empty_state(message: str, action: Optional[QPushButton] = None)`
  überlagert das Chart mit zentriertem Text (+ optionalem Button).
- Aufrufer (Charts) prüfen vor dem Plotten: keine Daten → Empty-State.

Drei Hauptvarianten:

1. **Nicht verbunden** — „Connect to Strava to see your runs" + Button → öffnet
   Auth-Flow
2. **Keine Daten im Zeitraum** — „No runs between {start} and {end}" + Hint, Date-Range
   zu erweitern
3. **HR-Charts ohne HR-Daten** — „No heart-rate data available — wear an HR sensor
   while running"

## Acceptance

- [x] Alle Charts zeigen Empty-State statt leerem Plot-Area
- [x] „Connect"-Button in Empty-State führt zum OAuth-Flow
- [x] Empty-States sind übersetzt (DE/EN)
- [x] Nach erfolgreicher Verbindung verschwindet der Empty-State und Daten erscheinen

## Annahmen

- Empty-State-Mechanismus liegt in `BaseChart` als `QStackedWidget`-Overlay mit
  zwei Seiten (Chart-View, Empty-Widget). Subklassen wickeln ihre `chart_view`
  beim Setup einmal mit `_wrap_chart_view_with_empty_state(...)` ein und nutzen
  `show_empty_state(message, show_connect_button=...)`. Keine Subklasse muss eine
  eigene Empty-State-Logik bauen.
- Der Connect-Button feuert das Class-Level-Signal `connect_requested`, das
  `MainWindow` einmalig auf `_authenticate_strava` verdrahtet — gleicher Pfad
  wie der Toolbar-Button (T01).
- `_clear_chart()` in `BaseChart` blendet automatisch die Empty-State-Seite aus,
  bevor neue Series/Axes hinzugefügt werden; alle elf Charts rufen das schon am
  Anfang ihres `update_chart()` auf, daher braucht es keine Anpassung der
  einzelnen `update_chart`-Methoden für „Daten kommen rein → Chart erscheint".
- Zwei Varianten der Botschaft (siehe `MainWindow._show_charts_empty_state`):
  „nicht verbunden" + Button oder „keine Daten im Zeitraum" ohne Button.
  Die ursprünglich geplante dritte Variante (HR-Charts ohne HR-Daten) bleibt out
  of scope, da das HR-Chart bereits eigene Hinweistexte zeigt, sobald es
  HR-frei aggregierte Daten erhält.
- Das `BaseChart`-`Connect to Strava`-Label nutzt `QCoreApplication.translate(
  "BaseChart", ...)` statt `self.tr(...)`, damit alle Subklassen denselben
  Übersetzungs-Kontext teilen — sonst bräuchten elf separate `<context>`
  Einträge in den `.ts`-Dateien.

## Dateien

- `run_trend/charts/base_chart.py`
- `run_trend/charts/distance_chart.py`
- `run_trend/charts/heartrate_chart.py`
- `run_trend/charts/pace_chart.py`
- `run_trend/charts/projection_chart.py`
- `run_trend/charts/structure_overview_chart.py`
- `run_trend/ui/main_window.py`
- `run_trend/translations/runtrend_de.ts`
- `run_trend/translations/runtrend_en.ts`
- `run_trend/translations/runtrend_de.qm` (regeneriert)
- `run_trend/translations/runtrend_en.qm` (regeneriert)
