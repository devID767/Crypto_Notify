from aiogram import types
import Data
import Crypto

#Back to ...
BackToMenu = types.InlineKeyboardButton('Вернуться в меню', callback_data='menu')
BackToSettings = types.InlineKeyboardButton('Вернуться в настройки', callback_data='settings')
BackToAlert = types.InlineKeyboardButton('Вернуться в уведомления', callback_data='alert')

#MainMenu
MainMenu = types.InlineKeyboardMarkup()
showCurrencies = types.InlineKeyboardButton('Посмотреть курс валют', callback_data='show')
MainMenu.add(showCurrencies)
Alert = types.InlineKeyboardButton('Уведомления', callback_data='alert')
MainMenu.add(Alert)
Settings = types.InlineKeyboardButton('Настройки', callback_data='settings')
MainMenu.add(Settings)

#Alert
Alert = types.InlineKeyboardMarkup()
addAlert = types.InlineKeyboardButton('Добавить новое уведомление', callback_data='addAlert')
Alert.add(addAlert)
showAlerts = types.InlineKeyboardButton('Посмотреть текущие уведомления', callback_data='showAlerts')
Alert.add(showAlerts)
Alert.add(BackToMenu)

def AddAlert(user_id):
    AddAlert = types.InlineKeyboardMarkup()
    SelectedCurrency = LoadOrCreateDictSelectedCurrencies(user_id)
    allCurrencies = Crypto.GetSelectedCurrencies(Data.GetFromBase(user_id, Data.Character.OwnCurrency.value)[0], SelectedCurrency)

    for Currency in allCurrencies:
            AddAlert.add(types.InlineKeyboardButton(f'{Currency}', switch_inline_query_current_chat=f'{Currency} больше 1 2 minutes'))

    AddAlert.add(BackToAlert)

    AddAlert.add(BackToMenu)

    return AddAlert

def ShowAlert(user_id):
    AlertsKeyboard = types.InlineKeyboardMarkup()
    for alert in Data.Alerts.values():
        if alert.user_id == user_id:
            AlertsKeyboard.add(types.InlineKeyboardButton(alert.text, callback_data= alert.text))

    AlertsKeyboard.add(BackToAlert)

    AlertsKeyboard.add(BackToMenu)

    return AlertsKeyboard

#Settings
Settings = types.InlineKeyboardMarkup()
ownCurrency = types.InlineKeyboardButton('Выбрать свою валюту', callback_data='ownCurrency')
Settings.add(ownCurrency)
SelectCurrency = types.InlineKeyboardButton('Выбрать используемые валюты', callback_data='SelectCurrency')
Settings.add(SelectCurrency)
Settings.add(BackToMenu)

def LoadOrCreateDictSelectedCurrencies(user_id):
    allCurrencies = Crypto.GetAllCurrencies(Data.GetFromBase(user_id, Data.Character.OwnCurrency.value)[0])
    openCurrencies = {}
    try:
        openCurrencies = Data.loadArray(f"{user_id}-{Data.GetFromBase(user_id, Data.Character.OwnCurrency.value)[0]}")
    except:
        for Currency in allCurrencies:
            openCurrencies[Currency] = False
        Data.saveArray(f"{user_id}-{Data.GetFromBase(user_id, Data.Character.OwnCurrency.value)[0]}", openCurrencies)
    finally:
        return openCurrencies

def ShowSelectedCurrency(user_id):
    AllSelectedCurrenciesKeyboard = types.InlineKeyboardMarkup()
    allCurrencies = Crypto.GetAllCurrencies(Data.GetFromBase(user_id, Data.Character.OwnCurrency.value)[0])

    openCurrencies = LoadOrCreateDictSelectedCurrencies(user_id)

    for Currency in allCurrencies:
        if openCurrencies[Currency]:
            AllSelectedCurrenciesKeyboard.add(types.InlineKeyboardButton(f'{Currency} ✅', callback_data=f'{Currency}'))
        else:
            AllSelectedCurrenciesKeyboard.add(types.InlineKeyboardButton(f'{Currency}', callback_data=f'{Currency}'))

    AllSelectedCurrenciesKeyboard.add(BackToSettings)

    AllSelectedCurrenciesKeyboard.add(BackToMenu)

    return AllSelectedCurrenciesKeyboard

def OwnCurrencies(currency, user_id):
    OwnCurrenciesKeyboard = types.InlineKeyboardMarkup()

    Currency = Data.GetFromBase(user_id, Data.Character.OwnCurrency.value)[0]
    #try:
    #except:
    #    Currency = '///'

    if currency == 'USD' or Currency == 'USD':
        Currency_USD = types.InlineKeyboardButton('USD ✅', callback_data='USD')
    else:
        Currency_USD = types.InlineKeyboardButton('USD', callback_data='USD')
    if currency == 'UAH' or Currency == 'UAH':
        Currency_UAH = types.InlineKeyboardButton('UAH ✅', callback_data='UAH')
    else:
        Currency_UAH = types.InlineKeyboardButton('UAH', callback_data='UAH')

    if currency == 'RUB' or Currency == 'RUB':
        Currency_RUB = types.InlineKeyboardButton('RUB ✅', callback_data='RUB')
    else:
        Currency_RUB = types.InlineKeyboardButton('RUB', callback_data='RUB')

    OwnCurrenciesKeyboard.add(Currency_USD)

    OwnCurrenciesKeyboard.add(Currency_UAH)

    OwnCurrenciesKeyboard.add(Currency_RUB)

    OwnCurrenciesKeyboard.add(BackToSettings)

    OwnCurrenciesKeyboard.add(BackToMenu)

    return OwnCurrenciesKeyboard