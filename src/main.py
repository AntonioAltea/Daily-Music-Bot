import datetime
import logging
import pysondb
import pytz
import os
from dotenv import load_dotenv
from spotify import getRandomSong, saveSongs
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
        self.METRICS_DATABASE = os.getenv("METRICS_DATABASE")

        self.userdb = pysondb.getDb(self.USER_DATABASE)
        self.metricsdb = pysondb.getDb(self.METRICS_DATABASE)

        saveSongs()

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

        self.application = ApplicationBuilder().token(self.TELEGRAM_TOKEN).build()

        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('subscribe', self.subscribe))
        self.application.add_handler(CommandHandler('unsubscribe', self.unsubscribe))
        self.application.add_handler(CommandHandler('hello', self.hello))
        self.application.add_handler(CommandHandler('song', self.sendSong))
        self.application.add_handler(CommandHandler('metrics', self.metrics))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="buenas, usa /subscribe para recibir una canción diaria o /song para recibir una" +
            " ahora mismo")

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
                text="genial! te mandaré una canción todos los días. \nusa /unsubscribe si no" +
                " quieres recibir más")
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="ya estás suscrito\nusa /unsubscribe si no quieres recibir más canciones")

    async def unsubscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        users_to_delete = self.userdb.getByQuery({"name": update.message.from_user["first_name"]})
        if users_to_delete != []:
            for user in users_to_delete:
                self.userdb.deleteById(user["id"])

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="no te mandaré mas canciones\nusa /subscribe para volver a recibir caciones " +
            "diarias")

    async def hello(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="hello " + update.message.from_user.full_name)

        print(self.userdb.getAll())
        for user in self.userdb.getAll():
            print(user["name"])
            print(user["chatid"])

    def metrics_receive_song(self, name, chatid):
        user_metrics = self.metricsdb.getByQuery({"chatid": chatid})
        if user_metrics == []:
            self.metricsdb.add({"name": name,
                                "chatid": chatid,
                                "songs_sent": 1
                                })
        else:
            songs_sent = user_metrics[0]["songs_sent"]
            self.metricsdb.updateByQuery({"chatid": chatid},
                                         {"songs_sent": songs_sent + 1})

    async def sendSong(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.metrics_receive_song(name=update.message.from_user.full_name,
                                  chatid=update.effective_chat.id)

        song = getRandomSong()
        if song is None:
            message = "la api de spotify no me deja mandarte más canciones\n" \
                "\nusureros cabrones no os pienso dar un duro"
        else:
            message = "toma, " + update.message.from_user.full_name + \
                "! un temita\n" + getRandomSong()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message)

    async def metrics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_metrics = self.metricsdb.getByQuery({"chatid": update.effective_chat.id})
        songs_sent = user_metrics[0]["songs_sent"]

        message = "has recibido " + str(songs_sent) + " canciones hasta ahora"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message)

    async def sendSongDaily(self, context: CallbackContext):
        song = getRandomSong()
        for user in self.userdb.getAll():
            self.metrics_receive_song(name=user["name"],
                                      chatid=user["chatid"])
            if song is None:
                message = "la api de spotify no me deja mandarte más canciones\n" \
                    "\nusureros cabrones no os pienso dar un duro"
            else:
                message = "toma un temita, " + \
                    user["name"] + "! así va a irte el día\n" + song
            await context.bot.send_message(
                chat_id=user["chatid"],
                text=message)

    def saveSongsDaily(self, context: CallbackContext):
        saveSongs()

    def run(self):
        self.application.job_queue.run_daily(
            self.saveSongsDaily,
            days=(0, 1, 2, 3, 4, 5, 6),
            time=datetime.time(hour=8, minute=0,
                               tzinfo=pytz.timezone("Europe/Madrid"))
        )
        self.application.job_queue.run_daily(
            self.sendSongDaily,
            days=(0, 1, 2, 3, 4, 5, 6),
            time=datetime.time(hour=8, minute=30,
                               tzinfo=pytz.timezone("Europe/Madrid"))
        )

        self.application.run_polling()


if __name__ == '__main__':
    bot = DailyMusicBot()
    bot.run()
