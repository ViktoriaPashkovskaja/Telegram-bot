import logging
import os
import time
import requests
import telegram

from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = telegram.Bot(token=TELEGRAM_TOKEN)
url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    'my_logger.log',
    maxBytes=50000000,
    backupCount=5
)
logger.addHandler(handler)


def parse_homework_status(homework):
    if homework is None:
        error = 'Данных нет'
        logging.error(error)
        return error
    else:
        homework_name = homework.get('homework_name')
        if homework_name is None:
            error = 'Данных нет'
            logging.error(error)
            return error
        status = homework.get('status')
        status_homework = {
            'reviewing': 'Работа в данный момент находится на ревью.',
            'approved': 'Ревьюеру всё понравилось, работа зачтена!',
            'rejected': 'К сожалению, в работе нашлись ошибки.'
        }
        verdict = status_homework[status]
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    current_timestamp = current_timestamp or int(time.time())
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            url, headers=headers, params=params)
        return homework_statuses.json()
    except requests.exceptions.RequestException as e:
        logging.exception(f'Бот упал с ошибкой: {e}')
        bot.send_message(chat_id=CHAT_ID, text=logging.exception)


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            homeworks = get_homeworks(current_timestamp)
            homework = homeworks['homeworks'][0]
            status_message = parse_homework_status(homework)
            send_message(status_message)
            time.sleep(5 * 60)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            site_error = f'Ошибка на API - json():{e}.'
            logging.error(site_error)
            return bot.send_message(site_error)


if __name__ == '__main__':
    main()
