# core/esp32_led.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Tuple, Optional, Dict, Any
import requests

DEFAULT_TIMEOUT = 2.0

# Mapa de colores “contrato”
DEFAULT_COLORS: Dict[str, Tuple[int, int, int]] = {
    "rojo": (255, 0, 0),
    "naranja": (255, 165, 0),
    "amarillo": (255, 255, 0),
    "verde": (0, 255, 0),
    "cian": (0, 255, 255),
    "azul": (0, 0, 255),
    "violeta": (128, 0, 128),
    "blanco": (255, 255, 255),
}

@dataclass
class ESP32LEDClient:
    """Cliente para controlar el LED RGB de tu ESP32 por HTTP (Ethernet/W5500).

    Contratos:
      - POST /set_color  body: {"color":"rojo"} o {"rgb":[r,g,b]}
      - POST /off
      - GET  /ack        -> texto plano "OK: color (r,g,b)"
      - GET  /status     -> JSON {"status":"ok","color":"...", "rgb":[r,g,b]}
    """
    base_url: str                      # p.ej. "http://192.168.10.2:80"
    timeout: float = DEFAULT_TIMEOUT
    colors: Dict[str, Tuple[int,int,int]] = None

    def __post_init__(self):
        self.base_url = self.base_url.rstrip("/")
        if self.colors is None:
            self.colors = DEFAULT_COLORS

    # === Contratos simples que querías ===
    def encender_led(self, color: str) -> str:
        """Enciende el LED con un color del mapa (contrato simple)."""
        color = color.lower().strip()
        rgb = self.colors.get(color)
        payload = {"color": color}
        if rgb:
            payload["rgb"] = list(rgb)
        r = requests.post(f"{self.base_url}/set_color", json=payload, timeout=self.timeout)
        r.raise_for_status()
        return self.ack()

    def set_rgb(self, r: int, g: int, b: int) -> str:
        """Enciende el LED con un RGB arbitrario."""
        resp = requests.post(f"{self.base_url}/set_color",
                             json={"rgb": [r, g, b]}, timeout=self.timeout)
        resp.raise_for_status()
        return self.ack()

    def apagar(self) -> str:
        """Apaga el LED."""
        r = requests.post(f"{self.base_url}/off", timeout=self.timeout)
        r.raise_for_status()
        return self.ack()

    def ack(self) -> str:
        """Lee el acuse en texto plano (útil para UI)."""
        r = requests.get(f"{self.base_url}/ack", timeout=self.timeout)
        r.raise_for_status()
        return r.text

    def estado(self) -> Dict[str, Any]:
        """Devuelve el estado JSON del dispositivo."""
        r = requests.get(f"{self.base_url}/status", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    # === Utilidades opcionales ===
    def set_destino(self, base_url: str):
        """Cambia destino en caliente (útil para UI)."""
        self.base_url = base_url.rstrip("/")

    def lista_colores(self) -> Iterable[str]:
        return self.colors.keys()
