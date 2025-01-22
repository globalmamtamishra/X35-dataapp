import sqlite3

DB_NAME = "polls.db"

def init_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS polls (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        is_active BOOLEAN NOT NULL
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS options (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        polls_Id INTEGER NOT NULL,
        FOREIGN KEY (polls_Id) REFERENCES polls (Id)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_Id INTEGER NOT NULL,
        option_Id INTEGER NOT NULL,
        FOREIGN KEY (question_Id) REFERENCES polls (Id),
        FOREIGN KEY (option_Id) REFERENCES options (Id)
    );
    """)

    connection.commit()
    connection.close()
    print("Tables created successfully.")
