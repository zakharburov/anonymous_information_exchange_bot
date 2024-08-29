import Database
import datetime


class Logger:
    def __init__(self, src):
        self.database = Database.Database(src)

    def log(self, log_type, user_id, description):
        self.database.execute(f"INSERT INTO logs (time, type, user_id, description) VALUES ('{datetime.datetime.now()}', '{log_type}', {user_id}, '{description}')")
