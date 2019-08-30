from tqdm import tqdm
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import gc

from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters

from time import sleep
import multiprocessing as mp

# instantiating pandas.plotting
register_matplotlib_converters()

# batch split into two
def batch_split_two(df_):
    """
    This is a simple function that will split a large df into two different dataframes in half. Considering Used mainly for testing
    ARGS:
        df_: <pandas dataframe object> - time series dataframe
    """
    # grabbing size
    batch_size = int(len(df_) / 2)
    
    # splitting into two
    df1 = df_.iloc[:batch_size].copy()
    df2 = df_.iloc[batch_size:].copy()
    
    # converting dates into floats for ohlc
    df1['date'] = [mdates.date2num(d) for d in df1['date']]
    df2['date'] = [mdates.date2num(d) for d in df2['date']]
    
    # returning
    return df1, df2

    
    
# test function
def candlestick_test(df_, window_size, candle_width=0.015):
    """
    This is a test function which will return a sample candlestick plot 
    ARGS:
        df_: <pandas dataframe object> - time series dataframe
        window_size: <int> - the window size. If you select 15 and each timestep is 1hr, then the window size is 15hrs
        candle_width: <float> - width of the candlestick - you may need to play around with this number and 'eye it'
    """
    # grabbing window size 
    test_window = df_.iloc[:int(window_size)].copy()
    
    # converting dates into floats for ohcl framework
    test_window['date'] = [mdates.date2num(d) for d in test_window['date']]
    
    # re-arranging values for ohlc
    quotes = [tuple(x) for x in test_window[['date', 'open', 'high', 'low', 'close']].values]
    
    # plotting
    fig, ax = plt.subplots()
    candlestick_ohlc(ax, quotes, width=candle_width, colorup='g', colordown='r')
    
    # hiding axis
    plt.yticks([])
    plt.xticks([])
    plt.axis('off')
    
    # creating plot
    plt.gcf().autofmt_xdate()
    
    
def save_images(df_, save_path,  buy_percentage, sell_percentage, window_size=15, target_size=3, candle_size=0.022):
    """
    This function will be our worker function - take a dataframe along with the save_path and other parameters to create a buy and sell dataset. 
    
    ARGS:
        df_: <pandas dataframe object>
        save_path: <string> - where we will store all our images
        window_size: <int> - how many timesteps will a window consist of: if you select 15, and each timestep is 1hr, then the window size will be 15hr
        target_size: <int> - how far off are we labeling an projecting? If you select 3, then we are labeling on the 18th (if the window size is 15)
        candle_size: <float> - the size of each candle
        buy_percentage: <float> - how much of an increase in price from window end to target for the image to be labeled as buy? If you select 0.03 we are only labeling images buy if there was an increase by 3% from the close of the end of the window_size to the open of the target
        sell_percentage: <float> - same as buy but for sell
    """
    gc.disable()
    
    # instantiating 
    start_index = 0
    end_index = window_size   # size of the window
    label_index = window_size + target_size # our target
    
    # checking if this is the first batch
    if df_.index.min() == 0:
        img_index = 0
    
    else:
        # grabbing the starting index of the dataframe
        img_index = df_.index.min() + 1 
    
    for i in tqdm(range(len(df_))):
        
        try:

            # Creating our window
            window_df = df_.iloc[start_index:end_index]
            
            # grabbing close 
            day_close = window_df.iloc[-1]['close']
            
            # Calculating % increase
            buy_percent_increase = day_close + (day_close * buy_percentage)
            
            # Calculating % decrease
            sell_percent_decrease = day_close - (day_close * sell_percentage)
            
            # Converting window_df into quotes for OHCL
            quotes = [tuple(x) for x in window_df[['date','open','high','low','close']].values]
            
            # Plot candlestick.
            fig, ax = plt.subplots()
            candlestick_ohlc(ax, quotes, width=candle_size, colorup='g', colordown='r')

            # hiding x, y values
            plt.yticks([])
            plt.xticks([])
            plt.axis('off')

            plt.gcf().autofmt_xdate()
            
            # Labelling 
            
            # BUY
            if df_.iloc[label_index]['open'] >= buy_percent_increase:
                
                # Saving buy
                label = 'Buy'
                plt.savefig(f'{path}/{img_index}.{label}.png', dpi=100)
                
                # Clearing memory
                plt.close('all')
                plt.clf()
                plt.cla()
                fig.clf()

                # Increase image index
                img_index += 1
            
            # SELL
            elif df_.iloc[label_index]['open'] <= sell_percent_decrease:
                
                # Sell
                label = 'Sell'
                plt.savefig(f'{path}/{img_index}.{label}.png', dpi=100)
                
                # Clearing memory
                plt.close('all')
                plt.clf()
                plt.cla()
                fig.clf()

                # Increase image index
                img_index += 1
                
            # HOLD
            else:
                
                # Hold
                label = 'Hold'
                plt.savefig(f'{path}/{img_index}.{label}.png', dpi=100)
                
                
                # Clearing memory
                plt.close('all')
                plt.clf()
                plt.cla()
                fig.clf()

                # Increase index
                img_index += 1
                
            # Coutning up index
            start_index += 1
            end_index += 1
            label_index += 1
            
            if i % 1000 == 0:
                sleep(5)
                gc.collect()
                sleep(5)

            
        except Exception:
            pass
        
        
    # finished
    print('Finished')