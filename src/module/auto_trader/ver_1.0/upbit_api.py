import requests
import jwt
import hashlib
import time
from urllib.parse import urlencode
import pandas as pd

import logging
logger = logging.getLogger('ubit_api')

class Upbit_Api():
    """
        <Upbit API Reference>
        https://docs.upbit.com/reference
    """

    def __init__(self, access_key: str = None, secret_key: str = None):
        self.access_key = access_key
        self.secret_key = secret_key

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
        if to != '':
            to + '+09:00'
        querystring = {"market": market, "to": to, "count": count}
        response = requests.request("GET", url, params=querystring)
        df = pd.json_normalize(response.json())
        df.rename(columns = {'opening_price': 'open',
                             'high_price': 'high',
                             'low_price': 'low',
                             'trade_price': 'close',
                             'candle_date_time_kst': 'Date'}, inplace = True)
        return df.sort_values('Date')

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
        return df.sort_values('Date')

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
        return df.sort_values('Date')

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
        return df.sort_values('Date')

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

    def get_ticker(self, markets: str = 'KRW-BTC') -> pd.DataFrame:
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
        querystring = {"markets": markets}
        response = requests.request("GET", url, params=querystring)
        return pd.json_normalize(response.json())

    def get_orderbook(self, markets: list or str = 'KRW-BTC') -> pd.DataFrame:
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
        querystring = {"markets": markets}
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
        return pd.json_normalize(res.json())


    def is_withdraws_api(self, currency:str = 'KRW-BTC') -> pd.DataFrame:
        server_url = 'https://api.upbit.com/v1/withdraws/chance'
        query = {
            'currency': currency
            }
        headers = self.get_trade_headers(query)
        res = requests.get(server_url, params=query, headers=headers)
        return pd.json_normalize(res.json())

    
    def order_cancel(self, uuid: str) -> pd.DataFrame:
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

    def order(self, market: str, side: str, volume: str, price: str, ord_type: str) -> pd.DataFrame:
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
        server_url = 'https://api.upbit.com/v1/orders'
        query = {
            'market': market,
            'side': side,
            'volume': volume,
            'price': price,
            'ord_type': ord_type,
        }
        headers = self.get_trade_headers(query)
        res = requests.post(server_url, params=query, headers=headers)
        return pd.json_normalize(res.json())
    
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
