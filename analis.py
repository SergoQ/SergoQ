import sqlite3
import os
from telethon.sync import TelegramClient
from telethon import utils
import pytesseract
from PIL import Image

class BotHandler:
    def __init__(self, api_id, api_hash, phone_number, session_name, bot_links):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.session_name = session_name
        self.bot_links = bot_links

        self.connect()

    def connect(self):
        # создаем клиент 
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        self.client.connect()

        #  пользователь не авторизован? отправляем запрос на код подтверждения
        if not self.client.is_user_authorized():
            self.client.send_code_request(self.phone_number)
            try:
                # двуэтапна
                self.client.sign_in(self.phone_number, input('Введите код из смс: '))
            except Exception as e:
                if "Two-steps verification is enabled" in str(e):
                    password = input('Введите пароль (если включена двухэтапная аутентификация): ')
                    self.client.sign_in(password=password)

    async def process_message(self, event):
        if event.message.text:
            for bot_link in self.bot_links:
                if bot_link in event.message.text:
                    bot_id = utils.resolve_id(bot_link)
                    if not self.is_bot_registered(bot_id):
                        self.register_bot(bot_id)

                    bot_method = self.get_bot_method(bot_id)

                    if "solve_math_captcha" in event.message.text and bot_method == 'math':
                        math_captcha_solution = self.solve_math_captcha(event.message.text)
                        await event.reply(math_captcha_solution)

                    if "solve_word_captcha" in event.message.text and bot_method == 'word':
                        word_captcha_solution = self.solve_word_captcha(event.message.text)
                        await event.reply(word_captcha_solution)

                    if "solve_ocr_captcha" in event.message.text and bot_method == 'ocr':
                        ocr_captcha_solution = self.solve_ocr_captcha(event.message.media)
                        await event.reply(ocr_captcha_solution)

    def solve_math_captcha(self, captcha_text):
        try:
            expression = captcha_text.split('(', 1)[1].split(')')[0]
            result = eval(expression)
            return f"Решение математической капчи: {result}"
        except Exception as e:
            return f"Ошибка при решении математической капчи: {e}"

    def solve_word_captcha(self, captcha_text):
        target_word = 'captcha'
        if target_word in captcha_text:
            return f"Решение капчи с поиском слова: {target_word} найдено"
        else:
            return f"Решение капчи с поиском слова: {target_word} не найдено"

    def solve_ocr_captcha(self, captcha_media):
        image_path = "captcha_image.png"
        with open(image_path, 'wb') as f:
            f.write(captcha_media.document.bytes)
        ocr_text = pytesseract.image_to_string(Image.open(image_path))
        
        # удаляем файл после использования
        os.remove(image_path)
        
        return f"OCR распознал текст: {ocr_text}"

    def is_bot_registered(self, bot_id):
         #замени Бд
        conn = sqlite3.connect('C:\\Users\\Сергей\\Desktop\\Тестовое 2\\bots.db')
        cursor = conn.cursor()

        
        cursor.execute('SELECT bot_id FROM registered_bots WHERE bot_id = ?;', (bot_id,))
        existing_bot = cursor.fetchone()

        
        conn.close()

        return existing_bot is not None

    def register_bot(self, bot_id):
         #замени Бд
        conn = sqlite3.connect('C:\\Users\\Сергей\\Desktop\\Тестовое 2\\bots.db')
        cursor = conn.cursor()

        # Создаем таблицу, если она еще не существует
        cursor.execute('CREATE TABLE IF NOT EXISTS registered_bots (bot_id INTEGER PRIMARY KEY, method TEXT);')

        # Проверочка ботика по id в бд
        cursor.execute('SELECT bot_id, method FROM registered_bots WHERE bot_id = ?;', (bot_id,))
        existing_bot = cursor.fetchone()

        # если бота нет в бд добавляем его
        if not existing_bot:
            # добавляем бота с методом  (math)
            cursor.execute('INSERT INTO registered_bots (bot_id, method) VALUES (?, "math");', (bot_id,))
            conn.commit()

        
        conn.close()

    def get_bot_method(self, bot_id):
         #замени Бд
        conn = sqlite3.connect('C:\\Users\\Сергей\\Desktop\\Тестовое 2\\bots.db')
        cursor = conn.cursor()

        # получаем метод для бота из базы данных
        cursor.execute('SELECT method FROM registered_bots WHERE bot_id = ?;', (bot_id,))
        method = cursor.fetchone()

        
        conn.close()

        # если метод не указан, возвращаем "math" 
        return method[0] if method else "math"

    def set_bot_method(self, bot_id, method):
        #замени Бд
        conn = sqlite3.connect('C:\\Users\\Сергей\\Desktop\\Тестовое 2\\bots.db')
        cursor = conn.cursor()

        # Обновляем метод для бота в базе данных
        cursor.execute('UPDATE registered_bots SET method = ? WHERE bot_id = ?;', (method, bot_id))
        conn.commit()

       
        conn.close()

    def run(self):
        self.client.add_event_handler(self.process_message)
        self.client.start()


api_id = ''
api_hash = ''
phone_number = ''
session_name = ''
bot_links = ['https://t.me/pogromista', 'https://t.me/LampMining']

bot_handler = BotHandler(api_id, api_hash, phone_number, session_name, bot_links)
bot_handler.run()
