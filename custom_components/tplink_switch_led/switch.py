import requests
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN, DEFAULT_NAME, MANUFACTURER, MODEL

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([TplinkLedSwitch(entry)])

class TplinkLedSwitch(SwitchEntity):
    def __init__(self, entry):
        self._url = entry.data["url"]
        self._username = entry.data["username"]
        self._password = entry.data["password"]
        self._state = None

    @property
    def name(self):
        return DEFAULT_NAME

    @property
    def icon(self):
        return "mdi:ethernet-switch"

    @property
    def assumed_state(self):
        return True

    @property
    def is_on(self):
        return self._state

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "switch")},
            "name": "TP-Link Switch",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    def _login(self, session):
        session.post(f"{self._url}/logon.cgi", data={
            "username": self._username,
            "password": self._password,
            "cpassword": "",
            "logon": "Login"
        })

    def _set_led(self, state):
        session = requests.Session()
        self._login(session)
        session.get(f"{self._url}/led_on_set.cgi",
                    params={"rd_led": state, "led_cfg": "Apply"})

    async def async_turn_on(self, **kwargs):
        self._set_led("1")
        self._state = True

    async def async_turn_off(self, **kwargs):
        self._set_led("0")
        self._state = False
