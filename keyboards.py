from telebot import types
import json
import logging
from db import UserDB


# Настройка логирования для отслеживания информации и ошибок
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Keyboard:
    @staticmethod
    def create_main_menu():
        # Создание главного меню с кнопкой "Документация"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Документация', callback_data='doc'))
        return markup

    @staticmethod
    def markup_back():
        # Создание кнопки "Назад" для возврата к предыдущему меню
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Назад', callback_data='doc'))
        return markup

    @staticmethod
    def create_initial_questions_markup(questions_answers):
        # Создание разметки для первых 5 вопросов из списка вопросов и ответов
        markup = types.InlineKeyboardMarkup()
        for index, item in enumerate(questions_answers[:5]):  # Выводим первые 5 вопросов
            question = item[0]
            callback_data = f"get_often_question_{index}"  # Формирование уникального идентификатора для каждого вопроса
            markup.add(types.InlineKeyboardButton(text=question, callback_data=callback_data))
        # Добавление кнопки для раскрытия всех вопросов и кнопки "Назад"
        markup.add(types.InlineKeyboardButton(text="Раскрыть все", callback_data="show_all_questions"))
        markup.add(types.InlineKeyboardButton(text="Назад", callback_data="doc"))
        return markup

    @staticmethod
    def create_all_questions_markup(questions_answers):
        # Создание разметки для отображения всех вопросов из списка вопросов и ответов
        markup = types.InlineKeyboardMarkup()
        for index, item in enumerate(questions_answers):
            question = item[0]
            callback_data = f"get_often_question_{index}"  # Формирование уникального идентификатора для каждого вопроса
            markup.add(types.InlineKeyboardButton(text=question, callback_data=callback_data))
        # Добавление кнопки "Назад" для возврата к начальному списку вопросов
        markup.add(types.InlineKeyboardButton(text="Назад", callback_data="show_initial_questions"))
        return markup
    
    @staticmethod
    def documentation_markup():
        # Создание разметки с кнопками для работы с документацией
        markup = types.InlineKeyboardMarkup()
        # Кнопки для взаимодействия с пользователем по вопросам документации
        markup.add(types.InlineKeyboardButton(text="Остались вопросы по документации?", callback_data="ask_question"))
        markup.add(types.InlineKeyboardButton('Частые вопросы', callback_data='often_questions'))
        markup.add(types.InlineKeyboardButton(text="Назад", callback_data="start"))
        return markup
    
    @staticmethod
    def ask_question(markup):
        # Добавление кнопок для выбора темы вопроса и возврата к началу
        markup.add(types.InlineKeyboardButton(text="Другое", callback_data="topic_"))
        markup.add(types.InlineKeyboardButton(text="Назад", callback_data="start"))
        return markup

    @staticmethod
    def received_answer_markup():
        # Разметка для отображения после получения ответа на вопрос
        resolution_markup = types.InlineKeyboardMarkup()
        resolution_markup.add(types.InlineKeyboardButton(text="Оценить ответ", callback_data="question_resolved"))
        resolution_markup.add(types.InlineKeyboardButton(text="Задать другой вопрос", callback_data="ask_question"))
        return resolution_markup
    
    @staticmethod
    def get_quality_markup():
        # Разметка для оценки качества ответа от 1 до 5
        quality_markup = types.InlineKeyboardMarkup()
        quality_markup.add(
            types.InlineKeyboardButton(text="1", callback_data="quality_1"),
            types.InlineKeyboardButton(text="2", callback_data="quality_2"),
            types.InlineKeyboardButton(text="3", callback_data="quality_3"),
            types.InlineKeyboardButton(text="4", callback_data="quality_4"),
            types.InlineKeyboardButton(text="5", callback_data="quality_5"),
        )
        return quality_markup