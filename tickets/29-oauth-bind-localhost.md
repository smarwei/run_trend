# 29 — OAuth-Callback-Server an `127.0.0.1` binden statt `0.0.0.0`

**Priorität:** P0
**Kategorie:** Sicherheit

## Problem

`run_trend/strava/simple_auth.py:233`:

```python
with socketserver.TCPServer(("", self.REDIRECT_PORT), CallbackHandler) as httpd:
```

Der leere Hostname `""` bindet auf alle Interfaces (`0.0.0.0`), also auch
LAN/WLAN. Während der OAuth-Flow läuft (typisch < 30 s) ist der Callback-
Server damit für jedes Gerät im gleichen Netzwerk erreichbar.

## Auswirkung auf Nutzer

Niedriges Risiko — der OAuth-Flow nutzt einen 16-Byte-zufälligen
`state`-Token, ohne den ein Angreifer den Code-Exchange nicht missbrauchen
kann. Trotzdem ist das exponierte Interface kein gewollter Zustand:

- Auf einem Café-WLAN startet der LAN-Scanner eines Mitkunden potenziell
  einen GET auf den offenen Port — der Server antwortet zwar mit Fehler,
  aber das ist unnötiges Logging-Geräusch und ein leichter Fingerprint.
- Flathub-Sandboxing schließt das nicht aus — der Port ist netzwerkweit
  offen, nicht nur in der Sandbox.

## Lösungsansatz

Bind explizit an Loopback:

```python
with socketserver.TCPServer(
    ("127.0.0.1", self.REDIRECT_PORT), CallbackHandler
) as httpd:
```

Browser-Redirect zeigt ohnehin auf `http://localhost:PORT/...`, das
Verhalten bleibt für den User identisch.

## Acceptance

- [x] Bind auf `"127.0.0.1"`
- [ ] OAuth-Flow manuell durchlaufen, Token wird empfangen
      (manuell zu verifizieren — Codeänderung selbst ist minimal)
- [x] Strava-Authorization-Callback-Domain in der README bleibt unverändert
      (`localhost`)
- [x] Test: Source-Inspection bestätigt `127.0.0.1`-Bind und schließt
      All-Interfaces-Bind aus

## Annahmen

- `127.0.0.1` reicht — kein IPv6-Support nötig, da Strava beim Redirect
  `http://localhost` benutzt, was unter beiden Adressfamilien resolved
  und Browser standardmäßig IPv4 wählen.

## Dateien

- `run_trend/strava/simple_auth.py:233`
- `tests/test_strava_auth.py` (Regression-Guard hinzugefügt)

## Status / Fortschritt

**Vollständig umgesetzt.**

- ✅ `simple_auth.py:239`: `socketserver.TCPServer(("", ...))` →
  `socketserver.TCPServer(("127.0.0.1", ...))`. Kommentar drüber erklärt
  die Loopback-Restriction für künftige Maintainer (T29-Ref).
- ✅ Neuer Test-Klasse `TestOAuthCallbackBindLocalhost` in
  `tests/test_strava_auth.py` mit zwei Cases:
  `test_loopback_address_appears_in_tcp_server_call` (whitespace-
  normalisiertes Source-Matching auf `("127.0.0.1", self.REDIRECT_PORT)`)
  und `test_no_all_interfaces_bind_remains` (greppt explizit auf
  `TCPServer(("",`, schlägt fehl wenn All-Interfaces-Bind zurückkommt).
- ✅ `pytest tests/` 285 grün (283 + 2 neue; eine Test-Klasse mit 2
  Cases statt 1).
- ✅ README bleibt unangetastet — Strava-Callback-Domain ist nach wie
  vor `localhost`, was sowohl `0.0.0.0` als auch `127.0.0.1`-Bind
  funktional bedient.

### Annahmen

- Manuelle E2E-Verifikation des OAuth-Flows bleibt offen — der
  Codeänderung ist trivial, aber ein automatisierter Test des
  vollständigen Flows würde einen lokalen HTTP-Listener + Strava-Mock
  + Browser-Simulation erfordern; das sprengt den Quick-Win-Scope.
  Falls beim nächsten echten OAuth-Lauf der Callback ankommt, ist
  ticket-konform alles grün.
