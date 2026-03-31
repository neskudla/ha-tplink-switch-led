# TP-Link Switch LED

Build for Home Assistant / HACS with local integration brand assets.

## Co obsahuje
- `icon.png` v rootu pro HACS
- `custom_components/tplink_switch_led/brand/icon.png`
- `custom_components/tplink_switch_led/brand/logo.png`
- jednu `switch` entitu
- debug logování HTTP kroků
- žádné čtení aktuálního stavu

## Logování
Pro zapnutí debug logů přidej do `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.tplink_switch_led: debug
```

## Verze
- `manifest.json`: `0.2.2`

Tato verze je určená pro použití přímo z `main`.
