import sqlite3
import os

DB_PATH = os.path.join('instance', 'alarms.db')

def check_database():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n=== Alarm Table Contents ===")
    cursor.execute("SELECT * FROM alarm")
    alarms = cursor.fetchall()
    if not alarms:
        print("No alarms found.")
    for alarm in alarms:
        print(f"ID: {alarm['id']}")
        print(f"Time: {alarm['time']}")
        print(f"Label: {alarm['label']}")
        print(f"Days: {alarm['days']}")
        print(f"Specific Date: {alarm['specific_date']}")
        print(f"Active: {alarm['is_active']}")
        print(f"Created At: {alarm['created_at']}")
        print("-" * 30)

    print("\n=== Memo Table Contents ===")
    cursor.execute("SELECT * FROM memo")
    memos = cursor.fetchall()
    if not memos:
        print("No memos found.")
    for memo in memos:
        print(f"ID: {memo['id']}")
        print(f"Content: {memo['content']}")
        print(f"Date: {memo['date']}")
        print(f"Created At: {memo['created_at']}")
        print("-" * 30)

    conn.close()

if __name__ == "__main__":
    check_database()