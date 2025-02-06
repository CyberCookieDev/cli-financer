
import yfinance as yf
import os
import colorama
import json
from colorama import Style
import argparse

colorama.init(autoreset=True)
Fore = colorama.Fore
Back = colorama.Back

def add_watchlist(name):
    with open(f"watchlists/{name}.json", "w") as f:
        json.dump([], f)
        pass

def add_to_portfolio(marker, number, price):
    try:
        with open("portfolio.json", "r") as file:
            data = json.load(file) 

    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    number = int(number)
    price = int(price)

    if marker not in data:
        total_price = price * number
        data[marker] = {"actions": number, "price": total_price}
    else:
        data[marker]["actions"] += number
        data[marker]["price"] += number * price

    with open("portfolio.json", "w") as file:
        json.dump(data, file, indent=4)

def add_to_watchlist(name, marker):
    try:
        with open(f"watchlists/{name}.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    if marker not in data:
        data.append(marker)  # Add stock to watchlist

    with open(f"watchlists/{name}.json", "w") as f:
        json.dump(data, f, indent=4)  # Save changes

def display_watchlist(name):
    with open(f"watchlists/{name}.json", "r") as f:
        for x in f:
            get_stock_change(x)

def remove_from_watchlist(name, marker):
    with open(f"watchlists/{name}.json", "w") as f:
        data = f
        data.pop(marker)
        json.dump(data, f)

def fetch_latest(marker):
    stock = yf.Ticker(marker)
    print(stock.history(period="1d")['Close'][0])


def get_stock_news(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    news = stock.news  # Fetch latest news

    if not news:
        print("No news found.")
        return

    print(f"\n Latest News for {ticker_symbol.upper()}:")
    for article in news[:5]:  # Limit to 5 articles

        print(f"\n {article['content']['title']}")

# Calculate change of price since the last day.

def get_stock_change(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="2d")
    if len(data) < 2:
        return "Not enough data"

    current_price = data['Close'].iloc[-1]
    prev_close = data['Close'].iloc[-2] 
    change = current_price - prev_close
    percent_change = (change / prev_close) * 100

    return f"{ticker}: {current_price:.2f} USD ({change:+.2f}USD, {percent_change:+.2f}%)"


def vital_info(marker):
    company = yf.Ticker(marker)

    name = company.info.get('longName', 'N/A')
    sector = company.info.get('sector', 'N/A')
    website = company.info.get('website', 'N/A')
    market_cap = company.info.get('marketCap', 'N/A')
    fifty_two_week_high = company.info.get('fiftyTwoWeekHigh', 'N/A')
    fifty_two_week_low = company.info.get('fiftyTwoWeekLow', 'N/A')

    output = f"""
{Fore.CYAN}{Style.BRIGHT}Marker: {Fore.GREEN}{marker}
{Fore.CYAN}{Style.BRIGHT}Name: {Fore.GREEN}{name}
{Fore.CYAN}{Style.BRIGHT}Sector: {Fore.GREEN}{sector}
{Fore.CYAN}{Style.BRIGHT}Current Price: {Fore.GREEN}{get_stock_change(marker)}
{Fore.CYAN}{Style.BRIGHT}Website: {Fore.BLUE}{website}
{Fore.CYAN}{Style.BRIGHT}Market Cap: {Fore.GREEN}{market_cap}
{Fore.CYAN}{Style.BRIGHT}52-Week High: {Fore.RED}{fifty_two_week_high}
{Fore.CYAN}{Style.BRIGHT}52-Week Low: {Fore.RED}{fifty_two_week_low}
"""

    print(output)

def show_portfolio():
    try:
        with open("portfolio.json", "r") as f:
            data = json.load(f)  # Read portfolio data
    except (FileNotFoundError, json.JSONDecodeError):
        print("No portfolio data found.")
        return

    for marker, details in data.items():
        company = yf.Ticker(marker)
        x = int(details["actions"]) * int(company.info["currentPrice"])
        x -= details["price"]
        if x >= 0:
            color = Fore.GREEN
        else:
            color = Fore.RED
        print(f"{Fore.CYAN}- {get_stock_change(marker)}  {color}Gains/Losses: {x} USD")



def search(marker):
    with open("portfolio.json", "r") as f:
        data = f
        if marker in data:
            company = yf.Ticker(marker)
            x = int(marker["actions"]) * int(company.info["currentPrice"])
            x -= marker["price"]
            if x >= 0:
                color = Fore.GREEN
            else:
                color = Fore.RED
            print(f"{Fore.CYAN}- {get_stock_change(marker)}  {color}Gains/Losses: {x} USD")
    vital_info(marker)

def display_watchlists():
    print(Fore.CYAN + "Available watchlists")
    for x in os.listdir('watchlists'):
        print(Fore.GREEN + f"- {x}")


parser = argparse.ArgumentParser(description="Stock CLI App")

parser.add_argument("--news", metavar="TICKER", help="Show latest stock news for TICKER")
parser.add_argument("--watchlist", metavar="NAME", help="Create a new watchlist")
parser.add_argument("--add", nargs=3, metavar=("TICKER", "NUMBER", "PRICE"), help="Add stock to portfolio")
parser.add_argument("--portfolio", action="store_true", help="Show portfolio performance")
parser.add_argument("--search", metavar="TICKER", help="Search for a stock in portfolio")
parser.add_argument("--fetch", action="store_true", help="Fetch latest stock price for TICKER")
parser.add_argument("--remove", nargs=2, metavar=("WATCHLIST", "MARKER"), help="Remove stock from watchlist")
parser.add_argument("--display", metavar="WATCHLIST", help="Show watchlist")
parser.add_argument("--list", action="store_true", help="List all watchlists")
parser.add_argument("--addto", nargs=2, metavar=("WATCHLIST", "MARKER"), help="Add stock to specific watchlist")


args = parser.parse_args()

if args.watchlist:
    add_watchlist(args.watchlist)

if args.add:
    add_to_portfolio(args.add[0], args.add[1], args.add[2])

if args.portfolio:
    show_portfolio()

if args.search:
    search(args.search)

if args.news:
    get_stock_news(args.news)

if args.fetch:
    fetch_latest(args.fetch)

if args.remove:
    remove_from_watchlist(args.remove[0], args.remove[1])

if args.addto:
    add_to_watchlist(args.addto[0], args.addto[1])

if args.display:
    display_watchlist(args.display)

if args.list:
    display_watchlists()
