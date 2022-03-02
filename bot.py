import asyncio
import datetime
import logging
import aioschedule
from config import Config
from database import Database
from buttons import Button
from schedulers import Scheduler
from aiogram import executor, types
from add_functions import Add_function
from states import States
from yoomoney import Quickpay
from check import Check
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

db = Database()
cfg = Config()
btn = Button()
add_func = Add_function()
check = Check()

# Configure logging
logging.basicConfig(level=logging.INFO)

@cfg.dp.message_handler(commands="start")
async def Start(message: types.Message):
    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT time, tokens FROM users WHERE user_id=%s;""", (message.from_user.id, ))
        user = cursor.fetchone()
        if not user == None:
            if datetime.datetime.strptime(user[0], "%d/%m/%y %H:%M") >= datetime.datetime.now():
                time = datetime.datetime.strptime(user[0], "%d/%m/%y %H:%M") - datetime.datetime.now()
                await cfg.bot.send_message(message.from_user.id, "Снова привет %s !\nТы уже запускал этого бота.\nВаша подписка действует ещё "%(str(message.from_user.first_name)) + 
                str(time.days) + " дн. " + await add_func.Change_time(time) +
                "\nВаш баланс: %d токенов"%(int(user[1])), reply_markup=btn.markup)
            else: 
                await cfg.bot.send_message(message.from_user.id, "Снова привет %s !\nТы уже запускал этого бота.\nТвоя подписка не активна !\nДля использования бота её необходимо продлить"%(str(message.from_user.first_name)) +
                "\nВаш баланс: %d токенов"%(int(user[1])), reply_markup=btn.markup)
            return
        elif " " in message.text:
            referrer = message.text.split()[1]
            if await check.onStart(referrer, message.from_user.id):
                await db.add_referral(message.from_user.id, referrer)
                if not await check.isReferrer(referrer):
                    await db.add_referral_for_analytics(referrer)
                await cfg.bot.send_message(message.from_user.id, "Привет {} !\n\nПоздравляю, вы перешли по нашей реферальной ссылке и получаете скидку 10% на первое продление подписки.".format(str(message.from_user.first_name)) +
                                                                "\n\nЭтот бот имеет пробную версию.\n\nЧтобы её активировать и начать использование, нажмите на кнопку." +
                                                                "\n\nРекомендуем вам, после активации, прочесть правила использования бота.", reply_markup=btn.inline_start)
                try:
                    await cfg.bot.send_message(referrer, "Пользователь {} перешёл по вашей реферальной ссылке.\n\nТеперь вы будете получать по 10% токенов с каждой его покупки подписки.".format(str(message.from_user.first_name)))
                except:
                    pass
                return
        await cfg.bot.send_message(message.from_user.id, "Привет {} !\n\nЭтот бот имеет пробную версию.\n\nЧтобы её активировать и начать использование, нажмите на кнопку.".format(str(message.from_user.first_name)) + 
        "\n\nРекомендуем вам, после активации, прочесть правила использования бота.", reply_markup=btn.inline_start)

@cfg.dp.callback_query_handler(text="start")
async def process_callback_start(callback_query: types.CallbackQuery):
    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT EXISTS(SELECT user_id FROM users WHERE user_id=%s);""",(callback_query.from_user.id, ))
        user = cursor.fetchone()
        if user[0]: # Found in database
            await cfg.bot.answer_callback_query(callback_query_id=callback_query.id, text="Вы уже активировали пробную подписку")
        else:
            await cfg.bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
            
            await db.table_users(user_id=int(callback_query.from_user.id), 
            username=str(callback_query.from_user.username), 
            first_name=str(callback_query.from_user.first_name),
            send_message=False, 
            referral=await check.isReferral(callback_query.from_user.id))
            await cfg.bot.send_message(callback_query.from_user.id, "Отлично!" +
                                                                    "\nВам предоставлен 1 сигнал от торгового бота - Бесплатно!" +
                                                                    "\n\n🔄Ожидайте, в скором времени сюда будут поступать автоматизированные сигналы от бота, старайтесь не пропустить🚨" + 
                                                                    "\n\nПо любым вопросам обращайтесь в нашу поддержку - @diptop_support", reply_markup=btn.markup)
            await cfg.bot.send_message(callback_query.from_user.id, "А пока внимательно изучите правила использования бота:", reply_markup=btn.info_start)

@cfg.dp.channel_post_handler(content_types='audio')
async def Send_audio(message):
    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT user_id FROM users WHERE send_message=false;""")
        users = cursor.fetchall()
        if users == None:
            return
        for user in users:
            try:
                await cfg.bot.send_audio(user[0], message.audio.file_id)
            except:
                pass

@cfg.dp.channel_post_handler(content_types='document')
async def Send_document(message):
    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT user_id FROM users WHERE send_message=false;""")
        users = cursor.fetchall()
        if users == None:
            return
        for user in users:
            try:
                await cfg.bot.send_document(user[0], message.document.file_id)
            except:
                pass

@cfg.dp.channel_post_handler(content_types='voice')
async def Send_voice(message):
    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT user_id FROM users WHERE send_message=false;""")
        users = cursor.fetchall()
        if users == None:
            return
        for user in users:
            try:
                await cfg.bot.send_voice(user[0], message.voice.file_id)
            except:
                pass

@cfg.dp.channel_post_handler(content_types='video')
async def Send_video(message):
    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT user_id FROM users WHERE send_message=false;""")
        users = cursor.fetchall()
        if users == None:
            return
        for user in users:
            try:
                await cfg.bot.send_video(user[0], message.video.file_id)
            except:
                pass

@cfg.dp.channel_post_handler(content_types='photo')
async def Send_photo(message):
    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT user_id FROM users WHERE send_message=false;""")
        users = cursor.fetchall()
        if users == None:
            return
        for user in users:
            try:
                await cfg.bot.send_photo(user[0], message.photo[-1].file_id)
            except:
                pass

@cfg.dp.channel_post_handler(content_types='text')
async def Send_text(message):
    if await add_func.Check_ignore_words(message.text):
        if message.text == "✅ BULL TREND":
            await cfg.trend_json.get_trend(param='w', new_trend="BULL TREND")
        elif message.text == "❌ BEAR TREND":
            await cfg.trend_json.get_trend(param='w', new_trend="BEAR TREND")
        with db.conn.cursor() as cursor:
            cursor.execute("""SELECT user_id, time FROM users WHERE send_message=false;""")
            users = cursor.fetchall()
            if users == None:
                return
            for user in users:
                try:
                    await cfg.bot.send_message(user[0], message.text)
                except:
                    pass
                if user[1] == None:
                    await db.sendMessage(user_id=user[0], send_message=True)
                    try:
                        await cfg.bot.send_message(user[0], "Пробный период закончился ❗️\n\nПродлите свою подписку, чтобы продолжить получить автоматизированные сигналы", reply_markup=btn.inline_subscription) 
                    except:
                        pass

@cfg.dp.message_handler(lambda message: message.text == 'Личный кабинет🏠') 
async def Last_time(message: types.Message):
    if await check.isUser(message.from_user.id):
        discount = ""
        if await check.isReferral(message.from_user.id):
            discount = "\n\nНапоминаем, что для вас действует акционное предложение: 1 неделя = 3 токена"
        with db.conn.cursor() as cursor:
            cursor.execute("""SELECT time, send_message, tokens FROM users WHERE user_id = %s;""", (message.from_user.id, ))
            user = cursor.fetchone()
            buyers, new_users, active_users = await add_func.check_who_bought_referrals(message.from_user.id)
            if user[1]:
                await cfg.bot.send_message(message.from_user.id, "Личный кабинет DipTop" +
                "\n\nВаш персональный код пользователя: {}".format(message.from_user.id) +
                "\n\nВаша подписка закончилась !\nПополните баланс и продлите её.\n\nВаш баланс: {} токенов".format(int(user[2])) +
                f"\n\nРефералы, которые перешли по вашей ссылке: {new_users}" +
                f"\n\nРефералы, которые перешли по вашей ссылке и активировали бота: {active_users}" +
                "\n\nРефералы, которые перешли по вашей ссылке и воспользовались скидкой: %d%s"%(buyers, discount), reply_markup=btn.inline_buy)
            elif user[0] == None:
                await cfg.bot.send_message(message.from_user.id, "Личный кабинет DipTop" +
                "\n\nВаш персональный код пользователя: {}".format(message.from_user.id) +
                "\n\nВаш баланс: {} токенов".format(int(user[2])) +
                f"\n\nРефералы, которые перешли по вашей ссылке: {new_users}" +
                f"\n\nРефералы, которые перешли по вашей ссылке и активировали бота: {active_users}" +
                "\n\nРефералы, которые перешли по вашей ссылке и воспользовались скидкой: %d%s"%(buyers, discount), reply_markup=btn.inline_buy)
            else:
                time = datetime.datetime.strptime(user[0], "%d/%m/%y %H:%M") - datetime.datetime.now()
                await cfg.bot.send_message(message.from_user.id, "Личный кабинет DipTop" +
                "\n\nВаш персональный код пользователя: {}".format(message.from_user.id) +
                "\n\nВаша подписка истекает через " + 
                str(time.days) + " дн. " + await add_func.Change_time(time) +
                "\n\nВаш баланс: {} токенов".format(int(user[2])) +
                f"\n\nРефералы, которые перешли по вашей ссылке: {new_users}" +
                f"\n\nРефералы, которые перешли по вашей ссылке и активировали бота: {active_users}" +
                "\n\nРефералы, которые перешли по вашей ссылке и воспользовались скидкой: %d%s"%(buyers, discount), reply_markup=btn.inline_buy
                )

@cfg.dp.callback_query_handler(text="token")
async def process_callback_add_tokens(callback_query: types.CallbackQuery):
    await cfg.bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT tokens FROM users WHERE user_id = %s;""", (callback_query.from_user.id, ))
        user = cursor.fetchone()
        await cfg.bot.send_message(callback_query.from_user.id, "%s у вас на счету %d токенов\nЦена 1 токена = 1$ = %d руб."%(callback_query.from_user.first_name, user[0], add_func.Rate_usd()))
        await cfg.bot.send_message(callback_query.from_user.id, "Укажите удобный для вас метод пополнения:", reply_markup=btn.markup_payment_method)
        await States.Set_payment_method.set()

@cfg.dp.message_handler(state=States.Set_payment_method) 
async def Set_payment_methods(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await state.finish()
        await cfg.bot.send_message(message.from_user.id, "Вы в главном меню", reply_markup=btn.markup)
        return
    elif message.text == "QIWI/Карта":
        await cfg.bot.send_message(message.from_user.id, "Введите насколько токенов вы хотите пополнить кошелёк: ", reply_markup=btn.markup_back)
        await States.Set_tokens.set()
    elif message.text == "USDT":
        await cfg.bot.send_message(message.from_user.id, "Введите насколько токенов вы хотите пополнить кошелёк: ", reply_markup=btn.markup_back)
        await States.Set_tokens_for_tether.set()
    elif message.text == "ЮMoney/Карта":
        await cfg.bot.send_message(message.from_user.id, "Введите насколько токенов вы хотите пополнить кошелёк: ", reply_markup=btn.markup_back)
        await States.Set_umoney.set()

@cfg.dp.message_handler(state=States.Set_umoney) 
async def Set_tokens_for_crypto(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await state.finish()
        await cfg.bot.send_message(message.from_user.id, "Вы в главном меню", reply_markup=btn.markup)
        return
    elif await add_func.Chek_digit(message.from_user.id, message.text):
        await state.finish()
        return
    await cfg.bot.send_message(message.from_user.id, "Пополнение счёта на {} токенов, будет составлять {} руб.".format(message.text, str(int(message.text)*add_func.Rate_usd())) +
    "\n\nПользователям с Украины для оплаты необходимо использовать VPN", reply_markup=btn.markup)

    amount = int(message.text)*add_func.Rate_usd()

    id = await db.table_trans(user_id = int(message.from_user.id), 
                num = int(message.text), 
                time = (datetime.datetime.now() + datetime.timedelta(minutes=15)).strftime("%d/%m/%y %H:%M"),
                source="umoney")

    quickpay = Quickpay(
            receiver=cfg.umoney,
            quickpay_form="shop",
            targets="Покупка %d токенов"%(int(message.text)),
            paymentType="SB",
            sum=amount,
            label=id
            )

    inline_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Пополнить счет ЮMoney', url=quickpay.redirected_url))
    mess = await cfg.bot.send_message(message.from_user.id, "Ссылка на счёт будет активна 15 мин.", reply_markup=inline_kb)

    await db.add_message_for_trans(id = id, message_id = mess.message_id)
    await state.finish()

@cfg.dp.message_handler(state=States.Set_tokens_for_tether) 
async def Set_tokens_for_crypto(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await state.finish()
        await cfg.bot.send_message(message.from_user.id, "Вы в главном меню", reply_markup=btn.markup)
        return
    elif await add_func.Chek_digit(message.from_user.id, message.text):
        await state.finish()
        return
    await cfg.bot.send_photo(message.from_user.id, photo=types.InputFile(cfg.photo_crypto),
                            caption="Для пополнения баланса заплатите %s$\n\n"%(message.text) +
                            "Сеть: Tron (TRC20)\nTYW8aXcotnssyQeQyB6xoayGKZtTC8Ty36\n\n" +
                            "После оплаты, пожалуйста, пришлите подтверждение @diptop_support\n\n" +
                            "Вместе с подтверждением отправьте ваш уникальный номер\n\n" +
                            "Ваш уникальный номер: %s"%(message.from_user.id), 
                            reply_to_message_id=message.message_id,
                            reply_markup=btn.markup)
    await state.finish()

@cfg.dp.message_handler(state=States.Set_tokens)
async def Set_tokens(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await state.finish()
        await cfg.bot.send_message(message.from_user.id, "Вы в главном меню", reply_markup=btn.markup)
        return
    elif await add_func.Chek_digit(message.from_user.id, message.text):
        await state.finish()
        return

    await cfg.bot.send_message(message.from_user.id, "Пополнение счёта на %s токенов, будет составлять %s руб."%(message.text, str(int(message.text)*add_func.Rate_usd())), reply_markup=btn.markup)

    amount = int(message.text)*add_func.Rate_usd()

    id = await db.table_trans(user_id = int(message.from_user.id), 
                num = int(message.text), 
                time = (datetime.datetime.now() + datetime.timedelta(minutes=15)).strftime("%d/%m/%y %H:%M"),
                source="qiwi")

    new_bill = cfg.p2p.bill(bill_id=id, amount=amount, lifetime=15, currency="RUB", comment="Покупка %d токенов"%(int(message.text)))
    inline_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Пополнить счет QIWI/Карта', url=new_bill.pay_url))
    mess = await cfg.bot.send_message(message.from_user.id, "Ссылка на счёт будет активна 15 мин.", reply_markup=inline_kb)

    await db.add_message_for_trans(id = id, message_id = mess.message_id)
    await state.finish()

@cfg.dp.message_handler(lambda message: message.text == 'Правила📋') 
async def Add_balance(message: types.Message):
    if await check.isUser(message.from_user.id):
        await cfg.bot.send_message(message.from_user.id, "Канал с правилами:", reply_markup=btn.inline_info)

#@cfg.dp.message_handler(lambda message: message.text == 'Торговые пары💵') 
#async def Add_balance(message: types.Message):
#    if await check.isUser(message.from_user.id):
#        await cfg.bot.send_message(message.from_user.id, "🔍 Список монет отлеживающихся ботом" +
#        "\n\n🔘 BTC/USDT" +
#        "\n🔘 FIL/USDT" +
#        "\n🔘 FTM/USDT" +
#        "\n🔘 WAVES/USDT" +
#        "\n🔘 TRX/USDT" +
#        "\n🔘 ADA/USDT" +
#        "\n🔘 ENJ/USDT" +
#        "\n🔘 ICP/USDT" +
#        "\n🔘 VET/USDT" +
#        "\n🔘 CHZ/USDT")
@cfg.dp.message_handler(lambda message: message.text == 'Отработка сигналов🚨') 
async def Current_signals(message: types.Message):
    if await check.isUser(message.from_user.id):
        await cfg.bot.send_message(message.from_user.id, "Узнать отработку сигналов:", reply_markup=btn.signals)

@cfg.dp.message_handler(lambda message: message.text == 'Отзывы❗️') 
async def review(message: types.Message):
    if await check.isUser(message.from_user.id):
        await cfg.bot.send_message(message.from_user.id, "Наши отзывы:", reply_markup=btn.review)

@cfg.dp.message_handler(lambda message: message.text == 'Поддержка⚒') 
async def support(message: types.Message):
    if await check.isUser(message.from_user.id):
        await cfg.bot.send_message(message.from_user.id, "Поддержка: @diptop_support")

#@cfg.dp.message_handler(lambda message: message.text == 'Тренд📊') 
#async def Current_trend(message: types.Message):
#    if await check.isUser(message.from_user.id):
#        read_trend = await cfg.trend_json.get_trend(param='r')
#        current_trend = ''
#        if read_trend == "BULL TREND":
#            current_trend = '✅ BULL TREND'
#        else:
#            current_trend = '❌ BEAR TREND'
#        await cfg.bot.send_message(message.from_user.id, "Текущий тренд: %s"%(current_trend))

@cfg.dp.message_handler(lambda message: message.text == 'Реферальная система👥') 
async def support(message: types.Message):
    if await check.isUser(message.from_user.id):
        await cfg.bot.send_message(message.from_user.id, "Реферальная система DipTop\n\nВы можете привлекать в бот новых подписчиков через свою личную реферальную ссылку" +
                                                    "\n\nВы будете получать по 10% с каждого продления подписки тех пользователей, которые воспользуются вашей ссылкой перед запуском бота." +
                                                    "\n\nКаждый новый пользователь, который воспользуется вашей ссылкой, получит скидку 10% на первое продление подписки" +
                                                    "\n\nВаша реферальная ссылка:\nhttps://t.me/DipTop_Trade_bot?start={}".format(message.from_user.id))

@cfg.dp.callback_query_handler(text="subscription")
async def process_callback_add_subscription(callback_query: types.CallbackQuery):
    await cfg.bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    if await check.isReferral(callback_query.from_user.id):
        await cfg.bot.send_message(callback_query.from_user.id, "1 неделя подписки = {0} токенов = {0}$\n1 месяц подписки = {1} токенов = {1}$\n\nС учётом вашей скидки:\n\n1 неделя подписки = {2} токенов = {2}$\n1 месяц подписки = {3} токенов = {3}$\n\nКак вы хотите продлить свою подписку?".format(cfg.cost_per_week, cfg.cost_per_month, cfg.discount_cost_per_week, cfg.discount_cost_per_month), reply_markup=btn.markup_month_day)
    else:
        await cfg.bot.send_message(callback_query.from_user.id, "1 неделя подписки = {0} токенов = {0}$\n1 месяц подписки = {1} токенов = {1}$\n\nКак вы хотите продлить свою подписку?".format(cfg.cost_per_week, cfg.cost_per_month), reply_markup=btn.markup_month_day)
    await States.Set_delta.set()

@cfg.dp.message_handler(state=States.Set_delta)
async def choose_method(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await state.finish()
        await cfg.bot.send_message(message.from_user.id, "Вы в главном меню", reply_markup=btn.markup)
        return
    elif message.text == "30 дней":
        await cfg.bot.send_message(message.from_user.id, "Введите к-во месяцев на которое хотите продлить подписку:", reply_markup=btn.markup_back)
        await States.Enter_months.set()
    elif message.text == "7 дней":
        await cfg.bot.send_message(message.from_user.id, "Введите к-во недель на которое хотите продлить подписку:", reply_markup=btn.markup_back)
        await States.Enter_weeks.set()
    else:
        await cfg.bot.send_message(message.from_user.id, "Извините, я вас не понимаю :(", reply_markup=btn.markup)
        await state.finish()

@cfg.dp.message_handler(state=States.Enter_months)
async def edit_months(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await state.finish()
        await cfg.bot.send_message(message.from_user.id, "Вы в главном меню", reply_markup=btn.markup)
        return
    elif await add_func.Chek_digit(message.from_user.id, message.text):
        await state.finish()
        return
    cost = 0
    if await check.isReferral(message.from_user.id):
        cost = cfg.discount_cost_per_month
    else:
        cost = cfg.cost_per_month
    await cfg.bot.send_message(message.from_user.id, "Вы собираетесь продлить вашу подписку на %d мес."%(int(message.text)), reply_markup=btn.markup)
    mess = await cfg.bot.send_message(message.from_user.id, "Эта операция будет стоить %d токенов."%(int(message.text)*cost),
    reply_markup=btn.inline_payment)
    await add_func.delete_previous_order(message.from_user.id)
    await db.table_orders(
        id_user=message.from_user.id,
        id_message=mess.message_id,
        week=False,
        num=int(message.text)
    )
    await state.finish()

@cfg.dp.message_handler(state=States.Enter_weeks)
async def edit_days(message: types.Message, state: FSMContext):
    if message.text == 'Вернуться в меню':
        await state.finish()
        await cfg.bot.send_message(message.from_user.id, "Вы в главном меню", reply_markup=btn.markup)
        return
    elif await add_func.Chek_digit(message.from_user.id, message.text):
        await state.finish()
        return
    cost = 0
    if await check.isReferral(message.from_user.id):
        cost = cfg.discount_cost_per_week
    else:
        cost = cfg.cost_per_week
    await cfg.bot.send_message(message.from_user.id, "Вы собираетесь продлить вашу подписку на %d нед."%(int(message.text)), reply_markup=btn.markup)
    mess = await cfg.bot.send_message(message.from_user.id, "Эта операция будет стоить %d токенов."%(int(message.text)*cost),
    reply_markup=btn.inline_payment)
    await add_func.delete_previous_order(message.from_user.id)
    await db.table_orders(
        id_user=message.from_user.id,
        id_message=mess.message_id,
        week=True,
        num=int(message.text)
    )
    await state.finish()
    
@cfg.dp.callback_query_handler(text="pay")
async def callback_button_pay(callback_query: types.CallbackQuery):
    with db.conn.cursor() as cursor_order:
        cursor_order.execute("""SELECT orders.week, orders.num, users.time, users.tokens, users.id, orders.id_message, users.referral_from FROM orders INNER JOIN users ON orders.id_user = users.id WHERE users.user_id = %s;""", (callback_query.from_user.id, ))
        order = cursor_order.fetchone()
        discount = False
        if await check.isReferral(callback_query.from_user.id):
            discount = True
        cost, time_long = await add_func.check_month_or_week(order[0], discount)
        if order[3] >= order[1] * cost:  
            await db.delete_referral(callback_query.from_user.id)
            if not order[6] == None:
                if order[0]:
                    await db.change_token(tokens = int(order[1]) * cfg.cashback_from_week, user_id = order[6], add = True)
                    try:
                        await cfg.bot.send_message(order[6], "Вам на счёт было начислено %d токенов от пользователей, которые перешли по вашей реферальной ссылке."%(int(order[1]) * cfg.cashback_from_week))
                    except:
                        pass
                else:
                    await db.change_token(tokens = int(order[1]) * cfg.cashback_from_month, user_id = order[6], add = True)
                    try:
                        await cfg.bot.send_message(order[6], "Вам на счёт было начислено %d токенов от пользователей, которые перешли по вашей реферальной ссылке."%(int(order[1]) * cfg.cashback_from_month))
                    except:
                        pass
            await db.change_token(
                user_id = callback_query.from_user.id,
                tokens = int(order[3]) - int(order[1]) * cost
            )
            await db.add_time(
                user_id = callback_query.from_user.id,
                time = await add_func.time_comparison(order[2], order[1], time_long)
            )
            await db.sendMessage(
                user_id = callback_query.from_user.id,
                send_message = False
            )
            await add_func.delete_this_order(user_id_tg=callback_query.from_user.id,
                                            user_id=order[4],
                                            message_id=order[5])
            await cfg.bot.send_message(callback_query.from_user.id, "«✅ Подписка успешно продлена!\n\n" +
                                                                    "🔄 Ожидайте, в скором времени сюда будут поступать автоматизированные сигналы от бота.\n" + 
                                                                    "По любым вопросам обращайтесь в нашу поддержку - @diptop_support»", reply_markup=btn.markup)
            return
        else:
            await add_func.delete_this_order(user_id_tg=callback_query.from_user.id,
                                            user_id=order[4],
                                            message_id=order[5])
            await cfg.bot.send_message(callback_query.from_user.id, "Недостаточно токенов для продления подписки !", reply_markup=btn.markup)
            await cfg.bot.send_message(callback_query.from_user.id, "Для совершения операции пополните счёт", reply_markup=btn.inline_token)
            return

# start admins code

@cfg.dp.message_handler(commands="admin")
async def admin(message: types.Message):
    if await check.isAdmin(message.from_user.id):
        await States.Admin.set()
        await cfg.bot.send_message(message.from_user.id, "Активирован режим администратора\n\nВсего пользователей в боте: {}".format(int(await db.get_count())) +
        "\n\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)

@cfg.dp.message_handler(lambda message: message.text == 'Выбрать id для пополнения', state=States.Admin) 
async def set_id(message: types.Message):
    if await check.isAdmin(message.from_user.id):
        await cfg.bot.send_message(message.from_user.id, "Введите номер пользователя, которому хотите добавить токенов", reply_markup=btn.markup_back)
        await States.Set_user_id.set()
    else:
        await cfg.bot.send_message(message.from_user.id, "Вы не являетесь администратором бота\nНажмите /stop для выхода", reply_markup=types.ReplyKeyboardRemove())
    
@cfg.dp.message_handler(lambda message: message.text == 'Добавить администратора', state=States.Admin) 
async def add_admin(message: types.Message):
    if await check.isAdmin(message.from_user.id):
        await cfg.bot.send_message(message.from_user.id, "Перешлите сообщение пользователя, которого хотите добавить в администраторы", reply_markup=btn.markup_back)
        await States.Add_admin_message.set()
    else:
        await cfg.bot.send_message(message.from_user.id, "Вы не являетесь администратором бота\nНажмите /stop для выхода", reply_markup=types.ReplyKeyboardRemove())

@cfg.dp.message_handler(lambda message: message.text == 'Изменить текущий тренд', state=States.Admin) 
async def change_trend(message: types.Message):
    if await check.isAdmin(message.from_user.id):
        await cfg.bot.send_message(message.from_user.id, "Какой тренд назначить текущим?", reply_markup=btn.markup_trends)
        await States.Set_trend.set()
    else:
        await cfg.bot.send_message(message.from_user.id, "Вы не являетесь администратором бота\nНажмите /stop для выхода", reply_markup=types.ReplyKeyboardRemove())

@cfg.dp.message_handler(state=States.Set_trend)
async def message_deleted_admin(message: types.Message):
    if message.text == "Вернуться в меню":
        await cfg.bot.send_message(message.from_user.id, "Вы в режиме администратора\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)
        await States.Admin.set()
        return
    elif message.text == "❌ BEAR TREND":
        await cfg.bot.send_message(message.from_user.id, "Выбран новый тренд: BEAR TREND")
        await cfg.trend_json.get_trend(param='w', new_trend="BEAR TREND")
        await cfg.bot.send_message(message.from_user.id, "Вы в режиме администратора\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)
        await States.Admin.set()
        return
    elif message.text == "✅ BULL TREND":
        await cfg.bot.send_message(message.from_user.id, "Выбран новый тренд: BULL TREND")
        await cfg.trend_json.get_trend(param='w', new_trend="BULL TREND")
        await cfg.bot.send_message(message.from_user.id, "Вы в режиме администратора\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)
        await States.Admin.set()
        return

@cfg.dp.message_handler(lambda message: message.text == 'Список администраторов', state=States.Admin) 
async def add_admin(message: types.Message):
    if await check.isAdmin(message.from_user.id):
        with db.conn.cursor() as cursor:
            cursor.execute("""SELECT admin_id, admins_name FROM admins;""")
            admins = cursor.fetchall()
            if admins == None:
                return
            for admin in admins:
                try:
                    await cfg.bot.send_message(message.from_user.id, "Имя: %s\nID: %s"%(admin[1], admin[0]))
                except:
                    pass
    else:
        await cfg.bot.send_message(message.from_user.id, "Вы не являетесь администратором бота\nНажмите /stop для выхода", reply_markup=types.ReplyKeyboardRemove())

@cfg.dp.message_handler(lambda message: message.text == 'Удалить администратора', state=States.Admin) 
async def delete_admin(message: types.Message):
    if await check.isAdmin(message.from_user.id):
        await cfg.bot.send_message(message.from_user.id, "Введите ID администратора, которого хотите удалить", reply_markup=btn.markup_back)
        await States.Delete_admin_message.set()
    else:
        await cfg.bot.send_message(message.from_user.id, "Вы не являетесь администратором бота\nНажмите /stop для выхода", reply_markup=types.ReplyKeyboardRemove())

@cfg.dp.message_handler(state=States.Add_admin_message, content_types=['game', 'photo', 'video','voice', 'audio', 'text', 'document', 'sticker', 'invoice']) 
async def message_new_admin(message):
    try:
        if message.text == "Вернуться в меню":
            await cfg.bot.send_message(message.from_user.id, "Вы в режиме администратора\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)
            await States.Admin.set()
        elif await check.isAdmin(message.forward_from.id):
            await cfg.bot.send_message(message.from_user.id, "Этот пользователь уже является администратором", reply_markup=btn.markup_admin)
            await States.Admin.set()
        else:
            await db.add_admins(message.forward_from.id, message.forward_from.first_name)
            await cfg.bot.send_message(message.from_user.id, "Пользователь %s добавлен в качестве администратора"%(message.forward_from.first_name), reply_markup=btn.markup_admin)
            await States.Admin.set()
    except:
        await cfg.bot.send_message(message.from_user.id, "Это не пересланное сообщение или пользователь скрыл свой профиль!\nЗапросите и пользователя раскрыть свой аккаунт на время добавление в администраторы", reply_markup=btn.markup_admin)
        await States.Admin.set()

@cfg.dp.message_handler(state=States.Delete_admin_message)
async def message_deleted_admin(message: types.Message):
    if message.text == "Вернуться в меню":
        await cfg.bot.send_message(message.from_user.id, "Вы в режиме администратора\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)
        await States.Admin.set()
        return
    elif await check.isAdmin(message.text):
        if message.text == message.from_user.id:
            await cfg.bot.send_message(message.from_user.id, "Вы не можете удалить сами себя из администраторов", reply_markup=btn.markup_admin)
            await States.Admin.set()
        else:
            await db.delete_admins(message.text)
            await cfg.bot.send_message(message.from_user.id, "Пользователь удалён из администраторов", reply_markup=btn.markup_admin)
            await States.Admin.set()
    else: 
        await cfg.bot.send_message(message.from_user.id, "Такого пользователя нет среди администраторов", reply_markup=btn.markup_admin)
        await States.Admin.set()

@cfg.dp.message_handler(state=States.Set_user_id) 
async def add_token_for_user(message: types.Message):
    if message.text == "Вернуться в меню":
        await cfg.bot.send_message(message.from_user.id, "Вы в режиме администратора\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)
        await States.Admin.set()
    elif await check.isUser(message.text):
        await db.set_user_token(message.text, message.from_user.id)
        await cfg.bot.send_message(message.from_user.id, "Введите число токенов для пополнения:", reply_markup=btn.markup_back)
        await States.Add_tokens_for_user.set()
    else:
        await cfg.bot.send_message(message.from_user.id, "Пользователь не найден в базе!", reply_markup=btn.markup_admin)
        await States.Admin.set()

@cfg.dp.message_handler(state=States.Add_tokens_for_user) 
async def add_token_for_user(message: types.Message):
    if message.text == 'Вернуться в меню':
        await States.Admin.set()
        await cfg.bot.send_message(message.from_user.id, "Вы в режиме администратора\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)
        return
    elif await add_func.Chek_digit(message.from_user.id, message.text, from_admin=True):
        await States.Admin.set()
        return

    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT users.user_id, users.referral_from FROM admins INNER JOIN users ON admins.id_user = users.id WHERE admins.admin_id = %s;""", (message.from_user.id, ))
        admins_user = cursor.fetchone()
        await db.change_token(
            user_id = admins_user[0], 
            tokens = int(message.text),
            add=True
            )
        if not admins_user[1] == None:
            await db.add_count_for_analytics(admins_user[1], int(message.text))
        await States.Admin.set()
        try:
            await cfg.bot.send_message(admins_user[0], "Ваш счёт пополнен на %d токен."%(int(message.text)))
        except:
            await cfg.bot.send_message(message.from_user.id, "Невозможно отправить пользователю сообщение с подтверждением!")
        await cfg.bot.send_message(message.from_user.id, "Операция успешна!", reply_markup=btn.markup_admin)

@cfg.dp.message_handler(state=States.Admin, commands="stop")
async def admin(message: types.Message, state: FSMContext):
    await state.finish()
    await cfg.bot.send_message(message.from_user.id, "Выход из режима администратора", reply_markup=btn.markup)

@cfg.dp.message_handler(lambda message: message.text == 'Отправить сообщение', state=States.Admin) 
async def Send_message_from_admin(message: types.Message):
    if await check.isAdmin(message.from_user.id):
        await cfg.bot.send_message(message.from_user.id, "Вы находитесь в режиме для отправки сообщений пользователям\n\n!!!\n\nВСЕ ВАШИ СООБЩЕНИЯ БУДУТ ОТПРАВЛЕНЫ АКТИВНЫМ ПОДПИСЧИКАМ БОТА\n\n!!!", reply_markup=btn.markup_back)
        await States.Admin_send_message.set()
    else:
        await cfg.bot.send_message(message.from_user.id, "Вы не являетесь администратором бота\nНажмите /stop для выхода", reply_markup=types.ReplyKeyboardRemove())

@cfg.dp.message_handler(state=States.Admin_send_message, content_types='audio')
async def Send_audio(message):
    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT user_id FROM users WHERE send_message=false;""")
        users = cursor.fetchall()
        if users == None:
            return
        for user in users:
            try:
                await cfg.bot.send_audio(user[0], message.audio.file_id)
            except:
                pass

@cfg.dp.message_handler(state=States.Admin_send_message, content_types='document')
async def Send_document(message):
    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT user_id FROM users WHERE send_message=false;""")
        users = cursor.fetchall()
        if users == None:
            return
        for user in users:
            try:
                await cfg.bot.send_document(user[0], message.document.file_id)
            except:
                pass

@cfg.dp.message_handler(state=States.Admin_send_message, content_types='voice')
async def Send_voice(message):
    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT user_id FROM users WHERE send_message=false;""")
        users = cursor.fetchall()
        if users == None:
            return
        for user in users:
            try:
                await cfg.bot.send_voice(user[0], message.voice.file_id)
            except:
                pass

@cfg.dp.message_handler(state=States.Admin_send_message, content_types='video')
async def Send_video(message):
    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT user_id FROM users WHERE send_message=false;""")
        users = cursor.fetchall()
        if users == None:
            return
        for user in users:
            try:
                await cfg.bot.send_video(user[0], message.video.file_id)
            except:
                pass

@cfg.dp.message_handler(state=States.Admin_send_message, content_types='photo')
async def Send_photo(message):
    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT user_id FROM users WHERE send_message=false;""")
        users = cursor.fetchall()
        if users == None:
            return
        for user in users:
            try:
                await cfg.bot.send_photo(user[0], message.photo[-1].file_id)
            except:
                pass
# test
@cfg.dp.message_handler(state=States.Admin_send_message, content_types='text')
async def Send_text(message):
    if message.text == "Вернуться в меню":
        await cfg.bot.send_message(message.from_user.id, "Вы в режиме администратора\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)
        await States.Admin.set()
        return
    if message.text == "Дорогие пользователи":
        with db.conn.cursor() as cursor:
            cursor.execute("""SELECT user_id FROM users;""")
            users = cursor.fetchall()
            if users == None:
                return
            for user in users:
                if not user[0] == 5037418573 or not user[0] == '5037418573':
                    try:
                        txt = "Для дополнительного бонуса, напишите в поддержку - «+» и узнайте подробности\n\n@diptop_support"
                        await cfg.bot.send_message(user[0], txt)
                    except:
                        pass
        return
    with db.conn.cursor() as cursor:
        cursor.execute("""SELECT user_id FROM users WHERE send_message=false;""")
        users = cursor.fetchall()
        if users == None:
            return
        for user in users:
            try:
                await cfg.bot.send_message(user[0], message.text)
            except:
                pass

@cfg.dp.callback_query_handler(text="new_test")
async def callback_button_pay(callback_query: types.CallbackQuery):
    await cfg.bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await cfg.bot.send_photo(callback_query.from_user.id, photo=types.InputFile(cfg.photo_crypto),
                            caption="Пополните свой баланс\n\n" +
                            "Сеть: Tron (TRC20)\nTYW8aXcotnssyQeQyB6xoayGKZtTC8Ty36\n\n" +
                            "После оплаты, пожалуйста, пришлите подтверждение @diptop_support\n\n" +
                            "Вместе с подтверждением отправьте ваш уникальный номер\n\n" +
                            "Ваш уникальный номер: %s"%(callback_query.from_user.id),
                            reply_markup=btn.markup)

# checkCode
@cfg.dp.message_handler(lambda message: message.text == 'Доход от пользователя', state=States.Admin) 
async def set_users_tokens_from(message: types.Message):
    if await check.isAdmin(message.from_user.id):
        await cfg.bot.send_message(message.from_user.id, "Введите id пользователя:", reply_markup=btn.markup_back)
        await States.Set_tokens_from_user.set()
    else:
        await cfg.bot.send_message(message.from_user.id, "Вы не являетесь администратором бота\nНажмите /stop для выхода", reply_markup=types.ReplyKeyboardRemove())

@cfg.dp.message_handler(state=States.Set_tokens_from_user) 
async def set_users_tokens_count(message: types.Message):
    if message.text == "Вернуться в меню":
        await cfg.bot.send_message(message.from_user.id, "Вы в режиме администратора\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)
        await States.Admin.set()
        return
    elif await check.isReferrer(message.text):
        with db.conn.cursor() as cursor:
            cursor.execute("""SELECT sold_tokens.counts, users.first_name FROM sold_tokens INNER JOIN users ON sold_tokens.user_id = users.id WHERE sold_tokens.user_id=(SELECT id FROM users WHERE user_id=%s);""", (message.text, ))
            user = cursor.fetchone()
            await cfg.bot.send_message(message.from_user.id, "Пользователи, которых привёл пользователь %s, суммарно купили %s токенов."%(str(user[1]), str(user[0])), reply_markup=btn.markup_admin)
        await cfg.bot.send_message(message.from_user.id, "Вы в режиме администратора\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)
        await States.Admin.set()
        return
    else:
        await cfg.bot.send_message(message.from_user.id, "Пользователь не использовал реферальную систему!")
        await cfg.bot.send_message(message.from_user.id, "Вы в режиме администратора\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)
        await States.Admin.set()

# ignore handlers

@cfg.dp.message_handler(lambda message: message.text == 'Игнорирующие слова', state=States.Admin) 
async def Ignore_words(message: types.Message):
    if await check.isAdmin(message.from_user.id):
        ignore_words = await add_func.ignore_words()
        if ignore_words == "В боте нет слов исключений !":
            await cfg.bot.send_message(message.from_user.id, ignore_words, reply_markup=btn.markup_ignore_no_words)
            await States.Ignore_no_words.set()
        else:
            await cfg.bot.send_message(message.from_user.id, ignore_words, reply_markup=btn.markup_ignore_words)
            await States.Ignore_words.set()
    else:
        await cfg.bot.send_message(message.from_user.id, "Вы не являетесь администратором бота\nНажмите /stop для выхода", reply_markup=types.ReplyKeyboardRemove())

@cfg.dp.message_handler(state=States.Ignore_no_words) 
async def Ignore_no_words_menu(message: types.Message):
    if message.text == "Вернуться в меню":
        await cfg.bot.send_message(message.from_user.id, "Вы в режиме администратора\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)
        await States.Admin.set()
        return
    elif message.text == "Добавить игнорирующее слово":
        await cfg.bot.send_message(message.from_user.id, "Введите слово или строку которые хотите сделать игнорирующими:\n\nБот будет игнорировать введёное вами слово или строку, независимо от того, написано ли БОЛЬШИМИ буквами или маленькими", reply_markup=btn.markup_back)
        await States.Add_ignore_words.set()
        return

@cfg.dp.message_handler(state=States.Ignore_words) 
async def Ignore_words_menu(message: types.Message):
    if message.text == "Вернуться в меню":
        await cfg.bot.send_message(message.from_user.id, "Вы в режиме администратора\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)
        await States.Admin.set()
        return
    elif message.text == "Добавить игнорирующее слово":
        await cfg.bot.send_message(message.from_user.id, "Введите слово или строку которые хотите сделать игнорирующими:\n\nБот будет игнорировать введёное вами слово или строку, независимо от того, написано ли БОЛЬШИМИ буквами или маленькими", reply_markup=btn.markup_back)
        await States.Add_ignore_words.set()
        return
    elif message.text == "Удалить игнорирующее слово": 
        await cfg.bot.send_message(message.from_user.id, "Введите номер слова или строки, которую вы хотите удалить из списка игнорирующих:", reply_markup=btn.markup_back)
        await States.Del_ignore_words.set()
        return

@cfg.dp.message_handler(state=States.Add_ignore_words) 
async def Add_ignor_word(message: types.Message):
    await cfg.ignore_words_json.get_ignore_words(new_word=message.text, param="w")
    await cfg.bot.send_message(message.from_user.id, "Слово успешно добавленно !", reply_markup=btn.markup_admin)
    await States.Admin.set()

@cfg.dp.message_handler(state=States.Del_ignore_words) 
async def Set_index_to_del(message: types.Message):
    if message.text == 'Вернуться в меню':
        await States.Admin.set()
        await cfg.bot.send_message(message.from_user.id, "Вы в режиме администратора\nДля выхода из режима администратора нажмите /stop", reply_markup=btn.markup_admin)
        return
    elif await add_func.Chek_digit(message.from_user.id, message.text, from_admin=True):
        await States.Admin.set()
        return
    elif await add_func.get_ignore_word_index(message.text):
        await States.Admin.set()
        await cfg.bot.send_message(message.from_user.id, "Слово удалено !", reply_markup=btn.markup_admin)
        return
    else:
        await States.Admin.set()
        await cfg.bot.send_message(message.from_user.id, "Такое слово не найдено !", reply_markup=btn.markup_admin)
        return

# end admins code

async def scheduler_users():
    aioschedule.every().minute.do(Scheduler.Check_send_message)
    aioschedule.every(5).seconds.do(Scheduler.Check_transaction)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

# Run function with await
async def on_startup(_):
    asyncio.create_task(scheduler_users())

if __name__ == "__main__":
    executor.start_polling(cfg.dp, skip_updates=True, on_startup=on_startup)