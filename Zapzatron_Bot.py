"""
:license: MIT License
:copyright: (c) 2023 Zapzatron
"""
import Packages

packages = {
    "whisper": "openai-whisper==20230314",
    "telebot": "pyTelegramBotAPI==4.10.0",
    "ffmpeg": "ffmpeg",
    "pytz": "pytz==2022.7.1",
    "psutil": "psutil==5.9.4",
    "torch": "torch==1.11.0",
    "pydub": "pydub==0.25.1",
    "gtts": "gTTS==2.3.2",
    "requests": "requests",
}
print("-" * 27)
print("Checking required packages.")
Packages.check_req_packages(packages)
print("Required packages checked.")
print("-" * 27)

import atexit
import datetime
import os
import io
import platform
import shutil
import sqlite3
import threading
import time
import zipfile
import logging as lg
from datetime import datetime as dt
from telebot import apihelper
from urllib.parse import urlparse
from source.Free_Proxy.fp import FreeProxy
from dotenv import load_dotenv
import pymysql.cursors
import openai
from gtts import gTTS
import ffmpeg_downloader as ffdl
import whisper
import pytz as ptz
import requests
import telebot
import traceback


load_dotenv("data/.env")


def read_file(file_name, split_symbol="\n"):
    with open(file_name, 'r') as file:
        return file.read().split(split_symbol)


def logging(logs: str, print_logs: bool = True, write_file: bool = False,
            logs_file_name: str = None, logs_dir_: str = "logs"):
    if print_logs:
        print(logs, flush=True)

    if write_file:
        ansi_codes = {
            "color_off": "\033[0m",
            "red": "\033[31m"
        }
        for code in ansi_codes:
            if ansi_codes[code] in logs:
                logs = logs.replace(ansi_codes[code], "")

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


def get_time(tz: str = 'Europe/Moscow', form: str = '%d-%m-%Y %H:%M:%S', strp: bool = False):
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


def handle_exception(message=None):
    print("-" * 120)
    string_manager = io.StringIO()
    traceback.print_exc(file=string_manager)
    error = string_manager.getvalue()
    if message:
        logging(logs=f"\033[31m[{message['time_text']}] "
                     f"Id: {message['id']} Fn: {message['fn']} "
                     f"Ln: {message['ln']} Ошибка: \n{error}\033[0m",
                write_file=True,
                logs_dir_=logs_dir)
    else:
        logging(logs=f"\033[31m[{get_time()}] Ошибка: \n{error}\033[0m",
                write_file=True,
                logs_dir_=logs_dir)
    print("-" * 120)


last_proxy = ""


def get_proxy(last_proxy_, url_to_check='https://example.com/'):
    global last_proxy
    start = get_time(strp=True)
    proxies = {}
    country_list = ['FR', 'DE', 'US', 'CA', 'BR', 'AE', 'IN', 'TH', 'SG', 'HK', 'PH', 'VN']
    proxy, proxy_description = FreeProxy(country_id=country_list, https=True, site_to_check="example.com").get()
    # print(proxy, proxy_descripton[3].text_content())
    if proxy == last_proxy_ or proxy is None:
        return False
    last_proxy = proxy
    if proxy[:5] == "https":
        proxies = {"https": proxy}
    elif proxy[:4] == "http":
        proxies = {"http": proxy}

    response = requests.get(url_to_check, proxies=proxies)
    if response.status_code == 200:
        end = get_time(strp=True)
        logging(logs=f"[{get_time()}] Прокси: {proxy} Страна: {proxy_description[3].text_content()} Поиск длился: {end - start}",
                write_file=True,
                logs_dir_=logs_dir)
        return proxies
    else:
        logging(logs=f"\033[31m[{get_time()}] Прокси нерабочий ({response.status_code}): {proxy}\033[0m",
                write_file=True,
                logs_dir_=logs_dir)
        get_proxy(last_proxy)


class ExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        if str(exception)[-68:] == "query is too old and response timeout expired or query ID is invalid":
            return True
        print(exception)
        handle_exception()
        return True


start_time = get_time()
work_dir = os.getcwd()
data_dir = os.path.join(work_dir, "data")
logs_dir = os.path.join(work_dir, "logs")

logging(logs=f"[{start_time}] Бот включён :)",
        write_file=True,
        logs_dir_=logs_dir)
logging(logs=f"Информация:\n"
             f"  • Время: {start_time}\n"
             f"  • Система: {platform.system()}\n"
             f"  • Рабочая директория: {work_dir}\n"
             f"  • Папка с данными: {data_dir}\n"
             f"  • Папка с логами: {logs_dir}",
        write_file=True,
        logs_file_name=start_time[0:10],
        logs_dir_=logs_dir)

# Считывание OpenAI токена
openai.api_key = read_file(f'{data_dir}/tokens.ini')[1][9:]
# Считывание токена телеграм бота и создание его.
bot = telebot.TeleBot(os.environ["TELEGRAM_TOKEN"],
                      exception_handler=ExceptionHandler())
bot.set_my_commands([
    telebot.types.BotCommand("/menu", "Вызвать меню бота"),
    telebot.types.BotCommand("/help", "Помощь"),
    telebot.types.BotCommand("/gpt4", "GPT-4"),
    telebot.types.BotCommand("/gpt3", "GPT-3-turbo"),
    telebot.types.BotCommand("/voice_to_text", "Голос в текст"),
    telebot.types.BotCommand("/text_to_voice", "Текст в голос")
])
# Словарь для проверки на спам
user_use_dict = {}
# Считывание списка разрешённых пользователей (телеграмм id)
ALLOWED_USERS = read_file(f"{data_dir}/allowed_users.ini", ", ")
# Интервал 5 минут между проверками разрешённых пользователей
ALLOWED_USERS_CHECK_INTERVAL = datetime.timedelta(minutes=5)
# Время обновления списка разрешённых пользователей
ALLOWED_USERS_CHECK_TIME = get_time(strp=True)
# Выбор модели ИИ
MODELS_GPT = "text-davinci-003"
# Максимальная длина для сообщения телеграмм
MAX_MESSAGE_LENGTH = 4096
# Создание кэша для хранения контекста запроса
hot_cache = {}
# Время актуальности кэша
HOT_CACHE_DURATION = datetime.timedelta(minutes=30)
# Имя базы данных для запросов AI
context_db = "context.db"
# Имя базы данных для просмотра запросов пользователей
user_prompts_db = "user_prompts.db"
# Имя базы данных для информации о пользователях
user_data_db = "user_data.db"


def is_spam(message, use_interval: datetime.timedelta = datetime.timedelta(seconds=30), command_name=None):
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
        logging(logs=f"[{time_text}] "
                     f"Id: {user_id} Fn: {first_name} "
                     f"Ln: {last_name} Do: {command_name}",
                write_file=True,
                logs_dir_=logs_dir)
    else:
        success_comm_time = user_use_dict[userid_comm]
        dif_time_use = time_text_strp - success_comm_time
        if dif_time_use > use_interval:
            user_use_dict[userid_comm] = time_text_strp
            logging(logs=f"[{time_text}] "
                         f"Id: {user_id} Fn: {first_name} "
                         f"Ln: {last_name} Do: {command_name}",
                    write_file=True,
                    logs_dir_=logs_dir)
            return False
        else:
            bot.reply_to(message, f"Можно использовать через {use_interval - dif_time_use}")
            logging(logs=f"[{time_text}] "
                         f"Id: {user_id} Fn: {first_name} "
                         f"Ln: {last_name} Do: Спам {command_name}",
                    write_file=True,
                    logs_dir_=logs_dir)
            return True


def check_allowed_users():
    global ALLOWED_USERS_CHECK_TIME
    allowed_users_check_time_now = get_time(strp=True)
    if allowed_users_check_time_now - ALLOWED_USERS_CHECK_TIME > ALLOWED_USERS_CHECK_INTERVAL:
        global ALLOWED_USERS
        ALLOWED_USERS = read_file(f"{data_dir}/allowed_users.ini", ", ")
        ALLOWED_USERS_CHECK_TIME = get_time(strp=True)


def restricted_access(func):
    def wrapper(message):
        user_id = message.from_user.id
        check_allowed_users()
        if str(user_id) in ALLOWED_USERS:
            return func(message)
        else:
            logging(logs=f"[{get_time()}] "
                         f"Id: {message.from_user.id} Fn: {message.from_user.first_name} "
                         f"Ln: {message.from_user.last_name} Do: {'Отказано в доступе.'}",
                    write_file=True,
                    logs_dir_=logs_dir)
            bot.reply_to(message, f"У тебя нет доступа к этой команде.")

    return wrapper


def gen_markup(buttons_list, buttons_dest="auto", markup_type="Reply", callback_list=None):
    def sort_buttons(markup_, buttons, callback):
        count = 0
        n = len(buttons)
        while True:
            if n - 3 >= 0:
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
            elif n - 2 >= 0:
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
            elif n - 1 >= 0:
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
            markup = sort_buttons(markup, buttons_list, callback_list)
    elif markup_type == "Inline":
        markup = telebot.types.InlineKeyboardMarkup()
        if buttons_dest == "auto":
            for i in range(len(buttons_list)):
                markup.add(telebot.types.InlineKeyboardButton(buttons_list[i], callback_data=callback_list[i]))
        elif buttons_dest == "3":
            markup = sort_buttons(markup, buttons_list, callback_list)
    return markup


thread_local = threading.local()


def work_with_db(name, path, sql, parameters=None, fetch=1):
    prev_path = os.getcwd()
    os.chdir(path)

    if not hasattr(thread_local, "con"):
        thread_local.conn = sqlite3.connect(name)

    sql = sql.replace("[name]", name[:-3])
    con = thread_local.conn
    cur = con.cursor()
    if parameters:
        cur.execute(sql, parameters)
    else:
        cur.execute(sql)
    row = None
    if sql[:6] == "CREATE" or sql[:6] == "DELETE" or sql[:6] == "INSERT":
        con.commit()
    if sql[:6] == "SELECT":
        row = cur.fetchmany(fetch)
    os.chdir(prev_path)
    if row:
        return row


def close_db():
    con = getattr(thread_local, "con", None)
    if con is not None:
        con.close()


work_with_db(context_db, data_dir,
             '''CREATE TABLE IF NOT EXISTS [name]
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, text TEXT, time DATETIME)''')

work_with_db(user_prompts_db, data_dir,
             '''CREATE TABLE IF NOT EXISTS [name]
             (id INTEGER PRIMARY KEY AUTOINCREMENT, fn TEXT, ln TEXT, user_id INTEGER, text TEXT, time DATETIME, command TEXT)''')

# work_with_db(user_data_db, data_dir,
#              '''CREATE TABLE IF NOT EXISTS [name]
#              (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, fn TEXT, ln TEXT,  count_tokens TEXT)''')


def help_message(message):
    chat_id = message["chat_id"]
    text = message["text"]
    if text == "/help" or text == "/start":
        user_id = message["user_id"]
        first_name = message["first_name"]
        last_name = message["last_name"]
        time_text = f"{get_time()}"
        logging(logs=f"[{time_text}] "
                     f"Id: {user_id} Fn: {first_name} "
                     f"Ln: {last_name} Do: {text}",
                write_file=True,
                logs_dir_=logs_dir)

    help_text = "Для вызова меню бота используй /menu\n" \
                "Я могу помочь тебе в следующих действиях:\n" \
                "1. Предоставить доступ к GPT-4 и GPT-3.5-turbo\n" \
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
                "/help для вызова этого текста.\n" \
                "Тех поддержка - degget6564business@gmail.com"
    if text == "/start":
        help_text = "Привет, добро пожаловать в Zapzatron Bot.\n" + help_text
    if text == "/help" or text == "/start":
        # bot.send_message(chat_id, help_text, reply_markup=gen_markup(["/help"]))
        bot.send_message(chat_id, help_text)
    return help_text


@bot.message_handler(commands=['drop_cache'])
def drop_cache(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    raw_text = message.text
    time_text = f"{get_time()}"
    if raw_text == "/drop_cache":
        logging(logs=f"[{time_text}] "
                     f"Id: {user_id} Fn: {first_name} "
                     f"Ln: {last_name} Do: {raw_text}",
                write_file=True,
                logs_dir_=logs_dir)

    work_with_db(context_db, data_dir, "DELETE FROM [name] WHERE user_id=?",
                 (user_id,))
    try:
        del hot_cache[user_id]
    except KeyError:
        pass

    bot.send_message(user_id, "Подожди 5 секунд пожалуйста.")
    time.sleep(5)
    bot.send_message(user_id, "Кэш очищен")


def gpt_help(message):
    chat_id = message["chat_id"]
    text = message["text"]
    if text == "/gpt_help":
        user_id = message["user_id"]
        first_name = message["first_name"]
        last_name = message["last_name"]
        time_text = get_time()
        logging(logs=f"[{time_text}] "
                     f"Id: {user_id} Fn: {first_name} "
                     f"Ln: {last_name} Do: {text}",
                write_file=True,
                logs_dir_=logs_dir)
    gpt_help_text = "Что сделать для доступа к GPT?:\n" \
                    "1. Вызови /gpt4 (GPT-4) или /gpt3 (GPT-3.5-turbo)\n" \
                    "2. Отправь вопрос в чат\n" \
                    "3. Для очистки контекста вызови тоже самое, что и в 1 пункте\n" \
                    "Контекст сохраняет последнее сообщение\n" \
                    "/gpt_help для вызова этого текста."
    if text == "/gpt_help":
        # bot.send_message(chat_id, gpt_help_text, reply_markup=gen_markup(["/drop_cache", "/gpt_help", "/help"]))
        bot.send_message(chat_id, gpt_help_text)
    return gpt_help_text


@bot.message_handler(func=lambda message: message.text[:5] == "GPT: ")
@restricted_access
def gpt(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    raw_text = message.text
    text = raw_text[5:]
    time_text = get_time()
    time_text_strp = dt.strptime(time_text, '%d-%m-%Y %H:%M:%S')
    if not is_spam(message, datetime.timedelta(seconds=10), raw_text[:3]):
        bot.send_message(chat_id, "Кнопки снизу обновлены.",
                         reply_markup=gen_markup(["/drop_cache", "/gpt_help", "/help"]))
    else:
        return
    try:
        prev_text, prev_time = hot_cache.get(user_id, (None, None))
        if prev_text and prev_time:
            if time_text_strp - prev_time < HOT_CACHE_DURATION:
                prompt = prev_text + '\n' + text
                hot_cache[user_id] = (prompt, time_text_strp)
            else:
                prompt = text
                hot_cache[user_id] = (prompt, time_text_strp)
        else:
            row = work_with_db(context_db, data_dir,
                               "SELECT text, time FROM context WHERE user_id=? ORDER BY id DESC LIMIT 1", (user_id,))
            if not (row is None) and time_text_strp - dt.strptime(row[0][1], "%d-%m-%Y %H:%M:%S") < HOT_CACHE_DURATION:
                prompt = row[0][0] + '\n' + text if row[0][0] is not None else text
            else:
                prompt = text
            hot_cache[user_id] = (prompt, time_text_strp)

        bot.reply_to(message, "Запрос отправлен на обработку, пожалуйста подождите.")

        response = openai.Completion.create(
            model=MODELS_GPT,
            prompt=prompt,
            max_tokens=3800,
            temperature=0.2)

        response_text = response.choices[0].text

        while len(response_text) > 0:
            response_chunk = response_text[:MAX_MESSAGE_LENGTH]
            response_text = response_text[MAX_MESSAGE_LENGTH:]

            bot.reply_to(message, response_chunk)
        work_with_db(context_db, data_dir,
                     "INSERT INTO context (user_id, text, time) VALUES (?, ?, ?)", (user_id, text, time_text))

    except Exception:
        # logging(logs=f"[{time_text}] "
        #              f"Id: {user_id} Fn: {first_name} "
        #              f"Ln: {last_name} Ошибка: \n{traceback.print_exc()}",
        #         write_file=True,
        #         logs_dir_=logs_dir)

        handle_exception({"time_text": time_text, "id": user_id, "fn": first_name, "ln": last_name})
        bot.reply_to(message, f"При обработке запроса произошла ошибка. Пожалуйста, повторите попытку позже. \n")
        drop_cache(message)


def gpt_openai(key, model, prompt, system_message_="", chat_context=[],
               temperature=1.0, max_tokens=2000, max_context=20):
    openai.api_key = key
    user_prompt = {"role": "user", "content": prompt}
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message_},
            *chat_context,
            user_prompt,
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    # print(response)
    content = response["choices"][0]["message"]["content"]
    # print(chat_context)
    if len(chat_context) >= max_context:
        chat_context.pop(0)
        chat_context.pop(0)

    chat_context.append(user_prompt)
    chat_context.append({"role": "assistant", "content": content})
    return content, chat_context


def gpt_mindsdb(prompt, model, chat_context=[], max_context=20):
    user_prompt = {"role": "user", "content": prompt}
    chat = ''
    if chat_context:
        for i in range(0, len(chat_context), 2):
            chat += 'Сообщение пользователя: ' + chat_context[i]["content"] + '\n'
            chat += 'Твоё сообщение: ' + chat_context[i + 1]["content"] + '\n'

        chat += 'Сообщение пользователя: ' + prompt + '\n'
    else:
        chat = prompt

    sql = f"SELECT response FROM mindsdb.{model} WHERE text='{chat}'"

    connection = pymysql.connect(host='cloud.mindsdb.com',
                                 user=os.environ["MINDSDB_USER"],
                                 password=os.environ["MINDSDB_PASSWORD"],
                                 db='mindsdb',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(sql)
    response = cursor.fetchone()
    content = response['response']
    if chat_context:
        if len(chat_context) >= max_context:
            chat_context.pop(0)
            chat_context.pop(1)

        chat_context.append(user_prompt)
        chat_context.append({"role": "assistant", "content": content})
        return content, chat_context
    return content


# hot_cache_gpt3 = {}
gpt3_context = []


def gpt3(message, command_name):
    # global hot_cache_gpt3
    global gpt3_context
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    text = message.text
    time_text = get_time()
    # time_text_strp = dt.strptime(time_text, '%d-%m-%Y %H:%M:%S')
    if not is_spam(message, datetime.timedelta(seconds=10), command_name):
        # bot.send_message(chat_id, "Кнопки снизу обновлены.",
        #                  reply_markup=gen_markup(["/help"]))
        pass
    else:
        return
    try:
        # prev_text, prev_time, count = hot_cache_gpt3.get(user_id, (None, None, None))
        # if prev_text and prev_time and count:
        #     if time_text_strp - prev_time < HOT_CACHE_DURATION and count <= 10:
        #         text = prev_text + '\n' + text
        #
        # if count is None:
        #     count = 1
        # else:
        #     count += 1

        bot.reply_to(message, "Запрос отправлен на обработку, пожалуйста подождите.")
        work_with_db(user_prompts_db, data_dir,
                     "INSERT INTO user_prompts (user_id, fn, ln, text, time, command) VALUES (?, ?, ?, ?, ?, ?)",
                     (user_id, first_name, last_name, text, time_text, command_name))
        text = text.replace("'", '"')
        text = text.replace("\n", "/nl")
        text = text.replace("\\", "/")
        # hot_cache_gpt3[user_id] = (text, time_text_strp, count)
        # print(hot_cache_gpt3)
        mindsdb = False
        tokens = read_file("data/new_gpt-3.ini")
        model = "gpt-3.5-turbo"
        system_message = "Ты GPT-3, большая языковая модель созданная OpenAI, " \
                         "отвечающая точно по теме, а также как можно кратче."
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
                    response_text, gpt3_context = gpt_openai(tokens[count][:51], model, text, system_message,
                                                             gpt3_context, temperature, max_tokens, max_context)
                    count += 1
                    # print(gpt4_context)
                    restart = False
                except openai.error.AuthenticationError:
                    with open("bad_gpt3.ini", "w") as bad_file:
                        tokens = bad_file.read().split("\n")
                        line = tokens[count][:51]
                        if line not in tokens:
                            bad_file.write(f"{line}\n")
                    tokens.pop(count)
            else:
                mindsdb = True
                break
        if mindsdb:
            response_text, gpt3_context = gpt_mindsdb(text, "gpt3", gpt3_context)
        while len(response_text) > 0:
            response_chunk = response_text[:MAX_MESSAGE_LENGTH]
            response_text = response_text[MAX_MESSAGE_LENGTH:]
            bot.reply_to(message, response_chunk)
    except Exception:
        handle_exception({"time_text": time_text, "id": user_id, "fn": first_name, "ln": last_name})
        # hot_cache_gpt3 = {}
        bot.reply_to(message, f"При обработке запроса произошла ошибка. Пожалуйста, повторите попытку позже.")


# hot_cache_gpt4 = {}
gpt4_context = []


def gpt4(message, command_name):
    # global hot_cache_gpt4
    global gpt4_context
    # print(gpt4_context)
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    text = message.text
    time_text = get_time()
    # time_text_strp = dt.strptime(time_text, '%d-%m-%Y %H:%M:%S')
    if not is_spam(message, datetime.timedelta(seconds=10), command_name):
        # bot.send_message(chat_id, "Кнопки снизу обновлены.",
        #                  reply_markup=gen_markup(["/help"]))
        pass
    else:
        return
    try:
        # prev_text, prev_time, count = hot_cache_gpt4.get(user_id, (None, None, None))
        # # print(prev_text, prev_time, count)
        # if prev_text and prev_time and count:
        #     if time_text_strp - prev_time < HOT_CACHE_DURATION and count <= 10:
        #         text = prev_text + '\n' + text
        #
        # if count is None:
        #     count = 1
        # else:
        #     count += 1
        # print(hot_cache_gpt4)
        # if not gpt4_context:
            # gpt4_context = [{"role": "user", "content": "Hi", "time": "05.05.2023"}, {"role": "assistant", "content": "Hi", "time": "05.05.2023"}]
            # user_prompt = {"role": "user", "content": prompt, "time": <time>} Могу ли я отправлять контекст в таком виде? (Добавил "time")
            # temp = work_with_db(context_db, data_dir, "SELECT text, time FROM context WHERE user_id=? ORDER BY id DESC LIMIT 1", (user_id,))
            # print(temp)
            # gpt4_context
            # if not temp and time_text_strp - dt.strptime(temp[0][1], "%d-%m-%Y %H:%M:%S") < HOT_CACHE_DURATION:
            #     prompt = temp[0][0] + '\n' + text if row[0][0] is not None else text
            # else:
            #     prompt = text
            # hot_cache[user_id] = (prompt, time_text_strp)
            # pass
        bot.reply_to(message, "Запрос отправлен на обработку, пожалуйста подождите.")
        work_with_db(user_prompts_db, data_dir,
                     "INSERT INTO user_prompts (user_id, fn, ln, text, time, command) VALUES (?, ?, ?, ?, ?, ?)",
                     (user_id, first_name, last_name, text, time_text, command_name))
        text = text.replace("'", '"')
        text = text.replace("\n", "/nl")
        text = text.replace("\\", "/")
        # hot_cache_gpt4[user_id] = (text, time_text_strp, count)
        mindsdb = False
        tokens = read_file("data/new_gpt-4.ini")
        model = "gpt-4"
        system_message = "Ты GPT-4, большая языковая модель созданная OpenAI, " \
                         "отвечающая точно по теме, а также как можно кратче."
        temperature = 0.5
        max_tokens = 6500
        max_context = 2
        if tokens[-1] == "":
            tokens.pop(-1)
        response_text = ""
        restart = True
        count = 0
        while restart:
            if count < len(tokens):
                try:
                    response_text, gpt4_context = gpt_openai(tokens[count][:51], model, text, system_message,
                                                             gpt4_context, temperature, max_tokens, max_context)
                    count += 1
                    # print(gpt4_context)
                    restart = False
                except openai.error.AuthenticationError:
                    with open("bad_gpt4.ini", "w") as bad_file:
                        tokens = bad_file.read().split("\n")
                        line = tokens[count][:51]
                        if line not in tokens:
                            bad_file.write(f"{line}\n")
                    tokens.pop(count)
            else:
                mindsdb = True
                break
        if mindsdb:
            response_text, gpt4_context = gpt_mindsdb(text, "gpt4", gpt4_context)
        while len(response_text) > 0:
            response_chunk = response_text[:MAX_MESSAGE_LENGTH]
            response_text = response_text[MAX_MESSAGE_LENGTH:]
            bot.reply_to(message, response_chunk)
    except Exception:
        handle_exception({"time_text": time_text, "id": user_id, "fn": first_name, "ln": last_name})
        # hot_cache_gpt4 = {}
        bot.reply_to(message, f"При обработке запроса произошла ошибка. Пожалуйста, повторите попытку позже.")


def voice_text_help(message):
    chat_id = message["chat_id"]
    text = message["text"]
    if text == "/voice_text_help":
        user_id = message["user_id"]
        first_name = message["first_name"]
        last_name = message["last_name"]
        time_text = get_time()
        logging(logs=f"[{time_text}] "
                     f"Id: {user_id} Fn: {first_name} "
                     f"Ln: {last_name} Do: {text}",
                write_file=True,
                logs_dir_=logs_dir)
    voice_text_text = "Как конвертировать Голос → Текст?:\n" \
                      "1. Вызови /voice_to_text\n" \
                      "2. Отправь голосовое сообщение в чат\n" \
                      "3. Наслаждайся полученным текстом\n" \
                      "Как конвертировать Текст → Голос?:\n" \
                      "1. Вызови /text_to_voice\n" \
                      "2. Отправь текстовое сообщение в чат\n" \
                      "3. Наслаждайся полученной озвучкой текста\n" \
                      "/voice_text_help для вызова этого текста."
    if text == "/voice_text_help":
        bot.send_message(chat_id, voice_text_text)
    return voice_text_text


whisper_model = whisper.load_model("medium")


def voice_to_text(message, command_name):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    time_text = f"{get_time()}"
    logging(logs=f"[{time_text}] "
                 f"Id: {user_id} Fn: {first_name} "
                 f"Ln: {last_name} Do: {command_name}",
            write_file=True,
            logs_dir_=logs_dir)
    bot.reply_to(message, "Аудио принято")
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    output_dir = f"temp/{user_id}/voice_text"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    try:
        with open(f"{output_dir}/voice_{user_id}.ogg", 'wb') as f:
            f.write(downloaded_file)

        bot.reply_to(message, "Распознавание голоса")

        ffmpeg_path = ffdl.ffmpeg_dir
        if ffmpeg_path not in os.environ['PATH'].split(os.pathsep):
            os.environ['PATH'] += os.pathsep + ffmpeg_path

        result = whisper_model.transcribe(f"{output_dir}/voice_{user_id}.ogg", language="ru", fp16=False)

        text = result["text"].strip()
        # print(text)
        bot.reply_to(message, "Проверка орфографии")
        text = f"Проверь следующее предложение как можно лучше на орфографию и пунктуацию, не пропуская слов, " \
               f"переделывая матерные слова в похожие по смыслу не матерные слова, " \
               f"и выведи только правильно составленное предложение: {text}"
        response_text = gpt_mindsdb(text, "gpt4")
        bot.reply_to(message, "Отправка текста")
        bot.send_message(message.chat.id, response_text)
        os.remove(f"{output_dir}/voice_{user_id}.ogg")
    except Exception:
        handle_exception({"time_text": time_text, "id": user_id, "fn": first_name, "ln": last_name})
        bot.reply_to(message, f"При обработке запроса произошла ошибка. Пожалуйста, повторите попытку позже. \n")


def text_to_voice(message, command_name):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    time_text = f"{get_time()}"
    logging(logs=f"[{time_text}] "
                 f"Id: {user_id} Fn: {first_name} "
                 f"Ln: {last_name} Do: {command_name}",
            write_file=True,
            logs_dir_=logs_dir)
    output_dir = f"temp/{user_id}/voice_text"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        gTTS(text=message.text, lang='ru').save(f"{output_dir}/voice_{user_id}.mp3")
        bot.send_audio(message.chat.id, open(f"{output_dir}/voice_{user_id}.mp3", 'rb'))
        os.remove(f"{output_dir}/voice_{user_id}.mp3")
    except Exception:
        handle_exception({"time_text": time_text, "id": user_id, "fn": first_name, "ln": last_name})
        bot.reply_to(message, f"При обработке запроса произошла ошибка. Пожалуйста, повторите попытку позже. \n")


@bot.message_handler(commands=['user_info'])
def user_info(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    raw_text = message.text
    time_text = f"{get_time()}"
    logging(logs=f"[{time_text}] "
                 f"Id: {user_id} Fn: {first_name} "
                 f"Ln: {last_name} Do: {raw_text}",
            write_file=True,
            logs_dir_=logs_dir)
    bot.reply_to(message, f"Я собрал немного информации о тебе:\n"
                          f"    • Id: {user_id}\n"
                          f"    • Ник: {username}\n"
                          f"    • Имя: {first_name}\n"
                          f"    • Фамилия: {last_name}\n"
                          f"    • Система: {platform.system()}")


def gen_words_help(message):
    chat_id = message["chat_id"]
    text = message["text"]
    if text == "/gen_words_help":
        user_id = message["user_id"]
        first_name = message["first_name"]
        last_name = message["last_name"]
        time_text = f"{get_time()}"
        logging(logs=f"[{time_text}] "
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
        bot.send_message(chat_id, gen_words_help_text)
    return gen_words_help_text


gen_words_letters = ""
gen_words_length = 0


def gen_words(message, command_name):
    global gen_words_letters
    global gen_words_length
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    text = message.text
    time_text = f"{get_time()}"
    logging(logs=f"[{time_text}] "
                 f"Id: {user_id} Fn: {first_name} "
                 f"Ln: {last_name} Do: {command_name}",
            write_file=True,
            logs_dir_=logs_dir)
    if text != "" and text != " ":
        try:
            if 1 < int(text) <= 27:
                gen_words_length = int(text)
            elif int(text) > 27 or int(text) <= 1:
                bot.reply_to(message, "Ошибка: Тебе нужно написать длину слов, которая меньше 27 и больше 1")
                return
        except ValueError:
            alphabet_ru = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
            text = text.lower()
            if isinstance(text, str) and not alphabet_ru.isdisjoint(text) and text != "" and text != " ":
                gen_words_letters = text
                bot.reply_to(message, "Отправь нужное количество букв в словах")
            elif alphabet_ru.isdisjoint(text) and text != "" and text != " ":
                bot.reply_to(message, "Ошибка: Тебе нужно написать строку из русских букв")
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

        result_display = f"Буквы: {gen_words_letters};   Длина: {gen_words_length}\n" + result_display + f"\nКоличество слов: {count_words}"
        bot.reply_to(message, result_display)
    gen_words_length = 0


def get_app_help(message):
    chat_id = message["chat_id"]
    text = message["text"]
    if text == "/get_app_help":
        user_id = message["user_id"]
        first_name = message["first_name"]
        last_name = message["last_name"]
        time_text = f"{get_time()}"
        logging(logs=f"[{time_text}] "
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
        bot.send_message(chat_id, get_app_help_text)
    return get_app_help_text


def get_app(message, command_name):
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
        with zipfile.ZipFile(rf"{path_from}\{zip_name}", 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            for path in need_files_dirs:
                path = rf"{path_from}\{path}"
                if os.path.isfile(path):
                    split_path = path.split("\\")
                    arc_path = ""
                    for p in split_path[split_path.index("GUI-master"):]:
                        if p == "GUI-master":
                            arc_path = f"{p[:-7]}Update"
                        else:
                            arc_path = rf"{arc_path}\{p}"

                    zipf.write(path, arc_path.strip("\\"))
                elif os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            split_path = file_path.split("\\")
                            arc_path = ""
                            for p in split_path[split_path.index("GUI-master"):]:
                                if p == "GUI-master":
                                    arc_path = f"{p[:-7]}Update"
                                else:
                                    arc_path = rf"{arc_path}\{p}"
                            zipf.write(file_path, arc_path.strip("\\"))

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
    logging(logs=f"[{time_text}] "
                 f"Id: {user_id} Fn: {first_name} "
                 f"Ln: {last_name} Do: {command_name}",
            write_file=True,
            logs_dir_=logs_dir)

    temp_path = rf"{os.getcwd()}\temp\{user_id}"

    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    bot.reply_to(message, f"Подготовка файлов...")
    extract_path = rf"{temp_path}\GUI-master"

    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    zip_file = "Zapzatron_GUI.zip"
    need_files = ["Update.bat", "Update_2.0.bat", "Python3109", "Photos_or_Icons", "Update", "Update_2.0"]
    get_zip(zip_file, extract_path, "https://github.com/Zapzatron/GUI/archive/refs/heads/master.zip")
    extract_zip(zip_file, extract_path, temp_path)
    extract_zip("Python3109.zip", extract_path, extract_path)
    delete_zip(zip_file, extract_path)
    create_zip(zip_file, extract_path, need_files)
    bot.reply_to(message, f"Отправляю установщик...")
    bot.send_document(chat_id, open(rf'{extract_path}\Zapzatron_GUI.zip', 'rb'))
    time.sleep(5)
    clear_folder(extract_path)


def get_file_help(message):
    chat_id = message["chat_id"]
    text = message["text"]
    if text == "/get_file_help":
        user_id = message["user_id"]
        first_name = message["first_name"]
        last_name = message["last_name"]
        time_text = f"{get_time()}"
        logging(logs=f"[{time_text}] "
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
        bot.send_message(chat_id, get_file_help_text)
    return get_file_help_text


def get_file(message, command_name):
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
    temp_path = rf"{os.getcwd()}\temp\{user_id}\files"
    logging(logs=f"[{time_text}] "
                 f"Id: {user_id} Fn: {first_name} "
                 f"Ln: {last_name} Do: {command_name}",
            write_file=True,
            logs_dir_=logs_dir)

    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    file_name = os.path.basename(urlparse(url).path)
    with open(rf"{temp_path}\{file_name}", "wb") as new_file:
        new_file.write(requests.get(url).content)
    time.sleep(2)
    bot.send_document(chat_id, open(rf"{temp_path}\{file_name}", 'rb'))
    time.sleep(5)
    clear_folder(temp_path)


def menu(message, first=True):
    buttons_list = ["GPT 🤖", "Голос ↔ Текст", "Генератор слов", "Приложение", "Ссылка → Файл", "Помощь ❔"]
    callback_list = ["/gpt_c", "/voice_text_c", "/gen_words_c", "/get_app_c", "/get_file_c", "/help_c"]
    markup = gen_markup(buttons_list, buttons_dest="3", markup_type="Inline", callback_list=callback_list)
    button_text = "Выбери нужное"
    chat_id = message["chat_id"]
    user_id = message["user_id"]
    first_name = message["first_name"]
    last_name = message["last_name"]
    message_id = message["message_id"]
    if first:
        logging(logs=f"[{get_time()}] "
                     f"Id: {user_id} Fn: {first_name} "
                     f"Ln: {last_name} Do: /menu",
                write_file=True,
                logs_dir_=logs_dir)
        bot.send_message(chat_id, button_text, reply_markup=markup)
    else:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=button_text, reply_markup=markup)


@bot.callback_query_handler(func=lambda message: True)
def callback_buttons(message):
    def button_message(message_, button_text_):
        chat_id = message_.message.chat.id
        message_id = message_.message.message_id
        bot.answer_callback_query(message_.id)
        buttons_list = ["Назад 🔙"]
        callback_list = ["/back_с"]
        markup = gen_markup(buttons_list, markup_type="Inline", callback_list=callback_list)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=button_text_, reply_markup=markup)

    text = message.data

    message_2 = {"chat_id": message.message.chat.id,
                 "message_id": message.message.message_id,
                 "user_id": message.message.chat.id,
                 "first_name": message.message.chat.first_name,
                 "last_name": message.message.chat.last_name,
                 "text": text}

    # print(text)
    # print(message.message.chat.id)
    # print(message.message.message_id)

    if text == "/help_c":
        button_text = help_message(message_2)
        button_message(message, button_text)
    elif text == "/voice_text_c":
        button_message(message, voice_text_help(message_2))
    elif text == "/gpt_c":
        button_message(message, gpt_help(message_2))
    elif text == "/gen_words_c":
        button_message(message, gen_words_help(message_2))
    elif text == "/get_app_c":
        button_message(message, get_app_help(message_2))
    elif text == "/get_file_c":
        button_message(message, get_file_help(message_2))
    elif text == "/back_с":
        bot.answer_callback_query(message.id)
        menu(message_2, first=False)


@bot.message_handler(commands=['stop_bot'])
def stop_bot(message):
    global is_stop_bot
    if message.from_user.id == 850607480:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        raw_text = message.text
        time_text = f"{get_time()}"
        logging(logs=f"[{time_text}] "
                     f"Id: {user_id} Fn: {first_name} "
                     f"Ln: {last_name} Do: {raw_text}",
                write_file=True,
                logs_dir_=logs_dir)
        bot.reply_to(message, f"Останавливаю бота...")
        is_stop_bot = True
        bot.stop_polling()


user_state = {}
actions = ["/gpt4", "/gpt3", "/voice_to_text", "/text_to_voice", "/gen_words_ru", "/get_app", "/get_file"]
actions_text = {
    "/gpt4": "Отправьте вопрос к GPT4 в чат",
    "/gpt3": "Отправьте вопрос к GPT3 в чат",
    "/voice_to_text": "Отправьте голосовое сообщение в чат",
    "/text_to_voice": "Отправьте текстовое сообщение в чат",
    "/gen_words_ru": "Отправьте набор русских букв в чат",
    "/get_file": "Отправьте ссылку на файл в чат"
}


@bot.message_handler(content_types=["text", "voice"])
def get_command_text(message):
    user_id = message.from_user.id
    text = message.text
    # print(message)
    message_2 = {"chat_id": message.chat.id,
                 "message_id": message.id,
                 "user_id": user_id,
                 "first_name": message.from_user.first_name,
                 "last_name": message.from_user.last_name,
                 "text": text}
    # print(text)
    if message.content_type == "voice" and user_id in user_state and user_state[user_id] == "/voice_to_text":
        voice_to_text(message, user_state[user_id])
    elif message.content_type == "text" and text == "/menu":
        menu(message_2)
    elif message.content_type == "text" and text[0] == "/" and text in actions:
        user_state[user_id] = text
        if text in actions_text:
            bot.reply_to(message, actions_text[text])
        if text == "/gpt4":
            global gpt4_context
            gpt4_context = []
        elif text == "/gpt3":
            global gpt3_context
            gpt3_context = []
    elif message.content_type == "text" and text[0] == "/" and text not in actions:
        if text == "/help" or text == "/start":
            help_message(message_2)
        elif text == "/gpt_help":
            gpt_help(message_2)
        elif text == "/voice_text_help":
            voice_text_help(message_2)
        elif text == "/gen_words_help":
            gen_words_help(message_2)
        elif text == "/get_app_help":
            get_app_help(message_2)
        elif text == "/get_file_help":
            get_file_help(message_2)
    elif message.content_type == "text" and text[0] != "/":
        if user_id in user_state:
            if user_state[user_id] == "/gpt4":
                gpt4(message, user_state[user_id])
            elif user_state[user_id] == "/gpt3":
                gpt3(message, user_state[user_id])
            elif user_state[user_id] == "/text_to_voice":
                text_to_voice(message, user_state[user_id])
            elif user_state[user_id] == "/gen_words_ru":
                gen_words(message, user_state[user_id])
            elif user_state[user_id] == "/get_app":
                get_app(message, user_state[user_id])
            elif user_state[user_id] == "/get_file":
                get_file(message, user_state[user_id])
    # print(user_state)


is_stop_bot = False


def get_ip_info(proxies={}):
    try:
        response = requests.get("http://ip-api.com/json/", proxies=proxies)  # Получаем информацию об IP
        if response.status_code == 200:
            data = response.json()
            return data
    except Exception:
        handle_exception()
    return None


atexit.register(close_db)

if __name__ == "__main__":
    while True:
        try:
            if is_stop_bot:
                logging(logs=f"[{get_time()}] Бот выключен :(\n",
                        write_file=True,
                        logs_dir_=logs_dir)
                break
            country = get_ip_info()["country"]
            if not country or country == "Russia":
                proxy = get_proxy(last_proxy)
                if proxy:
                    apihelper.proxy = proxy
                else:
                    continue
            # apihelper.proxy = {"http": "34.95.207.20:3129"}
            apihelper.RETRY_ON_ERROR = True
            bot.polling(logger_level=lg.NOTSET)
        except Exception:
            handle_exception()
