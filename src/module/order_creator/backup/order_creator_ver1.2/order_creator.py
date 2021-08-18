# 내부 모듈
import gathering
from indicator import *
from stock_signal import *

# 외부 라이브러리
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import re
from itertools import chain

# call graph를 그리기 위한 모듈
# from pycallgraph import PyCallGraph
# from pycallgraph.output import GraphvizOutput

"""
autor: 김상혁
"""

class OrderCreator(gathering.Gathering):
    '''
    log
    2020.7.20 시작, 2020.8.4 수정: json파일에 키의 값들을 추출한다.,
    2020.08.20 수정: 입력날짜에 기술적지표값이 모두 출력하기 위해 이평기간을 이전 기간을 생성
    2020.08.21 수정: technical value에 parameter값을 paramitors에 저장
    func: 읽은 파일에서 전략을 적용하기 위해 필요한 데이터를 정제한다.
    parameter: 파일의 내용의 데이터 프레임
    주가정보를 생성하기 위한 데이터(주가코드, 시작날짜, 끝날짜, 데이터타입), 기술적 지표 값(시그널), 전략의 리스트
    return: 없음
    '''
    def extract(self, df):
        # json파일에서 읽은 입력정보를 멤버변수에 리스트로 저장
        self._stockcode = list(df['stockcode'])
        self._startdate = list(df['startdate'])
        self._enddate = list(df['enddate'])
        self._datetype = list(df['datetype'])
        self._technical_value = list(df['indicator'])
        self._strategy = list(df['strategy'])

        # 사용자가 입력한 기간에 기술적지표값을 모두 생성하기 위해(이평값을 사용하면 빠지는 값이 발생한다.)
        # 원래 입력한 날짜보다 이전 기간에 날짜를 저장하기 위한 멤버변수
        self._tech_date = list(df['startdate'].map(lambda x: datetime.strptime(x, '%Y-%m-%d').date()))
        self._paramitors = []        

        def to_int(x):
            try:
                if float(x).is_integer():
                    return int(x)
                else:
                    return float(x)
            except:
                pass

        # 기술적 지표생성 parameter중에서 이평 기간이 가장 긴것을 찾아서 그것보다 7일 더 여유를 둔 날짜를 생성한다.
        for idx, tech_value in enumerate(self._technical_value):
            # tech_value에 parameter중에서 기간(period)을 추출
            value_list = list(map(lambda x: re.split('period=|,|\)', x), tech_value)) # tech_value 문자열을 {period= , )}문자를 기준으로 나눈다.
            value_list = list(chain.from_iterable(value_list)) # 다중 리스트를 하나의 리스트로 변환한다.
            preiod_list = [to_int(x) for x in value_list if to_int(x) is not None] # 문자열중에서 int로 변환가능한 것을 변환한다. None은 리스트에서 제외
    
            # tech_value에 parameter 값들을 추출
            paramitor_list = list(map(lambda x: re.split('=', x), value_list)) # value_list 문자열을 =문자를 기준으로 나눈다. 
            paramitor_list = list(chain.from_iterable(paramitor_list)) # 다중 리스트를 하나의 리스트로 변환한다.
            self._paramitors.append([str(to_int(x)) for x in paramitor_list if to_int(x) is not None]) # 문자열중에서 int로 변환가능한 것을 변환한다.

            # print(max(preiod_list))
            # datetype에 맞게 tech_date를 생성한다. 뒤로 미룰날짜가 일봉과 주봉이 다르기 때문이다.
            if self._datetype[idx] == 'D' or self._datetype[idx] == 'd':
                self._tech_date[idx] = self._tech_date[idx] - relativedelta(days=max(preiod_list)+25)
            
            elif self._datetype[idx] == 'W' or self._datetype[idx] == 'w':
                self._tech_date[idx] = self._tech_date[idx] - relativedelta(weeks=max(preiod_list)+15)   
        
        self._tech_date = list(map(lambda date: date.strftime('%Y-%m-%d'), self._tech_date))

        # print(self._stockcode)
        # print(self._startdate)
        # print(self._tech_date)
        # print(self._enddate)
        
        # print(self._datetype, end='\n\n')
        # print(self._technical_value, end='\n\n')
        # print(self._strategy)

    '''
    log: 2020.7.20 시작, 2020.8.4 수정: Gathering을 상속받아 get_stock을 오버라이딩한다.
    func: 주가데이터프레임을 생성하고 해당 주가의 코드와 이름을 데이터프레임에 추가한다.
    parameter: 없음
    return: 없음
    '''
    def _get_stock(self):
        self._df_list=[]

        df_krx = fdr.StockListing('KRX')
        for i in range(len(self._stockcode)):       
            df = super().get_stock(self._stockcode[i], self._tech_date[i], self._enddate[i], self._datetype[i])
            
            try:
                if df == 1:
                    self.print_error(1)                                       

                elif df == 2:
                    self.print_error(2)                   
                                
            # 데이터프레임과 정수를 비교할 때 에러가 발생했다는 것은 데이터프레임 정상적으로 생성됬다는 의미
            except ValueError: 
                try:
                    name = df_krx.loc[df_krx.Symbol == self._stockcode[i], 'Name'].values[0] # 주가 코드에 해당하는 이름을 찾음
                    # 주가 데이터프레임에 주가 코드, 이름을 추가
                    df['item_code'] = self._stockcode[i]
                    df['item_name'] = name

                    self._df_list.append(df)

                # 외국 주식에 경우 한국 거래소에서 이름을 찾지 못하기 때문에 주가코드를 이름으로 넣어줌
                except :
                    # 주가 데이터프레임에 주가 코드, 이름을 추가
                    df['item_code'] = self._stockcode[i]
                    df['item_name'] = self._stockcode[i]

                    self._df_list.append(df)            

    '''
    log: 
    2020.7.22 시작, 2020.8.4 수정: OrderCreator의 멤버변수를 이용하여 기술적지표값(시그널)을 데이터프레임에 추가, 8.13 수정: 주가의 결측값을 제거
    2020.08.20 수정: tech_date로 생성한 데이터프레임을 다시 사용자가 입력한 날짜로 슬라이싱
    func: OrderCreator의 멤버변수를 이용하여 기술적지표값(시그널)을 데이터프레임에 추가
    parameter: 없음
    return: 없음 '''
    def _add_indicator(self):
        for i in range(len(self._technical_value)):
            for j in range(len(self._technical_value[i])):
                tech_df = eval(self._technical_value[i][j].replace('(', '(self._df_list[i],'))
                
            self._df_list[i] = self._df_list[i].loc[self._startdate[i]:]           

            # self._df_list[i].to_csv(self._stockcode[i]+'_'+datetime.now().strftime('%y-%m-%d,%H.%M.%S')+'.csv', encoding='cp949') 

        # print(self._df_list[0])
        # print(self._df_list[1])

    '''
    log: 2020.7.22 시작, 2021.1.11 수정: 전략식에 맞게 문자열을 변환
    func: 전략이 만족할 때 buy(sell)함수를 호출하고 그 정보를 json파일로 생성한다.
    parameter: 없음
    return: 없음'''
    def make_order(self):
        
        def make_strategy(strategy):
            '''
            strategy를 확인하여 수정할 내용을 수정해서 return한다.
            수정1. sell, buy함수 인자로 trade 추가
            수정2. crossUp, Down함수 인자로 trade, inner_idx, trade_df 추가
            '''            
            strategy = strategy.replace('sell(', 'self._sell(trade, inner_idx, trade_df, ').replace('buy(', 'self._buy(trade, inner_idx, trade_df, ')

            if strategy in 'crossDown' or 'crossUp':
                strategy = strategy.replace('crossDown(', 'crossDown(trade, inner_idx, trade_df, ').replace('crossUp(', 'crossUp(trade, inner_idx, trade_df, ')

            return strategy

        
        # 예외가 발생되면 동작을 멈춰야함        
        try:
            self._get_stock() # 주가데이터 생성
            if not self._df_list:
                raise # _df_list가 비었다는 것은 정상적인 동작이 이뤄지지 않았다는 것이므로 에러를 발생

            self._add_indicator() # 주가데이터에 기술적지표 값(시그널)을 추가

        except:
            return

        
        self.trade_list = [] # 거래 정보를 저장하는 리스트

        # ------------------------------------------------------------------------------------------------------------------------
        '''
        수정사항
        사용자가 전략식 작성 시에 새로운 변수를 추가해서 사용할 수 있도록 수정
        dictionary type variable를 for loop 밖에서 선언하여 사용할 수 있도록
        그리고 전략식에서 add method로 변수를 추가하여 사용할 수 있도록 해야 함
        '''
        # ------------------------------------------------------------------------------------------------------------------------
        for idx, trade_df in enumerate(self._df_list):
            trade_df = trade_df.reset_index() # 날짜데이터가 인덱스이므로 컬럼으로 바꿈
            trade_df['Date'] = trade_df['Date'].apply(lambda x: x.strftime('%Y-%m-%d')) # json파일에서 datetime형식은 깨지므로 문자열로 변환

            for inner_idx, trade in trade_df.iterrows():
                for i in range(len(self._strategy[idx])): # 전략의 수에 따라서 loop를 실행                 
                    exec(make_strategy(self._strategy[idx][i])) # 전략식 수행
        
            # 리스트를 데이터프레임로 변환
            result_df = pd.DataFrame(self.trade_list, columns=['order_datetime', 'order_type', 'item_code', 'item_name',
                                                            'order_price', 'order_option', 'order_value'])

            # result_df = result_df.sort_values(by=['order_datetime']) # 날짜에 대해 정렬

            # json파일로 변환과정
            adict = result_df.to_dict(orient='records')
            
            # 전략에 맞는 주문이 없을 경우 빈 디렉토리가 생성되는데 그때 적절한 에러 메시지를 출력
            if not adict:
                print('*********전략에 맞는 주문이 생성되지 않았습니다.**********')
                continue
            
            # order json file 생성
            # json 파일명 형식: 생성된 시간 + datetype
            if self._datetype[idx].upper() == 'D':
                cwd = os.getcwd()
                with open(cwd+'/order_creator/order_file/'+self._df_list[idx]['item_code'][0]+'_'+datetime.now().strftime('%y_%m_%d,%H_%M_%S')+'_daily.json', 'w+', encoding='utf-8') as make_file:
                            json.dump(adict, make_file, ensure_ascii=False, indent='\t')           

            elif self._datetype[idx].upper() == 'W':
                cwd = os.getcwd()
                with open(cwd+'/order_creator/order_file/'+self._df_list[idx]['item_code'][0]+'_'+datetime.now().strftime('%y_%m_%d,%H_%M_%S')+'_weekly.json', 'w+', encoding='utf-8') as make_file:
                            json.dump(adict, make_file, ensure_ascii=False, indent='\t')
    
            del self.trade_list[:] # 리스트를 초기화하여 새로운 주문에 대해서 리스트를 받을 수 있게 함

        # 전략에 맞는 주문이 있어 데이터 프레임이 생성되어야 출력되도록 함
        if not result_df.empty:
            print(result_df)
            # result_df.to_csv('FAS/order_creator/order.csv', encoding='cp949', index=False)


    '''
    log
    2020.7.22 시작
    수정:
    2021.01.12: stock의 형태에 따라서 order_option을 변경
    2021.01.18: position - 주문가격을 선택할 수 있는 옵션 추가
    func: 입력한 데이터프레임의 행과 주식의 수, 코드정보를 필요한 정보만 정제해서 리스트로 만든다.
    parameter: row of dataframe, index of row, dataframe, 거래할 주식의 수, 주문가격선택
    return: 정제한(날짜, 거래종류, 주가코드, 주가이름, 거래가격, 거래할 주식의 수(또는 전쳬)) 리스트 '''
    def _buy(self, trade_row, idx, df, stock='all', position='Onclose'):
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

        
        # 다음날 거래하도록 하는 것이 아닌 다음인덱스(df에 존재하는 시간)에 거래하도록 함
        '''주봉에 경우 일봉 가격데이터로 거래 가격을 생성하는지 아님 주봉 가격데이터로 거래 가격을 생성하는지  '''
        # -------------------------------------------------------------------------------------------------------------------------------------------------
        # 신호가 오늘 발생했을 때에는 df.iloc[idx+1]['Date'] 문장에 에러가 발생할 것임 idx+1에 해당하는 인덱스가 없기 때문        
        try:
            result_date = df.iloc[idx+1]['Date']
        
        # 에러에 대한 처리를 해줘야 함 오늘 신호가 발생했을 때 즉, exception 발생 _enddate에 접근해서 + 1일 해주어야 함(토요일일 때는 월요일로)
        except IndexError:
            # order_date = enddate + 1일
            # order_date가 토요일이면 월요일로 수정해야 함
            buy_date = datetime.strptime(trade_row.Date, '%Y-%m-%d')
            result_date = buy_date + timedelta(days=1)
            
            if result_date.weekday() == 5:
                result_date = result_date + timedelta(days=2)

            result_date = datetime.strftime(result_date, '%Y-%m-%d')
            
        # -------------------------------------------------------------------------------------------------------------------------------------------------
       
        self.trade_list.append([result_date, 'buy', trade_row.item_code, trade_row.item_name, trade_price, order_option, str(stock)])


    '''
    log
    2020.7.22 시작
    수정:
    2020.08.12, stock의 형태에 따라서 order_option을 변경
    2021.01.18: position - 주문가격을 선택할 수 있는 옵션 추가
    func: 입력한 데이터프레임의 행과 주식의 수, 코드정보를 필요한 정보만 정제해서 리스트로 만든다.
    parameter: row of dataframe, index of row, dataframe, 거래할 주식의 수, 주문가격선택
    return: 정제한(날짜, 거래종류, 주가코드, 주가이름, 거래가격, 거래할 주식의 수(또는 전쳬)) 리스트 '''
    def _sell(self,trade_row, idx, df, stock='all', position='Onclose'):
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
            

        # 다음날 거래하도록 하는 것이 아닌 다음인덱스(df에 존재하는 시간)에 거래하도록 함
        '''주봉에 경우 일봉 가격데이터로 거래 가격을 생성하는지 아님 주봉 가격데이터로 거래 가격을 생성하는지  '''
        # -------------------------------------------------------------------------------------------------------------------------------------------------
        # 신호가 오늘 발생했을 때에는 df.iloc[idx+1]['Date'] 문장에 에러가 발생할 것임 idx+1에 해당하는 인덱스가 없기 때문
        try:
            result_date = df.iloc[idx+1]['Date']
        
        # 에러에 대한 처리를 해줘야 함 오늘 신호가 발생했을 때 즉, exception 발생 _enddate에 접근해서 + 1일 해주어야 함(토요일일 때는 월요일로)
        except IndexError:
            # order_date = enddate + 1일
            # order_date가 토요일이면 월요일로 수정해야 함
            sell_date = datetime.strptime(trade_row.Date, '%Y-%m-%d')
            result_date = sell_date + timedelta(days=1)
        
            if result_date.weekday() == 5:
                result_date = result_date + timedelta(days=2)

            result_date = datetime.strftime(result_date, '%Y-%m-%d')
            
        # -------------------------------------------------------------------------------------------------------------------------------------------------
        
        self.trade_list.append([result_date, 'sell', trade_row.item_code, trade_row.item_name, trade_price, order_option, str(stock)])

    '''    
    log: start. 2021.1.18
    func: 클래스 멤버 함수에서 발생된 에러코드에 대한 에러 메시지를 출력한다.
    parameter: error code
    return: None    '''
    def print_error(self, erc):
        super().print_error(erc)
        # error = {1 : '***기간을 다시 입력해 주세요***',
        #         2 : '***지원하지 않는 inverval입니다. d(일봉) 또는 w(주봉)을 입력해주세요***'}
    
        # print('error code {} : {}'.format(erc, error[erc]))



if __name__ == "__main__":
    import os
    import pathlib
    import json

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------
    """ 여러 종목에 대한 실행
    test_list = [
        'IXIC', 'DJI', 'US500', 'VIX', # 미국 주가지수
        'IBM', 'MSFT', 'AAPL', 'MCD', 'AMZN', 'NKE', 'MMM', 'SBUX', 'NVDA', 'FB', 'GOOGL', 'KO', 'BAC', # 미국 주가코드
        'KS11', 'KS50', 'KS100', 'KQ11', 'KQ100', # 한국 주가지수
        '000660', '019170', '005930', '005380', '006120', '000150', '017670', '004370', '007310', '000120', '003230', '000060' # 한국 주가코드
    ]

    cwd = os.getcwd()
    file = pathlib.Path(cwd+'/order_creator/strategy_file/DS_strategy_test.json')
    text = file.read_text()
    js = json.loads(text)
    strategy_df = pd.DataFrame(js)

    mod = OrderCreator()
    mod.extract(strategy_df)

    # for code in test_list:
    #     strategy_df['stockcode'] = code     

    #     mod.extract(strategy_df)

    #     mod.make_order()
    """
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------
    cwd = os.getcwd()
    file = pathlib.Path(cwd+'/order_creator/strategy_file/DS_strategy_ver2.json')
     
    text = file.read_text()
    js = json.loads(text)
    strategy_df = pd.DataFrame(js)

    # print(strategy_df)

    mod = OrderCreator()
    mod.extract(strategy_df)    
    mod.make_order()    
        
    # call graph를 그리기 위함
    # with PyCallGraph(output=GraphvizOutput()):
    #     mod.make_order()