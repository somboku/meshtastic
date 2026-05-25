#!/usr/bin/env python3

import serial
import sys
sys.path.insert(0, "./proto")
import mesh_pb2
import portnums_pb2
import elemetry_pb2
import admin_pb2

DEV="/dev/ttyACM0"
BAUD=115200
SYNC=b"\x94\xc3"
ser=serial.Serial(DEV,BAUD,timeout=0.1)

buf=b""
def hexify(d):
    return " ".join(f"{x:02x}" for x in d)


while True:
    data=ser.read(512)
    if data:
        buf+=data

    while True:
        start=buf.find(SYNC)
        if start < 0:
            if len(buf) > 4096:
                buf=b""
            break

        if start > 0:
            buf=buf[start:]
        if len(buf) < 4:
            break

        length=(buf[2] << 8) | buf[3]
        if length <= 0 or length > 2048:
            buf=buf[2:]
            continue
        if len(buf) < 4 + length:
            break

        frame=buf[:4+length]
        buf=buf[4+length:]
        payload=frame[4:]

        print("\n====================================")
        print("LEN:",length)
        print("RAW:",hexify(payload))

        try:

            msg=mesh_pb2.FromRadio()
            msg.ParseFromString(payload)

            #
            # dump whole envelope
            #

            print(msg)

            #
            # mesh packet
            #

            if msg.HasField("packet"):

                pkt=msg.packet

                print("FROM:",pkt.from_)
                print("TO:",pkt.to)
                print("ID:",pkt.id)

                #
                # decoded payload
                #

                if pkt.HasField("decoded"):

                    dec=pkt.decoded
                    print("PORTNUM:",dec.portnum)

                    #
                    # text message
                    #

                    if dec.portnum == portnums_pb2.TEXT_MESSAGE_APP:

                        try:
                            txt=dec.payload.decode("utf-8","ignore")
                            print("TEXT:",txt)
                        except Exception as e:
                            print("TEXT ERR:",e)

                    #
                    # telemetry
                    #

                    elif dec.portnum == portnums_pb2.TELEMETRY_APP:

                        try:

                            t=telemetry_pb2.Telemetry()
                            t.ParseFromString(dec.payload)

                            print("TELEMETRY:")
                            print(t)
                        except Exception as e:
                            print("TELEMETRY ERR:",e)
                            print(hexify(dec.payload))
                    # admin
                    elif dec.portnum == portnums_pb2.ADMIN_APP:

                        try:

                            a=admin_pb2.AdminMessage()
                            a.ParseFromString(dec.payload)

                            print("ADMIN:")
                            print(a)
                        except Exception as e:

                            print("ADMIN ERR:",e)
                            print(hexify(dec.payload))

                    #
                    # unknown payload
                    #
                    else:

                        print("PAYLOAD:",hexify(dec.payload))

                #
                # encrypted packet
                #
                elif pkt.HasField("encrypted"):
                    print("ENCRYPTED:")
                    print(hexify(pkt.encrypted))

        except Exception as e:
            print("DECODE FAILED:",e)
