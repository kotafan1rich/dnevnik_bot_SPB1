import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def get_all_user_id(self):
        with self.connection:
            user_id = self.cursor.execute("SELECT `user_id` FROM `users`").fetchall()
        return [user[0] for user in user_id]

    def add_user(self, user_id):
        with self.connection:
            save = self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
            return save

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def set_login(self, user_id, login):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `login` = ? WHERE `user_id` = ?", (login, user_id,))

    def set_password(self, user_id, password):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `password` = ? WHERE `user_id` = ?", (password, user_id,))

    def set_group_id(self, user_id, group_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `group_id` = ? WHERE `user_id` = ?", (group_id, user_id,))

    def set_name(self, user_id, name):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `name` = ? WHERE `user_id` = ?", (name, user_id,))

    def set_education_id(self, user_id, education_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `education_id` = ? WHERE `user_id` = ?", (education_id, user_id,))


    def get_education_id(self, user_id):
        with self.connection:
            education_id = self.cursor.execute("SELECT `education_id` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return education_id[0]


    def get_name(self, user_id):
        with self.connection:
            name = self.cursor.execute("SELECT `name` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return name[0]


    def get_group_id(self, user_id):
        with self.connection:
            group_id = self.cursor.execute("SELECT `login`, `group_id` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return group_id[0]

    def get_login_and_password(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `login`, `password` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            login = result[0][0]
            password = result[0][1]
            return [login, password]
