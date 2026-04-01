import logging
import re
import time

import requests

from .const import CACHE_SECONDS, STATE_PAGE

_LOGGER = logging.getLogger(__name__)

COMMON_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:148.0) "
        "Gecko/20100101 Firefox/148.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "cs,sk;q=0.9,en-US;q=0.8,en;q=0.7",
}

LED_RE = re.compile(r"var\s+led\s*=\s*([01])")


class TpLinkSwitchLedApi:
    def __init__(self, base_url, username, password):
        self._url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._cached_state = None
        self._cached_at = 0.0

    def _login(self, session):
        login_headers = {
            **COMMON_HEADERS,
            "Origin": self._url,
            "Referer": f"{self._url}/",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        login_resp = session.post(
            f"{self._url}/logon.cgi",
            data={
                "username": self._username,
                "password": self._password,
                "cpassword": "",
                "logon": "Login",
            },
            headers=login_headers,
            timeout=10,
            allow_redirects=True,
        )
        _LOGGER.debug(
            "Login response: status=%s final_url=%s location=%s cookies=%s",
            login_resp.status_code,
            getattr(login_resp, "url", ""),
            login_resp.headers.get("Location"),
            list(session.cookies.keys()),
        )
        return login_resp.status_code < 500

    def set_led(self, state):
        session = requests.Session()
        session.headers.update(COMMON_HEADERS)
        try:
            if not self._login(session):
                _LOGGER.error("Login failed before setting LED")
                return False

            led_headers = {**COMMON_HEADERS, "Referer": f"{self._url}/{STATE_PAGE}"}
            led_resp = session.get(
                f"{self._url}/led_on_set.cgi",
                params={"rd_led": state, "led_cfg": "Apply"},
                headers=led_headers,
                timeout=10,
                allow_redirects=True,
            )
            if led_resp.status_code >= 500:
                _LOGGER.error("LED request failed with status %s", led_resp.status_code)
                return False

            ok = led_resp.status_code in (200, 301, 302, 303, 307, 308, 401, 403) or led_resp.ok
            if ok:
                self._cached_state = state == "1"
                self._cached_at = time.monotonic()
            return ok
        except Exception as err:
            _LOGGER.error("Error while controlling switch LED: %s", err, exc_info=True)
            return False
        finally:
            session.close()

    def read_led_state(self, force_refresh=False):
        now = time.monotonic()
        if (
            not force_refresh
            and self._cached_state is not None
            and (now - self._cached_at) < CACHE_SECONDS
        ):
            _LOGGER.debug("Returning cached LED state: %s", self._cached_state)
            return self._cached_state

        session = requests.Session()
        session.headers.update(COMMON_HEADERS)
        try:
            if not self._login(session):
                _LOGGER.error("Login failed before reading LED state")
                return None

            state_resp = session.get(
                f"{self._url}/{STATE_PAGE}",
                headers={**COMMON_HEADERS, "Referer": f"{self._url}/"},
                timeout=10,
                allow_redirects=True,
            )
            if state_resp.status_code >= 500:
                return None

            match = LED_RE.search(state_resp.text)
            if not match:
                _LOGGER.warning("Could not parse LED state from %s", STATE_PAGE)
                return None

            state = match.group(1) == "1"
            self._cached_state = state
            self._cached_at = time.monotonic()
            return state
        except Exception as err:
            _LOGGER.error("Error while reading LED state: %s", err, exc_info=True)
            return None
        finally:
            session.close()
