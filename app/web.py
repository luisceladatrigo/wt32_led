# app/web.py
from flask import Flask, render_template_string, request, redirect, url_for
from core.esp32_led import ESP32LEDClient, DEFAULT_COLORS

def create_app(default_base_url: str = "http://192.168.10.2:80") -> Flask:
    app = Flask(__name__)
    app.config["CLIENT"] = ESP32LEDClient(default_base_url)

    TEMPLATE = """
    <!doctype html>
    <html lang="es">
    <head>
      <meta charset="utf-8" />
      <title>Control LED ESP32</title>
      <style>
        body{font-family:system-ui,Arial,sans-serif;max-width:760px;margin:40px auto;padding:0 16px}
        .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:10px;margin:16px 0}
        .btn{display:block;padding:14px;border:none;border-radius:10px;font-weight:600;cursor:pointer}
        .btn-dark{background:#111;color:#fff}
        .card{padding:12px;border:1px solid #eee;border-radius:12px;background:#fafafa}
        .row{display:flex;gap:8px;align-items:center}
        input[type=text]{padding:8px;border:1px solid #ddd;border-radius:8px;flex:1}
        .msg{margin-top:10px;font-weight:600}
        .ok{color:#0a7a28}.err{color:#b00020}
      </style>
    </head>
    <body>
      <h1>Control LED ESP32</h1>
      <div class="card" style="margin-top:12px">
        <form class="row" method="post" action="{{ url_for('set_target') }}">
          <input type="text" name="esp32_url" value="{{ base_url }}" placeholder="http://192.168.10.2:80" />
          <button class="btn btn-dark">Cambiar destino</button>
        </form>
      </div>

      <div class="grid">
        {% for name, rgb in colors.items() %}
          <form method="post" action="{{ url_for('set_color', color=name) }}">
            <button class="btn" style="background: rgb({{rgb[0]}},{{rgb[1]}},{{rgb[2]}}); color: white; text-shadow: 0 1px 2px rgba(0,0,0,.5)">
              {{ name|capitalize }}
            </button>
          </form>
        {% endfor %}
        <form method="post" action="{{ url_for('turn_off') }}">
          <button class="btn btn-dark">Apagar</button>
        </form>
      </div>

      <div class="card">
        <form class="row" method="post" action="{{ url_for('check_status') }}">
          <button class="btn btn-dark">Consultar estado</button>
          <div>{{ status_text }}</div>
        </form>
        {% if message %}
          <div class="msg {{ 'ok' if ok else 'err' }}">{{ message }}</div>
        {% endif %}
      </div>
    </body>
    </html>
    """

    @app.route("/", methods=["GET"])
    def index():
        client: ESP32LEDClient = app.config["CLIENT"]
        base = client.base_url
        try:
            st = client.estado()
            status_text = f"Color: {st.get('color')}  RGB: {st.get('rgb')}"
        except Exception:
            status_text = "Estado no disponible"
        return render_template_string(TEMPLATE,
                                     colors=client.colors,
                                     message=None,
                                     ok=True,
                                     base_url=base,
                                     status_text=status_text)

    @app.route("/set_target", methods=["POST"])
    def set_target():
        url = request.form.get("esp32_url", "").strip().rstrip("/")
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        client: ESP32LEDClient = app.config["CLIENT"]
        client.set_destino(url)
        return redirect(url_for("index"))

    @app.route("/set/<color>", methods=["POST"])
    def set_color(color: str):
        client: ESP32LEDClient = app.config["CLIENT"]
        try:
            msg = client.encender_led(color)
            ok = True
        except Exception as e:
            msg, ok = f"Error: {e}", False
        return render_template_string(TEMPLATE,
                                      colors=client.colors,
                                      message=msg,
                                      ok=ok,
                                      base_url=client.base_url,
                                      status_text="")

    @app.route("/off", methods=["POST"])
    def turn_off():
        client: ESP32LEDClient = app.config["CLIENT"]
        try:
            msg = client.apagar()
            ok = True
        except Exception as e:
            msg, ok = f"Error: {e}", False
        return render_template_string(TEMPLATE,
                                      colors=client.colors,
                                      message=msg,
                                      ok=ok,
                                      base_url=client.base_url,
                                      status_text="")

    @app.route("/check_status", methods=["POST"])
    def check_status():
        client: ESP32LEDClient = app.config["CLIENT"]
        try:
            st = client.estado()
            text = f"Color: {st.get('color')}  RGB: {st.get('rgb')}"
            ok = True
        except Exception as e:
            text, ok = f"Error consultando estado: {e}", False
        return render_template_string(TEMPLATE,
                                      colors=client.colors,
                                      message=None,
                                      ok=ok,
                                      base_url=client.base_url,
                                      status_text=text)

    return app
