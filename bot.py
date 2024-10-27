import telebot
from telebot import types
import logging
from db import UserDB
import config
import preproc_text
from keyboards import Keyboard
from initialization import BotInitializer


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Словари для хранения пользовательских вопросов и выбранных тем
user_questions = {}
selected_topic = {}

# Инициализация бота
bot = telebot.TeleBot(config.TG_BOT_TOKEN)
initializer = BotInitializer()
documentation_structure = initializer.documentation_structure
questions_answers = initializer.questions_answers
prompt_gener = initializer.prompt_generator
model = initializer.model


# Удаление предыдущего сообщения
def delete_previous_message(telegram_id, message_id):
    try:
        bot.delete_message(telegram_id, message_id)
    except Exception as e:
        logger.error(f"Error deleting message: {e}")


# Команда /start — Приветственное сообщение
@bot.message_handler(commands=['start'])
def send_welcome(message):
    telegram_id = message.chat.id
    delete_previous_message(telegram_id, message.message_id)
    logger.info(f"User {telegram_id} started the bot.")
    bot.send_message(
        telegram_id,
        "Добро пожаловать в QA бот компании СИЛА.\nНажмите на кнопку ниже и ознакомьтесь с документацией приложения:",
        reply_markup=Keyboard.create_main_menu()
    )


# Кнопка "Документация" — отправка документации и кнопок навигации
@bot.callback_query_handler(func=lambda call: call.data == 'doc')
def handle_documentation(call):
    telegram_id = call.message.chat.id
    delete_previous_message(telegram_id, call.message.message_id)
    markup = Keyboard.documentation_markup()
    with open("documentation/data.docx", "rb") as file:
        bot.send_document(
            telegram_id, file, caption="Ознакомьтесь с документацией.", reply_markup=markup
        )


# Кнопка «Назад» — возврат в главное меню
@bot.callback_query_handler(func=lambda call: call.data == 'start')
def go_back(call):
    telegram_id = call.message.chat.id
    delete_previous_message(telegram_id, call.message.message_id)
    bot.send_message(
        telegram_id,
        "Добро пожаловать в QA бот компании СИЛА.\nНажмите на кнопку ниже и ознакомьтесь с документацией приложения:",
        reply_markup=Keyboard.create_main_menu()
    )


# Часто задаваемые вопросы — отображение часто задаваемых вопросов
@bot.callback_query_handler(func=lambda call: call.data == 'often_questions')
def handle_often_questions(call):
    telegram_id = call.message.chat.id
    delete_previous_message(telegram_id, call.message.message_id)
    markup = Keyboard.create_initial_questions_markup(questions_answers=questions_answers)
    bot.send_message(telegram_id, "Список частых вопросов:", reply_markup=markup)

# Показ всех вопросов из часто задаваемых
@bot.callback_query_handler(func=lambda call: call.data == "show_all_questions")
def show_all_questions(call):
    markup = Keyboard.create_all_questions_markup(questions_answers=questions_answers)
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )


# Возврат к начальному списку вопросов
@bot.callback_query_handler(func=lambda call: call.data == "show_initial_questions")
def show_initial_questions(call):
    markup = Keyboard.create_initial_questions_markup(questions_answers=questions_answers)
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )

# Выбор вопроса из часто задаваемых и отображение ответа
@bot.callback_query_handler(func=lambda call: call.data.startswith("get_often_question_"))
def handle_question(call):
    try:
        question_index = int(call.data.split("get_often_question_")[1])
        answer = questions_answers[question_index][1]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="Назад", callback_data="show_initial_questions"))
        if '[img_data/imgs' in answer:
            image_paths, cleaned_text = preproc_text.extract_and_remove_image_paths(answer)

            bot.send_message(call.message.chat.id, cleaned_text)
            
            # Отправляем группу медиа
            media = [telebot.types.InputMediaPhoto(open(photo[1:-1], 'rb')) for photo in image_paths]
            bot.send_media_group(call.message.chat.id, media)
        else:
            bot.send_message(call.message.chat.id, answer, reply_markup=markup)
    except (ValueError, IndexError) as e:
        logger.error(f"Error processing question: {e}")
        bot.send_message(call.message.chat.id, "Произошла ошибка при обработке вашего запроса.")


# Запрос на выбор темы вопроса
@bot.callback_query_handler(func=lambda call: call.data == 'ask_question')
def ask_question(call):
    telegram_id = call.message.chat.id
    delete_previous_message(telegram_id, call.message.message_id)
    markup = types.InlineKeyboardMarkup()
    for topic in documentation_structure.keys():
        markup.add(types.InlineKeyboardButton(text=topic, callback_data=f"topic_{topic}"))
    bot.send_message(
        telegram_id,
        "В какой части документации у вас возник вопрос?",
        reply_markup=Keyboard.ask_question(markup)
    )


# Выбор темы вопроса и ожидание текста от пользователя
@bot.callback_query_handler(func=lambda call: call.data.startswith("topic_"))
def choose_topic(call):
    telegram_id = call.message.chat.id
    delete_previous_message(telegram_id, call.message.message_id)
    topic = call.data.split("_", 1)[1]
    selected_topic[telegram_id] = topic if topic else "Другое"
    bot.send_message(
        telegram_id,
        f"Вы выбрали вопрос с темой \"{topic}\".\nПожалуйста, введите ваш вопрос:"
    )


# Обработка вопроса пользователя и генерация ответа
@bot.message_handler(func=lambda message: message.chat.id in selected_topic)
def handle_user_question(message):
    global model, prompt_gener

    telegram_id = message.chat.id
    question = message.text
    topic = selected_topic[telegram_id]
    logger.info(f"User {telegram_id} asked a question on topic '{topic}': {question}")
    
    answer = model.question(question, prompt_gener)
    user_questions[telegram_id] = {'question': question, 'topic': topic, 'answer': answer}
    
    if '[img_data/imgs' in answer:
        image_paths, cleaned_text = preproc_text.extract_and_remove_image_paths(answer)

        bot.send_message(message.chat.id, cleaned_text)

        # Отправляем группу медиа
        media = [telebot.types.InputMediaPhoto(open(photo[1:-1], 'rb')) for photo in image_paths]
        bot.send_media_group(message.chat.id, media)
    else:
        bot.send_message(telegram_id, answer)
    
    bot.send_message(
        telegram_id,
        "Вы можете нажать кнопку ниже, чтобы подтвердить, что ваш вопрос решён:",
        reply_markup=Keyboard.received_answer_markup()
    )


# Кнопка "Вопрос решён" — подтверждение от пользователя
@bot.callback_query_handler(func=lambda call_data: call_data.data == "question_resolved")
def question_resolved(call_data):
    telegram_id = call_data.message.chat.id
    delete_previous_message(telegram_id, call_data.message.message_id)
    bot.send_message(
        telegram_id,
        "Пожалуйста, оцените качество ответа на ваш вопрос:",
        reply_markup=Keyboard.get_quality_markup()
    )


# Оценка качества ответа и запись в базу данных
@bot.callback_query_handler(func=lambda call_data: call_data.data.startswith("quality_"))
def handle_quality_rating(call_data):
    global prompt_gener, model
    telegram_id = call_data.message.chat.id
    quality_rating = int(call_data.data.split("_")[1])
    delete_previous_message(telegram_id, call_data.message.message_id)
    
    question = user_questions[telegram_id]['question']
    topic = user_questions[telegram_id]['topic']
    answer = user_questions[telegram_id]['answer']
    
    with UserDB('user_database.db') as db:
        db.add_question(telegram_id, question, answer, topic, quality_rating)
    if quality_rating >= 4:
        prompt_gener.record_qna(question=question, answer=answer)
    
    logger.info(f"User {telegram_id} rated the answer quality: {quality_rating}")
    bot.send_message(
        telegram_id,
        f"Спасибо за вашу оценку! Вы поставили оценку: {quality_rating}. Если у вас есть еще вопросы, не стесняйтесь задавать их!",
        reply_markup=Keyboard.markup_back()
    )


if __name__ == '__main__':
    bot.polling(none_stop=True)
