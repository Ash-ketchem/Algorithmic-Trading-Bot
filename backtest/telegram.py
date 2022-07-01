import requests
from time import sleep

class TeleBot:
    def __init__(self):
        self.bot_token = "BOT TOKEN"
        self.chat_id = "CHAT ID" # trading 2 grp
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage?"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
            }
        )

    def send_msg(self, message):
        url = f"{self.base_url}chat_id={self.chat_id}&text={message}"
        sleep(15) # some delay for rate-limit problems
        res = self.session.get(url)
        if res.ok:
            return True
        else:
            return False
