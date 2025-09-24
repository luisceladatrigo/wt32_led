# run.py
from app import create_app
import os

if __name__ == "__main__":
    base = os.environ.get("ESP32_URL", "http://192.168.10.2:80")
    app = create_app(default_base_url=base)
    app.run(host="0.0.0.0", port=5000, debug=True)
