'''The functions in this script are called to execute trades (opening and closing long and short positoins), calucate the value used to
open a position with the desired amount of base currency, and gather data on currently open positions.'''

import ccxt
import pandas as pd
import time

import fetch_data

# I recommend storing api keys in a seperate configuration file but for functionality and testing you could enter them like this
api_key = 'Your API key'
api_secret = 'Your API Secret'

api_key = 'fd602895-26e0-46e0-849c-b679a4f6df71'
api_secret = 'xL9QPouWvd8FWW6q6aOU7o4ohV8lsTbItpCSRDcI6jYwOTJkNWExYy05ZjY0LTQxZDAtOTdkZi1hYzhlZDAwNTBjZjc'

exchange = ccxt.phemex({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,  
})

''' Function for calculating the acutal values to be sent to the exchange when opening a position,
amount is base currency you want to use to open the position, leverage is calculated based on the risk
you are willing to accept for each position, and current price is used to determine how much of the asset you want to buy based
on the amount of base currency you are opening the position with.'''
def find_quantity(amount, leverage, current_price):
    quantity = leverage * (((amount) / current_price))

    return quantity

# Function for opening a long position
def buy_asset(quantity, symbol):
    try:
        order = exchange.create_order(symbol,'market','buy',quantity, params = {'posSide': 'Long'}) 
    except ccxt.BaseError as e:
        print(f'Error opening long position: {e}')

# Function for opening a short position
def sell_asset(quantity, symbol):
    try:
        order = exchange.create_order(symbol,'market','sell',quantity, params = {'posSide': 'Short'}) 
    except ccxt.BaseError as e:
        print(f'Error opening short position: {e}')

# Function for closing a position
def close_position(symbol, quantity, position_side):
    try:
        order = exchange.create_order(
            symbol, 'market', 'buy' if position_side == 'Short' else 'sell',
            quantity, params={'posSide': position_side}
        )
        print(f"Closed {quantity} of {position_side} position.")
    except ccxt.BaseError as e:
        print(f'Error while closing position: {e}')

# Fetch data on currently open positions, mainly used to fetch opening price of a position
def position_info(symbol):
    try:
        positions = exchange.fetch_positions(symbols=[symbol])

        positions_data = []
        
        for position in positions:
            position_data = {
                'User ID': position['info']['userID'],
                'Account ID': position['info']['accountID'],
                'Symbol': position['symbol'],
                'Side': position['side'],
                'Size': position['contracts'],
                'Leverage': position['leverage'],
                'Entry Price': position['entryPrice'],
                'Mark Price': position['markPrice'],
                'Liquidation Price': position['liquidationPrice'],
                'Unrealized PNL': position['unrealizedPnl'],
                'Initial Margin': position['initialMargin'],
                'Maintenance Margin': position['maintenanceMargin'],
                'Margin Ratio': position['marginRatio']
            }
            positions_data.append(position_data)
        
        df_positions = pd.DataFrame(positions_data)
        
        return df_positions

    except Exception as e:
        print(f"Error fetching position data: {e}")



# Test code used to verify the functions are working properly, be aware that you will pay fees when opening/closing positions
if __name__ == '__main__':
    # Set paramaters

    test_long = False # Set to True to test opening and closing a long position
    test_short = False # Set to True to test opening and closing a short position

    symbol = 'BTC/USDT:USDT'
    base_currency = 'USDT'
    leverage = 5
    exchange = ccxt.phemex({
        'apiKey': api_key,
        'secret': api_secret,
    })

    ticker = exchange.fetch_ticker(symbol)
    current_price = ticker['last']

    print('Current price', current_price)

    free, used, total = fetch_data.fetch_balance(base_currency)

    print('Available balance', free)

    # This code will open a long position as long as the api keys are valid and there is enough base currency in the account, it will then close the position
    if test_long:
        input('Press enter to open a long position...')
        exchange.set_leverage(leverage, symbol, {"hedged":True})
        quantity = find_quantity(free * 0.9, leverage, current_price)

        buy_asset(quantity, symbol)

        time.sleep(5)

        df_positions = position_info(symbol)
        entry_price = df_positions['Entry Price'].iloc[0]
        print(entry_price)

        close_position(symbol, quantity, 'Long')

    # This will do the same but for a short position
    if test_short:
        input('Press enter to open a short position...')
        exchange.set_leverage(leverage, symbol, {"hedged":True})
        quantity = find_quantity(free * 0.9, leverage, current_price)

        sell_asset(quantity, symbol)

        time.sleep(5)

        df_positions = position_info(symbol)
        entry_price = df_positions['Entry Price'].iloc[0]
        print(entry_price)

        close_position(symbol, quantity, 'Short')




