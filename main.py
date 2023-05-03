# @test_bot_py
import logging
from telegram import Update, InputMediaDocument
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from my_token import TOKEN
from constants import *
from find_word import find_word
from texts import *

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
        if context.user_data[game_over] == 'false':
            await guess_word(update, context)
        else:
            await help(update, context)
    else:
        await help(update, context)
    print(context.user_data)
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)
    # await context.bot.send_document(chat_id=update.effective_chat.id, document=open("src/all_pictures.jpg", "rb"))
    # await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("src/all_pictures.jpg", "rb"))


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=help_text)


async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        word = find_word()
        context.user_data[word_key] = word
        context.user_data[number_of_lives] = max_lives
        context.user_data[guessed_word] = ['_ ' for _ in range(len(context.user_data[word_key]))]
        context.user_data[all_letters] = ''
        context.user_data[game_over] = 'false'
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="I guessed a word " + ''.join(
                                           context.user_data[guessed_word]) + ". Now, please, write a letter")
    except:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Something went wrong. Please, try again later.")

    return 1


async def guess_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data[last_written_letter] = input_format(update.message.text)
    # обработка некорректного ввода
    if len(context.user_data[last_written_letter]) > 1 or not context.user_data[last_written_letter].isalpha():
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=incorrect_input)
        return 1
    else:
        # проверить, есть ли буква среди уже загаданных, если нет, то обработать
        context.user_data[last_written_letter] = context.user_data[last_written_letter].lower()
        if context.user_data[last_written_letter] in context.user_data[all_letters]:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=incorrect_input)
            return 2
        if context.user_data[last_written_letter] not in context.user_data[word_key]:
            if context.user_data[number_of_lives] == 1:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="Unfortunately, this letter is not in the guessed word..."
                                                    " Your lives wasted. It was a word " +
                                                    context.user_data[word_key])
                return 3
            context.user_data[number_of_lives] -= 1
            context.user_data[all_letters] += context.user_data[last_written_letter]
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Unfortunately, this letter is not in the guessed word..."
                                                " Now you have " + str(context.user_data[number_of_lives]) +
                                                " lives. Guessed word is " +
                                                ''.join(context.user_data[guessed_word]))
            return 4
        context.user_data[all_letters] += context.user_data[last_written_letter]
        for i in range(len(context.user_data[word_key])):
            if context.user_data[word_key][i] == context.user_data[last_written_letter]:
                context.user_data[guessed_word][i] = context.user_data[last_written_letter]
        if ''.join(context.user_data[guessed_word]) == context.user_data[word_key]:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Congratulations! You win! The word was " +
                                                ''.join(context.user_data[guessed_word]) +
                                                ". Use /start_a_game to play again")
            context.user_data[game_over] = 'true'
            return 5
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Yes, there is this letter in my word. Guessed word is " +
                                        ''.join(context.user_data[guessed_word]) + ". You have " +
                                        str(context.user_data[number_of_lives]) + " lives now. Write next letter.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # start_handler = CommandHandler('start', start)
    # application.add_handler(start_handler)

    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(CommandHandler('start', start))
    # application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('start_a_game', start_game))

    text_handler = MessageHandler(filters.TEXT, conversation_handler)
    application.add_handler(text_handler)

    application.run_polling()
