# 24 — Atomarer Config-Write + Thread-Lock + restriktive Rechte

**Priorität:** P0
**Kategorie:** Sicherheit / Robustheit

## Problem

`run_trend/settings/config.py:58-64` schreibt Settings naiv:

```python
def _save_settings(self):
    try:
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    except Exception:
        logger.exception("Error saving settings")
```

Daraus folgen drei Probleme:

1. **Nicht atomar.** Crash zwischen `open(...,'w')` und `json.dump`
   hinterlässt eine leere oder halb geschriebene `config.json` — und damit
   *alle* Auth-Daten weg. Besonders kritisch, weil der OAuth-Refresh aus
   einem Background-Thread `settings.set('strava_token_data', ...)`
   aufruft, also Crash-Risiko erhöht ist.
2. **Race-Condition.** UI-Thread (z.B. `settings.set('ui_period', 'month')`)
   und Refresh-Thread (`settings.set('strava_token_data', ...)`) schreiben
   parallel. Kein Lock — letzter Writer gewinnt, einer der Werte ist
   evtl. dauerhaft verloren.
3. **Standard-Rechte (0644)** auf einer Datei, die `client_secret`,
   `access_token` und `refresh_token` im Klartext enthält. Auf
   Multi-User-Linux ist der Inhalt für jeden lesbar.

## Lösungsansatz

```python
_lock = threading.Lock()

def _save_settings(self):
    with self._lock:
        path = Path(self.config_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode='w', dir=path.parent, delete=False, prefix='.config-', suffix='.tmp'
        ) as f:
            json.dump(self.settings, f, indent=2)
            tmp_path = Path(f.name)
        os.replace(tmp_path, path)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass  # best effort, Windows etc.
```

`os.replace` ist atomar auf POSIX und Windows ≥ Vista. `0o600` greift nur
nach dem Replace und ist Best-Effort (Flatpak-Sandbox: kein Problem,
schreibt das selbe XDG-Config-Dir).

## Acceptance

- [x] `_save_settings` nutzt `tempfile + os.replace`, nicht mehr `open('w')`
- [x] `_save_settings` ist durch ein Klassen-Level-`threading.Lock`
      geschützt; `set()` ruft `_save_settings()` im selben Lock-Pfad
- [x] `config.json` wird auf Erstanlage mit Mode `0o600` gespeichert
- [x] Test: simulierter Crash zwischen Tempfile und Replace
      (`os.replace` gemockt mit Raise) — alte Datei unverändert
- [x] Test: zwei parallele `set()`-Aufrufe aus Threads → beide Werte sind
      am Ende im JSON

## Annahmen

- Tempfile liegt im selben Verzeichnis wie die Zielfile, sonst kann
  `os.replace` über Filesystem-Grenzen hinweg scheitern.
- Keyring (Linux-Secret-Service / KWallet / GNOME-Keyring) wäre die
  saubere Lösung für `access_token` und `client_secret`, ist hier aber
  bewusst nicht im Scope — Flatpak-Permission-Modell + Plattform-Drift
  macht das größer als ein Quick-Win.
- `_lock` ist eine Klassen-Variable (`threading.Lock()` direkt im
  Klassenkörper), nicht Instanz-Variable, weil `AppSettings` aktuell als
  De-facto-Singleton genutzt wird (eine Instanz im MainWindow).

## Dateien

- `run_trend/settings/config.py`
- `tests/test_config.py` (neu, falls noch nicht vorhanden)

## Status / Fortschritt

**Vollständig umgesetzt.**

- ✅ `run_trend/settings/config.py`: Imports um `tempfile` und
  `threading` ergänzt, Klassen-Level-`_lock = threading.Lock()` direkt
  unter `DEFAULT_SETTINGS`. `_save_settings` neu:
  `NamedTemporaryFile(dir=parent, delete=False, prefix='.config-',
  suffix='.tmp', encoding='utf-8')` → `json.dump` → `os.replace` →
  `os.chmod(0o600)` (Best-Effort). Bei Fehler im Replace wird der
  Tempfile per `unlink` aufgeräumt, sodass kein Müll im Config-Dir
  liegen bleibt.
- ✅ Lock greift im gesamten Save-Pfad (`set` → `_save_settings`), schützt
  also auch die `json.dump`-Serialisierung von `self.settings` vor
  paralleler Mutation.
- ✅ `tests/test_config.py` (5 neu): `test_set_persists_to_disk`,
  `test_save_failure_preserves_existing_file` (mockt `os.replace` mit
  `OSError`, prüft Original-Bytes unverändert),
  `test_save_failure_cleans_up_tempfile`, `test_save_sets_restrictive_mode`
  (POSIX-only via `skipUnless`), `test_parallel_set_keeps_both_writes`
  (200 Iterationen × 2 Threads, JSON bleibt parseable und beide Keys
  überleben).
- ✅ `pytest tests/` 264 grün (259 + 5 neue).

### Annahmen (Implementierung)

- `tempfile.NamedTemporaryFile` legt das Tempfile mit Mode 0o600 an;
  auf POSIX vererbt `os.replace` die Source-Mode an die Zieldatei. Der
  zusätzliche `os.chmod` ist Defense-in-Depth (falls Filesystem
  Mode-Inheritance nicht garantiert oder das Replace eine bereits
  existierende 0644-Datei nur "in-place" überschreibt) und no-op auf
  POSIX, falls bereits 0600.
- `encoding='utf-8'` explizit gesetzt, damit Locale-unabhängig
  geschrieben wird (sonst hängt das Encoding von `locale.getencoding()`
  ab — bei alten C-Locales kann das ASCII sein und non-ASCII-Werte
  zerstören).
- Kein expliziter `mkdir` mehr in `_save_settings` — `__init__` legt das
  Verzeichnis bei Instanzierung an, und ein Mid-Session-Löschen des
  Config-Dirs ist außerhalb des Scopes.
