import pandas as pd
import math
import numpy as np
import os

# trading function
def simulate_thresh_test_trade_basic(sequence, buy_threshold, sell_threshold, start_cap, print_trades=True, return_attr=True):
    """
    This function will simulate a trade when given a sequence dataframe with a specific column holding percentage change values. SIMPLE does not include spread cost per currency pair OR leverage functionality
    
    This is an 'absolute' ideal trading simulation in which the threshold simulates what a product will produce. We are assuming we get every trade right
    
    ARGS:
        sequence: <pandas.DataFrame> should contain: open, close, percentage change: example ['24'] represent percent change in 24 hour window.
            column 1 = open or close
            column 2 = open or close
            column 3 = change window: example: '24' = 24 hour window
        
        buy_threshold: <float> represents how much % of a change in sequence['change_window'] must there be for this to be a buy?
        
        sell_threshold: <float> represents the same as buy but for selling the asset
        
        start_cap: <int or float> represents our starting capital
        
        window_size: <int> represents how large of a window this can also be set from int(sequence['change_window'])
        
        print_trades: <boolean> if True, this will print every trade made 
    
    RETURNS:
        start_cap, bc, roi, buy_threshold, sell_threshold, change_window
    
    ALGORITHM:
    if pn0 > x && bc > 0 && h == 0:
        grab opening price tn0
        buy shares with bc at tn0
        update bc to 0
        next el

    # sell and wait
    if pn0 < tn0 && bc == 0 && h > 0:
        grab tnf
        sell h at tnf (h * tnf)
        update bc to (h * tnf)
        update h to 0
        next el

    else:
        pass
    """
    # setting our parameters
    x_p = buy_threshold
    x_s = -sell_threshold
    
    bc = start_cap
    starting_cap = start_cap
    
    h = 0 # how many assets we own
    
    change_window = sequence.columns[2] # column with change window size
    
    start_idx = 0
    end_idx = int(change_window) + 1
    
    # Trading
    for i in range(len(sequence)):
        
        # grabbing window
        window = sequence.iloc[start_idx:end_idx]
        
        # buying trade if buy threshold met
        if window.iloc[-1][change_window] >= buy_threshold and bc > 0 and h == 0:
            
            # grabbing end and beginning of window
            pn0 = window.iloc[-1]
            tn0 = window.iloc[0]
            tni = tn0['open'] # buying the opening price
            
            # buying h shares
            h = math.floor(bc / tni)
            
            if print_trades:
                print('----------------------------------------')
                print('Buying')
                print(tn0)
                print(f'capital: {bc}')
                print(f'bought at: {tni}')
                print(f'bought {h} shares\n\n')
            
            # updating our capital to what is left over
            bc = bc - (h * tni)
            
            
        # selling assets if sell threshold is met
        elif window.iloc[-1][change_window] <= x_s and h > 0:
            
            # grabbing final buy - best one to grab
            tnf0 = window.iloc[-2]
            tnf = tnf0['open'] # selling at open
            
            # selling off shares
            bc = bc + (h * tnf)
            
            if print_trades:
                print('Selling')
                print(tnf0)
                print(f'capital: {bc}')
                print(f'sold at: {tnf}')
                print(f'sold {h} shares\n')
                
            # updating shares own - sold all
            h = 0
            
        # no threshold met - we HOLD
        else:
            pass
        
        # moving window
        start_idx += 1
        end_idx += 1
    
    # update our buying capital if we haven't sold
    if bc > 0 and bc < 100:
        print('Selling off shares, a sell execution was not triggered but we are displaying this for the sake of displaying metrics')
        bc = bc + (h * tnf) 
    
    roi = ((bc - starting_cap) / starting_cap) * 100
    roi = int(roi)
    
    # logging our performance
    print(f'Starting capital: {start_cap}')
    print(f'Ending capital: {bc}')
    print(f'Return on investment: {roi}%')
    
    if return_attr:
        # returning metrics & others
        return start_cap, bc, roi, buy_threshold, sell_threshold, change_window


def simulate_thresh_test_trade(sequence, buy_threshold, sell_threshold, start_cap, print_trades=True, return_attr=True, margin_trading=False):
    """
    This function will simulate a trade when given a sequence dataframe with a specific column holding percentage change values. 
    
    This is an 'absolute' ideal trading simulation in which the threshold simulates what a product will produce. We are assuming we get every trade right
    
    ARGS:
        sequence: <pandas.DataFrame> should contain: open, close, percentage change: example ['24'] represent percent change in 24 hour window.
            column 1 = open or close
            column 2 = open or close
            column 3 = change window: example: '24' = 24 hour window
        
        buy_threshold: <float> represents how much % of a change in sequence['change_window'] must there be for this to be a buy?
        
        sell_threshold: <float> represents the same as buy but for selling the asset
        
        start_cap: <int or float> represents our starting capital
        
        window_size: <int> represents how large of a window this can also be set from int(sequence['change_window'])
        
        print_trades: <boolean> if True, this will print every trade made 
    
    RETURNS:
        start_cap, bc, roi, buy_threshold, sell_threshold, change_window
    
    ALGORITHM:
    if pn0 > x && bc > 0 && h == 0:
        grab opening price tn0
        buy shares with bc at tn0
        update bc to 0
        next el

    # sell and wait
    if pn0 < tn0 && bc == 0 && h > 0:
        grab tnf
        sell h at tnf (h * tnf)
        update bc to (h * tnf)
        update h to 0
        next el

    else:
        pass
    """
    # setting our parameters
    x_p = buy_threshold
    x_s = -sell_threshold
    
    bc = start_cap
    starting_cap = start_cap
    
    h = 0 # how many assets we own
    
    change_window = sequence.columns[2] # column with change window size
    
    start_idx = 0
    end_idx = int(change_window) + 1
    
    # tracking metrics
    total_transaction_costs = 0
    
    # checking for margin trading
    if margin_trading:
        bc = margin_trade(bc)
        beginning_leverage = bc
    
    # Trading
    for i in range(len(sequence)):
        
        # grabbing window
        window = sequence.iloc[start_idx:end_idx]
        
        # buying trade if buy threshold met
        if window.iloc[-1][change_window] >= buy_threshold and bc > 0 and h == 0:
            
            # grabbing end and beginning of window
            pn0 = window.iloc[-1]
            tn0 = window.iloc[0]
            tni = tn0['open'] # buying the opening price
            
            # calculating how many shares we can buy with our current capital - without trasaction cost included
            h_pre = math.floor(bc / tni)
            
            # calculating our cost of the trade - using core
            core_cost = omega_oanda_core_cost(h_pre)
            total_transaction_costs += core_cost
            
            # updating our capital - charging the core cost of the trade
            bc = bc - core_cost
            
            # buying h shares with core cost included
            h = math.floor(bc / tni)
            
            if print_trades:
                print('----------------------------------------')
                print('Buying')
                print(tn0)
                print(f'capital: {bc}')
                print(f'bought at: {tni}')
                print(f'transaction cost: {core_cost}')
                print(f'bought {h} shares\n\n')
            
            # updating our capital to what is left over
            bc = bc - (h * tni)
            
            
        # selling assets if sell threshold is met
        elif window.iloc[-1][change_window] <= x_s and h > 0:
            
            # grabbing final buy - best one to grab
            tnf0 = window.iloc[-2]
            tnf = tnf0['open'] # selling at open
            
            # selling off shares
            bc = bc + (h * tnf)
            
            # calculating our core cost
            core_cost = omega_oanda_core_cost(h)
            total_transaction_costs += core_cost
            
            # upating our capital with core cost
            bc = bc - core_cost
            
            if print_trades:
                print('Selling')
                print(tnf0)
                print(f'capital: {bc}')
                print(f'sold at: {tnf}')
                print(f'transaction cost: {core_cost}')
                print(f'sold {h} shares\n')
                
            # updating shares own - sold all
            h = 0
            
        # no threshold met - we HOLD
        else:
            pass
        
        # moving window
        start_idx += 1
        end_idx += 1
    
    # update our buying capital if we haven't sold
    if bc > 0 and bc < 100 and h > 0:
        print('Selling off shares, a sell execution was not triggered but we are displaying this for the sake of displaying metrics')
        bc = bc + (h * tnf) 
        core_cost = omega_oanda_core_cost(h)
        total_transaction_costs += core_cost
        bc = bc - core_cost
    
    roi = ((bc - starting_cap) / starting_cap) * 100
    roi = int(roi)
    
    # logging our performance
    print(f'Starting capital: {start_cap}')
    if margin_trading:
        print(f'Beginning Leverage: {beginning_leverage}')
    print(f'Ending capital: {bc}')
    print(f'Return on investment: {roi}%')
    print(f'Total Transaction cost: {total_transaction_costs}')
    
    if return_attr:
        # returning metrics & others
        return start_cap, bc, roi, buy_threshold, sell_threshold, change_window


def simulate_thresh_test_trade_best(sequence, buy_threshold, sell_threshold, start_cap, print_trades=True, return_attr=True, margin_trading=False):
    """
    This function will simulate a trade when given a sequence dataframe with a specific column holding percentage change values. The differnce between this and the simulate_thresh_test_trade is that we will sell upon the price dropping sell_threshold from the price we bought at, not at the 24 hour window.
    
    This simulation will only work if we were to combine an ensemble to our buy/sell predictions. That is using a fixed time-window for our buy signals, but using a RNN for our sell threshold. Reasons being, an RNN will predict an any:any
    
    This is an 'absolute' ideal trading simulation in which the threshold simulates what a product will produce. We are assuming we get every trade right
    
    ARGS:
        sequence: <pandas.DataFrame> should contain: open, close, percentage change: example ['24'] represent percent change in 24 hour window.
            column 1 = open or close
            column 2 = open or close
            column 3 = change window: example: '24' = 24 hour window
        
        buy_threshold: <float> represents how much % of a change in sequence['change_window'] must there be for this to be a buy?
        
        sell_threshold: <float> represents the same as buy but for selling the asset
        
        start_cap: <int or float> represents our starting capital
        
        window_size: <int> represents how large of a window this can also be set from int(sequence['change_window'])
        
        print_trades: <boolean> if True, this will print every trade made 
    
    RETURNS:
        start_cap, bc, roi, buy_threshold, sell_threshold, change_window
    
    ALGORITHM:
    if pn0 > x && bc > 0 && h == 0:
        grab opening price tn0
        buy shares with bc at tn0
        update bc to 0
        next el

    # sell and wait
    if pn0 < tn0 && bc == 0 && h > 0:
        grab tnf
        sell h at tnf (h * tnf)
        update bc to (h * tnf)
        update h to 0
        next el

    else:
        pass
    """
    # setting our parameters
    x_p = buy_threshold
    x_s = -sell_threshold
    sell_thresh = 0
    
    bc = start_cap
    starting_cap = start_cap
    
    h = 0 # how many assets we own
    
    change_window = sequence.columns[2] # column with change window size
    
    start_idx = 0
    end_idx = int(change_window) + 1
    
    # tracking metrics
    total_transaction_costs = 0
    
    # checking for margin trading
    if margin_trading:
        bc = margin_trade(bc)
        beginning_leverage = bc
    
    # Trading
    for i in range(len(sequence)):
        
        # grabbing window
        window = sequence.iloc[start_idx:end_idx]
        
        # buying trade if buy threshold met
        if window.iloc[-1][change_window] >= buy_threshold and bc > 0 and h == 0:
            
            # grabbing end and beginning of window
            pn0 = window.iloc[-1]
            pni = pn0['open']
            tn0 = window.iloc[0]
            
            # buying mid
            tni = (tn0['open'] + tn0['close']) / 2 # buying the opening price
            
            # calculating how many shares we can buy with our current capital - without trasaction cost included
            h_pre = math.floor(bc / tni)
            
            # calculating our cost of the trade - using core
            core_cost = omega_oanda_core_cost(h_pre)
            total_transaction_costs += core_cost
            
            # updating our capital - charging the core cost of the trade
            bc = bc - core_cost
            
            # buying h shares with core cost included
            h = math.floor(bc / tni)
            
            # initializing our sell threshold
            sell_thresh = pni + (pni * x_s)
            
            if print_trades:
                print('----------------------------------------')
                print('Buying')
                print(tn0)
                print(f'capital: {bc}')
                print(f'bought at: {tni}')
                print(f'transaction cost: {core_cost}')
                print(f'Sell threshold: {sell_thresh}')
                print(f'bought {h} shares\n\n')
            
            # updating our capital to what is left over
            bc = bc - (h * tni)
            
            
        # selling assets if sell threshold is met
        elif window.iloc[-1]['open'] <= sell_thresh and h > 0:
            
            # grabbing final buy - best one to grab
            tnf0 = window.iloc[-2]
            tnf = tnf0['open'] # selling at open
            
            # selling off shares
            bc = bc + (h * tnf)
            
            # calculating our core cost
            core_cost = omega_oanda_core_cost(h)
            total_transaction_costs += core_cost
            
            # upating our capital with core cost
            bc = bc - core_cost
            
            if print_trades:
                print('Selling')
                print(tnf0)
                print(f'capital: {bc}')
                print(f'sold at: {tnf}')
                print(f'transaction cost: {core_cost}')
                print(f'sold {h} shares\n')
                
            # updating shares own - sold all
            h = 0
            
        # no threshold met - we HOLD
        else:
            pass
        
        # moving window
        start_idx += 1
        end_idx += 1
        
        # updating our sell threshold
        
    
    # update our buying capital if we haven't sold
    if bc > 0 and bc < 100 and h > 0:
        print('Selling off shares, a sell execution was not triggered but we are displaying this for the sake of displaying metrics')
        bc = bc + (h * tnf) 
        core_cost = omega_oanda_core_cost(h)
        total_transaction_costs += core_cost
        bc = bc - core_cost
    
    roi = ((bc - starting_cap) / starting_cap) * 100
    roi = int(roi)
    
    # logging our performance
    print(f'Starting capital: {start_cap}')
    if margin_trading:
        print(f'Beginning Leverage: {beginning_leverage}')
    print(f'Ending capital: {bc}')
    print(f'Return on investment: {roi}%')
    print(f'Total Transaction cost: {total_transaction_costs}')
    
    if return_attr:
        # returning metrics & others
        return start_cap, bc, roi, buy_threshold, sell_threshold, change_window


def simulate_thresh_test_trade_simple(sequence, buy_threshold, start_cap, print_trades=True, return_attr=True, margin_trading=False):
    """
    This function will simulate a trade when given a sequence dataframe with a specific column holding percentage change values. This will follow a simple trading rule in which we will buy upon buy_threshold which will mimic our CNN and sell at the prediction window. 
    
    This is an 'absolute' ideal trading simulation in which the threshold simulates what a product will produce. We are assuming we get every trade right
    
    This is an 'absolute' ideal trading simulation in which the threshold simulates what a product will produce. We are assuming we get every trade right
    
    ARGS:
        sequence: <pandas.DataFrame> should contain: open, close, percentage change: example ['24'] represent percent change in 24 hour window.
            column 1 = open or close
            column 2 = open or close
            column 3 = change window: example: '24' = 24 hour window
        
        buy_threshold: <float> represents how much % of a change in sequence['change_window'] must there be for this to be a buy?
        
        start_cap: <int or float> represents our starting capital
        
        window_size: <int> represents how large of a window this can also be set from int(sequence['change_window'])
        
        print_trades: <boolean> if True, this will print every trade made 
    
    RETURNS:
        start_cap, bc, roi, buy_threshold, sell_threshold, change_window
    
    ALGORITHM:
    if pn0 > x && bc > 0 && h == 0:
        grab opening price tn0
        buy shares with bc at tn0
        update bc to 0
        sell at pn0
        next el

    else:
        pass
    """
    # setting our parameters
    x_p = buy_threshold
    
    bc = start_cap
    starting_cap = start_cap
    
    h = 0 # how many assets we own
    
    change_window = sequence.columns[2] # column with change window size
    
    start_idx = 0
    end_idx = int(change_window) + 1
    
    # tracking metrics
    total_transaction_costs = 0
    
    # checking for margin trading
    if margin_trading:
        bc = margin_trade(bc)
        beginning_leverage = bc
    
    # Trading
    for i in range(len(sequence)):
        
        try:
        
            # grabbing window
            window = sequence.iloc[start_idx:end_idx]
            pn0 = window.iloc[-1]

            # buying trade if buy threshold met
            if window.iloc[-1][change_window] >= buy_threshold and bc > 0 and h == 0:

                # grabbing end and beginning of window
                pn0 = window.iloc[-1]
                pni = pn0['open']
                tn0 = window.iloc[0]

                # buying mid
                tni = (tn0['open'] + tn0['close']) / 2 # buying the opening price

                # calculating how many shares we can buy with our current capital - without trasaction cost included
                h_pre = math.floor(bc / tni)

                # calculating our cost of the trade - using core
                core_cost = omega_oanda_core_cost(h_pre)
                total_transaction_costs += core_cost

                # updating our capital - charging the core cost of the trade
                bc = bc - core_cost

                # buying h shares with core cost included
                h = math.floor(bc / tni)

                if print_trades:
                    print('----------------------------------------')
                    print('Buying')
                    print(tn0)
                    print(f'capital: {bc}')
                    print(f'bought at: {tni}')
                    print(f'transaction cost: {core_cost}')
                    print(f'bought {h} shares\n\n')

                # updating our capital to what is left over
                bc = bc - (h * tni)

                # Selling - end of window
                bc = bc + (h * pni)

                # calculating our core cost
                core_cost = omega_oanda_core_cost(h)
                total_transaction_costs += core_cost

                # upating our capital with core cost
                bc = bc - core_cost

                if print_trades:
                    print('Selling')
                    print(pn0)
                    print(f'capital: {bc}')
                    print(f'sold at: {pni}')
                    print(f'transaction cost: {core_cost}')
                    print(f'sold {h} shares\n')

                # updating shares own - sold all
                h = 0

                start_idx += int(change_window)
                end_idx += int(change_window)

            # no threshold met - we HOLD
            else:
                # moving window
                start_idx += 1
                end_idx += 1
                pass
            
        except Exception:
            pass
        
        # updating our sell threshold
        
    
    # update our buying capital if we haven't sold
    if bc > 0 and bc < 100 and h > 0:
        print('Selling off shares, a sell execution was not triggered but we are displaying this for the sake of displaying metrics')
        bc = bc + (h * tni) 
        core_cost = omega_oanda_core_cost(h)
        total_transaction_costs += core_cost
        bc = bc - core_cost
    
    roi = ((bc - starting_cap) / starting_cap) * 100
    roi = int(roi)
    
    # logging our performance
    print(f'Starting capital: {start_cap}')
    if margin_trading:
        print(f'Beginning Leverage: {beginning_leverage}')
    print(f'Ending capital: {bc}')
    print(f'Return on investment: {roi}%')
    print(f'Total Transaction cost: {total_transaction_costs}')
    
    if return_attr:
        # returning metrics & others
        return start_cap, bc, roi, buy_threshold, change_window
    
def omega_oanda_core_cost(h, spread=0.00002):
    """
    This function will return the cost per trade when using Oanda API. This will also assume a spread average of 0.00002 
    
    In a real life trading scenario we will calculate the spread on the fly which will require ask, bid, mid for the time the trade is executed. This is related to the volume of the trade.
    
    ARGS:
        h: <int> the number of shares owned
        spread: <float> the spread (ask - bid)
    """
    # cost of the spread
    spread_cost = h * spread
    
    # cost of core 
    core_cost = spread_cost + ((h / 100000) * 5)
    
    return core_cost


def margin_trade(margin, leverage=20):
    """
    This will function will allow for margin trading which takes in the brokers leverage and how many assets you want to leverage which is the margin.
    
    Example: If your broker provides a 20:1 leverage, and your margin (down payment) is $1000, this means you will be able to use $20,000 in buying power
    
    ARGS:
        leverage: <int> the multiplier
        margin: <float> our downpayment, how much we are willing to leverage 
    """
    return margin * leverage

def calculate_margin_trade(low, high, h_lot, leverage=20):
    """
    This function is for exploratory purposes: We provide a given positions open and high which we will take to calculate the middle. Then from the leverage and lot size we want, we can return the total margin required for that trade. 
    
    That is, the total down payment to buy h_lot amount of asset.
    
    ARGS:
        low: <float> the lowest price of the asset at n time, this is the open for testing purposes
        high: <float> the highest price of the asset at n time
        h_lot: <int> how many of x asset we want to buy
        leverage: <int> the leverage provided from the broker
    """
    mid = (low + high) / 2
    h = h_lot * mid
    
    # calculating our margin, this is the minimum downpayment of the trade
    margin = (1/leverage) * h
    
    return margin