# 내부 모듈
import gatherer
from indicator import *
from checker import *

# 외부 라이브러리
import pandas as pd
import FinanceDataReader as fdr
import os
import re
import pathlib
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Order:
    def __init__(self, mode):
        self.mode = mode

    '''
    log
    2020.7.20 시작, 2020.8.4 수정: json파일에 키의 값들을 추출한다.,
    2020.08.20 수정: 입력날짜에 기술적지표값이 모두 출력하기 위해 이평기간을 이전 기간을 생성
    2020.08.21 수정: technical value에 parameter값을 paramitors에 저장
    func: 읽은 파일에서 전략을 적용하기 위해 필요한 데이터를 정제한다.
    parameter: series
    주가정보를 생성하기 위한 데이터(주가코드, 시작날짜, 끝날짜, 데이터타입), 기술적 지표 값(시그널), 전략의 리스트
    return: None
    '''
    def _extract(self, order_request:pd.Series) -> None:
        # json파일에서 읽은 입력정보를 멤버변수에 리스트로 저장
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
        
        if self.mode == 'network':
            period_list = []
            # 기술적 지표생성 parameter중에서 이평 기간이 가장 긴것을 찾아서 그것보다 7일 더 여유를 둔 날짜를 생성한다.
            for tech_indi in self.indicator:
                # tech_value에 parameter중에서 기간(period)을 추출
                tech_indi = re.split('period=|,|\)', tech_indi) # tech_indi 문자열을 {period= , )}문자를 기준으로 나눈다.
                tech_indi = [to_int(x) for x in tech_indi if to_int(x) is not None] # 문자열중에서 int로 변환가능한 것을 변환한다. None은 리스트에서 제외
                period_list.extend(tech_indi)
                # print(period_list) # period_list가 없으면 빈 리스트가 된다.

            # datetype에 맞게 tech_date를 생성한다. 뒤로 미룰날짜가 일봉과 주봉이 다르기 때문이다.
            if self.interval.upper() == 'D':
                self.__tech_date = self.__tech_date - relativedelta(days=max(period_list)+30)
            
            elif self.interval.upper() == 'W':
                self.__tech_date = self.__tech_date - relativedelta(weeks=max(period_list)+30)   

            self.__tech_date = datetime.strftime(self.__tech_date, '%Y-%m-%d')

    '''
    log
    satrt: 2020.7.20
    edit:
    2020.8.4: Gathering을 상속받아 get_stock을 오버라이딩한다.
    2021.01.20: 파라미터추가 local-> local file에서 주가데이터를 생성함, network-> fdr로 주가데이터를 생성함
    func: 주가데이터프레임을 생성하고 해당 주가의 코드와 이름을 데이터프레임에 추가한다.
    parameter: mode
    return: None
    '''
    def _get_stock(self) -> None:
        self.stock_df = None

        if self.mode == 'local':
            df_krx = fdr.StockListing('KRX')
            try:
                name = df_krx.loc[df_krx.Symbol == self.__stockcode, 'Name'].values[0] # 주가 코드에 해당하는 이름을 찾음

            except IndexError: # 외국주식 종목이름은 한국거래소에 등록되어있지 않으므로 code를 name에 저장함
                name = self.__stockcode

            finally:
                if not os.path.isfile(os.getcwd()+'/stockFile/'+name+'_'+self.interval+'.csv'):
                    self._print_error(1)                    
            
            df = pd.read_csv(os.getcwd()+'/stockFile/'+name+'_'+self.interval+'.csv', index_col='Date')
            self.stock_df = df
        
        elif self.mode == 'network':
            gather = gatherer.Gatherer()             
            df, name = gather.get_stock(self.__stockcode, self.__tech_date, self.__enddate, self.interval, save=False)
            self.stock_df = df

            try:
                if df == None:
                    # 에러 종류
                    # 기간이 시간 순서가 아님
                    # 지원하지 않는 interval
                    pass 
                                
            # 데이터프레임과 정수를 비교할 때 에러가 발생했다는 것은 데이터프레임 정상적으로 생성됬다는 의미
            except ValueError: 
                # stockname 멤버변수에 종목이름을 추가                    
                self.stock_df['item_code'] = self.__stockcode
                self.stock_df['item_name'] = name                        

                
    '''
    log: 
    2020.7.22 시작, 2020.8.4 수정: OrderCreator의 멤버변수를 이용하여 기술적지표값(시그널)을 데이터프레임에 추가, 8.13 수정: 주가의 결측값을 제거
    2020.08.20 수정: tech_date로 생성한 데이터프레임을 다시 사용자가 입력한 날짜로 슬라이싱
    func: OrderCreator의 멤버변수를 이용하여 기술적지표값(시그널)을 데이터프레임에 추가
    parameter: None
    return: None '''
    def _add_indicator(self) -> None:
        for indicator in self.indicator:
            eval('add_'+indicator.replace('(', '(self.stock_df,'))
        self.stock_df = self.stock_df.loc[self.__startdate:]


    def set_request(self, order_request:pd.Series) -> None:
        self._extract(order_request)

        # get_stock 또는 add_indicator 함수에서 예외가 발생되면 동작을 멈춰야함        
        try:
            self._get_stock() # 주가데이터 생성

            if self.mode == 'local':
                self.stock_df.reset_index(inplace=True)
            
            elif self.mode == 'network':
                self._add_indicator() # 주가데이터에 기술적지표 값(시그널)을 추가
                self.stock_df.reset_index(inplace=True)
                self.stock_df['Date'] = self.stock_df['Date'].apply(lambda x: x.strftime('%Y-%m-%d')) # json파일로 만들때 datetime형식은 깨지므로 문자열로 변환

        except:
            return

    '''    
    log: start. 2021.1.18
    func: 클래스 멤버 함수에서 발생된 에러코드에 대한 에러 메시지를 출력한다.
    parameter: error code
    return: None    '''
    def _print_error(self, erc:int) -> None:
        error = {1 : '종목폴더에 해당 종목 파일이 없습니다.'}
    
        print('class order error code {} : {}'.format(erc, error[erc]))        


class OrderCreator:
    def __init__(self, mode:str) -> None:
        self.mode = mode
        self.order_requests = {}
    
    def read_file(self, file_name:str) -> None:      
        cwd = os.getcwd()
        file = pathlib.Path(cwd+'/strategyFile/'+file_name)
        
        text = file.read_text()
        js = json.loads(text)
        df = pd.DataFrame(js)

        for i in df.index:
            self.order_requests['strategy_'+str(i)] = Order(self.mode)
            self.order_requests['strategy_'+str(i)].set_request(df.loc[i])  

    '''
    log
    start: 2020.7.22
    edit
    2021.1.11: 전략식에 맞게 문자열을 변환
    func: 전략이 만족할 때 buy(sell)함수를 호출하고 그 정보를 json파일로 생성한다.
    return: None'''
    def make_order(self) -> None:
        
        def make_strategy(strategy:str) -> str:
            '''
            strategy를 확인하여 수정할 내용을 수정해서 return한다.
            수정1. sell, buy함수 인자로 trade 추가
            수정2. crossUp, Down함수 인자로 trade, inner_idx, trade_df 추가
            '''            
            strategy = strategy.replace('sell(', 'self._sell(trade, inner_idx, self.order_requests[idx].stock_df, ').replace('buy(', 'self._buy(trade, inner_idx, self.order_requests[idx].stock_df, ')

            if strategy in 'crossDown' or 'crossUp':
                strategy = strategy.replace('crossDown(', 'crossDown(trade, inner_idx, self.order_requests[idx].stock_df, ').replace('crossUp(', 'crossUp(trade, inner_idx, self.order_requests[idx].stock_df, ')

            return strategy

        '''
        수정사항
        사용자가 전략식 작성 시에 새로운 변수를 추가해서 사용할 수 있도록 수정
        dictionary type variable를 for loop 밖에서 선언하여 사용할 수 있도록
        그리고 전략식에서 add method로 변수를 추가하여 사용할 수 있도록 해야 함
        '''

        inner_variable = {} # 전략식에서 사용자가 사용할 변수를 담는 딕셔너리변수

        # ------------------------------------------------------------------------------------------------------------------------
        self.__trade_list = [] # 거래 정보를 저장하는 리스트

        for idx in self.order_requests:
            for inner_idx, trade in self.order_requests[idx].stock_df.iterrows():
                exec(make_strategy(self.order_requests[idx].strategy)) # 전략식 수행

        # ------------------------------------------------------------------------------------------------------------------------
        
            # 리스트를 데이터프레임로 변환
            result_df = pd.DataFrame(self.__trade_list, 
                                    columns=['order_datetime', 'order_type', 'item_code', 'item_name', 'order_price', 'order_option', 'order_value'])

            # result_df = result_df.sort_values(by=['order_datetime']) # 날짜에 대해 정렬

            # json파일로 변환과정1. dataframe을 딕셔너리로 변환
            adict = result_df.to_dict(orient='records')
            
            # 전략에 맞는 주문이 없을 경우 빈 디렉토리가 생성되는데 그때 적절한 에러 메시지를 출력
            if not adict:
                print('*********전략에 맞는 주문이 생성되지 않았습니다.*********')
                continue
            
            # order json file 생성
            # json 파일명 형식: 생성된 시간 + datetype
            os.makedirs(os.getcwd()+'/orderFile', exist_ok=True)

            if self.order_requests[idx].interval.upper() == 'D':
                with open(os.getcwd()+'/orderFile/'+self.order_requests[idx].stock_df['item_name'][0]+'_d.json', 'w+', encoding='utf-8') as make_file:
                    json.dump(adict, make_file, ensure_ascii=False, indent='\t')           

            elif self.order_requests[idx].interval.upper() == 'W':
                with open(os.getcwd()+'/orderFile/'+self.order_requests[idx].stock_df['item_name'][0]+'_w.json', 'w+', encoding='utf-8') as make_file:
                    json.dump(adict, make_file, ensure_ascii=False, indent='\t')
    
            del self.__trade_list[:] # 리스트를 초기화하여 새로운 주문에 대해서 리스트를 받을 수 있게 함

        # 전략에 맞는 주문이 있어 데이터 프레임이 생성되어야 출력되도록 함
        if not result_df.empty:
            print(result_df)

    '''
    log
    2020.7.22 시작
    수정:
    2021.01.12: stock의 형태에 따라서 order_option을 변경
    2021.01.18: position - 주문가격을 선택할 수 있는 옵션 추가
    func: 입력한 데이터프레임의 행과 주식의 수, 코드정보를 필요한 정보만 정제해서 리스트로 만든다.
    parameter: row of dataframe, index of row, dataframe, 거래할 주식의 수, 주문가격선택
    return: 정제한(날짜, 거래종류, 주가코드, 주가이름, 거래가격, 거래할 주식의 수(또는 전쳬)) 리스트 '''
    def _buy(self, trade_row:pd.Series, idx:int, df:pd.DataFrame, stock:int or float or str='all', position:str='Onclose') -> None:
        if type(stock) is int:
            order_option = 'scnt'

        elif type(stock) is float:
            order_option = 'por'

        elif stock == 'all':
            order_option = 'all'

        ''' 가격선택을 위한 기능
        Onclose: '신호발생한 날의 종가'로 거래
        Nextopen: '신호발생한 날 그 다음날의 시가'로 거래    '''
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
        # 에러에 대한 처리를 해줘야 함 오늘 신호가 발생했을 때 즉, exception 발생 __enddate에 접근해서 + 1일 해주어야 함(토요일일 때는 월요일로)
        except IndexError:
            # order_date = enddate + 1일            
            buy_date = datetime.strptime(trade_row.Date, '%Y-%m-%d')
            result_date = buy_date + timedelta(days=1)
            
            # order_date가 토요일이면 월요일로 수정해야 함
            if result_date.weekday() == 5:
                result_date = result_date + timedelta(days=2)

            result_date = datetime.strftime(result_date, '%Y-%m-%d')        
       
        self.__trade_list.append([result_date, 'buy', trade_row.item_code, trade_row.item_name, trade_price, order_option, str(stock)])


    '''
    log
    2020.7.22 시작
    수정:
    2020.08.12, stock의 형태에 따라서 order_option을 변경
    2021.01.18: position - 주문가격을 선택할 수 있는 옵션 추가
    func: 입력한 데이터프레임의 행과 주식의 수, 코드정보를 필요한 정보만 정제해서 리스트로 만든다.
    parameter: row of dataframe, index of row, dataframe, 거래할 주식의 수, 주문가격선택
    return: 정제한(날짜, 거래종류, 주가코드, 주가이름, 거래가격, 거래할 주식의 수(또는 전쳬)) 리스트 '''
    def _sell(self, trade_row:pd.Series, idx:int, df:pd.DataFrame, stock:int or float or str='all', position:str='Onclose') -> None:
        if type(stock) is int:
            order_option = 'scnt'

        elif type(stock) is float:
            order_option = 'por'

        elif stock == 'all':
            order_option = 'all'

        ''' 가격선택을 위한 기능
        Onclose: '신호발생한 날의 종가'로 거래
        Nextopen: '신호발생한 날 그 다음날의 시가'로 거래
        '''
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
        # 에러에 대한 처리를 해줘야 함 오늘 신호가 발생했을 때 즉, exception 발생 __enddate에 접근해서 + 1일 해주어야 함(토요일일 때는 월요일로)
        except IndexError:
            # order_date = enddate + 1일            
            sell_date = datetime.strptime(trade_row.Date, '%Y-%m-%d')
            result_date = sell_date + timedelta(days=1)

            # order_date가 토요일이면 월요일로 수정해야 함
            if result_date.weekday() == 5:
                result_date = result_date + timedelta(days=2)

            result_date = datetime.strftime(result_date, '%Y-%m-%d')
        
        self.__trade_list.append([result_date, 'sell', trade_row.item_code, trade_row.item_name, trade_price, order_option, str(stock)])

if __name__ == "__main__":

    mod = OrderCreator('network')
    mod.read_file('DS_strategy_test.json')
    mod.make_order()

    # call graph를 그리기 위함
    # with PyCallGraph(output=GraphvizOutput()):
    #     mod.make_order()