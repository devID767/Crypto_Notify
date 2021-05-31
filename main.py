from aiogram import Bot, Dispatcher, executor, types

import Crypto
import Data
import Keyboards as kb

bot = Bot('1556889010:AAFzDxEeQPa1NDB6lWoPlBJFkGJeoW6tXF8')
dp = Dispatcher(bot)

async def LoadOrCreateDictSelectedCurrencies(user_id):
    allCurrencies = await Crypto.GetCurrencies(Data.GetFromBase(user_id, Data.Character.OwnCurrency.value))
    openCurrencies = {}
    try:
        openCurrencies = Data.loadArray(f"{user_id}-{Data.GetFromBase(user_id, Data.Character.OwnCurrency.value)}")
    except:
        for Currency in allCurrencies:
            openCurrencies[Currency] = True
        Data.saveArray(f"{user_id}-{Data.GetFromBase(user_id, Data.Character.OwnCurrency.value)}", openCurrencies)
    finally:
        return openCurrencies


@dp.callback_query_handler(lambda c: c.data.startswith('reg'))
async def Registration(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    data = callback_query.data
    code = data.split()[-1]

    if code == 'USD' or code == 'UAH' or code == 'RUB':
        Data.Register(callback_query.from_user.id, code, 0, Data.Status.Default.value)

        AllCurrencies = await Crypto.GetCurrencies(
            Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value))
        OpenedCurrencies = await LoadOrCreateDictSelectedCurrencies(callback_query.from_user.id)

        await bot.send_message(callback_query.from_user.id,
                               'Следующим шагом будет фильтр криптовалют, чтобы работа со мной стала ещё комфортнее',
                               reply_markup=kb.ShowSelectedCurrencyReg(AllCurrencies, OpenedCurrencies))
    elif code in await Crypto.GetCurrencies(Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)):
        AllCurrencies = await Crypto.GetCurrencies(
            Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value))
        OpenedCurrencies = Data.loadArray(f"{callback_query.from_user.id}-"
                                          f"{Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)}")

        if OpenedCurrencies[code]:
            OpenedCurrencies[code] = False
        else:
            OpenedCurrencies[code] = True

        Data.saveArray(f"{callback_query.from_user.id}-"
                       f"{Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)}", OpenedCurrencies)
        await bot.send_message(callback_query.from_user.id,
                               '*Выберите криптовалюту, за которой вы желаете следить*', parse_mode='Markdown',
                               reply_markup=kb.ShowSelectedCurrencyReg(AllCurrencies, OpenedCurrencies))
    elif data.split()[1] == 'reset':
        AllCurrencies = await Crypto.GetCurrencies(
            Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value))
        OpenedCurrencies = Data.loadArray(f"{callback_query.from_user.id}-"
                                        f"{Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)}")

        for Currency in OpenedCurrencies:
            if code == 'true':
                OpenedCurrencies[Currency] = True
            else:
                OpenedCurrencies[Currency] = False

        Data.saveArray(f"{callback_query.from_user.id}-"
                       f"{Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)}",
                       OpenedCurrencies)
        await bot.send_message(callback_query.from_user.id,
                               '*Выберите криптовалюту, за которой вы желаете следить*', parse_mode='Markdown',
                               reply_markup=kb.ShowSelectedCurrencyReg(AllCurrencies, OpenedCurrencies))
    elif code == 'continue':
        await bot.send_message(callback_query.from_user.id,
                               'И это всё! теперь ты можешь смело идти ставить своё первое уведомление',
                               reply_markup=types.InlineKeyboardMarkup().add(kb.addAlert))


@dp.message_handler(commands=['start'])
async def registration(message):
    try:
        Data.GetFromBase(message.from_user.id, Data.Character.OwnCurrency.value)
        await bot.send_message(message.chat.id, f'{message.from_user.first_name}, Вы уже зарегестрированы!\n'
                                                f'Пропишите комманду /menu, чтобы продолжить')
    except:
        await bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}\n'
                                            'Я помогу тебе уследить за скачком валюты, чтобы ты не потерял свои'
                                            ' драгоценные денежки!)\n Но для начала работы со мной, тебе следует выбрать '
                                            'свою родную валюту, в которую будут конвертироваться другие.',
                           reply_markup=kb.OwnCurrencyReg())

async def AddAlert(user_id):
    SelectedCurrency = await LoadOrCreateDictSelectedCurrencies(user_id)
    OpenedCurrencies = await Crypto.GetCurrencies(
        Data.GetFromBase(user_id, Data.Character.OwnCurrency.value),
        SelectedCurrency)
    await bot.send_message(user_id, 'Чтобы установить уведомление введите комманду:\n'
                                        '@crypto_alert_helperbot [название криптовалюты] [больше/меньше/скачек] [значение]',
                           reply_markup=kb.AddAlert(OpenedCurrencies))

async def CreateAlert(bot, user_id, currency, sign, value, time):
    alert = Crypto.Sending(bot, user_id, currency, sign, value, time,
                           Data.GetFromBase(user_id, Data.Character.OwnCurrency.value))

    CountOfAlerts = Data.GetFromBase(user_id, Data.Character.CountOfAlerts.value)
    if CountOfAlerts >= 5:
        await bot.send_message(user_id, f'Вы уже использовали максимальное количевстко уведомлений! (3)')
    elif not alert.text_id in Data.Alerts:
        Data.Alerts[alert.text_id] = alert
        Data.Update(user_id, Data.Character.CountOfAlerts.value, CountOfAlerts+1)
        await bot.send_message(user_id, f'Уведомление {alert.text} запущено')
        await alert.Start()
    else:
        await bot.send_message(user_id, 'Такое уведомление уже существует!')

    await bot.send_message(user_id, '*Уведомления*', parse_mode='Markdown', reply_markup=kb.Alert)

@dp.message_handler(lambda c: c.text.startswith('/alert'))
async def createAlert(message):
    try:
        Currency = message.text.split()[1]
        if Currency not in await Crypto.GetCurrencies(Data.GetFromBase(message.from_user.id, Data.Character.OwnCurrency.value)):
            raise ValueError
        sign = message.text.split()[2].lower()
        print(sign)
        if sign != 'больше' and sign != 'меньше':
            raise ValueError
        value = message.text.split()[3]
        if value[-1] == '%':
            value = float(value.replace('%', ''))
        else:
            value = float(value)
        await CreateAlert(bot, message.from_user.id, Currency, sign, value, 3600)
    except ValueError:
        await bot.send_message(message.from_user.id, 'Ошибка.\nНекоректные значения\n\n'
                                                     'Пример: /alert BTC/USD больше 40000')

@dp.callback_query_handler(lambda c: c.data.startswith('alert'))
async def RegisteryAlert(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    data = callback_query.data
    code = data.split()[-1]

    if code == 'open':
        await bot.send_message(callback_query.from_user.id, '*Уведомления*', parse_mode='Markdown', reply_markup=kb.Alert)
    elif code in await Crypto.GetCurrencies(Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)):
        await bot.send_message(callback_query.from_user.id, '*Выбери скачек*', parse_mode='Markdown', reply_markup=kb.CurrencyJump(code))
    elif code[-1] == '%':
        Currency = callback_query.data.split()[1]
        code = code.replace('%', '')
        await bot.send_message(callback_query.from_user.id, '*Выбери время*', parse_mode='Markdown', reply_markup=kb.AlertTime(Currency, code))
    elif code == 'time':
        Currency = callback_query.data.split()[1]
        Jump = int(callback_query.data.split()[2])
        Time = int(callback_query.data.split()[3]) * 3600

        await CreateAlert(bot, callback_query.from_user.id, Currency, 'изменится на', Jump, Time)
    elif code == 'add':
        SelectedCurrency = await LoadOrCreateDictSelectedCurrencies(callback_query.from_user.id)
        OpenedCurrencies = await Crypto.GetCurrencies(Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value),
                                                      SelectedCurrency)
        await bot.send_message(callback_query.from_user.id, '*Выбери крипту*', parse_mode='Markdown',
                               reply_markup=kb.AddAlert(OpenedCurrencies))
    elif code == 'show':
        await bot.send_message(callback_query.from_user.id, '*Нажмите чтобы удалить*', parse_mode='Markdown',
                               reply_markup=kb.ShowAlerts(callback_query.from_user.id, Data.Alerts))
    elif data.split(maxsplit=1)[1] in Data.Alerts:
        data = data.split(maxsplit=1)[1]
        await Data.Alerts[data].Stop()
        await bot.send_message(callback_query.from_user.id, f'Уведомление "{Data.Alerts[data].text}" удалено')

        CountOfAlerts = Data.GetFromBase(callback_query.from_user.id, Data.Character.CountOfAlerts.value)
        Data.Update(callback_query.from_user.id, Data.Character.CountOfAlerts.value, CountOfAlerts - 1)

        del Data.Alerts[data]

        await bot.send_message(callback_query.from_user.id, '*Нажмите чтобы удалить*', parse_mode='Markdown',
                               reply_markup=kb.ShowAlerts(callback_query.from_user.id, Data.Alerts))
    elif code == 'delete':
        Data.Update(callback_query.from_user.id, Data.Character.CountOfAlerts.value, 0)
        Text_id = []
        for text_id in Data.Alerts:
            Text_id.append(text_id)
        for alert in Text_id:
            if Data.Alerts[alert].user_id == callback_query.from_user.id:
                await bot.send_message(callback_query.from_user.id, f'Уведомление "{Data.Alerts[alert].text}" удалено')
                await Data.Alerts[alert].Stop()
                del Data.Alerts[alert]

        await bot.send_message(callback_query.from_user.id, f'Все уведомления удалены')
        await bot.send_message(callback_query.from_user.id, '*Уведомления*', parse_mode='Markdown', reply_markup=kb.Alert)
    elif code == 'help':
        await bot.send_message(callback_query.from_user.id, 'Чтобы установить расширенное уведомление введите комманду:\n\n'
                                '/alert [название криптовалюты] [больше/меньше] [значение]\n\n'
                                '[название криптовалюты] - \nСама криптовалюта/родная валюта. \nПример: BTC/USD\n\n'
                                '[больше/меньше/скачек] - \nбольше: крипта должна перевалить значение [пороговая цена] в большую сторону.\n'
                                                          'меньше: крипта должна перевалить значение [пороговая цена] в меньшую сторону.\n'
                                                          'скачек: при каждой проверке будет проверяться не упала, или не поднялась ли крипта на [пороговая цена] процентов\n\n'
                                '[значение] - число, которое должно переступить условие [больше/меньше/скачек]. Процентцы поддерживает только скачек. '
                                                            'При скачке проценты можна не писать\n\n',
                               reply_markup=types.InlineKeyboardMarkup().add(kb.BackToAlert).add(kb.BackToMenu))

@dp.callback_query_handler(lambda c: c.data)
async def Commands(callback_query: types.CallbackQuery):
    data = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

    if data == 'menu':
        await bot.send_message(callback_query.from_user.id, f'*Вибери действие:*', parse_mode='Markdown', reply_markup=kb.MainMenu)
    elif data == 'show':
        OwnCurrency = Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)
        SelectedCurrencies = await LoadOrCreateDictSelectedCurrencies(f"{callback_query.from_user.id}")

        showSelectedCurrencies = await Crypto.GetCurrencies(OwnCurrency, SelectedCurrencies, price=True)
        for Currencies in showSelectedCurrencies:
            await bot.send_message(callback_query.from_user.id, f'{Currencies} - {showSelectedCurrencies[Currencies]}')

        await bot.send_message(callback_query.from_user.id, f'*Вибери действие:*', parse_mode='Markdown', reply_markup=kb.MainMenu)
    elif data == 'settings':
        await bot.send_message(callback_query.from_user.id, '*Настройки*', parse_mode='Markdown', reply_markup=kb.Settings)
    elif data == 'help':
        await bot.send_message(callback_query.from_user.id, 'Основная моя задача заключается в том, чтобы уведомлять тебя, '
                                                            'когда криптовалюта резко упадет или вырастет\n'
                                                            'Для этого, тебе следует передти во вкладку "Уведомления"\n\n'
                                                            'Для комфортного пользования '
                                                            'в настройках можешь выбрать для себя родную валюту и задать фильтр '
                                                            'валют, за которыми жедаешь следать.',
                                                            reply_markup=types.InlineKeyboardMarkup().add(kb.BackToSettings)
                                                            .add(kb.BackToAlert).add(kb.BackToMenu))
    elif data == 'ownCurrency' or data == 'USD' or data == 'UAH' or data == 'RUB':
        if data != 'ownCurrency':
            Data.Update(callback_query.from_user.id, Data.Character.OwnCurrency.value, data)
        Currency = Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)
        await bot.send_message(callback_query.from_user.id, '*Выбрать родную валюту*', parse_mode='Markdown',
                               reply_markup=kb.OwnCurrencies(Currency))
    elif data == 'SelectCurrency':
        AllCurrencies = await Crypto.GetCurrencies(Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value))
        OpenedCurrencies = await LoadOrCreateDictSelectedCurrencies(callback_query.from_user.id)

        await bot.send_message(callback_query.from_user.id, '*Выберите криптовалюту, за которой вы желаете следить*', parse_mode='Markdown',
                               reply_markup=kb.ShowSelectedCurrency(AllCurrencies, OpenedCurrencies))
    elif data in await Crypto.GetCurrencies(Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)):
        AllCurrencies = await Crypto.GetCurrencies(
            Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value))
        OpenedCurrencies = Data.loadArray(f"{callback_query.from_user.id}-"
                                        f"{Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)}")

        if OpenedCurrencies[data]:
            OpenedCurrencies[data] = False
        else:
            OpenedCurrencies[data] = True

        Data.saveArray(f"{callback_query.from_user.id}-"
                       f"{Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)}", OpenedCurrencies)
        await bot.send_message(callback_query.from_user.id, '*Выберите криптовалюту, за которой вы желаете следить*', parse_mode='Markdown',
                               reply_markup=kb.ShowSelectedCurrency(AllCurrencies, OpenedCurrencies))
    elif data.startswith('reset'):
        default = data.split()[1]

        AllCurrencies = await Crypto.GetCurrencies(
            Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value))
        OpenedCurrencies = Data.loadArray(f"{callback_query.from_user.id}-"
                                        f"{Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)}")

        for Currency in OpenedCurrencies:
            if default == 'true':
                OpenedCurrencies[Currency] = True
            else:
                OpenedCurrencies[Currency] = False

        Data.saveArray(f"{callback_query.from_user.id}-"
                       f"{Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)}",
                       OpenedCurrencies)
        await bot.send_message(callback_query.from_user.id, '*Выберите криптовалюту, за которой вы желаете следить*', parse_mode='Markdown',
                               reply_markup=kb.ShowSelectedCurrency(AllCurrencies, OpenedCurrencies))

@dp.message_handler(commands=['menu'])
async def send_welcome(message):
    await bot.send_message(message.chat.id, f'*Вибери действие:*', parse_mode='Markdown', reply_markup=kb.MainMenu)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
