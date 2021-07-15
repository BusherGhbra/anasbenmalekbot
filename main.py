import functools
import logging
import constants
import responses
from telegram import *
from telegram.ext import *
from LoginHandler import login_conv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)



def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        'أهلاً وسهلاً بكم\nيرجى تسجيل الدخول عن طريق إدخال بيانات الطالب الموجودة على بطاقته الشخصية\n',
        reply_markup=ReplyKeyboardMarkup(
            responses.get_keyboard(context),
            resize_keyboard=True
        ),
    )


def refresh(_: Update, context: CallbackContext) -> None:
    current_user = context.user_data.get('active_user', '')
    for admin, _ in constants.ADMIN:
        if current_user.lower() == admin.lower():
            responses.load_data()


def reset(update: Update, context: CallbackContext) -> None:
    current_user = context.user_data.get('active_user', '')
    for admin, _ in constants.ADMIN:
        if current_user.lower() == admin.lower():
            context.user_data.clear()
            start(update, context)


def get_file(update: Update, context: CallbackContext, file_type: str) -> None:
    username = context.user_data.get('active_user', '')
    wait_msg = context.bot.send_message(
        update.effective_chat.id,
        'الرجاء الانتظار\nجاري تحميل البيانات المطلوبة ...'
    )
    if username:
        status, fh = responses.get_file(username, file_type)
        if status:
            context.bot.send_document(
                update.effective_chat.id,
                document=fh,
                reply_markup=ReplyKeyboardMarkup(
                    constants.main_keyboard,
                    resize_keyboard=True
                )
            )
        else:
            update.message.reply_text(
                'عذراً البيانات المطلوبة غير متوفرة\nالرجاء مراجعة الإدارة',
                reply_markup=ReplyKeyboardMarkup(
                    constants.main_keyboard,
                    resize_keyboard=True
                )
            )

    else:
        update.message.reply_text(
            'الرجاء إضافة الطالب أولاً',
            reply_markup=ReplyKeyboardMarkup(
                responses.get_keyboard(context),
                resize_keyboard=True
            )
        )

    context.bot.delete_message(update.effective_chat.id, wait_msg.message_id)


def get_points(update: Update, context: CallbackContext) -> None:
    username = context.user_data.get('active_user', '')
    if username:
        update.message.reply_text(
            f'مجموع نقاطك هو {responses.get_points(username)} نقطة',
            reply_markup=ReplyKeyboardMarkup(
                constants.main_keyboard,
                resize_keyboard=True
            )
        )
    else:
        update.message.reply_text(
            'الرجاء إضافة الطالب أولاً',
            reply_markup=ReplyKeyboardMarkup(
                responses.get_keyboard(context),
                resize_keyboard=True
            )
        )


def sign_in(update: Update, context: CallbackContext) -> None:
    print(context.user_data)

    user = update.message.text[2:-2]
    context.user_data['active_user'] = context.user_data[user]
    update.message.reply_text(
        f'أهلاً وسهلاً بكم في حساب الطالب {user}',
        reply_markup=ReplyKeyboardMarkup(
            constants.main_keyboard,
            resize_keyboard=True
        )
    )


if __name__ == '__main__':
    responses.load_data()

    updater = Updater(constants.BOT_KEY, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('refresh', refresh))
    dispatcher.add_handler(CommandHandler('reset', reset))
    dispatcher.add_handler(login_conv)
    
    dispatcher.add_handler(
        MessageHandler(
            Filters.regex('^(الصفحات المسمعة)$'),
            functools.partial(lambda update, context, file_type: 
                get_file(update, context, file_type), file_type='P')
        )
    )

    dispatcher.add_handler(
        MessageHandler(
            Filters.regex('^(الأجزاء المسبورة)$'),
            functools.partial(lambda update, context, file_type: 
                get_file(update, context, file_type), file_type='S')
        )
    )


    dispatcher.add_handler(
        MessageHandler(
            Filters.regex('^(رصيد النقاط)$'), 
            get_points
        )
    )


    dispatcher.add_handler(
        MessageHandler(
            Filters.regex('^(العودة إلى القائمة الرئيسية)$'), 
            start
        )
    )


    dispatcher.add_handler(
        MessageHandler(
            Filters.regex('^\u2985 .+ \u2986$'),
            sign_in
        )
    )

    updater.start_polling()
    updater.idle()
