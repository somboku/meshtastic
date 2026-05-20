import meshtastic.serial_interface
from pubsub import pub
from flask import Flask
from datetime import datetime
import json

app = Flask(__name__)

messages = []

def safe(obj):
    """
    Convert weird Meshtastic objects into JSON-safe strings
    """
    try:
        json.dumps(obj)
        return obj
    except:
        return str(obj)

def on_receive(packet, interface):
    try:
        decoded = packet.get("decoded", {})

        msg = {
            "time": datetime.now().isoformat(),
            "from": packet.get("from"),
            "to": packet.get("to"),
            "text": decoded.get("text"),
            "type": decoded.get("portnum"),
            "raw": str(packet)
        }

        print("📩", msg)

        messages.append(msg)

        if len(messages) > 100:
            messages.pop(0)

    except Exception as e:
        print("ERROR:", e)


pub.subscribe(on_receive, "meshtastic.receive")

interface = meshtastic.serial_interface.SerialInterface()

@app.route("/")
def index():
    return app.response_class(
        response=json.dumps(messages, indent=2),
        mimetype="application/json"
    )

@app.route("/health")
def health():
    return "OK"

print("Listening for Meshtastic packets...")
app.run(host="0.0.0.0", port=5000)
