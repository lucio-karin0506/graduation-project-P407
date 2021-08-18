import requests
import jwt
import hashlib
import time
from urllib.parse import urlencode
import pandas as pd
import re
import logging
from datetime import timedelta
logger = logging.getLogger('ubit_api')

class Upbit_Api():
    """
        <Upbit API Reference>
        https://docs.upbit.com/reference
    """

    def __init__(self, access_key: str = None, secret_key: str = None):
        self.access_key = access_key
        self.secret_key = secret_key
        
    def error_handler(self, res):
        if res.status_code == 400:
            print('<ERROR> message:', res.json()['error']['message'], ', name:', res.json()['error']['name'])
            return 0
        elif res.status_code == 401:
            print('<ERROR> message:', res.json()['error']['message'], ', name:', res.json()['error']['name'])
            return 0
        else:
            return 1
        
    def get_trade_headers(self, query: dict) -> dict:
        """
        파라미터 암호화 함수

        Parameters
        ----------
        query : dict
            dict{parameter}

        Returns
        -------
        headers : dict
            Encrpyted parameters

        """
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.access_key,
            'nonce': int(time.time() * 1000),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}
        return headers

    def get_market_list(self, isDetails: str = 'false') -> pd.DataFrame:
        """
        업비트에서 거래 가능한 마켓의 종목 목록

        Parameters
        ----------
        isDetails : str, optional
            유의종목 필드과 같은 상세 정보 노출 여부. The default is 'false'.

        Returns
        -------
        Dataframe

        """
        url = 'https://api.upbit.com/v1/market/all'
        querystring = {'isDetails': isDetails}
        response = requests.request('GET', url, params=querystring)
        return pd.json_normalize(response.json())

    def get_candle_min(self, market: str = 'KRW-BTC', unit: str = '1', to: str = '', count: str = '200') -> pd.DataFrame:
        """
        분(Minute) 시세 캔들 조회

        Parameters
        ----------
        market : str, optional
            마켓 코드. The default is 'KRW-BTC'.
        unit : str, optional
            분 단위 (가능한 값:1,3,5,15,10,30,60,240). The default is '1'.
        to : str, optional
            마지막 캔들 시각(format: yyyy-MM-dd'T'HH:mm:ss). The default is ''.
        count : str, optional
            캔들 개수(최대 200개까지 요청 가능). The default is '200'.
        Returns
        -------
        Dataframe
            DESCRIPTION. 

        """
        url = f"https://api.upbit.com/v1/candles/minutes/{unit}"
        
        querystring = {"market": market, "to": to, "count": count}
        response = requests.request("GET", url, params=querystring)
        if self.error_handler(response) == 1:
            df = pd.json_normalize(response.json())
            df.rename(columns = {'opening_price': 'open',
                                 'high_price': 'high',
                                 'low_price': 'low',
                                 'trade_price': 'close',
                                 'candle_date_time_kst': 'Date'}, inplace = True)
            df = df.sort_values('Date').reset_index().drop('index', axis='columns')
            return df

    def get_candle_day(self, market: str = 'KRW-BTC', to: str = '', count: str = '200', convertingPriceUnit: str = 'KRW') -> pd.DataFrame:
        """
        일(Day) 시세 캔들 조회

        Parameters
        ----------
        market : str, optional
            마켓 코드. The default is 'KRW-BTC'.
        to : str, optional
            마지막 캔들 시각(format: yyyy-MM-dd'T'HH:mm:ss). The default is ''.
        count : str, optional
            캔들 개수(최대 200개까지 요청 가능). The default is '200'.
        convertingPriceUnit : str, optional
            종가 환산 화폐 단위(KRW로 명시할 시 원화 환산 가격을 반환). The default is 'KRW'.

        Returns
        -------
        Dataframe
            DESCRIPTION.

        """
        url = "https://api.upbit.com/v1/candles/days"
        querystring = {"market": market, "to": to, "count": count,
                       "convertingPriceUnit": convertingPriceUnit}
        response = requests.request("GET", url, params=querystring)
        df = pd.json_normalize(response.json())
        df.rename(columns = {'opening_price': 'open',
                              'high_price': 'high',
                              'low_price': 'low',
                              'trade_price': 'close',
                              'candle_date_time_kst': 'Date'}, inplace = True)
        df = df.sort_values('Date').reset_index().drop('index', axis='columns')
        return df

    def get_candle_week(self, market: str = 'KRW-BTC', to: str = '', count: str = '200') -> pd.DataFrame:
        """
        주(Week) 시세 캔들 조회

        Parameters
        ----------
        market : str, optional
            마켓 코드. The default is 'KRW-BTC'.
        to : str, optional
            마지막 캔들 시각(format: yyyy-MM-dd'T'HH:mm:ss). The default is ''.
        count : str, optional
            캔들 개수(최대 200개까지 요청 가능). The default is '200'.

        Returns
        -------
        Dataframe
            DESCRIPTION.

        """
        url = "https://api.upbit.com/v1/candles/weeks"
        querystring = {"market": market, "to": to, "count": count}
        response = requests.request("GET", url, params=querystring)
        df = pd.json_normalize(response.json())
        df.rename(columns = {'opening_price': 'open',
                             'high_price': 'high',
                             'low_price': 'low',
                             'trade_price': 'close',
                             'candle_date_time_kst': 'Date'}, inplace = True)
        df = df.sort_values('Date').reset_index().drop('index', axis='columns')
        return df

    def get_candle_month(self, market: str = 'KRW-BTC', to: str = '', count: str = '200') -> pd.DataFrame:
        """
        월(Month) 시세 캔들 조회

        Parameters
        ----------
        market : str, optional
            마켓 코드. The default is 'KRW-BTC'.
        to : str, optional
            마지막 캔들 시각(format: yyyy-MM-dd'T'HH:mm:ss). The default is ''.
        count : str, optional
            캔들 개수(최대 200개까지 요청 가능). The default is '200'.

        Returns
        -------
        Dataframe
            DESCRIPTION.

        """
        url = "https://api.upbit.com/v1/candles/months"
        querystring = {"market": market, "to": to, "count": count}
        response = requests.request("GET", url, params=querystring)
        df = pd.json_normalize(response.json())
        df.rename(columns = {'opening_price': 'open',
                             'high_price': 'high',
                             'low_price': 'low',
                             'trade_price': 'close',
                             'candle_date_time_kst': 'Date'}, inplace = True)
        df = df.sort_values('Date').reset_index().drop('index', axis='columns')
        return df
    
    
    def get_candle(self, currency_pair:str, start_date:str='', end_date:str='', limit:int=100, interval:str='30m'):
        market = currency_pair
        if len(interval) > 1:
            unit = interval[:-1]
            interval = interval[-1]
            
        if limit > 200:
            limit = 200
        
        # end_date 미만이 아니고 end_date 이상으로 하기 위해
        if end_date != '' and end_date.second == 0:
            end_date = end_date + timedelta(seconds=1)
            
        if interval == 'm':         
            df = self.get_candle_min(market=market, unit=unit, to=end_date, count=limit)
        elif interval == 'd':
            df = self.get_candle_day(market=market, to=end_date, count=limit)
        elif interval == 'w':
            df = self.get_candle_week(market=market, to=end_date, count=limit)
        elif interval == 'M':
            df = self.get_candle_month(market=market, to=end_date, count=limit)
        return df
        
    def get_ticks(self, market: str = 'KRW-BTC', to: str = '', count: str = '200', daysAgo: int = None) -> pd.DataFrame:
        """
        최근 체결 내역 조회

        Parameters
        ----------
        market : str, optional
            마켓 코드. The default is 'KRW-BTC'.
        to : str, optional
            마지막 체결 시각. 형식 : [HHmmss 또는 HH:mm:ss]. 비워서 요청시 가장 최근 데이터. The default is ''.
        count : str, optional
            체결 개수. The default is '200'.
        daysAgo : int, optional
            최근 체결 날짜 기준 7일 이내의 이전 데이터 조회 가능. 비워서 요청 시 가장 최근 체결 날짜 반환. (범위: 1 ~ 7)). The default is None.

        Returns
        -------
        Dataframe
            DESCRIPTION.

        """
        url = "https://api.upbit.com/v1/trades/ticks"
        querystring = {"market": market, "to": to,
                       "count": count, "daysAgo": daysAgo}
        response = requests.request("GET", url, params=querystring)
        return pd.json_normalize(response.json())
    
    def get_ticker(self, market: str = 'KRW-BTC') -> pd.DataFrame:
        """
        현재가 정보 조회

        Parameters
        ----------
        markets : str, optional
            마켓 코드. The default is 'KRW-BTC'.

        Returns
        -------
        Dataframe
            DESCRIPTION.

        """
        url = "https://api.upbit.com/v1/ticker"
        querystring = {"markets": market}
        response = requests.request("GET", url, params=querystring)
        return pd.json_normalize(response.json())

    def get_orderbook(self, currency_pair: list or str = 'KRW-BTC') -> pd.DataFrame:
        """
        호가 정보 조회

        Parameters
        ----------
        markets : list or str, optional
            마켓 코드 목록. The default is 'KRW-BTC'.

        Returns
        -------
        Dataframe
            DESCRIPTION.

        """
        url = "https://api.upbit.com/v1/orderbook"
        querystring = {"markets": currency_pair}
        response = requests.request("GET", url, params=querystring)
        return pd.json_normalize(response.json())

    def get_accounts(self) -> pd.DataFrame:
        """
        전체 계좌 조회

        Returns
        -------
        Dataframe
            DESCRIPTION.

        """
        access_key = self.access_key
        secret_key = self.secret_key
        server_url = 'https://api.upbit.com/v1/accounts'

        payload = {
            'access_key': access_key,
            'nonce': int(time.time() * 1000),
        }
        jwt_token = jwt.encode(payload, secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.get(server_url, headers=headers)
        return pd.json_normalize(res.json())

    def get_chance(self, market: str = 'KRW-BTC') -> pd.DataFrame:
        """
        주문 가능 정보 확인

        Parameters
        ----------
        market : str, optional
            Market ID. The default is 'KRW-BTC'.

        Returns
        -------
        Dataframe
            DESCRIPTION.

        """
        server_url = 'https://api.upbit.com/v1/orders/chance'
        query = {
            'market': market,
        }
        headers = self.get_trade_headers(query)
        res = requests.get(server_url, params=query, headers=headers)
        return pd.json_normalize(res.json())

    def get_order(self, uuid: str) -> pd.DataFrame:
        """
        개별 주문 조회

        Parameters
        ----------
        uuid : str
            주문 UUID.

        Returns
        -------
        Datafrmae
            DESCRIPTION.

        """
        server_url = 'https://api.upbit.com/v1/order'
        query = {
            'uuid': uuid,
        }
        headers = self.get_trade_headers(query)
        res = requests.get(server_url, params=query, headers=headers)
        return pd.json_normalize(res.json())
    
    def get_orders(self, market: str = 'KRW-BTC', state: str = 'done',  page: int = 1, order_by: str = 'desc') -> pd.DataFrame:
        """
        주문 리스트 조회

        Parameters
        ----------
        market : str, optional
            Market ID. The default is 'KRW-BTC'.
        state : str, optional
            주문 상태. The default is 'done'.
        page : int, optional
            요청 페이지. The default is 1.
        order_by : str, optional
            정렬(asc or desc). The default is 'desc'.

        Returns
        -------
        Dataframe
            DESCRIPTION.

        """

        server_url = 'https://api.upbit.com/v1/orders'
        query = {
            'market': market,
            'page': page,
            'order_by': order_by,
            'state': state,
        }
        headers = self.get_trade_headers(query)
        res = requests.get(server_url, params=query, headers=headers)
        # 에러처리
        if self.error_handler(res) == 1:
            df = pd.json_normalize(res.json())
            if len(df) != 0:
                df['create_time_utc'] = [last_time[:10] + ' ' + last_time[11:19] for last_time in list(df['created_at'])]
            return df
    
    
    def is_withdraws_api(self, currency:str = 'KRW-BTC') -> pd.DataFrame:
        server_url = 'https://api.upbit.com/v1/withdraws/chance'
        query = {
            'currency': currency
            }
        headers = self.get_trade_headers(query)
        res = requests.get(server_url, params=query, headers=headers)
        return pd.json_normalize(res.json())

    def cancel_orders(self, market:str, side):
        """
        코인을 기준으로 체결 대기중인 주문 취소

        Parameters
        ----------
        currency_pair : str
            DESCRIPTION.
        side : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        orders = self.get_orders(market=market, state='wait')
        if len(orders) != 0:            
            wait_uuids = list(self.get_orders(market=market, state='wait')['uuid'], side=side)
            if len(wait_uuids) != 0:
                for uuid in wait_uuids:
                    return self.cancel_order_uuid(uuid)
    
    def cancel_order_uuid(self, uuid: str) -> pd.DataFrame:
        """
        주문 취소 접수

        Parameters
        ----------
        uuid : str
            주문 UUID.

        Returns
        -------
        Dataframe
            DESCRIPTION.

        """
        server_url = 'https://api.upbit.com/v1/order'
        query = {
            'uuid': uuid,
        }
        headers = self.get_trade_headers(query)
        res = requests.delete(server_url, params=query, headers=headers)
        return pd.json_normalize(res.json())

    def create_order(self, currency_pair: str, side: str, volume: str=None, price: str=None, ord_type: str='limit') -> pd.DataFrame:
        """
        주문하기

        Parameters
        ----------
        market : str
            Market ID.
        side : str
            주문 종류(bid:매수, ask:매도).
        volume : str
            주문량.
        price : str
            주문가격.
        ord_type : str
            주문 타입(limit:지정가, price:시장가 매수, market:시장가 매도).

        Returns
        -------
        Datafrmae
            DESCRIPTION.

        """
        
        if side == 'sell':
            side = 'ask'
        elif side == 'buy':
            side = 'bid'
        if ord_type == 'market':
            if side == 'ask':
                ret = self.sell_market_order(market=currency_pair, volume=volume)
            elif side == 'bid':
                ret = self.buy_market_order(market=currency_pair, price=price)
        elif ord_type == 'limit':
            if side == 'ask':
                ret = self.sell_limit_order(market=currency_pair, volume=volume, price=price)
            elif side == 'bid':
                ret = self.buy_limit_order(market=currency_pair, volume=volume, price=price)
       
        return ret
        # server_url = 'https://api.upbit.com/v1/orders'
        # query = {
        #     'market': currency_pair,
        #     'side': side,
        #     'volume': volume,
        #     'price': price,
        #     'ord_type': ord_type,
        # }
        # headers = self.get_trade_headers(query)
        # res = requests.post(server_url, params=query, headers=headers)
        # return pd.json_normalize(res.json())
    
    def buy_market_order(self, market, price):
        server_url = 'https://api.upbit.com/v1/orders'
        query = {
            'market': market,
            'side': 'bid',
            'price': price,
            'ord_type': 'price',
        }
        headers = self.get_trade_headers(query)
        res = requests.post(server_url, params=query, headers=headers)
        return pd.json_normalize(res.json())
    
    def sell_market_order(self, market, volume):
        server_url = 'https://api.upbit.com/v1/orders'
        query = {
            'market': market,
            'side': 'ask',
            'volume': volume,
            'ord_type': 'market',
        }
        headers = self.get_trade_headers(query)
        res = requests.post(server_url, params=query, headers=headers)
        return pd.json_normalize(res.json())
    
    def buy_limit_order(self, market, volume, price):
        server_url = 'https://api.upbit.com/v1/orders'
        query = {
            'market': market,
            'side': 'bid',
            'volume': volume,
            'price': price,
            'ord_type': 'limit',
        }
        headers = self.get_trade_headers(query)
        res = requests.post(server_url, params=query, headers=headers)
        return pd.json_normalize(res.json())
    
    def sell_limit_order(self, market, volume, price):
        server_url = 'https://api.upbit.com/v1/orders'
        query = {
            'market': market,
            'side': 'ask',
            'volume': volume,
            'price': price,
            'ord_type': 'limit',
        }
        headers = self.get_trade_headers(query)
        res = requests.post(server_url, params=query, headers=headers)
        return pd.json_normalize(res.json())
