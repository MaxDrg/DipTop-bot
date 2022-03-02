from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pyqiwip2p import QiwiP2P
from json_data import Trend, Ignore_words
import os

class Config:
    def __init__(self):
        self.bot = Bot(token=os.environ.get('TELEGRAM_TOKEN'))
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.p2p = QiwiP2P(auth_key=os.environ.get('QIWI_TOKEN'))
        self.umoney_token = os.environ.get('UMONEY_TOKEN')
        self.cost_per_month = int(os.environ.get('COST_PER_MONTH'))
        self.cost_per_week = int(os.environ.get('COST_PER_WEEK'))
        
        self.cashback_from_month = self.cost_per_month / 100 * 10
        self.cashback_from_week = self.cost_per_week / 100 * 10
        self.discount_cost_per_month = int(self.cost_per_month - self.cashback_from_month)
        self.discount_cost_per_week = int(self.cost_per_week - self.cashback_from_week)

        self.photo_crypto = os.environ.get('PHOTO_CRYPTO')

        trend_file_json = os.environ.get('TREND_JSON_FILE')
        self.trend_json = Trend(file=trend_file_json)

        ignore_words_file_json = os.environ.get('IGNORE_WORDS_JSON_FILE')
        self.ignore_words_json = Ignore_words(file=ignore_words_file_json)

        self.host = os.environ.get('HOST')
        self.port = os.environ.get('PORT')
        self.username = os.environ.get('USER')
        self.password= os.environ.get('PASS')

        self.database = os.environ.get('DATA')
        self.user = os.environ.get('DATA_USER')
        self.password_data = os.environ.get('DATA_PASS')
        self.host_data = os.environ.get('HOST')
        self.port_data = os.environ.get('DATA_PORT')

        self.error_cost = int(os.environ.get('ERROR_COST'))

        self.umoney = os.environ.get('PURSE')