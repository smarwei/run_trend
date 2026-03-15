# Flathub Submission Guide

Dieser Guide erklärt die nächsten Schritte für die Flathub-Veröffentlichung.

## ✅ Bereits erledigt

- ✅ MetaInfo-Datei vorbereitet (`de.arneweiss.RunTrend.metainfo.xml`)
- ✅ Desktop-Datei validiert (`de.arneweiss.RunTrend.desktop`)
- ✅ Flatpak-Manifest aktualisiert (`de.arneweiss.RunTrend.json`)
- ✅ Screenshot hinzugefügt (`screenshots/main-window.png`)
- ✅ Alle Dateien committed

## 📋 Nächste Schritte

### 1. Git Tag aktualisieren und pushen

Der Tag `v0.1.0` zeigt noch auf einen alten Commit. Wir müssen ihn auf den aktuellen Stand bringen:

```bash
# Aktuellen Tag löschen (lokal)
git tag -d v0.1.0

# Neuen Tag auf aktuellem Commit erstellen
git tag v0.1.0

# Alle Commits und den aktualisierten Tag pushen
git push origin master --force-with-lease
git push origin v0.1.0 --force
```

**Wichtig:** Nach dem Push ist der Screenshot-Link live und die MetaInfo-Validierung sollte erfolgreich sein.

### 2. Flatpak-Build lokal testen (Optional, aber empfohlen)

```bash
# Flatpak Builder verwenden
flatpak-builder --force-clean --user --install build-dir de.arneweiss.RunTrend.json

# App testen
flatpak run de.arneweiss.RunTrend
```

Falls nicht installiert (NixOS):
```bash
nix-shell -p flatpak flatpak-builder
```

### 3. GitHub Release erstellen (Optional, aber empfohlen)

Gehe zu https://github.com/smarwei/run_trend/releases und erstelle einen neuen Release:
- Tag: `v0.1.0`
- Title: `Release 0.1.0`
- Description: Kopiere die Release Notes aus der MetaInfo-Datei

### 4. Flathub Repository vorbereiten

**Schritt 4.1: Flathub Repository forken**

1. Gehe zu https://github.com/flathub/flathub
2. Klicke auf "Fork" (oben rechts)
3. Fork wird in deinem Account erstellt: `https://github.com/<dein-username>/flathub`

**Schritt 4.2: Fork lokal klonen**

```bash
cd ~/projects
git clone https://github.com/<dein-username>/flathub.git
cd flathub
git checkout new-pr
```

**Schritt 4.3: Feature Branch erstellen**

```bash
git checkout -b add-runtrend new-pr
```

**Schritt 4.4: App-Dateien hinzufügen**

Kopiere die drei benötigten Dateien:

```bash
# Von deinem run_trend Projekt-Verzeichnis
cp ~/projects/run_trend/de.arneweiss.RunTrend.json .
cp ~/projects/run_trend/de.arneweiss.RunTrend.desktop .
cp ~/projects/run_trend/de.arneweiss.RunTrend.metainfo.xml .
```

**Schritt 4.5: Flathub Builder Lint ausführen**

```bash
# Flatpak Builder Lint Tool verwenden
flatpak run --command=flatpak-builder-lint org.flatpak.Builder manifest de.arneweiss.RunTrend.json
```

Falls Fehler auftreten, behebe sie und update die Dateien.

**Schritt 4.6: Commit und Push**

```bash
git add de.arneweiss.RunTrend.json de.arneweiss.RunTrend.desktop de.arneweiss.RunTrend.metainfo.xml
git commit -m "Add de.arneweiss.RunTrend"
git push origin add-runtrend
```

### 5. Pull Request erstellen

**Schritt 5.1: PR auf GitHub öffnen**

1. Gehe zu deinem Fork: `https://github.com/<dein-username>/flathub`
2. GitHub zeigt automatisch einen "Compare & pull request" Button → klicken
3. **WICHTIG:** Stelle sicher, dass der PR gegen `flathub:new-pr` geht (NICHT `master`)
4. Title: `Add de.arneweiss.RunTrend`
5. Description:
```
New app submission: Running Progress Tracker

A desktop application for tracking and analyzing running progress from Strava.

Features:
- Strava OAuth integration with automatic sync
- Heart rate analytics and aerobic fitness tracking
- Race time predictions
- Full internationalization (German/English)
- Privacy-focused local storage
```

**Schritt 5.2: Review-Prozess**

- Flathub Maintainer werden den PR reviewen
- Sie können Änderungen anfordern
- Nach Approval wird die App auf Flathub veröffentlicht
- Du erhältst Write-Access zum neuen `flathub/de.arneweiss.RunTrend` Repository

## 🔍 Pre-Submission Checklist

Vor dem PR checke nochmal:

- [ ] GitHub Tag v0.1.0 ist gepusht
- [ ] Screenshot ist auf GitHub verfügbar
- [ ] Desktop file ist valide: `desktop-file-validate de.arneweiss.RunTrend.desktop`
- [ ] MetaInfo ist valide: `appstream-util validate de.arneweiss.RunTrend.metainfo.xml`
- [ ] Manifest Lint ist sauber: `flatpak-builder-lint manifest de.arneweiss.RunTrend.json`
- [ ] Lokaler Build funktioniert (optional)
- [ ] PR geht gegen `new-pr` Branch (nicht `master`)
- [ ] GitHub 2FA ist aktiviert (für Write-Access nach Approval)

## 📚 Wichtige Hinweise

### Generative AI Policy

Flathub verbietet:
- Automatisch generierte PRs von AI-Bots
- Code, der hauptsächlich von AI ohne menschliche Review geschrieben wurde

**Für diese Submission:**
- ✅ Die App ist dein eigenes Projekt
- ✅ Du hast den Code verstanden und getestet
- ✅ Der PR wird von dir manuell erstellt
- ✅ Dies ist konform mit der Flathub AI Policy

### Lizenz

- Deine "MIT License with Commons Clause" ist für Flathub akzeptabel
- Sie erlaubt kostenlose Distribution (wie Flathub)
- Sie verbietet nur kommerziellen Verkauf
- Flathub verteilt kostenlos → kein Problem

## 🔗 Hilfreiche Links

- Flathub Submission Docs: https://docs.flathub.org/docs/for-app-authors/submission
- Flathub Requirements: https://docs.flathub.org/docs/for-app-authors/requirements
- App Maintenance Guide: https://docs.flathub.org/docs/for-app-authors/maintenance
- Flathub Matrix Chat: #flathub:matrix.org

## 🐛 Troubleshooting

**Screenshot-Link funktioniert nicht:**
```bash
# Stelle sicher, dass der Tag gepusht wurde
git push origin v0.1.0 --force
```

**Manifest Validation Fehler:**
```bash
# Führe Builder Lint aus
flatpak run --command=flatpak-builder-lint org.flatpak.Builder manifest de.arneweiss.RunTrend.json
```

**Build schlägt fehl:**
```bash
# Checke Logs
flatpak-builder --force-clean build-dir de.arneweiss.RunTrend.json
```

## ✉️ Kontakt

Bei Fragen kannst du:
- Im Flathub Matrix Chat fragen: #flathub:matrix.org
- Ein GitHub Issue im flathub/flathub Repository öffnen
- Die Flathub Docs konsultieren
