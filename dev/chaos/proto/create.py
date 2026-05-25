import sys
sys.path.append("/mnt/data/work/meshtastic/perl/protobufs/out/meshtastic/protobufs")

from meshtastic import mesh_pb2

msg = mesh_pb2.ToRadio()

# THIS is the important part
msg.want_config_id = 1   # sometimes boolean/int depending version

data = msg.SerializeToString()

print(data.hex())
print("len =", len(data))

