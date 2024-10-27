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
    

    @staticmethod
    def documentation_markup():
        markup = types.InlineKeyboardMarkup()
        # Кнопки для документации
        markup.add(types.InlineKeyboardButton(text="Остались вопросы по документации?", callback_data="ask_question"))
        markup.add(types.InlineKeyboardButton('Частые вопросы', callback_data='often_questions'))
        markup.add(types.InlineKeyboardButton(text="Назад", callback_data="start"))
        return markup
    
    
    @staticmethod
    def ask_question(markup):
        markup.add(types.InlineKeyboardButton(text="Другое", callback_data="topic_"))
        markup.add(types.InlineKeyboardButton(text="Назад", callback_data="start"))
        return markup

    @staticmethod
    def received_answer_markup():
        resolution_markup = types.InlineKeyboardMarkup()
        resolution_markup.add(types.InlineKeyboardButton(text="Оценить ответ", callback_data="question_resolved"))
        resolution_markup.add(types.InlineKeyboardButton(text="Задать другой вопрос", callback_data="ask_question"))
        return resolution_markup
    
    @staticmethod
    def get_quality_markup():
        quality_markup = types.InlineKeyboardMarkup()
        quality_markup.add(
            types.InlineKeyboardButton(text="1", callback_data="quality_1"),
            types.InlineKeyboardButton(text="2", callback_data="quality_2"),
            types.InlineKeyboardButton(text="3", callback_data="quality_3"),
            types.InlineKeyboardButton(text="4", callback_data="quality_4"),
            types.InlineKeyboardButton(text="5", callback_data="quality_5"),
        )
        return quality_markup
