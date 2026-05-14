# 41 — Methodische Caveats in Metrik-Tooltips ergänzen

**Priorität:** P0
**Kategorie:** Methodische Ehrlichkeit / UX

## Problem

Mehrere App-Metriken sind entweder forschungs-basiert aber kontrovers
(ACWR), forschungs-basiert mit bekannten Skalierungs-Unterschieden
(CTL aus TRIMP vs. TSS), aus etablierter Praxis aber ohne Peer-Review
(McMillan Race-Predictions) oder explizit selbst-zusammengestellt
(Training-Score, EF-Self-Calibrated-Variante). Aktuell verschweigen
die Tooltips diese Spannungen — die Anzeige wirkt durchgängig
„wissenschaftlich begründet", was nicht stimmt.

Beispiele für aktuell **fehlende** Caveats:

| Metrik | Stand | fehlt im Tooltip |
|---|---|---|
| ACWR | Gabbett 2016 | Impellizzeri-2020-Kritik (mathematische Artefakte, schwache Verletzungs-Korrelation) |
| Training Fitness (CTL) | Banister/Coggan | TRIMP-Skala ≠ TSS-Skala, Vergleich mit TrainingPeaks-Werten irreführend |
| Race Predictions | McMillan-Kalkulator | nicht peer-reviewed, empirisch verbreitet |
| EF Aerobic Capacity (Performance-Tab B) | Self-Calibrated | keine publizierte Methodik, Personal-Peak-Approximation |
| Training Score (0-100) | Spec §10 | ad-hoc gewählte Gewichte, plateau-anfällig im Steady-State (T39 adressiert das eigene UI-Label) |
| TRIMP (Banister) | Banister 1991 | Edwards-Zone-TRIMP wäre Alternative; gender-b-Faktor ist statistischer Mittel-Effekt, nicht individuell |

**Auswirkung:** Nutzer lesen Zahlen wie absolute Wahrheiten und treffen
Trainings-Entscheidungen darauf basierend. Eine ehrliche
Methoden-Disclosure im Tooltip vermeidet das.

## Lösungsansatz

Jeder Metrik-Tooltip endet mit einem **Caveat-Absatz**, der die wichtigste
Limitation in 1–3 Sätzen nennt. Format konsistent: am Tooltip-Ende, durch
eine Leerzeile getrennt, eingeleitet mit „Caveat:".

### Audit-Liste (sechs Touch-Points)

#### 1. ACWR — `run_trend/charts/training_load_chart.py:22`

Tooltip schon ausführlich (T05/T20). Ergänzen am Ende:

> Caveat: Gabbett's Sweet-Spot-Bänder (2016) sind empirisch verbreitet
> aber wissenschaftlich umstritten (Impellizzeri et al. 2020 zeigen
> mathematische Artefakte bei kleinen chronic-Werten und schwache
> Verletzungs-Korrelation in Follow-up-Studien). Lies ACWR als
> *Indikator*, nicht als Diagnose.

#### 2. Training Fitness (CTL) — `run_trend/ui/summary_panel.py` (T38)

Tooltip nach „Typical ranges" ergänzen:

> Caveat: RunTrend's CTL ist **TRIMP-basiert** (Banister), nicht
> TSS-basiert wie bei TrainingPeaks. Die absoluten Zahlen sind nicht
> direkt vergleichbar — relative Einordnung (recreational / trained /
> competitive) gilt analog, exakte Werte unterscheiden sich. Wenn du
> CTL-Werte aus anderen Apps hast, erwarte einen Skalen-Versatz.

#### 3. Race Predictions — `run_trend/ui/summary_panel.py` (existiert)

Tooltip ergänzen:

> Caveat: Vorhersagen basieren auf dem McMillan Running Calculator
> (verbreitet, aber nicht peer-reviewed). Reale Wettkampfzeiten hängen
> von Tagesform, Strecke, Wetter, Tapering und mentaler Leistung ab —
> bei 5K-Vorhersagen ist die Streuung kleiner, bei Marathon-Vorhersagen
> erheblich (±10 % nicht ungewöhnlich).

#### 4. EF Aerobic Capacity (Performance-Tab) — `run_trend/charts/age_grading_chart.py:91`

Schon transparent mit „We do NOT compare your EF to other athletes",
ein Caveat-Satz dazu:

> Caveat: Die Decline-Rate ist eine lineare Approximation aus
> Coppola 2022. Sie funktioniert gut bis ~Alter 70, ab dort
> beschleunigt sich der Decline (mitochondriale Mechanismen). Die
> Personal-Peak-Methodik selbst ist nicht publiziert — sie nutzt
> die Friel-EF-Konvention konsistent, aber das spezifische Modell ist
> RunTrend-internes Design.

#### 5. Training Score 0-100 — `run_trend/ui/summary_panel.py`

T39 ändert das Label auf „Trend". Caveat-Erweiterung des Tooltips:

> Caveat: Diese Skala ist **selbst-zusammengestellt** (spec §10),
> nicht aus einer Publikation. Die Gewichte (30 % Distanz / 20 %
> Frequenz / 30 % Pace / 20 % EF) sind plausibel, aber nicht
> empirisch optimiert. Im Steady-State pendelt der Wert um 50
> — das ist Design, nicht ein schlechtes Ergebnis. Für absolute
> Fitness siehe Training Fitness (CTL) darunter.

#### 6. TRIMP / Banister — *neuer* Help-Icon-Tooltip neben einem zukünftigen
„TRIMP heute"-Anzeige­wert? Oder im Manual? Empfehlung: nur im Manual
ausführlich, hier kein neuer Tooltip-Slot — TRIMP wird intern für CTL
benutzt aber nicht direkt angezeigt.

## Acceptance

- [ ] Tooltip-Erweiterungen wie oben aufgelistet, alle mit
      „Caveat:"-Marker am Ende
- [ ] Übersetzungen DE/EN für alle neuen Tooltip-Abschnitte,
      `.qm` regeneriert
- [ ] **Manual-Abschnitt „Methodische Caveats"** als eigene
      H2-Sektion in `MANUAL_de.md` / `MANUAL_en.md`, listet alle
      Metriken mit Quelle + bekannten Limitations in Tabellen-Form
- [ ] `pytest tests/` weiterhin grün (sollte trivial sein — reine
      String-Änderungen)
- [ ] T05-Test (`tests/test_chart_i18n.py` oder ähnlich) prüft
      mindestens: das Wort „Caveat" taucht in den großen Tooltips
      auf — niedrige Sensitivität, hohe Spezifität gegen Regression

## Methodische Punkte

1. **Wording**: „Caveat" (englisches Lehnwort, in der App schon
   etabliert durch T20-Tooltip) statt „Vorbehalt" oder
   „Einschränkung". Konsistenz mit bestehendem Caveat-Stil.
2. **Caveat-Länge**: 1–3 Sätze maximal. Längere Erläuterungen
   gehören ins Manual (Acceptance-Punkt #3).
3. **Konkretes Quellen-Zitat im Tooltip?**: Format
   „(Impellizzeri 2020)" ist kompakt; Tooltip wird nicht zu lang.
4. **Reihenfolge im Tooltip**: was die Metrik IST → Werte/Zonen →
   wie sie reagiert → **Caveat ans Ende**. Damit der Caveat nicht
   die Lektüre dominiert.

## Slice-Plan

Ein einziger Slice, weil:

- Alle Änderungen sind Tooltip-Text + Manual-Sektion
- Keine Code-Logik betroffen
- Übersetzungen folgen direkt mit
- Tests trivial

## Dateien

- `run_trend/charts/training_load_chart.py` (ACWR-Tooltip)
- `run_trend/charts/age_grading_chart.py` (EF-Tooltip)
- `run_trend/ui/summary_panel.py` (CTL, Race Predictions, Trend-Score)
- `run_trend/translations/runtrend_de.ts` / `runtrend_en.ts` (+ `.qm`)
- `MANUAL_de.md` / `MANUAL_en.md` (neue H2-Sektion „Methodische Caveats")
- ggf. `tests/test_chart_i18n.py` (Caveat-Präsenz-Test)

## Out of Scope

- **Methodik-Änderungen** — das ist T39 (Score), T40 (ACWR).
- **Neue Metriken** — nichts wird ergänzt, nur transparent gemacht.
- **Konfigurierbare „Strict-Mode"-Variante** ohne Caveats für Power-
  User — Caveats stehen für alle, immer.

## Quellen

- Bestehende Caveat-Konvention: T20 (`tickets/20-pace-acwr-review.md`),
  Implementierung in `training_load_chart.py:22-35`.
- Impellizzeri 2020 — siehe T40.
- Coppola 2022 — siehe T37.
- Spec §10 — Self-Reference: der existierende Score-Algorithmus.
