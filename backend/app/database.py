import sqlite3
from datetime import datetime
from app import config

#connection to our SQLite database file.
def get_connection():
    return sqlite3.connect(config.DB_PATH)

# Creates the logs table if it doesn't already exist
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            answer_found INTEGER NOT NULL,
            response_time_ms INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

#logging queries to the database. This function is called every time someone hits the /ask endpoint.
def log_query(question: str, answer: str, answer_found: bool, response_time_ms: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO query_logs (question, answer, answer_found, response_time_ms, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (question, answer, int(answer_found), response_time_ms, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()

# Returns the most frequently asked questions.
def get_most_frequent_questions(limit: int = 10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT lower(trim(question)) AS question, COUNT(*) AS times_asked
        FROM query_logs
        GROUP BY lower(trim(question))
        ORDER BY times_asked DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [{"question": row[0], "times_asked": row[1]} for row in rows]

# Returns the unanswered queries.
def get_unanswered_queries(limit: int = 20):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT question, created_at
        FROM query_logs
        WHERE answer_found = 0
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [{"question": row[0], "asked_at": row[1]} for row in rows]

# Returns the average response time across all logged questions, in ms.
def get_average_latency():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT AVG(response_time_ms) FROM query_logs")
    result = cursor.fetchone()[0]

    conn.close()

    return round(result, 2) if result is not None else 0

# Returns the total number of queries logged in the database.
def get_total_query_count():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM query_logs")
    count = cursor.fetchone()[0]

    conn.close()
    return count