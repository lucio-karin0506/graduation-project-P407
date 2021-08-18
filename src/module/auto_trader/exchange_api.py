import os
import sys
import re
sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))

from module.auto_trader import upbit_api, gateio_api, util
from datetime import datetime, timedelta
logger = util.CreateLogger('Trader')

class Exchange_Api:
    def __init__(self, exchange:str, access_key:str=None, secret_key:str=None):
        self.exchange = exchange.lower()
        self.access_key = access_key
        self.secret_key = secret_key
        
        # 거래소에 따라 거래소 api 변경
        if self.exchange == 'upbit':
            self.exchange_api = upbit_api.Upbit_Api(access_key=self.access_key, secret_key=self.secret_key)
        elif self.exchange == 'gate':
            self.exchange_api = gateio_api.Gate_Api(access_key=self.access_key, secret_key=self.secret_key)
        else:
            logger.error("거래소 이름 오류")
    def error_handler(self, df):
        """
        NoneType OR data is empty

        Parameters
        ----------
        df : TYPE
            DESCRIPTION.

        Returns
        -------
        0 : int
            NoneType OR data is empty.
        1 : int
            data is exists

        """
        if df is None:
            return 0
        elif len(df) == 0:
            return 0           
        else:
            return 1
    def c_name2upbit(self, currency_pair):
        """
        currency_pair 이름을 표준 이름('BTC_USDT')에서 업비트 포맷('KRW-BTC')으로 변경

        Parameters
        ----------
        currency_pair : TYPE
            DESCRIPTION.

        Returns
        -------
        str
            업비트에서 사용하는 포맷으로 변경된 currency_pair.

        """
        name = re.findall("(.*?)_(.*)", currency_pair)[0]
        return f'{name[1]}-{name[0]}'
    
    # input:대한민국(utc+9)
    def get_candle(self, currency_pair, start_date:str='', end_date:str='', interval='30m', limit=100):
        """
        캔들스틱 데이터 데이터프레임 형식으로 리턴
        date는 대한민국 시간 기준
        # UPBIT : start_date 미지원
        
        Parameters
        ----------
        currency_pair : TYPE
            DESCRIPTION.
        start_date : str, optional
            '%Y-%m-%d %H:%M:%S'. The default is ''.
        end_date : str, optional
            '%Y-%m-%d %H:%M:%S'. The default is ''.
        interval : TYPE, optional
            UPBIT:1m, 3m, 5m, 10m, 15m, 30m, 60m, 240m, d, w, M.
            GATE: 10s, 1m, 5m, 15m, 30m, 1h, 4h, 8h, 1d, 7d. The default is '30m'.
        limit : TYPE, optional
            #UPBIT: MAX(200)
            #GATE: MAX(1000). The default is 100.

        Returns
        -------
        TYPE
            캔들 데이터프레임.

        """
        # utc -> 대한민국
        
            
        if self.exchange == 'upbit':       
            if start_date != '':
                start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S") - timedelta(hours=9)
            if end_date != '':
                end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S") - timedelta(hours=9)
            if interval == '1h':
                interval = '60m'
            elif interval == '4h':
                interval = '240m'
            market = self.c_name2upbit(currency_pair)
            df = self.exchange_api.get_candle(market=market, start_date=start_date, 
                                     end_date=end_date, interval=interval, limit=limit)
            if self.error_handler(df) == 1:
                df = df.rename(columns={'market':'currency_pair'})
                df['currency_pair'] = currency_pair
                return df
        elif self.exchange == 'gate':
            if start_date != '':
                start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            if end_date != '':
                end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            if interval == 'w':
                interval = '1w'
            elif interval == '60m':
                interval = '1h'
            elif interval == '240m':
                interval = '4h'
            elif interval == '480m':
                interval = '8h'
            
            df =  self.exchange_api.get_candle(currency_pair=currency_pair, start_date=start_date, 
                                     end_date=end_date, interval=interval, limit=limit)
            
            df['close'] = [util.floor(close, 8) for close in list(df['close'])]
            df['open'] = [util.floor(open, 8) for open in list(df['open'])]
            df['high'] = [util.floor(high, 8) for high in list(df['high'])]
            df['low'] = [util.floor(low, 8) for low in list(df['low'])]
            
            return df
    
    def get_accounts(self):
        """
        코인 이름, 보유량, 평균 매수 금액 조회
        <유의> 업비트일 경우 원화 잔고에서 10을 뺀 잔고 리턴
        Returns
        -------
        TYPE
            데이터프레임.

        """
        if self.exchange == 'gate':
            return self.exchange_api.list_spot_accounts()
        elif self.exchange == 'upbit':
            df = self.exchange_api.get_accounts()
            krw_balance = float(df[df['currency'] == 'KRW']['balance'])
            df.loc[df[df['currency']=='KRW'].index, 'balance'] = int(krw_balance) - 10
            return df
    
    def create_order(self, currency_pair:str, side:str, volume:str=None, price:str=None, ord_type:str='limit'):
        """
        주문 생성 함수
        #GATE는 시장가 지원 안함 -> 계속 매수1호가로 매도 시도(time_in_force를 ioc로 변경)
        Parameters
        ----------
        currency_pair : str
            DESCRIPTION.
        side : str
            매수: 'buy'
            매도: 'sell'.
        volume : str, optional
            시장가 매수 주문시 불필요. The default is None.
        price : str, optional
            시장가 매도 주문시 불필요. The default is None.
        ord_type : str, optional         
            시장가: 'market'
            지정가: 'limit'. The default is 'limit'.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # 시장가(makret) 주문 시 매수->price, 매도->volume 필요 (upbit만 지원)
        # 지정가(limit) 주문 시 매수, 매도 -> price,volume 필요
        if self.exchange == 'upbit':
            currency_pair = self.c_name2upbit(currency_pair)
            
        if (self.exchange != 'upbit') and (ord_type == 'market'):
            while(1):
                ret = self.exchange_api.create_order(currency_pair=currency_pair, side=side, volume=volume, price=price, time_in_force='ioc')
                if ret == None:
                    break
                if float(ret.iloc[0]['left']) > 0:
                    volume -= float(ret.iloc[0]['left'])
                    price = self.get_orderbook(currency_pair).iloc[0]['orderbook_units'][0]['bid_price']
                
            # print(f'{self.exchange}거래소는 시장가를 지원 안합니다.')    
        else:
            return self.exchange_api.create_order(currency_pair=currency_pair, side=side, volume=volume, price=price, ord_type=ord_type)
    
    def cancel_orders(self, currency_pair:str, side:str):
        """
        주문 취소

        Parameters
        ----------
        currency_pair : str
            DESCRIPTION.
        side : str
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        
        if self.exchange == 'upbit':
            market = self.c_name2upbit(currency_pair)
            if side == 'sell':
                side = 'ask'
            elif side == 'buy':
                side = 'bid'
            ret = self.exchange_api.cancel_orders(market=market, side=side)
        elif self.exchange == 'gate':
            ret = self.exchange_api.cancel_orders(currency_pair=currency_pair, side=side)
        # if ret is None:
        #     continue
        #     # print(f'{currency_pair} 체결 대기 주문 없음')
        return ret
    
    def get_orders(self, currency_pair, status, page:int=1):  
        """
        done, wait, cancel 주문 조회

        Parameters
        ----------
        currency_pair : TYPE
            코인 이름 + 마켓.
        status : TYPE
            done: 체결 완료
            wait: 체결 대기
            cancel: 주문 취소.
        page : int, optional
            DESCRIPTION. The default is 1.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        if self.exchange == 'upbit':
            upbit_currency_pair = self.c_name2upbit(currency_pair)
            df =  self.exchange_api.get_orders(market=upbit_currency_pair, state=status, page=page)
            if self.error_handler(df) == 1:
                df = df.rename(columns={'uuid':'id'})
                return self.rename_upbit_df(df, currency_pair)
        elif self.exchange == 'gate':
            if status == 'done':
                gate_status = 'closed'
                df = self.exchange_api.list_orders(currency_pair=currency_pair, status='finished', page=page)
            elif status == 'wait':
                gate_status = 'open'
                df = self.exchange_api.list_orders(currency_pair=currency_pair, status='open', page=page)
            elif status == 'cancel':
                gate_status = 'cancelled'
                df = self.exchange_api.list_orders(currency_pair=currency_pair, status='finished', page=page)
                           
            if self.error_handler(df) == 1:
                df = df.rename(columns={'status':'state'})
                df = df[df['state'] == gate_status]
                df.loc[df[df['state'] == gate_status].index, 'state'] = status
                return df
        
    def get_orderbook(self, currency_pair:str, interval:str='0', limit:int=10):
        """
        호가 조회
        호가 매수/매도 총량, 호가
        # UPBIT는 interval, limit 지원 안함
        Parameters
        ----------
        currency_pair : str
            DESCRIPTION.
        interval : str, optional
            호가 간격. The default is '0'.
        limit : int, optional
            호가 개수. The default is 10.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # upbit -> interval, limit 지원 안함
        # gate -> interval, limit 지원 함
        if self.exchange == 'upbit':
            upbit_currency_pair = self.c_name2upbit(currency_pair)
            df = self.exchange_api.get_orderbook(currency_pair=upbit_currency_pair)    
            return self.rename_upbit_df(df, currency_pair)
        
        elif self.exchange == 'gate':
            return self.exchange_api.list_order_book(currency_pair=currency_pair, interval=interval, limit=limit)    
        
    def rename_upbit_df(self, df, currency_pair):
        """
        업비트일 경우 컬럼 이름 변경
        market -> currency_pair

        Parameters
        ----------
        df : TYPE
            DESCRIPTION.
        currency_pair : TYPE
            DESCRIPTION.

        Returns
        -------
        df : TYPE
            DESCRIPTION.

        """
        if len(df) != 0:
            df.rename(columns={'market':'currency_pair'}, inplace=True) 
            df['currency_pair'] = currency_pair
        return df
    def get_ticker(self, currency_pair):
        """
        코인 현재 정보 조회 함수

        Parameters
        ----------
        currency_pair : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        if self.exchange == 'upbit':
            upbit_currency_pair = self.c_name2upbit(currency_pair)
            df =  self.exchange_api.get_ticker(market=upbit_currency_pair)
            return self.rename_upbit_df(df, currency_pair)
        
        elif self.exchange == 'gate':
            return self.exchange_api.list_tickers(currency_pair=currency_pair)
        
    def is_withdrawl(self):
        if self.exchange == 'upbit':
            if 'error.message' in list(self.exchange_api.is_withdraws_api().keys()):
                return 0
            else:
                return 1
        elif self.exchange == 'gate':
            if self.exchange_api.is_withdraws()==1:
                return 0
            else:
                return 1
# if __name__ == '__main__':
#     api = Exchange_Api(exchange='upbit')
    # df = api.get_candle('BTC_USDT','2020-01-01 00:00:00', '2020-12-31 00:00:00', interval='1d')
    # api = Exchange_Api(exchange='upbit', access_key='xPBD01XVAMNUF5mfxOYbc6BR7xCrtb2LRTRJmrHS', secret_key='CS0cqYUmzPv4wqaaZX4rBX8hZGCz67xfzWvtHYs5')
    # api = Exchange_Api(exchange='gate', access_key='60f9f7df5fdb7a4ac64d1efba7bbda7a', secret_key='d4bb73c3aa84f6834f0fd5a056eb3d72789a730cef08492a88a33c3d492f726f')
    # df1 = api.get_candle('BTC_USDT', start_date='2020-11-01 10:00:00', interval='1w')
#     # df = api.exchange_api.avg_buy_price('XRP_USDT')
    # df = api.get_accounts()
    # df= api.get_avg_buy_price('KAI')
#     # df = api.order(currency_pair='XRP_USDT', side='sell', volume=2, price=0.46194, ord_type='limit')
    # accounts = api.get_accounts()
    # orderbook2 = api.get_orderbook('XRP_USDT')
#     # ticker = api.get_curr_price('XRP_KRW')
    # orders = api.get_orders('KAI_USDT' ,'done')
    # df = api.get_candle('XRP_USDT')