import requests
from bs4 import BeautifulSoup

import asyncio

def connectToSite():
    url = 'https://kuna.io/markets/xrpuah'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup

soup = connectToSite()

async def _GetCurrencies(OwnCurrency):
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

async def GetCurrencies(OwnCurrency, SelectedCurrencies=None, price=False):
    if price:
        global soup
        soup = connectToSite()

    selectedCurrenties = {}
    Currencieslist = await _GetCurrencies(OwnCurrency)
    for Currencies in Currencieslist:
        for currency in Currencies:
            if not SelectedCurrencies is None:
                if SelectedCurrencies[f"{currency.find('li').text}"]:
                    price = currency.find('ul', class_='last price')
                    selectedCurrenties[currency.find("li").text] = float(price.text)
            else:
                price = currency.find('ul', class_='last price')
                selectedCurrenties[currency.find("li").text] = float(price.text)

    return selectedCurrenties

class Sending:
    price = 1
    oldprice = 1
    def __init__(self, bot, user_id, crypto, sign, value, time, ownCurrency):
        self._bot = bot
        self.user_id = user_id

        self._sign = sign
        self._value = float(value)

        self._time = float(time)

        self.crypto = crypto
        self.ownCurrency = ownCurrency

        self.is_started = False
        self._task = None

        if sign == "изменится на":
            self.text = f'{self.crypto} {self._sign} {self._value}% за последних {int(time/3600)} часов'
        else:
            self.text = f'{self.crypto} {self._sign} {self._value} за последних {int(time/3600)} часов'

        self.text_id = f'{user_id} {self.crypto} {self._sign} {self._value} {self._time}'
    async def Start(self):
        if not self.is_started:
            self.is_started = True
            self._task = asyncio.ensure_future(self._Sending())


    async def Stop(self):
        if self.is_started:
            self.is_started = False
            self._task.cancel()

    async def _Sending(self):
        Currencies = await GetCurrencies(self.ownCurrency, price=True)
        self.price = Currencies[self.crypto]
        self.oldprice = self.price
        while True:
            Currencies = await GetCurrencies(self.ownCurrency, price=True)
            self.price = Currencies[self.crypto]

            if self._sign == 'больше' and self.price >= self._value:
                await self._bot.send_message(self.user_id, self.text)
            elif self._sign == 'меньше' and self.price <= self._value:
                await self._bot.send_message(self.user_id, self.text)
            elif self._sign == 'изменится на':
                if (self.price - self.oldprice)*100/self.oldprice >= self._value:
                    await self._bot.send_message(self.user_id, f'{self.crypto} поднялась на {round((self.price - self.oldprice)*100/self.oldprice, 2)}% до {self.price}')
                elif abs((self.price - self.oldprice)*100/self.oldprice) <= self._value:
                    await self._bot.send_message(self.user_id, f'{self.crypto} упала на {round((self.price - self.oldprice)*100/self.oldprice, 2)}% до {self.price}')

            self.oldprice = self.price

            await asyncio.sleep(self._time)