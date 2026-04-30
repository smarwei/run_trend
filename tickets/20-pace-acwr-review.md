# 20 — Pace als ACWR-Komponente überdenken

**Priorität:** P3
**Kategorie:** Methodisch / Diskussion vor Code

## Problem

`run_trend/analytics/training_load.py:119-121, 144-148` benutzt Pace als eine der
ACWR-Komponenten (mit invertierter Logik: schnellerer Pace = höhere Last).

Mathematisch konsistent. **Aber methodisch problematisch:**

- Wenn ein Läufer dauerhaft schneller wird (Fitness-Gewinn), erhöht sich der
  ACWR-Pace-Beitrag → die UI warnt vor „Übertraining"
- Das ist falsche Pathologisierung von Progression
- Gabbett (2016) basiert ACWR ursprünglich auf **Volumen** und **Trainingsbelastung**
  (RPE × Dauer), nicht auf Pace

## Optionen

1. **Pace-Komponente ganz weglassen** — ACWR nur aus Volumen + Dauer
2. **Trainingslast-Proxy statt nackter Pace** — `Volumen × (1/Pace)` ergibt
   „Equivalent Distance at threshold" → besser als isolierte Pace
3. **Aktueller Stand belassen, aber dokumentieren** — Tooltip im Chart, der das
   Caveat erklärt

## Acceptance (nach Diskussion)

- [x] Methodische Entscheidung dokumentiert in `specification_update.md`
- [x] Code-Anpassung gemäß gewählter Option
- [x] Falls 1 oder 2: bestehende Tests in `tests/test_analytics.py` aktualisieren

## Dateien

- `specification_update.md` (Diskussion)
- `run_trend/analytics/training_load.py:119-121, 144-148`
- `tests/test_analytics.py`

## Bemerkung

Vor Code-Change zwingend diskutieren — ACWR ist eine zentrale, sichtbare Metrik.

## Status / Fortschritt

**Vollständig umgesetzt — Option 3 (Document-only) gewählt.**

- ✅ `specification_update.md` §13 hinzugefügt: drei Optionen besprochen,
  Option 3 begründet ausgewählt (kein Behavior-Change ohne explizite
  Diskussion mit dem User; Pace-Caveat sichtbar machen, Formel
  unverändert lassen). Revisit-Trigger dokumentiert.
- ✅ `run_trend/charts/training_load_chart.py`: Tooltip um den
  Pace-Caveat-Absatz erweitert ("faster pace = higher load …
  fitness-driven pace improvement can push the score upward …").
- ✅ Übersetzungen: Quell- und Zielstring in `runtrend_de.ts` /
  `runtrend_en.ts` ausgetauscht; `.qm` regeneriert (375 DE / 370 EN —
  unverändert in der Anzahl, weil ein einzelner String erweitert wurde).
- ✅ `tests/test_analytics.py`: keine Änderung nötig — Verhalten der
  ACWR-Berechnung bleibt identisch. Volle Suite weiterhin 254 grün.
- ✅ Keine Code-Anpassung an `training_load.py` (Option 3 = bewusst
  formelfrei).

### Annahmen

- Der Caveat-Absatz wurde an die bestehende `?`-Tooltip-Erklärung im
  TrainingLoadChart angehängt, statt einen neuen UI-Slot zu öffnen —
  konsistent mit der Konvention der anderen Charts (T05).
- DE-Übersetzung erlaubt den englischen Begriff "Caveat" als Lehnwort
  (ohne deutsche Übersetzung), da er im Sprachgebrauch der App
  geläufig ist und kürzer als "Einschränkung/Vorbehalt" bleibt.
- Keine spezifikations-Konsequenzen für §10 (Score-Mapping) — der
  Mapping-Schwellwert bleibt unverändert; nur die Lesart wird
  zusätzlich kontextualisiert.
- Spätere Optionen (1 oder 2) bleiben offen und sind in §13 als
  Revisit-Bedingung dokumentiert.
