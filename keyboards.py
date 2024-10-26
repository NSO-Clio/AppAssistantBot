from telebot import types
import json
import logging
from db import UserDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Keyboard:
    @staticmethod
    def create_main_menu():
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Документация', callback_data='doc'))
        return markup

    @staticmethod
    def markup_back():
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Назад', callback_data='doc'))
        return markup

    @staticmethod
    def create_initial_questions_markup(questions_answers):
        markup = types.InlineKeyboardMarkup()
        for index, item in enumerate(questions_answers[:5]):  # Выводим первые 5 вопросов
            question = item[0]
            callback_data = f"get_often_question_{index}"
            markup.add(types.InlineKeyboardButton(text=question, callback_data=callback_data))
        markup.add(types.InlineKeyboardButton(text="Раскрыть все", callback_data="show_all_questions"))
        markup.add(types.InlineKeyboardButton(text="Назад", callback_data="doc"))
        return markup

    @staticmethod
    def create_all_questions_markup(questions_answers):
        markup = types.InlineKeyboardMarkup()
        for index, item in enumerate(questions_answers):
            question = item[0]
            callback_data = f"get_often_question_{index}"
            markup.add(types.InlineKeyboardButton(text=question, callback_data=callback_data))
        markup.add(types.InlineKeyboardButton(text="Назад", callback_data="show_initial_questions"))
        return markup

# class Keyboards:
#     def __init__(self):
#         """Загрузка структуры документации из JSON (если требуется для генерации кнопок"""
#         with open("documentation/output.json", "r", encoding="utf-8") as file:
#             self.documentation_structure = json.load(file)
#
#         """ Загрузка частых вопросов из JSON (если требуется для генерации кнопок) """
#         with open("documentation/data_quastions.json", "r", encoding="utf-8") as file:
#             self.questions_answers = json.load(file)
#
#     def main_menu(self):
#         """Создание кнопки главного меню"""
#         markup = types.InlineKeyboardMarkup()
#         markup.add(types.InlineKeyboardButton('Документация', callback_data='doc'))
#         return markup
#
#     def back_button(self, callback_data='doc'):
#         """Создание кнопки 'Назад'"""
#         markup = types.InlineKeyboardMarkup()
#         markup.add(types.InlineKeyboardButton('Назад', callback_data=callback_data))
#         return markup
#
#     def initial_questions_markup(self):
#         """Клавиатура с первыми 5 частыми вопросами и кнопкой 'Раскрыть все'"""
#         markup = types.InlineKeyboardMarkup()
#         for index, item in enumerate(self.questions_answers[:5]):
#             question = item[0]
#             callback_data = f"get_often_question_{index}"
#             markup.add(types.InlineKeyboardButton(text=question, callback_data=callback_data))
#         markup.add(types.InlineKeyboardButton(text="Раскрыть все", callback_data="show_all_questions"))
#         markup.add(types.InlineKeyboardButton(text="Назад", callback_data="doc"))
#         return markup
#
#     def all_questions_markup(self):
#         """Клавиатура с полным списком частых вопросов"""
#         markup = types.InlineKeyboardMarkup()
#         for index, item in enumerate(self.questions_answers):
#             question = item[0]
#             callback_data = f"get_often_question_{index}"
#             markup.add(types.InlineKeyboardButton(text=question, callback_data=callback_data))
#         markup.add(types.InlineKeyboardButton(text="Назад", callback_data="show_initial_questions"))
#         return markup
#
#     def documentation_buttons(self):
#         """Кнопки для документации и частых вопросов"""
#         markup = types.InlineKeyboardMarkup()
#         markup.add(types.InlineKeyboardButton(text="Остались вопросы по документации?", callback_data="ask_question"))
#         markup.add(types.InlineKeyboardButton(text="Частые вопросы", callback_data="often_questions"))
#         markup.add(types.InlineKeyboardButton(text="Назад", callback_data="start"))
#         return markup
#
#     def load_documentation_structure(file_path):
#         with open(file_path, 'r', encoding='utf-8') as file:
#             return json.load(file)
#
#     def topic_buttons(self):
#         """Кнопки с темами из документации"""
#         markup = types.InlineKeyboardMarkup()
#         for topic in self.documentation_structure.keys():
#             markup.add(types.InlineKeyboardButton(text=topic, callback_data=f"topic_{topic}"))
#         markup.add(types.InlineKeyboardButton(text="Другое", callback_data="topic_"))
#         markup.add(types.InlineKeyboardButton(text="Назад", callback_data="start"))
#         return markup
#
#     def resolution_markup(self):
#         """Клавиатура для подтверждения, что вопрос решён"""
#         markup = types.InlineKeyboardMarkup()
#         markup.add(
#             types.InlineKeyboardButton(text="Оценить ответ", callback_data="question_resolved"),
#             types.InlineKeyboardButton(text="Задать другой вопрос", callback_data="ask_question")
#         )
#         return markup
#
#     def quality_markup(self):
#         """Клавиатура для оценки качества ответа"""
#         markup = types.InlineKeyboardMarkup()
#         for i in range(1, 6):
#             markup.add(types.InlineKeyboardButton(text=str(i), callback_data=f"quality_{i}"))
#         return markup
#
#     def topics_keyboard(self):
#         # Создаем клавиатуру с темами из JSON
#         markup = types.InlineKeyboardMarkup()
#         for topic in self.documentation_structure.keys():
#             markup.add(types.InlineKeyboardButton(text=topic, callback_data=f"topic_{topic}"))
#         markup.add(types.InlineKeyboardButton(text="Другое", callback_data="topic_"))
#         markup.add(types.InlineKeyboardButton(text="Назад", callback_data="start"))
#         return markup