from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER, MODEL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.debug("Creating switch entity for entry %s", entry.entry_id)
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TpLinkLedSwitch(entry.entry_id, data["api"], data["coordinator"])])


class TpLinkLedSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = DEFAULT_NAME
    _attr_icon = "mdi:ethernet-switch"

    def __init__(self, entry_id: str, api, coordinator) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._api = api
        self._attr_unique_id = f"{entry_id}_led"

    @property
    def is_on(self):
        return self.coordinator.data.get("is_on")

    @property
    def available(self) -> bool:
        return super().available

    @property
    def device_info(self):
        host = self._api._url.replace("http://", "").replace("https://", "")
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "TP-Link Switch",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "configuration_url": self._api._url,
            "serial_number": host,
        }

    async def async_update(self) -> None:
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        ok = await self.hass.async_add_executor_job(self._api.set_led, "1")
        if not ok:
            raise HomeAssistantError("Nepodařilo se zapnout LED na switchi.")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        ok = await self.hass.async_add_executor_job(self._api.set_led, "0")
        if not ok:
            raise HomeAssistantError("Nepodařilo se vypnout LED na switchi.")
        await self.coordinator.async_request_refresh()
