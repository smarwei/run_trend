# Flathub Submission Guide

Dieser Guide erklärt die Schritte für die Flathub-Veröffentlichung.

## ✅ Bereits erledigt

- ✅ MetaInfo-Datei vorbereitet (`de.arneweiss.RunTrend.metainfo.xml`)
- ✅ Desktop-Datei validiert (`de.arneweiss.RunTrend.desktop`)
- ✅ Flatpak-Manifest lokal getestet (`de.arneweiss.RunTrend.json`)
- ✅ Flatpak-Manifest für Flathub vorbereitet (`de.arneweiss.RunTrend.json.github`)
- ✅ Screenshot hinzugefügt (`screenshots/main-window.png`)
- ✅ Übersetzungsdateien korrekt paketiert (via Python packaging)
- ✅ Manual-Dateien installiert (via post-install)
- ✅ Lokaler Flatpak-Build erfolgreich getestet
- ✅ Alle Dateien committed
- ✅ Git Tag v0.1.0 aktualisiert (Commit: `ea06c155f6769f092bb52f68d294b3c10ee67d70`)
- ✅ Statische Website erstellt (`docs/index.html`)
- ✅ GitHub Actions Workflow für automatische Builds konfiguriert (`.github/workflows/release.yml`)
- ✅ Briefcase-Konfiguration aktualisiert

## 📋 Nächste Schritte

### 1. Git Tag und Änderungen pushen

**NOCH ZU TUN:**

```bash
# Alle Commits und den aktualisierten Tag pushen
git push origin master
git push origin v0.1.0 --force
```

**Wichtig:** Nach dem Push:
- Screenshot-Link ist live und die MetaInfo-Validierung sollte erfolgreich sein
- GitHub Actions baut automatisch die Binaries (Windows .msi, macOS .dmg, Linux AppImage)
- Die Website wird live unter: https://runtrend.arne-weiss.de

### 2. Flathub Repository vorbereiten

**Schritt 2.1: Flathub Repository forken**

1. Gehe zu https://github.com/flathub/flathub
2. Klicke auf "Fork" (oben rechts)
3. Fork wird in deinem Account erstellt: `https://github.com/<dein-username>/flathub`

**Schritt 2.2: Fork lokal klonen**

```bash
cd ~/projects
git clone https://github.com/<dein-username>/flathub.git
cd flathub
git checkout new-pr
```

**Schritt 2.3: Feature Branch erstellen**

```bash
git checkout -b add-runtrend
```

**Schritt 2.4: App-Dateien hinzufügen**

Kopiere die drei benötigten Dateien (WICHTIG: `.json.github` wird zu `.json`):

```bash
# Von deinem run_trend Projekt-Verzeichnis
cp ~/projects/run_trend/de.arneweiss.RunTrend.json.github de.arneweiss.RunTrend.json
cp ~/projects/run_trend/de.arneweiss.RunTrend.desktop .
cp ~/projects/run_trend/de.arneweiss.RunTrend.metainfo.xml .
```

**Was diese Dateien enthalten:**

✅ **de.arneweiss.RunTrend.json** (von .json.github):
- Git source: `https://github.com/smarwei/run_trend.git`
- Tag: `v0.1.0`
- Commit: `ea06c155f6769f092bb52f68d294b3c10ee67d70`
- Translation files automatisch via Python packaging
- Manual files via post-install
- Alle Icons installiert

✅ **de.arneweiss.RunTrend.metainfo.xml**:
- AppStream-konform
- Screenshot von GitHub
- Vollständige Feature-Liste

✅ **de.arneweiss.RunTrend.desktop**:
- Desktop Entry Standard
- Kategorien: Sports, Utility

**Schritt 2.5: Commit und Push**

```bash
git add de.arneweiss.RunTrend.json de.arneweiss.RunTrend.desktop de.arneweiss.RunTrend.metainfo.xml
git commit -m "Add de.arneweiss.RunTrend"
git push origin add-runtrend
```

### 3. Pull Request erstellen

**Schritt 3.1: PR auf GitHub öffnen**

1. Gehe zu deinem Fork: `https://github.com/<dein-username>/flathub`
2. GitHub zeigt automatisch einen "Compare & pull request" Button → klicken
3. **WICHTIG:** Stelle sicher, dass der PR gegen `flathub:new-pr` geht (NICHT `master`)
4. **Title**: `Add de.arneweiss.RunTrend`
5. **Description**:

```markdown
New app submission: Running Progress Tracker

A desktop application for tracking and analyzing running progress from Strava.

**Features:**
- Strava OAuth integration with automatic sync
- Heart rate analytics and aerobic fitness tracking
- Race time predictions
- Full internationalization (German/English)
- Privacy-focused local storage

**Compliance:**
- MIT License with Commons Clause (allows free distribution)
- Human-authored code, tested and verified
- AppStream metadata validated
- Desktop file validated
```

**Schritt 3.2: Review-Prozess**

- Flathub Maintainer werden den PR reviewen
- Sie können Änderungen anfordern
- Nach Approval wird die App auf Flathub veröffentlicht
- Du erhältst Write-Access zum neuen `flathub/de.arneweiss.RunTrend` Repository

## 🔍 Pre-Submission Checklist

Vor dem PR checke nochmal:

- [x] Lokaler Flatpak-Build funktioniert
- [x] Übersetzungen funktionieren im Flatpak
- [x] Manual funktioniert im Flatpak
- [x] Screenshot ist auf GitHub verfügbar (nach Push)
- [x] Git commit hash in .json.github ist korrekt: `ea06c155f6769f092bb52f68d294b3c10ee67d70`
- [ ] GitHub Tag v0.1.0 ist gepusht (NOCH ZU TUN)
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

## 🌐 Website und Automatische Builds

### GitHub Pages Website

Die App hat jetzt eine professionelle statische Website unter `docs/index.html`:
- URL: https://runtrend.arne-weiss.de
- Zeigt Features, Screenshots, und Download-Links
- Modern und responsive Design mit sportlichem Thema
- Automatische Integration mit GitHub Releases API
- Custom Domain via CNAME-Datei konfiguriert

### GitHub Actions Workflow

Der Workflow `.github/workflows/release.yml` baut automatisch bei jedem Tag-Push (v*.*.*):

**Windows Build:**
- Erstellt `.msi` Installer via Briefcase
- Upload als Release Asset

**macOS Build:**
- Erstellt `.dmg` Installer via Briefcase
- Universal Binary (Intel + Apple Silicon)
- Upload als Release Asset

**Linux:**
- Kein separater Build in GitHub Actions
- Linux-Nutzer verwenden Flatpak über Flathub

**Release:**
- Erstellt automatisch GitHub Release
- Generiert Release Notes
- Alle Binaries als Downloads verfügbar

### GitHub Pages und Custom Domain aktivieren

**Nach dem Push musst du GitHub Pages aktivieren:**

1. **GitHub Pages aktivieren:**
   - Gehe zu Repository Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `master` (oder `main`)
   - Folder: `/docs`
   - Custom domain: `runtrend.arne-weiss.de`
   - "Enforce HTTPS" aktivieren (nach DNS-Propagation)
   - Save

2. **DNS konfigurieren:**

   Bei deinem DNS-Provider (z.B. wo arne-weiss.de gehostet ist) musst du einen CNAME-Record erstellen:

   ```
   Type: CNAME
   Name: runtrend
   Value: smarwei.github.io
   TTL: 3600 (oder Auto)
   ```

   Nach DNS-Propagation (kann bis zu 24h dauern, meist aber nur wenige Minuten) ist die Website unter https://runtrend.arne-weiss.de verfügbar.

## 🔗 Hilfreiche Links

- Website: https://runtrend.arne-weiss.de
- GitHub Repository: https://github.com/smarwei/run_trend
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
