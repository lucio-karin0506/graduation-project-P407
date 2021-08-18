import gathering
from tech_value import *
import pandas as pd
import pathlib
import json
from datetime import datetime, timedelta
import os

class OrderCreator(gathering.Gathering):
    '''
    로그: 2020.7.20 시작, 2020.8.4 수정: json파일에 키의 값들을 추출한다.
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

        # print(self.stockcode)
        # print(self.startdate)
        # print(self.enddate)
        
        # print(self.datetype); print()
        # print(self.technical_value); print()
        # print(self.strategy)
        # print(self.strategy[0][0].replace('buy','self.buy').replace('(stock', '(trade, stock'))

    '''
    로그: 2020.7.20 시작, 2020.8.4 수정: Gathering을 상속받아 get_stock을 오버라이딩한다.
    파라미터: 없음
    기능: 주가데이터프레임을 생성하고 해당 주가의 코드와 이름을 데이터프레임에 추가한다.
    리턴: 없음
    '''
    def get_stock(self):
        self.df_list=[]

        df_krx = fdr.StockListing('KRX')
        for i in range(len(self.stockcode)):                        
            df = super().get_stock(self.stockcode[i], self.startdate[i], self.enddate[i], self.datetype[i]) 
            # print(df)
            
            try:
                name = df_krx.loc[df_krx.Symbol == self.stockcode[i], 'Name'].values[0] # 주가 코드에 해당하는 이름을 찾음
                # 주가 데이터프레임에 주가 코드, 이름을 추가
                df['item_code'] = self.stockcode[i]
                df['item_name'] = name

                self.df_list.append(df)
            
            except:
                # 주가 데이터프레임에 주가 코드, 이름을 추가
                df['item_code'] = self.stockcode[i]
                df['item_name'] = self.stockcode[i]

                self.df_list.append(df)

        # print(self.df_list[0])
        # self.df_list[0].to_csv('test_df', )

    '''
    로그: 
    2020.7.22 시작, 2020.8.4 수정: OrderCreator의 멤버변수를 이용하여 기술적지표값(시그널)을 데이터프레임에 추가, 8.13 수정 주가의 결측값을 제거
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

        # print(self.df_list[0])
            # self.df_list[i].to_csv(self.stockcode[i]+'trade_df.csv', encoding='cp949')


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
            adict = result_df.to_dict(orient='record')
            
            # 전략에 맞는 주문이 없을 경우 빈 디렉토리가 생성되는데 그때 적절한 에러 메시지를 출력
            if not adict:
                print('*********전략에 맞는 주문이 생성되지 않았습니다.**********')
                continue
            
            if self.datetype[idx] == 'D':
                with open('2020-파이썬분석팀/FAS/result/'+self.df_list[idx]['item_code'][0]+str(idx)+'_daily.json', 'w+', encoding='utf-8') as make_file:
                            json.dump(adict, make_file, ensure_ascii=False, indent='\t')

            elif self.datetype[idx] == 'W':
                with open('2020-파이썬분석팀/FAS/result/'+self.df_list[idx]['item_code'][0]+str(idx)+'_weekly.json', 'w+', encoding='utf-8') as make_file:
                            json.dump(adict, make_file, ensure_ascii=False, indent='\t')
    
            del self.trade_list[:] # 리스트를 초기화하여 새로운 주문에 대해서 리스트를 받을 수 있게 함

        # 전략에 맞는 주문이 있어 데이터 프레임이 생성되어야 출력되도록 함
        if not result_df.empty:
            print(result_df)
            # result_df.to_csv('order.csv', encoding='cp949', index=False)

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
        # return buy_list

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
        # return sell_list


if __name__ == "__main__":
    import time

    start = time.time()

    # file = pathlib.Path('user_file/strategy.json')
    file = pathlib.Path('2020-파이썬분석팀/FAS/user_file/strategy.json')
    text = file.read_text()
    js = json.loads(text)
    strategy_df = pd.DataFrame(js)

    mod = OrderCreator()

    mod.extract(strategy_df)

    mod.make_order()

    print(time.time() - start)