import aiohttp
import asyncio
from datetime import datetime, timedelta
import sys
from typing import List, Dict, Any


class CurrencyAPI:
    BASE_URL = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='

    async def get_currency_rates(self, date: str) -> Dict[str, Any]:
        """API request to get the exchange rate for a specific date."""
        url = f"{self.BASE_URL}{date}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                print(f"Error when requesting the API: {e}")
                return {}


def filter_currency_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Фільтрує курси для валют EUR та USD."""
    filtered = {}
    for rate in data.get("exchangeRate", []):
        if rate['currency'] in ['EUR', 'USD']:
            filtered[rate['currency']] = {
                'sale': rate['saleRate'],
                'purchase': rate['purchaseRate']
            }
    return filtered


class CurrencyService:
    def __init__(self, _api: CurrencyAPI):
        self.api = _api

    async def get_rates_for_days(self, _days: int) -> List[Dict[str, Any]]:
        """Gets exchange rates for a specified number of days."""
        results = []
        for i in range(_days):
            date = (datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')
            data = await self.api.get_currency_rates(date)
            if data:
                filtered_data = filter_currency_data(data)
                results.append({date: filtered_data})
        return results


class CLI:
    def __init__(self, _service: CurrencyService):
        self.service = _service
        self.rates = None

    async def run(self, _days: int):
        if _days < 1 or _days > 10:
            print("Please enter the number of days from 1 to 10.")
            return

        self.rates = await self.service.get_rates_for_days(_days)
        self.display_rates()

    def display_rates(self) -> None:
        """Displays rates for all currencies in a clear format."""
        for day_data in self.rates:
            for date, currencies in day_data.items():
                print(f"Date: {date}")
                for currency, rate in currencies.items():
                    sale = rate['sale']
                    purchase = rate['purchase']
                    print(f"\t{currency}: Sale - {sale}, Purchase - {purchase}")
                print("-" * 30)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the number of days as an argument.")
        sys.exit(1)

    try:
        days = int(sys.argv[1])
    except ValueError:
        print("The argument must be a number.")
        sys.exit(1)

    api = CurrencyAPI()
    service = CurrencyService(api)
    cli = CLI(service)
    asyncio.run(cli.run(days))
