# 외부 라이브러리
import sys
import os
import pandas as pd
import pathlib
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))

# 내부 모듈
from module.order_creator.checker import *
from module.order_creator.request import Request

"""
Created on 2021.1.23
@author: 김상혁
"""

class OrderCreator:
    """
    전략 파일(JSON)을 읽어서 Request 객체를 생성하고 
    Request 객체를 이용하여 주문파일을 생성한다.

    파일명 정의 규칙
    -> '종목이름_interval' 로한다. 일봉일 땐 interval = d, 주봉일 땐 interval = w
    예) 
    일봉 -> 종목이름_d.json
    주봉 -> 종목이름_w.json
    
    # 사용 예시
    ----------
    
    >>> mod = OrderCreator('network')
    # OrderCreator 객체 생성
    # 주문생성 모드를 설정한다. {'local', 'network'}

    >>> mod.read_file('DS_strategy_test.json')
    # 전략파일 삽입

    >>> mod.make_order()
    # 주문파일 생성

    # example) order.json
    [
        {
            "order_datetime": "2019-01-28",
            "order_type": "sell",
            "item_code": "005930",
            "item_name": "삼성전자",
            "order_price": "44750",
            "order_option": "por",
            "order_value": "0.4"
        },
        {
            "order_datetime": "2019-01-29",
            "order_type": "sell",
            "item_code": "005930",
            "item_name": "삼성전자",
            "order_price": "45050",
            "order_option": "por",
            "order_value": "0.4"
        }
    ]    
    """    
    # -------------------------------------------------------------------------------
    # Constructors
    def __init__(self, network:bool, mix:bool, root_path) -> None:
        """
        클래스 멤버변수를 초기화한다.
        
        Parameters
        ----------
        network: T/F
            주문생성 모드, 가격데이터 생성시 network 사용 여부
        
            True: network를 이용하여 생성한다.
            False: Request 객체에 필요한 데이터를 생성할 때 local file로부터 생성한다.

        mix: T/F
            주문생성 모드, 여러 종목을 하나의 주문파일로 만들 것인지 여부

            True: 동일한 전략(또는 다양한 전략)에 대해서 여러 종목에 적용 시 하나의 주문파일로 생성함.
            False: 동일한 전략(또는 다양한 전략)에 대해서 여러 종목에 적용 시 각각의 주문파일로 생성함
        
        root_path:

        Returns
        -------
        None.
        """
        self.root_path = root_path
        self.network = network
        self.mix = mix
        self.order_requests = list()
        self.today_order = False
        self.__trade_list = list() # 거래 정보를 저장하는 리스트
        self.o_log = list() # 주문시 주가데이터 및 지표를 저장하는 리스트
    # -------------------------------------------------------------------------------  
    
    def read_file(
            self,
            file_name:str,
            full_path:bool=False,
            stock_file=False) -> None:
        """
        
        전략파일을 읽어 Request 객체를 생성하여 전달한다.
        생성된 Request 객체는 order_requests 멤버변수에 저장된다.
        
        Parameters
        ----------
        file_name:
            전략파일 이름
            DataFrame
        full_path:
            절대경로 설정 유무
            boolean
        stock_file:
            로컬파일모드 시 주가데이터파일을 입력

        Returns
        -------
        None.
        """
        if full_path:
            file = pathlib.Path(file_name)
        else:
            file = pathlib.Path(self.root_path+'/strategyFile/'+file_name)
        
        try:
            text = file.read_text(encoding='utf-8')
        except FileNotFoundError:
            self._print_error(2)
            return False

        js = json.loads(text)
        df = pd.DataFrame(js)

        for i in df.index:
            self.order_requests.append(Request(self.network, self.root_path))
            if self.network:
                if self.order_requests[i].set_request(df.loc[i]):
                    pass
                else:
                    return False
            else:
                if self.order_requests[i].set_request(df.loc[i], stock_file):
                    pass
                else:
                    return False
        
        return True

    def read_df(self,
                df:pd.DataFrame,
                path) -> None:
        """
        DataFrame을 읽어 Request 객체를 생성하여 전달한다.
        생성된 Request 객체는 order_requests 멤버변수에 저장된다.
        
        Parameters
        ----------
        file_name:
            전략파일 이름
            DataFrame

        Returns
        -------
        None.
        """
        for i in df.index:
            self.order_requests.append(Request(self.network,root_path=path))
            if self.order_requests[i].set_request(df.loc[i]):
                pass
            else:
                return False
        
        return True

    def _write_order(self, request:Request, file_name:str='') -> None:
        """
        trade_list를 이용하여 Order.json으로 저장한다.
        
        Parameters
        ----------
        request:
            Request 객체
            Request 객체에 저장된 DataFrame을 이용하기 위함

        file_name:string
            orderLogFile.json의 파일명을 입력받는다. 

        Returns
        -------
        None.
        """
        # 리스트를 데이터프레임로 변환
        result_df = pd.DataFrame(self.__trade_list, 
                                columns=['order_datetime',
                                        'order_type',
                                        'item_code',
                                        'item_name',
                                        'order_price',
                                        'order_option',
                                        'order_value'])
        result_df.set_index('order_datetime', inplace=True)
        
        # 사용자가 입력한 기간에 맞도록 슬라이싱
        result_df = result_df[request.startdate:request.enddate]
        result_df.reset_index(inplace=True)

        result_df = result_df.sort_values(by=['order_datetime']) # 날짜에 대해 정렬
    
        adict = result_df.to_dict(orient='records')
        
        if not adict:
            self._print_error(1)
            return False

        # order json file 생성        
        os.makedirs(self.root_path+'/orderFile', exist_ok=True)

        if self.mix:
            with open(self.root_path+'/orderFile/'+request.stock_df['item_name'][0]+'_mix_Order.json', 'w+', encoding='utf-8') as make_file:
                    json.dump(adict, make_file, ensure_ascii=False, indent='\t')

        else:
            if request.interval.upper() == 'D':
                if file_name == '':
                    with open(self.root_path+'/orderFile/'+request.stock_df['item_name'][0]+'_d_Order.json', 'w+', encoding='utf-8') as make_file:
                        json.dump(adict, make_file, ensure_ascii=False, indent='\t')
                else:
                    with open(f"{self.root_path}/orderFile/{file_name}_d_Order.json", 'w+', encoding='utf-8') as make_file:
                        json.dump(adict, make_file, ensure_ascii=False, indent='\t')

            elif request.interval.upper() == 'W':
                if file_name == '':
                    with open(self.root_path+'/orderFile/'+request.stock_df['item_name'][0]+'_w_Order.json', 'w+', encoding='utf-8') as make_file:
                        json.dump(adict, make_file, ensure_ascii=False, indent='\t')
                else:
                    with open(f"{self.root_path}/orderFile/{file_name}_w_Order.json", 'w+', encoding='utf-8') as make_file:
                        json.dump(adict, make_file, ensure_ascii=False, indent='\t')

        print('주문파일이 생성되었습니다.')
        del self.__trade_list[:] # 리스트를 초기화하여 새로운 주문에 대해서 리스트를 받을 수 있게 함
        return True

    def _write_olog(self, request:Request, file_name:str=''):
        '''
        Write orderLog.json

        Parameters
        ----------
        request:
            Request 객체
            Request 객체에 저장된 DataFrame을 이용하기 위함

        file_name:string
            orderLogFile.json의 파일명을 입력받는다. 

        Returns
        -------
        None.          
        '''
        # 리스트를 데이터프레임로 변환
        indi_col = list(request.stock_df.columns[9:])
        columns = list()
        columns.extend(['order_datetime',
                        'open',
                        'high',
                        'low',
                        'close',
                        'volume',
                        'change'])
        columns.extend(indi_col)
        columns.extend(['order_type','log'])

        result_df = pd.DataFrame(self.o_log, 
                                columns=columns)

        result_df = result_df.sort_values(by=['order_datetime']) # 날짜에 대해 정렬
    
        log_dict = result_df.to_dict(orient='records')

        if not log_dict:
            self._print_error(3)
            return False

        # orderLog json file 생성        
        os.makedirs(self.root_path+'/orderLogFile', exist_ok=True)

        if self.mix:
            with open(f"{self.root_path}'/orderFile/'{request.stock_df['item_name'][0]}_mix_orderLog.json", 'w+', encoding='utf-8') as make_file:
                    json.dump(log_dict, make_file, ensure_ascii=False, indent='\t')

        else:
            if request.interval.upper() == 'D':
                if file_name == '':
                    with open(f"{self.root_path}/orderLogFile/{request.stock_df['item_name'][0]}_d_orderLog.json", 'w+', encoding='utf-8') as make_file:
                        json.dump(log_dict, make_file, ensure_ascii=False, indent='\t')
                else:
                    with open(f"{self.root_path}/orderLogFile/{file_name}_d_orderLog.json", 'w+', encoding='utf-8') as make_file:
                        json.dump(log_dict, make_file, ensure_ascii=False, indent='\t')
            elif request.interval.upper() == 'W':
                if file_name == '':
                    with open(f"{self.root_path}/orderLogFile/{request.stock_df['item_name'][0]}_w_orderLog.json", 'w+', encoding='utf-8') as make_file:
                        json.dump(log_dict, make_file, ensure_ascii=False, indent='\t')
                else:
                    with open(f"{self.root_path}/orderLogFile/{file_name}_w_orderLog.json", 'w+', encoding='utf-8') as make_file:
                        json.dump(log_dict, make_file, ensure_ascii=False, indent='\t')

        print('주문로그파일이 생성되었습니다.')
        del self.o_log[:] # 리스트를 초기화하여 새로운 주문기록에 대해서 리스트를 받을 수 있게 함
        return True

    def make_order(self, file_name:str='') -> bool:
        """
        Request 객체에 담긴 데이터를 이용하여 주문파일을 생성한다.
        file_name을 주지않으면 [종목명]_[interval]_Order.json으로 파일명이 생성된다.
        
        Parameters
        ----------
        file_name
            order.json 파일명을 입력받는다.
        
        Returns
        -------
        boolean.
        """        
        
        def make_strategy(strategy:str) -> str:
            """
            사용자 편의를 위해 간력하게 입력한 문자열을 기존 함수 구조에 맞게 문자열을 수정한다.
            수정1. sell, buy함수 인자로 trade 추가
            수정2. crossUp, Down함수 인자로 trade, inner_idx, trade_df 추가
            
            Parameters
            ----------        
            strategy: 전략문자열

            Returns
            -------
            string.
            """
            
            strategy = strategy.\
                replace('crossDown(', 'crossDown(trade, inner_idx, request.stock_df, ').\
                replace('crossUp(', 'crossUp(trade, inner_idx, request.stock_df, ').\
                replace('sell(', 'self._sell(trade, inner_idx, request.stock_df, ').\
                replace('buy(', 'self._buy(trade, inner_idx, request.stock_df, ')

            strategy = re.sub("\'.*?\'", 'trade[\g<0>]', strategy) # 작은따음표 df[] 붙임
            strategy = re.sub("stock=trade\[(.*?)\]", "stock="+"\g<1>", strategy)  # stock='all' 
            # strategy = re.sub("\(trade\[(.*?)\]", "("+"\g<1>", strategy)   # cross_up, cross_down
            strategy = re.sub(",\s*trade\[(.*?)\]", ", \g<1>", strategy)   # cross_up, cross_down

            return strategy

        '''
        추가사항
        사용자가 전략식 작성 시에 새로운 변수를 추가해서 사용할 수 있도록 수정
        dictionary type variable를 for loop 밖에서 선언하여 사용할 수 있도록
        그리고 전략식에서 add method로 변수를 추가하여 사용할 수 있도록 해야 함
        '''
        inner_variable = {} # 전략식에서 사용자가 사용할 변수를 담는 딕셔너리변수
        # ------------------------------------------------------------------------------------
        for request in self.order_requests:
            for inner_idx, trade in request.stock_df.iterrows():
                # request.strategy = re.sub("\'.*?\'", 'trade[\g<0>]', request.strategy)
                exec(make_strategy(request.strategy)) # 전략식 수행
        # ------------------------------------------------------------------------------------
            if self.mix:
                self._write_olog(request, file_name=file_name)               

            else:
                # 각각의 order를 생성해야함
                self._write_order(request, file_name=file_name)
                self._write_olog(request, file_name=file_name)

        # 첫번째 Request 객체의 stock name으로 함
        if self.mix:
            if not self._write_order(self.order_requests['0']):
                return False

        return self.today_order

    def _buy(
        self,
        trade_row:pd.Series,
        idx:int,
        df:pd.DataFrame,
        log:str='',
        stock:int or float or str='all',
        money:int or float = None,
        position:str='Onclose'
        ) -> None:
        """
        전략에 일치하는 시점에 데이터를 이용하여 거래 정보(매수)를 생성한다.
        
        Parameters
        ----------
        trade_row: row of DataFrame
            Series로 된 데이터프레임의 행
        idx: index of row
        df: Stock DataFrame
        log: default ''
            buy 함수가 호출될 때 어떤 조건에의해 호출되었는지 기록할 수 있다.
        stock: stock option, default 'all'
            거래량을 정하는 옵션
            integer 일 땐 그 수만큼 종목을 매수
            float 일 땐 그 수를 %로 계산하여 보유 현금에 맞게 종목을 매수
            'all': 보유 현금으로 살 수 있는 최대로 매수
        money: stock option, default None
            거래량을 정하는 옵션
            integer 일 땐 그 금액만큼 종목을 매수
            float 일 땐 그 수를 %로 계산하여 초기 자본금에 맞게 종목을 매수
        position: {'Onclose', 'NextOpen'} default 'Onclose'
            거래 가격을 정하는 옵션
            'Onclose': 신호발생 종가로 신호발생 다음날 거래
            'Nextopen': 신호발생 다음날 시가로 신호발생 다음날 거래
        
        Returns
        -------
        None.
        """
        
        '''
        money변수에 값이 존재하는지 확인해야함
        money변수가 None이고 입력한 변수가 없으면 stock == 'all'로 하고 
        money변수와 stock변수를 함께 사용했을 땐 에러처리를 해야함
        '''

        order_value = ''

        if money:
            if type(money) is int:
                order_option = 'cash'

            elif type(money) is float:
                order_option = 'm_por'

            order_value = str(money)

        else:
            # 거래량 옵션
            if type(stock) is int:
                order_option = 'scnt'

            elif type(stock) is float:
                order_option = 'por'

            elif stock == 'all':
                order_option = 'all'

            order_value = str(stock)

        try:
            # 거래가격 옵션
            if position == 'Onclose':
                trade_price = str(int(trade_row.close))
            
            elif position == 'Nextopen':
                trade_price = str(int(df.iloc[idx+1]['open']))

        except IndexError:
            trade_price = str(int(trade_row.close))

        '''주봉에 경우 일봉 가격데이터로 거래 가격을 생성하는지 아님 주봉 가격데이터로 거래 가격을 생성하는지  
        -> 일봉가격으로 생성하려면 일봉가격이 데이터프레임에 존재해야함'''
        # 다음날 거래하도록 하는 것이 아닌 다음인덱스(df에 존재하는 시간)에 거래하도록 함        
        try:
            result_date = df.iloc[idx+1]['Date']

            self.__trade_list.append([result_date,
                                    'buy',
                                    trade_row.item_code,
                                    trade_row.item_name,
                                    trade_price,
                                    order_option,
                                    order_value])
        
        # 신호가 오늘 발생했을 때에는 df.iloc[idx+1]['Date'] 문장에 에러가 발생할 것임 idx+1에 해당하는 인덱스가 없기 때문        
        # 에러에 대한 처리를 해줘야 함 오늘 신호가 발생했을 때 
        # 즉, exception 발생 __enddate에 접근해서 + 1일 해주어야 함(토요일일 때는 월요일로)
        except IndexError:
            print('마지막 날에 buy 신호 발생 ')
            self.today_order = ['buy', trade_row.item_code, trade_price, order_value]

        finally:
            print(trade_row.Date, log, '조건에서 buy발생')

            log_list = list()

            log_list.extend([trade_row.Date,
                            trade_row.open,
                            trade_row.high,
                            trade_row.low,
                            trade_row.close,
                            trade_row.volume,
                            round(trade_row.change,5)])
            
            log_list.extend(list(trade_row)[9:])

            log_list.extend(['buy',log])

            self.o_log.append(log_list)        
       
    def _sell(
        self,
        trade_row:pd.Series,
        idx:int,
        df:pd.DataFrame,
        log:str='',
        stock:int or float or str='all',
        money:int or float=None,
        position:str='Onclose'
        ) -> list:
        """
        전략에 일치하는 시점에 데이터를 이용하여 거래 정보(매도)를 생성한다.
        
        Parameters
        ----------
        trade_row: row of DataFrame
            Series로 된 데이터프레임의 행
        idx: index of row
        df: Stock DataFrame
        log: default ''
            sell 함수가 호출될 때 어떤 조건에의해 호출되었는지 기록할 수 있다.
        stock: stock option, default 'all'
            거래량을 정하는 옵션
            integer 일 땐 그 수만큼 종목을 매도
            float 일 땐 그 수를 %로 계산하여 보유 주식에 맞게 종목을 매도
            'all': 보유 현금으로 살 수 있는 최대로 매도
        moeny: stock option, default None
            거래량을 정하는 옵션
            integer 일 땐 그 금액만큼 종목을 매도
            float 일 땐 그 수를 %로 계산하여 보유 주식에 맞게 종목을 매도
        position: {'Onclose', 'NextOpen'} default 'Onclose'
            거래 가격을 정하는 옵션
            'Onclose': 신호발생 종가로 신호발생 다음날 거래
            'Nextopen': 신호발생 다음날 시가로 신호발생 다음날 거래
        
        Returns
        -------
        list
            가격데이터프레임의 마지막 행에 신호가 발생했을 시
            주문 정보 리스트를 리턴한다.        
        """

        order_value = ''

        if money:
            # 거래량 옵션
            if type(money) is int:
                order_option = 'cash'

            elif type(money) is float:
                order_option = 'm_por'

            order_value = str(money)

        else:
            # 거래량 옵션
            if type(stock) is int:
                order_option = 'scnt'

            elif type(stock) is float:
                order_option = 'por'

            elif stock == 'all':
                order_option = 'all'

            order_value = str(stock)
        
        try:
            # 거래가격 옵션
            if position == 'Onclose':
                trade_price = str(int(trade_row.close))
            
            elif position == 'Nextopen':
                trade_price = str(int(df.iloc[idx+1]['open']))

        except IndexError:
            trade_price = str(int(trade_row.close))

        '''주봉에 경우 일봉 가격데이터로 거래 가격을 생성하는지 아님 주봉 가격데이터로 거래 가격을 생성하는지  
        -> 일봉가격으로 생성하려면 일봉가격이 데이터프레임에 존재해야함'''
        # 다음날 거래하도록 하는 것이 아닌 다음인덱스(df에 존재하는 시간)에 거래하도록 함        
        try:
            result_date = df.iloc[idx+1]['Date']

            self.__trade_list.append([result_date,
                                    'sell',
                                    trade_row.item_code,
                                    trade_row.item_name,
                                    trade_price,
                                    order_option,
                                    order_value])
        
        # 신호가 오늘 발생했을 때에는 df.iloc[idx+1]['Date'] 문장에 에러가 발생할 것임 idx+1에 해당하는 인덱스가 없기 때문
        # 에러에 대한 처리를 해줘야 함 오늘 신호가 발생했을 때 + 1일 해주어야 함(토요일일 때는 월요일로)
        except IndexError:
            print('마지막 날에 sell 신호 발생')
            self.today_order = ['sell', trade_row.item_code, trade_price, order_value]

        finally:
            print(trade_row.Date, log, '조건에서 sell발생')
            log_list = list()

            log_list.extend([trade_row.Date,
                            trade_row.open,
                            trade_row.high,
                            trade_row.low,
                            trade_row.close,
                            trade_row.volume,
                            round(trade_row.change,5)])
            
            log_list.extend(list(trade_row)[9:])

            log_list.extend(['sell',log])

            self.o_log.append(log_list)

    def _print_error(self, erc:int) -> None:
        """        
        Parameters
        ----------
        erc : TYPE
            DESCRIPTION.

        Returns
        -------
        None.
        
        warning code 1 -> 전략에 맞는 거래 시점이 존재하지 않음.
        warning code 2 -> 전략 파일이 존재하지 않습니다.
        warning code 3 -> 전략에 맞는 주문 기록이 없음
        """        
        error = {1 : '전략에 맞는 주문이 생성되지 않았습니다.',
                2 : '전략파일이 존재하지 않습니다.',
                3 : '전략에 맞는 주문기록이 존재하지 않습니다.'}
    
        print('OrderCreator warning code {} : {}'.format(erc, error[erc]))

if __name__ == "__main__":
    mod = OrderCreator(network=False, mix=False)
    if mod.read_file(file_name='삼성전자_d_strategy.json', stock_file='C:\\Users\\ksang\\Dropbox\\P407\\stockFile\\삼성전자_d.csv'):
        today_order = mod.make_order()
        print(today_order)
    

    # call graph를 그리기 위함
    # with PyCallGraph(output=GraphvizOutput()):
    #     mod.make_order()
    