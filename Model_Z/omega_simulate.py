import pandas as pd
import numpy as np
import os

# trading function
def simulate_thresh_test_trade(sequence, buy_threshold, sell_threshold, start_cap, print_trades=True, return_attr=True):
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
    x_s = sell_threshold
    
    bc = start_cap
    starting_cap = start_cap
    
    h = 0 # how many assets we own
    
    change_window = sequence.columns[2] # column with change window size
    
    start_idx = 0
    end_idx = int(change_window)
    
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
            h = round(bc / tni)
            
            if print_trades:
                print('----------------------------------------')
                print('Buying')
                print(pn0)
                print(f'capital: {bc}')
                print(f'bought at: {tni}')
                print(f'bought {h} shares\n\n')
            
            # resetting our capital to nothing
            bc = 0
            
        # selling assets if sell threshold is met
        elif window.iloc[-1][change_window] <= sell_threshold and bc == 0 and h > 0:
            
            # grabbing final buy - best one to grab
            tnf0 = window.iloc[-2]
            tnf = tnf0['open'] # selling at open
            
            # selling off shares
            bc = h * tnf
            
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
        
    # metrics
    roi = (bc / starting_cap) * 100
    roi = int(roi)
    
    # logging our performance
    print(f'Starting capital: {start_cap}')
    print(f'Ending capital: {bc}')
    print(f'Return on investment: {roi}%')
    
    if return_attr:
        # returning metrics & others
        return start_cap, bc, roi, buy_threshold, sell_threshold, change_window