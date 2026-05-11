# 22 — QtCharts: SIGSEGV durch laufende QAreaSeries-Animation beim Refresh

**Priorität:** P0
**Kategorie:** Bug / Stabilität

## Problem

Beim App-Start kann es nach Abschluss des Silent-Sync zu einem Segfault kommen.
Coredump (PID 95610, 2026-05-11 19:48:44) zeigt eindeutig:

```
#0 QAbstractSeries::chart() const          libQt6Charts
#1 AreaBoundItem::updateGeometry()         libQt6Charts
#2 XYAnimation::updateCurrentValue(...)    libQt6Charts
#3 QVariantAnimationPrivate::setCurrentValueForProgress
#4 QAbstractAnimation::setCurrentTime
#5 QAnimationTimer::updateAnimationsTime
```

Race-Condition:

1. `_check_authentication` ruft `_load_data()` auf → alle Charts bauen
   Series + Achsen auf. Mit `setAnimationOptions(SeriesAnimations)` startet Qt
   eine `XYAnimation`, die einen rohen Pointer auf die `QAreaSeries` hält.
2. Parallel läuft `_run_silent_sync()`. Sobald dessen `finished` feuert,
   ruft `_on_silent_sync_finished` ein zweites `_load_data()` auf.
3. Im zweiten `update_chart` löst `_clear_chart()` ein `removeAllSeries()`
   aus, während die Animation aus Schritt 1 noch im Animation-Timer steht.
4. Der nächste Animation-Tick dereferenziert die bereits freigegebene
   `QAreaSeries` → SIGSEGV in `AreaBoundItem::updateGeometry`.

Bekanntes Qt-Bug-Muster (QTBUG-65229 u. ä.): `QAreaSeries` +
`SeriesAnimations` + `removeSeries`/`removeAllSeries` während die
Animation noch läuft.

Betroffene Charts (die einzigen mit `QAreaSeries`):

- `run_trend/charts/heartrate_chart.py` (HR-Range-Band)
- `run_trend/charts/training_load_chart.py` (Training-Load-Band)

Beide haben `SeriesAnimations` aktiv (über `base_chart.py:57`).

## Auswirkung auf Nutzer

Sporadischer Crash beim App-Start, abhängig vom Timing zwischen
Startup-Render und Silent-Sync-Abschluss. Wahrscheinlicher bei vielen neuen
Aktivitäten (größere Datenänderung → längere Animation → breiteres
Race-Fenster).

## Lösungsansatz

Mehrere Optionen, von minimal bis robust:

1. **Animationen auf den zwei `QAreaSeries`-Charts deaktivieren** —
   `setAnimationOptions(QChart.NoAnimation)` in `heartrate_chart.py:46` und
   `training_load_chart.py` (entsprechende Zeile). Kleinste Änderung,
   trifft den genauen Crash-Vektor.
2. **Animationen global abschalten** in `base_chart.py:57`. Robust gegen
   ähnliche Bugs in anderen Series-Typen, aber UX-Verlust überall.
3. **Refresh nicht überlappen lassen** — `_on_silent_sync_finished` per
   `QTimer.singleShot(<animation_duration>, …)` verzögern oder vor
   `_clear_chart()` die Animation explizit beenden
   (`setAnimationOptions(NoAnimation)` → `removeAllSeries()` → restore).
   Komplexer und löst das Problem nicht zuverlässig, falls die Animation
   in einer anderen Event-Schleifen-Phase tickt.

Empfohlen: **Option 1** als erster Wurf, weil die Diagnose den Crash
eindeutig `AreaBoundItem` zuordnet.

## Workaround

Während der Diagnose war kurzzeitig `faulthandler.enable()` in
`run_trend/main.py` aktiv, um einen Python-Stacktrace beim nächsten
Segfault zu erzwingen. Der zweite Crash hat die Diagnose bestätigt
(GUI-Thread in `app.exec()`, keine Python-Frames darüber), der Aufruf
wurde mit dem Fix wieder entfernt.

## Lösung

Option 1 umgesetzt: `SeriesAnimations` für die beiden `QAreaSeries`-Charts
deaktiviert. Andere Charts behalten Animationen.

- `run_trend/charts/heartrate_chart.py:46` — `NoAnimation`
- `run_trend/charts/training_load_chart.py:37` — `NoAnimation` nach
  `_setup_chart_view` (überschreibt das Default aus `BaseChart`)

## Acceptance

- [ ] Kein Segfault mehr beim App-Start, auch bei vielen neuen Aktivitäten
  im Silent-Sync (Reproduktion: lange nicht synchronisiert, dann starten)
- [ ] HR-Chart und Training-Load-Chart rendern korrekt (Bands sichtbar)
- [x] `faulthandler.enable()`-Aufruf aus `run_trend/main.py` entfernt
- [ ] `pytest tests/` weiterhin grün

## Dateien

- `run_trend/charts/heartrate_chart.py:46` — Animation-Options
- `run_trend/charts/training_load_chart.py` — Animation-Options
- `run_trend/charts/base_chart.py:57` — falls Option 2
- `run_trend/main.py` — `faulthandler.enable()` wieder ausbauen

## Coredump-Referenz

- `coredumpctl info 95610` (Boot `7bdf34f7915c4865bfd4f4e99da0357c`)
- Storage: `/var/lib/systemd/coredump/core.python3\x2e13.1000.7bdf34f7915c4865bfd4f4e99da0357c.95610.1778521724000000.zst`
