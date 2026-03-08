# Flatpak Build Instructions

This document describes how to build and test the Flatpak package for Running Progress Tracker.

## Prerequisites

Install flatpak and flatpak-builder:

```bash
# On Debian/Ubuntu
sudo apt install flatpak flatpak-builder

# On Fedora
sudo dnf install flatpak flatpak-builder

# On NixOS (using nix-shell)
nix-shell -p flatpak flatpak-builder
```

Add Flathub repository:

```bash
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
```

Install the KDE runtime and SDK:

```bash
flatpak install flathub org.kde.Platform//6.7 org.kde.Sdk//6.7
```

## Building the Flatpak

### Local Development Build

```bash
# Build the Flatpak
flatpak-builder --force-clean --user --install build-dir de.arne-weiss.RunTrend.json

# Run the app
flatpak run de.arne-weiss.RunTrend
```

### Creating a Bundle

To create a single-file bundle for distribution:

```bash
# Build and export to repository
flatpak-builder --repo=repo --force-clean build-dir de.arne-weiss.RunTrend.json

# Create bundle
flatpak build-bundle repo run-trend.flatpak de.arne-weiss.RunTrend

# Install the bundle
flatpak install run-trend.flatpak

# Run the app
flatpak run de.arne-weiss.RunTrend
```

## Testing

```bash
# Run with verbose output
flatpak run -v de.arne-weiss.RunTrend

# Run with shell access for debugging
flatpak run --command=sh de.arne-weiss.RunTrend
```

## Submitting to Flathub

1. Fork the [Flathub repository](https://github.com/flathub/flathub)
2. Create a new repository named `de.arne-weiss.RunTrend`
3. Copy the manifest file (`de.arne-weiss.RunTrend.json`) to the repository
4. Submit a pull request to Flathub

### Flathub Requirements Checklist

Before submitting to Flathub, ensure:

- [ ] AppData file (`de.arne-weiss.RunTrend.metainfo.xml`) is valid
  ```bash
  appstream-util validate de.arne-weiss.RunTrend.metainfo.xml
  ```

- [ ] Desktop file is valid
  ```bash
  desktop-file-validate de.arne-weiss.RunTrend.desktop
  ```

- [ ] Screenshots are added to AppData
  - At least one screenshot (1600x900 recommended)
  - Screenshots should be in PNG format
  - Add to `screenshots/` directory

- [ ] Icon is in the correct format
  - 512x512 PNG minimum
  - Named `de.arne-weiss.RunTrend.png`

- [ ] All URLs are updated
  - Replace `https://github.com/your-username/run-trend` with actual repository
  - Update commit hash in manifest

- [ ] License is clear
  - `project_license` in MetaInfo matches LICENSE file

- [ ] App runs in Flatpak sandbox without issues
  - Test file system access
  - Test network connectivity (Strava API)

## Updating the Flatpak

When releasing a new version:

1. Update version in:
   - `pyproject.toml`
   - `de.arne-weiss.RunTrend.metainfo.xml` (add new release entry)
   - `app/ui/about_dialog.py`

2. Update manifest:
   - Change `tag` to new version (e.g., `v0.2.0`)
   - Update `commit` hash

3. Rebuild and test

4. Submit update PR to Flathub repository

## Troubleshooting

### Build fails with "No module named 'app'"

Ensure `pyproject.toml` is properly configured with all package directories.

### App doesn't start in Flatpak

Check permissions in the manifest's `finish-args` section. The app needs:
- Network access for Strava API
- Filesystem access for local database

### Icons not showing

Verify icon paths:
- Icon file must be in `icons/hicolor/512x512/apps/`
- Icon must be named `de.arne-weiss.RunTrend.png`
- Desktop file must reference correct icon name

## Resources

- [Flatpak Documentation](https://docs.flatpak.org/)
- [Flathub Submission Guide](https://docs.flathub.org/docs/for-app-authors/submission)
- [AppData Guidelines](https://www.freedesktop.org/software/appstream/docs/chap-Metadata.html)
