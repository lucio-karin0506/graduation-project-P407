import time
import hashlib
import hmac
import pandas as pd
import gate_api
from gate_api.exceptions import ApiException, GateApiException

class Gateio_Api:
    def __init__(self, access_key:str=None, secret_key:str=None):
        configuration = gate_api.Configuration(
            host = "https://api.gateio.ws/api/v4",
            key = access_key,
            secret = secret_key
        )    
        api_client = gate_api.ApiClient(configuration)
        # Create an instance of the API class
        self.api_instance = gate_api.SpotApi(api_client)

    def gen_sign(self, method, url, query_string=None, payload_string=None):
        key = self.access_key        # api_key
        secret = self.secret_key     # api_secret
    
        t = time.time()
        m = hashlib.sha512()
        m.update((payload_string or "").encode('utf-8'))
        hashed_payload = m.hexdigest()
        s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
        sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
        return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}
    
    def list_candlesticks(self, currency_pair:str, _from:int, to:int, limit:int=100, interval:str='30m'):
        """
        캔들 조회
        https://www.gate.io/docs/apiv4/en/index.html?python#market-candlesticks
        Parameters
        ----------
        currency_pair : str
            ex) 'BTC_USDT'.
        limit : int, optional
            조회 캔들 갯수
            Maximum:1000
            Default:100. 
        start_date : int, optional
            Format:'%Y-%m-%d'
            Default: to - 100 * interval. 
        end_date : int, optional
            Format:'%Y-%m-%d'
            Default: current time. 
        interval : int, optional
            arameter	Value
            interval	10s
            interval	1m
            interval	5m
            interval	15m
            interval	30m
            interval	1h
            interval	4h
            interval	8h
            interval	1d
            interval	7d. 

        Returns
        -------
        None.

        """
        
        # currency_pair = currency_pair # str | Currency pair
        # limit = limit # int | Maximum recent data points returned. `limit` is conflicted with `from` and `to`. If either `from` or `to` is specified, request will be rejected. (optional) (default to 100)
        # _from = _from # int | Start time of candlesticks, formatted in Unix timestamp in seconds. Default to`to - 100 * interval` if not specified (optional)
        # to = to # int | End time of candlesticks, formatted in Unix timestamp in seconds. Default to current time (optional)
        # interval = interval # str | Interval time between data points (optional) (default to '30m')
        
        try:
            # Market candlesticks
            api_response = self.api_instance.list_candlesticks(currency_pair, limit=limit, _from=_from, to=to, interval=interval)
            df = pd.DataFrame(api_response)
            df.columns = ['timestamp', 'volume', 'close', 'high',' low', 'open']
            return df
            # print(api_response)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_candlesticks: %s\n" % e)
            
    def list_currencies(self):
        """
        전체 코인 정보 조회 함수
        https://www.gate.io/docs/apiv4/en/index.html?python#list-all-currencies-39-detail
        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        
        try:
            # List all currencies' detail
            api_response = self.api_instance.list_currencies()
            return pd.DataFrame([row.to_dict() for row in api_response])
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_currencies: %s\n" % e)
            
    def get_currency(self, currency):
        """
        하나의 코인에 대한 정보 조회 함수

        Parameters
        ----------
        currency : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # currency = currency # str | Currency name
        
        try:
            # Get detail of one particular currency
            api_response = self.api_instance.get_currency(currency)
            return pd.DataFrame.from_dict([api_response.to_dict()])
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->get_currency: %s\n" % e)
            
    def list_currency_pairs(self):
        """
        전체 (코인 + 마켓)쌍의 정보 제공 함수
        https://www.gate.io/docs/apiv4/en/index.html?python#list-all-currency-pairs-supported
        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        try:
            # List all currency pairs supported
            api_response = self.api_instance.list_currency_pairs()
            return pd.DataFrame([row.to_dict() for row in api_response])
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_currency_pairs: %s\n" % e)
            
    def get_currency_pair(self, currency_pair:str):
        """
        하나의 (코인 + 마켓)쌍의 정보 제공 함수

        Parameters
        ----------
        currency_pair : str
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # currency_pair = currency_pair # str | Currency pair
        
        try:
            # Get detail of one single order
            api_response = self.api_instance.get_currency_pair(currency_pair)
            return pd.DataFrame.from_dict([api_response.to_dict()])
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->get_currency_pair: %s\n" % e)
            
    
    def list_tickers(self, currency_pair:str):
        """
        하나의 (코인 + 마켓)쌍의 현재 틱 정보 제공 함수
        https://www.gate.io/docs/apiv4/en/index.html?python#retrieve-ticker-information
        Parameters
        ----------
        currency_pair : str
            ex)BTC_USDT.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # currency_pair = currency_pair # str | Currency pair (optional)
        
        try:
            # Retrieve ticker information
            api_response = self.api_instance.list_tickers(currency_pair=currency_pair)
            return pd.DataFrame([row.to_dict() for row in api_response])
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_tickers: %s\n" % e)
    
    def list_order_book(self, currency_pair:str, interval:str='0', limit:int=10, with_id:bool=False):
        """
        하나의 (코인 + 마켓)쌍의 호가 정보 제공 함수
        
        https://www.gate.io/docs/apiv4/en/index.html?python#retrieve-order-book
        Parameters
        ----------
        currency_pair : str
            DESCRIPTION.
        interval : str
            호가 간격.
        limit : int
            호가 갯수.
        with_id : bool, optional
            . The default is False.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # currency_pair = currency_pair # str | Currency pair
        # interval = interval # str | Order depth. 0 means no aggregation is applied. default to 0 (optional) (default to '0')
        # limit = limit # int | Maximum number of order depth data in asks or bids (optional) (default to 10)
        # with_id = with_id # bool | Return order book ID (optional) (default to False)
        
        try:
            # Retrieve order book
            api_response = self.api_instance.list_order_book(currency_pair, interval=interval, limit=limit, with_id=with_id)
            return pd.DataFrame([api_response.to_dict()])
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_order_book: %s\n" % e)
    
    def list_trades(self, currency_pair:str, limit:int=100, last_id:str=None, reverse:bool=False):
        """
        하나의 (코인 + 마켓)쌍의 거래소 전체 거래 내역 조회 함수

        Parameters
        ----------
        currency_pair : str
            DESCRIPTION.
        limit : int, optional
            DESCRIPTION. The default is 100.
        last_id : str, optional
            DESCRIPTION. The default is None.
        reverse : bool, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # currency_pair = currency_pair # str | Currency pair
        # limit = limit # int | Maximum number of records returned in one list (optional) (default to 100)
        # last_id = last_id # str | Specify list staring point using the `id` of last record in previous list-query results (optional)
        # reverse = reverse # bool | Whether to retrieve records whose IDs are smaller than `last_id`'s. Default to larger ones.  When `last_id` is specified. Set `reverse` to `true` to trace back trading history; `false` to retrieve latest tradings.  No effect if `last_id` is not specified. (optional) (default to False)
        
        try:
            if last_id == None:
                # Retrieve market trades
                api_response = self.api_instance.list_trades(currency_pair, limit=limit, reverse=reverse)
            else:
                # Retrieve market trades
                api_response = self.api_instance.list_trades(currency_pair, limit=limit, last_id=last_id, reverse=reverse)
            return pd.DataFrame([row.to_dict() for row in api_response])
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_trades: %s\n" % e)
    
    
    def list_spot_accounts(self, currency:str=None):
        """
        코인 보유량 조회 함수

        Parameters
        ----------
        currency : str
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # currency = currency # str | Retrieved specified currency related data (optional)

        try:
            if currency == None:
                # List spot accounts
                api_response = self.api_instance.list_spot_accounts()
            else:
                # List spot accounts
                api_response = self.api_instance.list_spot_accounts(currency=currency)
            return pd.DataFrame([row.to_dict() for row in api_response])
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_spot_accounts: %s\n" % e)
            
    def list_all_open_orders(self, page:int=1, limit:int=100):
        """
        체결 대기중인 주문들 전체 조회

        Parameters
        ----------
        page : int, optional
            DESCRIPTION. The default is 1.
        limit : int, optional
            DESCRIPTION. The default is 100.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # page = page # int | Page number (optional) (default to 1)
        # limit = limit # int | Maximum number of records returned in one page in each currency pair (optional) (default to 100)
        
        try:
            # List all open orders
            api_response = self.api_instance.list_all_open_orders(page=page, limit=limit)
            return pd.DataFrame([row.to_dict() for row in api_response])
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_all_open_orders: %s\n" % e)
            
    def list_orders(self, currency_pair:str, status:str, page:int=1, limit:int=100):
        """
        체결 대기 혹은 체결 완료한 주문들 조회 함수
        체결 대기: status='open'
        체결 종료: status='finished'

        Parameters
        ----------
        currency_pair : str
            DESCRIPTION.
        status : str
            DESCRIPTION.
        page : int, optional
            DESCRIPTION. The default is 1.
        limit : int, optional
            DESCRIPTION. The default is 100.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # currency_pair = 'BTC_USDT' # str | Currency pair
        # status = 'open' # str | List orders based on status  `open` - order is waiting to be filled `finished` - order has been filled or cancelled 
        # page = 1 # int | Page number (optional) (default to 1)
        # limit = 100 # int | Maximum number of records returned. If `status` is `open`, maximum of `limit` is 100 (optional) (default to 100)
        
        try:
            # List orders
            api_response = self.api_instance.list_orders(currency_pair, status, page=page, limit=limit)
            return pd.DataFrame([row.to_dict() for row in api_response])
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_orders: %s\n" % e)
        
    def create_order(self, currency_pair:str, side:str, amount:str, price:str, time_in_force:str='gtc', iceberg:str=0):    
        """
        주문 생성 함수
        지정가로만 가능

        Parameters
        ----------
        currency_pair : str
            DESCRIPTION.
        side : str
            'buy' or 'sell'.
        amount : str
            DESCRIPTION.
        price : str
            DESCRIPTION.
        time_in_force : str, optional
            #######################
            gtc: GoodTillCancelled
            ioc: ImmediateOrCancelled, taker only
            poc: PendingOrCancelled, makes a post-only order that always enjoys a maker fee. 
            #######################
            The default is 'gtc'.
        iceberg : str, optional
            Amount to display for the iceberg order. Null or 0 for normal orders. Set to -1 to hide the amount totally. The default is 0.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        order = gate_api.Order(currency_pair=currency_pair, 
                               side=side,
                               amount=amount, 
                               price=price, 
                               iceberg=iceberg, 
                               time_in_force=time_in_force) # Order | 
        try:
            # Create an order
            api_response = self.api_instance.create_order(order)
            return pd.DataFrame([api_response.to_dict()])
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->create_order: %s\n" % e)
            
    def cancel_orders(self, currency_pair:str, side:str):
        """
        (코인 + 마켓)쌍의 체결 대기중인 모든 주문 취소

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
        # currency_pair = 'BTC_USDT' # str | Currency pair
        # side = 'sell' # str | All bids or asks. Both included in not specified (optional)
        # account = 'spot' # str | Specify account type. Default to all account types being included (optional)
        try:
            # Cancel all `open` orders in specified currency pair
            api_response = self.api_instance.cancel_orders(currency_pair, side=side, account='spot')
            return pd.DataFrame([row.to_dict() for row in api_response])
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->cancel_orders: %s\n" % e)
            
    def get_order(self, order_id:str, currency_pair:str):
        """
        주문 조회 함수

        Parameters
        ----------
        order_id : str
            DESCRIPTION.
        currency_pair : str
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # order_id = '12345' # str | ID returned on order successfully being created
        # currency_pair = 'BTC_USDT' # str | Currency pair
        
        try:
            # Get a single order
            api_response = self.api_instance.get_order(order_id, currency_pair)
            return pd.DataFrame([api_response.to_dict()])
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->get_order: %s\n" % e)
    
    def cancel_order(self, order_id:str, currency_pair:str):
        """
        주문 취소 함수

        Parameters
        ----------
        order_id : str
            DESCRIPTION.
        currency_pair : str
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # order_id = '12345' # str | ID returned on order successfully being created
        # currency_pair = 'BTC_USDT' # str | Currency pair
        
        try:
            # Cancel a single order
            api_response = self.api_instance.cancel_order(order_id, currency_pair)
            return pd.DataFrame([api_response.to_dict()])
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->cancel_order: %s\n" % e)
        
if __name__ == '__main__':
    user = Gateio_Api(access_key='', secret_key='')
    # df = user.list_candlesticks(currency_pair='BTC_USDT', _from=1614879000, to=1614979053)
    # coin_list = user.get_list_currencies()
    # currency = user.get_currency()
    # currency_pairs = user.list_currency_pairs()
    # currency_pair = user.get_currency_pair('ETH_BTC')
    # tickers = user.list_tickers('BTC_USDT')
    # order_book = user.list_order_book('BTC_USDT', interval='1', limit=20)
    # list_trades = user.list_trades('BTC_USDT')
    # accounts = user.list_spot_accounts('KAI')
    # open_orders = user.list_all_open_orders()
    # orders_list = user.list_orders('KAI_USDT', 'finished')
    # order = user.create_order('XRP_USDT', 'buy', 3, 1)
    # cancel_order = user.cancel_orders('BTC_USDT', 'sell')
    # get_order = user.get_order('34020104572', 'KAI_USDT')
    # from __future__ import print_function
