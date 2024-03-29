from Clicker import ClickerClient
from scripts import *


if __name__ == '__main__':
    asyncio.run(run_tasks())

# last_click = client.get_profile()['lastClickSeconds']
# print(client.click(last_click))
