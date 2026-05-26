#!/usr/bin/env python3

from pubsub import pub
import meshtastic.serial_interface

def on_receive(packet, interface):
    print("\n📩 RECEIVED PACKET on {interface}")
    print(packet)

def on_connection(interface, topic=pub.AUTO_TOPIC):
    print("\n🔌 CONNECTED TO NODE")
    print("Node:", interface.getMyNodeInfo())

    #interface.sendText("hello mesh from python 🚀")

print("Starting Meshtastic listener...")

iface = meshtastic.serial_interface.SerialInterface()

pub.subscribe(on_receive, "meshtastic.receive")
pub.subscribe(on_connection, "meshtastic.connection.established")

# keep alive
try:
    while True:
        pass
except KeyboardInterrupt:
    print("\nExiting...")
    iface.close()
