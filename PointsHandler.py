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

    get_points(update, _)
    return ConversationHandler.END


def get_points(update: Update, context: CallbackContext) -> None:
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

    update.message.reply_text(
        f'مجموع نقاطك هو {responses.get_points(_username)} نقطة',
        reply_markup=ReplyKeyboardMarkup(
            constants.main_keyboard,
            resize_keyboard=True
        )
    )


points_conv = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex('^(رصيد النقاط)$'), add_user)],
    states={
        USERNAME: [MessageHandler(Filters.text & ~Filters.command, get_username)],
    },
    fallbacks=[]
)
