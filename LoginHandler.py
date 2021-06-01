import constants
import responses
from telegram import *
from telegram.ext import *


global _username, _password
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


def login(update: Update, context: CallbackContext) -> None:
    global _username, _password
    fullname = responses.validate_user(_username, _password)
    if fullname:
        update.message.reply_text(
            f'أهلا وسهلاً بكم في حساب الطالب {fullname}',
            reply_markup=ReplyKeyboardMarkup(
                constants.main_keyboard,
                resize_keyboard=True
            )
        )
        users = context.user_data.get('users', set())
        users.add(_username.lower())
        context.user_data[_username.lower()] = fullname
        context.user_data[fullname] = _username.lower()
        context.user_data['users'] = users
        context.user_data['active_user'] = _username.lower()
    else:
        update.message.reply_text(
            'المعلومات المدخلة خاطئة، الرجاء المحاولة مجدداً ...',
            reply_markup=ReplyKeyboardMarkup(
                responses.get_keyboard(context),
                resize_keyboard=True
            )
        )


login_conv = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex('^(تسجيل الدخول)$'), add_user)],
    states={
        USERNAME: [MessageHandler(Filters.text & ~Filters.command, get_username)],
        PASSWORD: [MessageHandler(Filters.text & ~Filters.command, get_password)]
    },
    fallbacks=[]
)
