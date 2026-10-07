import sqlite3
import json
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "jobs.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for Jobs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT,
        posted_time TEXT,
        job_url TEXT NOT NULL,
        is_easy_apply INTEGER DEFAULT 0,
        description TEXT,
        match_score INTEGER DEFAULT 0,
        match_reasons TEXT,
        status TEXT DEFAULT 'DISCOVERED',
        applied_at TIMESTAMP,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Table for Leads / Hiring Managers (LinkedIn Premium target contacts)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT,
        name TEXT NOT NULL,
        headline TEXT,
        profile_url TEXT NOT NULL,
        inmail_subject TEXT,
        inmail_message TEXT,
        status TEXT DEFAULT 'DRAFTED',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    )
    """)

    conn.commit()
    conn.close()


def save_job(
    job_id: str,
    title: str,
    company: str,
    location: str,
    posted_time: str,
    job_url: str,
    is_easy_apply: bool,
    description: str = "",
    match_score: int = 0,
    match_reasons: Optional[List[str]] = None,
) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    reasons_json = json.dumps(match_reasons or [])
    try:
        cursor.execute(
            """
            INSERT INTO jobs (id, title, company, location, posted_time, job_url, is_easy_apply, description, match_score, match_reasons)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                company=excluded.company,
                location=excluded.location,
                posted_time=excluded.posted_time,
                is_easy_apply=excluded.is_easy_apply,
                description=COALESCE(excluded.description, jobs.description)
            """,
            (
                job_id,
                title,
                company,
                location,
                posted_time,
                job_url,
                1 if is_easy_apply else 0,
                description,
                match_score,
                reasons_json,
            ),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def update_job_status(job_id: str, status: str, notes: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        now = datetime.now().isoformat() if status == "APPLIED" else None
        cursor.execute(
            """
            UPDATE jobs
            SET status = ?, notes = ?, applied_at = COALESCE(?, applied_at)
            WHERE id = ?
            """,
            (status, notes, now, job_id),
        )
        conn.commit()
    finally:
        conn.close()


def save_lead(
    job_id: str,
    name: str,
    headline: str,
    profile_url: str,
    inmail_subject: str = "",
    inmail_message: str = "",
) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO leads (job_id, name, headline, profile_url, inmail_subject, inmail_message)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (job_id, name, headline, profile_url, inmail_subject, inmail_message),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_jobs(status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if status:
            cursor.execute(
                "SELECT * FROM jobs WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit),
            )
        else:
            cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_leads(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT l.*, j.title as job_title, j.company as job_company
            FROM leads l
            LEFT JOIN jobs j ON l.job_id = j.id
            ORDER BY l.created_at DESC LIMIT ?
            """,
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_daily_applied_count() -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        today_start = date.today().isoformat()
        cursor.execute(
            """
            SELECT COUNT(*) FROM jobs
            WHERE status = 'APPLIED' AND DATE(applied_at) = DATE(?)
            """,
            (today_start,),
        )
        count = cursor.fetchone()[0]
        return count
    finally:
        conn.close()


def get_statistics() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_discovered = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'APPLIED'")
        total_applied = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_easy_apply = 1")
        total_easy_apply = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM leads")
        total_leads = cursor.fetchone()[0]

        today_applied = get_daily_applied_count()

        return {
            "total_discovered": total_discovered,
            "total_easy_apply": total_easy_apply,
            "total_applied": total_applied,
            "applied_today": today_applied,
            "total_leads": total_leads,
        }
    finally:
        conn.close()
