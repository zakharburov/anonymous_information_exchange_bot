class Database:
    def __init__(self, database: str):
        import sqlite3 as sql

        base_folder_path = 'Databases/'
        folder_path = ''

        self.__connection = sql.connect(f'{base_folder_path if folder_path == "" else folder_path}{database}')
        self.__cursor = self.__connection.cursor()

    def execute(self, command: str):
        self.__cursor.execute(command)
        self.__connection.commit()

    def get_result(self):
        return self.__cursor.fetchall()
