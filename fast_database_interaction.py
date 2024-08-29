from Database import Database

while True:
    query = input()
    database = Database('user_database.db')
    database.execute(query)
    print(database.get_result())