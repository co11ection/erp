import telebot
import requests
from decouple import config


class RegistrationBot:
    def __init__(self):
        self.bot_token = config("TOKEN")
        self.api_base_url = config("API_BASE_URL")
        self.bot = telebot.TeleBot(self.bot_token)
        self.user_data = {}
        self.current_step = {}

        self.register_handlers()

    def start_bot(self):
        self.bot.polling()

    def register_handlers(self):
        @self.bot.message_handler(commands=["start"])
        def start(message):
            print(message.chat.id)
            self.bot.reply_to(
                message,
                "Привет! Я бот для регистрации. Отправь мне /register чтобы начать.",
            )

        @self.bot.message_handler(commands=["register"])
        def register(message):
            user_id = message.chat.id
            self.current_step[user_id] = "last_name"
            self.user_data[user_id] = {"step": "last_name"}
            self.bot.send_message(user_id, "Пожалуйста, введите вашу фамилию")

        @self.bot.message_handler(
            func=lambda message: self.current_step.get(message.chat.id) == "last_name"
        )
        def process_last_name(message):
            user_id = message.chat.id
            self.current_step[user_id] = "first_name"
            self.user_data[user_id]["last_name"] = message.text
            self.bot.send_message(user_id, "Теперь введите ваше имя")

        @self.bot.message_handler(
            func=lambda message: self.current_step.get(message.chat.id) == "first_name"
        )
        def process_first_name(message):
            user_id = message.chat.id
            self.current_step[user_id] = "middle_name"
            self.user_data[user_id]["first_name"] = message.text
            self.bot.send_message(user_id, "Теперь введите ваше отчество")

        @self.bot.message_handler(
            func=lambda message: self.current_step.get(message.chat.id) == "middle_name"
        )
        def process_fullname(message):
            user_id = message.chat.id
            self.user_data[user_id]["middle_name"] = message.text
            self.current_step[user_id] = "date_of_birthd"
            self.bot.send_message(user_id, "Теперь введите ваш дату рождения в формате: гггг-мм-дд")
            
        @self.bot.message_handler(
            func=lambda message: self.current_step.get(message.chat.id) == "date_of_birthd"
        )
        def process_date_of_birthd(message):
            user_id = message.chat.id
            self.user_data[user_id]["date_of_birthd"] = message.text
            self.current_step[user_id] = "phone_number"
            self.bot.send_message(user_id, "Теперь введите ваш номер телефона.")



        @self.bot.message_handler(
            func=lambda message: self.current_step.get(message.chat.id)
            == "phone_number"
        )
        def process_phone(message):
            user_id = message.chat.id
            self.user_data[user_id]["phone_number"] = message.text
            self.current_step[user_id] = "email"
            self.bot.send_message(
                user_id, "Пожалуйста, введите ваш адрес электронной почты."
            )

        @self.bot.message_handler(
            func=lambda message: self.current_step.get(message.chat.id) == "email"
        )
        def process_email(message):
            user_id = message.chat.id
            self.user_data[user_id]["email"] = message.text
            self.current_step[user_id] = "password"
            self.bot.send_message(
                user_id,
                "Пожалуйста, введите ваш пароль. Он должен состоять как минимум из 8 символов.",
            )

        @self.bot.message_handler(
            func=lambda message: self.current_step.get(message.chat.id) == "password"
            
        )
        def process_password(message):
            user_id = message.chat.id
            password = message.text

            if not self.validate_password(password):
                self.send_password_error_message(user_id)
                self.current_step[user_id] = "password"
            else:
                self.user_data[user_id]["password"] = password

                data = {
                    "first_name": self.user_data[user_id]["first_name"],
                    "middle_name": self.user_data[user_id]["middle_name"],
                    "last_name": self.user_data[user_id]["last_name"],
                    "date_of_birth": self.user_data[user_id]["date_of_birthd"],
                    "phone_number": self.user_data[user_id]["phone_number"],
                    "email": self.user_data[user_id]["email"],
                    "password": self.user_data[user_id]["password"],
                    "telegram": message.from_user,
                    "telegram_username": message.chat.username,
                    "telegram_id": message.chat.id
                }

                response = requests.post(
                    f"{self.api_base_url}/api/account/register/", data=data
                )
                print(response)
                print('!!!!!!')
                self.validate_email(user_id, response)

    @staticmethod
    def validate_password(password: str) -> bool:
        forbidden_symbols = "!@#$%^&*()_+{|}[]\/.,;''\"-=`~:<>?"
        return len(password) >= 8 and all(
            char not in forbidden_symbols for char in password
        )

    @staticmethod
    def validate_fullname(full_name: str) -> bool:
        return 3 <= len(full_name.split(" ")) < 4

    def send_password_error_message(self, user_id):
        self.bot.send_message(
            user_id,
            "Пожалуйста, снова введите ваш пароль. Он должен состоять как минимум из 8 символов.",
        )
        self.bot.send_message(
            user_id, "Также он должен содержать только буквы и цифры."
        )

    def validate_email(self, user_id, response):
        if response.status_code == 201:
            self.bot.send_message(
                user_id,
                "Регистрация успешно завершена, проверьте свою почту "
                "(включая папку со спамом)! /start",
            )
        elif response.status_code == 400:
            try:
                email_error = response.json().get("email")[0]
                print(email_error)
                if email_error == "Пользователь with this Электронная почта already exists.":
                    self.bot.send_message(
                        user_id, "Email с таким пользователем уже существует"
                    )
                    self.bot.send_message(
                        user_id,
                        "Попробуйте перерегистрироваться с другого аккаунта /register",
                    )
                elif email_error == "Enter a valid email address.":
                    self.bot.send_message(
                        user_id, "Введите правильный email. Пример: example@example.com"
                    )
                    self.bot.send_message(
                        user_id,
                        "Попробуйте перерегистрироваться с другого аккаунта /register",
                    )
                else:
                    self.bot.send_message(
                        user_id,
                        "Что-то пошло не так при регистрации. Попробуйте позже.",
                    )
            except:
                self.bot.send_message(
                    user_id, "Что-то пошло не так при регистрации. Попробуйте позже."
                )


if __name__ == "__main__":
    registration_bot = RegistrationBot()
    registration_bot.start_bot()
