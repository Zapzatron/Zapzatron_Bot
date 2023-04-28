"""
:license: MIT License
:copyright: (c) 2023 Zapzatron
"""


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
from fp.fp import FreeProxy
import openai
import pytz as ptz
import requests
import telebot
import traceback


def read_file(file_name, split_symbol="\n"):
    with open(file_name, 'r') as file:
        return file.read().split(split_symbol)


def logging(logs: str, print_logs: bool = True, write_file: bool = False,
            logs_file_name: str = None, logs_dir: str = "logs"):
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

        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        if logs_file_name is None:
            logs_file_name = f"{logs_dir}/{logs[1:11]}.txt"
        else:
            logs_file_name = f"{logs_dir}/{logs_file_name}.txt"

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
    if "KeyboardInterrupt" in error:
        print(error[-2:])
    if message:
        logging(logs=f"\033[31m[{message['time_text']}] "
                     f"Id: {message['id']} Fn: {message['fn']} "
                     f"Ln: {message['ln']} Ошибка: \n{error}\033[0m",
                write_file=True,
                logs_dir=logs_dir)
    else:
        logging(logs=f"\033[31m[{get_time()}] Ошибка: \n{error}\033[0m",
                write_file=True,
                logs_dir=logs_dir)
    print("-" * 120)


def get_proxy(url_to_check='http://icanhazip.com'):
    proxies = {}
    proxy = FreeProxy(country_id=['US', 'BR'], rand=True).get().strip()
    if proxy[:4] == "http":
        proxies = {"http": proxy}
    elif proxy[:5] == "https":
        proxies = {"https": proxy}
    response = requests.get(url_to_check, proxies=proxies)
    if response.status_code == 200:
        logging(logs=f"[{get_time()}] Прокси найден: {proxy}",
                write_file=True,
                logs_dir=logs_dir)
        return proxies
    else:
        logging(logs=f"\033[31m[{get_time()}] Прокси нерабочий ({response.status_code}): {proxy}\033[0m",
                write_file=True,
                logs_dir=logs_dir)
        get_proxy()


class ExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        handle_exception()
        return True


start_time = get_time()
work_dir = os.getcwd()
data_dir = os.path.join(work_dir, "data")
logs_dir = os.path.join(work_dir, "logs")

logging(logs=f"[{start_time}] Бот включён :)",
        write_file=True,
        logs_dir=logs_dir)
logging(logs=f"Информация:\n"
             f"  • Время: {start_time}\n"
             f"  • Система: {platform.system()}\n"
             f"  • Рабочая директория: {work_dir}\n"
             f"  • Папка с данными: {data_dir}\n"
             f"  • Папка с логами: {logs_dir}",
        write_file=True,
        logs_file_name=start_time[0:10],
        logs_dir=logs_dir)

# Считывание OpenAI токена
openai.api_key = read_file(f'{data_dir}/tokens.ini')[1][9:]
# Считывание токена телеграм бота и создание его.
bot = telebot.TeleBot(read_file(f'{data_dir}/tokens.ini')[0][10:],
                      exception_handler=ExceptionHandler())
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
HOT_CACHE_DURATION = datetime.timedelta(minutes=10)
# Имя базы данных для запросов AI
context_db = "context.db"


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
                logs_dir=logs_dir)
    else:
        success_comm_time = user_use_dict[userid_comm]
        dif_time_use = time_text_strp - success_comm_time
        if dif_time_use > use_interval:
            user_use_dict[userid_comm] = time_text_strp
            logging(logs=f"[{time_text}] "
                         f"Id: {user_id} Fn: {first_name} "
                         f"Ln: {last_name} Do: {command_name}",
                    write_file=True,
                    logs_dir=logs_dir)
            return False
        else:
            bot.reply_to(message, f"Можно использовать через {use_interval - dif_time_use}")
            logging(logs=f"[{time_text}] "
                         f"Id: {user_id} Fn: {first_name} "
                         f"Ln: {last_name} Do: Спам {command_name}",
                    write_file=True,
                    logs_dir=logs_dir)
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
                    logs_dir=logs_dir)
            bot.reply_to(message, f"У тебя нет доступа к этой команде.")

    return wrapper


def gen_markup(buttons_list, buttons_dest="auto"):
    if buttons_dest == "auto":
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for button in buttons_list:
            markup.add(button)
        return markup
    elif buttons_dest == "3":
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        count = 0
        for i in range(len(buttons_list) // 3):
            markup.add(buttons_list[count], buttons_list[count + 1], buttons_list[count + 2])
            count += 3
        markup.add(buttons_list[-1])
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


@bot.message_handler(commands=['start', 'help'])
def help_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    raw_text = message.text
    time_text = f"{get_time()}"
    logging(logs=f"[{time_text}] "
                 f"Id: {user_id} Fn: {first_name} "
                 f"Ln: {last_name} Do: {raw_text}",
            write_file=True,
            logs_dir=logs_dir)

    help_text = "Привет, добро пожаловать в Zapzatron Bot.\n" \
                "Что я могу делать?\n" \
                "1. Я могу отправлять запросы в OpenAI API\n" \
                "     • Вызови /gpt_help для большей информации\n" \
                "2. Я могу рассказать немного информации о тебе\n" \
                "     • Вызови /user_info\n" \
                "3. Я могу сгенерировать русские слова из набора букв\n" \
                "     • Вызови /gen_words_help для большей информации\n" \
                "4. Я могу помочь тебе установить наше приложение\n" \
                "     • Вызови /get_app_help для большей информации\n" \
                "5. Я могу скачать и отправить тебе файл по ссылке\n" \
                "     • Вызови /get_file_help для большей информации\n" \
                "6. ..."
    bot.send_message(chat_id, help_text, reply_markup=gen_markup(["/help"]))


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
                logs_dir=logs_dir)

    work_with_db(context_db, data_dir, "DELETE FROM [name] WHERE user_id=?",
                 (user_id,))
    try:
        del hot_cache[user_id]
    except KeyError:
        pass

    bot.send_message(user_id, "Подожди 5 секунд пожалуйста.")
    time.sleep(5)
    bot.send_message(user_id, "Кэш очищен")


@bot.message_handler(commands=['gpt_help'])
def gpt_help(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    raw_text = message.text
    time_text = f"{get_time()}"
    logging(logs=f"[{time_text}] "
                 f"Id: {user_id} Fn: {first_name} "
                 f"Ln: {last_name} Do: {raw_text}",
            write_file=True,
            logs_dir=logs_dir)
    gpt_help_text = "Привет, я твой умный помощник :)\n" \
                    "Ты можешь отправлять запросы в OpenAI API через меня.\n" \
                    "Напиши в чат 'GPT: <твой текст>'\n" \
                    "Например, 'GPT: Что такое солнце (кратко)?'\n" \
                    "Ты можешь использовать кнопки снизу.\n" \
                    "  • /drop_cache для очистки контекста.\n" \
                    "  • /gpt_help для вызова меня."
    bot.send_message(chat_id, gpt_help_text, reply_markup=gen_markup(["/drop_cache", "/gpt_help", "/help"]))


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
        #         logs_dir=logs_dir)

        handle_exception({"time_text": time_text, "id": user_id, "fn": first_name, "ln": last_name})
        bot.reply_to(message, f"При обработке запроса произошла ошибка. Пожалуйста, повторите попытку позже. \n")
        drop_cache(message)


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
            logs_dir=logs_dir)
    bot.reply_to(message, f"Я собрал немного информации о тебе:\n"
                          f"    • Id: {user_id}\n"
                          f"    • Ник: {username}\n"
                          f"    • Имя: {first_name}\n"
                          f"    • Фамилия: {last_name}\n"
                          f"    • Система: {platform.system()}")


@bot.message_handler(commands=['gen_words_help'])
def gen_words_help(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    raw_text = message.text
    time_text = f"{get_time()}"
    logging(logs=f"[{time_text}] "
                 f"Id: {user_id} Fn: {first_name} "
                 f"Ln: {last_name} Do: {raw_text}",
            write_file=True,
            logs_dir=logs_dir)

    gen_words_help_text = "Привет, я твой генератор русских слов :)\n" \
                          "Я могу генерировать русские слова из набора букв.\n" \
                          "Что тебе нужно сделать для этого?\n" \
                          "   • Напиши в чат 'Gen words: <набор букв>\n" \
                          "   • Напиши в чат 'Gen words: <длина слов>\n" \
                          "   • Ты можешь выбрать длину слов с помощью кнопок снизу.\n" \
                          "   • /gen_words_help для вызова меня."
    bot.send_message(chat_id, gen_words_help_text, reply_markup=gen_markup(["/gen_words_help", "/help"]))


gen_words_letters = ""
gen_words_length = 0


@bot.message_handler(func=lambda message: message.text[:11] == "Gen words: ")
def gen_words(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    raw_text = message.text
    text = raw_text[11:]
    time_text = f"{get_time()}"
    logging(logs=f"[{time_text}] "
                 f"Id: {user_id} Fn: {first_name} "
                 f"Ln: {last_name} Do: {raw_text[:9]}",
            write_file=True,
            logs_dir=logs_dir)
    global gen_words_letters
    global gen_words_length
    if text != "" and text != " ":
        try:
            if 1 < int(text) <= 27:
                gen_words_length = int(text)
            elif int(text) > 27 or int(text) <= 1:
                bot.send_message(chat_id, "Ошибка: Тебе нужно написать длину слов, которая меньше 27 и больше 1.",
                                 reply_markup=gen_markup(["Gen words: 3", "Gen words: 4", "Gen words: 5",
                                                          "Gen words: 6", "Gen words: 7", "Gen words: 8",
                                                          "/help"], buttons_dest="3"))
                return
        except ValueError:
            alphabet_ru = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
            text = text.lower()
            if isinstance(text, str) and not alphabet_ru.isdisjoint(text) and text != "" and text != " ":
                gen_words_letters = text
                bot.send_message(chat_id, "Выбери длину слов снизу или напиши сам.",
                                 reply_markup=gen_markup(["Gen words: 3", "Gen words: 4", "Gen words: 5",
                                                          "Gen words: 6", "Gen words: 7", "Gen words: 8",
                                                          "/help"], buttons_dest="3"))
            elif alphabet_ru.isdisjoint(text) and text != "" and text != " ":
                error_text = "Ошибка: Тебе нужно написать строку из русских букв."
                bot.send_message(chat_id, error_text, reply_markup=gen_markup(["/help"]))
                return

    if gen_words_length == 0:
        return
    bot.send_message(chat_id, f"Буквы: {gen_words_letters};   Длина: {gen_words_length}")

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
        result_display += f"\nКоличество слов: {count_words}"
        bot.send_message(chat_id, result_display)
    gen_words_length = 0


@bot.message_handler(commands=['get_app_help'])
def get_app_help(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    raw_text = message.text
    time_text = f"{get_time()}"
    logging(logs=f"[{time_text}] "
                 f"Id: {user_id} Fn: {first_name} "
                 f"Ln: {last_name} Do: {raw_text}",
            write_file=True,
            logs_dir=logs_dir)

    get_app_help_text = "Привет, Я твой помощник в установке нашего приложения :)\n" \
                        "Сейчас установщик работает только на Windows.\n" \
                        "Что тебе нужно сделать для установки?\n" \
                        "   • Вызови /get_app\n" \
                        "   • Подожни немного\n" \
                        "   • Скачай полученный файл\n" \
                        "   • Распакуй его где-нибудь\n" \
                        "   • Запусти Update.bat\n" \
                        "   • Следуй инструкциям в установщике\n" \
                        "   • Запусти Zapzatron_GUI.lnk на рабочем столе\n" \
                        "   • Наслаждайся приложением :)\n" \
                        "   • /get_app_help для вызова меня."
    bot.send_message(chat_id, get_app_help_text, reply_markup=gen_markup(["/get_app_help", "/help"]))


@bot.message_handler(commands=['get_app'])
def get_app(message):
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
    raw_text = message.text
    time_text = f"{get_time()}"
    logging(logs=f"[{time_text}] "
                 f"Id: {user_id} Fn: {first_name} "
                 f"Ln: {last_name} Do: {raw_text}",
            write_file=True,
            logs_dir=logs_dir)

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


@bot.message_handler(commands=['get_file_help'])
def get_file_help(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    raw_text = message.text
    time_text = f"{get_time()}"
    logging(logs=f"[{time_text}] "
                 f"Id: {user_id} Fn: {first_name} "
                 f"Ln: {last_name} Do: {raw_text}",
            write_file=True,
            logs_dir=logs_dir)

    get_file_help_text = "Привет, Я твой помощник в установке файла по ссылке :)\n" \
                         "Что тебе нужно сделать для установки?\n" \
                         "   • Напиши в чат 'Get file: <ссылка>\n" \
                         "   • Подожни немного\n" \
                         "   • Файл готов\n" \
                         "   • /get_file_help для вызова меня."
    bot.send_message(chat_id, get_file_help_text, reply_markup=gen_markup(["/get_file_help", "/help"]))


@bot.message_handler(func=lambda message: (message.text is not None) and ('/' != message.text[0]) and (message.text[:10] == "Get file: "))
def get_file(message):
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
    raw_text = message.text
    url = raw_text[10:]
    time_text = f"{get_time()}"
    temp_path = rf"{os.getcwd()}\temp\{user_id}\files"
    logging(logs=f"[{time_text}] "
                 f"Id: {user_id} Fn: {first_name} "
                 f"Ln: {last_name} Do: {raw_text[:9]}",
            write_file=True,
            logs_dir=logs_dir)

    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    file_name = os.path.basename(urlparse(url).path)
    with open(rf"{temp_path}\{file_name}", "wb") as new_file:
        new_file.write(requests.get(url).content)
    time.sleep(2)
    bot.send_document(chat_id, open(rf"{temp_path}\{file_name}", 'rb'))
    time.sleep(5)
    clear_folder(temp_path)


@bot.message_handler(func=lambda message: message.text is not None and '/' not in message.text)
def check_text_message(message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    message_text = message.text
    if message_text == "Привет" or message_text == "Здравствуйте":
        bot.reply_to(message, f"{message_text}, {first_name} {last_name}")
    elif message_text == "Как дела?" or message_text == "Как твои дела?":
        bot.reply_to(message, "Отлично, у тебя как?")


stop_bot = False


@bot.message_handler(commands=['stop_bot'])
def op_exit(message):
    if message.from_user.id == 850607480:
        global stop_bot
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        raw_text = message.text
        time_text = f"{get_time()}"
        logging(logs=f"[{time_text}] "
                     f"Id: {user_id} Fn: {first_name} "
                     f"Ln: {last_name} Do: {raw_text}",
                write_file=True,
                logs_dir=logs_dir)
        bot.reply_to(message, f"Останавливаю бота...")
        stop_bot = True
        bot.stop_polling()


atexit.register(close_db)


if __name__ == "__main__":
    while True:
        try:
            if stop_bot:
                logging(logs=f"[{get_time()}] Бот выключен :(\n",
                        write_file=True,
                        logs_dir=logs_dir)
                break
            apihelper.proxy = get_proxy("https://example.com/")
            bot.polling(logger_level=lg.NOTSET)
        except Exception:
            handle_exception()
