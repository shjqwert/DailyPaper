import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                date     TEXT NOT NULL,
                项目     TEXT NOT NULL,
                节点     TEXT NOT NULL,
                类型     TEXT NOT NULL,
                模块     TEXT NOT NULL,
                时间类型 TEXT NOT NULL,
                时间     REAL NOT NULL,
                工作内容 TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now','localtime'))
            )
        """)


def add_log(date_str, 项目, 节点, 类型, 模块, 时间类型, 时间, 工作内容):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO logs (date,项目,节点,类型,模块,时间类型,时间,工作内容) VALUES (?,?,?,?,?,?,?,?)",
            (date_str, 项目, 节点, 类型, 模块, 时间类型, 时间, 工作内容)
        )


def query_by_id(log_id: int):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM logs WHERE id=?", (log_id,)
        ).fetchall()


def query_by_date(date_str):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM logs WHERE date=? ORDER BY id", (date_str,)
        ).fetchall()


def query_by_range(start: str, end: str):
    """start/end 格式 YYYY-MM-DD，含两端"""
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM logs WHERE date BETWEEN ? AND ? ORDER BY date, id",
            (start, end)
        ).fetchall()


def get_week_range(offset=0):
    """offset=0 本周，offset=-1 上周"""
    today = date.today() + timedelta(weeks=offset)
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start.isoformat(), end.isoformat()


def get_month_range(offset=0):
    """offset=0 本月，offset=-1 上月"""
    today = date.today()
    month = today.month + offset
    year = today.year + (month - 1) // 12
    month = ((month - 1) % 12) + 1
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start.isoformat(), end.isoformat()


def delete_log(log_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM logs WHERE id=?", (log_id,))
