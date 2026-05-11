# 23 — HTTP-Timeouts an Strava-API-Calls

**Priorität:** P0
**Kategorie:** Robustheit / Sicherheit

## Problem

Vier `requests.get/.post`-Aufrufe in den Strava-Modulen haben **keinen** `timeout=`-Parameter:

- `run_trend/strava/client.py:48` (Haupt-API-Request)
- `run_trend/strava/simple_auth.py:84` (Token-Refresh)
- `run_trend/strava/simple_auth.py:266` (Initial-Token-Exchange)
- `run_trend/strava/simple_auth.py:308` (Deauthorize-Call in `revoke`)

Bricht die Strava-Verbindung mitten in einem Sync ab (Routing-Hänger, halb offene
Verbindung, Anbieter-Stall), blockiert der Worker-Thread bis zum TCP-Default
(typisch ~2 h auf Linux). Kein Code-Pfad prüft auf Hang oder bietet Abbruch an —
weder die UI noch der `RequestException`-Handler greift.

## Auswirkung auf Nutzer

App hängt mit drehender „Syncing…"-Statusbar, der Sync-Button bleibt deaktiviert,
und nur ein Force-Quit stellt die App wieder her. Beim Token-Refresh
(Background-Thread) ist der Hänger zusätzlich unsichtbar.

## Lösungsansatz

In beiden Modulen eine Modul-Konstante einführen:

```python
_HTTP_TIMEOUT = (5.0, 30.0)  # (connect, read) seconds
```

…und an jeden `requests.*`-Call durchreichen. Der bestehende
`requests.exceptions.RequestException`-Handler fängt `Timeout` bereits ab
(`Timeout` ist Subklasse), die Fehlerausgabe ist also unverändert.

## Acceptance

- [x] `_HTTP_TIMEOUT`-Konstante in `client.py` und `simple_auth.py`
- [x] Alle vier `requests.get/.post`-Aufrufe nutzen `timeout=_HTTP_TIMEOUT`
- [x] Test in `tests/test_strava_streams.py` o.ä.: `requests.Timeout`
      wird gefangen und liefert `None`/`False` ohne Exception nach außen
- [x] Bestehende Tests weiterhin grün

## Annahmen

- 5 s connect / 30 s read sind großzügig für ein Heim-Internet bei großer
  Activity-Liste (Strava antwortet typisch < 1 s). Falls in der Praxis
  zu kurz, einfach Konstante anpassen — keine API-Änderung nötig.
- Kein Retry-Mechanismus im Scope dieses Tickets; Timeout führt aktuell
  zum „failed to refresh / sync abort"-Pfad, was OK ist.

## Dateien

- `run_trend/strava/client.py`
- `run_trend/strava/simple_auth.py`
- `tests/test_strava_streams.py` (oder `tests/test_strava_auth.py`)

## Status / Fortschritt

**Vollständig umgesetzt.**

- ✅ `_HTTP_TIMEOUT = (5.0, 30.0)` als Modul-Konstante in `client.py:14`
  und `simple_auth.py:17` mit kurzem Why-Kommentar (TCP_USER_TIMEOUT-Hänger
  vermeiden).
- ✅ Alle vier Call-Sites bekommen `timeout=_HTTP_TIMEOUT`:
  `client.py:53` (`_make_request` → Strava API), `simple_auth.py:93`
  (`_refresh_access_token` → Token-Refresh), `simple_auth.py:275`
  (`_exchange_code` → OAuth-Tausch), `simple_auth.py:317`
  (`revoke` → Deauthorize).
- ✅ Bestehende Exception-Handler fangen `requests.Timeout` bereits
  korrekt (Timeout ⊂ RequestException ⊂ Exception); keine
  Handler-Änderung nötig.
- ✅ Tests in `tests/test_strava_auth.py` (3 neu:
  `test_refresh_passes_http_timeout`, `test_refresh_timeout_returns_false`,
  `test_exchange_code_timeout_returns_false`) und
  `tests/test_strava_streams.py` (2 neu in `TestMakeRequestTimeout`:
  `test_passes_http_timeout`, `test_timeout_returns_none`).
- ✅ `pytest tests/` 259 grün (254 + 5 neue).

### Annahmen

- Konstante als modul-privat (`_HTTP_TIMEOUT`), nicht klassenweit — sie
  ist Implementierungsdetail des HTTP-Layers und soll nicht von außen
  überschrieben werden.
- `revoke()` fängt das `Timeout` über das bestehende `except Exception`
  (Loglevel `exception`) — kein expliziter `requests.Timeout`-Branch,
  weil das Fehlverhalten identisch zu „server returned 500" ist und
  lokale Tokens trotzdem gecleared werden.
