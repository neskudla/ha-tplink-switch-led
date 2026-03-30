from __future__ import annotations

import logging
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
)

_LOGGER = logging.getLogger(__name__)

COMMON_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:148.0) "
        "Gecko/20100101 Firefox/148.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TpLinkLedSwitch(entry.entry_id, data)])

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

    @property
    def assumed_state(self) -> bool:
        return True

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
        ok = await self.hass.async_add_executor_job(self._set_led, "1")
        if not ok:
            raise HomeAssistantError("Nepodařilo se zapnout LED na switchi.")
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        ok = await self.hass.async_add_executor_job(self._set_led, "0")
        if not ok:
            raise HomeAssistantError("Nepodařilo se vypnout LED na switchi.")
        self._attr_is_on = False
        self.async_write_ha_state()

    def _set_led(self, state: str) -> bool:
        session = requests.Session()
        session.headers.update(COMMON_HEADERS)
        try:
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
            # Accept any non-5xx response here; these switches can return odd HTML/redirects.
            if login_resp.status_code >= 500:
                _LOGGER.error("Login failed with status %s", login_resp.status_code)
                return False

            led_resp = session.get(
                f"{self._url}/led_on_set.cgi",
                params={"rd_led": state, "led_cfg": "Apply"},
                headers={**COMMON_HEADERS, "Referer": f"{self._url}/"},
                timeout=10,
                allow_redirects=True,
            )
            if led_resp.status_code >= 500:
                _LOGGER.error("LED request failed with status %s", led_resp.status_code)
                return False

            # Treat redirects, 200, 401/403 after session churn as best-effort success
            if led_resp.status_code in (200, 301, 302, 303, 307, 308, 401, 403):
                return True

            return led_resp.ok
        except requests.RequestException as err:
            _LOGGER.error("HTTP error while controlling switch LED: %s", err)
            return False
        finally:
            session.close()
