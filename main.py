# -*- coding: UTF-8 -*-

import logging
import time
import telegram
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove, Update)
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)
import os

#########################################################################################################################################################################################


TGTOKEN = ''
# SVM_IP_ADDRESS = ''
# SVM_API_ID = ''
# SVM_API_KEY = ''

#REQUEST_KWARGS = {
    # "USERNAME:PASSWORD@" is optional, if you need authentication:
#    'proxy_url': 'http://127.0.0.1:10809/',
#}
#########################################################################################################################################################################################
bot = telegram.Bot(token=TGTOKEN)
updater = Updater(token=TGTOKEN, use_context=True)
dispatcher = updater.dispatcher
# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
#

checkAccount = range(1)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(text='Hi,我可以帮你检测Oracle账号状态，请输入你的账户名。',parse_mode='HTML')
    return checkAccount

def checkAccount(update: Update, context: CallbackContext):
    ret=update.message.text
    os.system('rm -f test')
    os.system('echo "'+ret+'" >> test')
    p = os.popen("xargs -a test -I '{}' curl -m 10 -o /dev/null -s -w %{http_code} https://myservices-'{}'.console.oraclecloud.com/mycloud/cloudportal/gettingStarted")
    retcode = p.read()
    if retcode == '302':
        update.message.reply_text(text='该账号正常。')
    elif retcode == '000':
        update.message.reply_text(text='抱歉，响应超时。')
    elif retcode == '503':
        update.message.reply_text(text='账号状态不正常！可能已被封号。')
    else:
        update.message.reply_text(text='无法识别的响应，返回值：'+retcode)
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    return ConversationHandler.END

def main():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, filters=Filters.chat_type.private)],
        states={
            checkAccount: [MessageHandler(Filters.chat_type.private & Filters.text, checkAccount)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        conversation_timeout=60.0
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

