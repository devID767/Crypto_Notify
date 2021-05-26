from aiogram import types

#Back to ...
BackToMenu = types.InlineKeyboardButton('Перейти в меню', callback_data='menu')
BackToSettings = types.InlineKeyboardButton('Перейти в настройки', callback_data='settings')
BackToAlert = types.InlineKeyboardButton('Перейти в уведомления', callback_data='alert')

#MainMenu
MainMenu = types.InlineKeyboardMarkup()
showCurrencies = types.InlineKeyboardButton('Посмотреть курс валют', callback_data='show')
MainMenu.add(showCurrencies)
Alert = types.InlineKeyboardButton('Уведомления', callback_data='alert')
MainMenu.add(Alert)
Settings = types.InlineKeyboardButton('Настройки', callback_data='settings')
MainMenu.add(Settings)
Help = types.InlineKeyboardButton('Помощь', callback_data='help')
MainMenu.add(Help)

#Alert
Alert = types.InlineKeyboardMarkup()
addAlert = types.InlineKeyboardButton('Добавить новое уведомление', callback_data='addAlert')
Alert.add(addAlert)
showAlerts = types.InlineKeyboardButton('Посмотреть текущие уведомления', callback_data='showAlerts')
Alert.add(showAlerts)
deleteAlerts = types.InlineKeyboardButton('Удалить все свои уведомления', callback_data='deleteAlerts')
Alert.add(deleteAlerts)
HelpAlert = types.InlineKeyboardButton('Помощь', callback_data='helpAlert')
Alert.add(HelpAlert)
Alert.add(BackToMenu)

def AddAlert(user_id, OpenedCurrency):
    AddAlert = types.InlineKeyboardMarkup()

    for Currency in OpenedCurrency:
            AddAlert.add(types.InlineKeyboardButton(f'{Currency}', switch_inline_query_current_chat=f'{Currency} больше 1'))

    AddAlert.add(BackToAlert)

    AddAlert.add(BackToMenu)

    return AddAlert

def ShowAlerts(user_id, Alerts):
    AlertsKeyboard = types.InlineKeyboardMarkup()
    for alert in Alerts:
        if alert.user_id == user_id:
            AlertsKeyboard.add(types.InlineKeyboardButton(alert.text, callback_data= alert.text_id))

    AlertsKeyboard.add(BackToAlert)

    AlertsKeyboard.add(BackToMenu)

    return AlertsKeyboard

#Settings
Settings = types.InlineKeyboardMarkup()
ownCurrency = types.InlineKeyboardButton('Родная валюта', callback_data='ownCurrency')
Settings.add(ownCurrency)
SelectCurrency = types.InlineKeyboardButton('Фильтр криптовалют', callback_data='SelectCurrency')
Settings.add(SelectCurrency)
Settings.add(BackToMenu)

def ShowSelectedCurrency(user_id, AllCurrencies, OpenedCurrencies):
    AllSelectedCurrenciesKeyboard = types.InlineKeyboardMarkup()

    for Currency in AllCurrencies:
        if OpenedCurrencies[Currency]:
            AllSelectedCurrenciesKeyboard.add(types.InlineKeyboardButton(f'{Currency} ✅', callback_data=f'{Currency}'))
        else:
            AllSelectedCurrenciesKeyboard.add(types.InlineKeyboardButton(f'{Currency}', callback_data=f'{Currency}'))

    AllSelectedCurrenciesKeyboard.add(types.InlineKeyboardButton('Отметить все', callback_data='reset true'))
    AllSelectedCurrenciesKeyboard.add(types.InlineKeyboardButton('Сбросить', callback_data='reset false'))

    AllSelectedCurrenciesKeyboard.add(BackToSettings)

    AllSelectedCurrenciesKeyboard.add(BackToMenu)

    return AllSelectedCurrenciesKeyboard

def OwnCurrencies(currency, user_id):
    OwnCurrenciesKeyboard = types.InlineKeyboardMarkup()

    if currency == 'USD':
        Currency_USD = types.InlineKeyboardButton('USD ✅', callback_data='USD')
    else:
        Currency_USD = types.InlineKeyboardButton('USD', callback_data='USD')
    if currency == 'UAH':
        Currency_UAH = types.InlineKeyboardButton('UAH ✅', callback_data='UAH')
    else:
        Currency_UAH = types.InlineKeyboardButton('UAH', callback_data='UAH')

    if currency == 'RUB':
        Currency_RUB = types.InlineKeyboardButton('RUB ✅', callback_data='RUB')
    else:
        Currency_RUB = types.InlineKeyboardButton('RUB', callback_data='RUB')

    OwnCurrenciesKeyboard.add(Currency_USD)

    OwnCurrenciesKeyboard.add(Currency_UAH)

    OwnCurrenciesKeyboard.add(Currency_RUB)

    OwnCurrenciesKeyboard.add(BackToSettings)

    OwnCurrenciesKeyboard.add(BackToMenu)

    return OwnCurrenciesKeyboard