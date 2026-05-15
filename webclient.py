import socketio
import json
import pprint

sio = socketio.Client()

def notify(data):
    try:
        sio.emit("update", {"alrt",data})
    except Exception as e:
        print("⚠️ websocket notify failed:", e)
try:
    sio.connect("http://127.0.0.1:5000")
    print("🌐 Connected to web server")
    notify("Bridge connected")
except Exception as e:
    print("❌ Could not connect to web server:", e)

