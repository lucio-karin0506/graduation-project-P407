from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import FinanceDataReader as fdr
import pandas as pd
import os

"""
autor: 김상혁
"""

class Gatherer:
    def __init__(self):
        self.df_krx = fdr.StockListing('KRX')

    """
    log: 2020.2.8시작, 2.18 수정
    func: 주가 데이터를 가져옴
    parameter: code: 주가 코드, startdate: 시작날짜, enddate: 끝날짜, interval: default(일봉), 주봉, 저장여부
    return: 볼린저 밴드가 추가된 주가 데이터프레임    """
    def get_stock(self, code: str, startdate: str, enddate: str ='today', interval: sorted='D', save: bool =True) -> (pd.DataFrame ,str):
        if not enddate == 'today':
            # startdate와 enddate 기간이 시간 순서가 아닐 때 에러처리
            check_start = datetime.strptime(startdate, '%Y-%m-%d')
            check_end = datetime.strptime(enddate, '%Y-%m-%d')

            if check_start > check_end:
                self.__print_error(1)
                return

        # 처음 4개의 조건문은 check_stock에 대한 parameter 처리이다.
        if startdate == 'today' and enddate == 'today':
            if interval.upper() == 'D':
                startdate = datetime.now() + timedelta(days=-30)
                startdate = startdate.strftime('%Y-%m-%d')                

            elif interval.upper() == 'W':
                startdate = datetime.now() + relativedelta(months=-5)
                startdate = startdate.strftime('%Y-%m-%d')

        elif startdate == enddate:
            if interval.upper() == 'D':
                startdate = datetime.strptime(startdate, "%Y-%m-%d")
                startdate = startdate + timedelta(days=-30)
                startdate = startdate.strftime('%Y-%m-%d')

            elif interval.upper() == 'W':
                startdate = datetime.strptime(startdate, "%Y-%m-%d")
                startdate = startdate + relativedelta(months=-5)
                startdate = startdate.strftime('%Y-%m-%d')

        if interval.upper() == 'D': # 일봉 가격데이터 생성
            df = fdr.DataReader(code, startdate, enddate).rename(columns=lambda col: col.lower())
            try:
                name = self.df_krx.loc[self.df_krx.Symbol == code, 'Name'].values[0] # 주가 코드에 해당하는 이름을 찾음

            except IndexError:
                name = code

            finally:
                if save:                
                    os.makedirs(os.getcwd()+'/stockFile', exist_ok=True)
                    df.to_csv(os.getcwd()+'/stockFile/'+name+'_d.csv', index_label='Date')

        elif interval.upper() == 'W': # 주봉 가격데이터 생성
            df = self.__get_week_stock(code, startdate, enddate).rename(columns=lambda col: col.lower())
            try:
                name = self.df_krx.loc[self.df_krx.Symbol == code, 'Name'].values[0] # 주가 코드에 해당하는 이름을 찾음

            except IndexError:
                name = code

            finally:
                if save:
                    os.makedirs(os.getcwd()+'/stockFile', exist_ok=True)
                    df.to_csv(os.getcwd()+'/stockFile/'+name+'_w.csv', index_label='Date')

        # 지원하지 않는 interval이 아닌 다른 값을 입력했을 때 에러처리
        else:
            self.__print_error(2)
            return 

        self.df = df

        return df, name

    '''    
    log: 2020.2.8시작, 2020.03.19 수정
    func: financedatereader에서 일봉데이터를 가져와서 주봉데이터에 맞게 변환, reason: pandas_datareader로 생성하는 주봉데이터가 틀리기 때문 
    parameter: 주가 코드, 시작날짜, 끝날짜
    return: 주봉 데이터프레임    '''
    def _get_week_stock(self, code: str, startdate: str, enddate: str) -> pd.DataFrame:
        '''  enddate가 None이거나 today일때 처리      '''
        if enddate == None or enddate == 'today':
            enddate = datetime.strftime(datetime.today(), "%Y-%m-%d")

        fri_end = datetime.strptime(enddate, "%Y-%m-%d")
        end_day = fri_end.weekday()

        if not end_day == 4: # 금요일이 아닌 날일 때
            new_end = (fri_end + timedelta(days=4 - end_day))
        else:
            new_end = fri_end       

        fdr_df = fdr.DataReader(code, startdate, new_end)
        
        # resample를 위해 시작일을 월요일로 맞춰주기 위함
        # day==0 월 / day==1 화 / day==2 수 / day==3 목 / day==4 금 / day==5 토 / day==6 일
        day_index = fdr_df.index[0]; 
        day = fdr_df.index[0].weekday() 
        if not day == 0: # 월요일이 아닌 날일 때
            day_index = day_index + timedelta(days=7-day)      

        fdr_df = fdr_df[day_index:] # time series 시작을 월요일로 통일함
        # 주봉데이터프레임의 각 컬럼들을 구성하기 위해 필요한 데이터프레임 생성
        week_mon = fdr_df.resample('W-MON').last().reset_index()      
        week_fri = fdr_df.resample('W-FRI').last().reset_index()
        week_max = fdr_df.resample('W').max().reset_index()
        week_min = fdr_df.resample('W').min().reset_index()
        week_sum = fdr_df.resample('W').sum().reset_index()

        df = week_mon['Open'].to_frame()
        df['High'] = week_max['High'].to_frame()
        df['Low'] = week_min['Low'].to_frame()
        df['Close'] = week_fri['Close'].to_frame()
        df['Date'] = week_mon['Date'].to_frame()
        df['Volume'] = week_sum['Volume'].to_frame()
        df.set_index('Date', inplace=True)

        try:
            # startdate가 2017년 이전인지 아닌지 확인해야함 startdate가 2017-10-09이전이면 2017-10-09에 대한 처리를 해야함
            # 또한 불러온 주가 데이터의 마지막 날이 2017-10-10 보다 커야함
            if datetime.strptime(startdate, '%Y-%m-%d').date() < datetime.strptime('2017-10-10', '%Y-%m-%d').date()\
                and fdr_df.index[-1].date() > datetime.strptime('2017-10-10', '%Y-%m-%d').date():

                df.drop(df.index[df.index == '2017-10-02'], axis=0, inplace=True)
                df.loc['2017-10-09', 'Open'] = fdr_df.loc['2017-10-10', 'Open']
                df.reset_index(inplace=True);  df['Date'] = pd.to_datetime(df['Date']) # 데이터프레임의 날짜형식을 변환하기 위함
                df.loc[df[df.Date == '2017-10-09'].index[0], 'Date'] = datetime.strptime('2017-10-10', '%Y-%m-%d') # 날짜를 변경 9일 -> 10일
                df.set_index('Date',inplace=True)

        except:
            print('주가코드나 날짜를 다시 확인해주세요')

        # dateframe에 마지막 컬럼의resample하는 날짜가 금주를 넘어가기 때문에 삭제함
        df.drop(df.index[-1], inplace=True)  

        # 전일 대비 등락률 계산
        df['Change'] = df['Close'].pct_change()

        df[['Open','High','Low','Close','Volume']] = df[['Open','High','Low','Close','Volume']].astype(int)

        return df
    '''    
    log: start. 2021.1.18
    func: 클래스 멤버 함수에서 발생된 에러코드에 대한 에러 메시지를 출력한다.
    parameter: error code
    return: None    '''
    def __print_error(self, erc: int) -> None:
        error = {1 : '기간을 다시 입력해 주세요.',
                2 : '지원하지 않는 inverval입니다. d(일봉) 또는 w(주봉)을 입력해주세요.'}
    
        print('gatherer error code {} : {}'.format(erc, error[erc]))

if __name__ == "__main__":
    mod = Gatherer()
    df, _ = mod.get_stock('AAPL', '2021-01-01', 'today', 'd', False)

    print(df)

    # df2 =  mod.get_stock('005380', '1990-01-01', interval='W')

    # print(df2.loc['2017-10-10'])
    # print(df2)

    # df2 =  mod.get_stock('000660', '2019-01-01', '2019-12-01', interval='a')
    # print(df2.loc['2017-10-10'])
    # print(df2)