from aiogram import Bot, Dispatcher, executor, types

import Crypto
import Data
import Keyboards as kb

bot = Bot('1556889010:AAFzDxEeQPa1NDB6lWoPlBJFkGJeoW6tXF8')
dp = Dispatcher(bot)

@dp.callback_query_handler(lambda c: c.data)
async def Commands(callback_query: types.CallbackQuery):
    data = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

    if data == 'menu':
        await bot.send_message(callback_query.from_user.id, f'Привет {callback_query.from_user.first_name}\n'
                                                            f'Вибери действие:', reply_markup=kb.MainMenu)
    elif data == 'settings':
        await bot.send_message(callback_query.from_user.id, 'Настройки', reply_markup=kb.Settings)
    elif data == 'help':
        await bot.send_message(callback_query.from_user.id, 'Для комфортной работы со мной, перейди в настройки, чтобы выбрать '
                                                            'родную валюту и валюты, за которыми желаешь следить.\n\n'
                                                            'Основная моя задача заключается в том, чтобы уведомлять тебя, '
                                                            'когда криптовалюта резко упадет или вырастет\n'
                                                            'Для этого, тебе следует передти во вкладку "Уведомления"',
                                                            reply_markup=types.InlineKeyboardMarkup().add(kb.BackToSettings)
                                                            .add(kb.BackToAlert).add(kb.BackToMenu))
    elif data == 'ownCurrency' or data == 'USD' or data == 'UAH' or data == 'RUB':
        if data != 'ownCurrency':
            Data.InsertToBase(callback_query.from_user.id, data)
        await bot.send_message(callback_query.from_user.id, 'Выбрать родную валюту',
                               reply_markup=kb.OwnCurrencies(data, callback_query.from_user.id))
    elif data == 'SelectCurrency':
        await bot.send_message(callback_query.from_user.id, 'Выберите криптовалюту, за которой вы желаете следить',
                               reply_markup=kb.ShowSelectedCurrency(callback_query.from_user.id))
    elif data in Crypto.GetAllCurrencies(Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)[0]):
        openCurrencies = Data.loadArray(f"{callback_query.from_user.id}-"
                                        f"{Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)[0]}")

        if openCurrencies[data]:
            openCurrencies[data] = False
        else:
            openCurrencies[data] = True

        Data.saveArray(f"{callback_query.from_user.id}-"
                       f"{Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)[0]}", openCurrencies)
        await bot.send_message(callback_query.from_user.id, 'Выберите криптовалюту, за которой вы желаете следить',
                               reply_markup=kb.ShowSelectedCurrency(callback_query.from_user.id))
    elif data.startswith('reset'):
        default = data.split()[1]
        openCurrencies = Data.loadArray(f"{callback_query.from_user.id}-"
                                        f"{Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)[0]}")

        for Currency in openCurrencies:
            if default == 'true':
                openCurrencies[Currency] = True
            else:
                openCurrencies[Currency] = False

        Data.saveArray(f"{callback_query.from_user.id}-"
                       f"{Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)[0]}",
                       openCurrencies)
        await bot.send_message(callback_query.from_user.id, 'Выберите криптовалюту, за которой вы желаете следить',
                               reply_markup=kb.ShowSelectedCurrency(callback_query.from_user.id))
    elif data == 'show':
        OwnCurrency = Data.GetFromBase(callback_query.from_user.id, Data.Character.OwnCurrency.value)[0]
        SelectedCurrencies = kb.LoadOrCreateDictSelectedCurrencies(f"{callback_query.from_user.id}")

        showenSelectedCurrencies = Crypto.GetSelectedCurrencies(OwnCurrency, SelectedCurrencies)
        for Currencies in showenSelectedCurrencies:
            await bot.send_message(callback_query.from_user.id, f'{Currencies} - {showenSelectedCurrencies[Currencies]}')

        await bot.send_message(callback_query.from_user.id, 'Вернуться в меню?',
                               reply_markup=types.InlineKeyboardMarkup().add(kb.BackToMenu))
    elif data == 'alert':
        await bot.send_message(callback_query.from_user.id, 'Уведомления', reply_markup=kb.Alert)
    elif data == 'addAlert':
        await bot.send_message(callback_query.from_user.id, 'Чтобы установить уведомление введите комманду:\n'
        '@crypto_alert_helperbot [название криптовалюты] [больше/меньше/скачек] [значение] за последние [число] [minutes/hours/days]',
                                                            reply_markup=kb.AddAlert(callback_query.from_user.id))
    elif data == 'showAlerts':
        await bot.send_message(callback_query.from_user.id, 'Уведомления\n'
                                                            'Нажмите чтобы удалить',
                               reply_markup=kb.ShowAlert(callback_query.from_user.id))
    elif data in Data.Alerts:
        await Data.Alerts[data].Stop()
        await bot.send_message(callback_query.from_user.id, f'Уведомление "{Data.Alerts[data].text}" удалено')
        del Data.Alerts[data]
        await bot.send_message(callback_query.from_user.id, 'Нажмите чтобы удалить',
                               reply_markup=kb.ShowAlert(callback_query.from_user.id))
    elif data == 'helpAlert':
        await bot.send_message(callback_query.from_user.id, '[Кликом по крипте автоматически напечатается пример коммнады]\n\n'
                               'Чтобы установить уведомление введите комманду:\n\n'
        '@crypto_alert_helperbot [название криптовалюты] [больше/меньше/скачек] [значение] за последние [число] [minutes/hours/days]\n\n'
                                '[название криптовалюты] - \nСама криптовалюта/родная валюта. \nПример: BTC/USD\n\n'
                                '[больше/меньше/скачек] - \nбольше: крипта должна перевалить значение [пороговая цена] в большую сторону.\n'
                                                          'меньше: крипта должна перевалить значение [пороговая цена] в меньшую сторону.\n'
                                                          'скачек: при каждой проверке будет проверяться не упала, или не поднялась ли крипта на [пороговая цена] процентов\n\n'
                                '[значение] - число, которое должно переступить условие [больше/меньше/скачек]. Процентцы поддерживает только скачек. '
                                                            'При скачке проценты можна не писать\n\n'
                                '[число] - пеориодичность одной проверки.\n\n'
                                '[minutes/hours/days] - тип времени. Секунды не поддерживаются',
                               reply_markup=types.InlineKeyboardMarkup().add(kb.BackToAlert).add(kb.BackToMenu))


@dp.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}\n'
                                            f'Вибери действие:', reply_markup=kb.MainMenu)

@dp.message_handler()
async def createAlert(message):
    if message.text.split()[0] == '@Crypto_Notify_Alert_bot':
        try:
            Currency = message.text.split()[1]
            sign = message.text.split()[2]
            value = message.text.split()[3]
            time = float(message.text.split()[6])
            if value[-1] == '%':
                print('yes')
                value = float(value.replace('%', ''))
            else:
                value = float(value)
            typeOfTime = message.text.split()[7]

            if typeOfTime == 'minutes':
                time *= 60
            elif typeOfTime == 'hours':
                time *= 360
            elif typeOfTime == 'days':
                time *= 360 * 24
            else:
                time = 'asd'

            alert = Crypto.Sending(bot, message.from_user.id, Currency, sign, value, time,
                                   Data.GetFromBase(message.from_user.id, Data.Character.OwnCurrency.value)[0])
            if not alert.text_id in Data.Alerts:
                Data.Alerts[alert.text_id] = alert
                await bot.send_message(message.from_user.id, f'Уведомление {alert.text} запущено',
                                       reply_markup=types.InlineKeyboardMarkup().add(kb.BackToAlert).add(kb.BackToMenu))
                await alert.Start()
            else:
                await bot.send_message(message.from_user.id, 'Такоe уведомление уже существует!',
                                       reply_markup=kb.MainMenu)
        except:
            await bot.send_message(message.from_user.id, 'Ошибка.\nНекоректные данные')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
