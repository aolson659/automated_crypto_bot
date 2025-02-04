
'''I want to mention this again, do not run this script on a live account, the strategy in this script is for demenstraion puposes
only, it is not profitable.

This is the main script used to run the trading bot. It operates in a loop, analyzing data based on the designated timeframe when
there are no open positions. It calls funcitons that are used to gather account data which is necessary for opening a position. It
also fetches historical data used in analysis when determing whehter or not to open a position.

When a position is opened, it pulls data continuosly to monitor whether or not price has reached a threshold that would close the
position for a profit or a loss.'''

import ccxt
import time
from datetime import datetime, timedelta
import warnings
import traceback
import math

import position_management
import fetch_data
import utils

warnings.filterwarnings('ignore', category=FutureWarning)

# I recommend storing api keys in a seperate configuration file but for functionality and testing you could enter them like this
api_key = 'Your API key'
api_secret = 'Your API Secret'

api_key = 'fd602895-26e0-46e0-849c-b679a4f6df71'
api_secret = 'xL9QPouWvd8FWW6q6aOU7o4ohV8lsTbItpCSRDcI6jYwOTJkNWExYy05ZjY0LTQxZDAtOTdkZi1hYzhlZDAwNTBjZjc'


# Initialize exchange parameters and variables to track positions
exchange = ccxt.phemex({
    'apiKey': api_key,
    'secret': api_secret,
})

# Adjust these variable to trade desired base currency/asset
base_currency = 'USDT'
symbol = 'BTC/USDT:USDT'
timeframe = '5m'
paper_trade = True # Setting to true enables paper trading, where the script will not place actual trades, but keep track of trades that would have been made, showing the effectiveness of the strategy without risking capital
interval = 5

# Set the initial balance of the account to track overall profit/loss
free, used, total = fetch_data.fetch_balance(base_currency)
initial_balance = free
balance = initial_balance

# Adjust these to trade desired base currency/asset
base_currency = 'USDT'
symbol = 'BTC/USDT:USDT'
timeframe = '5m'
interval = 5

# Set the initial balance of the account to track overall profit/loss
free, used, total = fetch_data.fetch_balance(base_currency)
initial_balance = free
balance = initial_balance

opens_l = [] # Generate list to keep track of long positions
opens_s = [] # Generate list to keep track of short positions
start = 0 # Data is gathered in increments aligned with the timeframe, this varaible is used to gather data when the program is initially ran
open_position = False
buy = 0 # This variable is used to identify when a long position is open
sell = 0 # This variable is used to identify when a short position is open
risk = 0.1 # Set this to the amount you want to risk per trade
reward = 1 # This variable is the ratio between a winning position and a losing position, setting to 1 means that each winning trade and losing trade will cancel each other out
long_profit = 0 # Number of winning long positions
short_profit = 0 # Number of winning short positions
long_loss = 0 # Number of losing long positions
short_loss = 0 # Number of losing short positions
width = 20 # Used to format print statements

# These are used to identify when a timeframe interval is reached, signaling an api call for new data
check_time = 0
current_minute = 0

'''
This loop accomplishes two things, it fetches data at the timeframe interval when there are no positions open, and
it fetches ticker data continuosly when there are poisiotns open to minimize slippage when closing the position.'''
while True:
    try:

        current_time = datetime.now()
        chart_time = current_time + timedelta(hours=7) # Modify this line according to your time zone so that timestamps match the time displayed on the exchange

        # Gather data to determine whether or not to open a position
        if not open_position:
            # Check if new time interval has occured
            if (current_time.minute % interval == 0 or current_time.minute == 0) and current_minute != current_time.minute:
                if check_time == 0:
                    check_time = 1
            else:
                check_time = 0

            # Fetch new data at time interval
            if ((check_time == 1 and current_minute != current_time.minute) or start == 0):
                df = fetch_data.fetch_ohlcv_data(symbol, timeframe) 
                start = 1
                df = fetch_data.prepare_data(df)
                df = df.dropna()
                current_minute = current_time.minute
                check_5 = 0

                ticker = exchange.fetch_ticker(symbol)
                current_price = ticker['last']

                # Print statements showing asset data and overall profitability data
                utils.print_no_positoin(df, current_price, long_profit, long_loss, short_profit, short_loss, balance, initial_balance, total)

        

        else:
            # Fetch current price while there is an open position
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            if buy > 0:
                # Print statements showing data on open long position
                utils.print_long_position(initial_price, current_price, leverage, tp, sl)
                
            if sell > 0:
                # Print statements showing data on open short position
                utils.print_short_position(initial_price, current_price, leverage, tp, sl)


        '''The strategy present in this script will open a long position when the 20 period moving average crosses above the 
        50 period moving average, it will open a short position when the 20 period moving average falls below the 50 period
        moving average.'''
        if not open_position:
            # Logic for opening a long position
            if  df['MA_20'].iloc[-2] <= df['MA_50'].iloc[-2] and df['MA_20'].iloc[-1] >= df['MA_50'].iloc[-1]:
                initial_price = current_price
                open_time = df['Timestamp'].iloc[-1]
                sl = initial_price * 0.99 # Stop loss for closing the posiiton 1% below opening price
                open_position = True
                buy = 1
                sell = 0
                leverage = math.floor(risk / (abs(((initial_price - sl) / initial_price)) + 0.0015)) # Set leverage so that the difference in price between opening and closing a position will result in the designated risk above
                if leverage > 100:
                    leverage = 100
                tp = initial_price * (1 + (((reward / (1 - (risk + 0.0015))) - 1) / leverage)) # Set profit level so that closing a position will match the risk/reward ratio dsignated above

                free, used, total = fetch_data.fetch_balance(base_currency)
                exchange.set_leverage(leverage, symbol, {"hedged":True})
                quantity = position_management.find_quantity(free * 0.9, leverage, current_price) #Amount sent to the exchange is needs to be converted based on the currency being traded

                position_management.buy_asset(quantity, symbol) # API call for opening a long position

                time.sleep(1)
            
                df_positions = position_management.position_info(symbol) #Fetches the actual opening price of the position from the exchange
                opens_l.append(df_positions['Entry Price'].iloc[0])
                initial_price = opens_l[-1]
                # Recalculate stop loss and take profit based on actual opening price of the position
                sl = opens_l[-1] * 0.99
                tp = opens_l[-1] * (1 + (((reward / (1 - (risk + 0.0015))) - 1) / leverage))
                print('-----------------------------------------------------------------')
                print(f"{'Open Long:':<{width}}{opens_l[-1]:.2f}")
                print()
                continue

            # Logic for opening a short position
            if  (df['MA_20'].iloc[-2] >= df['MA_50'].iloc[-2] and df['MA_20'].iloc[-1] <= df['MA_50'].iloc[-1]) or 2 == 2:                
                ''' This segment of code is structed the same as for opening a long position, however the logic for take profit
                and stop loss are inversely calculated.'''

                initial_price = current_price
                open_time = df['Timestamp'].iloc[-1]
                sl = initial_price / 0.99
                open_position = True
                buy = 0
                sell = 1
                leverage = math.floor(risk / (abs(((sl - initial_price) / initial_price)) + 0.0015))
                if leverage < 1:
                    leverage = 1
                if leverage > 100:
                    leverage = 100
                tp = initial_price / (1 + (((reward / (1 - (risk + 0.0015))) - 1) / leverage))

                free, used, total = fetch_data.fetch_balance(base_currency)
                exchange.set_leverage(leverage, symbol, {"hedged":True})
                quantity = position_management.find_quantity(free * 0.9, leverage, current_price)

                position_management.sell_asset(quantity, symbol)

                time.sleep(1)
                
                df_positions = position_management.position_info(symbol)
                opens_s.append(df_positions['Entry Price'].iloc[1])
                initial_price = opens_s[-1]
                sl = opens_s[-1] / 0.99
                tp = opens_s[-1] / (1 + (((reward / (1 - (risk + 0.0015))) - 1) / leverage))
                print('-----------------------------------------------------------------')
                print(f"{'Open Short:':<{width}}{opens_s[-1]:.2f}")
                print()
                continue

        # The following segment is for closing positions
        if buy > 0:
            # Closing a profitable long position
            if current_price >= tp:
                long_profit += 1
                open_position = False
                position_management.close_position(symbol, quantity * buy, 'Long') # API call for closing a long position
                print('-----------------------------------------------------------------')
                print(f"{'Close Long:':<{width}}{current_price:.2f}")
                buy = 0
            # Closing a long position for a loss
            elif current_price <= sl:
                long_loss += 1
                open_position = False
                position_management.close_position(symbol, quantity * buy, 'Long')
                print('-----------------------------------------------------------------')
                print(f"{'Close Long:':<{width}}{current_price:.2f}")
                buy = 0
        if sell > 0:
            # Closing a profitable short position
            if current_price <= tp:
                short_profit += 1
                open_position = False
                position_management.close_position(symbol, quantity * sell, 'Short') # API call for closing a short position
                print('-----------------------------------------------------------------')
                print(f"{'Close Short:':<{width}}{current_price:.2f}")
                sell = 0
            # Closing a short position for a loss
            elif current_price >= sl:
                short_loss += 1
                open_position = False
                position_management.close_position(symbol, quantity * sell, 'Short')
                print('-----------------------------------------------------------------')
                print(f"{'Close Short:':<{width}}{current_price:.2f}")
                sell = 0

    except Exception as e:
        if 'https://api.phemex.com/' in str(e):
            print(f"Phemex API Error")
            time.sleep(5)
        elif 'Time Series' in str(e):
            re_vantage = 1
        else:
            tb = traceback.format_exc()
            print(f"An error occurred: {e}\nTraceback: {tb}")
            continue