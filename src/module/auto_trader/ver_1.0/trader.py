import os
import sys
import re
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))

from module.auto_trader import upbit_api, util

logger = util.CreateLogger('trader')


class Trader():
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.upbit = upbit_api.Upbit_Api(
            access_key=access_key, secret_key=secret_key)

    def get_balance(self, market):
        accounts = self.upbit.get_accounts()
        if market not in list(accounts['currency']):
            return 0
        balance = accounts[accounts['currency'] == market].iloc[0]['balance']
        return float(balance)

    def get_total_buy_price(self, market):
        
        ticker = re.findall('-(.*)', market)[0]
        balance = self.get_balance(ticker)
        if balance == 0:
            return 0
        accounts = self.upbit.get_accounts()
        currency = accounts[accounts['currency'] == ticker].iloc[0]
        avg_buy_price = float(currency['avg_buy_price'])
        total_buy_price = balance * avg_buy_price
        return total_buy_price

    def get_total_curr_price(self, market):
        ticker = re.findall('-(.*)', market)[0]
        balance = self.get_balance(ticker)
        if balance == 0:
            return 0
        curr_price = self.upbit.get_ticker(market).iloc[0]['trade_price']
        total_curr_price = balance * curr_price
        return total_curr_price

    def gap_price_rate(self, market):
        total_curr_price = self.get_total_curr_price(market)
        total_buy_price = self.get_total_buy_price(market)

        if total_curr_price == 0:
            return 0
        else:
            return 1 - (total_curr_price / total_buy_price)
        
    def get_last_order_time(self, side, state, item):
        orders = self.upbit.get_orders(item.code)
        con1 = orders['state'] == state
        if side == 'sell':
            side = 'ask'
        elif side == 'buy':
            side = 'bid'
            
        con2 = orders['side'] == side
        
        last_order_time = orders[con1 & con2].iloc[0]['created_at'][:19]
        last_order_time = datetime.strptime(last_order_time, '%Y-%m-%dT%H:%M:%S')
        
        return last_order_time
        
    def get_order_state(self, uuid):
        try:
            state = self.upbit.get_order(uuid=uuid).iloc[0]['state']
            if state == 'done':
                logger.info(f'<주문 상태> uuid: {uuid} 체결 완료')
                return 'done'
            elif state == 'cancel':
                logger.info(f'<주문 상태> uuid: {uuid} 주문 취소')
                return 'cancel'
            else:
                logger.info(f'<주문 상태> uuid: {uuid} 체결 대기')
                return 'wait'
        except:
            return 'error'

    def order_cancel(self, uuid):
        return self.upbit.order_cancel(uuid)

    def buy(self, market, volume_rate, betting_rate, betting_price, ord_type, ord_price=0):
        '''
        order_price
        - 1: 매도1호가
        - -1: 매수1호가
        - 0: 현재가
        '''

        # 풀매수
        if volume_rate == 'all' or volume_rate == 1:
            volume_rate = 0.999
        # 거래량
        balance = self.get_balance(market='KRW')
        if balance == 0:
            logger.info("<매수 요청 실패> 보유 현금이 없습니다>")
            return 0

        # 코인별 배팅 금액 처리
        if betting_price < (balance * betting_rate):
            total_price = betting_price * volume_rate
        else:
            total_price = balance * betting_rate * volume_rate

        # 시장가
        if ord_type == 'market':
            # 매수
            logger.info(f"<매수 요청> code:{market}, total_price:{total_price}")
            ret = self.upbit.buy_market_order(market=market, price=total_price)
        # 지정가
        elif ord_type == 'limit':
            # 호가 정보
            order_book = self.upbit.get_orderbook(
                markets=market)['orderbook_units'][0]
            # 매수1호가
            if ord_price == 1:
                bid_price = order_book[0]['ask_price']
            # 매도1호가
            elif ord_price == -1:
                bid_price = order_book[0]['bid_price']
            # 현재가
            elif ord_price == 0:
                bid_price = self.upbit.get_ticks(market=market)[
                    'trade_price'].iloc[0]
            # 거래량
            if total_price == 0:
                volume = 0
            else:
                volume = total_price / bid_price
            # 소수점 8자리 까지
            volume = float('{:.9f}'.format(volume)[:-1])
            logger.info(
                f"<매수 요청> code:{market}, volume:{volume}, one_price:{bid_price}")
            # 매수
            ret = self.upbit.buy_limit_order(
                market=market, volume=volume, price=bid_price)
        return ret

    def sell(self, market, volume_rate, ord_type, ord_price=0):
        # 풀매수
        if volume_rate == 'all':
            volume_rate = 1
        # 가상화폐 코드명
        ticker = re.findall('-(.*)', market)[0]
        # 거래량
        balance = self.get_balance(market=ticker)
        if balance == 0:
            logger.info(f" <매도 요청 실패> {market} 보유량이 없습니다.")
            return 0
        volume = balance * volume_rate
        # 시장가
        if ord_type == 'market':
            logger.info(f"<매도 요청> code:{market}, total_volume:{volume}")
            ret = self.upbit.sell_market_order(market=market, volume=volume)
        # 지정가
        elif ord_type == 'limit':
            order_book = self.upbit.get_orderbook(
                markets=market)['orderbook_units'][0]
            if ord_price == 1:
                ask_price = order_book[0]['ask_price']
            elif ord_price == -1:
                ask_price = order_book[0]['bid_price']
            elif ord_price == 0:
                ask_price = self.upbit.get_ticks(market=market)[
                    'trade_price'].iloc[0]
            logger.info(
                f"<매도 요청> code:{market}, volume:{volume}, one_price:{ask_price}")
            ret = self.upbit.sell_limit_order(
                market=market, volume=volume, price=ask_price)
        return ret
