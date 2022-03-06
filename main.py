# -*- coding: UTF-8 -*-

import logging
import time
import mysql.connector
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

#########################################################################################################################################################################################

bot = telegram.Bot(token=TGTOKEN)
mycursor = mydb.cursor()
updater = Updater(token=TGTOKEN, use_context=True)
dispatcher = updater.dispatcher
# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
#

checkAccount = range(1)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(text='Hi,我可以帮你检测Oracle账号状态，请输入你的账户名，每行一个。', parse_mode='HTML')
    return checkAccount


def checkAccount(update: Update, context: CallbackContext):
    ret1 = update.message.text
    accountList=str.splitlines(ret1)
    retcode=''
    accok=0
    for i in len(accountList):
        if checkAccountIfActive(accountList[i])=='302':
            accok=accok+1
        elif checkAccountIfActive(accountList[i])=='000':
            update.message.reply_text(text='账号'+accountList[i]+'似乎不存在')
        elif checkAccountIfActive(accountList[i]) == '503':
            update.message.reply_text(text='账号' + accountList[i] + '似乎已被封号')
        else:
            update.message.reply_text(text='账号' + accountList[i] + '返回了未知状态码，为'+checkAccountIfActive(accountList[i]))

    update.message.reply_text(text='本次正常账号共'+accok+'个。',parse_mode='HTML')
    return ConversationHandler.END

def checkAccountIfActive(ret):
    os.system('rm -f test')
    os.system('echo "' + ret + '" >> test')
    p = os.popen(
        "xargs -a test -I '{}' curl -m 10 -o /dev/null -s -w %{http_code} https://myservices-'{}'.console.oraclecloud.com/mycloud/cloudportal/gettingStarted")
    retcode = p.read()
    return retcode

def dbWriteAccountInf(tgChatId, accountInf):
    sql = "INSERT INTO accountInf (tgChatId, accountInf) VALUES (%s, %s)"
    val = (tgChatId, accountInf)
    mycursor.execute(sql, val)
    mydb.commit()
    return

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
    #
    updater.start_polling()
    updater.idle()


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    main()
