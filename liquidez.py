import logging

import MetaTrader5 as mt5
import pandas as pd

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


class Liquidez():
    def __init__(self):
        """Run bot."""
        # Create the Updater and pass it your bot's token.
        updater = Updater("2010600314:AAF-C06lmE-3xK9ai3RHm7b8WL-rwNawdfw")

        self.ativo = ""
        self.anterior_buy = 0.1
        self.anterior_sell = 0.1

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # on different commands - answer in Telegram
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("help", self.start))
        dispatcher.add_handler(CommandHandler("set", self.set_timer))
        dispatcher.add_handler(CommandHandler("unset", self.unset))

        # Start the Bot
        updater.start_polling()


        # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
        # SIGABRT. This should be used most of the time, since start_polling() is
        # non-blocking and will stop the bot gracefully.
        updater.idle()


    def start(self, update: Update, context: CallbackContext) -> None:
        """Sends explanation on how to use the bot."""
        update.message.reply_text('Olá! Use /set <ativo> para configurar o alerta')


    def alarm(self, context: CallbackContext) -> None:
        """Send the alarm message."""

        book = mt5.market_book_get(self.ativo)
        book_frame = pd.DataFrame(book, columns=['Type', 'Price', 'Volume', 'Volume DBL'])
        buy_list = book_frame[(book_frame['Type'] == mt5.BOOK_TYPE_BUY)]
        sell_list = book_frame[(book_frame['Type'] == mt5.BOOK_TYPE_SELL)]

        print(buy_list)
        print(sell_list)

        if len(buy_list) != 0:
            buy = max(buy_list['Price'])
        else:
            buy = 0
            
            
        if len(sell_list) != 0:
            sell = min(sell_list['Price'])
        else:
            sell = 0

        if ((self.anterior_buy != buy) or (self.anterior_sell != sell)):
            text = f'Compra: R${buy}    Venda: R${sell}'
            job = context.job
            context.bot.send_message(job.context, text=text)
            self.anterior_buy = buy
            self.anterior_sell = sell


    def remove_job_if_exists(self, name: str, context: CallbackContext) -> bool:
        """Remove job with given name. Returns whether job was removed."""
        current_jobs = context.job_queue.get_jobs_by_name(name)
        if not current_jobs:
            return False
        for job in current_jobs:
            job.schedule_removal()
        return True


    def set_timer(self, update: Update, context: CallbackContext) -> None:
        """Add a job to the queue."""
        chat_id = update.message.chat_id

        try:
            #Inicializa Metatrader 5
            if mt5.initialize():
                if not mt5.market_book_add(context.args[0]):
                    update.message.reply_text(f'Some thing happened adding {context.args[0]} to market book')
                    print(f'Some thing happened adding {context.args[0]} to market book, error: {mt5.last_error()}')
                    
                    return
            else:
                update.message.reply_text(f'Problema ao inicializar o terminal')
                print(f'Problema ao inicializar o terminal, error: {mt5.last_error()}')
                if mt5.shutdown():
                    print(f'O terminal foi finalizado.')
                else:
                    print(f'Problema ao finalizar o terminal, error: {mt5.last_error()}')
                
                
                return

            self.ativo = context.args[0]

            job_removed = self.remove_job_if_exists(str(chat_id), context)
            context.job_queue.run_repeating(self.alarm, 10, context=chat_id, name=str(chat_id))

            text = 'Ativo cadastrado com sucesso!'
            if job_removed:
                text += ' Cadastro anterior excluido.'
            update.message.reply_text(text)

        except (IndexError, ValueError):
            update.message.reply_text('ALERTA: Ativo não foi cadastrado!')
            



    def unset(self, update: Update, context: CallbackContext) -> None:
        """Remove the job if the user changed their mind."""

        if not mt5.market_book_release(self.ativo):
                print(f'Problema ao liberar {self.ativo} do book, error: {mt5.last_error()}')
        if not mt5.shutdown():
            print(f'Problema ao finalizar o terminal, error: {mt5.last_error()}')

        chat_id = update.message.chat_id
        job_removed = self.remove_job_if_exists(str(chat_id), context)
        text = 'Observação cancelada com sucesso!' if job_removed else 'ALERTA: Você não tinha observção ativa..'
        update.message.reply_text(text)


Liquidez()
