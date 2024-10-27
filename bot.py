import telebot
from telebot import types
import logging
import json
from db import UserDB
import config
from model import PromptGenerator, ClioYandex_GPT
import preproc_text
# from keyboards import Keyboard


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Словари для хранения пользовательских вопросов и выбранных тем
user_questions = {}
selected_topic = {}

# Инициализация бота
bot = telebot.TeleBot(config.TG_BOT_TOKEN)

chunks = preproc_text.preproc_docx_file(
    docx_file_path='documentation/data.docx',
    output_json='documentation/output.json',
    data_txt_path='documentation/data.txt'
)

# Загрузка структуры документации из JSON
with open("documentation/output.json", "r", encoding="utf-8") as file:
    documentation_structure = json.load(file)

# Загрузка структуры частых вопросов из JSON
with open("documentation/data_quastions.json", "r", encoding="utf-8") as file:
    questions_answers = json.load(file)

prompt_gener = PromptGenerator(
    chunks=chunks,
    qna=questions_answers
)
model = ClioYandex_GPT(
    oauth_token=config.YANDEX_PASSPORT_O_AUTH_TOKEN,
    modelUri=config.MODEL_URI
)


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


# Функция для удаления предыдущего сообщения
def delete_previous_message(telegram_id, message_id):
    try:
        bot.delete_message(telegram_id, message_id)
    except Exception as e:
        logger.error(f"Error deleting message: {e}")


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    telegram_id = message.chat.id
    delete_previous_message(telegram_id, message.message_id)
    logger.info(f"User {telegram_id} started the bot.")
    bot.send_message(telegram_id, "Добро пожаловать в QA бот компании СИЛА.\nНажмите на кнопку ниже и ознакомьтесь с документацией приложения:", reply_markup=Keyboard.create_main_menu())


# Обработчик нажатия кнопки "Документация"
@bot.callback_query_handler(func=lambda call: call.data == 'doc')
def handle_documentation(call):
    telegram_id = call.message.chat.id
    delete_previous_message(telegram_id, call.message.message_id)
    markup = types.InlineKeyboardMarkup()

    # Кнопки для документации
    markup.add(types.InlineKeyboardButton(text="Остались вопросы по документации?", callback_data="ask_question"))
    markup.add(types.InlineKeyboardButton('Частые вопросы', callback_data='often_questions'))
    markup.add(types.InlineKeyboardButton(text="Назад", callback_data="start"))

    # Отправка документации
    with open("documentation/data.docx", "rb") as file:
        bot.send_document(telegram_id, file, caption="Ознакомьтесь с документацией.", reply_markup=markup)


# Обработчик для кнопки «Назад»
@bot.callback_query_handler(func=lambda call: call.data == 'start')
def go_back(call):
    telegram_id = call.message.chat.id
    delete_previous_message(telegram_id, call.message.message_id)
    markup = types.InlineKeyboardMarkup()
    for topic in documentation_structure.keys():
        markup.add(types.InlineKeyboardButton(text=topic, callback_data=f"question_{topic}"))

    bot.send_message(telegram_id, "Добро пожаловать в QA бот компании СИЛА.\nНажмите на кнопку ниже и ознакомьтесь с документацией приложения:", reply_markup=Keyboard.create_main_menu())


# Обработка часто задаваемых вопросов
@bot.callback_query_handler(func=lambda call: call.data == 'often_questions')
def handle_often_questions(call):
    telegram_id = call.message.chat.id
    delete_previous_message(telegram_id, call.message.message_id)
    markup = Keyboard.create_initial_questions_markup(questions_answers=questions_answers)
    bot.send_message(telegram_id, "Список частых вопросов:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "show_all_questions")
def show_all_questions(call):
    markup = Keyboard.create_all_questions_markup(questions_answers=questions_answers)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "show_initial_questions")
def show_initial_questions(call):
    markup = Keyboard.create_initial_questions_markup(questions_answers=questions_answers)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)


# Обработчик для выбора вопроса из часто задаваемых
@bot.callback_query_handler(func=lambda call: call.data.startswith("get_often_question_"))
def handle_question(call):
    try:
        question_index = int(call.data.split("get_often_question_")[1])
        answer = questions_answers[question_index][1]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="Назад", callback_data="show_initial_questions"))
        bot.send_message(call.message.chat.id, answer, reply_markup=markup)
    except (ValueError, IndexError) as e:
        print(f"Error processing question: {e}")
        bot.send_message(call.message.chat.id, "Произошла ошибка при обработке вашего запроса.")


# Обработка нажатия кнопки "Остались вопросы по документации?"
@bot.callback_query_handler(func=lambda call: call.data == 'ask_question')
def ask_question(call):
    telegram_id = call.message.chat.id
    delete_previous_message(telegram_id, call.message.message_id)

    # Создаем клавиатуру с темами из JSON
    markup = types.InlineKeyboardMarkup()
    for topic in documentation_structure.keys():
        markup.add(types.InlineKeyboardButton(text=topic, callback_data=f"topic_{topic}"))

    markup.add(types.InlineKeyboardButton(text="Другое", callback_data="topic_"))
    markup.add(types.InlineKeyboardButton(text="Назад", callback_data="start"))
    bot.send_message(telegram_id, "В какой части документации у вас возник вопрос?", reply_markup=markup)


# Обработка выбора темы вопроса
@bot.callback_query_handler(func=lambda call: call.data.startswith("topic_"))
def choose_topic(call):
    telegram_id = call.message.chat.id
    delete_previous_message(telegram_id, call.message.message_id)
    topic = call.data.split("_", 1)[1]  # Извлекаем тему (после "topic_")
    if topic:  # Если тема выбрана
        selected_topic[telegram_id] = topic  # Сохраняем выбранную тему
        bot.send_message(telegram_id, f"Вы выбрали вопрос с темой \"{topic}\".\nПожалуйста, введите ваш вопрос:")
    else:  # Если выбрана кнопка "Другое"
        selected_topic[telegram_id] = "Другое"
        bot.send_message(telegram_id, "Пожалуйста, введите ваш вопрос:")


# TODO
# Обработка текстовых сообщений, если пользователь находится в процессе задать вопрос
@bot.message_handler(func=lambda message: message.chat.id in selected_topic)
def handle_user_question(message):
    global model, prompt_gener

    telegram_id = message.chat.id
    question = message.text
    topic = selected_topic[telegram_id]  # Извлекаем выбранную тему

    # Логируем вопрос пользователя
    logger.info(f"User {telegram_id} asked a question on topic '{topic}': {question}")

    print(question)
    answer = model.question(question, prompt_gener)

    # Сохраняем вопрос в словаре
    user_questions[telegram_id] = {
        'question': question,
        'topic': topic,
        'answer': answer
    }

    # bot.send_message(telegram_id, "Здесь будет ответ на ваш вопрос.\nЕсли у вас ещё остались вопросы, присылайте, разберёмся во всём!")
    if '[img_data/imgs' in answer:
        image_paths, cleaned_text = preproc_text.extract_and_remove_image_paths(answer)
        with open(image_paths, 'rb') as img:
            bot.send_photo(message.chat.id, img, caption=cleaned_text)
    else:
        bot.send_message(telegram_id, answer)
    print(answer)
    # Кнопки "Вопрос решён" и "Задать другой вопрос"
    resolution_markup = types.InlineKeyboardMarkup()
    resolution_markup.add(
        types.InlineKeyboardButton(text="Оценить ответ", callback_data="question_resolved"),
        types.InlineKeyboardButton(text="Задать другой вопрос", callback_data="ask_question")
    )

    bot.send_message(telegram_id, "Вы можете нажать кнопку ниже, чтобы подтвердить, что ваш вопрос решён:", reply_markup=resolution_markup)


# Обработчик для кнопки "Вопрос решён"
@bot.callback_query_handler(func=lambda call_data: call_data.data == "question_resolved")
def question_resolved(call_data):
    telegram_id = call_data.message.chat.id
    delete_previous_message(telegram_id, call_data.message.message_id)

    # Кнопка для оценки
    quality_markup = types.InlineKeyboardMarkup()
    quality_markup.add(
        types.InlineKeyboardButton(text="1", callback_data="quality_1"),
        types.InlineKeyboardButton(text="2", callback_data="quality_2"),
        types.InlineKeyboardButton(text="3", callback_data="quality_3"),
        types.InlineKeyboardButton(text="4", callback_data="quality_4"),
        types.InlineKeyboardButton(text="5", callback_data="quality_5"),
    )

    bot.send_message(telegram_id, "Пожалуйста, оцените качество ответа на ваш вопрос:\nГде 1 - вы не однакратно пытались задать вопрос ассистенту, но он не дал нужного ответа, а 5 - бот верно ответил на ваш вопрос и помог вам разобраться в вашем вопросе.", reply_markup=quality_markup)


# Обработчик для оценки качества ответа
@bot.callback_query_handler(func=lambda call_data: call_data.data.startswith("quality_"))
def handle_quality_rating(call_data):
    global prompt_gener, model

    telegram_id = call_data.message.chat.id
    quality_rating = int(call_data.data.split("_")[1])  # Извлекаем рейтинг
    delete_previous_message(telegram_id, call_data.message.message_id)

    question = user_questions[telegram_id]['question']
    topic = user_questions[telegram_id]['topic']
    answer = user_questions[telegram_id]['answer']
    with UserDB('user_database.db') as db:
        db.add_question(telegram_id, question, answer, topic, quality_rating)
        print(db.get_all_data())
    if quality_rating >= 4:
        prompt_gener.record_qna(
            question=question,
            answer=answer
        )

    # Логируем оценку
    logger.info(f"User {telegram_id} rated the answer quality: {quality_rating}")
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(text="Назад", callback_data="doc"),
    )
    # Здесь можно добавить код для сохранения оценки в базу данных
    bot.send_message(telegram_id, f"Спасибо за вашу оценку! Вы поставили оценку: {quality_rating}. Если у вас есть еще вопросы, не стесняйтесь задавать их!", reply_markup=markup)

if __name__ == '__main__':
    bot.polling(none_stop=True)
