# 내부 모듈
import gathering
from tech_value import *

# 외부 라이브러리
import pandas as pd
import pathlib
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import re
from itertools import chain
import os

# call graph를 그리기 위한 모듈
# from pycallgraph import PyCallGraph
# from pycallgraph.output import GraphvizOutput

class OrderCreator(gathering.Gathering):
    '''
    로그
    2020.7.20 시작, 2020.8.4 수정: json파일에 키의 값들을 추출한다.,
    2020.08.20 수정: 입력날짜에 기술적지표값이 모두 출력하기 위해 이평기간을 이전 기간을 생성
    2020.08.21 수정: technical value에 파라미터값을 paramitors에 저장
    파라미터: 파일의 내용의 데이터 프레임
    기능: 읽은 파일에서 전략을 적용하기 위해 필요한 데이터를 정제한다.
    주가정보를 생성하기 위한 데이터(주가코드, 시작날짜, 끝날짜, 데이터타입), 기술적 지표 값(시그널), 전략의 리스트
    리턴: 없음
    '''
    def extract(self, df):
        self.stockcode = list(df['stockcode'])
        self.startdate = list(df['startdate'])
        self.enddate = list(df['enddate'])
        self.datetype = list(df['datetype'])
        self.technical_value = list(df['technical value'])
        self.strategy = list(df['strategy'])

        # 사용자가 입력한 기간에 기술적지표값을 모두 생성하기 위해(이평값을 사용하면 빠지는 값이 발생한다.)
        # 원래 입력한 날짜보다 이전 기간에 날짜를 저장하기 위한 멤버변수
        self.tech_date = list(df['startdate'].map(lambda x: datetime.strptime(x, '%Y-%m-%d').date()))
        self.paramitors = []        

        def to_int(x):
            try:
                if float(x).is_integer():
                    return int(x)
                else:
                    return float(x)
            except:
                pass

        # 기술적 지표생성 파라미터중에서 이평 기간이 가장 긴것을 찾아서 그것보다 7일 더 여유를 둔 날짜를 생성한다.
        for idx, tech_value in enumerate(self.technical_value):
            # tech_value에 파라미터중에서 기간(period)을 추출
            value_list = list(map(lambda x: re.split('period=|,|\)', x), tech_value)) # tech_value 문자열을 {period= , )}문자를 기준으로 나눈다.
            value_list = list(chain.from_iterable(value_list)) # 다중 리스트를 하나의 리스트로 변환한다.
            preiod_list = [to_int(x) for x in value_list if to_int(x) is not None] # 문자열중에서 int로 변환가능한 것을 변환한다. None은 리스트에서 제외
    
            # tech_value에 파라미터 값들을 추출
            paramitor_list = list(map(lambda x: re.split('=', x), value_list)) # value_list 문자열을 =문자를 기준으로 나눈다. 
            paramitor_list = list(chain.from_iterable(paramitor_list)) # 다중 리스트를 하나의 리스트로 변환한다.
            self.paramitors.append([str(to_int(x)) for x in paramitor_list if to_int(x) is not None]) # 문자열중에서 int로 변환가능한 것을 변환한다.

            # print(max(preiod_list))
            # datetype에 맞게 tech_date를 생성한다. 뒤로 미룰날짜가 일봉과 주봉이 다르기 때문이다.
            if self.datetype[idx] == 'D':
                self.tech_date[idx] = self.tech_date[idx] - relativedelta(days=max(preiod_list)+25)
            
            elif self.datetype[idx] == 'W':
                self.tech_date[idx] = self.tech_date[idx] - relativedelta(weeks=max(preiod_list)+15)   
        
        self.tech_date = list(map(lambda date: date.strftime('%Y-%m-%d'), self.tech_date))

        # print(self.stockcode)
        # print(self.startdate)
        # print(self.tech_date)
        # print(self.enddate)
        
        # print(self.datetype); print()
        # print(self.technical_value); print()
        # print(self.strategy)

    '''
    로그: 2020.7.20 시작, 2020.8.4 수정: Gathering을 상속받아 get_stock을 오버라이딩한다.
    파라미터: 없음
    기능: 주가데이터프레임을 생성하고 해당 주가의 코드와 이름을 데이터프레임에 추가한다.
    리턴: 없음
    '''
    def get_stock(self):
        self.df_list=[]

        df_krx = gathering.fdr.StockListing('KRX')
        for i in range(len(self.stockcode)):       
            df = super().get_stock(self.stockcode[i], self.tech_date[i], self.enddate[i], self.datetype[i])
            # print(df)
            
            try:
                name = df_krx.loc[df_krx.Symbol == self.stockcode[i], 'Name'].values[0] # 주가 코드에 해당하는 이름을 찾음
                # 주가 데이터프레임에 주가 코드, 이름을 추가
                df['item_code'] = self.stockcode[i]
                df['item_name'] = name

                self.df_list.append(df)
            
            # 외국 주식에 경우 한국 거래소에서 이름을 찾지 못하기 때문에 주가코드를 이름으로 넣어줌
            except:
                # 주가 데이터프레임에 주가 코드, 이름을 추가
                df['item_code'] = self.stockcode[i]
                df['item_name'] = self.stockcode[i]

                self.df_list.append(df)

            # print(self.df_list[i])

    '''
    로그: 
    2020.7.22 시작, 2020.8.4 수정: OrderCreator의 멤버변수를 이용하여 기술적지표값(시그널)을 데이터프레임에 추가, 8.13 수정: 주가의 결측값을 제거
    2020.08.20 수정: tech_date로 생성한 데이터프레임을 다시 사용자가 입력한 날짜로 슬라이싱
    파라미터: 없음
    기능: OrderCreator의 멤버변수를 이용하여 기술적지표값(시그널)을 데이터프레임에 추가
    리턴: 없음 '''
    def add_indicator(self):
        for i in range(len(self.technical_value)):
            for j in range(len(self.technical_value[i])):
                tech_df = eval('create_' + self.technical_value[i][j].replace('(', '(self.df_list[i],'))
                self.df_list[i] = gathering.merge_all_df(self.df_list[i], tech_df)

                # 데이터가 open, high, low 값이 0인경우 행을 제거한다.
                self.df_list[i].drop_duplicates(subset=['open', 'high', 'low'], keep=False, inplace=True)

            self.df_list[i] = self.df_list[i].loc[self.startdate[i]:]           

            # print(self.df_list[0])
            # self.df_list[i].to_csv(self.stockcode[i]+'_'+datetime.now().strftime('%y-%m-%d,%H.%M.%S')+'.csv', encoding='cp949') 

    '''
    로그: 2020.7.22 시작, 2020.8.4 수정: exec함수로 전략과 주문이 한번에 동작되도록 변경함
    파라미터: 없음
    기능: 전략이 만족할 때 buy(sell)함수를 호출하고 그 정보를 json파일로 생성한다.
    리턴: 없음'''
    def make_order(self):
        self.get_stock() # 주가데이터 생성
        self.add_indicator() # 주가데이터에 기술적지표 값(시그널)을 추가

        self.trade_list = []
        for idx, trade_df in enumerate(self.df_list):
            trade_df = trade_df.reset_index() # 날짜데이터가 인덱스이므로 컬럼으로 바꿈
            trade_df['Date'] = trade_df['Date'].apply(lambda x: x.strftime('%Y-%m-%d')) # json파일에서 datetime형식은 깨지므로 문자열로 변환

            for _, trade in trade_df.iterrows():
                for i in range(len(self.strategy[idx])): # 전략의 수에 따라서 loop를 실행
                    exec(self.strategy[idx][i].replace('sell(', 'self.sell(trade,').replace('buy(', 'self.buy(trade,'))                    
        
            # 리스트를 데이터프레임로 변환
            result_df = pd.DataFrame(self.trade_list, columns=['order_datetime', 'order_type', 'item_code', 'item_name',
                                                            'order_price', 'order_option', 'order_value'])

            result_df = result_df.sort_values(by=['order_datetime']) # 날짜에 대해 정렬

            # json파일로 변환과정
            adict = result_df.to_dict(orient='records')
            
            # 전략에 맞는 주문이 없을 경우 빈 디렉토리가 생성되는데 그때 적절한 에러 메시지를 출력
            if not adict:
                print('*********전략에 맞는 주문이 생성되지 않았습니다.**********')
                continue
            
            if self.datetype[idx] == 'D':
                # with open('FAS/order_creator/result/'+self.df_list[idx]['item_code'][0]+'_'+datetime.now().strftime('%y-%m-%d,%H.%M.%S')+'_daily.json', 'w+', encoding='utf-8') as make_file:
                #             json.dump(adict, make_file, ensure_ascii=False, indent='\t')
                try:
                    new_dir = 'C:/Users/ksang/Dropbox (KPU-JJLEE)/LabData_Finance/order_daily/'+self.df_list[idx]['item_code'][0]+'_order_daily'
                    os.mkdir(new_dir)
                except FileExistsError:
                    pass

                path_dir = new_dir+'/'
                if idx == 0:                    
                    with open(path_dir+self.df_list[idx]['item_code'][0]+'_bb_'+
                    self.paramitors[idx][0]+'_'+self.paramitors[idx][1]+'_'+self.paramitors[idx][2]+'_'+self.paramitors[idx][3]+'_'+self.paramitors[idx][4]+'_'+self.paramitors[idx][5]+
                    '_D.json', 'w+', encoding='utf-8') as make_file:
                        json.dump(adict, make_file, ensure_ascii=False, indent='\t')

                elif idx == 1:
                    with open(path_dir+self.df_list[idx]['item_code'][0]+'_bb_'+
                    self.paramitors[idx][0]+'_'+self.paramitors[idx][1]+'_'+self.paramitors[idx][2]+'_'+self.paramitors[idx][3]+'_'+self.paramitors[idx][4]+'_'+self.paramitors[idx][5]+
                    '_macd_'+self.paramitors[idx][6]+'_'+self.paramitors[idx][7]+'_'+self.paramitors[idx][8]+
                    '_D.json', 'w+', encoding='utf-8') as make_file:
                        json.dump(adict, make_file, ensure_ascii=False, indent='\t')

                elif idx == 2:
                    with open(path_dir+self.df_list[idx]['item_code'][0]+'_bb_'+
                    self.paramitors[idx][0]+'_'+self.paramitors[idx][1]+'_'+self.paramitors[idx][2]+'_'+self.paramitors[idx][3]+'_'+self.paramitors[idx][4]+'_'+self.paramitors[idx][5]+
                    '_rsi_'+self.paramitors[idx][6]+
                    '_D.json', 'w+', encoding='utf-8') as make_file:
                        json.dump(adict, make_file, ensure_ascii=False, indent='\t')

            elif self.datetype[idx] == 'W':
                # with open('FAS/order_creator/result/'+self.df_list[idx]['item_code'][0]+'_'+datetime.now().strftime('%y-%m-%d,%H.%M.%S')+'_weekly.json', 'w+', encoding='utf-8') as make_file:
                #             json.dump(adict, make_file, ensure_ascii=False, indent='\t')
                try:
                    new_dir = 'C:/Users/ksang/Dropbox (KPU-JJLEE)/LabData_Finance/order_weekly/'+self.df_list[idx]['item_code'][0]+'_order_weekly'
                    os.mkdir(new_dir)
                except FileExistsError:
                    pass

                path_dir= new_dir+'/'
                if idx == 3:
                    with open(path_dir+self.df_list[idx]['item_code'][0]+'_bb_'+
                    self.paramitors[idx][0]+'_'+self.paramitors[idx][1]+'_'+self.paramitors[idx][2]+'_'+self.paramitors[idx][3]+'_'+self.paramitors[idx][4]+'_'+self.paramitors[idx][5]+
                    '_W.json', 'w+', encoding='utf-8') as make_file:
                        json.dump(adict, make_file, ensure_ascii=False, indent='\t')

                elif idx == 4:
                    with open(path_dir+self.df_list[idx]['item_code'][0]+'_bb_'+
                    self.paramitors[idx][0]+'_'+self.paramitors[idx][1]+'_'+self.paramitors[idx][2]+'_'+self.paramitors[idx][3]+'_'+self.paramitors[idx][4]+'_'+self.paramitors[idx][5]+
                    '_macd_'+self.paramitors[idx][6]+'_'+self.paramitors[idx][7]+'_'+self.paramitors[idx][8]+
                    '_W.json', 'w+', encoding='utf-8') as make_file:
                        json.dump(adict, make_file, ensure_ascii=False, indent='\t')

                elif idx == 5:
                    with open(path_dir+self.df_list[idx]['item_code'][0]+'_bb_'+
                    self.paramitors[idx][0]+'_'+self.paramitors[idx][1]+'_'+self.paramitors[idx][2]+'_'+self.paramitors[idx][3]+'_'+self.paramitors[idx][4]+'_'+self.paramitors[idx][5]+
                    '_rsi_'+self.paramitors[idx][6]+
                    '_W.json', 'w+', encoding='utf-8') as make_file:
                        json.dump(adict, make_file, ensure_ascii=False, indent='\t')
    
            del self.trade_list[:] # 리스트를 초기화하여 새로운 주문에 대해서 리스트를 받을 수 있게 함

        # 전략에 맞는 주문이 있어 데이터 프레임이 생성되어야 출력되도록 함
        if not result_df.empty:
            print(result_df)
            # result_df.to_csv('FAS/order_creator/order.csv', encoding='cp949', index=False)

    '''
    로그: 2020.7.22 시작, 수정: 2020.08.12, stock의 형태에 따라서 order_option을 변경
    파라미터: 주가데이터프레임의 행, 거래할 주식의 수
    기능: 입력한 데이터프레임의 행과 주식의 수, 코드정보를 필요한 정보만 정제해서 리스트로 만든다.
    리턴: 정제한(날짜, 거래종류, 주가코드, 주가이름, 거래가격, 거래할 주식의 수(또는 전쳬)) 리스트 '''
    def buy(self, trade_row, stock):
        if type(stock) is int:
            order_option = 'scnt'

        elif type(stock) is float:
            order_option = 'por'

        else:
            order_option = 'all'
        
        # 전략이 만족하는 날에 다음 날짜로 거래할 수 있도록 함
        # 만약 금요일에 전략이 만족하여 토요일이 될 경우 월요일로 변경해서 선택한다.
        buy_date = datetime.strptime(trade_row.Date, '%Y-%m-%d')
        result_date = buy_date + timedelta(days=1)
    
        if result_date.weekday() == 5:
            result_date = result_date + timedelta(days=2)

        self.trade_list.append([result_date.strftime('%Y-%m-%d'), 'buy', trade_row.item_code, trade_row.item_name, trade_row.close, order_option, str(stock)])

    '''
    로그: 2020.7.22 시작, 수정: 2020.08.12, stock의 형태에 따라서 order_option을 변경
    파라미터: 주가데이터프레임의 행, 거래할 주식의 수
    기능: 입력한 데이터프레임의 행과 주식의 수, 코드정보를 필요한 정보만 정제해서 리스트로 만든다.
    리턴: 정제한(날짜, 거래종류, 주가코드, 주가이름, 거래가격, 거래할 주식의 수(또는 전쳬)) 리스트 '''
    def sell(self, trade_row, stock):
        if type(stock) is int:
            order_option = 'scnt'

        elif type(stock) is float:
            order_option = 'por'

        else:
            order_option = 'all'

        # 전략이 만족하는 날에 다음 날짜로 거래할 수 있도록 함
        # 만약 금요일에 전략이 만족하여 토요일이 될 경우 월요일로 변경해서 선택한다.
        sell_date = datetime.strptime(trade_row.Date, '%Y-%m-%d')
        result_date = sell_date + timedelta(days=1)
    
        if result_date.weekday() == 5:
            result_date = result_date + timedelta(days=2)

        self.trade_list.append([result_date.strftime('%Y-%m-%d'), 'sell', trade_row.item_code, trade_row.item_name, trade_row.close, order_option, str(stock)])

if __name__ == "__main__":
    # file = pathlib.Path('user_file/strategy.json')
    test_list = [
        'IXIC', 'DJI', 'US500', 'VIX', # 미국 주가지수
        'IBM', 'MSFT', 'AAPL', 'MCD', 'AMZN', 'NKE', 'MMM', 'SBUX', 'NVDA', 'FB', 'GOOGL', 'KO', 'BAC', # 미국 주가코드
        'KS11', 'KS50', 'KS100', 'KQ11', 'KQ100', # 한국 주가지수
        '000660', '019170', '005930', '005380', '006120', '000150', '017670', '004370', '007310', '000120', '003230', '000060' # 한국 주가코드
    ]

    file = pathlib.Path('FAS/order_creator/user_file/strategy.json')
    text = file.read_text()
    js = json.loads(text)
    strategy_df = pd.DataFrame(js)

    mod = OrderCreator()
    mod.extract(strategy_df)

    # mod.make_order()

    for code in test_list:
        strategy_df['stockcode'] = code     

        mod.extract(strategy_df)

        mod.make_order()
        
    # call graph를 그리기 위함
    # with PyCallGraph(output=GraphvizOutput()):
    #     mod.make_order()