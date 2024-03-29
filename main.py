from pyrogram import Client

# Убрал персональные данные, чтобы не светить их на гите
client = Client('test_client')

client.start()
client.send_message('me', 'test!')
client.stop()
