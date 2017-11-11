from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import argparse

# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind

import pandas

###########################################
# Crossover Stratey based on SMA crossovers
###########################################

class SMAStrategy(bt.Strategy):
    params = (
        ('fastperiod', 30*60),
		('slowperiod', 89*60),
        ('tp_delta', 0.015),
        ('sl_delta', 0.01)
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s : %s' % (dt.isoformat(), txt))


    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.sellprice = None
        
        # Add a MovingAverageSimple indicator
        self.fastsma = btind.SimpleMovingAverage(self.datas[0], period=self.params.fastperiod)
        self.slowsma = btind.SimpleMovingAverage(self.datas[0], period=self.params.slowperiod)
        
        self.cross = btind.CrossOver(self.fastsma,self.slowsma)
        
        self.orefs = list()
        
		
    def notify_order(self, order):
        self.log('{}: Order ref: {} / Type {} / Status {}'.format(
            self.data.datetime.date(0),
            order.ref, 'Buy' * order.isbuy() or 'Sell',
            order.getstatusname()))

        if order.status == order.Completed:
            self.holdstart = len(self)

        if not order.alive() and order.ref in self.orefs:
            self.orefs.remove(order.ref)
    

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        # self.log('Close, %.2f' % self.dataclose[0])
               
        # Check if orders are pending ... if yes, do nothing
        if self.orefs:
            return

        # Check if we are in the market
        if not self.position:

            # positive crossover

            tp_d = self.params.tp_delta
            sl_d = self.params.sl_delta

        #print( self.datadate[0])
        #print('date %s open %.5f, close %.5f' % (str(self.data.datetime.datetime()),self.datas[0].open[0],self.datas[0].close[0]))
        #print( 'sma fast %.2f' % self.fastsma[0])
            if self.cross > 0.0:
                  
                print('Crossover positive')

                # BUY
                self.log('BUY CREATE, %.5f' % self.dataclose[0])

                close = self.dataclose[0]
                tp = close + close * tp_d
                sl = close - close * sl_d
                os = self.order = self.buy_bracket( price=close,exectype=bt.Order.Market,stopprice=sl,limitprice=tp)               
                # Keep track of the created orders
                self.orefs = [o.ref for o in os]

                # try trailing stop
                #os = self.order = self.sell()
                #self.orefs.append( os.ref)
                #os = self.order = self.buy( exectype=bt.Order.StopTrail, trailpercent=sl_d)
                #self.orefs.append( os.ref)

           # negative crossover
            
            if self.cross < 0.0:
                
                print('Crossover negative')

                # SELL
                self.log('SELL CREATE, %.5f' % self.dataclose[0])

                close = self.dataclose[0]
                tp = close - close * tp_d
                sl = close + close * sl_d
                os = self.order = self.sell_bracket( price=close,exectype=bt.Order.Market,stopprice=sl,limitprice=tp)
                # Keep track of the created orders
                self.orefs = [o.ref for o in os]

                # try trailing stop
                #os = self.order = self.sell()
                #self.orefs.append( os.ref)
                #os = self.order = self.buy( exectype=bt.Order.StopTrail, trailpercent=sl_d)
                #self.orefs.append( os.ref)


def parse_args():

    parser = argparse.ArgumentParser(description='SimpleCross Back Tester')

    parser.add_argument('--fast', action='store_true',default='8',required=False,help='Period of the faster moving average (default: 8)')
    parser.add_argument('--slow', action='store_true',default='89',required=False,help='Period of the slower moving average (default: 89)')
    parser.add_argument('--fast_type', action='store_true',default='SMA',choices=['SMA','EMA'],required=False,help='Type of faster moving average (SMA or EMA) (default: SMA)')
    parser.add_argument('--slow_type', action='store_true',default='SMA',choices=['SMA','EMA'],required=False,help='Type of slower moving average (SMA or EMA) (default: SMA)')

    return parser.parse_args()


############################
# MAIN
############################                

def main():         

    args = parse_args()

    # for smaller datasets, especially when tesitng
    startdate = datetime.datetime(2006, 1, 1)
    enddate = datetime.datetime(2006, 1, 31)

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(SMAStrategy)

    # load the csv data (converted from hst)
    datapath = ('../data/test/EURUSD_1min.csv')
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        fromdate=startdate,
        todate=enddate,
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1,
        timeframe=bt.TimeFrame.Minutes
        )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(10000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=5000)

    # Set the commission
 #   cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getcash())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('Final Cash Value: %.2f' % cerebro.broker.getcash())

    # Plot the result
    cerebro.plot(volume=False)

if __name__ == '__main__':
    main()