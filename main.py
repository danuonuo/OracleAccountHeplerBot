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
import uuid

#########################################################################################################################################################################################

TGTOKEN = '' #可在@botfather处申请

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
#preconfig

os.system('mkdir ~/ocihelper')
os.system('chmod 777 ~/ocihelper')

def start(update: Update, context: CallbackContext):
    update.message.reply_text(text='Hi,我可以帮你检测Oracle账号状态，请输入你的账户名，每行一个。建议私聊使用', parse_mode='HTML')
    return checkAccount


def checkAccount(update: Update, context: CallbackContext):
    ret1 = update.message.text
    accountList=str.splitlines(ret1)
    accok=0
    for accountName in accountList:
        if checkAccountIfActive(accountName)=='302':
            accok=accok+1
        elif checkAccountIfActive(accountName)=='000':
            update.message.reply_text(text='账号'+accountName+'似乎不存在')
        elif checkAccountIfActive(accountName) == '503':
            update.message.reply_text(text='账号' + accountName + '似乎已被封号')
        else:
            update.message.reply_text(text='账号' + accountName + '返回了未知状态码，为'+checkAccountIfActive(accountName))

    update.message.reply_text(text='本次正常账号共'+str(accok)+'个。',parse_mode='HTML')
    return ConversationHandler.END



def checkAccountIfActive(ret):
    uid=uuid.uuid4()
    
    os.system('echo "' + ret + '" >> ~/ocihelper/'+uid)
    p = os.popen(
        "xargs -a ~/ocihelper/"+uid+" -I '{}' curl -m 10 -o /dev/null -s -w %{http_code} https://myservices-'{}'.console.oraclecloud.com/mycloud/cloudportal/gettingStarted")
    retcode = p.read()
    return retcode



def cancel(update: Update, context: CallbackContext):
    return ConversationHandler.END


def main():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            checkAccount: [MessageHandler(Filters.chat_type.private & Filters.text, checkAccount)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        conversation_timeout=60.0
    )

    dispatcher.add_handler(conv_handler)
    #
    updater.start_polling()
    updater.idle()


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    main()
