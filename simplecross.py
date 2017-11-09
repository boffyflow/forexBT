from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('fastperiod', 8),
		('slowperiod', 89)
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.sellprice = None
        
        # Add a MovingAverageSimple indicator
        self.fastsma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.fastperiod)
        self.slowsma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.slowperiod)
        
        self.cross = bt.ind.CrossOver(self.fastsma,self.slowsma)
        
        self.orefs = list()
        
		
    def notify_order(self, order):
        print('{}: Order ref: {} / Type {} / Status {}'.format(
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
            if self.cross > 0.0:
                    
                self.log('Crossover positive')
                
                # BUY
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                close = self.dataclose[0]
                tp = 1.1 * close
                sl = 0.95 * close
                os = self.order = self.buy_bracket( price=close,exectype=bt.Order.Market,stopprice=sl,limitprice=tp)
                # Keep track of the created orders
                self.orefs = [o.ref for o in os]
                
            # negative crossover
            
            if self.cross < 0.0:
                
                self.log('Crossover negative')

                # SELL
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                close = self.dataclose[0]
                tp = 0.9 * close
                sl = 1.05 * close
                os = self.order = self.sell_bracket( price=close,exectype=bt.Order.Market,stopprice=sl,limitprice=tp)
                # Keep track of the created orders
                self.orefs = [o.ref for o in os]
              

############################
# MAIN
############################                
                
if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'backtrader-master/datas/orcl-1995-2014.txt')

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(1996, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(2013, 12, 31),
        # Do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(10000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    #cerebro.plot()