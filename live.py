import meshtastic.serial_interface
from pubsub import pub
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# -----------------------------
# STATE
# -----------------------------
nodes = {}
messages = []

# -----------------------------
# NODE UPDATE
# -----------------------------
def update_node(node_id, packet, decoded):
    now = datetime.now().isoformat()

    if node_id not in nodes:
        nodes[node_id] = {
            "id": packet.get("from"),
            "hex": node_id,
            "first_seen": now,
            "last_seen": now,
            "name": None,
            "messages": []
        }

    node = nodes[node_id]
    node["last_seen"] = now

    # Try to extract a human name if available
    if "user" in packet:
        user = packet.get("user", {})
        if isinstance(user, dict):
            node["name"] = user.get("longName") or user.get("shortName")

    return node


# -----------------------------
# ROUTER (clean separation)
# -----------------------------
def route_packet(node_id, node, decoded):
    msg_type = decoded.get("portnum")
    text = decoded.get("text")

    entry = {
        "time": datetime.now().isoformat(),
        "type": msg_type,
        "text": text
    }

    node["messages"].append(entry)
    node["messages"] = node["messages"][-10:]

    messages.append({
        "node": node_id,
        **entry
    })

    if len(messages) > 200:
        messages.pop(0)

    print(f"📡 [{msg_type}] {node_id} → {text}")


# -----------------------------
# MAIN INGEST FUNCTION
# -----------------------------
def on_receive(packet, interface):
    decoded = packet.get("decoded", {})

    node_id = packet.get("fromId") or str(packet.get("from"))

    node = update_node(node_id, packet, decoded)
    route_packet(node_id, node, decoded)


# subscribe to meshtastic events
pub.subscribe(on_receive, "meshtastic.receive")

# connect to device
interface = meshtastic.serial_interface.SerialInterface()


# -----------------------------
# WEB DASHBOARD
# -----------------------------
@app.route("/")
def index():
    html = """
    <html>
    <head>
        <meta http-equiv="refresh" content="2">
        <style>
            body { font-family: monospace; background:#111; color:#0f0; }
            .node { border:1px solid #333; margin:10px; padding:10px; }
            .msg { color:#aaa; margin-left:10px; }
        </style>
    </head>
    <body>
    <h2>📡 LoRa Mesh Intelligence Gateway (Step E)</h2>
    """

    for node_id, n in nodes.items():
        display_name = n["name"] or node_id

        html += f"""
        <div class="node">
            <b>Node:</b> {display_name}<br>
            <b>ID:</b> {node_id}<br>
            <b>First seen:</b> {n['first_seen']}<br>
            <b>Last seen:</b> {n['last_seen']}<br>
            <b>Messages:</b> {len(n['messages'])}
            <hr>
        """

        for m in n["messages"]:
            html += f"""
            <div class="msg">
                [{m['time']}] {m['type']} : {m['text']}
            </div>
            """

        html += "</div>"

    html += "</body></html>"
    return html


@app.route("/json")
def json_view():
    return {
        "nodes": nodes,
        "messages": messages
    }


@app.route("/health")
def health():
    return "OK"


# -----------------------------
# START
# -----------------------------
print("🚀 LoRa Gateway (Step E) starting...")
app.run(host="0.0.0.0", port=5000)
