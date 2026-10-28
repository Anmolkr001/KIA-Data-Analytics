"""
Audit logging for Ask Your Data queries, generated code, execution outcomes, and latency.
Writes to logs/query_audit.jsonl in JSON Lines format.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from ask_your_data.config import ROOT_DIR

LOG_DIR = ROOT_DIR / "logs"
LOG_FILE = LOG_DIR / "query_audit.jsonl"


def log_query_interaction(
    question: str,
    plan: str,
    generated_code: str,
    outcome: str,
    success: bool,
    retries: int,
    latency_ms: float,
    summary: str,
    chart_type: Optional[str] = None,
    error: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Logs every question, code generated, retry count, and outcome to a JSONL audit file."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "plan": plan,
            "code": generated_code,
            "success": success,
            "outcome": outcome,
            "retries": retries,
            "latency_ms": round(latency_ms, 2),
            "summary": summary,
            "chart_type": chart_type,
            "error": error,
            "extra": extra or {},
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
    except Exception as e:
        print(f"[Warning] Failed to write audit log: {e}")


def read_recent_logs(limit: int = 50) -> list:
    """Reads recent audit log entries for observability."""
    if not LOG_FILE.exists():
        return []
    logs = []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    logs.append(json.loads(line))
        return logs[-limit:]
    except Exception as e:
        print(f"[Warning] Failed to read audit logs: {e}")
        return []
