from __future__ import annotations

import logging
import re
from typing import Any

import requests

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_PASSWORD,
    CONF_URL,
    CONF_USERNAME,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    STATE_PAGE,
)

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

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.debug("Creating switch entity for entry %s", entry.entry_id)
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TpLinkLedSwitch(entry.entry_id, data)], update_before_add=True)

class TpLinkLedSwitch(SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = DEFAULT_NAME
    _attr_icon = "mdi:ethernet-switch"

    def __init__(self, entry_id: str, data: dict[str, Any]) -> None:
        self._entry_id = entry_id
        self._url = data[CONF_URL].rstrip("/")
        self._username = data[CONF_USERNAME]
        self._password = data[CONF_PASSWORD]
        self._attr_unique_id = f"{entry_id}_led"
        self._attr_is_on = None
        _LOGGER.debug("Switch entity initialized for %s", self._url)

    @property
    def available(self) -> bool:
        return True

    @property
    def device_info(self):
        host = self._url.replace("http://", "").replace("https://", "")
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "TP-Link Switch",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "configuration_url": self._url,
            "serial_number": host,
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        _LOGGER.debug("Turning LED ON for %s", self._url)
        ok = await self.hass.async_add_executor_job(self._set_led, "1")
        if not ok:
            raise HomeAssistantError("Nepodařilo se zapnout LED na switchi.")
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        _LOGGER.debug("Turning LED OFF for %s", self._url)
        ok = await self.hass.async_add_executor_job(self._set_led, "0")
        if not ok:
            raise HomeAssistantError("Nepodařilo se vypnout LED na switchi.")
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_update(self) -> None:
        state = await self.hass.async_add_executor_job(self._read_led_state)
        if state is not None:
            self._attr_is_on = state
            _LOGGER.debug("Read LED state from switch: %s", state)

    def _login(self, session: requests.Session) -> bool:
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

    def _set_led(self, state: str) -> bool:
        session = requests.Session()
        session.headers.update(COMMON_HEADERS)

        try:
            if not self._login(session):
                _LOGGER.error("Login failed before setting LED")
                return False

            led_headers = {**COMMON_HEADERS, "Referer": f"{self._url}/{STATE_PAGE}"}
            _LOGGER.debug(
                "GET %s/led_on_set.cgi?rd_led=%s&led_cfg=Apply",
                self._url,
                state,
            )
            led_resp = session.get(
                f"{self._url}/led_on_set.cgi",
                params={"rd_led": state, "led_cfg": "Apply"},
                headers=led_headers,
                timeout=10,
                allow_redirects=True,
            )

            body_preview = led_resp.text[:200].replace("\n", " ").replace("\r", " ")
            _LOGGER.debug(
                "LED response: status=%s final_url=%s location=%s body_preview=%s",
                led_resp.status_code,
                getattr(led_resp, "url", ""),
                led_resp.headers.get("Location"),
                body_preview,
            )

            if led_resp.status_code >= 500:
                _LOGGER.error("LED request failed with status %s", led_resp.status_code)
                return False

            return led_resp.status_code in (200, 301, 302, 303, 307, 308, 401, 403) or led_resp.ok

        except requests.RequestException as err:
            _LOGGER.error("HTTP error while controlling switch LED: %s", err, exc_info=True)
            return False
        except Exception as err:
            _LOGGER.error("Unexpected error while controlling switch LED: %s", err, exc_info=True)
            return False
        finally:
            session.close()

    def _read_led_state(self) -> bool | None:
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
            body_preview = state_resp.text[:200].replace("\n", " ").replace("\r", " ")
            _LOGGER.debug(
                "State page response: status=%s final_url=%s location=%s body_preview=%s",
                state_resp.status_code,
                getattr(state_resp, "url", ""),
                state_resp.headers.get("Location"),
                body_preview,
            )
            if state_resp.status_code >= 500:
                return None

            match = LED_RE.search(state_resp.text)
            if not match:
                _LOGGER.warning("Could not parse LED state from %s", STATE_PAGE)
                return None

            return match.group(1) == "1"
        except requests.RequestException as err:
            _LOGGER.error("HTTP error while reading LED state: %s", err, exc_info=True)
            return None
        except Exception as err:
            _LOGGER.error("Unexpected error while reading LED state: %s", err, exc_info=True)
            return None
        finally:
            session.close()
