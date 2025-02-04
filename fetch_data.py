'''The functions in this script are used to fetch historical ohlcv (open, high, low, close, and volume) data and make calculations on that data
which is then used in determining whether or not to open a position. The function for fetching account balance, necessary for keeping track
of profit/loss and determining proper values used to open and close positions is also present in this script.'''

import ccxt
import ccxt.async_support as ccxt
import pandas as pd
import warnings
import asyncio


warnings.filterwarnings('ignore')

# I recommend storing api keys in a seperate configuration file but for functionality and testing you could enter them like this
api_key = 'Your API key'
api_secret = 'Your API Secret'


# This function establishes a connection to the exchange, retrieves historical data, and formats it into a pandas dataframe.
async def async_ohlcv(symbol, timeframe):
    exchange = ccxt.phemex({'enableRateLimit': True})

    await exchange.load_markets()

    ohlcv = await exchange.fetch_ohlcv(symbol, timeframe)

    df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')

    await exchange.close()
    
    return df

# This function allows the asynchronous fetching of OHLCV data to be called in other scripts.
def fetch_ohlcv_data(symbol, timeframe):
    ohlcv_data = asyncio.run(async_ohlcv(symbol, timeframe))
    return ohlcv_data


'''This function calculates the metrics used in the strategy, this is where you would also put logic to make other calculations when developing
your own strategy, metrics like RSI, MACD, Bollinger Bands, etc...'''
def prepare_data(df):
    
    df['MA_20'] = df['Close'].rolling(window=20).mean()
    df['MA_50'] = df['Close'].rolling(window=60).mean()

    df = df.dropna()

    return df


# Establishes a connection with the exchange to fetch the account balance
async def test(api_key, api_secret):
    exchange = ccxt.phemex({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True
    })

    if hasattr(exchange, 'futures'):
        exchange.options['defaultType'] = 'future'

    try:
        balance = await exchange.fetch_balance(params={"type": "swap"})
    except Exception as e:
        print("An error occurred:", e)
    finally:
        await exchange.close()  

    return balance

'''Return the account balance of the desiganted base currency, free is amount availabe to purchase assets
 with, used is amount currently invested into open positions.'''
async def main(base_currency):
    balance = await test(api_key, api_secret)
    free = balance['free'][base_currency]
    used = balance['used'][base_currency]
    total = balance['total'][base_currency]

    return free, used, total 

# This function allows the asynchronous fetching of account data to be called in other scripts.
def fetch_balance(base_currency):
    free, used, total = asyncio.run(main(base_currency))

    return free, used, total  

    

if __name__ == '__main__':
    '''Test code used to fetch account data and historical data'''

    base_currency = 'USDT'
    timeframe = '5m'
    limit = 200

    free, used, total = fetch_balance(base_currency)
    initial_balance = free

    print(f"{base_currency} Free: {free}")
    print(f"{base_currency} Used: {used}")
    print(f"{base_currency} Total: {total}")

    symbol = 'BTC/USDT:USDT'

    df = fetch_ohlcv_data(symbol, timeframe)
    print(df)

    df = prepare_data(df)
    print(df)
