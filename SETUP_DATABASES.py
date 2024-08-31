from Database import Database

database = Database('answer_an_questions.db')

try:
    database.execute('DROP TABLE users')
except:
    pass

database.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id INTEGER, user_id INTEGER, answer TEXT)')


database = Database('logs.db')

try:
    database.execute('DROP TABLE logs')
except:
    pass

database.execute('CREATE TABLE logs (id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, type TEXT, user_id INTEGER, description TEXT)')


database = Database('questions.db')

try:
    database.execute('DROP TABLE questions')
except:
    pass

database.execute('CREATE TABLE questions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, description TEXT)')


database = Database('reports.db')

try:
    database.execute('DROP TABLE reports')
except:
    pass

database.execute('CREATE TABLE reports (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, description TEXT)')


database = Database('user_database.db')

try:
    database.execute('DROP TABLE users')
except:
    pass

database.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, chat_id INTEGER, ban_status INTEGER, menu TEXT, data_storage TEXT, user_info TEXT)')