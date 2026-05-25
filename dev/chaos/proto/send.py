import sys
import serial
import time
import struct

# 👇 FIX THIS PATH to your generated protobuf folder
sys.path.append("/mnt/data/work/meshtastic/perl/protobufs/out")

from meshtastic import mesh_pb2

PORT = "/dev/ttyACM0"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=0.1)


# ----------------------------
# SERIAL FRAME ENCODER
# ----------------------------
def send(payload: bytes):
    frame = b"\x94\xC3" + struct.pack(">H", len(payload)) + payload
    ser.write(frame)


# ----------------------------
# MESHTASTIC MESSAGES
# ----------------------------
def heartbeat():
    msg = mesh_pb2.ToRadio()
    msg.heartbeat.SetInParent()
    return msg.SerializeToString()


def want_config(request_id=1):
    msg = mesh_pb2.ToRadio()
    msg.want_config_id = request_id
    return msg.SerializeToString()


# ----------------------------
# RX DEBUG (what comes back)
# ----------------------------
def read_serial():
    while ser.in_waiting:
        data = ser.read(ser.in_waiting)
        if data:
            print("\n[RX RAW]", data.hex())
            try:
                print("[RX ASCII]", data.decode(errors="ignore"))
            except:
                pass


# ----------------------------
# MAIN
# ----------------------------
print("🚀 starting meshtastic session...")

# initial sync burst
send(heartbeat())
time.sleep(0.3)
read_serial()

send(want_config(1))
time.sleep(0.3)
read_serial()


# keep alive loop + RX monitor
while True:
    send(heartbeat())
    time.sleep(5)
    read_serial()
