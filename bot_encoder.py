# type: ignore
import os
import time
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен берется из переменных окружения Render
TOKEN = os.getenv('TOKEN')
if not TOKEN:
    logging.error("❌ TOKEN не найден в переменных окружения!")
    exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# БАЗА ДАННЫХ
users_db = {}  # user_id: {group_id, role}
groups_db = {}  # group_id: {owner_id, max_members, members_count, config_id, member_passwords}
user_states = {}

# АДМИН
ADMIN_PASSWORD = "adminp255"

# 5 уникальных конфигураций шифрования
GROUP_CONFIGS = {
    1: {
        'basic_symbols': {
            'а': 'X7k', 'б': 'Q2r', 'в': 'L9m', 'г': 'P4s', 'д': 'K3t', 'е': 'N8v', 'ё': 'R1w', 'ж': 'M6y',
            'з': 'T5z', 'и': 'S0a', 'й': 'V9b', 'к': 'W2c', 'л': 'Z8d', 'м': 'Y4e', 'н': 'U7f', 'о': 'X1g',
            'п': 'Q6h', 'р': 'L3i', 'с': 'P9j', 'т': 'K5l', 'у': 'N2n', 'ф': 'R8o', 'х': 'M1p', 'ц': 'T7q',
            'ч': 'S4u', 'ш': 'V0x', 'щ': 'W6A', 'ъ': 'Z3B', 'ы': 'Y9C', 'ь': 'U5D', 'э': 'X2E', 'ю': 'Q7F',
            'я': 'L4G',
            'А': 'P8H', 'Б': 'K1I', 'В': 'N6J', 'Г': 'R3K', 'Д': 'M9L', 'Е': 'T2M', 'Ё': 'S7N', 'Ж': 'V5O',
            'З': 'W0P', 'И': 'Z4Q', 'Й': 'Y8R', 'К': 'U1S', 'Л': 'X6T', 'М': 'Q9U', 'Н': 'L2V', 'О': 'P5W',
            'П': 'K7X', 'Р': 'N4Y', 'С': 'R0Z', 'Т': 'M3a', 'У': 'T8b', 'Ф': 'S1c', 'Х': 'V6d', 'Ц': 'W9e',
            'Ч': 'Z2f', 'Ш': 'Y7g', 'Щ': 'U4h', 'Ъ': 'X0i', 'Ы': 'Q3j', 'Ь': 'L8k', 'Э': 'P1l', 'Ю': 'K6m',
            'Я': 'N9n',
            'a': 'R4o', 'b': 'M2p', 'c': 'T9q', 'd': 'S6r', 'e': 'V1s', 'f': 'W8t', 'g': 'Z5u', 'h': 'Y0v',
            'i': 'U3w', 'j': 'X7x', 'k': 'Q4y', 'l': 'L1z', 'm': 'P6A', 'n': 'K9B', 'o': 'N5C', 'p': 'R2D',
            'q': 'M8E', 'r': 'T0F', 's': 'S3G', 't': 'V7H', 'u': 'W4I', 'v': 'Z1J', 'w': 'Y6K', 'x': 'U9L',
            'y': 'X2M', 'z': 'Q8N',
            'A': 'L5O', 'B': 'P0P', 'C': 'K4Q', 'D': 'N7R', 'E': 'R1S', 'F': 'M5T', 'G': 'T3U', 'H': 'S9V',
            'I': 'V2W', 'J': 'W6X', 'K': 'Z8Y', 'L': 'Y1Z', 'M': 'U4a', 'N': 'X9b', 'O': 'Q5c', 'P': 'L7d',
            'Q': 'P2e', 'R': 'K0f', 'S': 'N6g', 'T': 'R8h', 'U': 'M1i', 'V': 'T4j', 'W': 'S7k', 'X': 'V9l',
            'Y': 'W3m', 'Z': 'Z0n',
            '0': 'o5P', '1': 'p9Q', '2': 'q2R', '3': 'r7S', '4': 's1T', '5': 't6U', '6': 'u3V', '7': 'v8W',
            '8': 'w4X', '9': 'x0Y'
        },
        'special_symbols': {
            '!': 'y7Z', '@': 'z2A', '#': 'A8B', '$': 'B3C', '%': 'C9D', '^': 'D4E', '&': 'E0F', '*': 'F5G',
            '(': 'G1H', ')': 'H6I', '-': 'I2J', '_': 'J7K', '=': 'K3L', '+': 'L8M', '[': 'M4N', ']': 'N9O',
            '{': 'O5P', '}': 'P1Q', '|': 'Q6R', ';': 'R2S', ':': 'S7T', '"': 'T3U', "'": 'U8V', ',': 'V4W',
            '.': 'W9X', '/': 'X5Y', '?': 'Y1Z', '>': 'Z6A', '<': 'A2B', '~': 'B7C', '`': 'C3D'
        },
        'space_start': 'D8k',
        'special_start': 'F4m',
        'length_start': 'H9n',
        'end_marker': 'J5p'
    },
    2: {
        'basic_symbols': {
            'а': 'B3r', 'б': 'C8s', 'в': 'D4t', 'г': 'E9u', 'д': 'F5v', 'е': 'G0w', 'ё': 'H6x', 'ж': 'I1y',
            'з': 'J7z', 'и': 'K2A', 'й': 'L8B', 'к': 'M3C', 'л': 'N9D', 'м': 'O4E', 'н': 'P0F', 'о': 'Q5G',
            'п': 'R1H', 'р': 'S6I', 'с': 'T2J', 'т': 'U7K', 'у': 'V3L', 'ф': 'W8M', 'х': 'X4N', 'ц': 'Y9O',
            'ч': 'Z5P', 'ш': 'A1Q', 'щ': 'B6R', 'ъ': 'C2S', 'ы': 'D7T', 'ь': 'E3U', 'э': 'F8V', 'ю': 'G4W',
            'я': 'H0X',
            'А': 'I5Y', 'Б': 'J1Z', 'В': 'K6a', 'Г': 'L2b', 'Д': 'M7c', 'Е': 'N3d', 'Ё': 'O8e', 'Ж': 'P4f',
            'З': 'Q0g', 'И': 'R5h', 'Й': 'S1i', 'К': 'T6j', 'Л': 'U2k', 'М': 'V7l', 'Н': 'W3m', 'О': 'X8n',
            'П': 'Y4o', 'Р': 'Z0p', 'С': 'A5q', 'Т': 'B1r', 'У': 'C6s', 'Ф': 'D2t', 'Х': 'E7u', 'Ц': 'F3v',
            'Ч': 'G8w', 'Ш': 'H4x', 'Щ': 'I0y', 'Ъ': 'J5z', 'Ы': 'K1A', 'Ь': 'L6B', 'Э': 'M2C', 'Ю': 'N7D',
            'Я': 'O3E',
            'a': 'P8F', 'b': 'Q4G', 'c': 'R0H', 'd': 'S5I', 'e': 'T1J', 'f': 'U6K', 'g': 'V2L', 'h': 'W7M',
            'i': 'X3N', 'j': 'Y8O', 'k': 'Z4P', 'l': 'A0Q', 'm': 'B5R', 'n': 'C1S', 'o': 'D6T', 'p': 'E2U',
            'q': 'F7V', 'r': 'G3W', 's': 'H8X', 't': 'I4Y', 'u': 'J0Z', 'v': 'K5a', 'w': 'L1b', 'x': 'M6c',
            'y': 'N2d', 'z': 'O7e',
            'A': 'P3f', 'B': 'Q8g', 'C': 'R4h', 'D': 'S0i', 'E': 'T5j', 'F': 'U1k', 'G': 'V6l', 'H': 'W2m',
            'I': 'X7n', 'J': 'Y3o', 'K': 'Z8p', 'L': 'A4q', 'M': 'B0r', 'N': 'C5s', 'O': 'D1t', 'P': 'E6u',
            'Q': 'F2v', 'R': 'G7w', 'S': 'H3x', 'T': 'I8y', 'U': 'J4z', 'V': 'K0A', 'W': 'L5B', 'X': 'M1C',
            'Y': 'N6D', 'Z': 'O2E',
            '0': 'F7d', '1': 'G2e', '2': 'H8f', '3': 'I3g', '4': 'J9h', '5': 'K4i', '6': 'L0j', '7': 'M5k',
            '8': 'N1l', '9': 'O6m'
        },
        'special_symbols': {
            '!': 'P2q', '@': 'Q7r', '#': 'R3s', '$': 'S8t', '%': 'T4u', '^': 'U0v', '&': 'V5w', '*': 'W1x',
            '(': 'X6y', ')': 'Y2z', '-': 'Z7a', '_': 'A3b', '=': 'B8c', '+': 'C4d', '[': 'D0e', ']': 'E5f',
            '{': 'F1g', '}': 'G6h', '|': 'H2i', ';': 'I7j', ':': 'J3k', '"': 'K8l', "'": 'L4m', ',': 'M0n',
            '.': 'N5o', '/': 'O1p', '?': 'P6q', '>': 'Q2r', '<': 'R7s', '~': 'S3t', '`': 'T8u'
        },
        'space_start': 'U4v',
        'special_start': 'W0x',
        'length_start': 'Y5z',
        'end_marker': 'A1b'
    },
    # ... остальные группы 3,4,5
}

# Инициализация групп


def initialize_groups():
    """Инициализация групп с паролями владельцев и участников"""
    for group_id in range(1, 6):
        if group_id not in groups_db:
            groups_db[group_id] = {
                'owner_id': None,
                'max_members': 5,
                'members_count': 0,
                'config_id': group_id,
                'member_passwords': [
                    f"kls{group_id}32",
                    f"bs3{group_id}67",
                    f"wae{group_id}89",
                    f"fhd{group_id}39"
                ],
                'owner_password': f"as34h{group_id}s97"
            }

# ФУНКЦИИ ШИФРОВАНИЯ


def encode_text(text, config):
    """Шифрование текста с использованием конфигурации группы"""
    basic_symbols = config['basic_symbols']
    special_symbols = config['special_symbols']

    splitted_txt = text.split()
    num_of_spaces = len(text) - len("".join(splitted_txt))

    # Кодирование количества пробелов
    if num_of_spaces < 10:
        txt_num_of_spaces = config['space_start'] + \
            basic_symbols[str(num_of_spaces)]
    elif num_of_spaces < 100:
        txt_num_of_spaces = config['space_start'] + basic_symbols[str(
            num_of_spaces//10)] + basic_symbols[str(num_of_spaces % 10)]
    else:
        txt_num_of_spaces = config['space_start'] + basic_symbols[str(num_of_spaces//100)] + basic_symbols[str(
            num_of_spaces % 100//10)] + basic_symbols[str(num_of_spaces % 100 % 10)]

    txt_num_of_spaces += config['end_marker']

    # Кодирование специальных символов
    place_of_spec_symbols = ''
    ind = 0
    for i in splitted_txt:
        if i and i[-1] in special_symbols:
            if ind < 10:
                place_of_spec_symbols += (
                    special_symbols[i[-1]] + basic_symbols[str(ind)])
            elif ind < 100:
                place_of_spec_symbols += (special_symbols[i[-1]] + basic_symbols[str(
                    ind//10)] + basic_symbols[str(ind % 10)])
            else:
                place_of_spec_symbols += (special_symbols[i[-1]] + basic_symbols[str(
                    ind//100)] + basic_symbols[str(ind % 100//10)] + basic_symbols[str(ind % 100 % 10)])
        ind += 1

    if not place_of_spec_symbols:
        place_of_spec_symbols = 'kl4'

    special_symbols_in_txt = config['special_start'] + \
        place_of_spec_symbols + config['end_marker']

    # Кодирование длин слов
    lengths_codes = ''
    for i in splitted_txt:
        effective_len = (
            len(i)-1) if (i and i[-1] in special_symbols) else len(i)
        for d in f"{effective_len:03d}":
            lengths_codes += basic_symbols[d]

    lengths_section = config['length_start'] + \
        lengths_codes + config['end_marker'] * 2

    # Кодирование основных символов
    basic_symbols_in_txt = ''
    for i in splitted_txt:
        for x in i:
            if x in basic_symbols:
                basic_symbols_in_txt += basic_symbols[x]
            elif x in special_symbols:
                pass
            else:
                basic_symbols_in_txt += x

    return txt_num_of_spaces + special_symbols_in_txt + lengths_section + basic_symbols_in_txt


def decode_text(encoded_text, config):
    """Дешифрование текста с использованием конфигурации группы"""
    basic_symbols = config['basic_symbols']
    special_symbols = config['special_symbols']
    reverse_basic = {v: k for k, v in basic_symbols.items()}
    reverse_special = {v: k for k, v in special_symbols.items()}

    try:
        # Используем маркеры из конфигурации
        space_start = config['space_start']
        special_start = config['special_start']
        length_start = config['length_start']
        end_marker = config['end_marker']

        # ДЕБАГ: выводим что получили
        print(f"ДЕБАГ: encoded_text={encoded_text}")
        print(
            f"ДЕБАГ: space_start={space_start}, special_start={special_start}, length_start={length_start}, end_marker={end_marker}")

        # 1. Секция пробелов
        if not encoded_text.startswith(space_start):
            return "Ошибка: неверный формат (отсутствует space_start)"

        space_end_pos = encoded_text.find(end_marker, len(space_start))
        if space_end_pos == -1:
            return "Ошибка: не найден конец секции пробелов"

        space_section = encoded_text[len(space_start):space_end_pos]
        print(f"ДЕБАГ: space_section={space_section}")

        # Декодируем количество пробелов
        space_code = ''
        i = 0
        while i < len(space_section):
            chunk = space_section[i:i+3]
            if chunk in reverse_basic:
                space_code += reverse_basic[chunk]
                i += 3
            else:
                i += 1

        num_spaces = int(space_code) if space_code.isdigit() else 0
        print(f"ДЕБАГ: num_spaces={num_spaces}")

        # 2. Секция специальных символов
        remaining_text = encoded_text[space_end_pos + len(end_marker):]
        print(f"ДЕБАГ: remaining_text после пробелов={remaining_text}")

        if not remaining_text.startswith(special_start):
            return "Ошибка: не найдена секция специальных символов"

        spec_end_pos = remaining_text.find(end_marker, len(special_start))
        if spec_end_pos == -1:
            return "Ошибка: не найден конец секции специальных символов"

        spec_section = remaining_text[len(special_start):spec_end_pos]
        print(f"ДЕБАГ: spec_section={spec_section}")

        # Декодируем специальные символы
        pairs = []
        i = 0
        while i < len(spec_section):
            # Ищем специальный символ (3 символа)
            if i + 3 <= len(spec_section):
                token = spec_section[i:i+3]
                if token in reverse_special:
                    pairs.append({'symb': reverse_special[token], 'idx': ''})
                    i += 3
                    # После спецсимвола идем до конца или до следующего спецсимвола
                    while i < len(spec_section):
                        if i + 3 <= len(spec_section):
                            next_token = spec_section[i:i+3]
                            if next_token in reverse_special:
                                break  # Новый спецсимвол
                            elif next_token in reverse_basic:
                                pairs[-1]['idx'] += reverse_basic[next_token]
                                i += 3
                            else:
                                i += 1
                        else:
                            i += 1
                else:
                    i += 1
            else:
                i += 1

        print(f"ДЕБАГ: pairs={pairs}")

        # 3. Секция длин слов
        remaining_text = remaining_text[spec_end_pos + len(end_marker):]
        print(f"ДЕБАГ: remaining_text после спецсимволов={remaining_text}")

        if not remaining_text.startswith(length_start):
            return "Ошибка: не найдена секция длин"

        len_end_pos = remaining_text.find(end_marker * 2, len(length_start))
        if len_end_pos == -1:
            return "Ошибка: не найден конец секции длин"

        len_section = remaining_text[len(length_start):len_end_pos]
        print(f"ДЕБАГ: len_section={len_section}")

        # Декодируем длины слов
        lengths_list = []
        i = 0
        while i < len(len_section):
            if i + 9 <= len(len_section):  # 3 цифры по 3 символа = 9
                word_length_code = ''
                for j in range(3):
                    chunk = len_section[i+j*3:i+(j+1)*3]
                    if chunk in reverse_basic:
                        word_length_code += reverse_basic[chunk]
                    else:
                        word_length_code += '0'
                if word_length_code.isdigit():
                    lengths_list.append(int(word_length_code))
                i += 9
            else:
                i += 1

        print(f"ДЕБАГ: lengths_list={lengths_list}")

        # 4. Основные символы
        basic_section = remaining_text[len_end_pos + len(end_marker)*2:]
        print(f"ДЕБАГ: basic_section={basic_section}")

        # Декодируем основные символы
        decoded_text = ''
        i = 0
        while i < len(basic_section):
            if i + 3 <= len(basic_section):
                chunk = basic_section[i:i+3]
                if chunk in reverse_basic:
                    decoded_text += reverse_basic[chunk]
                    i += 3
                else:
                    # Если не нашли, пробуем сдвинуться на 1 символ
                    decoded_text += basic_section[i]
                    i += 1
            else:
                decoded_text += basic_section[i]
                i += 1

        print(f"ДЕБАГ: decoded_text до разбиения={decoded_text}")

        # Формируем слова по длинам
        words = []
        if lengths_list:
            pos = 0
            for L in lengths_list:
                if pos + L <= len(decoded_text):
                    words.append(decoded_text[pos:pos+L])
                    pos += L
                else:
                    break

        # Если не удалось разбить по длинам, используем пробелы
        if not words:
            words = decoded_text.split()

        print(f"ДЕБАГ: words до добавления спецсимволов={words}")

        # Добавляем специальные символы
        for pair in pairs:
            symb = pair['symb']
            idx_str = pair['idx']
            if idx_str.isdigit():
                idx_int = int(idx_str)
                if idx_int < len(words):
                    words[idx_int] += symb

        print(f"ДЕБАГ: words после добавления спецсимволов={words}")

        # Восстанавливаем текст
        result = " ".join(words)

        # Добавляем правильное количество пробелов (если нужно)
        expected_spaces = len(words) - 1 if words else 0
        if num_spaces > expected_spaces:
            # Добавляем дополнительные пробелы
            result += " " * (num_spaces - expected_spaces)

        print(f"ДЕБАГ: final result={result}")
        return result

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ДЕБАГ ОШИБКА: {error_details}")
        return f"Ошибка дешифрования: {str(e)}"

# КЛАВИАТУРЫ (остаются без изменений)


def get_main_keyboard(user_id):
    builder = ReplyKeyboardBuilder()

    if user_id in users_db:
        user_data = users_db[user_id]
        if user_data.get('role') == 'admin':
            builder.add(KeyboardButton(text="👑 Админ-панель"))
        elif user_data.get('role') == 'owner':
            builder.add(KeyboardButton(text="⚙️ Управление группой"))

        builder.add(KeyboardButton(text="🔐 Шифровать"))
        builder.add(KeyboardButton(text="🔓 Расшифровать"))

        if user_data.get('role') == 'owner':
            builder.add(KeyboardButton(text="👥 Информация о группе"))

        builder.add(KeyboardButton(text="ℹ️ Помощь"))
        builder.add(KeyboardButton(text="🚪 Выйти"))
    else:
        builder.add(KeyboardButton(text="👑 Админ-панель"))
        builder.add(KeyboardButton(text="👑 Стать владельцем"))
        builder.add(KeyboardButton(text="🔑 Войти в группу"))
        builder.add(KeyboardButton(text="ℹ️ О боте"))

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# ОБРАБОТЧИКИ (остаются без изменений)


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    await message.reply(
        "🤖 Добро пожаловать в бот-шифратор!\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard(user_id)
    )


@dp.message(lambda message: message.text == "👑 Админ-панель")
async def admin_access_handler(message: types.Message):
    user_id = message.from_user.id
    if users_db.get(user_id, {}).get('role') == 'admin':
        await message.reply("👑 Админ-панель:", reply_markup=get_admin_keyboard())
    else:
        user_states[user_id] = "waiting_admin_password"
        await message.reply("Введите пароль админ-панели:")


@dp.message(lambda message: message.text == "👑 Стать владельцем")
async def become_owner_handler(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_owner_password"

    text = (
        "👑 Приобретение группы\n\n"
        "Чтобы стать владельцем группы и получить:\n"
        "• Уникальный шифр для вашей группы\n"
        "• 4 пароля для участников\n"
        "• Панель управления группой\n\n"
        "📞 Свяжитесь с создателем: @butwhynotbro\n"
        "для обсуждения условий и оплаты.\n\n"
        "После оплаты вам выдадут пароль для доступа.\n"
        "Введите пароль владельца:"
    )
    await message.reply(text)


@dp.message(lambda message: message.text == "🔑 Войти в группу")
async def join_group_handler(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_group_id"
    await message.reply("Введите ID группы:")


@dp.message(lambda message: message.text == "🔐 Шифровать")
async def encode_button_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_db:
        await message.reply("❌ Сначала требуется авторизация!")
        return

    user_states[user_id] = "waiting_for_encode"
    await message.reply("📝 Введите текст для шифрования:")


@dp.message(lambda message: message.text == "🔓 Расшифровать")
async def decode_button_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_db:
        await message.reply("❌ Сначала требуется авторизация!")
        return

    user_states[user_id] = "waiting_for_decode"
    await message.reply("🔓 Введите зашифрованный текст:")


@dp.message(lambda message: message.text == "👥 Информация о группе")
async def group_info_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id, {})

    if user_data.get('role') != 'owner':
        await message.reply("❌ Только владелец группы имеет доступ к этой информации!")
        return

    group_id = user_data['group_id']
    group_data = groups_db[group_id]

    text = (
        f"👥 Информация о группе #{group_id}\n"
        f"Участников: {group_data['members_count']}/{group_data['max_members']}\n"
        f"Ваша роль: Владелец"
    )
    await message.reply(text)


@dp.message(lambda message: message.text == "ℹ️ Помощь")
async def help_handler(message: types.Message):
    help_text = (
        "🤖 Бот-шифратор с групповой системой\n\n"
        "🔐 Шифровать - зашифровать текст\n"
        "🔓 Расшифровать - расшифровать текст\n"
        "👥 Информация о группе - информация (только для владельцев)\n"
        "ℹ️ Помощь - это сообщение\n"
        "🚪 Выйти - выйти из системы\n\n"
        "Каждая группа имеет уникальный шифр!"
    )
    await message.reply(help_text)


@dp.message(lambda message: message.text == "ℹ️ О боте")
async def about_handler(message: types.Message):
    about_text = (
        "🔐 Бот-шифратор с уникальными шифрами\n\n"
        "• 5 различных групп с уникальными шифрами\n"
        "• Групповая система доступа\n"
        "• Удобные кнопки вместо команд\n"
        "• Профессиональное шифрование\n\n"
        "Для доступа требуется авторизация."
    )
    await message.reply(about_text)


@dp.message(lambda message: message.text == "🚪 Выйти")
async def logout_button_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id in users_db:
        # Уменьшаем счетчик участников в группе
        user_data = users_db[user_id]
        if user_data.get('role') in ['owner', 'member']:
            group_id = user_data['group_id']
            if group_id in groups_db:
                groups_db[group_id]['members_count'] = max(
                    0, groups_db[group_id]['members_count'] - 1)

        del users_db[user_id]
        user_states.pop(user_id, None)
        await message.reply("✅ Вы вышли из системы.", reply_markup=get_main_keyboard(user_id))
    else:
        await message.reply("Вы и так не авторизованы.")

# ==================== АДМИН-ПАНЕЛЬ ====================


@dp.message(lambda message: message.text == "📊 Все группы")
async def admin_all_groups_handler(message: types.Message):
    user_id = message.from_user.id
    if users_db.get(user_id, {}).get('role') != 'admin':
        await message.reply("❌ Доступ запрещен!")
        return

    groups_info = "👥 Все группы:\n\n"
    for group_id, group_data in groups_db.items():
        owner_info = f"Владелец: {group_data['owner_id']}" if group_data['owner_id'] else "Владелец: нет"
        groups_info += f"Группа #{group_id}\n"
        groups_info += f"Участников: {group_data['members_count']}/{group_data['max_members']}\n"
        groups_info += f"{owner_info}\n"
        groups_info += "─" * 20 + "\n"

    await message.reply(groups_info)


@dp.message(lambda message: message.text == "👥 Все пользователи")
async def admin_all_users_handler(message: types.Message):
    user_id = message.from_user.id
    if users_db.get(user_id, {}).get('role') != 'admin':
        await message.reply("❌ Доступ запрещен!")
        return

    if not users_db:
        await message.reply("❌ Нет зарегистрированных пользователей")
        return

    users_info = "👤 Все пользователи:\n\n"
    for user_id, user_data in users_db.items():
        users_info += f"ID: {user_id}\n"
        users_info += f"Группа: {user_data.get('group_id', 'нет')}\n"
        users_info += f"Роль: {user_data.get('role', 'неизвестно')}\n"
        users_info += "─" * 20 + "\n"

    await message.reply(users_info)


@dp.message(lambda message: message.text == "🔑 Пароли групп")
async def admin_group_passwords_handler(message: types.Message):
    user_id = message.from_user.id
    if users_db.get(user_id, {}).get('role') != 'admin':
        await message.reply("❌ Доступ запрещен!")
        return

    passwords_info = "🔑 Пароли всех групп:\n\n"
    for group_id, group_data in groups_db.items():
        passwords_info += f"Группа #{group_id}:\n"
        passwords_info += f"Пароль владельца: {group_data['owner_password']}\n"
        passwords_info += f"Пароли участников: {', '.join(group_data['member_passwords'])}\n"
        passwords_info += "─" * 20 + "\n"

    await message.reply(passwords_info)


@dp.message(lambda message: message.text == "🔙 Назад")
async def back_button_handler(message: types.Message):
    user_id = message.from_user.id
    await message.reply(
        "Возврат в главное меню:",
        reply_markup=get_main_keyboard(user_id)
    )

# ==================== ПАНЕЛЬ ВЛАДЕЛЬЦА ====================


@dp.message(lambda message: message.text == "⚙️ Управление группой")
async def owner_panel_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id, {})

    if user_data.get('role') != 'owner':
        await message.reply("❌ Только владелец группы имеет доступ!")
        return

    group_id = user_data['group_id']
    group_data = groups_db[group_id]

    text = (
        f"⚙️ Управление группой #{group_id}\n"
        f"Участников: {group_data['members_count']}/{group_data['max_members']}\n\n"
        "Выберите действие:"
    )
    await message.reply(text, reply_markup=get_owner_keyboard())


@dp.message(lambda message: message.text == "👥 Участники")
async def owner_members_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id, {})

    if user_data.get('role') != 'owner':
        await message.reply("❌ Только владелец группы имеет доступ!")
        return

    group_id = user_data['group_id']

    # Находим всех участников группы
    group_members = []
    for uid, u_data in users_db.items():
        if u_data.get('group_id') == group_id and u_data.get('role') in ['owner', 'member']:
            group_members.append((uid, u_data.get('role')))

    if not group_members:
        await message.reply("❌ В группе нет участников")
        return

    members_info = f"👥 Участники группы #{group_id}:\n\n"
    for uid, role in group_members:
        role_text = "Владелец" if role == 'owner' else "Участник"
        members_info += f"ID: {uid}\nРоль: {role_text}\n"
        members_info += "─" * 20 + "\n"

    await message.reply(members_info)


@dp.message(lambda message: message.text == "🔑 Пароли группы")
async def owner_passwords_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id, {})

    if user_data.get('role') != 'owner':
        await message.reply("❌ Только владелец группы имеет доступ!")
        return

    group_id = user_data['group_id']
    group_data = groups_db[group_id]

    passwords_info = (
        f"🔑 Пароли группы #{group_id}:\n\n"
        f"Пароли для участников:\n"
    )

    for i, password in enumerate(group_data['member_passwords'], 1):
        passwords_info += f"{i}. {password}\n"

    passwords_info += f"\nID группы: {group_id}\n"
    passwords_info += "Передайте эти пароли участникам для входа в группу."

    await message.reply(passwords_info)


@dp.message(lambda message: message.text == "🗑 Исключить")
async def owner_remove_member_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id, {})

    if user_data.get('role') != 'owner':
        await message.reply("❌ Только владелец группы имеет доступ!")
        return

    user_states[user_id] = "waiting_remove_member"
    await message.reply("Введите ID пользователя для исключения:")


@dp.message(lambda message: message.text == "📊 Статистика")
async def owner_stats_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id, {})

    if user_data.get('role') != 'owner':
        await message.reply("❌ Только владелец группы имеет доступ!")
        return

    group_id = user_data['group_id']
    group_data = groups_db[group_id]

    # Считаем участников
    member_count = 0
    for uid, u_data in users_db.items():
        if u_data.get('group_id') == group_id and u_data.get('role') == 'member':
            member_count += 1

    stats_info = (
        f"📊 Статистика группы #{group_id}:\n\n"
        f"Всего участников: {group_data['members_count']}\n"
        f"Владельцев: 1\n"
        f"Обычных участников: {member_count}\n"
        f"Свободных мест: {group_data['max_members'] - group_data['members_count']}\n"
        f"Лимит участников: {group_data['max_members']}"
    )

    await message.reply(stats_info)

# Обработчик текстовых сообщений (остается без изменений)


@dp.message()
async def text_message_handler(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text.strip()

    user_state = user_states.get(user_id)

    if user_state == "waiting_admin_password":
        if user_text == ADMIN_PASSWORD:
            users_db[user_id] = {'role': 'admin'}
            user_states.pop(user_id, None)
            await message.reply(
                "✅ Вы вошли как администратор!",
                reply_markup=get_main_keyboard(user_id)
            )
        else:
            await message.reply("❌ Неверный пароль админа!")

    elif user_state == "waiting_owner_password":
        for group_id, group_data in groups_db.items():
            if user_text == group_data['owner_password']:
                if group_data['owner_id'] is None:
                    group_data['owner_id'] = user_id
                    group_data['members_count'] = 1
                    users_db[user_id] = {
                        'group_id': group_id,
                        'role': 'owner'
                    }
                    user_states.pop(user_id, None)
                    await message.reply(
                        f"✅ Вы стали владельцем группы #{group_id}!",
                        reply_markup=get_main_keyboard(user_id)
                    )
                    return
                else:
                    await message.reply("❌ Эта группа уже имеет владельца!")
                    return

        await message.reply("❌ Неверный пароль владельца!")

    elif user_state == "waiting_group_id":
        try:
            group_id = int(user_text)
            if group_id not in groups_db:
                await message.reply("❌ Группа не найдена!")
                return

            user_states[user_id] = f"waiting_member_password_{group_id}"
            await message.reply("Введите пароль участника:")

        except ValueError:
            await message.reply("❌ Введите корректный ID группы (число)")

    elif user_state and user_state.startswith("waiting_member_password_"):
        group_id = int(user_state.split("_")[-1])
        group_data = groups_db[group_id]

        if user_text in group_data['member_passwords']:
            users_db[user_id] = {
                'group_id': group_id,
                'role': 'member'
            }
            group_data['members_count'] += 1
            user_states.pop(user_id, None)

            await message.reply(
                f"✅ Вы успешно вошли в группу #{group_id}!",
                reply_markup=get_main_keyboard(user_id)
            )
        else:
            await message.reply("❌ Неверный пароль!")

    elif user_state == "waiting_for_encode":
        if user_id not in users_db:
            await message.reply("❌ Сначала требуется авторизация!")
            return

        user_data = users_db[user_id]
        group_config = GROUP_CONFIGS[user_data['group_id']]

        try:
            encoded_text = encode_text(user_text, group_config)
            user_states.pop(user_id, None)
            await message.reply(
                f"🔐 Зашифрованный текст:\n`{encoded_text}`",
                parse_mode="Markdown",
                reply_markup=get_main_keyboard(user_id)
            )
        except Exception as e:
            user_states.pop(user_id, None)
            await message.reply(f"❌ Ошибка при шифровании: {e}", reply_markup=get_main_keyboard(user_id))

    elif user_state == "waiting_for_decode":
        if user_id not in users_db:
            await message.reply("❌ Сначала требуется авторизация!")
            return

        user_data = users_db[user_id]
        group_config = GROUP_CONFIGS[user_data['group_id']]

        try:
            decoded_text = decode_text(user_text, group_config)
            user_states.pop(user_id, None)
            await message.reply(
                f"🔓 Расшифрованный текст:\n{decoded_text}",
                reply_markup=get_main_keyboard(user_id)
            )
        except Exception as e:
            user_states.pop(user_id, None)
            await message.reply(f"❌ Ошибка при дешифровании: {e}", reply_markup=get_main_keyboard(user_id))

    elif user_state == "waiting_remove_member":
        if users_db.get(user_id, {}).get('role') != 'owner':
            await message.reply("❌ Доступ запрещен!")
            return

        try:
            target_user_id = int(user_text)
            user_data = users_db[user_id]
            group_id = user_data['group_id']

            # Проверяем, что пользователь существует и в той же группе
            if target_user_id in users_db and users_db[target_user_id].get('group_id') == group_id:
                target_role = users_db[target_user_id].get('role')

                if target_role == 'owner':
                    await message.reply("❌ Нельзя исключить владельца группы!")
                else:
                    # Исключаем пользователя
                    del users_db[target_user_id]
                    groups_db[group_id]['members_count'] = max(
                        0, groups_db[group_id]['members_count'] - 1)
                    user_states.pop(user_id, None)

                    await message.reply(
                        f"✅ Пользователь {target_user_id} исключен из группы!",
                        reply_markup=get_owner_keyboard()
                    )
            else:
                await message.reply("❌ Пользователь не найден в вашей группе!")

        except ValueError:
            await message.reply("❌ Введите корректный ID пользователя (число)")

    else:
        await message.reply(
            "Используйте кнопки для управления ботом:",
            reply_markup=get_main_keyboard(user_id)
        )


def get_admin_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📊 Все группы"))
    builder.add(KeyboardButton(text="👥 Все пользователи"))
    builder.add(KeyboardButton(text="🔑 Пароли групп"))
    builder.add(KeyboardButton(text="🔙 Назад"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_owner_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="👥 Участники"))
    builder.add(KeyboardButton(text="🗑 Исключить"))
    builder.add(KeyboardButton(text="🔑 Пароли группы"))
    builder.add(KeyboardButton(text="📊 Статистика"))
    builder.add(KeyboardButton(text="🔙 Назад"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


# Инициализация при запуске
initialize_groups()


async def main():
    logging.info("🤖 Бот запущен на Render!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
