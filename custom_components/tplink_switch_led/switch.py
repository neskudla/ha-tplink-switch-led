from homeassistant.components.switch import SwitchEntity

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([TplinkSwitch()])

class TplinkSwitch(SwitchEntity):
    @property
    def name(self):
        return "TP-Link LED"

    @property
    def is_on(self):
        return True

    async def async_turn_on(self, **kwargs):
        pass

    async def async_turn_off(self, **kwargs):
        pass
