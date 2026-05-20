import json
import ast
import db

messages = db.easy("""
    select * from messages 
    where node_id = '!b2a735f0' 
    order by ts
    DESC
    limit 19
    """)
def maybe_parse(field):
    if not isinstance(field, str):
        return field
    if field.strip().startswith(("{", "[")):
        try:
            return ast.literal_eval(field)
        except Exception:
            return field
    return field
    
messages = db.get_messages()

for node in messages:
    print ("=============================================================")
    if "35f0" in node.get("node_id"): 
        print(node)
 #   line = [maybe_parse(f) for f in node]
 #   print(line[3], line[4],line[5]("from"))
#
#    packet = ast.literal_eval(node)
#    print(packet)


