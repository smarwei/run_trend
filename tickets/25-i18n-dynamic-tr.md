# 25 — i18n: Dynamische `tr()`-Calls statisch machen

**Priorität:** P0
**Kategorie:** Spec-Konformität / i18n

## Problem

`pylupdate6` extrahiert nur **statische String-Literale** aus `self.tr(...)`.
Aufrufe der Form `self.tr(variable)` werden vom Tooling übersehen — die
deutschen Strings landen nie in `runtrend_de.ts` und erscheinen daher im
deutschen UI **immer auf Englisch**.

Betroffene Stellen:

- `run_trend/charts/training_load_chart.py:72` — `self.tr(name)` mit
  `name ∈ {"Safe Zone (40-65)", "Caution Zone (65-80)", "Danger Zone (80+)"}`
- `run_trend/charts/projection_chart.py:264` — `self.tr(milestone_name)` mit
  `milestone_name ∈ {"10K Run", "15K Run", "Half Marathon", "30K Run",
  "Marathon Ready"}`

Verifikation: `grep -c "Safe Zone\|Marathon Ready"
run_trend/translations/runtrend_de.ts` liefert `0`.

## Lösungsansatz

`tr()` direkt an der Quelle des Literals platzieren, nicht erst am
Anwendungspunkt. Pattern: an der Definitionsstelle des Dicts/der Konstante
die englischen Strings stehen lassen und einen `_translate(self)`-Helper
oder eine Dict-Comprehension nutzen, die alle Werte einmal durch
`self.tr(static_literal)` zieht.

Konkret für die Zonen-Liste:

```python
def _zone_labels(self):
    return {
        "Safe Zone (40-65)": self.tr("Safe Zone (40-65)"),
        "Caution Zone (65-80)": self.tr("Caution Zone (65-80)"),
        "Danger Zone (80+)": self.tr("Danger Zone (80+)"),
    }
```

…und beim Render `self._zone_labels()[name]` statt `self.tr(name)`. Analog
für `LONG_RUN_MILESTONES`.

## Acceptance

- [x] Alle acht Strings (3 Zonen + 5 Meilensteine) liegen als statisches
      `tr()`-Literal vor
- [x] `pylupdate6` extrahiert sie in `runtrend_en.ts` und `runtrend_de.ts`
- [x] DE-Übersetzungen ergänzt
- [x] `.qm` regeneriert
- [x] Visual-Check: deutsche UI zeigt "Sichere Zone" / "Marathon-bereit"

## Annahmen

- Übersetzung der Milestone-Namen darf eindeutschen ("Halbmarathon" für
  "Half Marathon"), aber Distanz-Kürzel wie „10K" sollten erhalten
  bleiben — gleicher Stil wie im Strava-UI.
- "Safe / Caution / Danger Zone" wird so übersetzt wie der TRIMP-Tooltip
  aus T05 — Konsistenz wahren.

## Dateien

- `run_trend/charts/training_load_chart.py`
- `run_trend/charts/projection_chart.py`
- `run_trend/translations/runtrend_de.ts`
- `run_trend/translations/runtrend_en.ts`
- `run_trend/translations/*.qm`

## Status / Fortschritt

**Vollständig umgesetzt.**

- ✅ `training_load_chart.py`: `_zone(lo, hi, color_rgba, translated_name)`
  bekommt jetzt einen vorab-übersetzten Namen statt einer Variablen. Die
  drei Aufrufstellen rufen `self.tr("Safe Zone (40-65)")` etc. mit dem
  statischen Literal direkt vor Ort — pylupdate6 sieht den String und
  kann ihn extrahieren.
- ✅ `projection_chart.py`: Neue Methode `_tr_milestone(name)` mit
  Lookup-Dict, das alle 7 bekannten Namen aus `Forecaster.MILESTONES`
  und `LONG_RUN_MILESTONES` als statische `self.tr("…")`-Literale
  enthält. Aufruf an Zeile 264 jetzt `self._tr_milestone(milestone_name)`.
  Unbekannte Namen fallen unübersetzt durch.
- ✅ Insgesamt 10 neue Source-Strings (7 Meilensteine + 3 Zonen) in
  `runtrend_de.ts` und `runtrend_en.ts` ergänzt. DE-Übersetzungen:
  Halbmarathon, Marathon-bereit, 10-km-Lauf, 15-km-Lauf, 30-km-Lauf,
  Sichere Zone (40-65), Vorsichtszone (65-80), Gefahrenzone (80+).
  „5K" und „10K" bleiben unverändert (Distanz-Kürzel — Strava-Stil).
- ✅ `lrelease` regeneriert: 385 DE (vorher 375) / 380 EN (vorher 370).
- ✅ Neuer Test `tests/test_chart_i18n.py` mit 7 Cases:
  `_tr_milestone`-Fallback für unbekannte Namen, alle 7 Milestones
  liefern non-empty Strings, alle 10 Source-Strings im DE/EN .ts
  vorhanden, DE-Stichproben tatsächlich übersetzt (Halbmarathon,
  Marathon-bereit, Sichere Zone).
- ✅ `pytest tests/` 271 grün (264 + 7 neue).

### Annahmen

- „Marathon Ready" → „Marathon-bereit" (statt „Marathon-fertig", das im
  Sprachgebrauch geläufig wäre): „bereit" ist im Kontext einer
  Vorbereitungs-App präziser („zur Vorbereitung bereit") und schiebt nicht
  die Erwartung in Richtung „ich habe ihn schon gelaufen".
- „10K Run" → „10-km-Lauf" mit Bindestrichen: Duden-konformer als
  „10K-Lauf", konsistent mit „Langer Lauf" / „Historischer langer Lauf"
  weiter oben im selben Kontext.
- ProjectionChart hat jetzt eine `_tr_milestone`-Methode anstelle eines
  Klassen-Konstanten-Dicts. Grund: `self.tr()` braucht eine Instanz für
  Qt's Translation-Context; eine Klassen-Konstante würde beim Import
  ausgewertet, wo noch keine QApplication existiert.
- Manuelle `.ts`-Edits statt `pylupdate6`-Regenerierung, weil das
  Projekt aktuell ohne pylupdate6 in der Toolchain auskommt (existierende
  Strings sind im Repo auch manuell gepflegt). Das verkleinert das
  Diff-Surface — der bestehende `<location>`-Kram bleibt unangetastet.
