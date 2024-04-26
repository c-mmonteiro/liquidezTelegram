import logging

from getData import *
import pandas as pd

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


class bookTelegram():
    def __init__(self):
        """Run bot."""

        self.handler_dados = getData()
        # Create the Updater and pass it your bot's token.
        updater = Updater("2010600314:AAF-C06lmE-3xK9ai3RHm7b8WL-rwNawdfw")

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # on different commands - answer in Telegram
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("help", self.help))
        dispatcher.add_handler(CommandHandler("add", self.add))
        dispatcher.add_handler(CommandHandler("remove", self.remove))
        dispatcher.add_handler(CommandHandler("clear", self.clear))
        dispatcher.add_handler(CommandHandler("getlist", self.getList))

        # Start the Bot
        updater.start_polling()


        # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
        # SIGABRT. This should be used most of the time, since start_polling() is
        # non-blocking and will stop the bot gracefully.
        updater.idle()

    def remove_job_if_exists(self, name: str, context: CallbackContext) -> bool:
        """Remove job with given name. Returns whether job was removed."""
        current_jobs = context.job_queue.get_jobs_by_name(name)
        if not current_jobs:
            return False
        for job in current_jobs:
            job.schedule_removal()
        return True        

    def start(self, update: Update, context: CallbackContext) -> None:
        """Add a job to the queue."""
        chat_id = update.message.chat_id

        job_removed = self.remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(self.updater, 10, context=chat_id, name=str(chat_id))

        text = 'Bot inicializado!'
        if job_removed:
            text += ' Bot anterior excluido.'
        update.message.reply_text(text)

    def help(self, update: Update, context: CallbackContext) -> None:
        """Sends explanation on how to use the bot."""
        update.message.reply_text('Olá! Este chatbot enviará atualizações nas ações cadastradas \n' +
                                  '/start para iniciar ou reiniciar o bot.\n'
                                  '/add <ativo> para adicionar um ativo a lista.\n' +
                                  '/remove <ativo> para remover um ativo da lista.\n' + 
                                  '/clear para limpar a lista de ativos.\n' +
                                  '/getlist para ver a lista de ativos cadastrados.\n')

    def add(self, update: Update, context: CallbackContext) -> None:
        if self.handler_dados.addAtivo(context.args[0]) == 1:
            text = 'Ativo adicionado com sucesso!'
        else:
            text = 'Ativo NÃO foi adicionado!'
        
        update.message.reply_text(text)

    def remove(self, update: Update, context: CallbackContext) -> None:
        if self.handler_dados.removeAtivo(context.args[0]) == 1:
            text = 'Ativo removido com sucesso!'
        else:
            text = 'Ativo NÃO foi removido!'
        
        update.message.reply_text(text)

    def clear(self, update: Update, context: CallbackContext) -> None:
        if self.handler_dados.limparAtivos() == 1:
            text = 'A lista de ativos está limpa!'
        else:
            text = 'NÃO foi possivel limpar a lista de ativos!'
        
        update.message.reply_text(text)

    def getList(self, update: Update, context: CallbackContext) -> None:
        list_ativos = self.handler_dados.getAtivos()
        text = f'Lista de ativos cadastrados: \n {list_ativos}'        
        update.message.reply_text(text)


    def updater(self, context: CallbackContext) -> None:
        """Send the alarm message."""
        dados = self.handler_dados.atualizarDados()
        print(dados)
        
        for idx, m in enumerate(dados['Mudanca']):
            if m == 1:
                text = f'{dados["Ativo"][idx]} \n Buy: R${dados["Preco Compra"][idx]} ({dados["Vol Compra"][idx]})   Sell: R${dados["Preco Venda"][idx]} ({dados["Vol Venda"][idx]})'
                job = context.job
                context.bot.send_message(job.context, text=text)


bookTelegram()
