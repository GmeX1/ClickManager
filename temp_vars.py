API_ID = 27416719
API_HASH = '55a6eb65e1563a8d709b3fb0f581d7d1'


'''Для автоматизации можно использовать этот код:
client = pyrogram.Client('test',api_id,api_hash)

Подключаемся к серверам
client.connect()

Отправляем код для входа
sCode = client.send_code(phone)
code = input('Enter auth code: ')

Логинимся 
client.sign_in(phone,sCode.phone_code_hash,code)'''
