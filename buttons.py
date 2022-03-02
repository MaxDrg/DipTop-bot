from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
                    InlineKeyboardMarkup, InlineKeyboardButton

class Button:
    def __init__(self):
        # markup button
        button_cabinet = KeyboardButton('Личный кабинет🏠')
        #button_current_trend = KeyboardButton('Тренд📊')
        button_signals = KeyboardButton('Отработка сигналов🚨')
        button_rules = KeyboardButton('Правила📋')
        button_reviews = KeyboardButton('Отзывы❗️')
        button_maintance = KeyboardButton('Поддержка⚒')
        button_referral = KeyboardButton('Реферальная система👥')
        #button_couples = KeyboardButton('Торговые пары💵')
        self.markup = ReplyKeyboardMarkup(resize_keyboard=True).row(button_cabinet).row(button_signals).row(button_rules, button_maintance).row(button_referral).row(button_reviews)

        # inline button
        inline_buy_token = InlineKeyboardButton('Пополнить счёт💸', callback_data='token')
        inline_buy_subscription = InlineKeyboardButton('Продлить подписку⏰', callback_data='subscription')
        self.inline_buy = InlineKeyboardMarkup().add(inline_buy_token, inline_buy_subscription)
        self.inline_token = InlineKeyboardMarkup().add(inline_buy_token)
        self.inline_subscription = InlineKeyboardMarkup().add(inline_buy_subscription)

        info_kb_start = InlineKeyboardButton('Правила📋', url="https://t.me/joinchat/9xQANy2wf-8xOTYy")
        inline_start_trial = InlineKeyboardButton('Запустить пробную версию🚀', callback_data='start')
        self.inline_start = InlineKeyboardMarkup().add(inline_start_trial)
        self.info_start = InlineKeyboardMarkup().add(info_kb_start)

        inline_pay_button = InlineKeyboardButton('Оплатить', callback_data='pay')
        self.inline_payment = InlineKeyboardMarkup().add(inline_pay_button)

        info_kb = InlineKeyboardButton('Перейти', url="https://t.me/joinchat/9xQANy2wf-8xOTYy")
        self.inline_info = InlineKeyboardMarkup().add(info_kb)

        review_kb = InlineKeyboardButton('Перейти', url="https://t.me/joinchat/0fLMKjMEVkZjNGI6")
        self.review = InlineKeyboardMarkup().add(review_kb)
        
        signals_kb = InlineKeyboardButton('Узнать', url="https://t.me/+Ja0RxH89SRExZjgy")
        self.signals = InlineKeyboardMarkup().add(signals_kb)

        # admins button
        set_id = KeyboardButton('Выбрать id для пополнения')
        add_admin = KeyboardButton('Добавить администратора')
        list_admin = KeyboardButton('Список администраторов')
        delete_admin = KeyboardButton('Удалить администратора')
        change_trend = KeyboardButton('Изменить текущий тренд')
        message = KeyboardButton('Отправить сообщение')
        ignore_word = KeyboardButton('Игнорирующие слова')
        tokens_from = KeyboardButton('Доход от пользователя')
        self.markup_admin = ReplyKeyboardMarkup(resize_keyboard=True).row(set_id, list_admin).row(add_admin, delete_admin).row(change_trend, ignore_word).row(tokens_from).row(message)

        # back button
        back_button = KeyboardButton('Вернуться в меню')
        self.markup_back = ReplyKeyboardMarkup(resize_keyboard=True).add(back_button)

        # markup button month_days
        button_days = KeyboardButton('7 дней')
        button_months = KeyboardButton('30 дней')
        self.markup_month_day = ReplyKeyboardMarkup(resize_keyboard=True).row(button_days, button_months).add(back_button)

        # payment buttons
        button_qiwi = KeyboardButton('QIWI/Карта')
        button_crypto = KeyboardButton('USDT')
        button_umoney = KeyboardButton('ЮMoney/Карта')
        self.markup_payment_method = ReplyKeyboardMarkup(resize_keyboard=True).row(button_crypto, button_qiwi, button_umoney).add(back_button)

        # button trend
        button_bull = KeyboardButton('✅ BULL TREND')
        button_bear = KeyboardButton('❌ BEAR TREND')
        self.markup_trends = ReplyKeyboardMarkup(resize_keyboard=True).row(button_bull, button_bear).row(back_button)

        # ignore words 
        add_ignore_words = KeyboardButton('Добавить игнорирующее слово')
        del_ignore_words = KeyboardButton('Удалить игнорирующее слово')
        self.markup_ignore_words = ReplyKeyboardMarkup(resize_keyboard=True).row(add_ignore_words, del_ignore_words).add(back_button)
        self.markup_ignore_no_words = ReplyKeyboardMarkup(resize_keyboard=True).add(add_ignore_words, back_button)

        # test 
        test_kb = InlineKeyboardButton('Получить бонус🎁', callback_data='new_test')
        self.testing = InlineKeyboardMarkup().add(test_kb)