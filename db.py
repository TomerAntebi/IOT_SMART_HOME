# db.py
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path("smart_room.db")


def get_conn(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    conn = get_conn(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts REAL NOT NULL,
        temp REAL NOT NULL,
        hum REAL NOT NULL,
        mode TEXT NOT NULL,
        level TEXT NOT NULL,
        message TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts REAL NOT NULL,
        type TEXT NOT NULL,      -- e.g., MODE_CHANGE, ALERT, RELAY_CMD
        level TEXT NOT NULL,     -- INFO/WARNING/ALARM
        details TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def insert_measurement(ts: float, temp: float, hum: float, mode: str, level: str, message: str,
                      db_path: Path = DB_PATH) -> None:
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO measurements (ts, temp, hum, mode, level, message)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ts, temp, hum, mode, level, message))
    conn.commit()
    conn.close()


def insert_event(ts: float, event_type: str, level: str, details: str,
                 db_path: Path = DB_PATH) -> None:
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO events (ts, type, level, details)
        VALUES (?, ?, ?, ?)
    """, (ts, event_type, level, details))
    conn.commit()
    conn.close()

