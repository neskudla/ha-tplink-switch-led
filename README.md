# TP-Link Switch LED

Custom Home Assistant integrace pro ovládání LED na podporovaných TP-Link Easy Smart switchích.

## Co umí
- přidání přes UI
- jedna `switch` entita
- čtení stavu z `TurnOnLEDRpm.htm`
- on-demand refresh bez pravidelného pollingu
- cache stavu na 30 sekund
- HACS-ready struktura
- lokální brand ikony pro Home Assistant
- root `icon.png` pro HACS

## Jak funguje
Integrace používá:
- `POST /logon.cgi`
- `GET /led_on_set.cgi?rd_led=0|1&led_cfg=Apply`
- `GET /TurnOnLEDRpm.htm` pro čtení stavu

Stav se čte z JavaScript proměnné:
- `var led = 0`
- `var led = 1`

## Chování aktualizace
- žádný pravidelný polling
- po zapnutí/vypnutí LED se stav hned refreshne
- při čtení stavu se používá cache na 30 sekund, aby se omezily zbytečné loginy

## Instalace
1. Nahraj obsah tohoto balíčku do GitHub repa.
2. Přidej repo do HACS jako **Custom repository** typu **Integration**.
3. Nainstaluj integraci z HACS.
4. Restartuj Home Assistant.
5. Přidej integraci v **Settings → Devices & Services**.

## Poznámky
Otevření entity v UI samo o sobě nemusí vždy vynutit refresh. Pokud chceš spolehlivě zachytit externí změny provedené mimo Home Assistant, je vhodnější krátký periodický refresh nebo ruční `update_entity`.
