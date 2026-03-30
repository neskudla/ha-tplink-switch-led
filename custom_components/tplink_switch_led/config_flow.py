from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_PASSWORD, CONF_URL, CONF_USERNAME, DOMAIN

class TpLinkSwitchLedConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_URL].rstrip("/"))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_URL].rstrip("/"),
                data={
                    CONF_URL: user_input[CONF_URL].rstrip("/"),
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_URL, default="http://switch.local"): str,
                vol.Required(CONF_USERNAME, default="admin"): str,
                vol.Required(CONF_PASSWORD, default=""): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
