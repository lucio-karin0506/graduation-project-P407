import os
import sys
import re
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))

from module.auto_trader import exchange_api, util

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
        
        avg_buy_price = self.get_avg_buy_price(currency)
        if avg_buy_price == 0:
            return 0
        curr_price = self.get_curr_price(currency_pair)
        
        return util.floor(curr_price / avg_buy_price, 8)
    
    def get_pair2currency(self, currency_pair):
        """
        코인이름+마켓 -> 코인 이름

        Parameters
        ----------
        currency_pair : TYPE
            코인 이름+마켓
            EX) BTC_USDT, XRP_KRW.

        Returns
        -------
        TYPE
            코인이름
            EX) BTC, XRP.

        """
        return re.findall("(.*?)_.*", currency_pair)[0]
    
    def get_evaluation_amount(self, currency_pair):
        """
        코인의 현재 평가 가치
        소수점 이하 8자리까지 표현
        Parameters
        ----------
        currency_pair : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            현재 평가 가치.

        """
        currency = self.get_pair2currency(currency_pair)
        evaluation_amount = self.get_volume(currency) * self.get_curr_price(currency_pair)
        return util.floor(evaluation_amount,8)
    
    def get_total_evaluation_amount(self):
        """
        사용자의 모든 보유 코인 + 현금의 현재 가치

        Returns
        -------
        floor
            소수점 이하 8자리까지.

        """
        result = 0
        for index, row_df in self.api.get_accounts().iterrows():
            if row_df['currency'] in ['USDT', 'GT', 'KRW']:
                result += float(row_df['balance'])
            elif row_df['currency'] in ['USDTEST']:
                continue
            else:
                if self.exchange == 'upbit':
                    result += self.get_evaluation_amount(f"{row_df['currency']}_KRW")
                elif self.exchange == 'gate':
                    result += self.get_evaluation_amount(f"{row_df['currency']}_USDT")
        return util.floor(result, 8)
    
    def get_rate2volume(self, volume_rate):
        """
        현재 총 보유자산 대비 비율 금액

        Parameters
        ----------
        volume_rate : TYPE
            비율.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return util.floor(self.get_total_evaluation_amount() * volume_rate, 8)
                
    def get_curr_price(self, currency_pair:str):
        """
        현재가 조회 함수

        Parameters
        ----------
        currency_pair : str
            BTC_USDT.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return util.floor(self.api.get_ticker(currency_pair=currency_pair).iloc[0]['trade_price'],8)
    def error_handler(self, df):
        """
        NoneType 확인

        Parameters
        ----------
        df : TYPE
            DESCRIPTION.

        Returns
        -------
        0: int
            NoneType.
        1: int
            Not NoneTYpe

        """
        if df is None:
            return 0
        else:
            return 1
    def get_last_order_time(self, currency_pair, side):
        """
        마지막 주문 요청 시간 조회

        Parameters
        ----------
        currency_pair : TYPE
            DESCRIPTION.
        side : TYPE
            wait: 체결 대기
            done: 체결 완료.

        Returns
        -------
        last_time : TYPE
            utc.

        """
        wait_df = self.api.get_orders(currency_pair, 'wait')
        done_df = self.api.get_orders(currency_pair, 'done')
        if self.error_handler(wait_df):
            wait_df = pd.DataFrame()
        if self.error_handler(done_df):
            done_df = pd.DataFrame()

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
        """
        매수 평균가 조회

        Parameters
        ----------
        currency : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        df = self.api.get_accounts()
        if currency in list(df['currency']):
            return util.floor(df[df['currency'] == currency].iloc[0]['avg_buy_price'],8)
        else:
            # logger.info(f'{currency} 보유량 없음')
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
            price = self.get_curr_price(currency_pair)
        return util.floor(price, 8)
    
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
        balance = accounts[accounts['currency'] == currency].iloc[0]['balance']
        return util.floor(balance, 8)
        
    
    def create_order(self, currency_pair:str, side:str, total_value, ordbook_type=0,ord_type:str='limit'):
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
        if ordbook_type == 0:
            price = self.get_price(currency_pair,'curr')
        elif ordbook_type == -1:
            price = self.get_price(currency_pair, 'buy', 1)
        elif ordbook_type == -2:
            price = self.get_price(currency_pair, 'buy', 2)
        elif ordbook_type == 1:
            price = self.get_price(currency_pair, 'sell', 1)
        if side == 'buy':
            amount = total_value / price
        elif side == 'sell':
            amount = total_value
        amount =util.floor(amount, 8)
        ret = self.api.create_order(currency_pair, side, amount, price, ord_type)
        
        if self.error_handler(ret):
            if self.exchange == 'upbit':
                ret =ret.rename(columns={'uuid':'id', 'market':'currency_pair', 'created_at':'create_time', 'remaining_volume':'left', 'volume':'amount'})
            elif self.exchange == 'gate':
                ret = ret.rename(columns={'type':'ord_type'})
            return ret[['id','currency_pair','side','ord_type','side','price','amount','left','create_time']]
    
    def cancel_orders(self, currency_pair:str, side:str):           
        """
        매수 or 매도 포지션의 주문 취소

        Parameters
        ----------
        currency_pair : str
            DESCRIPTION.
        side : str
            'buy': 매수포지션 주문 취소
            'sell': 매도포지션 주문 취소.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
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
                
    def is_withdrwas(self):
        """
        출금 가능 API KEY 확인

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self.api.is_withdrawl()
        

if __name__ == '__main__':
    # user = Trader(exchange='upbit', access_key='xPBD01XVAMNUF5mfxOYbc6BR7xCrtb2LRTRJmrHS', secret_key='CS0cqYUmzPv4wqaaZX4rBX8hZGCz67xfzWvtHYs5')
    user = Trader(exchange='gate', access_key='60f9f7df5fdb7a4ac64d1efba7bbda7a', secret_key='d4bb73c3aa84f6834f0fd5a056eb3d72789a730cef08492a88a33c3d492f726f')

    # gap = user.gap_rate_buy2curr('META_KRW')
    # price = user.stop_loss_order(currency_pair='BTC_USDT',stop_loss=0.01, volume_rate=0.5, ord_type='limit', orderbook_side='curr')
    # cancel = user.cancel_orders('XRP_KRW', 'buy')
    # last_time = user.get_last_order_time('XRP_KRW', 'buy')
    a = user.get_total_evaluation_amount()