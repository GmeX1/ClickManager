API_ID = 123
API_HASH = 'abcd'
BASE_URL = 'https://arbuz.betty.games/api'
ENC_KEY = 'click-secret'
LOG_LEVEL = 'DEBUG'

CLICKS_AMOUNT = [5, 160]
CLICKS_SLEEP = [8, 25]
UPDATE_FREQ = 15  # TODO: периодическое обновление данных о профиле


# TODO: Проксирование + TLSv1.3
'''Для автоматизации можно использовать этот код:
client = pyrogram.Client('test',api_id,api_hash)

Подключаемся к серверам
client.connect()

Отправляем код для входа
sCode = client.send_code(phone)
code = input('Enter auth code: ')

Логинимся 
client.sign_in(phone,sCode.phone_code_hash,code)'''
