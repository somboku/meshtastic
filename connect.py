import meshtastic.serial_interface
iface = meshtastic.serial_interface.SerialInterface()


for k, v in vars(iface.localNode).items():
    print(k, "=", v)
print("=========================================================")

for node_id, node in iface.nodes.items():
    print(node_id)
    print(node)
    print("------")

print(iface.localNode)

