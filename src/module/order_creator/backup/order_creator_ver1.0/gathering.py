from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import FinanceDataReader as fdr
import pandas as pd

class Gathering:
    """
    로그: 2020.2.8시작, 2.18 수정
    기능: 주가 데이터를 가져옴
    주요파라미터: code - 주가 코드, 시작날짜, 끝날짜, dtype - default(일봉), 주봉
    리턴: 볼린저 밴드가 추가된 주가 데이터프레임    """
    def get_stock(self, code, startdate, enddate=None, dtype='D'):
        # 처음 4개의 조건문은 check_stock에 대한 파라미터 처리이다.
        if startdate == 'today' and enddate == 'today':
            if dtype == 'D':
                startdate = datetime.now() + timedelta(days=-30)
                startdate = startdate.strftime('%Y-%m-%d')
                # print(startdate)
                # return

            elif dtype == 'W':
                startdate = datetime.now() + relativedelta(months=-5)
                startdate = startdate.strftime('%Y-%m-%d')
        elif startdate == enddate:
            if dtype == 'D':
                startdate = datetime.strptime(startdate, "%Y-%m-%d")
                startdate = startdate + timedelta(days=-30)
                startdate = startdate.strftime('%Y-%m-%d')

            elif dtype == 'W':
                startdate = datetime.strptime(startdate, "%Y-%m-%d")
                startdate = startdate + relativedelta(months=-5)
                startdate = startdate.strftime('%Y-%m-%d')

        if dtype == 'D':
            df = fdr.DataReader(code, startdate, enddate).rename(columns=lambda col: col.lower())

        elif dtype == 'W':
            df = self.get_week_stock(code, startdate, enddate).rename(columns=lambda col: col.lower())

        return df
    '''
    로그: 2020.2.8시작, 2020.03.19 수정
    기능: financedatereader에서 일봉데이터를 가져와서 주봉데이터에 맞게 변환
    리턴: 주봉 데이터프레임    '''
    def get_week_stock(self, code, startdate, enddate):
        fdr_df = fdr.DataReader(code, startdate, enddate)
        # resample를 위해 시작일을 월요일로 맞춰주기 위함
        day_index = fdr_df.index[0]; day = fdr_df.index[0].weekday() 
        if not day == 0: # 월요일이 아닌 날일 때
            if day == 1: # 화
                day_index = (day_index + timedelta(days=7-day))                
            elif day == 2: # 수
                day_index = (day_index + timedelta(days=7-day))                
            elif day == 3: # 목
                day_index = (day_index + timedelta(days=7-day))                
            elif day == 4: # 금
                day_index = (day_index + timedelta(days=7-day))                
            elif day == 5: # 토
                day_index = (day_index + timedelta(days=7-day))
            elif day == 6: # 일
                day_index = (day_index + timedelta(days=7-day))

        fdr_df = fdr_df[day_index:] # time series 시작을 월요일로 통일함
        # 주봉데이터프레임의 각 컬럼들을 구성하기 위해 필요한 데이터프레임 생성
        week_mon = fdr_df.resample('W-MON').last().reset_index()       
        week_fri = fdr_df.resample('W-FRI').last().reset_index()
        week_max = fdr_df.resample('W').max().reset_index()
        week_min = fdr_df.resample('W').min().reset_index()

        df = week_mon['Open'].to_frame()
        df['High'] = week_max['High'].to_frame()
        df['Low'] = week_min['Low'].to_frame()
        df['Close'] = week_fri['Close'].to_frame()
        df['Date'] = week_mon['Date'].to_frame()
        df.set_index('Date', inplace=True)

        # # 금주의 high, low, close 값은 달라지므로 변경해줌
        # df.iloc[-1, 1] = fdr_df.iloc[-1]['High']
        # df.iloc[-1, 2] = fdr_df.iloc[-1]['Low']
        # df.iloc[-1, 3] = fdr_df.iloc[-1]['Close']

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
        return df

'''
로그: 2020.02.20 시작
파라미터: 주가데이터와 모든 보조지표데이터프레임
기능: 모든 보조지표들을 하나의 데이터프레임으로 합친다.
리턴: 한 데이터프레임에 모든 주가데이터와 보조지표를 추가하여 리턴    '''
def merge_all_df(*args, false='on'):
    result = pd.concat(args, axis='columns', join='outer')
    if false == 'on':            
        result.fillna(value=False, inplace=True)
    elif false == 'off':
        pass

    return result

if __name__ == "__main__":
    import datetime
    from datetime import timedelta

    d = datetime.datetime(1997, 8, 1)
    x_d = d - timedelta(days=20)
    print(d)
    print(d.strftime('%Y-%m-%d'))
    # print(type(x_d))
    
    # print(x_d.strftime('%Y-%m-%d'))

    str_d = x_d.strftime('%Y-%m-%d')
    print(str_d)

    mod = Gathering()
    # df1 = mod.get_stock('000660', d.strftime('%Y-%m-%d'), '2000-08-01', 'D')
    # print(df1)

    df2 =  mod.get_stock('005930', '1990-01-01', dtype='W')
    print(df2)