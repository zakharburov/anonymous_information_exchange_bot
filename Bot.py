import telebot
import json
from Database import Database
from Logger import Logger


class Bot(telebot.TeleBot):
    def __init__(self):
        with open('bot_settings.json', 'r', encoding='utf-8') as settings:
            settings = json.load(settings)
            token = settings['Settings']['token']
            self.__rules = settings['Settings']['rules']
            self.__admins = settings['Settings']['admins']
            self.__commands = settings['Settings']['commands']
            self.__messages_for_commands = settings['Settings']['messages_for_commands']

        super().__init__(token)

        self.run()

    """
        *** Статичные функции ***
    """
    @staticmethod
    def make_new_user_id(user_id, chat_id, first_name, last_name, username):
        database = Database('user_database.db')
        database.execute(f"INSERT INTO users (user_id, chat_id, ban_status, menu, data_storage, user_info) VALUES ({user_id}, {chat_id}, 0, 'MAIN_MENU', '[[], []]', 'firstname: {first_name}, lastname: {last_name}, username: {username}')")
        database.execute(f'SELECT id FROM users WHERE user_id = {user_id}')

        id = database.get_result()[0][0]

        return id

    @staticmethod
    def get_user_hex_id(id):
        hex_id = hex(id)[2::]
        result = '0' * (4 - len(hex_id)) + hex_id

        return result

    @staticmethod
    def make_main_menu_markup(user_id, admins_list):
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

        button_send_message = telebot.types.KeyboardButton("Отправить работу")
        button_report = telebot.types.KeyboardButton("Пожаловаться")
        button_help = telebot.types.KeyboardButton("FAQ")

        markup.add(button_send_message, button_report)

        if user_id in admins_list:
            button_admin_panel = telebot.types.KeyboardButton("Админ-панель")
            markup.add(button_admin_panel)

        markup.add(button_help)

        return markup

    @staticmethod
    def make_admin_menu_markup():
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

        button_ban = telebot.types.KeyboardButton("Забанить")
        button_unban = telebot.types.KeyboardButton("Разбанить")
        button_answer_an_question = telebot.types.KeyboardButton("Ответить на вопрос")
        button_questions_list = telebot.types.KeyboardButton("Список вопросов")
        button_reports_list = telebot.types.KeyboardButton("Список жалоб")
        button_escape = telebot.types.KeyboardButton("Выйти")

        markup.add(button_ban, button_unban)
        markup.add(button_answer_an_question)
        markup.add(button_questions_list, button_reports_list)
        markup.add(button_escape)

        return markup

    @staticmethod
    def make_send_message_menu_markup():
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_send = telebot.types.KeyboardButton("Отправить")
        markup.add(button_send)

        return markup

    @staticmethod
    def make_help_menu_markup():
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

        button_1 = telebot.types.KeyboardButton("Как достигается анонимность?")
        button_2 = telebot.types.KeyboardButton("Как сохранить анонимность?")
        button_3 = telebot.types.KeyboardButton("Как отправлять работы?")

        button_another = telebot.types.KeyboardButton("Другой вопрос")
        button_escape = telebot.types.KeyboardButton("Выйти")

        markup.add(button_1)
        markup.add(button_2)
        markup.add(button_3)

        markup.add(button_another)
        markup.add(button_escape)

        return markup

    @staticmethod
    def make_answer_an_question_menu_markup():
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

        button_input_user_id = telebot.types.KeyboardButton("Ввести UserID")
        button_input_answer = telebot.types.KeyboardButton("Написать ответ")
        button_send_answer = telebot.types.KeyboardButton("Отправить")
        button_escape = telebot.types.KeyboardButton("Выйти")

        markup.add(button_input_user_id)
        markup.add(button_input_answer)
        markup.add(button_send_answer)
        markup.add(button_escape)

        return markup

    @staticmethod
    def make_reports_list_menu_markup():
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

        button_set_report_completed = telebot.types.KeyboardButton("Отметить жалобу рассмотренной")
        button_escape = telebot.types.KeyboardButton("Выйти")

        markup.add(button_set_report_completed)
        markup.add(button_escape)

        return markup

    @staticmethod
    def make_questions_list_menu_markup():
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

        button_set_question_completed = telebot.types.KeyboardButton("Отметить вопрос решенным")
        button_escape = telebot.types.KeyboardButton("Выйти")

        markup.add(button_set_question_completed)
        markup.add(button_escape)

        return markup

    @staticmethod
    def make_help_another_menu_markup():
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

        button_escape = telebot.types.KeyboardButton("Выйти")

        markup.add(button_escape)

        return markup

    @staticmethod
    def get_photos_id_list(message):
        database = Database('user_database.db')
        database.execute(f'SELECT data_storage FROM users WHERE user_id = {message.from_user.id}')

        data_storage_str = database.get_result()[0][0]
        photos_id_list = json.loads(data_storage_str)[1]

        return photos_id_list

    """
        *** Конец статичных функций ***
    """

    """
        *** Слэш команды ***
    """

    def command_start(self, message):
        database = Database('user_database.db')
        database.execute(f'SELECT * FROM users WHERE user_id = {message.from_user.id}')

        if len(database.get_result()) > 0:
            self.send_message(message.from_user.id, 'Аккаунт с вашим ID уже зарегистрирован!')

            database.execute(f"""UPDATE users SET data_storage = '[[], []]' WHERE user_id = {message.from_user.id}""")
            database.execute(f"UPDATE users SET menu = 'MAIN_MENU' WHERE user_id = {message.from_user.id}")

            database.execute(f'SELECT id FROM users WHERE user_id = {message.from_user.id}')
            id = database.get_result()[0][0]
            hex_id = self.get_user_hex_id(id)

            markup = self.make_main_menu_markup(user_id=message.from_user.id, admins_list=self.__admins)

            self.send_message(message.from_user.id, f'Your UserID: {hex_id}', reply_markup=markup)

            database = Database('answer_an_questions.db')
            database.execute(f"DELETE FROM users WHERE admin_id = {message.from_user.id}")

            # self.send_message(message.from_user.id, f'{self.__rules}\nYour UserID: {hex_id}', reply_markup=markup)  # Вывести список правил при каждом нажатии /start

            return

        id = self.make_new_user_id(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username)
        hex_id = self.get_user_hex_id(id)

        logger = Logger('logs.db')
        logger.log('New user', message.from_user.id, f'New user have started the bot. user hex_id: {hex_id}')
        print(f'New user. hex_id: {hex_id}, user_id: {message.from_user.id}')

        markup = self.make_main_menu_markup(user_id=message.from_user.id, admins_list=self.__admins)

        self.send_message(message.from_user.id, f'{self.__rules}\nYour UserID: {hex_id}', reply_markup=markup)

    """
        *** Конец слэш команд ***
    """

    """
        *** Функции для текстовых команд ***
    """

    """
        Команда отправки рабыты с компонентами
    """

    def text_command_send_message(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'SEND_MESSAGE_MENU' WHERE user_id = {message.from_user.id}")
        database.execute(f"UPDATE users SET data_storage = '[[], []]' WHERE user_id = {message.from_user.id}")

        markup = self.make_send_message_menu_markup()

        self.send_message(message.from_user.id, f'{self.__messages_for_commands["main_commands"]["Отправить работу"]}', reply_markup=markup)

    def text_command_send_message_action(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'MAIN_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_main_menu_markup(user_id=message.from_user.id, admins_list=self.__admins)

        self.send_message(message.from_user.id, 'Работа успешно отправлена', reply_markup=markup)

        logger = Logger('logs.db')
        logger.log('New message', message.from_user.id, f'User have sent message to everyone')

        database.execute('SELECT user_id FROM users WHERE ban_status = 0')
        users_id = database.get_result()
        for user in users_id:
            try:
                user = user[0]
                self.send_message(user, self.make_description(message=message))

                photos_id_list = self.get_photos_id_list(message=message)
                for photo_id in photos_id_list:
                    self.send_photo(user, photo_id)
            except:
                pass  # Предположительно: ошибка отправки, бот заблокирован пользователем

        database.execute(f"""UPDATE users SET data_storage = '[[], []]' WHERE user_id = {message.from_user.id}""")

    def make_description(self, message):
        description = ''

        database = Database('user_database.db')
        database.execute(f"SELECT data_storage FROM users WHERE user_id = {message.from_user.id}")
        data_storage_str = database.get_result()[0][0]
        data_storage = json.loads(data_storage_str)
        description_storage = data_storage[0]

        for part_of_description in description_storage:
            description += part_of_description + '\n'

        database.execute(f"SELECT id FROM users WHERE user_id = {message.from_user.id}")
        id = database.get_result()[0][0]

        description += f'\nUserID: {self.get_user_hex_id(id)}'

        return description

    @staticmethod
    def add_text_to_data_storage(message):
        database = Database('user_database.db')
        database.execute(f'SELECT data_storage FROM users WHERE user_id = {message.from_user.id}')

        data_storage_str = database.get_result()[0][0]
        data_storage = json.loads(data_storage_str)
        data_storage[0].append(message.text)
        data_storage_json = json.dumps(data_storage)

        database.execute(f"""UPDATE users SET data_storage = '{data_storage_json}' WHERE user_id = {message.from_user.id}""")

    @staticmethod
    def add_photo_to_data_storage(message):
        photo_id = message.photo[-1].file_id

        database = Database('user_database.db')
        database.execute(f'SELECT data_storage FROM users WHERE user_id = {message.from_user.id}')

        data_storage_str = database.get_result()[0][0]
        data_storage = json.loads(data_storage_str)
        data_storage[1].append(photo_id)
        data_storage_json = json.dumps(data_storage)

        database.execute(f"""UPDATE users SET data_storage = '{data_storage_json}' WHERE user_id = {message.from_user.id}""")

    @staticmethod
    def add_photos_text_to_data_storage(message):
        database = Database('user_database.db')
        database.execute(f'SELECT data_storage FROM users WHERE user_id = {message.from_user.id}')

        data_storage_str = database.get_result()[0][0]
        data_storage = json.loads(data_storage_str)
        data_storage[0].append(message.caption)
        data_storage_json = json.dumps(data_storage)

        database.execute(f"""UPDATE users SET data_storage = '{data_storage_json}' WHERE user_id = {message.from_user.id}""")

    """
        Конец команды отправки работы
    """

    """
        Команда жалобы с компонентами
    """

    @staticmethod
    def add_report_to_database(message):
        database = Database('reports.db')
        database.execute(f"INSERT INTO reports (user_id, description) VALUES ({message.from_user.id}, '{message.text}')")

    def text_command_report(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'REPORT_MENU' WHERE user_id = {message.from_user.id}")

        self.send_message(message.from_user.id, f'{self.__messages_for_commands["main_commands"]["Пожаловаться"]}', reply_markup=telebot.types.ReplyKeyboardRemove())

    def text_command_report_action(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'MAIN_MENU' WHERE user_id = {message.from_user.id}")

        self.add_report_to_database(message=message)

        markup = self.make_main_menu_markup(user_id=message.from_user.id, admins_list=self.__admins)

        self.send_message(message.from_user.id, f'Спасибо за бдительность, жалоба будет рассмотрена в ближайшее время', reply_markup=markup)

        logger = Logger('logs.db')
        logger.log('New report', message.from_user.id, f'User have sent new report. Report text: <{message.text}>')

    """
        Конец команды жалобы
    """

    """
        Команда перехода в админ-панель
    """

    def text_command_admin_panel(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_admin_menu_markup()

        self.send_message(message.from_user.id, 'Вы перешли в режим админа', reply_markup=markup)

        logger = Logger('logs.db')
        logger.log('Enter admin mode', message.from_user.id, 'User have entered to admin mode')

    """
        Конец команды перехода в админ-панель
    """

    """
        # Команды админ-панели #
    """

    """
        Команда бан с компонентами
    """

    def text_command_admin_mode_ban(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MODE_BAN_MENU' WHERE user_id = {message.from_user.id}")

        self.send_message(message.from_user.id, 'Введите UserID пользователя, которого необходимо забанить', reply_markup=telebot.types.ReplyKeyboardRemove())

    def text_command_admin_mode_ban_action(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_admin_menu_markup()

        try:
            id = int(message.text, 16)
            database.execute(f'UPDATE users SET ban_status = 1 WHERE id = {id}')
        except:
            self.send_message(message.from_user.id, 'Введен неверный UserID пользователя', reply_markup=markup)
            return

        self.send_message(message.from_user.id, 'Пользователь успешно забанен', reply_markup=markup)

        logger = Logger('logs.db')
        logger.log('Ban user', message.from_user.id, f'Admin have banned user {message.text}')

    """
        Конец команды бана
    """

    """
        Команда разбана с компонентами
    """

    def text_command_admin_mode_unban(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MODE_UNBAN_MENU' WHERE user_id = {message.from_user.id}")

        self.send_message(message.from_user.id, 'Введите UserID пользователя, которого необходимо разбанить', reply_markup=telebot.types.ReplyKeyboardRemove())

    def text_command_admin_mode_unban_action(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_admin_menu_markup()

        try:
            id = int(message.text, 16)
            database.execute(f'UPDATE users SET ban_status = 0 WHERE id = {id}')
        except:
            self.send_message(message.from_user.id, 'Введен неверный UserID пользователя', reply_markup=markup)
            return

        self.send_message(message.from_user.id, 'Пользователь успешно разбанен', reply_markup=markup)

        logger = Logger('logs.db')
        logger.log('Unban user', message.from_user.id, f'Admin have unbanned user {message.text}')

    """
        Конец команды разбана
    """

    """
        Команда выхода из админ-панели
    """

    def text_command_admin_mode_leave(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'MAIN_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_main_menu_markup(user_id=message.from_user.id, admins_list=self.__admins)

        self.send_message(message.from_user.id, 'Вы вышли из режима админа', reply_markup=markup)

        logger = Logger('logs.db')
        logger.log('Leave admin mode', message.from_user.id, 'User have left admin mode')

    """
        Конец команды выхода из админ-панели
    """

    """
        Команда ответа на вопрос с компонентами
    """

    def text_command_admin_mode_answer_an_question(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MODE_ANSWER_AN_QUESTION_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_answer_an_question_menu_markup()

        self.send_message(message.from_user.id, f'Вы перешли в меню ответа на вопрос', reply_markup=markup)

        database = Database('answer_an_questions.db')
        database.execute(f"INSERT INTO users (admin_id) VALUES ({message.from_user.id})")

    def text_command_admin_mode_answer_an_question_input_user_id(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MODE_ANSWER_AN_QUESTION_INPUT_USER_ID_MENU' WHERE user_id = {message.from_user.id}")

        self.send_message(message.from_user.id, 'Введите UserID пользователя', reply_markup=telebot.types.ReplyKeyboardRemove())

    def text_command_admin_mode_answer_an_question_input_user_id_action(self, message):
        try:
            database = Database('user_database.db')
            database.execute(f'SELECT user_id FROM users WHERE id = {int(message.text, 16)}')
            user_id = database.get_result()[0][0]

            database = Database('answer_an_questions.db')
            database.execute(f'UPDATE users SET user_id = {user_id} WHERE admin_id = {message.from_user.id}')

            markup = self.make_answer_an_question_menu_markup()

            self.send_message(message.from_user.id, f'Успешно введен UserID пользователя', reply_markup=markup)

            database = Database('user_database.db')
            database.execute(f"UPDATE users SET menu = 'ADMIN_MODE_ANSWER_AN_QUESTION_MENU' WHERE user_id = {message.from_user.id}")
        except:
            self.send_message(message.from_user.id, 'Пользователя с таким UserID не существует')
            return

    def text_command_admin_mode_answer_an_question_input_answer(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MODE_ANSWER_AN_QUESTION_INPUT_ANSWER_MENU' WHERE user_id = {message.from_user.id}")

        self.send_message(message.from_user.id, 'Напишите ответ пользователю', reply_markup=telebot.types.ReplyKeyboardRemove())

    def text_command_admin_mode_answer_an_question_input_answer_action(self, message):
        database = Database('answer_an_questions.db')
        database.execute(f"UPDATE users SET answer = '{message.text}' WHERE admin_id = {message.from_user.id}")

        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MODE_ANSWER_AN_QUESTION_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_answer_an_question_menu_markup()

        self.send_message(message.from_user.id, f'Успешно введен ответ пользователю', reply_markup=markup)

    def text_command_admin_mode_answer_an_question_send(self, message):
        database = Database('answer_an_questions.db')

        try:
            database.execute(f'SELECT user_id FROM users WHERE admin_id = {message.from_user.id}')
            user_id = database.get_result()[0][0]
            database.execute(f'SELECT answer FROM users WHERE admin_id = {message.from_user.id}')
            answer = database.get_result()[0][0]
            self.send_message(user_id, f'Ответ на ваш вопрос:\n{answer}')
        except:
            self.send_message(message.from_user.id, 'Какой-то из параметров не введен')
            return

        database.execute(f"DELETE FROM users WHERE admin_id = {message.from_user.id}")

        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_admin_menu_markup()

        self.send_message(message.from_user.id, 'Ответ успешно отправлен пользователю', reply_markup=markup)

        database.execute(f'SELECT id FROM users WHERE user_id = {user_id}')
        hex_id = self.get_user_hex_id(database.get_result()[0][0])
        logger = Logger('logs.db')
        logger.log('Send help', message.from_user.id, f'Admin have answered the user {hex_id} question with answer <{answer}> ')

    def text_command_admin_mode_answer_an_question_leave(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_admin_menu_markup()

        database = Database('answer_an_questions.db')
        database.execute(f'DELETE FROM users WHERE admin_id = {message.from_user.id}')

        self.send_message(message.from_user.id, 'Вы вышли из меню ответа на вопрос', reply_markup=markup)

    """
        Конец команды ответа на вопрос с компонентами
    """

    """
        Команда вызова списка жалоб с компонентами
    """

    def text_command_admin_mode_get_reports_list(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MODE_REPORTS_LIST_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_reports_list_menu_markup()

        self.send_message(message.from_user.id, 'Текущий список жалоб', reply_markup=markup)

        reports_database = Database('reports.db')
        reports_database.execute('SELECT * FROM reports')
        reports_list = reports_database.get_result()

        for report in reports_list:
            report_id, user_id, description = report

            database.execute(f'SELECT id FROM users WHERE user_id = {user_id}')
            id = database.get_result()[0][0]
            hex_user_id = self.get_user_hex_id(id)

            self.send_message(message.from_user.id, f'Жалоба:\n{description}\n\nReportID: {report_id}\nUserID: {hex_user_id}')

    def text_command_admin_mode_get_reports_list_set_report_completed(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MODE_REPORTS_LIST_SET_REPORT_COMPLETED_MENU' WHERE user_id = {message.from_user.id}")

        self.send_message(message.from_user.id, 'Введите ID рассмотренной жалобы', reply_markup=telebot.types.ReplyKeyboardRemove())

    def text_command_admin_mode_get_reports_list_set_report_completed_action(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MODE_REPORTS_LIST_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_reports_list_menu_markup()

        reports = Database('reports.db')
        try:
            reports.execute(f'SELECT description FROM reports WHERE id = {message.text}')
            report_text = reports.get_result()[0][0]

            reports.execute(f'DELETE FROM reports WHERE id = {message.text}')
            self.send_message(message.from_user.id, 'Жалоба успешно удалена', reply_markup=markup)

            database.execute(f"SELECT id FROM users WHERE user_id = {message.from_user.id}")
            id = database.get_result()[0][0]
            admin_hex_id = self.get_user_hex_id(id)

            logger = Logger('logs.db')
            logger.log('Delete report', message.from_user.id, f'Admin {admin_hex_id} has removed report from reports list. Report text <{report_text}>')
        except:
            self.send_message(message.from_user.id, 'Неверно указан ID жалобы', reply_markup=markup)

    def text_command_admin_mode_get_reports_list_leave(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_admin_menu_markup()

        self.send_message(message.from_user.id, 'Вы вышли из списка жалоб', reply_markup=markup)

    """
        Конец команды вызова списка жалоб с компонентами
    """

    """
        Команда вызова списка вопросов с компонентами
    """

    def text_command_admin_mode_get_questions_list(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MODE_QUESTIONS_LIST_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_questions_list_menu_markup()

        self.send_message(message.from_user.id, 'Текущий список вопросов', reply_markup=markup)

        questions_database = Database('questions.db')
        questions_database.execute('SELECT * FROM questions')
        questions_list = questions_database.get_result()

        for question in questions_list:
            question_id, user_id, description = question

            database.execute(f'SELECT id FROM users WHERE user_id = {user_id}')
            id = database.get_result()[0][0]
            hex_user_id = self.get_user_hex_id(id)

            self.send_message(message.from_user.id, f'Вопрос:\n{description}\n\nQuestionID: {question_id}\nUserID: {hex_user_id}')

    def text_command_admin_mode_get_questions_list_set_question_completed(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MODE_QUESTIONS_LIST_SET_QUESTION_COMPLETED_MENU' WHERE user_id = {message.from_user.id}")

        self.send_message(message.from_user.id, 'Введите ID решенного вопроса', reply_markup=telebot.types.ReplyKeyboardRemove())

    def text_command_admin_mode_get_questions_list_set_question_completed_action(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MODE_QUESTIONS_LIST_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_questions_list_menu_markup()

        questions = Database('questions.db')
        try:
            questions.execute(f'SELECT description FROM reports WHERE id = {message.text}')
            question = questions.get_result()[0][0]

            questions.execute(f'DELETE FROM questions WHERE id = {message.text}')
            self.send_message(message.from_user.id, 'Вопрос успешно удален', reply_markup=markup)

            database.execute(f"SELECT id FROM users WHERE user_id = {message.from_user.id}")
            id = database.get_result()[0][0]
            admin_hex_id = self.get_user_hex_id(id)

            logger = Logger('logs.db')
            logger.log('Delete question', message.from_user.id, f'Admin {admin_hex_id} has removed question from questions list. Question text <{question}>')
        except:
            self.send_message(message.from_user.id, 'Неверно указан ID вопроса', reply_markup=markup)

    def text_command_admin_mode_get_questions_list_leave(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'ADMIN_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_admin_menu_markup()

        self.send_message(message.from_user.id, 'Вы вышли из списка вопросов', reply_markup=markup)

    """
        Конец команды вызова списка вопросов с компонентами
    """

    """
        # Конец команд админ-панели #
    """

    """
        Команда перехода в помощь (FAQ)
    """

    def text_command_help(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'HELP_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_help_menu_markup()

        self.send_message(message.from_user.id, 'Вы вошли в раздел поддержки', reply_markup=markup)

        logger = Logger('logs.db')
        logger.log('Enter help module', message.from_user.id, 'User have entered to the help module')

    """
        Конец перехода в помощь (FAQ)
    """

    """
        # Команды помощи #
    """

    def text_command_help_1(self, message):
        self.send_message(message.from_user.id, self.__messages_for_commands["help_commands"]["Как достигается анонимность?"])

    def text_command_help_2(self, message):
        self.send_message(message.from_user.id, self.__messages_for_commands["help_commands"]["Как сохранить анонимность?"])

    def text_command_help_3(self, message):
        self.send_message(message.from_user.id, self.__messages_for_commands["help_commands"]["Как отправлять информацию?"])

    def text_command_help_another(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'HELP_ANOTHER_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_help_another_menu_markup()

        self.send_message(message.from_user.id, 'Опишите вашу проблему', reply_markup=markup)

    def text_command_help_another_leave(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'HELP_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_help_menu_markup()

        self.send_message(message.from_user.id, f'Вы вышли из раздела других вопросов', reply_markup=markup)

    @staticmethod
    def add_question_to_database(message):
        questions = Database('questions.db')
        questions.execute(f"INSERT INTO questions (user_id, description) VALUES ({message.from_user.id}, '{message.text}')")

    def text_command_help_another_action(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'HELP_MENU' WHERE user_id = {message.from_user.id}")

        self.add_question_to_database(message=message)

        markup = self.make_help_menu_markup()

        self.send_message(message.from_user.id, 'Вашей проблемой займутся администраторы в ближайшее время', reply_markup=markup)

        database.execute(f"SELECT id FROM users WHERE user_id = {message.from_user.id}")
        user_hex_id = self.get_user_hex_id(database.get_result()[0][0])

        logger = Logger('logs.db')
        logger.log('Help request', message.from_user.id, f'User {user_hex_id} request for a help with question <{message.text}>')

    def text_command_help_leave(self, message):
        database = Database('user_database.db')
        database.execute(f"UPDATE users SET menu = 'MAIN_MENU' WHERE user_id = {message.from_user.id}")

        markup = self.make_main_menu_markup(user_id=message.from_user.id, admins_list=self.__admins)

        self.send_message(message.from_user.id, 'Вы вышли из раздела поддержки', reply_markup=markup)

        logger = Logger('logs.db')
        logger.log('Leave help module', message.from_user.id, f'User have left help module')

    """
        # Конец команд помощи #
    """

    """
        *** Конец функций для текстовых команд ***
    """

    """
        *** Функция обработки получаемых сообщений ***
    """

    def message_get(self, message):
        database = Database('user_database.db')
        database.execute('SELECT user_id FROM users')
        list_of_users_id = database.get_result()

        if not tuple([message.from_user.id]) in list_of_users_id:  # Проверка на наличие аккаунта
            self.command_start(message=message)
            return

        database.execute(f'SELECT ban_status FROM users WHERE user_id = {message.from_user.id}')
        ban_status = database.get_result()[0][0]
        if ban_status == 1:  # Проверка на забаненность аккаунта
            database.execute(f"UPDATE users SET menu = 'MAIN_MENU' WHERE user_id = {message.from_user.id}")

            markup = self.make_main_menu_markup(user_id=message.from_user.id, admins_list=self.__admins)

            self.send_message(message.from_user.id, 'Ваш аккаунт забанен!', reply_markup=markup)
            return

        database.execute(f'SELECT menu FROM users WHERE user_id = {message.from_user.id}')
        menu = database.get_result()[0][0]

        if message.text in self.__commands["main_commands"] and menu == 'MAIN_MENU':  # Обработка main_menu
            actions = {
                "Отправить работу": self.text_command_send_message,
                "Пожаловаться": self.text_command_report,
                "Админ-панель": self.text_command_admin_panel,
                "FAQ": self.text_command_help
            } if message.from_user.id in self.__admins else {
                "Отправить работу": self.text_command_send_message,
                "Пожаловаться": self.text_command_report,
                "FAQ": self.text_command_help
            }

            try:
                actions[message.text](message=message)
            except Exception as e:
                if str(type(e)) == "<class 'KeyError'>":
                    self.send_message(message.from_user.id, f'У вас нет доступа к данной команде!')

            return

        if menu == 'REPORT_MENU':  # Обработка report_menu
            self.text_command_report_action(message=message)
        elif menu == 'ADMIN_MENU':  # Обработка admin_menu
            actions = {
                "Забанить": self.text_command_admin_mode_ban,
                "Разбанить": self.text_command_admin_mode_unban,
                "Ответить на вопрос": self.text_command_admin_mode_answer_an_question,
                "Список вопросов": self.text_command_admin_mode_get_questions_list,
                "Список жалоб": self.text_command_admin_mode_get_reports_list,
                "Выйти": self.text_command_admin_mode_leave
            }
            if message.text in actions.keys():
                actions[message.text](message=message)
        elif menu == 'ADMIN_MODE_BAN_MENU':  # Обработка admin_mode_ban_menu
            self.text_command_admin_mode_ban_action(message=message)
        elif menu == 'ADMIN_MODE_UNBAN_MENU':  # Обработка admin_mode_unban_menu
            self.text_command_admin_mode_unban_action(message=message)
        elif menu == 'SEND_MESSAGE_MENU':  # Обработка send_message_menu
            if message.text == 'Отправить':  # Обработка кнопки Отправить
                self.text_command_send_message_action(message=message)
                return

            if message.text is not None:  # Добавление текста в рассылку
                self.add_text_to_data_storage(message=message)
            if message.photo is not None:  # Добавление фото в рассылку
                self.add_photo_to_data_storage(message=message)
            if message.caption is not None:  # Добавление описания фото в рассылку
                self.add_photos_text_to_data_storage(message=message)
        elif menu == 'HELP_MENU':
            actions = {
                "Как достигается анонимность?": self.text_command_help_1,
                "Как сохранить анонимность?": self.text_command_help_2,
                "Как отправлять информацию?": self.text_command_help_3,
                "Другой вопрос": self.text_command_help_another,
                "Выйти": self.text_command_help_leave
            }
            if message.text in actions.keys():
                actions[message.text](message=message)
        elif menu == 'HELP_ANOTHER_MENU':
            actions = {
                "Выйти": self.text_command_help_another_leave
            }
            if message.text in actions:
                actions[message.text](message=message)
            else:
                self.text_command_help_another_action(message=message)
        elif menu == 'ADMIN_MODE_ANSWER_AN_QUESTION_MENU':
            actions = {
                "Ввести UserID": self.text_command_admin_mode_answer_an_question_input_user_id,
                "Написать ответ": self.text_command_admin_mode_answer_an_question_input_answer,
                "Отправить": self.text_command_admin_mode_answer_an_question_send,
                "Выйти": self.text_command_admin_mode_answer_an_question_leave
            }
            if message.text in actions.keys():
                actions[message.text](message=message)
        elif menu == 'ADMIN_MODE_ANSWER_AN_QUESTION_INPUT_USER_ID_MENU':
            self.text_command_admin_mode_answer_an_question_input_user_id_action(message=message)
        elif menu == 'ADMIN_MODE_ANSWER_AN_QUESTION_INPUT_ANSWER_MENU':
            self.text_command_admin_mode_answer_an_question_input_answer_action(message=message)
        elif menu == 'ADMIN_MODE_REPORTS_LIST_MENU':
            actions = {
                "Отметить жалобу рассмотренной": self.text_command_admin_mode_get_reports_list_set_report_completed,
                "Выйти": self.text_command_admin_mode_get_reports_list_leave
            }
            if message.text in actions:
                actions[message.text](message=message)
        elif menu == 'ADMIN_MODE_REPORTS_LIST_SET_REPORT_COMPLETED_MENU':
            self.text_command_admin_mode_get_reports_list_set_report_completed_action(message=message)
        elif menu == 'ADMIN_MODE_QUESTIONS_LIST_MENU':
            actions = {
                "Отметить вопрос решенным": self.text_command_admin_mode_get_questions_list_set_question_completed,
                "Выйти": self.text_command_admin_mode_get_questions_list_leave
            }
            if message.text in actions:
                actions[message.text](message=message)
        elif menu == 'ADMIN_MODE_QUESTIONS_LIST_SET_QUESTION_COMPLETED_MENU':
            self.text_command_admin_mode_get_questions_list_set_question_completed_action(message=message)

    """
        *** Конец функции обработки получаемых сообщений ***
    """

    def run(self):
        self.register_message_handler(self.command_start, commands=['start'])
        self.register_message_handler(self.message_get, content_types=['text', 'photo'])

        self.polling(none_stop=True, interval=0)


while True:
    try:
        print('Bot started')
        bot = Bot()
    except Exception as exception:
        print('Bot crashed')
        print(exception)
