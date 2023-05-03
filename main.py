# @test_bot_py
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from my_token import TOKEN
from constants import *
from work_with_word_api import *
from texts import *
from database import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def input_format(text: str):
    """formatting input text"""
    ch_map = {
        ord('\t'): ' ',
        ord('\n'): ' ',
        ord('\r'): None
    }
    return text.translate(ch_map).rstrip().strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """\start and \help"""
    keyboard = [
        [InlineKeyboardButton("Start new game", callback_data=start_callback), ],
        [InlineKeyboardButton("Check your results", callback_data=result_callback), ], ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text, reply_markup=reply_markup)


async def conversation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """processing of user input"""
    if word_key in context.user_data:
        if context.user_data[game_over] == 'false':
            await guess_word(update, context)
        else:
            await start(update, context)
    else:
        await start(update, context)


async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """get a word and start a game"""
    init_user(update.effective_chat.id)
    try:
        word = find_word()
        context.user_data[word_key] = word
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


async def guess_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """processing user input during the game"""
    context.user_data[last_written_letter] = input_format(update.message.text)
    # checking if input is correct
    if len(context.user_data[last_written_letter]) > 1 or not context.user_data[last_written_letter].isalpha():
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=incorrect_input)
        return 1
    else:
        context.user_data[last_written_letter] = context.user_data[last_written_letter].lower()
        # check if a letter already was written by user
        if context.user_data[last_written_letter] in context.user_data[all_letters]:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=incorrect_input)
            return 2
        # check if a letter wasn't written by user
        if context.user_data[last_written_letter] not in context.user_data[word_key]:
            if context.user_data[number_of_lives] == 1:
                context.user_data[game_over] = 'true'
                await game_over_actions(update, context,
                                        game_pictures_paths[max_lives - context.user_data[number_of_lives]],
                                        "Unfortunately, this letter is not in the guessed word..."
                                        " Your lives wasted. It was a word " + context.user_data[word_key], lose=True)
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
                                    ". Use /start_a_game to play again", win=True)
            return 5
    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo=open(game_pictures_paths[max_lives - context.user_data[number_of_lives]],
                                            "rb"),
                                 caption="Yes, there is this letter in my word. Guessed word is " +
                                         ''.join(context.user_data[guessed_word]) + ". You have " +
                                         str(context.user_data[number_of_lives]) + " lives now. Write next letter.")


async def game_over_actions(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_path: str, text: str, win=False,
                            lose=False):
    """write a text if a game is over"""
    if game_over not in context.user_data or context.user_data[game_over] == 'false':
        return 1
    set_result(update.effective_chat.id, win, lose)
    keyboard = [
        [InlineKeyboardButton("Start new game", callback_data=start_callback), ],
        [InlineKeyboardButton("Check your results", callback_data=result_callback), ],
        [InlineKeyboardButton("Find out word's meaning", callback_data=words_meaning_callback)], ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo=open(photo_path, "rb"),
                                 caption=text, reply_markup=reply_markup)


async def word_meaning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """return a meaning of a guessed word. works if game is over"""
    if game_over not in context.user_data or context.user_data[game_over] == 'false':
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="You can find out the meaning of word only after end of the game.")
        return 1
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=meaning_of_word(context.user_data[word_key]))
    except:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="I don't know meaning of this word... You can Google it!")


async def result_of_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = get_result(update.effective_chat.id)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Number of games: {results[0]}\n"
                                        f"Games won: {results[1]}\n"
                                        f"Games lost: {results[2]}")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """choose functions for response a button press"""
    query = update.callback_query

    await query.answer()
    if query.data == start_callback:
        await start_game(update, context)
    elif query.data == result_callback:
        await result_of_game(update, context)
    elif query.data == words_meaning_callback:
        await word_meaning(update, context)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Something went wrong. Please, try again.")


if __name__ == '__main__':
    """initialization of bot"""
    application = ApplicationBuilder().token(TOKEN).build()
    """add functions to bot commands"""
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', start))
    application.add_handler(CommandHandler('start_a_game', start_game))
    """function for responding to a button press"""
    application.add_handler(CallbackQueryHandler(button))
    """function for responding to a written text"""
    text_handler = MessageHandler(filters.TEXT, conversation_handler)
    application.add_handler(text_handler)

    application.run_polling()
