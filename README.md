# TP-Link Switch LED

Debug build for Home Assistant / HACS.

## Co umí
- přidání přes UI
- vytvoření jedné `switch` entity
- zapnutí/vypnutí LED přes web rozhraní switche
- žádné čtení aktuálního stavu
- debug logování HTTP kroků

## Logování
Pro zapnutí debug logů přidej do `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.tplink_switch_led: debug
```

Pak restartuj Home Assistant.

## Verze
- `manifest.json`: `0.2.0`

Tato verze je připravená pro použití přímo z `main`.
