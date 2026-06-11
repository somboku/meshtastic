# this one is web.py listen on port 5000
# may 2026

from flask import Flask, jsonify
from flask_socketio import SocketIO
import db
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)



def write_to_file(data):
    ts = datetime.now().strftime("%d.%m %H:%M")
    line = f"{ts} {data}\n"
    print(line)
    with open("./web.py.log", "a", encoding="utf-8") as f:
        f.write(line)


@app.route("/")
def index():
    return open("ui.html").read()


@app.route("/data")
def data():
    write_to_file("@app.route/data called in web.py")
    return {
        "nodes": db.get_nodes(),
        "messages": db.get_messages()
    }

@app.route("/api/nodes")
def nodes():
    return jsonify(db.get_nodes())


@app.route("/api/messages")
def messages():
    return jsonify(db.get_messages())


@socketio.on("connect")
def on_connect():
    print("🟢 UI connected")

    socketio.emit("update", {
        "nodes": db.get_nodes(),
        "messages": db.get_messages()
    })

@socketio.on("update")
def on_update(node):
    ring = node.get("alrt", "")
    print("🟢 updateing...",ring)
    try:
        socketio.emit("update", {
            "nodes": db.get_nodes(),
            "messages": db.get_messages(),
            "alrt": ring
        })
    except Exception as e:
        print("something went wrong here in def on_update web.py")


if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        allow_unsafe_werkzeug=True,
        debug=True
    )
                 
