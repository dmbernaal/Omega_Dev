import os
import pandas as pd
import numpy as np

def return_open_close_change(df_, target_):
    """
    This function will return a new pandas series with percentage change between opening price of target time and close of starting price.
    
    ARGS:
        df_: <pandas dataframe object>
        target_: <int> - this is the beginning index of the close we are comparing. This will increment on a rolling basis
    """ 
    df = df_.copy()
    
    # creating our series
#     change = df['open'] - df['close'].shift(target_ - 1)
#     change = ((df['open'] - df['close'].shift(target_ - 1)) / df['close'].shift(target_ - 1)) 
    change = ((df['open'] - df['close'].shift(target_)) / df['close'].shift(target_)) 
    
    return change

def return_open_close_range_change(df_, range_):
    """
    This function adds onto the single return_open_close_change and will return a dataframe of size range_
    
    ARGS:
        df_: <pandas dataframe object>
        range_: <int> max range 
        
    RETURN a DF of size: (index, target)
    
    The target is how far off we are predicting
    """
    df = df_.copy()
    
    # instantiating our df
    changes = pd.DataFrame(data=[])
    
    # looping and creating our df
    for i in range(range_):
        change = return_open_close_change(df, i+1)
        changes[i+1] = change
        
    return changes