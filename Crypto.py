import requests
from bs4 import BeautifulSoup

import asyncio


url = 'https://kuna.io/markets/xrpuah'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

def GetCurrencies(OwnCurrency):

    CurrenciesList = []
    if OwnCurrency == 'USD':
        Currencies = soup.find_all('li', class_=f'market quote-{OwnCurrency.lower()}')
        CurrenciesList.append(Currencies)

        Currencies = soup.find_all('li', class_=f'market quote-{OwnCurrency.lower()}t')
        CurrenciesList.append(Currencies)

        Currencies = soup.find_all('li', class_=f'market quote-{OwnCurrency.lower()}c')
        CurrenciesList.append(Currencies)
    else:
        Currencies = soup.find_all('li', class_=f'market quote-{OwnCurrency.lower()}')
        CurrenciesList.append(Currencies)

    return CurrenciesList

def GetSelectedCurrencies(OwnCurrency, SelectedCurrencies):
    selectedCurrenties = {}
    Currencieslist = GetCurrencies(OwnCurrency)
    for Currencies in Currencieslist:
        for currency in Currencies:
            if SelectedCurrencies[f"{currency.find('li').text}"]:
               price = currency.find('ul', class_='last price')
               selectedCurrenties[currency.find("li").text] = float(price.text)

    return selectedCurrenties

def GetAllCurrencies(OwnCurrency):
    allCurrencies = {}
    Currencieslist = GetCurrencies(OwnCurrency)

    for Currencies in Currencieslist:
        for currency in Currencies:
            price = currency.find('ul', class_='last price')
            allCurrencies[currency.find("li").text] = float(price.text)

    return allCurrencies

class Sending:
    price = 0
    def __init__(self, bot, user_id, crypto, sign, value, time, ownCurrency):
        self._bot = bot
        self.user_id = user_id

        self._sign = sign
        self._value = value

        self._time = time

        self.crypto = crypto
        self.ownCurrency = ownCurrency

        self.is_started = False
        self._task = None

        self.text = f'{self.crypto} {self._sign} {self._value}'
        self.text_id = f'{user_id}-{self.crypto} {self._sign} {self._value}'

    async def Start(self):
        if not self.is_started:
            self.is_started = True
            self._task = asyncio.ensure_future(self._Sending())


    async def Stop(self):
        if self.is_started:
            self.is_started = False
            self._task.cancel()

    async def _Sending(self):
        while True:
            CurrenciesDict = GetAllCurrencies(self.ownCurrency)
            self.price = CurrenciesDict[self.crypto]

            if self._sign == 'больше' and self.price >= self._value:
                await self._bot.send_message(self.user_id, f'{self.crypto} - {self.price} >= {self._value}')
            elif self._sign == 'меньше' and self.price <= self._value:
                await self._bot.send_message(self.user_id, f'{self.crypto} - {self.price} <= {self._value}')
            await asyncio.sleep(self._time)

        await self._bot.send_message(self.user_id, f'{self.text} stopped')
