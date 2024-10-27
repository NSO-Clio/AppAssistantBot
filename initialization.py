import json
from model import PromptGenerator, ClioYandex_GPT
import preproc_text
import config


class BotInitializer:
    def __init__(self):
        # Предобработка и загрузка данных документации
        self.chunks = preproc_text.preproc_docx_file(
            docx_file_path='documentation/data.docx',
            output_json='documentation/output.json',
            data_txt_path='documentation/data.txt'
        )

        # Загрузка структуры документации и часто задаваемых вопросов
        self.documentation_structure = self.load_json("documentation/output.json")
        self.questions_answers = self.load_json("documentation/data_quastions.json")

        # Инициализация генератора промптов и модели
        self.prompt_generator = PromptGenerator(chunks=self.chunks, qna=self.questions_answers)
        self.model = ClioYandex_GPT(
            oauth_token=config.YANDEX_PASSPORT_O_AUTH_TOKEN,
            modelUri=config.MODEL_URI
        )

    @staticmethod
    def load_json(filepath):
        """Вспомогательный метод для загрузки JSON-файла."""
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)