# Script for mining data via OandaAPI
import sys
import json
import os
import time

from datetime import date

from oandapyV20.contrib.factories import InstrumentsCandlesFactory
from oandapyV20 import API

# instantiating API Acess
access_token = "75e433aae2d86eb803457a23008a4cd5-4e2eddaf539b5f55b612cea9cb36e4f6" # change this
client = API(access_token=access_token)

# Pulling Functions
def cnv(r, h):
    for candle in r.get('candles'):
        ctime = candle.get('time')[0:19]
        try:
            rec = "{time},{complete},{o},{h},{l},{c},{v}".format(
                time=ctime,
                complete=candle['complete'],
                o=candle['mid']['o'],
                h=candle['mid']['h'],
                l=candle['mid']['l'],
                c=candle['mid']['c'],
                v=candle['volume'],
            )
        except Exception as e:
            print(e, r)
        else:
            h.write(rec+"\n")

def download_data(start_date, end_date, gr, instr, path):
    """
    
    This will download raw price action data from OandaAPI and will save it to the path provided in CSV format. 
    
    ARGS:
        start_date: <datetime object> - example: date(2009, 6, 1)
        end_date: <datetime object>
        gr: <string> - granularity of the data (time intervals). Check readme
        instr: <string> - instrument or 'pair' - example: "GBP_USD"
        path: <string> - path to save the CSV
    """
    _from = f'{start_date.isoformat()}T00:00:00Z'
    _to = f'{end_date.isoformat()}T00:00:00Z'
    gran = gr
    instr_ = instr

    params = {
        "granularity": gran,
        "from": _from,
        "to": _to
    }
    
    print(f'Saving to path: {path}')
    
    with open(f'{path}/{instr}_{gran}_{start_date.isoformat()}_{end_date.isoformat()}.csv', "w") as O:
        for r in InstrumentsCandlesFactory(instrument=instr_, params=params):
            print("REQUEST: {} {} {}".format(r, r.__class__.__name__, r.params))
            rv = client.request(r)
            cnv(r.response, O)
            
    print('Finished')