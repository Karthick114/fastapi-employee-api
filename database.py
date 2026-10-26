
import sqlite3

def get_connection():
    connection = sqlite3.connect("employees.db")
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            experience INTEGER NOT NULL
        )
    """)

    connection.commit()
    connection.close()
