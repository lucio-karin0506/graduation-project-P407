import os
import re
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import re
import FinanceDataReader as fdr

from module.gatherer.gatherer import Gatherer
from module.indicator.indicator import *
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
    def __init__(self, network:bool, root_path):
        """
        클래스 멤버변수를 초기화한다.
        
        Parameters
        ----------
        network: True, False
            주문생성 모드
            True일 땐 network를 이용하여 생성한다.
            False일 땐 Request 객체에 필요한 데이터를 생성할 때 local file로부터 생성한다.
        
        root_path

        Returns
        -------
        None.  
        """        
        self.network = network
        self.root_path = root_path
    # -------------------------------------------------------------------------------          

    def check_strategy(self):
        if self.strategy.find('moeny') > 0 and self.strategy.find('stock') > 0:
            self._print_error(2)
            return False
        else:
            return True

    def _extract(self, order_request:pd.Series) -> None:
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
        self.startdate = order_request['startdate']
        self.enddate = order_request['enddate']
        self.interval = order_request['interval']
        self.indicator = order_request['indicator']
        self.strategy = order_request['strategy']

        if self.check_strategy():
            pass
        else:
            return False

        # strategy에 money와 stock이 함께 쓰였는지 확인하는 함수 필요

        # 사용자가 입력한 기간에 기술적지표값을 모두 생성하기 위해(이평값을 사용하면 빠지는 값이 발생한다.)
        # 원래 입력한 날짜보다 이전 기간에 날짜를 저장하기 위한 멤버변수
        self.__tech_date = datetime.strptime(self.startdate, '%Y-%m-%d').date()     

        def check_date(x):
            try:    
                if float(x).is_integer():
                    self.check_d = ''
                    return int(x)
                else:
                    self.check_d = ''
                    return int(x)

            except ValueError:
                if x[-1].lower() == 'y':
                    self.check_d = 'y'
                    self.check_p = int(x[:-1])
                    
                elif x[-1].lower() == 'm':
                    if self.check_d == 'y':
                        pass
                    else:
                        self.check_d = 'm'
                        self.check_p = int(x[:-1])
                    
                elif x[-1].lower() == 'd':
                    if self.check_d == 'y':
                        pass
                    else:
                        self.check_d = 'd'
                        self.check_p = int(x[:-1])
                    
        
        # if self.network:
        #     period_list = []
        #     for tech_indi in self.indicator:
        #         # tech_value에 parameter중에서 기간(period)을 추출
        #         tech_indi = re.split('\=|period=|,|\(|\)', tech_indi) # tech_indi 문자열을 {period= , )}문자를 기준으로 나눈다.
        #         # 문자열중에서 int로 변환가능한 것을 변환한다. None은 리스트에서 제외
        #         tech_indi = [to_int(x) for x in tech_indi if to_int(x) is not None]
        #         period_list.extend(tech_indi)

        #     # datetype에 맞게 tech_date를 생성한다. 뒤로 미룰날짜가 일봉과 주봉이 다르기 때문이다.
        #     if self.interval.upper() == 'D':
        #         self.__tech_date = self.__tech_date - relativedelta(days=max(period_list)+30)
            
        #     elif self.interval.upper() == 'W':
        #         self.__tech_date = self.__tech_date - relativedelta(weeks=max(period_list)+30)

        #     self.__tech_date = datetime.strftime(self.__tech_date, '%Y-%m-%d')
        
        # if self.network:
        period_list = []
        for tech_indi in self.indicator:
            # tech_value에 parameter중에서 기간(period)을 추출
            p = re.compile('\d{1,3}[y|Y|m|M|d|D]*')
            # 문자열중에서 int로 변환가능한 것을 변환한다. None은 리스트에서 제외
            a = p.findall(tech_indi)
            # print(a)
            tech_indi = [check_date(x) for x in a if check_date(x) is not None]
            period_list.extend(tech_indi)

        if self.check_d == 'y':
            self.__tech_date = self.__tech_date - relativedelta(years=self.check_p)
        elif self.check_d == 'm':
            self.__tech_date = self.__tech_date - relativedelta(months=self.check_p)
        elif self.check_d == 'd':
            self.__tech_date = self.__tech_date - relativedelta(days=self.check_p)

        else:
            # datetype에 맞게 tech_date를 생성한다. 뒤로 미룰날짜가 일봉과 주봉이 다르기 때문이다.
            if self.interval.upper() == 'D':
                self.__tech_date = self.__tech_date - relativedelta(days=max(period_list)+30)
            
            elif self.interval.upper() == 'W':
                self.__tech_date = self.__tech_date - relativedelta(weeks=max(period_list)+30)

        self.__tech_date = datetime.strftime(self.__tech_date, '%Y-%m-%d')
        
        return True

    def _get_stock(self, stock_file) -> None:
        """
        초기화된 멤버변수를 이용하여 주가 가격데이터프레임을 생성한다.
        network 멤버변수를 확인하여 
        => True-> FinanceDataReader로 주가데이터를 생성함, False-> local file에서 주가데이터를 생성함
        
        Parameters
        ----------        

        Returns
        -------
        None.  
        """
        if self.network:
            gather = Gatherer(path=self.root_path)             
            df, name = gather.get_stock(self.__stockcode, 
                                        self.__tech_date,
                                        self.enddate,
                                        self.interval,
                                        save=False)
            
            if type(df) is pd.DataFrame:
                self.stock_df = df
            
            else:
                self._pring_error(3)
                return False

        else:            
            try:
                if os.path.isfile(f'{self.root_path}/stockFile/KRX.csv'):
                    krx_df = pd.read_csv(f'{self.root_path}/stockFile/KRX.csv')
                else:
                    krx_df = fdr.StockListing('KRX')
                name = krx_df.loc[krx_df.Symbol == self.__stockcode, 'Name'].values[0] # 주가 코드에 해당하는 이름을 찾음

            except IndexError or FileNotFoundError: # 외국주식 종목이름은 한국거래소에 등록되어있지 않으므로 code를 name에 저장함
                name = self.__stockcode

            finally:
                # if not os.path.isfile(os.getcwd()+'/stockFile/'+name+'_'+self.interval+'.csv'):
                if not os.path.isfile(stock_file):
                    self._print_error(1)
                    return False
            
            df = pd.read_csv(stock_file, index_col='Date')
            self.stock_df = df[self.__tech_date:self.enddate].copy()
    
        self.stock_df['item_code'] = self.__stockcode
        self.stock_df['item_name'] = name

        return True

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
            if indicator == "":
                continue
            else:
                eval('add_'+indicator.replace('(', '(self.stock_df,'))
        self.stock_df = self.stock_df.loc[self.startdate:]

    def set_request(self, order_request:pd.Series, stock_file=False) -> None:
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
        if self._extract(order_request):
            pass
        else:
            return False

        # get_stock 또는 add_indicator 함수에서 예외가 발생되면 동작을 멈춰야함        
        if self._get_stock(stock_file): # 주가데이터 생성
            self._add_indicator() # 주가데이터에 기술적지표 값(시그널)을 추가
            self.stock_df.reset_index(inplace=True)

            if self.network:                
                # json파일로 만들때 datetime형식은 깨지므로 문자열로 변환
                self.stock_df['Date'] = self.stock_df['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))

            else:                
                # self.stock_df.reset_index(inplace=True)
                pass
        else:
            return False

        return True

    def set_self(self,
                stockcode,
                df,
                startdate,
                enddate,
                interval,
                indicator,
                strategy):
        """
        주문생성에 필요한 정보를 직접 입력받아서 request 세팅을하는 함수
        
        Parameters        
        ----------
        order_request: row of DataFrame
            전략파일 객체에 담긴 데이터 Series

        Returns
        -------
        None.  
        """

        self.__stockcode = stockcode
        self.startdate = startdate
        self.enddate = enddate
        self.interval = interval
        self.indicator = indicator
        self.strategy = strategy
        self.stock_df = df
        try:
            krx_df=\
                pd.read_csv(self.root_path+'/stockFile/'+'KRX.csv', usecols=['Symbol', 'Market', 'Name'])

            name = krx_df.loc[krx_df.Symbol == self.__stockcode, 'Name'].values[0] # 주가 코드에 해당하는 이름을 찾음

        except IndexError or FileNotFoundError: # 외국주식 종목이름은 한국거래소에 등록되어있지 않으므로 code를 name에 저장함
            name = self.__stockcode

        self.stock_df['item_code'] = self.__stockcode
        self.stock_df['item_name'] = name


    def _print_error(self, erc:int) -> None:
        """        
        Parameters
        ----------
        erc : TYPE
            DESCRIPTION.

        Returns
        -------
        None.
        
        warning code 1 -> 종목폴더에 해당하는 종목 파일이 없음
        warning code 2 -> 거래 함수(sell, buy)에 stock과 money를 함께 사용할 수 없음.
        warning code 3 -> 종목코드에 일치하는 주가데이터 없음.
        warning code 4 ->
        warning code 5 ->
        """        
        error = {1 : '종목폴더에 해당 종목 파일이 없습니다.',
                2 : '거래 함수(sell, buy)에 stock과 money를 함께 사용할 수 없습니다.',
                3 : '종목코드에 일치하는 주가데이터가 존재하지 않습니다.'}
    
        print('Request warning code {} : {}'.format(erc, error[erc]))
