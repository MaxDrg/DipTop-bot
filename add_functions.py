import datetime
from config import Config
from database import Database
from buttons import Button
from forex_python.converter import CurrencyRates
from timed_cache import Cash

usd_rate = CurrencyRates()
cash = Cash()
cfg = Config()
db = Database()
btn = Button()

class Add_function:
    @cash.timed_lru_cache(days=1)
    def Rate_usd(self):
        try:
            usd = usd_rate.get_rate(base_cur='USD', dest_cur='RUB')
            return int(usd)
        except:
            return cfg.error_cost_usd

    # Change times
    async def Change_time(self, delta):
        delta -= datetime.timedelta(delta.days)
        delta -= datetime.timedelta(microseconds=delta.microseconds)
        return str(delta)

    async def delete_previous_order(self, user_id: int):
        with db.conn.cursor() as cursor:
            cursor.execute("""SELECT orders.id_message, users.id FROM orders INNER JOIN users ON orders.id_user = users.id WHERE users.user_id = %s;""", (user_id, ))
            order = cursor.fetchone()
            if order == None:
                return
            else:
                try:
                    await cfg.bot.delete_message(user_id, message_id=int(order[0]))
                except:
                    pass
                await db.delete_orders(id_user=order[1])

    async def delete_this_order(self, user_id_tg: int, user_id: int, message_id: int):
        try:
            await cfg.bot.delete_message(user_id_tg, message_id=message_id)
        except:
            pass
        await db.delete_orders(id_user=user_id)

    async def check_month_or_week(self, week: bool, discount: bool):
        if(week):
            if discount:
                return cfg.discount_cost_per_week, 7
            return cfg.cost_per_week, 7
        else:
            if discount:
                return cfg.discount_cost_per_month, 30
            return cfg.cost_per_month, 30

    async def time_comparison(self, time, num, time_long):
        if time == None:
            pass
        elif datetime.datetime.strptime(time, "%d/%m/%y %H:%M") >= datetime.datetime.now():
            return (datetime.datetime.strptime(time, "%d/%m/%y %H:%M") + datetime.timedelta(days=int(num)*time_long)).strftime("%d/%m/%y %H:%M")
        return (datetime.datetime.now() + datetime.timedelta(days=int(num)*time_long)).strftime("%d/%m/%y %H:%M")

    async def check_who_bought_referrals(self, user_id: int):
        with db.conn.cursor() as cursor:
            cursor.execute("""SELECT user_id FROM users WHERE referral_from = %s UNION SELECT referral FROM referrals WHERE user_from = (SELECT id FROM users WHERE user_id = %s);""", (user_id, user_id ))
            users = cursor.fetchall()
            with db.conn.cursor() as cursor_count_referrals:
                cursor_count_referrals.execute("""SELECT COUNT(referral) FROM referrals WHERE user_from = (SELECT id FROM users WHERE user_id = %s);""", (user_id, ))
                referrals = cursor_count_referrals.fetchone()[0]
                with db.conn.cursor() as cursor_count_buyers:
                    cursor_count_buyers.execute("""SELECT COUNT(user_id) FROM users WHERE referral_from = %s;""", (user_id, ))
                    buyers = cursor_count_buyers.fetchone()[0]
                    buyer_users = len(users) - int(referrals)
                    new_users = len(users) - int(buyers)
                    return buyer_users, new_users, len(users) - buyer_users - new_users

    # Check digit num
    async def Chek_digit(self, id, text, from_admin = False):
        if from_admin:
            markup = btn.markup_admin 
        else:
            markup = btn.markup
        if not text.isdigit():
            await cfg.bot.send_message(id, "Вы не ввели число :(", reply_markup=markup)
            return True
        elif int(text) <= 0:
            await cfg.bot.send_message(id, "Вы ввели некорректное число :(", reply_markup=markup)
            return True
        else: 
            return False

    # Ignore words
    async def ignore_words(self):
        ignore_words = await cfg.ignore_words_json.get_ignore_words(param='r')
        words = ''
        num = 0
        for ignore_word in ignore_words:
            num += 1
            words += "%s. %s\n"%(str(num), ignore_word)
        if words == '':
            return "В боте нет слов исключений !"
        return words

    async def get_ignore_word_index(self, index):
        ignore_words = await cfg.ignore_words_json.get_ignore_words(param='r')
        if not int(index) > int(len(ignore_words)):
            await cfg.ignore_words_json.get_ignore_words(param='d', index=int(index)-1)
            return True
        else:
            return False

    async def Check_ignore_words(self, text: str):
        ignore_words = await cfg.ignore_words_json.get_ignore_words(param='r')
        for ignore_word in ignore_words:
            if ignore_word.lower() in text.lower():
                return False
        return True