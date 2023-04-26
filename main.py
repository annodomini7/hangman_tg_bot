# @test_bot_py
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from my_token import TOKEN
from constants import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def input_format(text):  # санитарная обработка введенного текста
    ch_map = {
        ord('\t'): ' ',
        ord('\n'): ' ',
        ord('\r'): None
    }
    return text.translate(ch_map).rstrip().strip()


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def conversation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if word_key in context.user_data:
        await guess_word(update, context)
    print(context.user_data)
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Write \"/start_a_game\" to start a game."
                                        " After this I will tell you a number of letters in guessed word."
                                        " After this you should write letters. If you write a letter, which ...")


async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I thought of a word. Write a letter")
    context.user_data[word_key] = 'qwerty'
    return 1


async def guess_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data[last_written_letter] = input_format(update.message.text)
    if len(context.user_data[last_written_letter]) > 1:
        # введен неправильный текст + обработать ввод цифр
        pass
    else:
        # проверить, есть ли буква среди уже загаданных, если нет, то обработать
        pass
    await context.bot.send_message(chat_id=update.effective_chat.id, text="write a letter")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # start_handler = CommandHandler('start', start)
    # application.add_handler(start_handler)

    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(CommandHandler('start', start))
    # application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    application.add_handler(CommandHandler('rules', rules))
    application.add_handler(CommandHandler('start_a_game', start_game))

    text_handler = MessageHandler(filters.TEXT, conversation_handler)
    application.add_handler(text_handler)

    application.run_polling()
