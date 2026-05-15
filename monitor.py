import ast
import base64
import sqlite3
import re
import json
from meshtastic.protobuf import mesh_pb2
import sys

DB = "mesh.db"
conn = sqlite3.connect(DB)

# rows become dict-like
conn.row_factory = sqlite3.Row

c = conn.cursor()
#msg = mesh_pb2.User()
#msg.ParseFromString(data)
#print(msg)

print ("==================================================================================")
c.execute("""
    SELECT
        nodes.name,
        messages.type,
        messages.text,
        messages.ts
    FROM messages
    JOIN nodes
    ON messages.node_id = nodes.node_id
    where messages.text not like '%battery%'
    ORDER BY messages.ts DESC
    LIMIT 30
""")
rows = c.fetchall()

for row in rows:
    
    (text,typ,name) = (row["text"],row["type"],row["name"])
    res = text
    if text == '{}':
        res = 'empty :/'
    if "portnum" in text:
            print(text)

            obj = json.loads(text)
            user = obj.get("user")
            payload = obj.get("payload")
            msg = mesh_pb2.NodeInfo()
            msg.ParseFromString(payload)
        #    print(msg)

            res = f'{user["longName"]} on a {user["hwModel"]} >>>{payload}<<<'
    print(res)



