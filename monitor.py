import sqlite3
import re
import ast
from meshtastic.protobuf import mesh_pb2

DB = "mesh.db"
conn = sqlite3.connect(DB)

# rows become dict-like
conn.row_factory = sqlite3.Row

c = conn.cursor()
c.execute("""
    SELECT *
    FROM nodes
    LIMIT 5
""")
rows = c.fetchall()
#for row in rows:
#    print(dict(row))

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
    LIMIT 14
""")
rows = c.fetchall()

for row in rows:
    (text,typ,name) = (row["text"],row["type"],row["name"])
    if re.search(r"portnum",text):
        obj = ast.literal_eval(text)
        print ("portnum found")
        print(obj["text"])
        print("-------------------------------------")






