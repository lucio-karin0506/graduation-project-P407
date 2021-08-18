import time
import hashlib
import hmac
import pandas as pd
import gate_api
from gate_api.exceptions import ApiException, GateApiException
from datetime import datetime, timedelta, timezone
class Gate_Api:
    def __init__(self, access_key:str=None, secret_key:str=None):
        self.configuration = gate_api.Configuration(
            host = "https://api.gateio.ws/api/v4",
            key = access_key,
            secret = secret_key
        )    
        self.api_client = gate_api.ApiClient(self.configuration)
        # Create an instance of the API class
        self.api_instance = gate_api.SpotApi(self.api_client)

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
    
    def get_candle(self, currency_pair:str, start_date:str='', end_date:str='', limit:int=100, interval:str='30m'):
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
        
        # utc -> timestamp
        if start_date != '':
            start_date = int(start_date.replace(tzinfo=timezone.utc).timestamp())
        if end_date != '':
            end_date = int(end_date.replace(tzinfo=timezone.utc).timestamp())
        
        try:
            # Market candlesticks
            
            api_response = self.api_instance.list_candlesticks(currency_pair, limit=limit, _from=start_date, to=end_date, interval=interval)
            if len(api_response) == 0:
                return pd.DataFrame(api_response)
            else:
                df = pd.DataFrame(api_response)
                df.columns = ['timestamp', 'volume', 'close', 'high','low', 'open']
                df['candle_date_time_utc'] = [datetime.utcfromtimestamp(int(timestamp)) for timestamp in df['timestamp']]
                df['candle_date_time_kst'] = [utc + timedelta(hours=9) for utc in df['candle_date_time_utc']]
                return df
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
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_currencies: %s\n" % e)
            
        return pd.DataFrame([row.to_dict() for row in api_response])    
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
            df = pd.DataFrame([row.to_dict() for row in api_response])
            df.rename({'last':'trade_price'}, axis='columns', inplace=True)
            return df
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
            api_response = self.api_instance.list_order_book(currency_pair=currency_pair, interval=interval, limit=limit, with_id=with_id)
            df = api_response.to_dict()
            asks_price = [float(ask[0]) for ask in df['asks']]
            bids_price = [float(bid[0]) for bid in df['bids']]
            asks_size = [float(ask[1]) for ask in df['asks']]
            bids_size = [float(bid[1]) for bid in df['bids']]
            orderbook = pd.DataFrame([{'currency_pair':currency_pair, 'total_ask_size':sum(asks_size), 'total_bids_size':sum(bids_size)}])
            orderbook['orderbook_units'] = \
                [[{'ask_price':units[0], 'bid_price':units[1], 'ask_size':units[2], 'bid_size':units[3] } for units in list(zip(asks_price,bids_price,asks_size,bids_size))]]
            return orderbook
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
            
            df = pd.DataFrame([row.to_dict() for row in api_response])
            df['avg_buy_price'] = [self.avg_buy_price(currency_pair=currency+'_USDT')\
                                   if currency not in['USDTEST', 'USDT', 'GT'] else 0 for currency in df['currency']]
            df = df.rename(columns={'available':'balance'})
            return df
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
            
    def avg_buy_price(self, currency_pair:str):
        """
        매수 평균가 계산 함수

        Parameters
        ----------
        currency_pair : str
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        try:
            orders  = self.list_orders(currency_pair=currency_pair, status='finished')
            orders = orders[orders['status']=='closed'][::-1]
                        
            numerator = 0
            denominator = 0
            check_balance = 0
            for index, order in orders.iterrows():
                amount = float(order['amount'])
                left = float(order['left'])
                price = float(order['price'])
                side = order['side']
                if side == 'buy':
                    numerator += (amount - left) * price
                    denominator += amount - left      
                    check_balance += numerator
                elif side == 'sell':
                    check_balance -= (amount - left) * price
                    
                if check_balance <= 1:
                    numerator = 0
                    denominator = 0
                    check_balance = 0
                    
            if numerator <= 1:
                return 0
            else:
                return numerator / denominator
            
        except Exception as e:
            print(f'<ERROR> {e}')
        
        
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
            df = pd.DataFrame([row.to_dict() for row in api_response])
            if len(df) != 0:
                df['create_time_utc'] = [datetime.strftime(datetime.utcfromtimestamp(int(last_time)),"%Y-%m-%d %H:%M:%S") for last_time in list(df['create_time'])]
            return df
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling SpotApi->list_orders: %s\n" % e)
        
    def create_order(self, currency_pair:str, side:str, volume:str, price:str, ord_type:str='limit', time_in_force:str='gtc', iceberg:str=0):    
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
                               amount=volume, 
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
            
    def is_withdraws(self):
        api_client = gate_api.ApiClient(self.configuration)
        # Create an instance of the API class
        api_instance = gate_api.WithdrawalApi(api_client)
        ledger_record = gate_api.LedgerRecord(currency='BTC_USDT', amount=0) # LedgerRecord | 
        
        try:
            # Withdraw
            api_response = api_instance.withdraw(ledger_record)
            return 1
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
            return 0
        except ApiException as e:
            print("Exception when calling WithdrawalApi->withdraw: %s\n" % e)
            return 0
if __name__ == '__main__':
    user = Gate_Api(access_key='60f9f7df5fdb7a4ac64d1efba7bbda7a', secret_key='d4bb73c3aa84f6834f0fd5a056eb3d72789a730cef08492a88a33c3d492f726f')
    withdrawl = user.withdrawl()
#     df = user.get_candle(currency_pair='BTC_USDT', to='2020-01-01 00:00:00')
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
