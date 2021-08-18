import os
import sys
import re
import pandas as pd
from datetime import datetime, timezone
sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))

from module.auto_trader import util
from module.labeler.labeler import *
from module.auto_trader.indicator import *

# logger = logging.getLogger('strategy_monitor')
logger = util.CreateLogger('check_condition')

# item 클래스


class Item():
    def __init__(self, code: str, interval: str, unit: str, strategy_name: list,
                 buy_count: int, sell_count: int, betting_rate: float or int, betting_price: int,
                 buy_pyramiding: float or int, sell_pyramiding: float or int, stop_loss: float):
        """

        Parameters
        ----------
        code : str
            코인명
            ex)KRW-XRP, KRW-BTC ...
        interval : str
            candle 봉 시간 타입
            ex)m, d, w, M
        unit : str
            봉 타입일 경우 시간
            ex) 5, 15, 30, 60
        strategy_name : list
            적용할 전략파일 이름
            ex) ['strategy1.json', 'strategy2.json', ...]
        buy_count : int
            매수 동일 조건 진입 횟수
        sell_count : int
            매도 동일 조건 진입 횟수
        betting_rate : float or int
            총 KRW 대비 코인 할당 비율
        betting_price : int
            코인 할당 금액
        buy_pyramiding: float or int
            매수 피라미딩 차수
        sell_pyramiding : float or int
            매도 피라미딩 차수
        Returns
        -------
        None.

        """

        self.code: str = code                   # 코인 코드
        self.interval: str = interval           # 캔들 시간
        self.df: pd.Dataframe = pd.DataFrame()  # 가격 정보 데이터프레임
        self.strategy_name = strategy_name      # 전략 파일 이름
        self.max_buy_count = buy_count          # 동일 매수 조건 최대 진입 허용 횟수
        self.max_sell_count = sell_count        # 동일 매도 조건 최대 진입 허용 횟수
        self.buy_order_volume = {}              # 매수량{매수신호이름:매수량}
        self.sell_order_volume = {}             # 매도량{매도신호이름:매도량}
        self.buy_count = {}                     # 현재 매수 조건 진입 횟수{매수신호이름:횟수}
        self.sell_count = {}                    # 현재 매도 조건 진입 횟수{매도신호이름:횟수}
        self.buy_uuids = {}                     # 매수 주문 체결 대기 중인 uuid{매수신호이름:[uuid]}
        self.sell_uuids = {}                    # 매도 주문 체결 대기 중인 uuid{매도신호이름:[uuid]}
        self.last_buy_time = {}                 # 마지막 매수 주문 시간(대기 or 완료, 취소 X){마지막매수주문시간:True}
        self.last_sell_time = {}                # 마지막 매도 주문 시간(대기 or 완료, 취소 X){마지막매도주문시간:True}
        self.betting_rate = betting_rate        # 현재 현금 대비 코인에 적용할 자산 비율
        self.betting_price = betting_price      # 코인에 적용할 자산 금액 
        self.buy_pyramiding = buy_pyramiding    # 매수 피라미딩
        self.sell_pyramiding = sell_pyramiding  # 매도 피라미딩
        self.stop_loss = stop_loss              # 손절 비율
        if unit.isdigit():                      # 몇 분
            self.unit: int = int(unit)
        else:
            self.unit = None

    def set_df(self, upbit_quotation):
        """
        가격 정보가 포함되어 있는 데이터프레임 수신

        Parameters
        ----------
        upbit_quotation : upbit_api.Upbit_Api
            업비트 API

        Returns
        -------
        None.


        """
        temp = pd.DataFrame()
        if self.interval == 'm':
            if self.unit == 1:
                temp = upbit_quotation.get_candle_min(market=self.code, unit=1)
            elif self.unit == 3:
                temp = upbit_quotation.get_candle_min(market=self.code, unit=3)
            elif self.unit == 5:
                temp = upbit_quotation.get_candle_min(market=self.code, unit=5)
            elif self.unit == 10:
                temp = upbit_quotation.get_candle_min(
                    market=self.code, unit=10)
            elif self.unit == 15:
                temp = upbit_quotation.get_candle_min(
                    market=self.code, unit=15)
            elif self.unit == 30:
                temp = upbit_quotation.get_candle_min(
                    market=self.code, unit=30)
            elif self.unit == 60:
                temp = upbit_quotation.get_candle_min(
                    market=self.code, unit=60)
            elif self.unit == 240:
                temp = upbit_quotation.get_candle_min(
                    market=self.code, unit=240)
        elif self.interval == 'd':
            temp = upbit_quotation.get_candle_day(market=self.code)
        elif self.interval == 'w':
            temp = upbit_quotation.get_candle_week(market=self.code)
        elif self.interval == 'M':
            temp = upbit_quotation.get_candle_month(market=self.code)
        self.df = temp

    def set_indi(self, strategy_dict: dict):
        """
        데이터프레임(self.df)에 지표, 레이블 컬럼 추가

        Parameters
        ----------
        strategy_dict : dict
            strategy객체가 들어 있는 리스트.

        Returns
        -------
        None.

        """
        df = self.df
        for strategy_name in self.strategy_name:
            for i in strategy_dict[strategy_name].indicator:
                eval('add_' + i.replace('(', '(df, '))

    def interval_order(self, ord_type):
        df_time = self.df['candle_date_time_utc']
        df_time = datetime.strptime(df_time.iloc[-1], '%Y-%m-%dT%H:%M:%S')
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
        now = datetime.strptime(now, '%Y-%m-%dT%H:%M:%S')
        
        if ord_type == 'buy':
            last_order_time = self.last_buy_time
        elif ord_type == 'sell':
            last_order_time = self.last_sell_time

        if len(last_order_time) == 0:
            last_order_time[now] = True
            return 1
        else:
            # 마지막 매매 시간이 현재 interval이 아니면
            if list(last_order_time.keys())[0] < df_time:
                last_order_time = {}
                last_order_time[now] = True
                return 1
            # 마지막 매매 시간이 현재 interval이면
            else:
                return 0

    def check_condition(self, strategy_name: str, strategy_dict: dict):
        """
        현재 코드의 가격정보와 매매 전략 조건 만족 여부 판단

        Parameters
        ----------
        strategy_name : str
            전략파일 이름.
        strategy_dict : dict
            strategy객체 리스트.

        Returns
        -------
        None.

        """
        def make_strategy(strategy: str) -> str:
            """
            전략파일 내용을 파이썬에서 처리 할 수 있게 정제

            Parameters
            ----------
            strategy : str
                전략파일 내용.

            Returns
            -------
            str
                정제된 전략파일 내용.

            """
            # strategy: 전략 내용
            # strategy_name: 전략파일 이름
            strategy = strategy.\
                replace('crossDown', 'cross_down').\
                replace('crossUp', 'cross_up').\
                replace('buy(', 'self.buy(strategy_name, ').\
                replace('sell(', 'self.sell(strategy_name, ')
            # 작은따음표 df[] 붙임
            strategy = re.sub("\'.*?\'", 'df[\g<0>]', strategy)
            strategy = re.sub(
                "stock=df\[(.*?)\]", "stock="+"\g<1>", strategy)  # stock='all'
            strategy = re.sub(
                "\(df\[(.*?)\]", "("+"\g<1>", strategy)   # cross_up, cross_down
            # cross_up, cross_down
            strategy = re.sub(",\s*df\[(.*?)\]", ", \g<1>", strategy)
            strategy = strategy.\
                replace('cross_down(', 'cross_down(df_all, ').\
                replace('cross_up(', 'cross_up(df_all, ')
            return strategy

        df_all = self.df
        df = df_all.iloc[-1].copy()    # 마지막 인덱스(가장 최근 인덱스만 확인)

        # count 조건 처리
        buy_signal = re.findall(
            "buy\(\'(.*?)\'\,", strategy_dict[strategy_name].strategy)
        for signal_name in buy_signal:
            replace_name = strategy_name.replace('.json', '')
            name = f'{replace_name}.{signal_name}'
            if name in list(self.buy_count.keys()):
                df.loc[signal_name] = self.buy_count[name]
            else:
                df.loc[signal_name] = 0

        sell_signal = re.findall(
            "sell\(\'(.*?)\'\,", strategy_dict[strategy_name].strategy)
        for signal_name in sell_signal:
            replace_name = strategy_name.replace('.json', '')
            name = f'{replace_name}.{signal_name}'
            if name in list(self.sell_count.keys()):
                df.loc[signal_name] = self.sell_count[name]
            else:
                df.loc[signal_name] = 0

        exec(make_strategy(strategy_dict[strategy_name].strategy))

    def buy(self, strategy_name: str, signal_name: str, stock: float or int or str):
        """
        매수 신호 발생시 처리 함수

        Parameters
        ----------
        strategy_name : str
            전략 파일 이름.
        signal_name : str
            매수 신호 이름.
        stock : float or int or str
            매수량.

        Returns
        -------
        None.

        """
        # 거래 이름 설정
        strategy_name = strategy_name.replace('.json', '')
        name = f'{strategy_name}.{signal_name}'
        # 처음 거래하는 조건일 시 초기화
        if name not in self.buy_count.keys():
            self.buy_count[name] = 0
        # ord_count만큼만 거래
        if (self.buy_count[name] + 1) <= self.max_buy_count:

            # 피라미딩 처리
            if self.buy_count[name] >= 1:
                pyramiding =  self.buy_pyramiding ** self.buy_count[name]
            # 첫번째 매수 일시 피라미딩은 1
            else:
                pyramiding = 1
            # 매수량 처리
            self.buy_order_volume[name] = stock * pyramiding
            # 매수 횟수 처리
            self.buy_count[name] += 1
        else:
            logger.info(f"<횟수 제한> {name}:{self.buy_count[name]}")

    def sell(self, strategy_name: str, signal_name: str, stock: float or int or str):
        """
        매도 신호 발생시 처리 함수

        Parameters
        ----------
        strategy_name : str
            전략 파일 이름.
        signal_name : str
            매도 신호 이름.
        stock : float or int or str
            매도량.

        Returns
        -------
        None.

        """
        # 거래 이름 설정
        strategy_name = strategy_name.replace('.json', '')
        name = f'{strategy_name}.{signal_name}'
        # 처음 거래하는 조건일 시 초기화
        if name not in self.sell_count.keys():
            self.sell_count[name] = 0
        # ord_count만큼만 거래
        if (self.sell_count[name] + 1) <= self.max_sell_count:
            # # 매도 신호 발생시 매수 조건 진입 횟수 초기화
            # for buy_name in self.buy_count.keys():
            #     if strategy_name in buy_name:
            #         self.buy_count[buy_name] = 0
            # 피라미딩 처리
            if self.sell_count[name] >= 1:
                pyramiding = self.sell_pyramiding ** self.sell_count[name]
            # 첫번째 매수 일시 피라미딩은 1
            else:
                pyramiding = 1
            # 매도량 처리
            self.sell_order_volume[name] = stock * pyramiding
            # 매도 횟수 처리
            self.sell_count[name] += 1
        else:
            logger.info(f"<횟수 제한> {name}:{self.sell_count[name]}")


# strategy 클래스
class Strategy():
    def __init__(self, name, strategy, indicator):
        """
        전략 파일 이름에 전략과 지표 및 레이블러를 매핑함

        Parameters
        ----------
        name : TYPE
            전략파일 이름.
        strategy : TYPE
            전략.
        indicator : TYPE
            지표 및 레이블.

        Returns
        -------
        None.

        """
        self.name = name
        self.strategy = strategy
        self.indicator = indicator
        
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