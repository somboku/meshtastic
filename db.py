import sqlite3
import json
DB = "mesh.db"

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

def update_full_node(node_id, name, hw, last_seen):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    INSERT INTO nodes (
        node_id,
        name,
        hw,
        first_seen,
        last_seen
    )
    VALUES (
        ?, ?, ?,
        datetime('now','localtime'),
        ? 
    )
    ON CONFLICT(node_id)
    DO UPDATE SET
        name=excluded.name,
        hw=excluded.hw,
        last_seen=excluded.last_seen
    """, (node_id, name, hw, last_seen))

    conn.commit()
    conn.close()

def insert_message(node_id, msg_type, text):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    INSERT INTO messages (
        node_id,
        type,
        text,
		ts
    )
    VALUES (?, ?, ?,
        datetime('now','localtime')
    )
    """, (node_id, msg_type, text)
    )

    conn.commit()
    conn.close()

def insertNodeInfo(packet,interface):
	conn = sqlite3.connect(DB)
	c = conn.cursor()
	c.execute("""
	insert into node_info (full_raw)
	values (?)
	""", (json.dumps(packet, default=str))
	)



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
def update_node(node_id):
	conn = sqlite3.connect(DB)
	c = conn.cursor()

	c.execute("""
	update nodes set (last_seen)
	values (datetime('now','localtime')) where node_id = ?
	""",(node_id))


def get_messages(limit=200):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    SELECT
        ts,
        node_id,
        type,
        substr(`text`,0,30) as text
    FROM messages
    ORDER BY ts DESC 
    LIMIT ?
    """, (limit,))

    rows = c.fetchall()
    conn.close()
    return rows
