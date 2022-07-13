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
import requests
import asyncio
import aiohttp

#########################################################################################################################################################################################

TGTOKEN = ''  # 可在@botfather处申请

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
# preconfig




def start(update: Update, context: CallbackContext):
	update.message.reply_text(text='Hi,我可以帮你检测Oracle账号状态，请输入你的账户名，每行一个。建议私聊使用', parse_mode='HTML')
	return checkAccount


def checkAccount(update: Update, context: CallbackContext):
	ret1 = update.message.text
	accountList = str.splitlines(ret1)
	accok = 0
	for accountName in accountList:
		#update.message.reply_text(text='账号' + accountName + '返回状态码'+checkAccountIfActive(accountName))
		if checkAccountIfActive(accountName) == 200:
			accok = accok + 1
		elif checkAccountIfActive(accountName) == 000:
			update.message.reply_text(text='账号' + accountName + '似乎不存在或者已被封号')
		elif checkAccountIfActive(accountName) == 503:
			update.message.reply_text(text='账号' + accountName + '似乎已被封号')
		else:
			update.message.reply_text(text='账号' + accountName + '返回了未知状态码，为' + checkAccountIfActive(accountName))

	update.message.reply_text(text='本次正常账号共' + str(accok) + '个。', parse_mode='HTML')
	return ConversationHandler.END

#async def getAccountCode(accountName):
#	async with aiohttp.ClientSession() as session:
#		async with session.get('http://httpbin.org/get') as resp:
#			print(resp.status)

def checkAccountIfActive(accountName):
	try:
		tmp1=requests.get('https://myservices-' + accountName + '.console.oraclecloud.com/mycloud/cloudportal/gettingStarted',timeout=5)
		retcode=tmp1.status_code
	except requests.exceptions.ConnectionError:
		retcode=000
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
