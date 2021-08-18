import os
import sys
import re
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))

from module.auto_trader2 import exchange_api, util

logger = util.CreateLogger('Trader')
class Trader():
    def __init__(self, exchange, access_key:str=None, secret_key:str=None):
        self.exchange = exchange.lower()
        self.api = exchange_api.Exchange_Api(exchange = exchange, access_key=access_key, secret_key=secret_key)
    
    def gap_rate_buy2curr(self, currency_pair:str):
        """
        현재가와 매수 평균가 차이 비율 -> 손절/익절에 사용

        Parameters
        ----------
        currency_pair : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
            
        currency = re.findall("(.*?)_.*", currency_pair)[0]
        
        avg_buy_price = self.api.get_avg_buy_price(currency)
        if avg_buy_price == 0:
            return 0
        curr_price = self.api.get_curr_price(currency_pair)
        
        return curr_price / avg_buy_price
    
    def get_curr_price(self, currency_pair:str):
        """
        현재가 조회 함수

        Parameters
        ----------
        currency_pair : str
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return float(self.api.get_ticker(currency_pair=currency_pair).iloc[0]['trade_price'])
    def error_handler(self, df):
        if df is None:
            return pd.DataFrame()
        else:
            return df
    def get_last_order_time(self, currency_pair, side):
        wait_df = self.error_handler(self.api.get_orders(currency_pair, 'wait'))
        done_df = self.error_handler(self.api.get_orders(currency_pair, 'done'))
        
        if (len(done_df) != 0) and (len(wait_df) == 0):
            last_time = done_df.iloc[0]['create_time_utc']
        elif (len(done_df) == 0) and (len(wait_df)) != 0:
            last_time =  wait_df.iloc[0]['create_time_utc']
        elif (len(done_df) != 0) and (len(wait_df) != 0):
            last_time =  max(wait_df.iloc[0]['create_time_utc'], done_df.iloc[0]['create_time_utc'])
        else:
            return
        return last_time
        
    def get_avg_buy_price(self, currency):
        df = self.api.get_accounts()
        if currency in list(df['currency']):
            return float(df[df['currency'] == currency].iloc[0]['avg_buy_price'])
        else:
            logger.info(f'{currency} 보유량 없음')
            return 0
        
    def get_price(self, currency_pair, side, unit_num=1):
        """
        매수/매도 호가, 현재가 조회 함수

        Parameters
        ----------
        currency_pair : TYPE
            DESCRIPTION.
        side : TYPE
            'buy':매수호가
            'sell':매도호가
            'curr':현재가.
        unit_num : TYPE, optional
            1: 매수/매매 1호가
            2: 매수/매매 2호가
            .       *
            .       *
            . The default is 1.

        Returns
        -------
        price : TYPE
            DESCRIPTION.

        """
        orderbook_units = self.api.get_orderbook(currency_pair).iloc[0]['orderbook_units']
        if side == 'sell':
            price = orderbook_units[unit_num-1]['ask_price']
        elif side == 'buy':
            price = orderbook_units[unit_num-1]['bid_price']
        elif side == 'curr':
            price = self.api.get_curr_price(currency_pair)
        return price
    
    def get_volume(self, currency):
        """
        보유량 조회

        Parameters
        ----------
        currency : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        
        accounts = self.api.get_accounts()
        if currency not in list(accounts['currency']):
            return 0
        return float(accounts[accounts['currency'] == currency].iloc[0]['available'])
    
    def create_order(self, currency_pair:str, side:str, volume:str=None, price:str=None, ord_type:str='limit'):
        """
        주문 생성 함수

        Parameters
        ----------
        currency_pair : str
            DESCRIPTION.
        side : str
            DESCRIPTION.
        volume : str, optional
            DESCRIPTION. The default is None.
        price : str, optional
            DESCRIPTION. The default is None.
        ord_type : str, optional
            DESCRIPTION. The default is 'limit'.

        Returns
        -------
        None.

        """
        self.api.create_order(currency_pair, side, volume, price, ord_type)
    
    def cancel_orders(self, currency_pair:str, side:str):           
        return self.api.cancel_orders(currency_pair=currency_pair, side=side)
        
    def stop_order(self, currency_pair:str, volume_rate:str, ord_type:str, orderbook_side:str, orderbook_unit:int=1, stop_loss=None, stop_profit=None):
        """
        손절 조건 만족시 주문 생성 함수

        Parameters
        ----------
        stop_loss : TYPE
            DESCRIPTION.
        currency_pair : TYPE
            DESCRIPTION.
        volume_rate : TYPE
            DESCRIPTION.
        orderbook_side : TYPE
            DESCRIPTION.
        ord_type : TYPE
            DESCRIPTION.
        orderbook_unit : TYPE, optional
            DESCRIPTION. The default is 1.

        Returns
        -------
        None.

        """
           
        currency = re.findall("(.*?)_.*", currency_pair)[0]
        # 손절 조건이 만족하면 매도
        if stop_loss != None:
            if (1 - self.gap_rate_buy2curr(currency_pair)) >= stop_loss:
                price = self.get_price(currency_pair, orderbook_side, orderbook_unit)
                volume = self.get_volume(currency)
                if volume == 0:
                    return
                self.api.create_order(currency_pair, 'sell', volume, price, ord_type)
        # 익절 조건을 만족하면 매도        
        elif stop_profit != None:
            if (self.gap_rate_buy2curr(currency_pair) - 1) >= stop_profit:
                price = self.get_price(currency_pair, orderbook_side, orderbook_unit)
                volume = self.get_volume(currency)
                if volume == 0:
                    return
                self.api.create_order(currency_pair, 'sell', volume, price, ord_type)
