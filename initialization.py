import json
from model import PromptGenerator, ClioYandex_GPT
import preproc_text
import config


class BotInitializer:
    def __init__(self):
        # Предобработка и загрузка данных документации
        self.chunks = preproc_text.preproc_docx_file(
            docx_file_path='documentation/data.docx',  # Путь к файлу документации в формате DOCX
            output_json='documentation/output.json',    # Путь для сохранения предобработанных данных в формате JSON
            data_txt_path='documentation/data.txt'      # Путь для сохранения текста документации в формате TXT
        )

        # Загрузка структуры документации и часто задаваемых вопросов из JSON-файлов
        self.documentation_structure = self.load_json("documentation/output.json")  # Загружаем предобработанные данные документации
        self.questions_answers = self.load_json("documentation/data_quastions.json")  # Загружаем данные о часто задаваемых вопросах

        # Инициализация генератора промптов с предобработанными данными и вопросами/ответами
        self.prompt_generator = PromptGenerator(chunks=self.chunks, qna=self.questions_answers)
        
        # Инициализация модели ClioYandex_GPT с использованием токена OAuth и URI модели из конфигурации
        self.model = ClioYandex_GPT(
            oauth_token=config.YANDEX_PASSPORT_O_AUTH_TOKEN,  # Токен для авторизации в Яндексе
            modelUri=config.MODEL_URI  # URI для доступа к модели
        )

    @staticmethod
    def load_json(filepath):
        """Вспомогательный метод для загрузки JSON-файла."""
        with open(filepath, "r", encoding="utf-8") as file:  # Открытие файла с указанием кодировки UTF-8
            return json.load(file)  # Загрузка и возврат содержимого файла в виде словаря Python