# 21 — EF-Baseline-Fallback statt arbiträrem Default

**Priorität:** P3
**Kategorie:** Methodisch

## Problem

`run_trend/analytics/training_score.py:53`:

```python
baseline_efficiency = 0.018  # Default ~0.018 (2.78 m/s @ 155 bpm)
```

Wenn Nutzer noch keine HR-Historie hat, fließt dieser arbiträre Default in die
Score-Berechnung ein. Für sehr fitte oder Anfänger-Läufer kann das den Score
systematisch verzerren.

Es gibt bereits eine HR-Fallback-Logik (Zeilen 118–125) — die zieht aber erst, wenn HR
**komplett fehlt**, nicht wenn EF-Daten **zu wenig** sind für eine valide Baseline.

## Lösungsansatz

Schwelle für aktivierte EF-Komponente leicht höher setzen:

- Aktuell: HR-fallback wenn keine HR
- Vorschlag: EF-fallback wenn `< 3 EF-Werte` über Trainingshistorie verfügbar

Wenn EF-Komponente nicht verfügbar, sollte sie:

1. **Aus der Score-Formel rausgenommen werden** — Gewichtung der anderen Komponenten
   wird neu auf 100% normalisiert (30% Vol, 20% Cons, 50% Int)
2. **Nicht durch Default ersetzt werden** — Default verzerrt systematisch

## Acceptance

- [x] EF-Komponente nur aktiv mit `>= 3` validen Werten
- [x] Sonst: Re-Normalisierung der Gewichtungen
- [x] Score-Breakdown (siehe Ticket 17) zeigt explizit „EF: nicht verfügbar"
- [x] Test in `tests/test_analytics.py` für beide Fälle

## Annahmen

- Schwellwert sitzt als Modul-Konstante `MIN_EF_SAMPLES = 3` in
  `training_score.py`. Geprüft wird `len(efficiencies) >= MIN_EF_SAMPLES`
  über die gesamte (komplette) Historie — nicht pro Periode.
- Re-Normalisierung der Gewichtungen ist bereits implementiert (existierender
  `if has_hr_data: … else: …`-Pfad). Es wurde nur die Bedingung verschärft:
  `has_hr_data = ef_history_sufficient and current_efficiency > 0`. Damit
  greift der Drittel-Fallback (37.5/25/37.5) sowohl bei „kein HR" als auch
  bei „zu wenig HR-Historie".
- Der arbiträre Default `baseline_efficiency = 0.018` ist **ersatzlos**
  entfernt. Wenn `ef_history_sufficient=False`, wird `baseline_efficiency`
  niemals gelesen, weil `has_hr_data=False` den EF-Pfad überspringt — daher
  sicher kein Division-by-zero-Risiko.
- Anzeigetext in `summary_panel._set_breakdown_label`: „No HR data" →
  „not available", weil das Label jetzt zwei Fälle abdeckt (kein HR + zu
  wenig HR-Historie). Übersetzung DE: „nicht verfügbar".
- `get_score_explanation()` ergänzt um Hinweis auf 3-Sample-Threshold im
  HR-Fallback-Block.
- `score_components.has_hr_data` behält seinen Schlüsselnamen, bedeutet
  jetzt aber „EF trägt zum Score bei" (per-Periode UND globaler Threshold).
  Das ist semantisch konsistent mit der bisherigen UI-Verwendung
  (`get_score_contributions` → `efficiency.has_data`).

## Dateien

- `run_trend/analytics/training_score.py`
- `run_trend/ui/summary_panel.py`
- `run_trend/translations/runtrend_{de,en}.{ts,qm}`
- `tests/test_analytics.py`
