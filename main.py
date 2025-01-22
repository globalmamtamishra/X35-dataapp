import sqlite3
import json
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application

# Database setup
DB_NAME = "polls.db"

# Initialize database and create tables
def init_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    # Create the polls table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS polls (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        is_active BOOLEAN NOT NULL
    );
    """)

    # Create the options table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS options (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        polls_Id INTEGER NOT NULL,
        FOREIGN KEY (polls_Id) REFERENCES polls (Id)
    );
    """)

    # Create the votes table
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

# Base handler to set default headers
class BaseHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

# Polls API: Handles creation and retrieval of polls
class PollsHandler(BaseHandler):
    def get(self):
        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM polls")
        polls = cursor.fetchall()
        connection.close()

        # Format response as JSON
        response = [{"Id": poll[0], "question": poll[1], "is_active": bool(poll[2])} for poll in polls]
        self.write(json.dumps(response))

    def post(self):
        data = json.loads(self.request.body)
        question = data.get("question")
        is_active = data.get("is_active", True)

        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO polls (question, is_active) VALUES (?, ?)",
            (question, int(is_active))
        )
        connection.commit()
        connection.close()

        self.write({"message": "Poll added successfully!"})

# Options API: Handles creation and retrieval of poll options
class OptionsHandler(BaseHandler):
    def get(self):
        poll_id = self.get_argument("poll_id", None)
        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()

        if poll_id:
            cursor.execute("SELECT * FROM options WHERE polls_Id = ?", (poll_id,))
        else:
            cursor.execute("SELECT * FROM options")

        options = cursor.fetchall()
        connection.close()

        # Format response as JSON
        response = [{"Id": option[0], "description": option[1], "polls_Id": option[2]} for option in options]
        self.write(json.dumps(response))

    def post(self):
        data = json.loads(self.request.body)
        description = data.get("description")
        polls_Id = data.get("polls_Id")

        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO options (description, polls_Id) VALUES (?, ?)",
            (description, polls_Id)
        )
        connection.commit()
        connection.close()

        self.write({"message": "Option added successfully!"})

# Votes API: Handles voting functionality
class VotesHandler(BaseHandler):
    def post(self):
        data = json.loads(self.request.body)
        question_Id = data.get("question_Id")
        option_Id = data.get("option_Id")

        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO votes (question_Id, option_Id) VALUES (?, ?)",
            (question_Id, option_Id)
        )
        connection.commit()
        connection.close()

        self.write({"message": "Vote added successfully!"})

# Create the Tornado application
def make_app():
    return Application([
        (r"/polls", PollsHandler),
        (r"/options", OptionsHandler),
        (r"/votes", VotesHandler),
    ])

if __name__ == "__main__":
    init_db()  # Initialize the database and create tables
    app = make_app()
    app.listen(8848)
    print("Server running on http://localhost:8848")
    IOLoop.current().start()
