from aiogram import Bot, Dispatcher, executor, types

import Crypto
import Data
import Keyboards as kb

bot = Bot('1556889010:AAFzDxEeQPa1NDB6lWoPlBJFkGJeoW6tXF8')
dp = Dispatcher(bot)


def LoadOrCreateDictSelectedCurrencies(user_id):
    allCurrencies = Crypto.GetCurrencies(Data.GetFromBase(user_id, Data.Character.OwnCurrency.value))
    openCurrencies = {}
    try:
        openCurrencies = Data.loadArray(f"{user_id}-{Data.GetFromBase(user_id, Data.Character.OwnCurrency.value)}")
    except:
        for Currency in allCurrencies:
            openCurrencies[Currency] = True
        Data.saveArray(f"{user_id}-{Data.GetFromBase(user_id, Data.Character.OwnCurrency.value)}", openCurrencies)
    finally:
        return openCurrencies

@dp.callback_query_handler(lambda c: c.data)
async def Commands(callback_query: types.CallbackQuery):
    data = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

    if data == 'menu':
        await bot.send_message(callback_query.from_user.id, f'Вибери действие:', reply_markup=kb.MainMenu)
    elif data == 'show':
        OwnCurrency = Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)
        SelectedCurrencies = LoadOrCreateDictSelectedCurrencies(f"{callback_query.from_user.id}")

        showSelectedCurrencies = Crypto.GetCurrencies(OwnCurrency, SelectedCurrencies, price=True)
        for Currencies in showSelectedCurrencies:
            await bot.send_message(callback_query.from_user.id, f'{Currencies} - {showSelectedCurrencies[Currencies]}')

        await bot.send_message(callback_query.from_user.id, f'Вибери действие:', reply_markup=kb.MainMenu)
    elif data == 'settings':
        await bot.send_message(callback_query.from_user.id, 'Настройки', reply_markup=kb.Settings)
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
        await bot.send_message(callback_query.from_user.id, 'Выбрать родную валюту',
                               reply_markup=kb.OwnCurrencies(Currency, callback_query.from_user.id))
    elif data == 'SelectCurrency':
        AllCurrencies = Crypto.GetCurrencies(Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value))
        OpenedCurrencies = LoadOrCreateDictSelectedCurrencies(callback_query.from_user.id)

        await bot.send_message(callback_query.from_user.id, 'Выберите криптовалюту, за которой вы желаете следить',
                               reply_markup=kb.ShowSelectedCurrency(callback_query.from_user.id, AllCurrencies, OpenedCurrencies))
    elif data in Crypto.GetCurrencies(Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)):
        AllCurrencies = Crypto.GetCurrencies(
            Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value))
        OpenedCurrencies = Data.loadArray(f"{callback_query.from_user.id}-"
                                        f"{Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)}")

        if OpenedCurrencies[data]:
            OpenedCurrencies[data] = False
        else:
            OpenedCurrencies[data] = True

        Data.saveArray(f"{callback_query.from_user.id}-"
                       f"{Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)}", OpenedCurrencies)
        await bot.send_message(callback_query.from_user.id, 'Выберите криптовалюту, за которой вы желаете следить',
                               reply_markup=kb.ShowSelectedCurrency(callback_query.from_user.id, AllCurrencies, OpenedCurrencies))
    elif data.startswith('reset'):
        default = data.split()[1]

        AllCurrencies = Crypto.GetCurrencies(
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
        await bot.send_message(callback_query.from_user.id, 'Выберите криптовалюту, за которой вы желаете следить',
                               reply_markup=kb.ShowSelectedCurrency(callback_query.from_user.id, AllCurrencies, OpenedCurrencies))
    elif data == 'alert':
        await bot.send_message(callback_query.from_user.id, 'Уведомления', reply_markup=kb.Alert)
    elif data == 'addAlert':
        SelectedCurrency = LoadOrCreateDictSelectedCurrencies(callback_query.from_user.id)
        OpenedCurrencies = Crypto.GetCurrencies(Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value),
                                             SelectedCurrency)
        await bot.send_message(callback_query.from_user.id, 'Чтобы установить уведомление введите комманду:\n'
        '@crypto_alert_helperbot [название криптовалюты] [больше/меньше/скачек] [значение]',
                                                        reply_markup=kb.AddAlert(callback_query.from_user.id, OpenedCurrencies))
    elif data == 'showAlerts':
        await bot.send_message(callback_query.from_user.id, 'Уведомления\n'
                                                            'Нажмите чтобы удалить',
                               reply_markup=kb.ShowAlerts(callback_query.from_user.id, Data.Alerts.values()))
    elif data in Data.Alerts:
        await Data.Alerts[data].Stop()
        await bot.send_message(callback_query.from_user.id, f'Уведомление "{Data.Alerts[data].text}" удалено')

        CountOfAlerts = Data.GetFromBase(callback_query.from_user.id, Data.Character.CountOfAlerts.value)
        Data.Update(callback_query.from_user.id, Data.Character.CountOfAlerts.value, CountOfAlerts - 1)

        del Data.Alerts[data]
        await bot.send_message(callback_query.from_user.id, 'Нажмите чтобы удалить',
                               reply_markup=kb.ShowAlerts(callback_query.from_user.id, Data.Alerts.values()))
    elif data == 'deleteAlerts':
        Data.Update(callback_query.from_user.id, Data.Character.CountOfAlerts.value, 0)
        for alert in Data.Alerts.values():
            if alert.user_id == callback_query.from_user.id:
                await Data.Alerts
                await Data.Alerts[alert.text_id].Stop()
                await bot.send_message(callback_query.from_user.id, f'Уведомление "{Data.Alerts[alert.text_id].text}" удалено')

                del Data.Alerts[alert.text_id]
        await bot.send_message(callback_query.from_user.id, f'Все уведомления удалены',
                               reply_markup=types.InlineKeyboardMarkup().add(kb.BackToAlert).add(kb.BackToMenu))
    elif data == 'helpAlert':
        await bot.send_message(callback_query.from_user.id, '[Кликом по крипте автоматически напечатается пример коммнады]\n\n'
                               'Чтобы установить уведомление введите комманду:\n\n'
        '@crypto_alert_helperbot [название криптовалюты] [больше/меньше/скачек] [значение]\n\n'
                                '[название криптовалюты] - \nСама криптовалюта/родная валюта. \nПример: BTC/USD\n\n'
                                '[больше/меньше/скачек] - \nбольше: крипта должна перевалить значение [пороговая цена] в большую сторону.\n'
                                                          'меньше: крипта должна перевалить значение [пороговая цена] в меньшую сторону.\n'
                                                          'скачек: при каждой проверке будет проверяться не упала, или не поднялась ли крипта на [пороговая цена] процентов\n\n'
                                '[значение] - число, которое должно переступить условие [больше/меньше/скачек]. Процентцы поддерживает только скачек. '
                                                            'При скачке проценты можна не писать\n\n',
                               reply_markup=types.InlineKeyboardMarkup().add(kb.BackToAlert).add(kb.BackToMenu))


@dp.message_handler(commands=['start'])
async def registration(message):
    Data.Register(message.from_user.id, 'USD', 0, Data.Status.Default.value)
    await bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}\n'
                                            'Пропиши комманду /menu, чтобы вызвать главное меню')

@dp.message_handler(commands=['menu'])
async def send_welcome(message):
    await bot.send_message(message.chat.id, f'Вибери действие:', reply_markup=kb.MainMenu)

@dp.message_handler()
async def createAlert(message):
    if message.text.split()[0] == '@Crypto_Notify_Alert_bot':
        try:
            Currency = message.text.split()[1]
            sign = message.text.split()[2]
            value = message.text.split()[3]
            if value[-1] == '%':
                value = float(value.replace('%', ''))
            else:
                value = float(value)

            alert = Crypto.Sending(bot, message.from_user.id, Currency, sign, value, 3600,
                                   Data.GetFromBase(message.from_user.id, Data.Character.OwnCurrency.value))
            CountOfAlerts = Data.GetFromBase(message.from_user.id, Data.Character.CountOfAlerts.value)
            if CountOfAlerts >= 3:
                await bot.send_message(message.from_user.id, f'Вы уже использовали максимальное количевстко уведомлений! (3)',
                                       reply_markup=types.InlineKeyboardMarkup().add(kb.BackToAlert).add(kb.BackToMenu))
            elif not alert.text_id in Data.Alerts:
                Data.Alerts[alert.text_id] = alert
                Data.Update(message.from_user.id, Data.Character.CountOfAlerts.value, CountOfAlerts+1)
                await bot.send_message(message.from_user.id, f'Уведомление {alert.text} запущено',
                                       reply_markup=types.InlineKeyboardMarkup().add(kb.BackToAlert).add(kb.BackToMenu))
                await alert.Start()
            else:
                await bot.send_message(message.from_user.id, 'Такоe уведомление уже существует!',
                                       reply_markup=types.InlineKeyboardMarkup().add(kb.BackToAlert).add(kb.BackToMenu))
        except:
            await bot.send_message(message.from_user.id, 'Ошибка.\nНекоректные данные')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
