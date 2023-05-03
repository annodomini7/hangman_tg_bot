# @test_bot_py
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
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


async def conversation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == start_a_game_text:
        await start_game(update, context)
    elif word_key in context.user_data:
        if context.user_data[game_over] == 'false':
            await guess_word(update, context)
        else:
            await start(update, context)
    else:
        await start(update, context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text,
                                   reply_markup=ReplyKeyboardMarkup([[start_a_game_text]], one_time_keyboard=True)
                                   )


async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        word = find_word()
        context.user_data[word_key] = word
        print(word)
        context.user_data[number_of_lives] = max_lives
        context.user_data[guessed_word] = ['_ ' for _ in range(len(context.user_data[word_key]))]
        context.user_data[all_letters] = ''
        context.user_data[game_over] = 'false'
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=open(game_pictures_paths[max_lives - context.user_data[number_of_lives]],
                                                "rb"),
                                     caption="I guessed a word " + ''.join(context.user_data[guessed_word]) +
                                             ". Now, please, write a letter")
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
                await game_over_actions(update, context,
                                        game_pictures_paths[max_lives - context.user_data[number_of_lives]],
                                        "Unfortunately, this letter is not in the guessed word..."
                                        " Your lives wasted. It was a word " + context.user_data[word_key])
                return 3
            context.user_data[number_of_lives] -= 1
            context.user_data[all_letters] += context.user_data[last_written_letter]
            await context.bot.send_photo(chat_id=update.effective_chat.id,
                                         photo=open(game_pictures_paths[max_lives - context.user_data[number_of_lives]],
                                                    "rb"),
                                         caption="Unfortunately, this letter is not in the guessed word..."
                                                 " Now you have " + str(context.user_data[number_of_lives]) +
                                                 " lives. Guessed word is " +
                                                 ''.join(context.user_data[guessed_word]))
            return 4
        context.user_data[all_letters] += context.user_data[last_written_letter]
        for i in range(len(context.user_data[word_key])):
            if context.user_data[word_key][i] == context.user_data[last_written_letter]:
                context.user_data[guessed_word][i] = context.user_data[last_written_letter]
        if ''.join(context.user_data[guessed_word]) == context.user_data[word_key]:
            context.user_data[game_over] = 'true'
            await game_over_actions(update, context, congratulation_picture_path,
                                    "Congratulations! You win! The word was " +
                                    ''.join(context.user_data[guessed_word]) +
                                    ". Use /start_a_game to play again")
            return 5
    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo=open(game_pictures_paths[max_lives - context.user_data[number_of_lives]],
                                            "rb"),
                                 caption="Yes, there is this letter in my word. Guessed word is " +
                                         ''.join(context.user_data[guessed_word]) + ". You have " +
                                         str(context.user_data[number_of_lives]) + " lives now. Write next letter.")


async def game_over_actions(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_path, text):
    if game_over not in context.user_data or context.user_data[game_over] == 'false':
        return 1

    keyboard = [
        [InlineKeyboardButton("Start new game", callback_data="1"), ],
        [InlineKeyboardButton("Check your results", callback_data="2"), ],
        [InlineKeyboardButton("Find out word's meaning", callback_data="3")], ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo=open(photo_path, "rb"),
                                 caption=text, reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parses the CallbackQuery and updates the message text."""

    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed

    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery

    await query.answer()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Selected option: {query.data}")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # start_handler = CommandHandler('start', start)
    # application.add_handler(start_handler)

    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(CommandHandler('start', start))
    # application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    application.add_handler(CommandHandler('help', start))
    application.add_handler(CommandHandler('start_a_game', start_game))
    application.add_handler(CallbackQueryHandler(button))
    text_handler = MessageHandler(filters.TEXT, conversation_handler)
    application.add_handler(text_handler)

    application.run_polling()
