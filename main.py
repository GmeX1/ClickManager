from temp_vars import API_ID, API_HASH
from pyrogram import Client

client = Client('test_client', api_id=API_ID, api_hash=API_HASH)

client.start()
client.send_message('me', 'Test message!')
client.stop()
