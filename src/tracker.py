import sqlite3
from datetime import datetime
from pathlib import Path


class Tracker:
    def __init__(self, db_path: str = "usage.db"):
        self.db = Path(db_path)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts          TEXT,
                    model       TEXT,
                    tier        TEXT,
                    input_tok   INTEGER,
                    output_tok  INTEGER,
                    cost_usd    REAL,
                    latency_ms  INTEGER
                )
            """)

    def record(self, *, model, tier, input_tok, output_tok, cost_usd, latency_ms):
        with sqlite3.connect(self.db) as conn:
            conn.execute(
                "INSERT INTO usage (ts,model,tier,input_tok,output_tok,cost_usd,latency_ms) VALUES (?,?,?,?,?,?,?)",
                (datetime.utcnow().isoformat(), model, tier, input_tok, output_tok, cost_usd, latency_ms),
            )

    def summary(self) -> dict:
        with sqlite3.connect(self.db) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT model, tier,
                       COUNT(*)          AS calls,
                       SUM(input_tok)    AS total_input,
                       SUM(output_tok)   AS total_output,
                       SUM(cost_usd)     AS total_cost,
                       AVG(latency_ms)   AS avg_latency
                FROM usage
                GROUP BY model, tier
                ORDER BY total_cost DESC
            """).fetchall()

        total_cost = sum(r["total_cost"] for r in rows)
        total_calls = sum(r["calls"] for r in rows)
        return {
            "total_calls": total_calls,
            "total_cost_usd": round(total_cost, 6),
            "by_model": [dict(r) for r in rows],
        }
