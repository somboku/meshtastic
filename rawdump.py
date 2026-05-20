import meshtastic.serial_interface
from pubsub import pub
import json
from datetime import datetime


def safe(obj):
    """
    Convert weird protobuf objects into printable JSON-safe data
    """
    try:
        json.dumps(obj)
        return obj
    except:
        return str(obj)


def pretty(packet):
    """
    Deep-convert packet into readable structure
    """
    if isinstance(packet, dict):
        return {k: pretty(v) for k, v in packet.items()}

    if isinstance(packet, list):
        return [pretty(v) for v in packet]

    return safe(packet)


def on_receive(packet, interface):

    print("\n" + "=" * 80)
    print("TIME:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)

    try:
        cleaned = pretty(packet)

        print(json.dumps(cleaned, indent=2))

    except Exception as e:
        print("ERROR:", e)
        print(packet)


pub.subscribe(on_receive, "meshtastic.receive")

print("📡 RAW SERIAL DUMP RUNNING")
print("Waiting for packets...\n")

interface = meshtastic.serial_interface.SerialInterface()

input("Press ENTER to exit\n")
