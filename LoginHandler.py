import constants
import responses
from telegram import *
from telegram.ext import *

USERNAME, PASSWORD = range(2)


def add_user(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        'ادخل اسم المستخدم',
        reply_markup=ReplyKeyboardRemove(),
    )

    return USERNAME


def get_username(update: Update, _: CallbackContext) -> int:
    global _username
    _username = update.message.text

    update.message.reply_text(
        'ادخل كلمة المرور',
        reply_markup=ReplyKeyboardRemove(),
    )

    return PASSWORD


def get_password(update: Update, _: CallbackContext) -> int:
    global _password
    _password = update.message.text

    login(update, _)
    return ConversationHandler.END


# def login(update: Update, context: CallbackContext) -> None:
#     global _username, _password
#     update.message.reply_text(
#         'تم تسجيل الدخول بنجاح',
#         reply_markup=ReplyKeyboardMarkup(
#             constants.main_keyboard,
#             resize_keyboard=True
#         )
#     )
#     context.user_data[_username] = True


def login(update: Update, context: CallbackContext) -> None:
    global _username, _password
    if responses.validate_user(_username, _password):
        update.message.reply_text(
            'تم تسجيل الدخول بنجاح',
            reply_markup=ReplyKeyboardMarkup(
                constants.main_keyboard,
                resize_keyboard=True
            )
        )
        context.user_data[_username] = True
    else:
        update.message.reply_text(
            'المعلومات المدخلة خاطئة، الرجاء المحاولة مجدداً ...',
            reply_markup=ReplyKeyboardMarkup(
                constants.main_keyboard,
                resize_keyboard=True
            )
        )


login_conv = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex('^(إضافة طالب جديد)$'), add_user)],
    states={
        USERNAME: [MessageHandler(Filters.text & ~Filters.command, get_username)],
        PASSWORD: [MessageHandler(Filters.text & ~Filters.command, get_password)]
    },
    fallbacks=[]
)
