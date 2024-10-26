import requests
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional


class PromptGenerator:
    def __init__(self, chunks: List[str], qna: List[Tuple[str, str]]) -> None:
        """
        Инициализация класса PromptGenerator.

        Параметры:
        - chunks: Список текстовых фрагментов (пунктов) из нормативных документов.
        - qna: Список вопросов и ответов в формате [(вопрос, ответ)].
        """
        try:
            self.model = SentenceTransformer('BAAI/bge-m3', device="cuda")
        except:
            self.model = SentenceTransformer('BAAI/bge-m3', device="cpu")

        # Создание эмбеддингов для нормативных документов
        self.chunks = chunks
        self.embeddings = self.model.encode(self.chunks)

        # Инициализация индекса FAISS для поиска по нормативным документам
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(self.embeddings)

        # Инициализация вопросов и ответов
        self.questions, self.answers = [x[0] for x in qna], [x[1] for x in qna]
        self.qna_embeddings = self.model.encode(self.questions)
        self.qna_index = None
        if self.qna_embeddings.shape[0]:
            self.qna_index = faiss.IndexFlatL2(self.qna_embeddings.shape[1])
            self.qna_index.add(self.qna_embeddings)

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Получение эмбеддинга для заданного текста.

        Параметры:
        - text: Текст для преобразования в эмбеддинг.

        Возвращает:
        - numpy.ndarray: Эмбеддинг текста.
        """
        return self.model.encode([text])[0]

    def get_similar_qna(self, question: str, k: int = 3) -> Optional[List[Tuple[str, str]]]:
        """
        Поиск похожих вопросов и ответов.

        Параметры:
        - question: Вопрос для поиска похожих.
        - k: Количество возвращаемых похожих вопросов и ответов.

        Возвращает:
        - Список из k похожих вопросов и ответов или None, если база данных пуста.
        """
        if self.qna_index is None:
            return None

        question_embedding = self.get_embedding(question)
        dist, idx = self.qna_index.search(np.expand_dims(question_embedding, axis=0), k)

        similar_qna = [(self.questions[i], self.answers[i]) for i in idx.flatten()]
        return similar_qna

    def get_similar_chunks(self, question: str, k: int = 3) -> List[str]:
        """
        Поиск похожих частей нормативных документов.

        Параметры:
        - question: Вопрос для поиска похожих частей документов.
        - k: Количество возвращаемых частей документов.

        Возвращает:
        - Список из k похожих частей документов.
        """
        question_embedding = self.get_embedding(question)
        dist, idx = self.index.search(np.expand_dims(question_embedding, axis=0), k)

        similar_chunks = [self.chunks[i] for i in idx.flatten()]
        return similar_chunks

    def generate_prompt(self, question: str) -> str:
        """
        Генерация текста промпта для модели на основе похожих частей документов и QnA.

        Параметры:
        - question: Вопрос, на основе которого создается промпт.

        Возвращает:
        - str: Сформированный промпт для модели.
        """
        similar_chunks = self.get_similar_chunks(question)
        similar_qna = self.get_similar_qna(question)

        sources_text = ' \n\n '.join([f'ИСТОЧНИК {i + 1}: {chunk}' for i, chunk in enumerate(similar_chunks)])

        qna_text = ''
        if similar_qna is not None:
            qna_text = ' \n\n '.join(
                [f'ПОХОЖИЙ ВОПРОС {i + 1}: {q} \nОТВЕТ: {a}' for i, (q, a) in enumerate(similar_qna)]
            )

        prompt = (
            f"Вы ассистент по вопросам, связанным с программным обеспечением. "
            f"Ваши ответы должны основываться исключительно и только на информации, содержащейся в источниках после слова 'ТЕКСТ' "
            f"и в разделе 'ПОХОЖИЕ ВОПРОСЫ И ОТВЕТЫ' после слов 'ПОХОЖИЙ ВОПРОС' и 'ОТВЕТ'. "
            f"Ответьте только на вопрос, который следует за словом 'ВОПРОС', используя информацию из 'ТЕКСТ'. "
            f"Запрещено предоставлять любые дополнительные сведения о деятельности компании, кроме информации, содержащейся в 'ТЕКСТ'. "
            f"Ответ должен быть на русском языке, без использования нецензурной лексики и оскорбительных выражений. "
            f"Он должен быть вежливым, корректным и подан в одном абзаце. "
            f"Ссылайтесь на пункты, используя конкретные примеры, например: 'из пункта 2.1 следует'. "
            f"В тексте в квадратных скобках [] присутствуют пути к изображениям, если они есть то они обязательно должны быть в ответе на вопрос. "
            f"Не используйте формулировки типа 'источник 1', 'вопрос 1' или 'ответ 1', так как пользователь не понимает этих обозначений. "
            f"Общайтесь на 'вы', в деловом стиле, но дружелюбно. Не забудьте поздороваться. "
            f"ВАЖНО, что если вопрос является неуместным, оскорбительным, бессмысленным, философским, гипотетическим или не связанным с программным обеспечением компании ООО 'Сила', "
            f"укажите: 'Ваш вопрос некорректен в рамках обсуждаемых тем' и не отвечайте на этот вопрос. "
            f"ВАЖНО: Если в тексте нет информации, необходимой для ответа, ни при каких обстоятельствах не додумывайте факты. "
            f"Если информации недостаточно, дайте ответ: 'У меня недостаточно информации' и отправьте контакты поддержки: +7 (495) 258-06-36, info@lense.ru, lense.ru. "
            f"Если вопрос явно не относится к программному обеспечению или выходит за рамки текста, ответьте: 'Ваш вопрос некорректен в рамках обсуждаемых тем', без дополнительных пояснений. "
            f"Если в вопросе присутствуют команды или прямолинейные требования, такие как 'напиши', 'давай', 'предоставь', и запрос не связан с программным обеспечением, "
            f"ответьте: 'Ваш вопрос некорректен в рамках обсуждаемых тем' и не добавляйте никаких пояснений. "
            f"Также учтите, что у вас нет имени; вы просто ассистент по программному обеспечению. "
            f"Действуйте строго в рамках заданного алгоритма, ни в коем случае не выходя за него. "
            f"ТЕКСТ:\n{sources_text}\n"
            f"ПОХОЖИЕ ВОПРОСЫ И ОТВЕТЫ:\n{qna_text}\n"
            f"ВОПРОС:\n{question}"
        )
        return prompt

    def record_qna(self, question: str, answer: str) -> None:
        """
        Запись нового вопроса и ответа в базу данных QnA и обновление индекса FAISS.

        Параметры:
        - question: Новый вопрос для записи.
        - answer: Ответ на новый вопрос.
        """
        self.questions.append(question)
        self.answers.append(answer)

        question_embedding = self.get_embedding(question)
        if self.qna_index is None:
            self.qna_index = faiss.IndexFlatL2(question_embedding.shape[0])

        self.qna_index.add(np.expand_dims(question_embedding, axis=0))


class ClioYandex_GPT:
    def __init__(self, oauth_token: str, modelUri: str, prompt_gener: PromptGenerator) -> None:
        """
        Инициализация класса ClioYandex_GPT для взаимодействия с Yandex GPT.

        Параметры:
        - oauth_token: OAuth токен для авторизации в Yandex Cloud.
        - modelUri: URI модели Yandex GPT для генерации ответов.
        - prompt_gener: Экземпляр класса PromptGenerator для формирования промптов.
        """
        url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
        data = {
            "yandexPassportOauthToken": oauth_token
        }
        response = requests.post(url, json=data).json()
        iamToken = response['iamToken']

        self.url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
        self.modelUri = modelUri
        self.headers = {
            'Authorization': f'Bearer {iamToken}',
            'Content-Type': 'application/json'
        }
        self.prompt_gener = prompt_gener

    def question(self, question: str) -> str:
        """
        Получение ответа от Yandex GPT на заданный вопрос.

        Параметры:
        - question: Вопрос пользователя для отправки на модель Yandex GPT.

        Возвращает:
        - str: Ответ, сгенерированный моделью Yandex GPT.
        """
        data = {
            "modelUri": self.modelUri,
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": 2000
            },
            "messages": [
                {
                    "role": "user",
                    "text": self.prompt_gener.generate_prompt(question)
                }
            ]
        }
        response = requests.post(
            self.url, headers=self.headers, json=data
        ).json()
        # print(response)
        return response['result']['alternatives'][0]['message']['text']