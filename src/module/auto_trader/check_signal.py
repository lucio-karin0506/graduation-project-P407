import os
import sys
import re
import pandas as pd
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))

from module.auto_trader import util
from module.labeler.labeler import *
from module.indicator.indicator import *

logger = util.CreateLogger('Item')
# class Strategy_monitor():
class Item():
    def __init__(self,
                  currency_pair:str,            # coin + makret
                  interval:str,                 # interval
                  buying_portion:float,         # 현재 계좌 가치에 따른 코인 별 최대 매수 금액 비율
                  buying_money:float,           # 코인 별 최대 매수 금액
                  max_buy_count:int,            # 동일 매수 조건 최대 진입 허용 횟수
                  max_sell_count:int,           # 동일 매도 조건 최대 진입 허용 횟수
                  buy_pyramiding_rate:float,    # 동일 매수 조건의 매수량 누적 피라미딩
                  sell_pyramiding_rate:float,   # 동일 매도 조건의 매도량 누적 피라미딩
                  strategy_name:list,           # 적용 전략파일 이름 리스트
                  buy_price_type:int,           # 매수 가격 종류 (매수1호가, 매도1호가, 현재가)
                  sell_price_type:int,          # 매도 가격 종류 (매수1호가, 매도1호가 ,현재가)
                  trader,                       # Trader 클래스의 객체
                  state_db,                     # State_db 클래스의 객체
                  slack_list=None):             # Slakc 클래스의 객체가 들어있는 리스트
        self.trader = trader
        self.slack_list = slack_list    
        self.buy_price_type = buy_price_type
        self.sell_price_type = sell_price_type
        self.state_db = state_db
        self.currency = re.findall("(.*?)_(.*)", currency_pair)[0][0]
        self.market = re.findall("(.*?)_(.*)", currency_pair)[0][1]
        self.currency_pair = currency_pair
        if len(interval) == 1:
            interval = '1'+interval
        self.interval = interval
        self.buying_portion = buying_portion
        self.buying_money = buying_money
        self.max_buy_count = max_buy_count
        self.max_sell_count = max_sell_count
        self.buy_pyramiding_rate = buy_pyramiding_rate
        self.sell_pyramiding_rate = sell_pyramiding_rate
        self.strategy_name = strategy_name
        
        self.order_count = {'buy':{}, 'sell':{}}
        self.last_order_time = {'buy':{}, 'sell':{}}
        self.interval_flag = {'buy': False, 'sell': False}
        self.order_list = {'buy':{}, 'sell':{}}
        self.wait_orders = []
        self.df = pd.DataFrame()
        
    def set_df(self, api):
        """
        멤버 변수 df에 현재 시간 기준 최신의 코인 가격 데이터를 데이터프레임 형식으로 설정함

        Parameters
        ----------
        api : TYPE
            Trader 클래스의 객체.

        Returns
        -------
        None.

        """
        self.df = api.api.get_candle(currency_pair=self.currency_pair,
                           interval=self.interval,
                           limit=200)
    
    def set_indi(self, strategy_dict: dict):    
        """
        멤버 변수 df에 기술적 지표 값 및 레이블링 값 컬럼 추가

        Parameters
        ----------
        strategy_dict : dict
            DESCRIPTION.

        Returns
        -------
        None.

        """
        for strategy_name in self.strategy_name:
            for indi in strategy_dict[strategy_name].ref_indi:
                eval(indi)
                
    def get_signal_name(self, strategy_dict):
        """
        객체에 적용되는 전략들의 조건들 이름을 받아
        order_count, last_order_time, order_list 멤버 변수에 조건 이름을 이용하여 초기화 함.

        Parameters
        ----------
        strategy_dict : TYPE
            {전략파일이름:Strategy객체}.

        Returns
        -------
        None.

        """
        for strategy_name in self.strategy_name:       
            for side in ['buy', 'sell']:
                self.order_count[side][strategy_name] = {}
                self.last_order_time[side][strategy_name] = {}
                self.order_list[side][strategy_name] = {}
                for signal_name in strategy_dict[strategy_name].signal_name[side]:
                    self.order_count[side][strategy_name][signal_name] = 0
                    self.last_order_time[side][strategy_name][signal_name] = 0
                    self.order_list[side][strategy_name][signal_name] = 0

                    
    def set_stop_order(self, gap_rate_buy2curr):
        """
        멤버변수 df에 매수 평균가와 현재가의 차이에 대한 비율을 
        stop_loss, stop_profit 컬럼에 추가함
        
        Parameters
        ----------
        gap_rate_buy2curr : TYPE
            현재가  / 매수평균가.

        Returns
        -------
        None.

        """
        if gap_rate_buy2curr != 0:
            stop_loss = 1 - gap_rate_buy2curr
            stop_profit = gap_rate_buy2curr - 1
        elif gap_rate_buy2curr == 0:
            stop_loss = 0
            stop_profit = 0
            
        self.df['stop_loss'] = stop_loss
        self.df['stop_profit'] = stop_profit
        
    def check_signal(self, strategy_dict):
        """
        멤버 변수 df의 시간 기준 가장 최신 행을 기준으로 자동 거래를 수행

        Parameters
        ----------
        strategy_dict : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        def cross_up(df, source, target):
            """
            df의 가장 최근 데이터 기준으로 상향돌파 유무 확인
        
            Parameters
            ----------
            df : Dataframe
                DESCRIPTION.
            source : str
                DESCRIPTION.
            target : str or int or float
                DESCRIPTION.
        
            Returns
            -------
            TYPE
                DESCRIPTION.
        
            """
            if isinstance(target, int) or isinstance(target, float):
                prev_target = target
                curr_target = target
            else:
                prev_target = df[target].iloc[-2]
                curr_target = df[target].iloc[-1]
            curr_source = df[source].iloc[-1]
            prev_source = df[source].iloc[-2]
        
            return 1 if ((prev_source <= prev_target) & (curr_source > curr_target)) else 0

        def cross_down(df, source, target):
            """
            df의 가장 최근 데이터 기준으로 하향돌파 유무 확인
        
            Parameters
            ----------
            df : Dataframe
                DESCRIPTION.
            source : str
                DESCRIPTION.
            target : str or int or float
                DESCRIPTION.
        
            Returns
            -------
            TYPE
                DESCRIPTION.
        
            """
            if isinstance(target, int) or isinstance(target, float):
                prev_target = target
                curr_target = target
            else:
                prev_target = df[target].iloc[-2]
                curr_target = df[target].iloc[-1]
            curr_source = df[source].iloc[-1]
            prev_source = df[source].iloc[-2]
        
            return 1 if ((prev_source >= prev_target) & (curr_source < curr_target)) else 0
        df_all = self.df.copy()
        df = self.df.iloc[-1].copy()
        #######################################
        # df[signal_name] 컬럼 추가 ##############################
        #######################################
        for strategy_name in self.strategy_name:
            for side in ['buy', 'sell']:
                for signal_name, count in list(self.order_count[side][strategy_name].items()):
                    df[f'{strategy_name}.{signal_name}'] = count
            exec(strategy_dict[strategy_name].ref_strategy)
            
    def buy(self, strategy_name, signal_name, stock):
        """
        매수 조건 발생 시 max_buy_count와 buy_pyramiding 적용 후 거래 함수 호출

        Parameters
        ----------
        strategy_name : TYPE
            전략파일 이름.
        signal_name : TYPE
            조건 이름.
        stock : TYPE
            최대 매수 금액 대비 매수비율.

        Returns
        -------
        None.

        """
        logger.info(f'<매수 조건 만족> coin:{self.currency_pair}, strategy_name:{strategy_name}, signal_name:{signal_name}, stock:{stock}')
        if (self.order_count['buy'][strategy_name][signal_name] + 1)<= self.max_buy_count:
            stock = stock * (self.buy_pyramiding_rate ** self.order_count['buy'][strategy_name][signal_name])
            self.order('buy', stock, strategy_name, signal_name)
        else:
            logger.info('<조건 불만족> count 조건 불만족')

        
    def sell(self, strategy_name, signal_name, stock):
        """
        매도 조건 발생 시 max_sell_count와 sell_pyramiding 적용 후 거래 함수 호출

        Parameters
        ----------
        strategy_name : TYPE
            전략파일 이름.
        signal_name : TYPE
            조건 이름.
        stock : TYPE
            보유량 대비 매도비율.

        Returns
        -------
        None.

        """
        logger.info(f'<매도 조건 만족> coin:{self.currency_pair}, strategy_name:{strategy_name}, signal_name:{signal_name}, stock:{stock}')
        if (self.order_count['sell'][strategy_name][signal_name] + 1)<= self.max_buy_count:
            stock = stock * (self.sell_pyramiding_rate ** self.order_count['sell'][strategy_name][signal_name])
            self.order('sell', stock, strategy_name, signal_name)
        else:
            logger.info('<조건 불만족> count 조건 불만족')
            
    def push_slack(self, message:str):
        """
        슬랙 봇 메시지 푸시 기능 함수

        Parameters
        ----------
        message : str
            보낼 메시지.

        Returns
        -------
        None.

        """
        if self.slack_list is not None:
            for slack in self.slack_list:
                slack.push_message(message)
            
    def order(self, side:str, stock:str, strategy_name:str, signal_name:str):
        """
        주문 함수
        매매 금액 설정, interval 조건 여부 확인, 주문 정상적 요청 시 처리

        Parameters
        ----------
        side : TYPE
            'buy' or 'sell'.
        stock : TYPE
            side=='buy' -> 최대 매수 금액 대비 매수비율.
            side=='sell' -> 보유량 대비 매도비율.
        strategy_name : TYPE
            전략 파일 이름.
        signal_name : TYPE
            조건 이름.

        Returns
        -------
        max_holding_value : TYPE
            DESCRIPTION.

        """
        def set_max_holding_value(item):
            """
            현재 기준으로 코인 최대 매수 금액 설정

            Parameters
            ----------
            item : TYPE
                Item 객체.

            Returns
            -------
            max_holding_value : TYPE
                최대 매수 금액.

            """
            if item.buying_portion == 0 and item.buying_money != 0:
                max_holding_value = item.buying_money
            elif item.buying_portion != 0 and item.buying_money == 0:
                max_holding_value = item.trader.get_rate2volume(item.buying_portion)
            elif item.buying_portion == 0 and item.buying_money == 0:
                max_holding_value = 0
            elif item.buying_portion != 0 and item.buying_money != 0:
                max_holding_value = min(item.trader.get_rate2volume(item.buying_portion), item.buying_money)
                
            return max_holding_value
                    
        ordbook_type = {'buy':self.buy_price_type,'sell':self.sell_price_type}  # 매수:매수1호가, 매도:매도1호가
        
        if self.check_interval_order(side) == 1:
            if side =='buy':
                opposite_side = 'sell'
                self.trader.cancel_orders(self.currency_pair, opposite_side)                                             # 반대 포지션 체결 대기 주문 취소
                max_holding_value = set_max_holding_value(self)                                                          # 최대 코인 보유 가치 설정
                max_curr_buying_value =  max_holding_value - self.trader.get_evaluation_amount(self.currency_pair)       # 현재 최대 매수 금액 설정
                total_value = util.floor((max_curr_buying_value * stock), 8)                                             # 총 매매 금액
                balance = self.trader.get_volume(self.market)                                                            # 현금 보유량
                if total_value > balance:                                                                                # 총 매수 금액은 현금 보유량 이하
                    total_value = balance
            
            if side == 'sell':          
                opposite_side = 'buy'
                self.trader.cancel_orders(self.currency_pair, opposite_side)                                             # 반대 포지션 체결 대기 주문 취소
                amount = self.trader.get_volume(self.currency)
                total_value = amount * stock
            logger.info(f'<주문 시도> coin:{self.currency_pair}, side:{side}, total_value:{total_value}, strategy_name:{strategy_name}, signal_name:{signal_name}, count:{self.order_count[side][strategy_name][signal_name]}')
            
            order_ret = self.trader.create_order(self.currency_pair, side, total_value, ordbook_type[side], ord_type='limit')   # 주문 시도
            
            if order_ret is not None:                                                                      # 주문 정상적 처리
                self.push_slack(f'<create_order> coin:{self.currency_pair}, side:{side}, total_value:{total_value}, strategy_name:{strategy_name}, signal_name:{signal_name}')
                self.interval_flag[side]=True                                                             # 다음 side는 interval 조건 만족 여부 확인
                self.interval_flag[opposite_side]=False                                                   # 다음 opposite_side는 interval 조건 필요 X
                
                order_ret = order_ret.iloc[0]    
                self.wait_orders.append(order_ret['id'])                                                  # 체결 대기 주문 추가
                self.last_order_time[side][strategy_name][signal_name] = int(datetime.now().timestamp())  # 마지막 주문 시간 갱신
                self.order_count[side][strategy_name][signal_name] += 1                                   # 매매 카운트 갱신
                for opposite_signal_name in list(self.order_count[opposite_side][strategy_name].keys()):     
                    if opposite_signal_name not in ['stop_loss', 'stop_profit']:
                        self.order_count[opposite_side][strategy_name][opposite_signal_name] = 0              # 동일 전략 반대쪽 포지션 카운트 초기화
                        self.state_db.write_order_count(self.currency_pair,
                                               self.trader.exchange,
                                               opposite_side, strategy_name,
                                               opposite_signal_name, self.order_count[opposite_side][strategy_name][opposite_signal_name])
                # 카운트, 마지막 주문 시간 db 추가
                self.state_db.write_order_count(self.currency_pair,
                                           self.trader.exchange,
                                           side, strategy_name,
                                           signal_name, self.order_count[side][strategy_name][signal_name],
                                           self.last_order_time[side][strategy_name][signal_name])
                self.state_db.write_wait_order(self.currency_pair,
                                          self.trader.exchange,
                                          order_ret['id'],
                                          side, strategy_name,
                                          signal_name)
                logger.info(f"<주문 완료> id:{order_ret['id']}, coin:{self.currency_pair}, side:{side}, total_value:{total_value}, strategy_name:{strategy_name}, signal_name:{signal_name}, count:{self.order_count[side][strategy_name][signal_name]}")
            else:
                logger.info(f"<주문 실패> coin:{self.currency_pair}, side:{side}, total_value:{total_value}, strategy_name:{strategy_name}, signal_name:{signal_name}, count:{self.order_count[side][strategy_name][signal_name]}'")
        else:
            logger.info('<조건 불만족> interval조건 불만족')
        
    def check_interval_order(self, side:str):
        """
        Interval 조건 여부 확인 함수

        Parameters
        ----------
        side : TYPE
            'buy' or 'sell'.

        Returns
        -------
        int
            1: 조건 만족
            0: 조건 불만족.

        """
        if self.interval_flag[side] == False:
            return 1
        else:
            last_order_time = max([max([order_time for order_time in list(self.last_order_time[side][strategy_name].values())])\
                                    for strategy_name in self.strategy_name])
            # 마지막 대기 + 체결 주문 시간
            if self.interval[-1] == 'm':
                add_timestamp = int(self.interval[:-1]) * 60
            elif self.interval[-1] == 'h':
                add_timestamp = int(self.interval[:-1]) * 3600
            elif self.interval[-1] == 'd':
                add_timestamp = int(self.interval[:-1]) * 86400
            elif self.interval[-1] == 'w':
                add_timestamp = int(self.interval[:-1]) * 604800
            elif self.interval[-1] == 'M':
                add_timestamp = int(self.interval[:-1]) * 18144000
                
            if int(datetime.now().timestamp()) >= last_order_time + add_timestamp:
                return 1    # 조건 만족
            else:
                return 0    # 조건 불만족
            
    def count_check(self, strategy_name:str, signal_name:str):
        """
        조건의 현재 진입횟수 리턴

        Parameters
        ----------
        strategy_name : str
            전략 파일 이름.
        signal_name : str
            조건 이름.

        Returns
        -------
        count : int
            진입 횟수.

        """
        for side in list(self.order_count.values()):
            if signal_name in list(side[strategy_name].keys()):
                count = side[strategy_name][signal_name]
        return count
        
class Strategy():
    def __init__(self,
                 strategy_name,
                 strategy,
                 indicator,
                 condition):
        self.strategy_name = strategy_name          # 전략 파일 이름
        self.strategy = strategy                    # strategy 내용
        self.indicator = indicator                  # indicator 내용
        self.condition = condition                  # condition 내용
        self.signal_name = {'buy':[], 'sell':[]}    # 조건 이름 초기화
        self.get_signal_name()                      # 조건 이름 초기화
        self.ref_strategy = self.make_strategy()    # eval 함수 돌리기 위하여 정제한 strategy
        self.ref_indi = self.make_indi()            # eval 함수 돌리기 위하여 정제한 indicator
        
        
    def make_strategy(self):
        """
        전략 파일 내의 전략 내용을 파이썬에서 사용할 수 있도록 정제


        Returns
        -------
        strategy : TYPE
            정제된 전략 .

        """
        # strategy: 전략 내용
        # strategy_name: 전략파일 이름
        
        # crossDown -> cross_down
        # crossUp -> cross_up
        # buy( -> self.buy(strategy_name,
        # sell( -> self.sell(strategy_name, 
        strategy = self.strategy.\
            replace('crossDown', 'cross_down').\
            replace('crossUp', 'cross_up').\
            replace('buy(', 'self.buy(strategy_name, ').\
            replace('sell(', 'self.sell(strategy_name, ')
            
        # 'a' -> df['a']
        # ex) 'rsi_7' -> 'df[rsi_7']
        strategy = re.sub("\'.*?\'", 'df[\g<0>]', strategy)
        
        # stock = df['all'] -> stock = 'all'
        strategy = re.sub(
            "stock=df\[(.*?)\]", "stock="+"\g<1>", strategy)
        # (df[a] -> (a
        strategy = re.sub(
            "\(df\[(.*?)\]", "("+"\g<1>", strategy)   # cross_up, cross_down    
        
        # buy(df[signal_name]) -> buy(signal_name) 
        strategy = re.sub(",\s*df\[(.*?)\]", ", \g<1>", strategy)   
        
        # cross_up, cross_down
        strategy = strategy.\
            replace('cross_down(', 'cross_down(df_all, ').\
            replace('cross_up(', 'cross_up(df_all, ')
            
        # count 조건 df[signal_name] -> self.count_check(strategy_name, signal_name)
        for side in list(self.signal_name.values()):
            for signal_name in side:
                if signal_name not in ['stop_loss', 'stop_profit']:
                    strategy = re.sub("(df\[\'{}\'\])".format(signal_name), f"self.count_check(strategy_name, '{signal_name}')",  strategy)
        return strategy
        
    def make_indi(self):
        """
        전략 파일 내 indicator 내용을 파이썬에서 사용할 수 있도록 정제

        Returns
        -------
        ref_indi : TYPE
            정제한 데이터.

        """
        ref_indi = []
        for indi in self.indicator:
            ref_indi.append(f"add_{indi.replace('(', '(self.df, ')}")
        return ref_indi

    def get_signal_name(self):
        """
        멤버 변수 signal_name에 전략 파일 내에 사용하는 조건들을 'buy', 'sell'로 구분하여 추가

        Returns
        -------
        None.

        """
        for side in ['buy', 'sell']:
            signal = re.findall(f"{side}\(\'(.*?)\'\,", self.strategy)
            for signal_name in signal:
                self.signal_name[side].append(signal_name)

