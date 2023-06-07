"""
:license: MIT License
:copyright: (c) 2023 Zapzatron
"""
import source.Packages as Packages

packages = {
    "gtts": "gTTS==2.3.2",
    "openai": "openai==0.27.0",
    "aiohttp": "aiohttp==3.8.4",
    "EdgeGPT": "EdgeGPT==0.10.4",
    "pandas": "pandas==1.3.5",
    "mindsdb_sdk": "mindsdb-sdk==1.0.2",
    "pymysql": "PyMySQL==1.0.3",
    "aiomysql": "aiomysql==0.1.1",
    "aiosqlite": "aiosqlite==0.19.0",
    "telebot": "pyTelegramBotAPI==4.12.0",
    "pytz": "pytz==2023.3",
    "psutil": "psutil==5.9.4",
    "requests": "requests==2.28.2",
    "lxml": "lxml==4.9.2",
    "nest_asyncio": "nest_asyncio==1.5.6",
}

print("-" * 27)
print("Checking required packages.")
Packages.check_req_packages(packages, True)
print("Required packages checked.")
print("-" * 27)

from io import BufferedReader, BytesIO  # Используется для работы с бинарными потоками данных в памяти
import signal  # Используется для обработки сигналов от операционной системы
import data.config as config  # Используется для импорта данных конфигурации из локального файла
from telebot.async_telebot import AsyncTeleBot  # Используется для создания асинхронного экземпляра класса TeleBot
# from telebot import formatting
from aiohttp import web  # Используется для создания HTTP-сервера и клиента с помощью asyncio
# import mindsdb_sdk # Используется для работы с MindsDB SDK
# import atexit  # Используется для регистрации функций, которые будут вызваны при выходе из программы
import datetime  # Используется для работы с датами и временем
import os  # Используется для взаимодействия с операционной системой
import io  # Используется для работы с потоками данных
import json  # Используется для кодирования и декодирования данных JSON
import platform  # Используется для получения информации о текущей платформе
import shutil  # Используется для высокоуровневых файловых операций
# import sqlite3 # Используется для работы с базами данных SQLite
# import threading  # Используется для работы с потоками
import time  # Используется для работы с функциями, связанными со временем
import zipfile  # Используется для работы с архивами ZIP
from datetime import datetime as dt  # Используется для создания объектов datetime из строк или чисел
# from telebot import apihelper # Используется для работы с API Telegram
from telebot import asyncio_helper  # Используется для работы с асинхронным кодом в Telebot
from urllib.parse import urlparse  # Используется для разбора URL на компоненты
import pymysql.cursors  # Используется для работы с базами данных MySQL с использованием курсоров
import aiomysql  # Используется для создания асинхронного интерфейса к базам данных MySQL
import openai  # Используется для взаимодействия с API OpenAI
from gtts import gTTS  # Используется для преобразования текста в речь с использованием API Google Text-to-Speech
import pytz as ptz  # Используется для работы с часовыми поясами
import requests  # Используется для выполнения HTTP-запросов
import telebot  # Используется для создания экземпляров класса TeleBot и взаимодействия с API Telegram Bot
import traceback  # Используется для печати или логирования трассировок стека исключений
from EdgeGPT.EdgeGPT import Chatbot, \
    ConversationStyle  # Используются для создания экземпляров класса Chatbot и указания стилей разговора
import asyncio  # Используется для асинхронного программирования с использованием корутин и циклов событий
import nest_asyncio  # Используются для исправления asyncio, чтобы разрешить вложенные циклы событий
import re  # Используются для работы с регулярными выражениями
import aiosqlite  # Используются для создания асинхронного интерфейса к базам данных SQLite
import aiohttp  # Используется для создания асинхронного HTTP-клиента


def read_file(file_name, split_symbol="\n"):
    """
    Эта функция считывает содержимое файла с именем `file_name`
    и возвращает список строк, разделенных символом `split_symbol`.
    По умолчанию символ разделения - это символ новой строки (`/n`).

     :param file_name: Имя файла для считывания данных
     :param split_symbol: Символ разделения текста
    """
    with open(file_name, 'r') as file:
        return file.read().split(split_symbol)


class CustomBytesIO(BytesIO):
    def __init__(self, *args, **kwargs):
        self.name = "result.txt"
        super().__init__(*args, **kwargs)


async def logging(logs: str, print_logs: bool = True, write_file: bool = False,
                  logs_file_name: str = None, logs_dir_: str = "logs"):
    """
    Эта функция для логирования.

    Если `print_logs` равно `True`, логи будут выводиться в консоль.

    Если `write_file` равно `True`, функция записывает логи в файл.

    Если указано `logs_file_name`, то файл с логами будет с этим именем,
    иначе файл создастся с именем из первых 11 символов логов.

    Если указана `logs_dir_`, то файл с логами будет сохранён в неё,
    иначе в папку 'logs'.

    Если файл уже существует, логи добавляются в конец файла.

    Также происходит отправка логов через бот Telegram, если он определен
    и его токен соответствует значению в конфигурации.

    :param logs: Логи следующего вида '[05-06-2023 03:21:01] <логи>'

    :param print_logs: Выводить логи в чат или нет

    :param write_file: Записывать логи в файл или нет

    :param logs_file_name: Имя файла для записи логов

    :param logs_dir_: Директория куда будет сохранён файл с логами
    """
    ansi_codes = {
        "color_off": "\033[0m",
        "red": "\033[31m"
    }

    if print_logs:
        print(logs, flush=True)

    for code in ansi_codes:
        if ansi_codes[code] in logs:
            logs = logs.replace(ansi_codes[code], "")

    try:
        if not (bot is None) and bot.token == config.TELEGRAM_BOT_TOKEN:
            # temp = logs
            if len(logs) < MAX_MESSAGE_LENGTH:
                await bot.send_message(config.TELEGRAM_LOGS_CHANNEL, logs)
            else:
                await bot.send_document(config.TELEGRAM_LOGS_CHANNEL, BufferedReader(CustomBytesIO(logs.encode('utf-8'))))
                # temp_logs_file = f"{temp_dir}/logs/{logs[1:19]}.txt"
                # with open(temp_logs_file, "w", encoding="utf-8") as f:
                #     f.write(logs)
                # await bot.send_document(-1001957630208, open(temp_logs_file, 'rb'))
                # time.sleep(2)
                # os.remove(temp_logs_file)
            # while len(temp) > 0:
            #     response_chunk = temp[:MAX_MESSAGE_LENGTH]
            #     temp = temp[MAX_MESSAGE_LENGTH:]
            #     await bot.send_message(-1001957630208, response_chunk)
    except Exception:
        pass

    if write_file:
        if not os.path.exists(logs_dir_):
            os.makedirs(logs_dir_)

        if logs_file_name is None:
            logs_file_name = f"{logs_dir_}/{logs[1:11]}.txt"
        else:
            logs_file_name = f"{logs_dir_}/{logs_file_name}.txt"

        if os.path.exists(logs_file_name):
            with open(logs_file_name, 'r', encoding='utf-8') as logs_file:
                previous_text = logs_file.read()
            with open(logs_file_name, 'w', encoding='utf-8') as logs_file:
                logs_file.write(previous_text + logs + "\n")
        else:
            with open(logs_file_name, 'w', encoding='utf-8') as logs_file:
                logs_file.write(logs + "\n")


def get_time(tz: str | None = 'Europe/Moscow', form: str = '%d-%m-%Y %H:%M:%S', strp: bool = False):
    """
    Это функция для получения настоящего времени

    Функция возвращает текущее время в указанном часовом поясе и формате.

    Если strp равен True, функция возвращает время в виде объекта datetime, иначе - в виде строки.

    :param tz: Часовой пояс, по умолчанию "Europe/Moscow"

    :param form: Формат даты и времени, по умолчанию "%d-%m-%Y %H:%M:%S"

    :param strp: Выбор каким объектом выводить время"
    """
    if strp:
        if tz:
            return dt.strptime(dt.now(ptz.timezone(tz)).strftime(form), form)
        else:
            return dt.strptime(dt.now().strftime(form), form)
    else:
        if tz:
            return dt.now(ptz.timezone(tz)).strftime(form)
        else:
            return dt.now().strftime(form)


async def handle_exception(message=None, extra_text=None):
    """
    Эта функция обрабатывает исключения и выводит информацию об ошибках.

    В начале и конце вывода ставит разделитель из 120 дефисов.

    Если передан аргумент message, функция формирует строку с информацией об ошибке, включая время, идентификатор,
    имя функции и номер строки, а также саму ошибку. Затем вызывает функцию logging для записи лога с этой информацией,
    также указывая директорию для записи логов.

    Если message не передан, функция формирует строку с информацией об ошибке только с временем и самой ошибкой,
    после чего вызывает функцию logging для записи лога с этой информацией.

    Если передан аргумент extra_text, функция также вызывает функцию logging для записи лога с дополнительным текстом.

    :param message: Информация о пользователе

    :param extra_text: Дополнительный текст для лога
    """
    print("-" * 120)
    string_manager = io.StringIO()
    traceback.print_exc(file=string_manager)
    error = string_manager.getvalue()
    if message:
        await logging(logs=f"\033[31m[{message['time_text']}] "
                           f"Chat Id: {message['chat_id']} "
                           f"Id: {message['id']} Fn: {message['fn']} "
                           f"Ln: {message['ln']} Ошибка: \n{error}\033[0m",
                      write_file=True,
                      logs_dir_=logs_dir)
    else:
        await logging(logs=f"\033[31m[{get_time()}] Ошибка: \n{error}\033[0m",
                      write_file=True,
                      logs_dir_=logs_dir)
    if extra_text:
        await logging(logs=f"\033[31m[{message['time_text']}] "
                           f"{extra_text}\033[0m",
                      write_file=True,
                      logs_dir_=logs_dir)
    print("-" * 120)


class ExceptionHandler(telebot.ExceptionHandler):
    """
    Класс ExceptionHandler наследует от telebot.ExceptionHandler и переопределяет метод handle,
    который принимает аргумент exception. Метод обрабатывает исключения, возникающие в telebot.

    Если текст исключения заканчивается на "query is too old and response timeout expired or query ID is invalid",
    метод возвращает True, игнорируя это исключение.

    В противном случае метод выводит текст исключения, вызывает асинхронную функцию handle_exception()
    для обработки исключения и записи информации об ошибке, а затем возвращает True.
    """

    def handle(self, exception):
        if str(exception)[-68:] == "query is too old and response timeout expired or query ID is invalid":
            return True
        print(exception)
        asyncio.run(handle_exception())
        return True


# Позволяет запускать асинхронные функции (asyncio) внутри синхронных функций, используя один и тот же цикл событий.
nest_asyncio.apply()


async def is_spam(message, use_interval: datetime.timedelta = datetime.timedelta(seconds=30), command_name=None):
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    time_text = get_time()
    time_text_strp = dt.strptime(time_text, '%d-%m-%Y %H:%M:%S')
    if use_interval == datetime.timedelta(seconds=0):
        return False

    if command_name is None:
        command_name = message.text

    userid_comm = f"{user_id}_{command_name}"
    if userid_comm not in user_use_dict:
        user_use_dict[userid_comm] = time_text_strp
        await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                           f"Id: {user_id} Fn: {first_name} "
                           f"Ln: {last_name} Do: {command_name}",
                      write_file=True,
                      logs_dir_=logs_dir)
    else:
        success_comm_time = user_use_dict[userid_comm]
        dif_time_use = time_text_strp - success_comm_time
        if dif_time_use > use_interval:
            user_use_dict[userid_comm] = time_text_strp
            await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                               f"Id: {user_id} Fn: {first_name} "
                               f"Ln: {last_name} Do: {command_name}",
                          write_file=True,
                          logs_dir_=logs_dir)
            return False
        else:
            await bot.reply_to(message, f"Можно использовать через {use_interval - dif_time_use}")
            await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                               f"Id: {user_id} Fn: {first_name} "
                               f"Ln: {last_name} Do: Спам {command_name}",
                          write_file=True,
                          logs_dir_=logs_dir)
            return True


async def gen_markup(buttons_list, buttons_dest="auto", markup_type="Reply", callback_list=None, url=None,
                     url_text=None):
    def sort_buttons(markup_, buttons, callback, buttons_dest_):
        count = 0
        n = len(buttons)
        while True:
            if n - 3 >= 0 and buttons_dest_ == 3:
                if callback:
                    buttons_1 = telebot.types.InlineKeyboardButton(buttons[count],
                                                                   callback_data=callback[count])
                    buttons_2 = telebot.types.InlineKeyboardButton(buttons[count + 1],
                                                                   callback_data=callback[count + 1])
                    buttons_3 = telebot.types.InlineKeyboardButton(buttons[count + 2],
                                                                   callback_data=callback[count + 2])
                else:
                    buttons_1 = telebot.types.InlineKeyboardButton(buttons[count])
                    buttons_2 = telebot.types.InlineKeyboardButton(buttons[count + 1])
                    buttons_3 = telebot.types.InlineKeyboardButton(buttons[count + 2])

                markup_.add(buttons_1, buttons_2, buttons_3)
                count += 3
                n -= 3
            elif n - 2 >= 0 and buttons_dest_ >= 2:
                if callback:
                    buttons_1 = telebot.types.InlineKeyboardButton(buttons[count],
                                                                   callback_data=callback[count])
                    buttons_2 = telebot.types.InlineKeyboardButton(buttons[count + 1],
                                                                   callback_data=callback[count + 1])
                else:
                    buttons_1 = telebot.types.InlineKeyboardButton(buttons[count])
                    buttons_2 = telebot.types.InlineKeyboardButton(buttons[count + 1])
                markup_.add(buttons_1, buttons_2)
                count += 2
                n -= 2
            elif n - 1 >= 0 and buttons_dest_ >= 1:
                if callback:
                    buttons_1 = telebot.types.InlineKeyboardButton(buttons[count],
                                                                   callback_data=callback[count])
                else:
                    buttons_1 = telebot.types.InlineKeyboardButton(buttons[count])
                markup_.add(buttons_1)
                count += 1
                n -= 1
            else:
                break
        return markup_

    markup = ""
    if markup_type == "Reply":
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        if buttons_dest == "auto":
            for button in buttons_list:
                markup.add(button)
        elif buttons_dest == "3":
            markup = sort_buttons(markup, buttons_list, callback_list, int(buttons_dest))
    elif markup_type == "Inline":
        markup = telebot.types.InlineKeyboardMarkup()
        if url and url_text:
            markup.add(telebot.types.InlineKeyboardButton(text=url_text, url=url))
        if buttons_dest == "auto":
            for i in range(len(buttons_list)):
                markup.add(telebot.types.InlineKeyboardButton(buttons_list[i], callback_data=callback_list[i]))
        elif int(buttons_dest) < 4:
            markup = sort_buttons(markup, buttons_list, callback_list, int(buttons_dest))

    return markup


# thread_local = threading.local()


# def work_with_db(name, path, sql, parameters=None, fetch=1):
#     prev_path = os.getcwd()
#     os.chdir(path)
#
#     if not hasattr(thread_local, "con"):
#         thread_local.conn = sqlite3.connect(name)
#
#     sql = sql.replace("[name]", name[:-3])
#     con = thread_local.conn
#     cur = con.cursor()
#     if parameters:
#         cur.execute(sql, parameters)
#     else:
#         cur.execute(sql)
#     row = None
#     if sql[:6] == "CREATE" or sql[:6] == "DELETE" or sql[:6] == "INSERT":
#         con.commit()
#     if sql[:6] == "SELECT":
#         row = cur.fetchmany(fetch)
#     os.chdir(prev_path)
#     if row:
#         return row


async def work_with_db(db_path, sql, params=None, host="", user="", password=""):
    loop = asyncio.get_event_loop()
    # print(db)
    db_name = os.path.basename(urlparse(db_path).path)
    if db_name[-3:] == ".db":
        db_name = db_name[:-3]
    # print(db_name)
    # print(params)
    sql = sql.replace("[name]", db_name)
    if host and user and password:
        pool = await aiomysql.create_pool(host=host, user=user, password=password,
                                          db=db_path, loop=loop)

        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql)
                (content,) = await cur.fetchone()
        pool.close()
        await pool.wait_closed()
        # print(content)
        return content
    else:
        async with aiosqlite.connect(db_path, loop=loop) as db:
            if params:
                cursor = await db.execute(sql, params)
            else:
                cursor = await db.execute(sql)
            rows = None
            if sql[:6] == "CREATE" or sql[:6] == "DELETE" or sql[:6] == "INSERT":
                await db.commit()
            if sql[:6] == "SELECT":
                rows = await cursor.fetchall()

            await cursor.close()
            # print(rows)
            return rows


# def close_db():
#     con = getattr(thread_local, "con", None)
#     if con is not None:
#         con.close()


async def commands(message):
    chat_id = message["chat_id"]
    user_id = message["user_id"]
    first_name = message["first_name"]
    last_name = message["last_name"]
    time_text = get_time()
    text = message["text"]

    if text == "/commands" or text == "/start":
        await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                           f"Id: {user_id} Fn: {first_name} "
                           f"Ln: {last_name} Do: {text}",
                      write_file=True,
                      logs_dir_=logs_dir)

    commands_text = "Для вызова меню бота /menu\n" \
                    "Я могу помочь тебе в следующих действиях:\n" \
                    "1. Предоставить доступ к GPT-4, GPT-3 и Bing AI\n" \
                    "     • Вызови /gpt_help для большей информации\n" \
                    "2. Конвертировать голос ↔ текст\n" \
                    "     • Вызови /voice_text_help для большей информации\n" \
                    "3. Рассказать немного информации о тебе\n" \
                    "     • Вызови /user_info\n" \
                    "4. Сгенерировать русские слова из набора букв\n" \
                    "     • Вызови /gen_words_help для большей информации\n" \
                    "5. Помочь тебе установить наше приложение\n" \
                    "     • Вызови /get_app_help для большей информации\n" \
                    "6. Скачать и отправить тебе файл по ссылке\n" \
                    "     • Вызови /get_file_help для большей информации\n" \
                    "7. ...\n" \
                    "/commands для вызова этого текста."
    if text == "/start":
        # if not work_with_db(user_data_db, data_dir, "SELECT user_id FROM [name] where user_id = ?", (user_id,)):
        if not await work_with_db(f"{data_dir}/{user_data_db}", "SELECT user_id FROM [name] where user_id = ?",
                                  (user_id,)):
            # work_with_db(user_data_db, data_dir,
            #              "INSERT INTO [name] (user_id, fn, ln, start_in_Moscow) VALUES (?, ?, ?, ?)",
            #              (user_id, first_name, last_name, time_text))
            await work_with_db(f"{data_dir}/{user_data_db}",
                               "INSERT INTO [name] (user_id, fn, ln, start_in_Moscow) VALUES (?, ?, ?, ?)",
                               (user_id, first_name, last_name, time_text))
        commands_text = "Привет, добро пожаловать в Zapzatron Bot.\n" + commands_text
    if text == "/commands" or text == "/start":
        # bot.send_message(chat_id, help_text, reply_markup=gen_markup(["/help"]))
        await bot.send_message(chat_id, commands_text)
    return commands_text


async def about_us(message):
    chat_id = message["chat_id"]
    text = message["text"]
    if text == "/about_us":
        user_id = message["user_id"]
        first_name = message["first_name"]
        last_name = message["last_name"]
        time_text = get_time()
        await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                           f"Id: {user_id} Fn: {first_name} "
                           f"Ln: {last_name} Do: {text}",
                      write_file=True,
                      logs_dir_=logs_dir)

    about_us_text = "Благодарим вас за использование нашего проекта!\n" \
                    "Канал → https://t.me/Zapzatron_Bot_Channel\n" \
                    "Чат → https://t.me/+NkT96igVJ180NTQy\n" \
                    "Почта поддержки → zapzatron.bot.help@gmail.com\n" \
                    "Для поддержки разработчика вызовите /donation"

    if text == "/about_us":
        await bot.send_message(chat_id, about_us_text, disable_web_page_preview=True)
    return about_us_text


async def donation(message):
    chat_id = message["chat_id"]
    user_id = message["user_id"]
    first_name = message["first_name"]
    last_name = message["last_name"]
    time_text = get_time()
    await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                       f"Id: {user_id} Fn: {first_name} "
                       f"Ln: {last_name} Do: {message['text']}",
                  write_file=True,
                  logs_dir_=logs_dir)
    markup = telebot.types.InlineKeyboardMarkup()
    button_text = "🍓 Поддержать разработчика 🍓"
    photo = open(f'{data_dir}/TipsQRCode.png', 'rb')
    url = "https://pay.cloudtips.ru/p/80c6b619"
    text = "На самом деле, GPT это платная технология\n" \
           "Также для работы бота требуется оплачивать хостинг.\n" \
           "А разработчик активно трудится для вас."
    markup.add(telebot.types.InlineKeyboardButton(text=button_text, url=url))
    await bot.send_photo(chat_id, photo, caption=text, reply_markup=markup)


async def gpt_help(message):
    chat_id = message["chat_id"]
    text = message["text"]
    if text == "/gpt_help":
        user_id = message["user_id"]
        first_name = message["first_name"]
        last_name = message["last_name"]
        time_text = get_time()
        await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                           f"Id: {user_id} Fn: {first_name} "
                           f"Ln: {last_name} Do: {text}",
                      write_file=True,
                      logs_dir_=logs_dir)
    gpt_help_text = "Что сделать для доступа к GPT?:\n" \
                    "1. Вызови /gpt4 или /gpt3 или /bing\n" \
                    "2. Отправь вопрос в чат\n" \
                    "3. Для очистки контекста вызови тоже самое, что и в 1 пункте\n" \
                    "Контекст сохраняет последнее сообщение. Хранится два часа\n" \
                    "/chat_mode отключает/меняет отправку лишних сообщений\n" \
                    "/gpt4 - GPT-4\n" \
                    "/gpt3 - GPT-3.5-turbo\n" \
                    "/bing - Bing AI\n" \
                    "/gpt_help для вызова этого текста."
    # print(text)
    if text == "/gpt_help":
        # bot.send_message(chat_id, gpt_help_text, reply_markup=gen_markup(["/drop_cache", "/gpt_help", "/help"]))
        await bot.send_message(chat_id, gpt_help_text)
    return gpt_help_text


async def gpt_openai(key, model, prompt, system_message_="", chat_context=None,
                     temperature=1.0, max_tokens=2000, max_context=20):
    # print(f"{key}")
    openai.api_key = key
    user_prompt = {"role": "user", "content": prompt}
    if chat_context is None:
        messages = [{"role": "system", "content": system_message_}, user_prompt]
    else:
        messages = [{"role": "system", "content": system_message_}, *chat_context, user_prompt]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    # print(response)
    content = response["choices"][0]["message"]["content"]
    # print(chat_context)
    # content = content.replace("**", "*")
    if not (chat_context is None):
        if len(chat_context) >= max_context:
            chat_context.pop(0)
            chat_context.pop(0)
        temp = content.replace("'", '"').replace("\n", "/nl").replace("\\", "/")
        chat_context.append(user_prompt)
        chat_context.append({"role": "assistant", "content": temp})
        return content, chat_context
    return content


async def gpt_mindsdb(prompt, model, chat_context=None, max_context=20):
    # print(chat_context)
    user_prompt = {"role": "user", "content": prompt}
    question, context = prompt, ""
    if chat_context is None:
        pass
    else:
        for i in range(0, len(chat_context), 2):
            context = f"user: {chat_context[i]['content']} assistant: {chat_context[i + 1]['content']}"
    db_name = f"mindsdb.{model}"
    sql = f"SELECT response FROM {db_name} WHERE question='{question}' and context='{context}'"
    # chat = ''
    # # print(chat_context)
    # if chat_context is None:
    #     chat = prompt
    # else:
    #     # for i in range(0, len(chat_context), 2):
    #     #     chat += 'Сообщение пользователя: ' + chat_context[i]["content"] + '\n'
    #     #     chat += 'Твоё сообщение: ' + chat_context[i + 1]["content"] + '\n'
    #     #
    #     # chat += 'Сообщение пользователя: ' + prompt + '\n'
    #     for i in range(0, len(chat_context), 2):
    #         chat += 'user: ' + chat_context[i]["content"] + '\n'
    #         chat += 'assistant: ' + chat_context[i + 1]["content"] + '\n'
    #
    #     chat += 'user: ' + prompt + '\n'
    #
    # db_name = f"mindsdb.{model}"
    # # sql = f"SELECT response FROM mindsdb.{model} WHERE text='{chat}'"
    # sql = f"SELECT response FROM {db_name} WHERE text='{chat}'"
    # print("Before connection")
    # connection = pymysql.connect(host='cloud.mindsdb.com',
    #                              user=config.MINDSDB_USER,
    #                              password=config.MINDSDB_PASSWORD,
    #                              db='mindsdb',
    #                              charset='utf8mb4',
    #                              cursorclass=pymysql.cursors.DictCursor,
    #                              connect_timeout=30)
    # print("After connection")
    # cursor = connection.cursor()
    # cursor.execute(sql)
    # response = cursor.fetchone()
    # content = response['response']

    content = await work_with_db(db_name, sql, host="cloud.mindsdb.com",
                                 user=config.MINDSDB_USER, password=config.MINDSDB_PASSWORD)
    # print(content)
    # print(f"work_with_db():\n{content}")

    # loop = asyncio.get_event_loop()
    # pool = await aiomysql.create_pool(host='cloud.mindsdb.com',
    #                                   user=config.MINDSDB_USER, password=config.MINDSDB_PASSWORD,
    #                                   db='mindsdb', loop=loop)
    # # print(sql)
    # async with pool.acquire() as conn:
    #     async with conn.cursor() as cur:
    #         await cur.execute(sql)
    #         (content,) = await cur.fetchone()
    # pool.close()
    # await pool.wait_closed()

    # server = mindsdb_sdk.connect(login=config.MINDSDB_USER, password=config.MINDSDB_PASSWORD)
    # query = server.get_database('files').query(sql)
    # row = query.fetch()
    # content = row.iloc[0]['response']
    # content = content.replace("**", "*")
    if not (chat_context is None):
        if len(chat_context) >= max_context:
            chat_context.pop(0)
            chat_context.pop(0)
        # content = content.replace("'", '"').replace("\n", "/nl").replace("\\", "/")
        temp = content.replace("'", '"').replace("\n", "/nl").replace("\\", "/")
        chat_context.append(user_prompt)
        chat_context.append({"role": "assistant", "content": temp})
        return content, chat_context
    return content


gpt3_context = []


async def gpt3(message, command_name):
    global gpt3_context
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    text = message.text
    time_text = get_time()
    if not await is_spam(message, datetime.timedelta(seconds=timeout_messages), command_name):
        pass
    else:
        return
    try:
        if not is_chat_mode:
            await bot.reply_to(message, "Запрос отправлен на обработку, пожалуйста подождите.")
        # work_with_db(user_prompts_db, data_dir,
        #              "INSERT INTO user_prompts (user_id, fn, ln, text, time, command) VALUES (?, ?, ?, ?, ?, ?)",
        #              (user_id, first_name, last_name, text, time_text, command_name))
        await work_with_db(f"{data_dir}/{user_prompts_db}",
                           "INSERT INTO user_prompts (user_id, fn, ln, text, time, command) VALUES (?, ?, ?, ?, ?, ?)",
                           (user_id, first_name, last_name, text, time_text, command_name))
        text = text.replace("'", '"')
        text = text.replace("\n", "/nl")
        text = text.replace("\\", "/")
        mindsdb = False
        tokens = read_file("data/gpt-3.ini")
        model = "gpt-3.5-turbo"
        # system_message = "Ты GPT-3, большая языковая модель созданная OpenAI, отвечающая кратко точно по теме."
        system_message = "Answer briefly. If you don't know the answer, just say so. " \
                         "Answer in a markdown style. Knowledge cutoff: 2021 (year)."
        temperature = 0.5
        max_tokens = 2000
        max_context = 2
        if tokens[-1] == "":
            tokens.pop(-1)
        response_text = ""
        restart = True
        count = 0
        while restart:
            if count < len(tokens):
                try:
                    response_text, gpt3_context = await gpt_openai(tokens[count][:51], model, text, system_message,
                                                                   gpt3_context, temperature, max_tokens, max_context)
                    count += 1
                    restart = False
                except (openai.error.AuthenticationError, openai.error.RateLimitError):
                    bad_path = f"{data_dir}/bad_gpt3.ini"
                    if not os.path.exists(bad_path):
                        with open(bad_path, 'w') as file_w:
                            file_w.write("")

                    with open(bad_path, "r+") as bad_file:
                        bad_tokens = bad_file.read().split("\n")
                        line = tokens[count][:51]
                        if line not in bad_tokens:
                            bad_file.write(f"{line}\n")
                    tokens.pop(count)
                except openai.error.APIError:
                    extra_text = "Ошибка в предыдущем сообщении выведена, но система попробует ещё раз через 5 секунд."
                    # await handle_exception({"time_text": time_text, "id": user_id, "fn": first_name, "ln": last_name},
                    #                        extra_text)
                    await handle_exception({"time_text": time_text, "chat_id": chat_id, "id": user_id, "fn": first_name,
                                            "ln": last_name}, extra_text)
                    time.sleep(5)
            else:
                mindsdb = True
                break

        if mindsdb:
            try:
                response_text, gpt3_context = await gpt_mindsdb(text, "gpt3", gpt3_context, max_context)
            except (pymysql.err.ProgrammingError, pymysql.err.OperationalError,):
                response_text, gpt3_context = await gpt_mindsdb(text, "gpt3", gpt3_context, max_context)

        if len(response_text) < MAX_MESSAGE_LENGTH:
            try:
                await bot.reply_to(message, response_text, parse_mode='Markdown')
            except asyncio_helper.ApiTelegramException:
                # await bot.reply_to(message, formatting.escape_markdown(response_text), parse_mode='Markdown')
                await bot.reply_to(message, response_text)
        else:
            # await bot.send_document(chat_id, BytesIO(response_text.encode('utf-8')))
            await bot.send_document(chat_id, BufferedReader(CustomBytesIO(response_text.encode('utf-8'))))

        # while len(response_text) > 0:
        #     response_chunk = response_text[:MAX_MESSAGE_LENGTH]
        #     response_text = response_text[MAX_MESSAGE_LENGTH:]
        #     await bot.reply_to(message, response_chunk, parse_mode='Markdown')
        #     # await bot.reply_to(message, response_chunk)
    except Exception:
        gpt3_context = []
        # await handle_exception({"chat_id": chat_id, "time_text": time_text, "id": user_id, "fn": first_name, "ln": last_name})
        await handle_exception({"time_text": time_text, "chat_id": chat_id, "id": user_id,
                                "fn": first_name, "ln": last_name})
        # hot_cache_gpt3 = {}

        if not is_chat_mode:
            await bot.reply_to(message, f"При обработке запроса произошла ошибка. Пожалуйста, повторите попытку позже.")
        else:
            await bot.reply_to(message, f"Задай другой вопрос или спроси позже, не хочу общаться на эту тему сейчас.")


gpt4_context = []


async def gpt4(message, command_name):
    global gpt4_context
    # print(gpt4_context)
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    text = message.text
    time_text = get_time()
    if not await is_spam(message, datetime.timedelta(seconds=timeout_messages), command_name):
        pass
    else:
        return
    try:
        if not is_chat_mode:
            await bot.reply_to(message, "Запрос отправлен на обработку, пожалуйста подождите.")
        # work_with_db(user_prompts_db, data_dir,
        #              "INSERT INTO user_prompts (user_id, fn, ln, text, time, command) VALUES (?, ?, ?, ?, ?, ?)",
        #              (user_id, first_name, last_name, text, time_text, command_name))
        await work_with_db(f"{data_dir}/{user_prompts_db}",
                           "INSERT INTO user_prompts (user_id, fn, ln, text, time, command) VALUES (?, ?, ?, ?, ?, ?)",
                           (user_id, first_name, last_name, text, time_text, command_name))
        text = text.replace("'", '"')
        text = text.replace("\n", "/nl")
        text = text.replace("\\", "/")
        mindsdb = False
        tokens = read_file("data/gpt-4.ini")
        model = "gpt-4"
        # system_message = "Ты GPT-4, большая языковая модель созданная OpenAI, отвечающая кратко точно по теме."
        system_message = "Answer briefly. If you don't know the answer, just say so. " \
                         "Answer in a markdown style. Knowledge cutoff: 2021 (year)."
        temperature = 0.5
        max_tokens = 5500
        max_context = 2
        if tokens[-1] == "":
            tokens.pop(-1)
        response_text = ""
        restart = True
        count = 0
        # count = 99
        while restart:
            if count < len(tokens):
                try:
                    response_text, gpt4_context = await gpt_openai(tokens[count][:51], model, text, system_message,
                                                                   gpt4_context, temperature, max_tokens, max_context)
                    count += 1
                    # print(gpt4_context)
                    restart = False
                except (openai.error.AuthenticationError, openai.error.RateLimitError):
                    bad_path = f"{data_dir}/bad_gpt4.ini"
                    if not os.path.exists(bad_path):
                        with open(bad_path, 'w') as file_w:
                            file_w.write("")

                    with open(bad_path, "r+") as bad_file:
                        bad_tokens = bad_file.read().split("\n")
                        line = tokens[count][:51]
                        if line not in bad_tokens:
                            bad_file.write(f"{line}\n")
                    tokens.pop(count)
                except openai.error.APIError:
                    extra_text = "Ошибка в предыдущем сообщении выведена, но система попробует ещё раз через 5 секунд."
                    # await handle_exception({"time_text": time_text, "id": user_id, "fn": first_name, "ln": last_name},
                    #                        extra_text)
                    await handle_exception({"time_text": time_text, "chat_id": chat_id, "id": user_id,
                                            "fn": first_name, "ln": last_name}, extra_text)
                    time.sleep(5)
            else:
                mindsdb = True
                break

        # try:
        #     print(tokens[count])
        # except IndexError:
        #     pass
        # finally:
        #     print(f"Mindsdb: {mindsdb}")

        if mindsdb:
            try:
                response_text, gpt4_context = await gpt_mindsdb(text, "gpt4", gpt4_context, max_context)
            except (pymysql.err.ProgrammingError, pymysql.err.OperationalError,):
                response_text, gpt4_context = await gpt_mindsdb(text, "gpt4", gpt4_context, max_context)
        # print(spend_tokens, len(gpt4_context[-1]["content"]), len(gpt4_context[-2]["content"]))
        # spend_tokens = int(spend_tokens) + len(gpt4_context[-1]["content"]) + len(gpt4_context[-2]["content"])
        # print(spend_tokens)
        # remain_tokens = remain_tokens - spend_tokens
        # remain_tokens = int(remain_tokens)
        # work_with_db(user_data_db, data_dir,
        #              "UPDATE user_data SET spend_tokens = ?, remain_tokens = ? WHERE user_id = ? and model = ?;",
        #              (spend_tokens, remain_tokens, user_id, model))

        # print(response_text, mindsdb)

        if len(response_text) < MAX_MESSAGE_LENGTH:
            try:
                await bot.reply_to(message, response_text, parse_mode='Markdown')
            except asyncio_helper.ApiTelegramException:
                # await bot.reply_to(message, formatting.escape_markdown(response_text), parse_mode='Markdown')
                await bot.reply_to(message, response_text)
        else:
            # await bot.send_document(chat_id, BytesIO(response_text.encode('utf-8')))
            await bot.send_document(chat_id, BufferedReader(CustomBytesIO(response_text.encode('utf-8'))))
        # while len(response_text) > 0:
        #     response_chunk = response_text[:MAX_MESSAGE_LENGTH]
        #     response_text = response_text[MAX_MESSAGE_LENGTH:]
        #     await bot.reply_to(message, response_chunk, parse_mode='Markdown')
        #     # await bot.reply_to(message, response_chunk)
    except Exception:
        gpt4_context = []
        # await handle_exception({"time_text": time_text, "id": user_id, "fn": first_name, "ln": last_name})
        await handle_exception({"time_text": time_text, "chat_id": chat_id, "id": user_id,
                                "fn": first_name, "ln": last_name})

        if not is_chat_mode:
            await bot.reply_to(message, f"При обработке запроса произошла ошибка. Пожалуйста, повторите попытку позже.")
        else:
            await bot.reply_to(message, f"Задай другой вопрос или спроси позже, не хочу общаться на эту тему сейчас.")


async def bing_chat(prompt):
    cookies = json.loads(open(f"{data_dir}/cookies.json", encoding="utf-8").read())
    gbot = await Chatbot().create(cookies=cookies)
    # gbot = await Chatbot().create()
    # print(prompt)
    # response_dict = await gbot.ask(prompt=prompt, conversation_style=ConversationStyle.creative)
    response_dict = await gbot.ask(prompt=f"Ответ на вопрос давай в стиле Markdown. {prompt}",
                                   conversation_style=ConversationStyle.precise)
    await gbot.close()
    # print(response_dict)
    # print(response_dict['item']['messages'][1])
    content = re.sub(r'\[\^(\d)\^\]', "", response_dict['item']['messages'][1]['text'])
    content = content.replace(r"**", r"*")
    return content


bing_context = []


async def bing(message, command_name):
    # await bot.reply_to(message, "Временно не работает (Бинг блокирует работу)")
    # return
    global bing_context
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    text = message.text
    time_text = get_time()

    if not await is_spam(message, datetime.timedelta(seconds=timeout_messages), command_name):
        # bot.send_message(chat_id, "Кнопки снизу обновлены.",
        #                  reply_markup=gen_markup(["/help"]))
        pass
    else:
        return
    try:
        if not is_chat_mode:
            await bot.reply_to(message, "Запрос отправлен на обработку, пожалуйста подождите.")
        # work_with_db(user_prompts_db, data_dir,
        #              "INSERT INTO user_prompts (user_id, fn, ln, text, time, command) VALUES (?, ?, ?, ?, ?, ?)",
        #              (user_id, first_name, last_name, text, time_text, command_name))
        await work_with_db(f"{data_dir}/{user_prompts_db}",
                           "INSERT INTO user_prompts (user_id, fn, ln, text, time, command) VALUES (?, ?, ?, ?, ?, ?)",
                           (user_id, first_name, last_name, text, time_text, command_name))

        text = text.replace("'", '"')
        text = text.replace("\n", "/nl")
        text = text.replace("\\", "/")
        # response_text, bing_context = asyncio.run(bing_chat(text, bing_context, 2))
        response_text = await bing_chat(text)
        # print(response_text)
        if len(response_text) < MAX_MESSAGE_LENGTH:
            try:
                await bot.reply_to(message, response_text, parse_mode='Markdown')
            except asyncio_helper.ApiTelegramException:
                # await bot.reply_to(message, formatting.escape_markdown(response_text), parse_mode='Markdown')
                await bot.reply_to(message, response_text)
        else:
            # await bot.send_document(chat_id, BytesIO(response_text.encode('utf-8')))
            await bot.send_document(chat_id, BufferedReader(CustomBytesIO(response_text.encode('utf-8'))))
        # while len(response_text) > 0:
        #     response_chunk = response_text[:MAX_MESSAGE_LENGTH]
        #     response_text = response_text[MAX_MESSAGE_LENGTH:]
        #     await bot.reply_to(message, response_chunk, parse_mode='Markdown')
        #     # await bot.reply_to(message, response_chunk)
    except Exception as e:
        bing_context = []
        if str(e) != "'text'":
            # await handle_exception({"time_text": time_text, "id": user_id, "fn": first_name, "ln": last_name})
            await handle_exception({"time_text": time_text, "chat_id": chat_id, "id": user_id,
                                    "fn": first_name, "ln": last_name})

        if not is_chat_mode:
            await bot.reply_to(message, f"При обработке запроса произошла ошибка. Пожалуйста, повторите попытку позже."
                                        f"\nВозможно Bing AI не понравился ваш вопрос :) (Такой он)")
        else:
            await bot.reply_to(message, f"Задай другой вопрос или спроси позже, не хочу общаться на эту тему сейчас.")


async def voice_text_help(message):
    chat_id = message["chat_id"]
    text = message["text"]
    if text == "/voice_text_help":
        user_id = message["user_id"]
        first_name = message["first_name"]
        last_name = message["last_name"]
        time_text = get_time()
        await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                           f"Id: {user_id} Fn: {first_name} "
                           f"Ln: {last_name} Do: {text}",
                      write_file=True,
                      logs_dir_=logs_dir)
    voice_text_text = "Как конвертировать Голос → Текст?:\n" \
                      "1. Вызови /voice_to_text\n" \
                      "2. Отправь голосовое сообщение в чат\n" \
                      "3. Наслаждайся полученным текстом\n" \
                      "Ограничение: считываются первые 30 секунд\n" \
                      "Как конвертировать Текст → Голос?:\n" \
                      "1. Вызови /text_to_voice\n" \
                      "2. Отправь текстовое сообщение в чат\n" \
                      "3. Наслаждайся полученной озвучкой текста\n" \
                      "/voice_text_help для вызова этого текста."
    if text == "/voice_text_help":
        await bot.send_message(chat_id, voice_text_text)
    return voice_text_text


async def voice_to_text_hf(data, voice_to_text_model, api_token):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {api_token}"}
        api_url = f"https://api-inference.huggingface.co/models/{voice_to_text_model}"

        async with session.post(api_url, headers=headers, data=data) as response:
            response_content = await response.content.read()
            response_data = response_content.decode("utf-8")
            response_json = json.loads(response_data)
            return response_json


async def en_to_ru_hf(en_text, en_to_ru_model, api_token):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {api_token}"}
        api_url = f"https://api-inference.huggingface.co/models/{en_to_ru_model}"
        json_data = {"inputs": en_text, "options": {'wait_for_model': True}}
        async with session.post(api_url, headers=headers, json=json_data) as response:
            response_content = await response.content.read()
            response_data = response_content.decode("utf-8")
            # print(response_data)
            response_json = json.loads(response_data)
            return response_json


# whisper_model = whisper.load_model("base")


async def voice_to_text(message, command_name):
    # await bot.reply_to(message, "Временно недоступно из-за ограничений на хостинге\n(не хватает памяти)")
    # return
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    time_text = f"{get_time()}"
    await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                       f"Id: {user_id} Fn: {first_name} "
                       f"Ln: {last_name} Do: {command_name}",
                  write_file=True,
                  logs_dir_=logs_dir)
    try:
        await bot.reply_to(message, "Аудио принято")
        file_info = await bot.get_file(message.voice.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        voice_to_text_model = "openai/whisper-large-v2"
        restart = True
        num_restart = 10
        count = 0
        while restart:
            if count <= num_restart:
                count += 1
                response = await voice_to_text_hf(downloaded_file, voice_to_text_model, config.HUGGINGFACE_TOKEN)
                try:
                    if response["error"] == f"Model {voice_to_text_model} is currently loading":
                        print(response)
                        time_to_sleep = response['estimated_time'] * 1.5
                        print(f"Asleep for a while: {time_to_sleep} seconds")
                        time.sleep(time_to_sleep)
                        continue
                    elif response["error"] == f"Internal Server Error":
                        print(response)
                        time_to_sleep = 30
                        print(f"Asleep for a while: {time_to_sleep} seconds")
                        time.sleep(time_to_sleep)
                        continue
                except KeyError:
                    pass

                db_name = f"mindsdb.tr_en_ru"
                text = response["text"].strip().replace("'", '"')
                sql = f"SELECT response FROM {db_name} WHERE text='{text}'"
                # mindsdb = False
                en_to_ru_model = "Helsinki-NLP/opus-mt-en-ru"
                # print(f"EN: {text}")
                try:
                    response = await work_with_db(db_name, sql, host="cloud.mindsdb.com",
                                                  user=config.MINDSDB_USER, password=config.MINDSDB_PASSWORD)
                    # mindsdb = True
                    # print("mindsdb")
                except (pymysql.err.ProgrammingError, pymysql.err.OperationalError,):
                    response = await work_with_db(db_name, sql, host="cloud.mindsdb.com",
                                                  user=config.MINDSDB_USER, password=config.MINDSDB_PASSWORD)
                    # mindsdb = True
                    # print("mindsdb")
                except (pymysql.err.ProgrammingError, pymysql.err.OperationalError,):
                    response = (await en_to_ru_hf(text, en_to_ru_model, config.HUGGINGFACE_TOKEN))[0]['translation_text']
                    # print("Hugging Face")
                # finally:
                # if mindsdb:
                #     print(f"RU: {response}")
                #     await bot.reply_to(message, response)
                # else:
                #     # print(f"")
                #     await bot.reply_to(message, response["text"])
                # restart = False
                # print(f"RU: {response}")
                await bot.reply_to(message, "Отправка текста")
                await bot.reply_to(message, response)
                restart = False
            else:
                # print(f"Speech recognition isn`t available right now, try again later.")
                await bot.reply_to(message, "Распознавание речи сейчас недоступно, повторите попытку позже.")
    except Exception:
        # await handle_exception({"time_text": time_text, "id": user_id, "fn": first_name, "ln": last_name})
        await handle_exception({"time_text": time_text, "chat_id": chat_id, "id": user_id,
                                "fn": first_name, "ln": last_name})
        await bot.reply_to(message, f"При обработке запроса произошла ошибка. Пожалуйста, повторите попытку позже.")
    # print(file_info)
    # print("\n\n\n")
    # print(downloaded_file)
    return
    output_dir = f"temp/{user_id}/voice_text"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    try:
        with open(f"{output_dir}/voice_{user_id}.ogg", 'wb') as f:
            f.write(downloaded_file)

        await bot.reply_to(message, "Распознавание голоса")

        ffmpeg_path = ffdl.ffmpeg_dir
        if ffmpeg_path not in os.environ['PATH'].split(os.pathsep):
            os.environ['PATH'] += os.pathsep + ffmpeg_path

        result = whisper_model.transcribe(f"{output_dir}/voice_{user_id}.ogg", language="ru", fp16=False)

        text = result["text"].strip()
        # print(text)
        await bot.reply_to(message, "Проверка орфографии")
        text = f"Проверь следующее предложение как можно лучше на орфографию и пунктуацию, не пропуская слов, " \
               f"переделывая матерные слова в похожие по смыслу не матерные слова, " \
               f"и выведи только правильно составленное предложение: {text}"
        # print(text)
        try:
            response_text = await gpt_mindsdb(text, "gpt4")
        except (pymysql.err.ProgrammingError, pymysql.err.OperationalError,):
            response_text = await gpt_mindsdb(text, "gpt4")
        # print(response_text)
        await bot.reply_to(message, "Отправка текста")
        await bot.send_message(message.chat.id, response_text)
        os.remove(f"{output_dir}/voice_{user_id}.ogg")
    except Exception:
        # await handle_exception({"time_text": time_text, "id": user_id, "fn": first_name, "ln": last_name})
        await handle_exception({"time_text": time_text, "chat_id": chat_id, "id": user_id,
                                "fn": first_name, "ln": last_name})
        await bot.reply_to(message, f"При обработке запроса произошла ошибка. Пожалуйста, повторите попытку позже. \n")


async def text_to_voice(message, command_name):
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    time_text = f"{get_time()}"
    await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                       f"Id: {user_id} Fn: {first_name} "
                       f"Ln: {last_name} Do: {command_name}",
                  write_file=True,
                  logs_dir_=logs_dir)
    # output_dir = f"temp/{user_id}/voice_text"
    #
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)

    try:
        audio_data = BytesIO()
        gTTS(text=message.text, lang='ru').write_to_fp(audio_data)
        audio_data.seek(0)
        # gTTS(text=message.text, lang='ru').save(f"{output_dir}/voice_{user_id}.mp3")
        # await bot.send_audio(message.chat.id, open(f"{output_dir}/voice_{user_id}.mp3", 'rb'))
        await bot.send_audio(message.chat.id, audio_data)
        # os.remove(f"{output_dir}/voice_{user_id}.mp3")
    except Exception:
        # await handle_exception({"time_text": time_text, "id": user_id, "fn": first_name, "ln": last_name})
        await handle_exception({"time_text": time_text, "chat_id": chat_id, "id": user_id,
                                "fn": first_name, "ln": last_name})
        await bot.reply_to(message, f"При обработке запроса произошла ошибка. Пожалуйста, повторите попытку позже. \n")


async def user_info(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    raw_text = message.text
    time_text = f"{get_time()}"
    await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                       f"Id: {user_id} Fn: {first_name} "
                       f"Ln: {last_name} Do: {raw_text}",
                  write_file=True,
                  logs_dir_=logs_dir)
    await bot.reply_to(message, f"Я собрал немного информации о тебе:\n"
                                f"    • Id: {user_id}\n"
                                f"    • Ник: {username}\n"
                                f"    • Имя: {first_name}\n"
                                f"    • Фамилия: {last_name}\n"
                                f"    • Система: {platform.system()}")


async def gen_words_help(message):
    chat_id = message["chat_id"]
    text = message["text"]
    if text == "/gen_words_help":
        user_id = message["user_id"]
        first_name = message["first_name"]
        last_name = message["last_name"]
        time_text = f"{get_time()}"
        await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                           f"Id: {user_id} Fn: {first_name} "
                           f"Ln: {last_name} Do: {text}",
                      write_file=True,
                      logs_dir_=logs_dir)

    gen_words_help_text = "Как генерировать русские слова из набора букв?\n" \
                          "1. Вызови /gen_words_ru\n" \
                          "2. Отправь набор русских букв в чат\n" \
                          "3. Отправь нужное количество букв в словах\n" \
                          "Максимальное количество букв в словах 27\n" \
                          "/gen_words_help для вызова этого текста."
    if text == "/gen_words_help":
        await bot.send_message(chat_id, gen_words_help_text)
    return gen_words_help_text


gen_words_letters = ""
gen_words_length = 0


async def gen_words(message, command_name):
    global gen_words_letters
    global gen_words_length
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    text = message.text
    time_text = f"{get_time()}"
    await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                       f"Id: {user_id} Fn: {first_name} "
                       f"Ln: {last_name} Do: {command_name}",
                  write_file=True,
                  logs_dir_=logs_dir)
    if text != "" and text != " ":
        try:
            if 1 < int(text) <= 27:
                gen_words_length = int(text)
            elif int(text) > 27 or int(text) <= 1:
                await bot.reply_to(message, "Ошибка: Тебе нужно написать длину слов, которая меньше 27 и больше 1")
                return
        except ValueError:
            alphabet_ru = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
            text = text.lower()
            if isinstance(text, str) and len([e for e in text if e.lower() in alphabet_ru]) == len(
                    text) and text != "" and text != " ":
                gen_words_letters = text
                await bot.reply_to(message, "Отправь нужное количество букв в словах")
            elif not len([e for e in text if e.lower() in alphabet_ru]) == len(text) and text != "" and text != " ":
                await bot.reply_to(message, "Ошибка: Тебе нужно написать строку из русских букв")
                return

    if gen_words_length == 0:
        return

    with open(f'{data_dir}/russian_nouns_without_io.txt', encoding='utf8') as f1:
        result = [f"Слова из {gen_words_length} букв:"]
        count_words = 0
        line = ""
        while line != "-----":
            line = f1.readline()
            if "\n" in line:
                line = line[:-1]
            if len(line) == gen_words_length and line != "" and line != "-----":
                count = 0
                for letter in line:
                    if letter in gen_words_letters and line.count(letter) <= gen_words_letters.count(letter):
                        count += 1
                if count == gen_words_length and line not in result:
                    result.append(line)
        result_display = ""
        for line in result:
            if line[:8] != "Слова из":
                count_words += 1
                result_display += f"\n{count_words} слово: {line}"
            else:
                result_display = line

        result_display = f"Буквы: {gen_words_letters};   Длина: {gen_words_length}\n" + result_display \
                         + f"\nКоличество слов: {count_words}"
        await bot.reply_to(message, result_display)
    gen_words_length = 0


async def get_app_help(message):
    chat_id = message["chat_id"]
    text = message["text"]
    if text == "/get_app_help":
        user_id = message["user_id"]
        first_name = message["first_name"]
        last_name = message["last_name"]
        time_text = f"{get_time()}"
        await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                           f"Id: {user_id} Fn: {first_name} "
                           f"Ln: {last_name} Do: {text}",
                      write_file=True,
                      logs_dir_=logs_dir)

    get_app_help_text = "Что сделать для установки нашего приложения?\n" \
                        "1. Вызови /get_app\n" \
                        "2. Подожни немного\n" \
                        "3. Скачай полученный файл\n" \
                        "4. Распакуй его где-нибудь\n" \
                        "5. Запусти Update.bat\n" \
                        "6. Следуй инструкциям в установщике\n" \
                        "7. Запусти Zapzatron_GUI.lnk на рабочем столе\n" \
                        "8. Наслаждайся приложением :)\n" \
                        "Сейчас установщик и само приложение работает только на Windows.\n" \
                        "/get_app_help для вызова этого текста."
    if text == "/get_app_help":
        await bot.send_message(chat_id, get_app_help_text)
    return get_app_help_text


async def get_app(message):
    def clear_folder(path):
        if not os.path.exists(path):
            os.makedirs(path)
        file_list = os.listdir(path)
        for item in file_list:
            s = os.path.join(path, item)
            if os.path.isdir(s):
                try:
                    shutil.rmtree(s)
                except OSError:
                    pass
            else:
                os.remove(s)

    def get_zip(file, path_to, url):
        with open(f"{path_to}/{file}", "wb") as new_file:
            new_file.write(requests.get(url).content)
        time.sleep(1)

    def extract_zip(file, path_from, path_to):
        with zipfile.ZipFile(f"{path_from}/{file}", 'r') as zip_file:
            zip_file.extractall(path_to)
        time.sleep(5)

    def create_zip(zip_name, path_from, need_files_dirs=None):
        with zipfile.ZipFile(rf"{path_from}/{zip_name}", 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            for path in need_files_dirs:
                path = rf"{path_from}/{path}"
                if os.path.isfile(path):
                    split_path = path.split("/")
                    arc_path = ""
                    for p in split_path[split_path.index("GUI-master"):]:
                        if p == "GUI-master":
                            arc_path = f"{p[:-7]}Update"
                        else:
                            arc_path = rf"{arc_path}/{p}"

                    zipf.write(path, arc_path.strip("/"))
                elif os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            split_path = file_path.split("/")
                            arc_path = ""
                            for p in split_path[split_path.index("GUI-master"):]:
                                if p == "GUI-master":
                                    arc_path = f"{p[:-7]}Update"
                                else:
                                    arc_path = rf"{arc_path}/{p}"
                            zipf.write(file_path, arc_path.strip("/"))

    def delete_zip(file, from_path):
        try:
            os.remove(f"{from_path}/{file}")
            time.sleep(2)
        except OSError:
            pass

    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    time_text = f"{get_time()}"
    await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                       f"Id: {user_id} Fn: {first_name} "
                       f"Ln: {last_name} Do: {message.text}",
                  write_file=True,
                  logs_dir_=logs_dir)

    temp_path = rf"{os.getcwd()}/temp/{user_id}"

    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    await bot.reply_to(message, f"Подготовка файлов...")
    extract_path = rf"{temp_path}/GUI-master"

    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    zip_file = "Zapzatron_GUI.zip"
    need_files = ["Update.bat", "Update_2.0.bat", "Python3109", "Photos_or_Icons", "Update", "Update_2.0", "Fonts"]
    get_zip(zip_file, extract_path, "https://github.com/Zapzatron/GUI/archive/refs/heads/master.zip")
    extract_zip(zip_file, extract_path, temp_path)
    extract_zip("Python3109.zip", extract_path, extract_path)
    delete_zip(zip_file, extract_path)
    create_zip(zip_file, extract_path, need_files)
    await bot.reply_to(message, f"Отправляю установщик...")
    await bot.send_document(chat_id, open(rf'{extract_path}/Zapzatron_GUI.zip', 'rb'))
    time.sleep(5)
    clear_folder(extract_path)


async def get_file_help(message):
    chat_id = message["chat_id"]
    text = message["text"]
    if text == "/get_file_help":
        user_id = message["user_id"]
        first_name = message["first_name"]
        last_name = message["last_name"]
        time_text = f"{get_time()}"
        await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                           f"Id: {user_id} Fn: {first_name} "
                           f"Ln: {last_name} Do: {text}",
                      write_file=True,
                      logs_dir_=logs_dir)

    get_file_help_text = "Что сделать для установки файла по ссылке?\n" \
                         "1. Вызови /get_file\n" \
                         "2. Отправь ссылку на файл в чат\n" \
                         "3. Подожни немного\n" \
                         "4. Файл готов\n" \
                         "/get_file_help для вызова этого текста."
    if text == "/get_file_help":
        await bot.send_message(chat_id, get_file_help_text)
    return get_file_help_text


async def get_file(message, command_name):
    def clear_folder(path):
        if not os.path.exists(path):
            os.makedirs(path)
        file_list = os.listdir(path)
        for item in file_list:
            s = os.path.join(path, item)
            if os.path.isdir(s):
                try:
                    shutil.rmtree(s)
                except OSError:
                    pass
            else:
                os.remove(s)

    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    url = message.text.strip()
    time_text = f"{get_time()}"
    temp_path = rf"{os.getcwd()}/temp/{user_id}/files"
    await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                       f"Id: {user_id} Fn: {first_name} "
                       f"Ln: {last_name} Do: {command_name}",
                  write_file=True,
                  logs_dir_=logs_dir)

    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    file_name = os.path.basename(urlparse(url).path)
    try:
        with open(rf"{temp_path}/{file_name}", "wb") as new_file:
            new_file.write(requests.get(url).content)
    except requests.exceptions.MissingSchema:
        await bot.reply_to(message, "Возможно вы ввели неправильную ссылку, попробуйте ещё раз.")
        return
    time.sleep(2)
    await bot.send_document(chat_id, open(rf"{temp_path}/{file_name}", 'rb'))
    time.sleep(5)
    clear_folder(temp_path)


async def menu(message, first=True):
    buttons_list = ["GPT 🤖", "Голос ↔ Текст", "Генератор слов", "Приложение",
                    "Ссылка ⬇︎ Файл", "Команды 🔍", "О нас ℹ︎"]
    callback_list = ["/gpt_c", "/voice_text_c", "/gen_words_c", "/get_app_c",
                     "/get_file_c", "/commands_c", "/about_us_c"]
    markup = await gen_markup(buttons_list, buttons_dest="3", markup_type="Inline", callback_list=callback_list)
    button_text = "Выбери нужное"
    chat_id = message["chat_id"]
    user_id = message["user_id"]
    first_name = message["first_name"]
    last_name = message["last_name"]
    message_id = message["message_id"]
    if first:
        await logging(logs=f"[{get_time()}] Chat Id: {chat_id} "
                           f"Id: {user_id} Fn: {first_name} "
                           f"Ln: {last_name} Do: /menu",
                      write_file=True,
                      logs_dir_=logs_dir)
        await bot.send_message(chat_id, button_text, reply_markup=markup,
                               disable_web_page_preview=True)
    else:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=button_text, reply_markup=markup,
                                    disable_web_page_preview=True)


is_stop_bot = False


async def stop_bot(message):
    global is_stop_bot
    if message.from_user.id in config.ADMINS_LIST:
        chat_id = message.chat.id
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        raw_text = message.text
        time_text = f"{get_time()}"
        await logging(logs=f"[{time_text}] Chat Id: {chat_id} "
                           f"Id: {user_id} Fn: {first_name} "
                           f"Ln: {last_name} Do: {raw_text}",
                      write_file=True,
                      logs_dir_=logs_dir)
        await bot.reply_to(message, f"Останавливаю бота...")
        is_stop_bot = True
        if is_webhook:
            asyncio.run(bot.delete_webhook())
            asyncio.run(app.shutdown())
        asyncio.run(logging(logs=f"[{get_time()}] Бот выключен :(\n",
                            write_file=True,
                            logs_dir_=logs_dir))
        os.kill(os.getpid(), signal.SIGTERM)


#################################
#################################
is_production = False
is_webhook = False
#################################
#################################
is_production_auto_check = True
#################################
#################################


if is_production_auto_check and config.IS_PRODUCTION:
    is_production = True

# Считывание токена телеграм бота и создание его.
if is_production:
    is_webhook = True
    bot = AsyncTeleBot(config.TELEGRAM_BOT_TOKEN, exception_handler=ExceptionHandler())
    WEBHOOK_PATH = f"/bot/{config.TELEGRAM_BOT_TOKEN}"
else:
    # bot = AsyncTeleBot(config.TEST_TELEGRAM_BOT_TOKEN, exception_handler=ExceptionHandler(), parse_mode="Markdown")
    bot = AsyncTeleBot(config.TEST_TELEGRAM_BOT_TOKEN, exception_handler=ExceptionHandler())
    WEBHOOK_PATH = f"/bot/{config.TEST_TELEGRAM_BOT_TOKEN}"

if is_webhook:
    WEBHOOK_URL = f"{config.NGROK_TUNNEL_URL}{WEBHOOK_PATH}"
    app = web.Application()


async def handle(request):
    if str(request.message.url)[5:] == bot.token:
        update = telebot.types.Update.de_json(await request.json())
        # print("Send Update")
        # await bot.process_new_updates([update])
        asyncio.create_task(bot.process_new_updates([update]))
        # print("New Update")
        return web.Response()
    else:
        return web.Response(status=403)


if is_webhook:
    app.router.add_post(WEBHOOK_PATH, handle)

work_dir = os.getcwd()
data_dir = os.path.join(work_dir, "data")
logs_dir = os.path.join(work_dir, "logs")
temp_dir = os.path.join(work_dir, "temp")

asyncio.run(bot.set_my_commands([
    telebot.types.BotCommand("/menu", "Вызвать меню бота"),
    telebot.types.BotCommand("/gpt4", "GPT-4"),
    telebot.types.BotCommand("/gpt3", "GPT-3"),
    telebot.types.BotCommand("/bing", "Bing AI"),
    telebot.types.BotCommand("/chat_mode", "Отключает/меняет отправку лишних сообщений"),
    telebot.types.BotCommand("/voice_to_text", "Голос в текст"),
    telebot.types.BotCommand("/text_to_voice", "Текст в голос"),
]))

# Разрешённое время между сообщениями (в секундах)
timeout_messages = 10
# Включение и отключение чат мода (Отправлять ли уведомления, например, "Запрос отправлен")
is_chat_mode = False
# Словарь для проверки на спам
user_use_dict = {}
# Максимальная длина для сообщения телеграмм
MAX_MESSAGE_LENGTH = 4096
# Имя базы данных для запросов AI
context_db = "context.db"
# Имя базы данных для просмотра запросов пользователей
user_prompts_db = "user_prompts.db"
# Имя базы данных для информации о пользователях
user_data_db = "user_data.db"
user_state = {}

actions = ["/gpt4", "/gpt3", "/bing", "/voice_to_text", "/text_to_voice", "/gen_words_ru", "/get_file"]
actions_text = {
    "/gpt4": "Отправьте вопрос к GPT4 в чат",
    "/gpt3": "Отправьте вопрос к GPT3 в чат",
    "/bing": "Отправьте вопрос к Bing AI в чат",
    "/voice_to_text": "Отправьте голосовое сообщение в чат",
    "/text_to_voice": "Отправьте текстовое сообщение в чат",
    "/gen_words_ru": "Отправьте набор русских букв в чат",
    "/get_file": "Отправьте ссылку на файл в чат"
}
gpt_context_duration = datetime.timedelta(hours=2)

# work_with_db(context_db, data_dir,
#              '''CREATE TABLE IF NOT EXISTS [name]
#              (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, text TEXT, time DATETIME)''')

# work_with_db(user_prompts_db, data_dir,
#              '''CREATE TABLE IF NOT EXISTS [name]
#              (id INTEGER PRIMARY KEY AUTOINCREMENT, fn TEXT, ln TEXT, user_id INTEGER, text TEXT, time DATETIME, command TEXT)''')

asyncio.run(work_with_db(f"{data_dir}/{user_prompts_db}",
                         '''CREATE TABLE IF NOT EXISTS [name]
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, fn TEXT, ln TEXT, user_id INTEGER, text TEXT, time DATETIME, command TEXT)'''))

# work_with_db(user_data_db, data_dir,
#              '''CREATE TABLE IF NOT EXISTS [name]
#              (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, fn TEXT, ln TEXT, start_in_Moscow TEXT)''')

asyncio.run(work_with_db(f"{data_dir}/{user_data_db}",
                         '''CREATE TABLE IF NOT EXISTS [name]
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, fn TEXT, ln TEXT, start_in_Moscow TEXT)'''))


@bot.callback_query_handler(func=lambda message: True)
async def callback_buttons(message):
    async def button_message(message_, button_text_):
        # print(message_.message.message_id, message_.id)
        # chat_id = message_.message.chat.id
        chat_id = message_["chat_id"]
        # message_id = message_.message.message_id
        message_id = message_["message_id"]
        # bot.answer_callback_query(message_.id)
        await bot.answer_callback_query(message_["all_message_id"])
        buttons_list = ["Назад 🔙"]
        callback_list = ["/back_с"]
        markup = await gen_markup(buttons_list, markup_type="Inline", callback_list=callback_list)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=button_text_, reply_markup=markup,
                                    disable_web_page_preview=True)

    text = message.data

    message_2 = {"chat_id": message.message.chat.id,
                 "message_id": message.message.message_id,
                 "all_message_id": message.id,
                 "user_id": message.message.chat.id,
                 "first_name": message.message.chat.first_name,
                 "last_name": message.message.chat.last_name,
                 "text": text}

    # print(text)
    # print(message.message.chat.id)
    # print(message.message.message_id)

    if text == "/commands_c":
        await button_message(message_2, await commands(message_2))
    elif text == "/about_us_c":
        await button_message(message_2, await about_us(message_2))
    elif text == "/voice_text_c":
        await button_message(message_2, await voice_text_help(message_2))
    elif text == "/gpt_c":
        await button_message(message_2, await gpt_help(message_2))
    elif text == "/gen_words_c":
        await button_message(message_2, await gen_words_help(message_2))
    elif text == "/get_app_c":
        await button_message(message_2, await get_app_help(message_2))
    elif text == "/get_file_c":
        await button_message(message_2, await get_file_help(message_2))
    elif text == "/back_с":
        await bot.answer_callback_query(message.id)
        await menu(message_2, first=False)
    elif text == "/subscribe_ads_c":
        pass


@bot.message_handler(content_types=["text", "voice"])
async def get_command_text(message):
    global gpt4_context
    global gpt3_context
    global bing_context
    global is_chat_mode
    global timeout_messages
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    text = message.text
    cur_time = get_time(strp=True)
    # print(message)
    # print(text)
    if round(time.time()) - message.date > 1 * 60:  # 1 минута
        return

    message_2 = {"chat_id": chat_id,
                 "message_id": message.id,
                 "user_id": user_id,
                 "first_name": first_name,
                 "last_name": last_name,
                 "text": text}
    # print(text)
    if message.content_type == "text" and text != "/menu" and text != "/donation" and text != "/start":
        try:
            if (await bot.get_chat_member(config.TELEGRAM_ADS_CHANNEL, user_id)).status == "left":
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton("Подписаться", "https://t.me/Zapzatron_Bot_Ads"))
                await bot.send_message(chat_id, "Чтобы пользоваться ботом нужно подписаться на наш канал.",
                                       reply_markup=markup, disable_web_page_preview=False)
                return
        except asyncio_helper.ApiTelegramException as e:
            if e.result_json['description'] == 'Bad Request: user not found':
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton("Подписаться", "https://t.me/Zapzatron_Bot_Ads"))
                await bot.send_message(chat_id, "Чтобы пользоваться ботом нужно подписаться на наш канал.",
                                       reply_markup=markup, disable_web_page_preview=False)
                return
            asyncio.run(handle_exception())

    if message.content_type == "voice" and user_id in user_state and user_state[user_id][0] == "/voice_to_text":
        await voice_to_text(message, user_state[user_id][0])
    elif message.content_type == "text" and text == "/menu":
        await menu(message_2)
    elif message.content_type == "text" and text[0] == "/" and text in actions:
        user_state[user_id] = (text, None)
        if text in actions_text:
            await bot.reply_to(message, actions_text[text])
        if text == "/gpt4":
            gpt4_context = []
        elif text == "/gpt3":
            gpt3_context = []
        elif text == "/bing":
            bing_context = []
    elif message.content_type == "text" and text[0] == "/" and text not in actions:
        if text == "/commands" or text == "/start":
            await commands(message_2)
        elif text == "/about_us":
            await about_us(message_2)
        elif text == "/donation":
            await donation(message_2)
        elif text == "/gpt_help":
            await gpt_help(message_2)
        elif text == "/voice_text_help":
            await voice_text_help(message_2)
        elif text == "/gen_words_help":
            await gen_words_help(message_2)
        elif text == "/get_app_help":
            await get_app_help(message_2)
        elif text == "/get_file_help":
            await get_file_help(message_2)
        elif text == "/get_app":
            await get_app(message)
        elif text == "/user_info":
            await user_info(message)
        elif text == "/chat_mode":
            is_chat_mode = not is_chat_mode
            timeout_messages = 1
            if is_chat_mode:
                await bot.reply_to(message, "Чат мод активирован")
            else:
                await bot.reply_to(message, "Чат мод деактивирован")
        elif text == "/stop_bot":
            await stop_bot(message)
    elif message.content_type == "text" and text[0] != "/":
        if user_id in user_state:
            if user_state[user_id][0] == "/gpt4":
                if user_state[user_id][1] and cur_time - user_state[user_id][1] > gpt_context_duration:
                    await bot.reply_to(message, "Начинаю новый диалог из-за долгого перерыва")
                    gpt4_context = []
                await gpt4(message, user_state[user_id][0])
                user_state[user_id] = (user_state[user_id][0], cur_time)
            elif user_state[user_id][0] == "/gpt3":
                if user_state[user_id][1] and cur_time - user_state[user_id][1] > gpt_context_duration:
                    await bot.reply_to(message, "Начинаю новый диалог из-за долгого перерыва")
                    gpt3_context = []
                await gpt3(message, user_state[user_id][0])
                user_state[user_id] = (user_state[user_id][0], cur_time)
            elif user_state[user_id][0] == "/bing":
                if user_state[user_id][1] and cur_time - user_state[user_id][1] > gpt_context_duration:
                    await bot.reply_to(message, "Начинаю новый диалог из-за долгого перерыва")
                    bing_context = []
                await bing(message, user_state[user_id][0])
                user_state[user_id] = (user_state[user_id][0], cur_time)
            elif user_state[user_id][0] == "/text_to_voice":
                await text_to_voice(message, user_state[user_id][0])
            elif user_state[user_id][0] == "/gen_words_ru":
                await gen_words(message, user_state[user_id][0])
            elif user_state[user_id][0] == "/get_file":
                await get_file(message, user_state[user_id][0])
    # print(user_state)


# atexit.register(close_db)


async def run_info():
    start_time = get_time()
    await logging(logs=f"[{start_time}] Бот включён :)",
                  write_file=True,
                  logs_dir_=logs_dir)
    await logging(logs=f"Информация:\n"
                       f"  • Хостинг: {is_production}\n"
                       f"  • WebHook: {is_webhook}\n"
                       f"  • Время: {start_time}\n"
                       f"  • Система: {platform.system()}\n"
                       f"  • Рабочая директория: {work_dir}\n"
                       f"  • Папка с данными: {data_dir}\n"
                       f"  • Папка с логами: {logs_dir}",
                  write_file=True,
                  logs_file_name=start_time[0:10],
                  logs_dir_=logs_dir)


async def run_webhook():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="127.0.0.1", port=8443)
    await site.start()


def shutdown(signum, frame):
    asyncio.run(logging(logs=f"[{get_time()}] Бот выключен :(\n",
                        write_file=True,
                        logs_dir_=logs_dir))
    if is_webhook:
        asyncio.run(bot.delete_webhook())
    os.kill(os.getpid(), signal.SIGTERM)


signal.signal(signal.SIGINT, shutdown)


if __name__ == "__main__":
    while True:
        try:
            if is_stop_bot:
                asyncio.run(logging(logs=f"[{get_time()}] Бот выключен :(\n",
                                    write_file=True,
                                    logs_dir_=logs_dir))
                break
            asyncio.run(run_info())
            # asyncio_helper.proxy = {"http": "157.245.27.9:3128"}
            if is_webhook:
                loop = asyncio.new_event_loop()
                loop.create_task(run_webhook())
                loop.run_forever()
            else:
                asyncio.run(bot.polling())
        except Exception:
            asyncio.run(handle_exception())
