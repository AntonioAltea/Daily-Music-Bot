import datetime
import logging
import pysondb
import pytz
import os
from dotenv import load_dotenv
from spotify import getSpotifyLink
from telegram import Update
from telegram.ext import (ApplicationBuilder,
                          CallbackContext,
                          ContextTypes,
                          CommandHandler)


class DailyMusicBot:
    def __init__(self):
        load_dotenv()
        self.TELEGRAM_TOKEN = os.getenv("TELEGREM_TOKEN")
        self.USER_DATABASE = os.getenv("USER_DATABASE")
        self.userdb = pysondb.getDb(self.USER_DATABASE)

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

        self.application = ApplicationBuilder().token(self.TELEGRAM_TOKEN).build()

        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(
            CommandHandler('subscribe', self.subscribe))
        self.application.add_handler(
            CommandHandler('unsubscribe', self.unsubscribe))
        self.application.add_handler(CommandHandler('hello', self.hello))
        self.application.add_handler(CommandHandler('song', self.sendSong))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello! Use /subscribe to receive a daily song or /song to get one right now")

    async def subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id_list = [x["chatid"] for x in self.userdb.getAll()]
        if update.effective_chat.id not in chat_id_list:
            print(update.message.from_user)
            self.userdb.add(
                {"name": update.message.from_user["first_name"],
                 "chatid": update.effective_chat.id}
            )

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Welcome! I will sent you a Spotify song every day. Use /unsubscribe if you" +
                " don't want to receive daily songs anymore")
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You are already subscribed. Use /unsubscribe if you" +
                " don't want to receive daily songs anymore")

    async def unsubscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        users_to_delete = self.userdb.getBy(
            {"name": update.message.from_user["first_name"]})
        if users_to_delete != []:
            for user in users_to_delete:
                self.userdb.deleteById(user["id"])

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Yo will not receive daily songs anymore. Use /subscribe to receive daily songs" +
            " again")

    async def hello(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="hello " + update.message.from_user.full_name)

        print(self.userdb.getAll())
        for user in self.userdb.getAll():
            print(user["name"])
            print(user["chatid"])

    async def sendSong(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = "Hello, " + update.message.from_user.full_name + \
            "! Enjoy this song!\n" + getSpotifyLink()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message)

    async def sendSongDaily(self, context: CallbackContext):
        link = getSpotifyLink()
        for user in self.userdb.getAll():
            message = "Hello, " + user["name"] + \
                "! Enjoy this song!\n" + link
            await context.bot.send_message(
                chat_id=user["chatid"],
                text=message)

    def run(self):
        self.application.job_queue.run_daily(
            self.sendSongDaily,
            days=(0, 1, 2, 3, 4, 5, 6),
            time=datetime.time(hour=9,
                               minute=30,
                               tzinfo=pytz.timezone("Europe/Madrid")
                               ),
        )

        self.application.run_polling()


if __name__ == '__main__':
    bot = DailyMusicBot()
    bot.run()
