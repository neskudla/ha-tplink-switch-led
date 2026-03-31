# TP-Link Switch LED

Custom Home Assistant integrace pro ovládání LED na podporovaných TP-Link Easy Smart switchích.

## Co umí
- přidání přes UI (`config_flow`)
- jedna `switch` entita pro zapnutí a vypnutí LED
- čtení aktuálního stavu z `TurnOnLEDRpm.htm`
- HACS-ready struktura
- lokální brand ikony pro Home Assistant
- root `icon.png` pro HACS
- debug logování HTTP kroků

## Jak funguje
Integrace používá:
- `POST /logon.cgi`
- `GET /led_on_set.cgi?rd_led=0|1&led_cfg=Apply`
- `GET /TurnOnLEDRpm.htm` pro čtení stavu

Stav se čte z JavaScript proměnné:
- `var led = 0`
- `var led = 1`

## Instalace
1. Nahraj obsah tohoto balíčku do GitHub repa.
2. Přidej repo do HACS jako **Custom repository** typu **Integration**.
3. Nainstaluj integraci z HACS.
4. Restartuj Home Assistant.
5. Přidej integraci v **Settings → Devices & Services**.

## Logování
Pro zapnutí debug logů přidej do `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.tplink_switch_led: debug
```
