import time
import pprint
import socketio
from flask_socketio import SocketIO
import meshtastic.serial_interface
from pubsub import pub
import json
import db
from datetime import datetime


db.init()
sio = socketio.Client()

def _l(w):
	print(w)
#================================================
def notify(data):
    try:
        sio.emit("update",{"alrt": data})
    except Exception as e:
        print("⚠️ websocket notify failed:", e)


try:
    sio.connect("http://127.0.0.1:5000")
    print("🌐 Connected to web server")
    #notify("Bridge connected")
except Exception as e:
    print("❌ Could not connect to web server:", e)


#
# connect to meshtastic device
#
interface = meshtastic.serial_interface.SerialInterface()

print("📡 Connected to Meshtastic radio")


# import ALL known nodes from meshtastic cache
def import_nodes():
    print("📚 Importing node database...")
    nodes = interface.nodes
    user = {}
    print(f"🔍 found {len(nodes)} nodes")
    for node_id, node in nodes.items():
        user = node.get("user", {})
        long_name = user.get("longName")
        hw = user.get("hwModel")

        last_heard = node.get("lastHeard")
        if last_heard:
            last_seen = datetime.fromtimestamp(
                last_heard
            ).strftime("%Y-%m-%d %H:%M:%S")

        if not long_name:
            long_name = str(node_id)

        db.update_full_node(
            str(node_id),
            long_name,
            hw,
            last_seen
        )
        print(f"🧩 {node_id} -> {long_name} [{hw}]")




def on_receive(packet, interface):
    db.insert_packet(packet)
    user = {}
    decoded = packet.get("decoded", {})
    node_id = (
        packet.get("fromId")
        or str(packet.get("from"))
    )
    if isinstance(node_id, int):
        node_id = f"!{node_id:08x}"
    
    msg_type = decoded.get("portnum")
# ---------------------------------
    if msg_type == "TEXT_MESSAGE_APP":
        text = decoded.get("text")

# ---------------------------------
    elif msg_type == "TELEMETRY_APP":

        telemetry = decoded.get("telemetry", {})
        metrics = telemetry.get("deviceMetrics", {})
        batt = metrics.get("batteryLevel")
        volt = metrics.get("voltage")
        text = f"battery={batt}% voltage={volt}V"

# -----------------------------------------------
    elif msg_type == "POSITION_APP":

        pos = decoded.get("position", {})
        lat = pos.get("latitudeI")
        lon = pos.get("longitudeI")

        if lat and lon:
            text = f"lat={lat/1e7} lon={lon/1e7}"
        else:
            text = "position update"
# -----------------------------------------------
    elif msg_type == "NODEINFO_APP":

        user = decoded.get("user", {})
        text = f'{user.get("longName")} on a <span style=color:red;> {user.get("hwModel")}</span> as a {user.get("role")}';

    else:
        text =  json.dumps(decoded, default=str)


    node_name = node_id
    known = interface.nodes.get(node_id)
    if not known and isinstance(node_id, str):
        try:
            numeric_id = int(node_id.replace("!", ""), 16)
            known = interface.nodes.get(numeric_id)

        except:
            pass
    if known:
        user = known.get("user", {})
        if user.get("longName"):
            node_name = user.get("longName")

        last_heard = known.get("lastHeard")

        if last_heard:
            last_seen = datetime.fromtimestamp(
            last_heard
            ).strftime("%Y-%m-%d %H:%M:%S")
        else:
            last_seen = None
    else:
        last_seen = None    
    if (user):
        hw = user.get("hwModel")
    else:
        hw = "unknown"

    db.update_full_node(
        str(node_id),
        node_name,
        hw,
        last_seen            
    )

    db.insert_message(
        str(node_id),
        str(msg_type),
        str(text),
        str(packet),
        str(decoded)
    )
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    print(f"{now}📨 {node_name} [{msg_type}] {text}")
    print("pushing to web")
    try:
        sio.emit("update", {
            "nodes":    db.get_nodes(),
            "messages": db.get_messages(),
            #"alrt": "bridge started...."
        })
    except Exception as e:
        print("⚠️ websocket emit failed in bridge.py:", e)

def on_nodeinfo(packet,interface):
	_l("on_nodeinfo called")
	db.insertNodeInfo(packet,interface)



pub.subscribe(on_receive, "meshtastic.receive")
pub.subscribe(on_nodeinfo, "meshtastic.nodeinfo")
time.sleep(5)
import_nodes()

print("🚀 Bridge running (CTRL+C to exit)")


while True:
    time.sleep(1)
