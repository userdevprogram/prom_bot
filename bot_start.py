import json
import telebot
from auth_data import token


def telegram_bot():
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        file = open('bot_id.txt', 'rt')
        str_id = file.read()
        file.close()
        str_id = str_id + ' ' + str(message.chat.id)
        file = open('bot_id.txt', 'wt')
        file.write(str_id)
        file.close()
        bot.send_message(message.chat.id, "Telegram bot connected")

    bot.polling()


if __name__ == '__main__':
    telegram_bot()
