import requests
import os
from load_dotenv import load_dotenv

load_dotenv()


class Finance_API():
    def __init__(self):
        API_KEY = os.environ["FINANCIALMODELLINGREP_API_KEY"]
        self.add_api = f"&apikey={API_KEY}"

    def get_income_statement(self,ticker, period):
        # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
        url = f'https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period={period}&limit=50'+self.add_api
        r = requests.get(url)
        data = r.json()

        return (data)

    def get_balance_sheet(self, ticker, period = "annual"):
        url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?period={period}"
        r = requests.get(url)
        data = r.json()

        return (data)


    def get_transcripts(self,
                        company_ticker: str,
                        year: str,
                        quarter: str):
        url = f"https://financialmodelingprep.com/api/v3/earning_call_transcript/{company_ticker}?year={year}&quarter={quarter}"+self.add_api
        r = requests.get(url)
        data = r.json()

        return (data)


    def get_news(self):
        url = f"https://financialmodelingprep.com/api/v3/fmp/articles?page=0&size=100"+self.add_api
        r = requests.get(url)
        data = r.json()

        return (data)


        