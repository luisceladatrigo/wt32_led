# ESP32 Client

Mini cliente Flask + SDK para controlar el LED RGB de un ESP32-S3-ETH (W5500).

## Estructura
- `core/esp32_led.py`: SDK reutilizable (`encender_led`, `set_rgb`, `apagar`, `estado`)
- `app/web.py`: vista Flask que usa el SDK
- `run.py`: arranque de la web
- `requirements.txt`: dependencias

## Uso
```bash
pip install -r requirements.txt
python run.py
```

Abre http://localhost:5000 en tu navegador.
