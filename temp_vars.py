API_ID = 123
API_HASH = 'abcd'
BASE_URL = 'https://arbuz.betty.games/api'
ENC_KEY = 'click-secret'
LOG_LEVEL = 'DEBUG'

CLICKS_AMOUNT = [5, 160]  # Кол-во кликов (от X до Y)
CLICKS_SLEEP = [8, 25]  # Сон между кликами (от X до Y)
UPDATE_FREQ = 30  # Частота обновления данных профиля
UPDATE_VAR = 4  # Разброс по частоте обновления данных профиля

BUY_MAX_LVL = 1000  # Максимальный уровень улучшения. -1 в этой переменной отключает улучшения
BUY_CLICK = True  # Покупать/Улучшать клики
BUY_MINER = False  # Покупать/Улучшать майнер
BUY_ENERGY = True


# TODO: выписывание чеков, сбор статистики
'''Для автоматизации можно использовать этот код:
client = pyrogram.Client('test',api_id,api_hash)

Подключаемся к серверам
client.connect()

Отправляем код для входа
sCode = client.send_code(phone)
code = input('Enter auth code: ')

Логинимся 
client.sign_in(phone,sCode.phone_code_hash,code)'''
