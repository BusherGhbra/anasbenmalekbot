import constants
# import logging
from telegram import *
from telegram.ext import *
from LoginHandler import login_conv
from PointsHandler import points_conv
from PagesHandler import pages_conv
from SectionsHandler import sections_conv

# # Enable logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
# )

# logger = logging.getLogger(__name__)


def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(
        'أهلا وسهلا بكم في بوت مسجد أنس بن مالك\n'
        'يمكنكم البقاء على اطلاع على جميع صفحاتكم المسمعة في المسجد بالإضافة إلى معرفة رصيد نقاطكم',
        reply_markup=ReplyKeyboardMarkup(
            constants.main_keyboard,
            resize_keyboard=True
        ),
    )


if __name__ == '__main__':
    updater = Updater(constants.BOT_KEY, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(login_conv)
    dispatcher.add_handler(points_conv)
    dispatcher.add_handler(pages_conv)
    dispatcher.add_handler(sections_conv)

    updater.start_polling()
    updater.idle()
