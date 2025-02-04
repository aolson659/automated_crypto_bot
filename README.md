# automated_crypto_bot

## Description
automated_crypto_bot has the capability to autonomously trade cryptocurrencies through exchanges that are available in the ccxt library. The strategy currently built into the program is simple and for demonstration purposes only, do not run this on a live account, the strategy is not profitable.

The origin of this project came out of necessity, I was already developing a trading bot through the platform trality.com. This site offered a web-based python editor and the capability to connect to cryptocurrency exchanges, however, the platform ceased operations and I decided to work towards building this capability myself.

The code provided operates in a loop, analyzing historical data and making decisions on whether to open a long position or a short position. It monitors price closely once a position is opened, and will close the position if the price reaches a designated level.

Again, this will perform actions on a live account if you decide to run this using your own funds and API keys.

# Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

### Prerequisites
- Python 3.8 or higher
- pandas==1.1.3
- ccxt==1.30.59

### Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/aolson659/automated_crypto_bot.git

2. **Navigate to project directory**:
   cd automated_crypto_bot

3. **Install required python libraries**:
   pip install -r requirements.txt

### Running the program
You will need to generate API keys and fund an account on one of the exchanges available in your region, as well as an exchange available through the ccxt library.

You can assign your API keys to a variable within the script, however, I would suggest storing your API keys in a separate configuration file.

The program operates in a loop, so it will need to be ran continuously. You can do this in an editor, or you can use `nohup` to run it in the background.

To run nohup:
- nohup python main.py

### Features
This project's purpose is to provide an outline for running an automated crypto trading program. Stocks, cryptocurrencies, and other financial markets can be described as chaotic time series, which are inherently unpredictable. Running this program should only be done after thorough testing has been completed. Testing can be done by backtesting strategies on historical data, or it can be done by paper trading (placing fictional trades, risking no money) which is an option using paper_trade.py

Example output while no open position:

------------------------------------------------------------------------------------------------
Timestamp: 2025-01-31 00:55:00
Ticker:             104820.90
Recent Open:        104909.00
Recent High:        104909.10
Recent Low:         104822.60
Recent Close:       104846.60
Recent Volume:      3.04
MA 20:              104818.10
MA 50:              105035.35

Long Wins:          0.00
Long Losses:        0.00

Short Wins:         0.00
Short Losses:       0.00

Total P/L:          1.0000
Total Trades:       0.0000
Balance:            100.00

Example output while long position is open:

------------------------------------------------------------------------------------------------
Long Open 104797.000
Current Price 104796.800

Long PL 0.997
Long TP 105406.593
Long SL 104587.406

Example output while short position is open:

------------------------------------------------------------------------------------------------
Short Open 103326.000
Current Price 103327.800

Long PL 0.997
Short TP 103533.061
Long SL 102725.548

### Contact
For collaboration and troubleshooting, you can reach me at aolsondm@gmail.com


