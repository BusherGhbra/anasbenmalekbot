import constants
import responses
from telegram import *
from telegram.ext import *

USERNAME = range(1)


def add_user(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        'ادخل اسم المستخدم',
        reply_markup=ReplyKeyboardRemove(),
    )

    return USERNAME


def get_username(update: Update, _: CallbackContext) -> int:
    global _username
    _username = update.message.text

    get_pages(update, _)
    return ConversationHandler.END


def get_pages(update: Update, context: CallbackContext) -> None:
    global _username
    if not responses.logged_in(context, _username):
        update.message.reply_text(
            'الرجاء إضافة الطالب أولاً',
            reply_markup=ReplyKeyboardMarkup(
                constants.main_keyboard,
                resize_keyboard=True
            )
        )
        return

    context.bot.send_document(
        update.effective_chat.id,
        document=responses.get_pages(_username),
        reply_markup=ReplyKeyboardMarkup(
            constants.main_keyboard,
            resize_keyboard=True
        )
    )


pages_conv = ConversationHandler(
    entry_points=[MessageHandler(
        Filters.regex('^(الصفحات المسمعة)$'), add_user)],
    states={
        USERNAME: [MessageHandler(Filters.text & ~Filters.command, get_username)],
    },
    fallbacks=[]
)
