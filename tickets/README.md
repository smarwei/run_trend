# RunTrend Tickets

Verbesserungen, Erweiterungen und offene Punkte aus Codebase-Analyse + UX-Review.
Stand: 2026-05-11.

## Priorität

- **P0** — Spec-Konformität / Korrektheit, schnell umsetzbar
- **P1** — Spürbarer UX-Gewinn, mittlerer Aufwand
- **P2** — Größere Features, Roadmap
- **P3** — Methodisch zu klären, nicht-blocker

## Index

### Quick Wins (P0)
- [01 — Sync- und Connect-Buttons in der Toolbar](01-sync-toolbar-buttons.md)
- [41 — Methodische Caveats in Metrik-Tooltips ergänzen](41-methodische-caveats.md)
- [02 — Letzte Sync-Zeit persistent in Statusleiste](02-persistent-last-sync.md)
- [03 — RunsTable: fehlende HR sortiert ans Ende](03-runs-table-hr-sort.md)
- [04 — Empty-States für leere Charts und unverbundene Konten](04-empty-states.md)
- [05 — Tooltips für Fachbegriffe (ACWR, TRIMP, EF, Score)](05-metric-tooltips.md)
- [06 — Pace-Achsen einheitlich als MM:SS formatieren](06-pace-axis-formatting.md)
- [07 — `consistency_ratio` im UI sichtbar machen](07-consistency-ratio-display.md)
- [08 — `PaceDistanceChart` auf `BaseChart` umstellen](08-pace-distance-base-chart.md)
- [09 — `PaceDistanceChart`: Margin-Berechnung robust machen](09-pace-distance-margin.md)
- [10 — QThread-Cleanup (Memory-Leak bei wiederholten Syncs)](10-thread-cleanup.md)
- [11 — Toten Code entfernen (`_connect_signals`)](11-dead-connect-signals.md)
- [22 — QtCharts: SIGSEGV durch laufende QAreaSeries-Animation beim Refresh](22-qtcharts-areaseries-animation-crash.md)
- [23 — HTTP-Timeouts an Strava-API-Calls](23-http-timeouts.md)
- [24 — Atomarer Config-Write + Thread-Lock + restriktive Rechte](24-atomic-config-write.md)
- [25 — i18n: Dynamische `tr()`-Calls statisch machen](25-i18n-dynamic-tr.md)
- [26 — AboutDialog: `tr()` einbauen, Version dynamisch lesen](26-about-dialog-i18n.md)
- [27 — `requirements.txt` mit `pyproject.toml` synchronisieren](27-requirements-sync.md)
- [28 — `datetime.utcnow()` → `datetime.now(timezone.utc)`](28-datetime-utcnow.md)
- [29 — OAuth-Callback-Server an `127.0.0.1` binden statt `0.0.0.0`](29-oauth-bind-localhost.md)
- [30 — Toten Code `load_strava_credentials_from_file` entfernen](30-dead-code-load-creds.md)
- [31 — Debug-Skripte und Streamer aus dem Repo-Root räumen](31-debug-scripts-cleanup.md)

### UX-Erweiterungen (P1)
- [12 — Export: Charts als PNG, Daten als CSV](12-export-png-csv.md)
- [39 — Training-Score als „Trend-Indikator" labeln (oder ersetzen)](39-score-rename-trend.md)
- [13 — Onboarding-Wizard beim ersten Start](13-onboarding-wizard.md)
- [14 — Year-over-Year-Vergleichslinie auf Charts](14-year-over-year.md)
- [15 — Race-Marker auf Zeitachsen-Charts](15-race-markers.md)
- [16 — Settings-Dialog in Tabs gliedern](16-settings-tabs.md)
- [17 — Score-Breakdown anzeigen ("Warum X/100?")](17-score-breakdown.md)
- [32 — N+1 DB-Queries beim HR-Zonen-Render eliminieren](32-hr-zone-batch-query.md)
- [33 — RoC-Toggle in `BaseChart` deduplizieren](33-roc-toggle-dedup.md)
- [34 — Test-Coverage-Lücken bei Kern-Modulen schließen](34-test-coverage-core.md)
- [35 — Keyboard-Shortcuts und Accessibility-Attribute](35-keyboard-shortcuts-a11y.md)

### Größere Features (P2)
- [18 — Goal-Tracking mit Ist/Ziel-Linie auf Projection-Chart](18-goal-tracking.md)
- [19 — HR-Zonen-Auswertung mit Zeit-in-Zone](19-hr-zones.md)
- [36 — `MainWindow` God-Object refactorn](36-mainwindow-refactor.md)
- [37 — Age-Graded Performance Chart (WMA + HF-Physiologie)](37-age-graded-performance.md)
- [38 — Training-Fitness via CTL/ATL/TSB (absolute Skala neben Training-Score)](38-training-fitness-ctl.md)
- [40 — ACWR auf tägliche 7:28-Tage-Rolling-Sums umstellen](40-acwr-daily-rolling.md)

### Methodisch (P3)
- [20 — Pace als ACWR-Komponente überdenken](20-pace-acwr-review.md)
- [21 — EF-Baseline-Fallback statt arbiträrem Default](21-ef-baseline-fallback.md)
