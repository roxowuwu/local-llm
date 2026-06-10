import sqlite3
import json
import time
import os


class LongTermMemory:

    def __init__(self, db_path: str = "memory/long_term.db"):
        os.makedirs("memory", exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        self._init_tables()

    # -----------------------------
    # INIT TABLES
    # -----------------------------
    def _init_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            action_json TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            user_input TEXT,
            response TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at INTEGER
        )
        """)

        self.conn.commit()

    # -----------------------------
    # STORE ACTION
    # -----------------------------
    def store_action(self, action_data: dict):
        data = json.dumps(action_data)
        ts = int(time.time())

        self.cursor.execute(
            "INSERT INTO actions (timestamp, action_json) VALUES (?, ?)",
            (ts, data)
        )
        self.conn.commit()

    # -----------------------------
    # GET LAST ACTION
    # -----------------------------
    def get_last_action(self):
        self.cursor.execute(
            "SELECT action_json FROM actions ORDER BY timestamp DESC LIMIT 1"
        )
        row = self.cursor.fetchone()

        if not row:
            return None

        return json.loads(row[0])

    # -----------------------------
    # STORE INTERACTION
    # -----------------------------
    def store_interaction(self, user_input: str, response: str):
        ts = int(time.time())

        self.cursor.execute(
            "INSERT INTO interactions (timestamp, user_input, response) VALUES (?, ?, ?)",
            (ts, user_input, response)
        )
        self.conn.commit()

    # -----------------------------
    # GET RECENT INTERACTIONS
    # -----------------------------
    def get_recent_interactions(self, n: int = 10):
        self.cursor.execute(
            "SELECT user_input, response FROM interactions ORDER BY timestamp DESC LIMIT ?",
            (n,)
        )

        rows = self.cursor.fetchall()

        results = []
        for user_input, response in rows:
            results.append({
                "user_input": user_input,
                "response": response
            })

        return results[::-1]  # reverse to chronological order

    # -----------------------------
    # STORE PREFERENCE (UPSERT)
    # -----------------------------
    def store_preference(self, key: str, value: str):
        ts = int(time.time())

        self.cursor.execute("""
        INSERT INTO preferences (key, value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
        """, (key, value, ts))

        self.conn.commit()

    # -----------------------------
    # GET PREFERENCE
    # -----------------------------
    def get_preference(self, key: str):
        self.cursor.execute(
            "SELECT value FROM preferences WHERE key = ?",
            (key,)
        )

        row = self.cursor.fetchone()

        if not row:
            return None

        return row[0]
