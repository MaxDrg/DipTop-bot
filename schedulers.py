import datetime
from config import Config
from database import Database
from buttons import Button
from check_umoney import Check_transaction_umoney

db = Database()
cfg = Config()
btn = Button()
ch = Check_transaction_umoney()

class Scheduler:
    async def Check_send_message():
        with db.conn.cursor() as cursor:
            cursor.execute("""SELECT user_id, time FROM users WHERE send_message = 'false';""")
            users = cursor.fetchall()
            if users == None:
                return
            for user in users:
                if not user[1] == None:
                    if datetime.datetime.strptime(user[1], "%d/%m/%y %H:%M") <= datetime.datetime.now():
                        await db.sendMessage(user_id=user[0], send_message=True)
                        try:
                            await cfg.bot.send_message(user[0], "Пробный период закончился ❗️\n\nПродлите свою подписку, чтобы продолжить получить автоматизированные сигналы", reply_markup=btn.inline_subscription) 
                        except:
                            pass
        
    async def Check_transaction():
        with db.conn.cursor() as cursor_trans:
            cursor_trans.execute("""SELECT transactions.id, users.user_id, transactions.num, transactions.time, transactions.message_id, transactions.source, users.referral_from FROM transactions INNER JOIN users ON transactions.user_id = users.id;""")
            transactions = cursor_trans.fetchall()
            if transactions == None:
                return
            for trans in transactions:
                check_str = ""
                check_from_server = ""

                if str(trans[5]) == "qiwi":
                    check_str = "PAID"
                    check_from_server = str(cfg.p2p.check(bill_id=trans[0]).status)

                elif str(trans[5]) == "umoney":
                    check_str = "success"
                    check_from_server = str(await ch.request(label=trans[0]))
                    
                if check_from_server == check_str or datetime.datetime.strptime(trans[3], "%d/%m/%y %H:%M") <= datetime.datetime.now():
                    if check_str == check_from_server:
                        if not trans[6] == None:
                            await db.add_count_for_analytics(trans[6], trans[2])
                        await db.change_token(trans[1], int(trans[2]), add=True)
                        try:
                            await cfg.bot.send_message(trans[1], "Успешный платёж\nВаш баланс пополнен на %d токенов"%(trans[2]), reply_markup=btn.markup)
                        except:
                            pass
                    try:
                        await cfg.bot.delete_message(chat_id=trans[1], message_id=trans[4])
                    except:
                        pass
                    await db.delete_trans(id=trans[0])