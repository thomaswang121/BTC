from datetime import datetime
import pathlib
import backtrader as bt
# from __future__ import (absolute_import, division, print_function, unicode_literals)
import pyfolio as pf
from pyfolio import timeseries 
from reference.Strategy import zwpy_sta
import pandas as pd
import json

BTC_data = pathlib.Path().cwd() / "data" / "BTC_hour.csv"


cerebro = bt.Cerebro()
cerebro.addstrategy(zwpy_sta.MacdV2Strategy)
cerebro.broker.setcash(100000)

dt_start = datetime.strptime("20210101","%Y%m%d")
dt_end = datetime.strptime("20211028","%Y%m%d")
data = bt.feeds.GenericCSVData(
    timeframe = bt.TimeFrame.Minutes,
    compression = 60,
    dataname=BTC_data,
    fromdate=dt_start,      
    todate=dt_end,
    nullvalue=0.0,
    dtformat=('%Y-%m-%d %H:%M:%S'),   
    datetime=0,            
    open = 1,
    high = 2,
    low = 3,
    close = 4,
    openinterest=-1,
    volume = -1
)
cerebro.adddata(data)
print('Starting Value: %.2f' % cerebro.broker.getvalue())
cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
cerebro.addanalyzer(bt.analyzers.Returns, _name = "returns")
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = "sharpe")
results = cerebro.run()
print('Ending Value: %.2f' % cerebro.broker.getvalue())
strat = results[0]      
pyfoliozer = strat.analyzers.getbyname('pyfolio')
returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()

pf.create_full_tear_sheet(returns,)
perf_func = timeseries.perf_stats 
perf_stats_all = perf_func( returns,positions=None, transactions=None, turnover_denom="AGB")
strat.compare['sharpe']['macdV2']=perf_stats_all['Sharpe ratio']
with open("./report/compare.json", "w")as f:
    json.dump(strat.compare, f, indent = 4)
cerebro.plot(iplot = False)