import sqlite3
import inspect
import ast
import json
import traceback
import pprint
from datetime import datetime

DB = "mesh.db"




def dump_caller():
    frame = inspect.currentframe().f_back
    print("caller:", frame.f_code.co_name)
    print("file:", frame.f_code.co_filename)
    print("line:", frame.f_lineno)
    print("locals:", frame.f_locals)

def write_to_file(data="",b=""):
    ts = datetime.now().strftime("%d.%m %H:%M")
    line = f"{ts} {data}"
    print(line)
    with open("./db.py.log", "a", encoding="utf-8") as f:
        f.write(line)
    return
#__________________________________________________________________________
#=============================================================================================================


def insert_packet(packet):
    node_id = packet.get("fromId") or str(packet.get("from"))
    to_id = packet.get("toId") or str(packet.get("to"))
    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("""
            INSERT INTO packets (node_id,json,raw) 
            values (?,?,?)""",
            (node_id,
            json.dumps(packet, default=str),
            pprint.pformat(packet)
            ))
        conn.commit()
        #print("insert whole packet commited")
    except Exception as e:
        import traceback
        print("DB ERROR:",e)
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

    caller = inspect.stack()[1]
    f=caller.filename
    fn = f.split("/")[-1]
    l=f"insert_packet() from {fn} -> {caller.function}"
    write_to_file(l)

    return
#____________________________________________________________________________



def update_node(node_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    update nodes 
    set last_seen = datetime('now','localtime')
    where node_id = ?
    """,(node_id,))
    conn.commit()
    conn.close()

    caller = inspect.stack()[1]
    f=caller.filename
    fn = f.split("/")[-1]
    l=f"update_node() from {fn} -> {caller.function}"
    write_to_file(l)
#__________________________________________________________________________



def update_full_node(node_id, name, hw, last_seen,last_heard):
    update_node(node_id)
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    if not last_seen: 
        last_seen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
    INSERT INTO nodes (
        node_id,
        name,
        hw,
        first_seen,
        last_seen,
        last_heard
    )
    VALUES (
        ?, ?, ?,
        datetime('now','localtime'),
        ?, ?
    )
    ON CONFLICT(node_id)
    DO UPDATE SET
        name=excluded.name,
        hw=excluded.hw,
        last_seen=excluded.last_seen
    """, (node_id, name, hw, last_seen,last_heard))
    (f"insert into update:{name} last: seen:{last_seen}")  
    conn.commit()
    conn.close()
 
    caller = inspect.stack()[1]
    f=caller.filename
    fn = f.split("/")[-1]
    l=f"update_full_node() from {fn} -> {caller.function}"
    write_to_file(l)
#__________________________________________________________________________



def insert_message(node_id, msg_type, text,pac,deco,grml):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    INSERT INTO messages (
        node_id,
        type,
        text,
        ts,
        pac,
        deco,
        messages_type
    )
    VALUES (?, ?, ?,
        datetime('now','localtime'),
        ?,?,?
    )
    """, (node_id, 
            msg_type, 
            json.dumps(text),
            pac,
            deco,
            grml
        ))
    conn.commit()
    conn.close()

    caller = inspect.stack()[1]
    f=caller.filename
    fn = f.split("/")[-1]
    l=f"insert_message() from {fn} -> {caller.function}"
    write_to_file(l)
#__________________________________________________________________________



def insertNodeInfo(packet,interface):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    insert into node_info (full_raw)
    values (?)
    """, (json.dumps(packet, default=str))
    )

    caller = inspect.stack()[1]
    f=caller.filename
    fn = f.split("/")[-1]
    l=f"insert_NodeInfo() from {fn} -> {caller.function}"
    write_to_file(l)
#__________________________________________________________________________



def get_nodes():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    SELECT
        node_id,
        name,
        hw,
        first_seen,
        last_seen
    FROM nodes
    ORDER BY last_seen DESC
    """)

    rows = c.fetchall()
    conn.close()
    return rows

    caller = inspect.stack()[1]
    f=caller.filename
    fn = f.split("/")[-1]
    l=f"get_nodes() from {fn} -> {caller.function}"
    write_to_file(l)
#__________________________________________________________________________
 


def clean_text(text):
    if not isinstance(text, str):
        return str(text)

    # fast path: only structured packets
    if "portnum" in text:
        obj = None

        # try JSON first
        try:
            obj = json.loads(text)
        except Exception:
            pass
        if isinstance(obj, str):
            obj = json.loads(obj)
        # fallback: python repr
        if obj is None:
            try:
                obj = ast.literal_eval(text)
            except Exception:
                return text  # give up safely

        if isinstance(obj, dict):
            user = obj.get("user", {})
            name = user.get("longName")
            hw = user.get("hwModel")

            if name and hw:
                return f"{name} on a <span style=color:red; >{hw}</span>"

    return text

def get_messages(limit=1144,):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT *
        FROM (
            SELECT
                id,
                ts,
                node_id,
                type,
                text,
                ROW_NUMBER() OVER (
                    PARTITION BY node_id
                    ORDER BY ts DESC
                ) AS rn
            FROM messages
        )
        WHERE rn <= 10
        ORDER BY ts DESC;
    """)

    rows = c.fetchall()
    #print(rows)
    dummy = []
    ctr = {}
    for row in rows:
        (text,ts,node_id) = (row["text"],row["ts"],row["node_id"])
        txt = clean_text(text)        
       # if node_id not in ctr:
       #     ctr[node_id] = {"cn":0}
       # ctr[node_id]["cn"] += 1

       # if ctr[node_id]["cn"] > 10:
        #   continue
        dummy.append({
            "node_id": node_id,
            "text": txt,
            "ts": row["ts"],
        })
    conn.close()
    caller = inspect.stack()[1]
    f=caller.filename
    fn = f.split("/")[-1]
    l=f"get_messages() from {fn} -> {caller.function}"
    write_to_file(l)

    return dummy
#__________________________________________________________________________





def init():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS nodes (
        node_id TEXT PRIMARY KEY,
        name TEXT,
        hw TEXT,
        first_seen TEXT,
        last_seen TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT DEFAULT CURRENT_TIMESTAMP,
        node_id TEXT,
        type TEXT,
        text TEXT
    )
    """)

    conn.commit()
    conn.close()

