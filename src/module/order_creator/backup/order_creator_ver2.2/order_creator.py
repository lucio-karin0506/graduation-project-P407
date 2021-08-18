# 외부 라이브러리
import sys
import os
import pandas as pd
import FinanceDataReader as fdr
import re
import pathlib
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))

# 내부 모듈
from module.gatherer.gatherer import Gatherer
from module.indicator.indicator import *
from module.order_creator.checker import *
from module.labeler.labeler import *

"""
Created on 2021.1.23
@author: 김상혁
"""

class Request:
    """
    전략 파일(JSON)에 객체에 담긴 정보를 저장한다.
    
    # 사용 예시
    ----------

    >>> file = pathlib.Path(os.getcwd()+'/strategyFile/'+'strategy.json')
    >>> text = file.read_text(encoding='utf-8')
    >>> js = json.loads(text)
    >>> request = pd.DataFrame(js)

    >>> mod = Request('network')
    # Request 클래스 객체 생성
    # 주문모드 설정 {'local', 'network'}

    >>> mod.set_request(request.loc[0])
    # 전략파일 정보 세팅
    # 전략파일의 객체 담긴 정보가 Request 객체로 저장된다.

    # example) strategy.json
    [
    	{
    		"stockcode": "066570",
    		"startdate": "2019-01-01",
    		"enddate": "2021-01-01",
    		"interval": "d",
    		"indicator": ["BBands(period=20,nbdevup=2,nbdevdn=2)",
            "RSI(period=14)"],
    		"strategy": 
            "if crossDown('rsi_14', 25): buy(stock=0.2)
            elif 20 < trade.rsi_14 <= 25: buy(stock=0.3)
            elif trade.rsi_14 <= 20: buy(stock=0.5)
            if 35 < trade.rsi_14 <= 45 and trade.close <= trade.lbb_20_2_2: buy(stock=0.1)
            elif trade.rsi_14 <= 35 and trade.close <= trade.lbb_20_2_2: buy(stock=0.3)            
            if crossUp('rsi_14', 70): sell(stock=0.4)
            elif 70 <= trade.rsi_14 < 80: sell(stock=0.4)
            elif crossDown('rsi_14', 70): sell(stock=0.2)            
            if crossUp('rsi_14', 80): sell(stock=0.3)
            elif trade.rsi_14 >= 80: sell(stock=0.3)            
            if crossUp('close', 'ubb_20_2_2') and trade.close < trade.open: sell(stock='all')"
    	}     
    ]
    """
    # -------------------------------------------------------------------------------          
    # Constructors
    def __init__(self, network:bool):
        """
        클래스 멤버변수를 초기화한다.
        
        Parameters
        ----------
        network: True, False
            주문생성 모드
            True일 땐 network를 이용하여 생성한다.
            False일 땐 Request 객체에 필요한 데이터를 생성할 때 local file로부터 생성한다.

        Returns
        -------
        None.  
        """        
        self.network = network
    # -------------------------------------------------------------------------------          

    def _extract(self, order_request:"Series") -> None:
        """
        입력받은 전략파일 데이터를 멤버변수에 초기화한다.
        
        Parameters
        ----------
        order_request:
            전략파일 객체에 담긴 데이터 Series

        Returns
        -------
        None.  
        """         
       
        self.__stockcode = order_request['stockcode']
        self.__startdate = order_request['startdate']
        self.__enddate = order_request['enddate']
        self.interval = order_request['interval']
        self.indicator = order_request['indicator']
        self.strategy = order_request['strategy']

        # 사용자가 입력한 기간에 기술적지표값을 모두 생성하기 위해(이평값을 사용하면 빠지는 값이 발생한다.)
        # 원래 입력한 날짜보다 이전 기간에 날짜를 저장하기 위한 멤버변수
        self.__tech_date = datetime.strptime(self.__startdate, '%Y-%m-%d').date()     

        def to_int(x):
            try:
                if float(x).is_integer():
                    return int(x)
                else:
                    return float(x)
            except:
                pass
        
        if self.network:
            period_list = []
            for tech_indi in self.indicator:
                # tech_value에 parameter중에서 기간(period)을 추출
                tech_indi = re.split('\=|period=|,|\(|\)', tech_indi) # tech_indi 문자열을 {period= , )}문자를 기준으로 나눈다.
                # 문자열중에서 int로 변환가능한 것을 변환한다. None은 리스트에서 제외
                tech_indi = [to_int(x) for x in tech_indi if to_int(x) is not None]
                period_list.extend(tech_indi)

            # datetype에 맞게 tech_date를 생성한다. 뒤로 미룰날짜가 일봉과 주봉이 다르기 때문이다.
            if self.interval.upper() == 'D':
                self.__tech_date = self.__tech_date - relativedelta(days=max(period_list)+30)
            
            elif self.interval.upper() == 'W':
                self.__tech_date = self.__tech_date - relativedelta(weeks=max(period_list)+30)   

            self.__tech_date = datetime.strftime(self.__tech_date, '%Y-%m-%d')

    def _get_stock(self) -> None:
        """
        초기화된 멤버변수를 이용하여 가격데이터프레임을 생성한다.
        network 멤버변수를 확인하여 
        => True-> FinanceDataReader로 주가데이터를 생성함, False-> local file에서 주가데이터를 생성함
        
        Parameters
        ----------        

        Returns
        -------
        None.  
        """            
        self.stock_df = None

        if self.network:
            gather = Gatherer()             
            df, name = gather.get_stock(self.__stockcode, 
                                        self.__tech_date,
                                        self.__enddate,
                                        self.interval,
                                        save=False)
            
            if type(df) is pd.DataFrame:
                self.stock_df = df
            
            else:
                return False           

        else:
            krx_df=\
                pd.read_csv(os.getcwd()+'/stockFile/'+'KRX.csv', usecols=['Symbol', 'Market', 'Name'])
            try:
                name = krx_df.loc[krx_df.Symbol == self.__stockcode, 'Name'].values[0] # 주가 코드에 해당하는 이름을 찾음

            except IndexError: # 외국주식 종목이름은 한국거래소에 등록되어있지 않으므로 code를 name에 저장함
                name = self.__stockcode

            finally:
                if not os.path.isfile(os.getcwd()+'/stockFile/'+name+'_'+self.interval+'.csv'):
                    self._print_error(1)
                    return False
            
            df = pd.read_csv(os.getcwd()+'/stockFile/'+name+'_'+self.interval+'.csv', index_col='Date')
            self.stock_df = df
            
        
        self.stock_df['item_code'] = self.__stockcode
        self.stock_df['item_name'] = name    

    def _add_indicator(self) -> None:
        """
        가격데이터프레임에 기술적지표 컬럼을 추가한다.
        mode가 'network'일 때만 호출된다.
        mode가 'local'일 땐 파일에 미리 추가되어 있는 지표를 사용하므로 호출되지 않음.
        
        Parameters
        ----------

        Returns
        -------
        None.  
        """         
        for indicator in self.indicator:
            eval('add_'+indicator.replace('(', '(self.stock_df,'))
        self.stock_df = self.stock_df.loc[self.__startdate:]

    def set_request(self, order_request:"Series") -> None:
        """
        입력받은 전략파일 데이터를 extract 멤버함수에 전달하고
        get_stock, add_indicator를 호출한다.
        
        Parameters        
        ----------
        order_request: row of DataFrame
            전략파일 객체에 담긴 데이터 Series

        Returns
        -------
        None.  
        """          
        self._extract(order_request)

        # get_stock 또는 add_indicator 함수에서 예외가 발생되면 동작을 멈춰야함        
        try:
            self._get_stock() # 주가데이터 생성

            if self.network:
                self._add_indicator() # 주가데이터에 기술적지표 값(시그널)을 추가
                self.stock_df.reset_index(inplace=True)
                # json파일로 만들때 datetime형식은 깨지므로 문자열로 변환
                self.stock_df['Date'] = self.stock_df['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))

            else:
                self.stock_df = self.stock_df.loc[self.__startdate:]
                self.stock_df.reset_index(inplace=True)

        except:
            return

    def _print_error(self, erc:int) -> None:
        """        
        Parameters
        ----------
        erc : TYPE
            DESCRIPTION.

        Returns
        -------
        None.
        
        error code 1 -> 종목폴더에 해당하는 종목 파일이 없음
        error code
        error code
        """        
        error = {1 : '종목폴더에 해당 종목 파일이 없습니다.'}
    
        print('Request error code {} : {}'.format(erc, error[erc]))

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
    def __init__(self, network:bool, mix:bool) -> None:
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

        Returns
        -------
        None.
        """
        self.network = network
        self.mix = mix
        self.order_requests = list()
    # -------------------------------------------------------------------------------  
    
    def read_file(self, file_name:str) -> None:
        """
        전략파일을 읽어 Request 객체를 생성하여 전달한다.
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
        file = pathlib.Path(os.getcwd()+'/strategyFile/'+file_name)
        
        try:
            text = file.read_text(encoding='utf-8')
        except FileNotFoundError:
            self._print_error(2)
            return

        js = json.loads(text)
        df = pd.DataFrame(js)

        for i in df.index:
            self.order_requests.append(Request(self.network))
            self.order_requests[i].set_request(df.loc[i])

    def read_df(self, df:"DataFrame") -> None:
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
            self.order_requests.append(Request(self.network))
            self.order_requests[i].set_request(df.loc[i])

    def _write_order(self, request:"Sereis") -> None:
        """
        trade_list를 이용하여 Order.json으로 저장한다.
        
        Parameters
        ----------
        request:
            Request 객체
            Request 객체에 저장된 DataFrame을 이용하기 위함

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

        result_df = result_df.sort_values(by=['order_datetime']) # 날짜에 대해 정렬
        
        adict = result_df.to_dict(orient='records')
        
        if not adict:
            self._print_error(1)
            return
        
        # order json file 생성
        cwd = os.getcwd()
        os.makedirs(cwd+'/orderFile', exist_ok=True)

        if self.mix:
            with open(cwd+'/orderFile/'+request.stock_df['item_name'][0]+'_mix_Order.json', 'w+', encoding='utf-8') as make_file:
                    json.dump(adict, make_file, ensure_ascii=False, indent='\t')

        else:
            if request.interval.upper() == 'D':
                with open(cwd+'/orderFile/'+request.stock_df['item_name'][0]+'_d_Order.json', 'w+', encoding='utf-8') as make_file:
                    json.dump(adict, make_file, ensure_ascii=False, indent='\t')

            elif request.interval.upper() == 'W':
                with open(cwd+'/orderFile/'+request.stock_df['item_name'][0]+'_w_Order.json', 'w+', encoding='utf-8') as make_file:
                    json.dump(adict, make_file, ensure_ascii=False, indent='\t')

    def make_order(self) -> None:
        """
        Request 객체에 담긴 데이터를 이용하여 주문파일을 생성한다.
        
        Parameters
        ----------        
        
        Returns
        -------
        None.
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
                        replace('sell(', 'self._sell(trade, inner_idx, request.stock_df, ').\
                        replace('buy(', 'self._buy(trade, inner_idx, request.stock_df, ')

            if strategy in 'crossDown' or 'crossUp':
                strategy = strategy.\
                            replace('crossDown(', 'crossDown(trade, inner_idx, request.stock_df, ').\
                            replace('crossUp(', 'crossUp(trade, inner_idx, request.stock_df, ')

            return strategy


        '''
        추가사항
        사용자가 전략식 작성 시에 새로운 변수를 추가해서 사용할 수 있도록 수정
        dictionary type variable를 for loop 밖에서 선언하여 사용할 수 있도록
        그리고 전략식에서 add method로 변수를 추가하여 사용할 수 있도록 해야 함
        '''
        inner_variable = {} # 전략식에서 사용자가 사용할 변수를 담는 딕셔너리변수
        # ------------------------------------------------------------------------------------
        self.__trade_list = [] # 거래 정보를 저장하는 리스트

        for request in self.order_requests:
            for inner_idx, trade in request.stock_df.iterrows():
                exec(make_strategy(request.strategy)) # 전략식 수행
        # ------------------------------------------------------------------------------------
            if not self.mix:
                # 각각의 order를 생성해야함
                self._write_order(request)
                del self.__trade_list[:] # 리스트를 초기화하여 새로운 주문에 대해서 리스트를 받을 수 있게 함
        
        # 첫번째 Request 객체의 stock name으로 함
        if self.mix:
            self._write_order(self.order_requests['0'])

    def _buy(
        self,
        trade_row:"Series",
        idx:int,
        df:"DataFrame",
        stock:int or float or str='all',
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
        stock: stock option, default 'all'
            거래량을 정하는 옵션
            integer 일 땐 그 수만큼 종목을 매수
            float 일 땐 그 수를 %로 계산하여 보유 현금에 맞게 종목을 매수
            'all': 보유 현금으로 살 수 있는 최대로 매수
        position: {'Onclose', 'NextOpen'} default 'Onclose'
            거래 가격을 정하는 옵션
            'Onclose': 신호발생 종가로 신호발생 다음날 거래
            'Nextopen': 신호발생 다음날 시가로 신호발생 다음날 거래
        
        Returns
        -------
        None.
        """

        # 거래량 옵션
        if type(stock) is int:
            order_option = 'scnt'

        elif type(stock) is float:
            order_option = 'por'

        elif stock == 'all':
            order_option = 'all'

        # 거래가격 옵션
        if position == 'Onclose':
            trade_price = str(trade_row.close)
        
        elif position == 'Nextopen':
            trade_price = str(df.iloc[idx+1]['open'])

        '''주봉에 경우 일봉 가격데이터로 거래 가격을 생성하는지 아님 주봉 가격데이터로 거래 가격을 생성하는지  
        -> 일봉가격으로 생성하려면 일봉가격이 데이터프레임에 존재해야함'''
        # 다음날 거래하도록 하는 것이 아닌 다음인덱스(df에 존재하는 시간)에 거래하도록 함        
        try:
            result_date = df.iloc[idx+1]['Date']
        
        # 신호가 오늘 발생했을 때에는 df.iloc[idx+1]['Date'] 문장에 에러가 발생할 것임 idx+1에 해당하는 인덱스가 없기 때문        
        # 에러에 대한 처리를 해줘야 함 오늘 신호가 발생했을 때 
        # 즉, exception 발생 __enddate에 접근해서 + 1일 해주어야 함(토요일일 때는 월요일로)
        except IndexError:            
            buy_date = datetime.strptime(trade_row.Date, '%Y-%m-%d')
            result_date = buy_date + timedelta(days=1)
            
            # order_date가 토요일이면 월요일로 수정해야 함
            if result_date.weekday() == 5:
                result_date = result_date + timedelta(days=2)

            result_date = datetime.strftime(result_date, '%Y-%m-%d')        
       
        self.__trade_list.append([result_date,
                                'buy',
                                trade_row.item_code,
                                trade_row.item_name,
                                trade_price,
                                order_option,
                                str(stock)])

    def _sell(
        self,
        trade_row:"Series",
        idx:int,
        df:"DataFrame",
        stock:int or float or str='all',
        position:str='Onclose'
        ) -> None:
        """
        전략에 일치하는 시점에 데이터를 이용하여 거래 정보(매도)를 생성한다.
        
        Parameters
        ----------
        trade_row: row of DataFrame
            Series로 된 데이터프레임의 행
        idx: index of row
        df: Stock DataFrame
        stock: stock option, default 'all'
            거래량을 정하는 옵션
            integer 일 땐 그 수만큼 종목을 매도
            float 일 땐 그 수를 %로 계산하여 보유 현금에 맞게 종목을 매도
            'all': 보유 현금으로 살 수 있는 최대로 매도
        position: {'Onclose', 'NextOpen'} default 'Onclose'
            거래 가격을 정하는 옵션
            'Onclose': 신호발생 종가로 신호발생 다음날 거래
            'Nextopen': 신호발생 다음날 시가로 신호발생 다음날 거래
        
        Returns
        -------
        None.
        """            

        # 거래량 옵션
        if type(stock) is int:
            order_option = 'scnt'

        elif type(stock) is float:
            order_option = 'por'

        elif stock == 'all':
            order_option = 'all'
        
        # 거래가격 옵션
        if position == 'Onclose':
            trade_price = str(trade_row.close)
        
        elif position == 'Nextopen':
            trade_price = str(df.iloc[idx+1]['open'])            

        '''주봉에 경우 일봉 가격데이터로 거래 가격을 생성하는지 아님 주봉 가격데이터로 거래 가격을 생성하는지  
        -> 일봉가격으로 생성하려면 일봉가격이 데이터프레임에 존재해야함'''
        # 다음날 거래하도록 하는 것이 아닌 다음인덱스(df에 존재하는 시간)에 거래하도록 함        
        try:
            result_date = df.iloc[idx+1]['Date']
        
        # 신호가 오늘 발생했을 때에는 df.iloc[idx+1]['Date'] 문장에 에러가 발생할 것임 idx+1에 해당하는 인덱스가 없기 때문
        # 에러에 대한 처리를 해줘야 함 오늘 신호가 발생했을 때 + 1일 해주어야 함(토요일일 때는 월요일로)
        except IndexError:
            # order_date = enddate + 1일            
            sell_date = datetime.strptime(trade_row.Date, '%Y-%m-%d')
            result_date = sell_date + timedelta(days=1)

            # order_date가 토요일이면 월요일로 수정해야 함
            if result_date.weekday() == 5:
                result_date = result_date + timedelta(days=2)

            result_date = datetime.strftime(result_date, '%Y-%m-%d')
        
        self.__trade_list.append([result_date,
                                'sell',
                                trade_row.item_code,
                                trade_row.item_name,
                                trade_price,
                                order_option,
                                str(stock)])

    def _print_error(self, erc:int) -> None:
        """        
        Parameters
        ----------
        erc : TYPE
            DESCRIPTION.

        Returns
        -------
        None.
        
        error code 1 -> 전략에 맞는 거래 시점이 존재하지 않음.
        error code 2 -> 전략 파일이 존재하지 않습니다.
        error code
        """        
        error = {1 : '전략에 맞는 주문이 생성되지 않았습니다.',
                2 : '전략파일이 존재하지 않습니다.'}
    
        print('OrderCreator error code {} : {}'.format(erc, error[erc]))

if __name__ == "__main__":

    mod = OrderCreator(network=True, mix=False)
    mod.read_file('DS_strategy_ver3_test.json')
    mod.make_order()

    # call graph를 그리기 위함
    # with PyCallGraph(output=GraphvizOutput()):
    #     mod.make_order()