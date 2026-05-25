#!/usr/bin/env python3

import serial
from meshtastic import mesh_pb2
from meshtastic import portnums_pb2

DEV="/dev/ttyACM0"
BAUD=115200

SYNC=b"\x94\xc3"

print("OPEN:",DEV)

ser=serial.Serial(DEV,BAUD,timeout=0.5)

buf=b""

def hexify(d):
    return " ".join(f"{x:02x}" for x in d)

while True:

    data=ser.read(512)

    if data:
        print("RX:",len(data),"bytes")
        print(hexify(data))
        buf+=data

    start=buf.find(SYNC)

    if start >= 0:
        print("SYNC FOUND AT",start)

    while True:

        start=buf.find(SYNC)

        if start < 0:
            break

        if start > 0:
            print("SKIP:",start)
            buf=buf[start:]

        if len(buf) < 4:
            break

        length=(buf[2] << 8) | buf[3]

        print("FRAME LEN:",length)

        if length <= 0 or length > 2048:
            print("BAD LEN")
            buf=buf[2:]
            continue

        if len(buf) < 4 + length:
            print("WAIT MORE")
            break

        frame=buf[:4+length]
        buf=buf[4+length:]

        payload=frame[4:]

        print("PAYLOAD:")
        print(hexify(payload))

        try:

            msg=mesh_pb2.FromRadio()
            msg.ParseFromString(payload)

            print("DECODE OK")
            print(msg)

        except Exception as e:

            print("DECODE FAIL:",e)
