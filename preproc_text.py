import docx2txt
import re
import json
import os
from typing import Dict, List, Union, Tuple


def extract_and_remove_image_paths(text: str) -> Tuple[List[str], str]:
    """
    Извлекает пути изображений формата [img_data/imgsX.jpg] из текста и удаляет их.

    :param text: Исходный текст
    :return: Кортеж из списка путей изображений и текста без этих путей
    """
    # Регулярное выражение для поиска путей изображений
    pattern = r'\[img_data/imgs\d+\.jpg\]'
    
    # Находим все пути изображений
    image_paths = re.findall(pattern, text)
    
    # Удаляем найденные пути из текста
    cleaned_text = re.sub(pattern, '', text)
    
    return image_paths, cleaned_text


def manage_file(file_path: str, file_type: str = 'txt') -> None:
    """
    Проверяет наличие файла. Если файл существует, очищает его. 
    Если нет, создает новый файл.

    :param file_path: Путь к файлу
    :param file_type: Тип файла ('txt' или 'json')
    :raises ValueError: Если file_type не является 'txt' или 'json'
    """
    if file_type not in ['txt', 'json']:
        raise ValueError("file_type должен быть 'txt' или 'json'.")

    # Очищаем или создаем файл в зависимости от его существования
    with open(file_path, 'w', encoding='utf-8') as file:
        if file_type == 'json':
            json.dump({}, file)  # Записываем пустой объект для JSON


def split_long_texts(input_dict: Dict[str, Union[str, List[str]]], max_length: int = 1024) -> Dict[str, Union[str, List[str]]]:
    """
    Проходит по словарю и делит длинные тексты на списки из частей по количеству слов.

    :param input_dict: Исходный словарь с текстами
    :param max_length: Максимальное количество слов в одной части
    :return: Обновленный словарь с разделенными текстами
    """
    output_dict = {}

    for key, value in input_dict.items():
        if isinstance(value, str) and len(value.split()) > max_length:
            # Разделяем текст на слова и разбиваем на части
            words = value.split()
            parts = [" ".join(words[i:i + max_length]) for i in range(0, len(words), max_length)]
            output_dict[key] = parts
        else:
            # Если текст не длинный, оставляем его как есть
            output_dict[key] = value

    return output_dict


def preproc_docx_file(docx_file_path: str, output_json: str, data_txt_path: str) -> List[str]:
    """
    Обрабатывает DOCX файл и извлекает текст, разделяя его на части.

    :param docx_file_path: Путь к DOCX файлу
    :return: Список обработанных текстовых частей
    """
    manage_file(data_txt_path, 'txt')
    manage_file(output_json, 'json')
    
    print("Файлы обработаны.")

    # Извлечение текста из DOCX файла
    text = docx2txt.process(docx_file_path)
    
    # Очистка текста от нежелательных символов
    text = re.sub(r"[^А-Яа-яёЁa-zA-Z\s.,«»0-9()@._+-]", "", text)
    text = re.sub(r"\(Рисунок (\d+)\)", r"[img_data/imgs\1.jpg]", text)

    # Запись очищенного текста в файл
    with open(data_txt_path, "w", encoding="utf-8") as file:
        file.write(text)
    with open(data_txt_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    data_plugs = {}
    data_titelse = {}
    fin_ind = 0
    for ind, i in enumerate(content[content.index('СОДЕРЖАНИЕ\n') + 1:]):
        if len(data_plugs):
            if list(data_plugs.keys())[0] in re.sub(r'\s+', ' ', re.sub(r'[^А-Яа-яёЁa-zA-Z\s.,«»]', '', i)).strip():
                fin_ind = ind
                break
        if '.' not in i and len(re.sub(r'\s+', ' ', re.sub(r'[^А-Яа-яёЁa-zA-Z\s.,«»]', '', i)).strip()) > 0:
            data_plugs[re.sub(r'\s+', ' ', re.sub(r'[^А-Яа-яёЁa-zA-Z\s.,«»]', '', i)).strip()] = ''
        if len(re.sub(r'\s+', ' ', re.sub(r'[^А-Яа-яёЁa-zA-Z\s.,«»]', '', i)).strip()) > 0:
            data_titelse[re.sub(r'[\d\.]+|\t', '', i).strip()] = i.split('\t')[0]
    point_key, ind_key = 0, 0
    keys_data_plugs = list(data_plugs.keys())
    for ind, i in enumerate(content[fin_ind + content.index('СОДЕРЖАНИЕ\n') + 1:]):
        if len(keys_data_plugs) <= point_key + 1:
            ind_key = ind
            break
        if keys_data_plugs[point_key + 1] not in i:
            if re.sub(r'[\d\.]+|\t', '', i).strip() in data_titelse:
                elem = i.replace(re.sub(r'[\d\.]+|\t', '', i).strip(), data_titelse[re.sub(r'[\d\.]+|\t', '', i).strip()])
                data_plugs[keys_data_plugs[point_key]] += elem
            else:
                data_plugs[keys_data_plugs[point_key]] += i
        else:
            point_key += 1
    for ind, i in enumerate(content[fin_ind + content.index('СОДЕРЖАНИЕ\n') + 1 + ind_key:]):
        if re.sub(r'[\d\.]+|\t', '', i).strip() in data_titelse:
                elem = i.replace(re.sub(r'[\d\.]+|\t', '', i).strip(), data_titelse[re.sub(r'[\d\.]+|\t', '', i).strip()])
                data_plugs[keys_data_plugs[-1]] += elem
        else:
            data_plugs[keys_data_plugs[-1]] += i

    # Запись обработанных данных в JSON файл
    with open(output_json, 'w', encoding='utf-8') as json_file:
        json.dump(data_plugs, json_file, ensure_ascii=False, indent=4)

    # Разделение длинных текстов на части и возвращение результата
    chunks_data = split_long_texts(data_plugs, max_length=512)
    
    chunks = []
    
    for key in chunks_data:
        if isinstance(chunks_data[key], list):
            chunks.extend(chunks_data[key])
        else:
            chunks.append(data_plugs[key])

    return chunks