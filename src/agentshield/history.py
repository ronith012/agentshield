"""Test history storage using SQLite."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from agentshield.models import AgentTestSuiteResult as TestSuiteResult


class TestHistory:
    """Store and retrieve test history."""

    def __init__(self, db_path: str | Path = ".agentshield/history.db"):
        """Initialize test history storage.

        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS test_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    agent_name TEXT,
                    total_tests INTEGER,
                    passed INTEGER,
                    failed INTEGER,
                    errors INTEGER,
                    duration_seconds REAL,
                    suite_result_json TEXT
                )
                """
            )
            conn.commit()

    def save_run(
        self,
        suite_result: TestSuiteResult,
        agent_name: str,
    ):
        """Save a test run to history.

        Args:
            suite_result: The test suite results
            agent_name: Name of the agent tested
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO test_runs (
                    timestamp, agent_name, total_tests, passed, failed, errors,
                    duration_seconds, suite_result_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.utcnow().isoformat(),
                    agent_name,
                    suite_result.total_tests,
                    suite_result.passed,
                    suite_result.failed,
                    suite_result.errors,
                    suite_result.total_duration_seconds,
                    suite_result.model_dump_json(),
                ),
            )
            conn.commit()

    def get_recent_runs(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent test runs.

        Args:
            limit: Maximum number of runs to return

        Returns:
            List of test run dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, timestamp, agent_name, total_tests, passed, failed, errors, duration_seconds
                FROM test_runs
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "timestamp": row[1],
                "agent_name": row[2],
                "total_tests": row[3],
                "passed": row[4],
                "failed": row[5],
                "errors": row[6],
                "duration_seconds": row[7],
            }
            for row in rows
        ]

    def get_trends(self, agent_name: str | None = None, runs: int = 20) -> dict[str, Any]:
        """Get test trends over time.

        Args:
            agent_name: Filter by agent name (optional)
            runs: Number of recent runs to analyze

        Returns:
            Dictionary with trend statistics
        """
        query = """
            SELECT timestamp, passed, failed, errors, total_tests
            FROM test_runs
        """
        params = []

        if agent_name:
            query += " WHERE agent_name = ?"
            params.append(agent_name)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(runs)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        if not rows:
            return {"message": "No test history found"}

        # Calculate trends
        pass_rates = [row[1] / row[4] * 100 for row in rows if row[4] > 0]
        avg_pass_rate = sum(pass_rates) / len(pass_rates) if pass_rates else 0

        recent = rows[0]
        oldest = rows[-1]

        return {
            "total_runs": len(rows),
            "average_pass_rate": round(avg_pass_rate, 2),
            "most_recent": {
                "timestamp": recent[0],
                "passed": recent[1],
                "failed": recent[2],
                "errors": recent[3],
            },
            "oldest_in_range": {
                "timestamp": oldest[0],
                "passed": oldest[1],
                "failed": oldest[2],
                "errors": oldest[3],
            },
        }
