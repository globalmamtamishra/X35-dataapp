import tornado.ioloop
import tornado.web
import sqlite3
from db_utils import init_db, DB_NAME

class BaseHandler(tornado.web.RequestHandler):
    def get_db_connection(self):
        return sqlite3.connect(DB_NAME)

class MainHandler(BaseHandler):
    def get(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM polls WHERE is_active = 1")
        polls = cursor.fetchall()
        connection.close()
        self.render("index.html", polls=polls)

class CreatePollHandler(BaseHandler):
    def get(self):
        self.render("create_poll.html")

    def post(self):
        question = self.get_argument("question")
        options = self.get_arguments("options")
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO polls (question, is_active) VALUES (?, 1)", (question,))
        poll_id = cursor.lastrowid
        for option in options:
            cursor.execute("INSERT INTO options (description, polls_Id) VALUES (?, ?)", (option, poll_id))
        connection.commit()
        connection.close()
        self.redirect("/")

class PollHandler(BaseHandler):
    def get(self, poll_id):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM polls WHERE Id = ?", (poll_id,))
        poll = cursor.fetchone()
        cursor.execute("SELECT * FROM options WHERE polls_Id = ?", (poll_id,))
        options = cursor.fetchall()
        connection.close()
        self.render("poll.html", poll=poll, options=options)

    def post(self, poll_id):
        option_id = self.get_argument("option")
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO votes (question_Id, option_Id) VALUES (?, ?)", (poll_id, option_id))
        connection.commit()
        connection.close()
        self.redirect(f"/poll/{poll_id}")

class AdminHandler(BaseHandler):
    def get(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM polls")
        polls = cursor.fetchall()
        cursor.execute("SELECT * FROM options")
        options = cursor.fetchall()
        cursor.execute("SELECT * FROM votes")
        votes = cursor.fetchall()
        connection.close()
        self.render("admin.html", polls=polls, options=options, votes=votes)

class DeletePollHandler(BaseHandler):
    def post(self, poll_id):
        connection = self.get_db_connection()
        cursor = connection.cursor()

        # Delete associated votes and options before deleting the poll
        cursor.execute("DELETE FROM votes WHERE question_Id = ?", (poll_id,))
        cursor.execute("DELETE FROM options WHERE polls_Id = ?", (poll_id,))
        cursor.execute("DELETE FROM polls WHERE Id = ?", (poll_id,))

        connection.commit()
        connection.close()

        self.redirect("/admin")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/create", CreatePollHandler),
        (r"/poll/(\d+)", PollHandler),
        (r"/admin", AdminHandler),
        (r"/delete/(\d+)", DeletePollHandler),
    ], debug=True, template_path="templates", static_path="static")

if __name__ == "__main__":
    init_db()
    app = make_app()
    app.listen(8808)
    print("Tornado app running at http://localhost:8808")
    tornado.ioloop.IOLoop.current().start()
