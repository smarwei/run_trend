# 39 — Training-Score als „Trend-Indikator" labeln (oder ersetzen)

**Priorität:** P1
**Kategorie:** UX / Methodische Klarheit

## Problem

Der bestehende „Training Score" (`run_trend/analytics/training_score.py`,
Konfiguration in `specification.md` §10) ist **explizit selbst-relativ**:
jede Komponente vergleicht die aktuelle Periode gegen ein rollendes
Eigen-Baseline. Konsequenz, die zwei Nutzer-Beobachtungen auslöste:

> „Häufigkeit 3.7/20 obwohl ich jeden zweiten Tag laufe" (durch T-Fix
> in `40606f8` auf die letzte abgeschlossene Periode umgestellt — half,
> löste aber das Grund-Problem nicht).
>
> „Es wäre seltsam, wenn ich irgendwann super leistungsfähig bin und
> mein Wert dann auf 50% sinkt. Eine Verdopplung der Trainings­häufigkeit
> ist weder realistisch noch erstrebenswert."

Stimmt — bei stabilen 7×/Woche-Routinen läuft die Baseline mit, der
Score pendelt konstruktionsbedingt um ~50. **Das ist kein Bug**, sondern
die Spec-Wahl „rolling baseline" mit 2×-Cap. Aber die UI suggeriert
über die 0–100-Skala und die Farb-Codierung (Rot/Grün) etwas anderes:
„höher = besser, fitter, in Form". Das stimmt nur in Ramp-up-Phasen.

T38 hat das Symptom (Plateau) durch eine **absolute** Größe daneben
adressiert: Training Fitness (CTL) bleibt im Steady-State hoch und
zeigt das tatsächliche Niveau. Aber:

- **Doppelanzeige verwirrt** — Score 54 und Training Fitness 70 in
  derselben Box ohne Erklärung was was bedeutet.
- **Score ist immer noch prominenter** (24px, fett, farbig) als
  Fitness (11px) — also liest der User den ad-hoc Wert zuerst.
- **„Score" ist semantisch falsch** für eine selbst-relative Größe.
  Ein Score ist üblicherweise absolut.

## Lösungsansatz

Drei Optionen, von minimal bis maximal:

### Option A — Umbenennen + entzerren (empfohlen)

- **Label** „Training Score" → **„Training Trend"** (DE: „Trainings-Trend")
- Subtitle unter dem Wert: „relativ zu deinem Baseline" / „relative to
  your baseline" (statisch eingeblendet, nicht versteckt im Tooltip)
- **Visuelle Hierarchie umkehren**: Training Fitness wird der
  prominente 24px-Wert, Training Trend rutscht auf 18px und schließt
  optisch an die Score-Komponenten an
- Farb-Codierung des Trend-Werts überdenken: Rot/Grün vs. Baseline
  bleibt sinnvoll, da hier Veränderung wirklich gemessen wird
- Bestehende Score-Komponenten („Breakdown") behalten Sinn unter dem
  neuen Trend-Label

### Option B — Score ersatzlos entfernen

CTL/TSB übernehmen die „wie steht es um meine Fitness"-Frage komplett.
Der Score wird gelöscht. Vorteile: keine Verwirrung mehr. Nachteile:
das Trending-Signal (sehe ich mich gerade steigern oder abbauen?) geht
verloren, und ältere Nutzer haben das Score-Verhalten verinnerlicht.

### Option C — Grounded Composite

Ein neuer, publikations-basierter 0–100-Indikator. Kandidaten:

- **Polarisations-Index**: Anteil Zeit in Z1+Z2 (Ziel ~80 %). Aus
  T19-HR-Zonen ableitbar.
- **CTL-Perzentil** der eigenen Historie über z. B. 2 Jahre.
- **Composite aus CTL × TSB-Faktor**: Fitness × Form-Modifikator.

Mehr Aufwand, mehr Diskussion vor Implementierung nötig.

**Empfehlung: Option A**. Niedrigster Risiko, höchster Klarheits-Gewinn,
respektiert die jetzige Investition in den bestehenden Score.

## Acceptance (für Option A)

- [ ] **UI-Label** in `summary_panel.py` von „Score" → „Trend"
      (`score_label` und seine Tooltip-Hilfe entsprechend angepasst)
- [ ] **Subtitle** „relative to your baseline" (DE: „relativ zu deinem
      Baseline") als statisches `QLabel` direkt unter dem Trend-Wert
- [ ] **Visuelle Hierarchie umgekehrt**: Training Fitness (CTL) wird
      der prominente 24px-Wert, Trend wird 18px
- [ ] **Tooltip** des neuen Trend-Werts erklärt explizit:
  - Vergleich mit eigenem Baseline, nicht mit Absolut-Standards
  - Steady-State ≈ 50, ist *nicht* schlecht
  - Hohe Werte heißen „du steigerst dich gerade", nicht „du bist fit"
- [ ] **Übersetzungen**: DE/EN, `.qm` regeneriert
- [ ] **Manual-Update**: bestehende „Training Score (0-100)"-Sektion
      umtitelt + Zusatz-Absatz „Warum Trend statt Score?"
- [ ] **Specification** `§10` umtitelt von „Training Status Score" auf
      „Training Status Trend Indicator" mit Hinweis auf §10a (CTL).
      Anmerkung zu Score-Plateau-Phänomen ergänzt.

## Methodische Punkte (vor Code klären)

1. **Score behalten oder löschen?**: Option A vs. B. Empfehlung A wegen
   Trending-Wert; löschen wäre konsequenter aber löscht echte Info.
2. **Skala beibehalten?**: 0–100 bleibt oder Wechsel auf %?
   Beibehalten — weniger Migration, gleicher Wertebereich.
3. **Color-Coding-Schwellen**: Rot/Gelb/Grün-Schwellen bleiben oder
   neu kalibrieren? Empfehlung beibehalten (30/60/80) — semantisch
   passt „rot bei Trend < 30" = „du bist deutlich unter deinem
   Baseline".
4. **Spec §10 ändern**: ja, mit Verweis auf §10a (T38 hat sie schon
   in spec-implizit eingeführt, hier sauber dokumentiert).

## Slice-Plan

1. UI-Umbenennung + Subtitle + Hierarchie-Tausch + Tooltip-Erweiterung.
2. Translations.
3. Manual-Update + spec.md-Erweiterung.

Alles in einem Slice mergeable, weil die Änderungen klein und
zusammenhängend sind.

## Dateien

- `run_trend/ui/summary_panel.py` (Labels, Stile, Subtitle)
- `run_trend/translations/runtrend_de.ts` + `runtrend_en.ts` (+ `.qm`)
- `MANUAL_de.md` / `MANUAL_en.md` (Score-Sektion umtitelt)
- `specification.md` (§10-Titel + §10a-Verweis)

## Out of Scope

- **Score-Formel verändern** — sie bleibt unverändert, nur die
  Anzeige-Semantik wird ehrlicher.
- **Komponenten-Gewichte rebalancieren** — separate Diskussion.

## Quellen

- Bestehender Score-Algorithmus: `run_trend/analytics/training_score.py`
  und `specification.md` §10.
- T38 (CTL/ATL/TSB als absolute Companion-Metrik, Commit-Reihe
  `2acb65a` / `6b10e1c` / `1386d0a` / `cef58cd`).
- T20 (Pace-als-ACWR-Komponente überdenken — gleicher Spannungsfeld
  „selbstrelativ vs. absolut").
