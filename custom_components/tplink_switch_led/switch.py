import requests
from homeassistant.components.switch import SwitchEntity

async def async_setup_entry(hass,entry,async_add_entities):
    async_add_entities([TplinkLedSwitch(entry)])

class TplinkLedSwitch(SwitchEntity):
    def __init__(self,entry):
        self._url=entry.data['url']
        self._username=entry.data['username']
        self._password=entry.data['password']
        self._state=None

    @property
    def name(self): return 'TP-Link Switch LED'
    @property
    def icon(self): return 'mdi:ethernet-switch'
    @property
    def assumed_state(self): return True
    @property
    def is_on(self): return self._state

    def _login(self,s):
        s.post(f"{self._url}/logon.cgi",data={'username':self._username,'password':self._password,'cpassword':'','logon':'Login'})

    def _set(self,state):
        s=requests.Session()
        self._login(s)
        s.get(f"{self._url}/led_on_set.cgi",params={'rd_led':state,'led_cfg':'Apply'})

    async def async_turn_on(self,**kw): self._set('1'); self._state=True
    async def async_turn_off(self,**kw): self._set('0'); self._state=False
