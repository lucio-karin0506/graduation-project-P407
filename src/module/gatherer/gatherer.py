from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import FinanceDataReader as fdr
import pandas as pd
import os
from typing import Tuple

from pandas.core.frame import DataFrame

"""
Created on 2021.1.23

파일명 정의 규칙
-> '종목이름_interval' 로한다. 일봉일 땐 interval = d, 주봉일 땐 interval = w
예) 
일봉 -> 종목이름_d.csv
주봉 -> 종목이름_w.csv

@author: 김상혁
"""

class Gatherer:
    """
    주가 가격데이터 수집 및 저장을 수행한다.
    
    사용 예시
    ----------

    >>> mod = Gatherer()
    # Gatherer 클래스 객체 생성

    >>> df, name = mod.get_stock(code = '005930', startdate = '1990-01-01', enddate = 'today', interval = 'd', save = True)
    # 가격데이터를 생성할 주가코드, 시작날짜, 끝날짜, 가격생성단위(일, 주), 저장여부를 입력하여 가격데이터프레임과 종목이름을 리턴받는다.
    # stockFile 폴더가 생성되고 폴더 안에 종목가격데이터프레임이 파일(CSV)로 저장된다.    
    """
    # -------------------------------------------------------------------------------
    # Constructors
    def __init__(self,
                krx:bool=False,
                path=None):        
        """
        클래스 멤버변수를 초기화한다.
        
        Parameters
        ----------

        Returns
        -------
        None.        
        """
        if krx:
            self.krx_df = fdr.StockListing('KRX')
            os.makedirs(path+'/stockFile', exist_ok=True)
            self.krx_df.to_csv(path+'/stockFile/'+'KRX.csv')

        else:
            if os.path.isfile(f'{path}/stockFile/KRX.csv'):
                self.krx_df = pd.read_csv(f'{path}/stockFile/KRX.csv', usecols=['Symbol', 'Market', 'Name']) 
            else:
                self.krx_df = fdr.StockListing('KRX')               
    # -------------------------------------------------------------------------------  

    def get_stock(
        self,
        code:str,
        startdate:str,
        enddate:str ='today',
        interval:str ='D',
        path=None,
        save:bool =True
        ) -> Tuple[DataFrame, str]:

        """
        주가가격 데이터를 수집하고 옵션에 따라 파일로 저장한다.
        
        Parameters
        ----------
        code: stock code as a string
        startdate: Date as a string
        enddate: Date as a string, default 'today'
        interval: {'d', 'w'}, default 'd'
            종목 가격을 생성을 위한 시간단위를 선택.
            대소문자 구분하지 않음.
        save: {True, False}, default True
            파일저장 여부를 선택

        Returns
        -------
        DataFrame
            주가가격 데이터프레임

        name
            주가코드에 매핑되는 종목이름
        """

        if not enddate == 'today':
            # startdate와 enddate 기간이 시간 순서가 아닐 때 에러처리
            check_start = datetime.strptime(startdate, '%Y-%m-%d')
            check_end = datetime.strptime(enddate, '%Y-%m-%d')

            if check_start > check_end:
                self.__print_error(1)
                return False

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
            df = df.drop_duplicates(keep=False)
            
            try:
                name = self.krx_df.loc[self.krx_df.Symbol == code, 'Name'].values[0] # 주가 코드에 해당하는 이름을 찾음
            except IndexError:
                name = code

            finally:
                if save:                
                    os.makedirs(path+'/stockFile', exist_ok=True)
                    df.to_csv(path+'/stockFile/'+name+'_d.csv', index_label='Date')

        elif interval.upper() == 'W': # 주봉 가격데이터 생성
            df = self._get_week_stock(code, startdate, enddate).rename(columns=lambda col: col.lower())
            try:
                name = self.krx_df.loc[self.krx_df.Symbol == code, 'Name'].values[0] # 주가 코드에 해당하는 이름을 찾음
        
            except IndexError:
                name = code

            finally:
                if save:
                    os.makedirs(path+'/stockFile', exist_ok=True)
                    df.to_csv(path+'/stockFile/'+name+'_w.csv', index_label='Date')

        # 지원하지 않는 interval이 아닌 다른 값을 입력했을 때 에러처리
        else:
            self.__print_error(2)
            return False

        return df, name

    def _get_week_stock(
        self,
        code: str,
        startdate: str,
        enddate: str
        ) -> DataFrame:

        """
        get_stock()에의해 호출되는 함수.
        일봉가격으로 주봉가격 데이터프레임을 생성하여 리턴한다.
        
        Parameters
        ----------
        code: stock code as a string
        startdate: Date as a string
        enddate: Date as a string

        Returns
        -------
        DataFrame
            주봉 주가가격 데이터프레임

        """
        df = fdr.DataReader(code, startdate, enddate)
        df = df.drop_duplicates(keep=False)
        df = df.reset_index()

        week_stock = list()

        for idx, row in df.iterrows():
            '''
            확인할 사항
            몇 주차인지, 무슨 요일인지(1,2,3,4,5)
            '''
            if idx == 0:
                pre_week = row['Date'].isocalendar()[1]
                # pre_day = row['Date'].isocalendar()[2]
                date = row['Date']
                open = row['Open']
                high = row['High']
                low = row['Low']
                close = row['Close']
                volume = row['Volume']
            
            else:
                # print(row['Date'].isocalendar())
                cur_week = row['Date'].isocalendar()[1] # 몇주차인지 확인, 같은 주인지를 확인하는 것임
                # cur_day = row['Date'].isocalendar()[2] # 몇요일인지 확인,

                if pre_week == cur_week: # 같은 주
                    if high > row['High']:
                        pass
                    else:
                        high = row['High']
                    
                    if low < row['Low']:
                        pass
                    else:
                        low = row['Low']

                    close = row['Close']
                    volume = volume + row['Volume']

                else: # 다른 주
                    week_stock.append([date, open, high, low, close, volume])
                    pre_week = cur_week
                    # pre_day = cur_day
                    date = row['Date']
                    open = row['Open']
                    high = row['High']
                    low = row['Low']
                    close = row['Close']
                    volume = row['Volume']

        week_stock.append([date, open, high, low, close, volume])
        reseult_df = pd.DataFrame(week_stock, columns=['Date','Open','High','Low','Close','Volume'])
        
        reseult_df[['Open','High','Low','Close']] = reseult_df[['Open','High','Low','Close']].astype(int)

        # 전일 대비 등락률 계산
        reseult_df['Change'] = reseult_df['Close'].pct_change()
        reseult_df.set_index('Date', inplace=True)

        return reseult_df

    def _print_error(self, erc: int) -> None:
        """        
        Parameters
        ----------
        erc : TYPE
            DESCRIPTION.

        Returns
        -------
        None.
        
        warning code 1 -> 기간이 시간순서가 아님
        warning code 2 -> 지원하지 않는 interval을 입력함
        warning code
        """
        error = {1 : '기간을 다시 입력해 주세요.',
                2 : '지원하지 않는 inverval입니다. d(일봉) 또는 w(주봉)을 입력해주세요.'}
    
        print('gatherer warning code {} : {}'.format(erc, error[erc]))

if __name__ == "__main__":
    mod = Gatherer(False)
    df, _ = mod.get_stock('243070', '2020-10-01', '2020-12-29', interval='w', save=False)
    # df, name = mod.get_crypto('BTC','2020-01-01', '2020-02-15', 'w')

    print(df)
    # print(name)
    # df.to_csv('이지홀딩스_d.csv', index_label='Date')

    # df2, _ =  mod.get_stock('035420', '1990-01-01', 'today', interval='w')

    # print(df2.loc['2017-10-10'])
    # print(df2)

    # df2 =  mod.get_stock('000660', '2019-01-01', '2019-12-01', interval='a')
    # print(df2.loc['2017-10-10'])
    # print(df2)