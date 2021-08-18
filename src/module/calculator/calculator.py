import pathlib
import json
import pandas as pd
import os
import datetime
import FinanceDataReader as fdr
import re
from pandas.core.reshape.concat import concat

# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 16:58:46 2020

@author: giho9
"""

class Calculator:
    '''
    거래내역을 입력받아서 주간 수익률, 월간 수익률, 연간 수익률을 계산한다.
    
    
    사용 예시
    ----------
    
    >>> import pandas as pd
    >>> import pathlib
    >>> import json
    >>> import os
    
    >>> file = pathlib.Path(os.getcwd()+'\\TradingLog.json')
    >>> text = file.read_text(encoding='utf-8')
    >>> js = json.loads(text)
    >>> trade = pd.DataFrame(js)
    # json 거래내역 파일을 읽어와서 데이터프레임에 저장
    
    >>> mod = Calculator()
    # 클래스 선언
    
    >>> mod.insert_log(trade)
    # 거래내역 삽입
    
    >>> mod.create_dates()
    >>> mod.create_weeks()
    >>> mod.create_months()
    >>> mod.create_years()
    # 거래내역 날짜를 기반으로 날짜 생성

    >>> mod.calculation('week')
    >>> mod.calculation('month')
    >>> mod.calculation('year')
    # 주간 수익률, 월간 수익률, 연간 수익률 계산
    
    >>> mod.write_atlog('', 'week')
    >>> mod.write_atlog('', 'month')
    >>> mod.write_atlog('', 'year')
    # 주간 수익률, 월간 수익률, 연간 수익률 json파일 출력
    
    '''
    
    def __init__(self):        
        '''
        클래스 멤버변수를 초기화하는 init 함수이다.

        Parameters
        ----------

        Returns
        -------
        None.           
        '''
        
        self._wast_log = pd.DataFrame(columns=
                                     ['datetime', 
                                      'asset', 
                                      'profit/loss ratio',
                                      'cumulative profit/loss ratio'])
        
        self._mast_log = pd.DataFrame(columns=
                                     ['datetime', 
                                      'asset', 
                                      'profit/loss ratio',
                                      'cumulative profit/loss ratio'])
        
        self._yast_log = pd.DataFrame(columns=
                                     ['datetime', 
                                      'asset', 
                                      'profit/loss ratio',
                                      'cumulative profit/loss ratio'])
        
        self._weeks = list()
        self._months = list()
        self._years = list()

    def read_file(self,
                file_name:str,
                path=None) -> bool:
        """
        거래 로그 파일을 읽어 insert_log 함수에 전달한다.
        
        Parameters
        ----------
        file_name:
            전략파일 이름

        Returns
        -------
        boolean.
        """
        
        file = pathlib.Path(path+'/tradingLogFile/'+file_name)
        self.stock_name = file_name.split('_')
        
        try:
            text = file.read_text(encoding='utf-8')
        except FileNotFoundError:
            self._print_error(1)
            return False

        js = json.loads(text)

        self.insert_log(pd.DataFrame(js))

        self.create_dates()
        self.create_weeks()
        self.create_months()
        self.create_years()

        return True
        
    def insert_log(self, log):        
        '''
        거래내역을 입력하는 함수이다.
        
        Parameters
        ----------
        log : DataFrame
            거래내역이 들어있는 데이터프레임

        Returns
        -------
        None.
        '''
        
        self._trd_log = log
    
    def create_dates(self):        
        '''
        거래 시작 날짜와 마지막 날짜 사이의 모든 날짜를 구한다.
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        None.
        '''
        
        fod = self._trd_log['order_datetime'][0]
        lod = self._trd_log['order_datetime'][len(self._trd_log)-1]
        di = pd.date_range(start=fod, end=lod)
        dl = di.strftime("%Y-%m-%d").tolist()
        
        self._dates = dl
    
    def create_weeks(self):        
        '''
        거래 시작 날짜와 마지막 날짜 사이의 모든 날짜에서
        금요일인 날짜만 남긴다.
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        None.        
        '''
        
        for date in self._dates:
            wtmp = datetime.datetime.strptime(date, "%Y-%m-%d")
            if wtmp.weekday() == 4: self._weeks.append(date)
            
    def create_months(self):        
        '''
            거래 시작 날짜와 마지막 날짜 사이의 모든 날짜에서
            월 마지막인 날짜만 남긴다.
            ex) 
            
            Parameters
            ----------
            None.
            
            Returns
            -------
            None.        
        '''
        import calendar
        
        for date in self._dates:
            y,m = str(date[0:4]), str(date[5:7])
            d = str(calendar.monthrange(int(date[0:4]), int(date[5:7]))[1])
            self._months.append(y + '-' + m + '-' + d)
        self._months = sorted(list(set(self._months)))
    
    def create_years(self):        
        '''
        거래 시작 날짜와 마지막 날짜 사이의 모든 날짜에서
        연 마지막인 날짜만 남긴다.
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        None.
        '''
        
        for date in self._dates:
            y = str(date[0:4]) + '-12-31'
            self._years.append(y)

        self._years = sorted(list(set(self._years)))

    def rated(self, rdf, rdt)->bool:
        '''
        해당 시점 이전의 거래내역에 대해서 수익률을 계산한다.
        
        Parameters
        ----------
        rdf : DataFrame
            해당 시점 이전의 거래내역이 담긴 데이터프레임
        
        rdt : str
            날짜

        Returns
        -------
        boolean.
        '''
        import time
        
        t = rdt        
        ist = list()
        
        if rdf.empty:            
            return False
        
        for _, pr in rdf.iterrows():            
            pdf = fdr.DataReader(pr.item_code, rdt, rdt)
            
            while pdf.empty:                
                rdt = str(datetime.datetime.strptime(rdt, '%Y-%m-%d')\
                            - datetime.timedelta(1))[:10]
                
                pdf = fdr.DataReader(pr.item_code, rdt, rdt)
                
                time.sleep(0.5)                
                print(rdt)
                
            ist.append(int(pr['hold']) * int(pdf['Close']))

        ast = sum(ist) + int(rdf.tail(1)['res_cash'])
        
        # cum = round((ast) /
        #     (int(self._trd_log.head(1).order_value + self._trd_log.head(1).res_cash)) ,3)
        
        if not self.atlog:
            pl_ratio = round((ast - (int(self._trd_log.head(1).order_value + self._trd_log.head(1).res_cash)))\
            / (int(self._trd_log.head(1).order_value + self._trd_log.head(1).res_cash)) * 100 , 2)
        
        else:
            pl_ratio = round((ast - self.atlog['asset']) / self.atlog['asset'] * 100, 2)
        
        cpl_ratio = round((ast - (int(self._trd_log.head(1).order_value + self._trd_log.head(1).res_cash)))\
            / (int(self._trd_log.head(1).order_value + self._trd_log.head(1).res_cash)) * 100 , 2)
        
        self.atlog = {'datetime' : t, 
                    'asset' : ast,
                    'profit/loss ratio' : pl_ratio,
                    'cumulative profit/loss ratio' : cpl_ratio
                    }
        return True

    def calculation(self, opt):        
        '''
        Parameters
        ----------
        opt : str
        
            주간 수익률 -> week
            월간 수익률 -> month
            연간 수익률 -> year
            
        Returns
        -------
        None.
        '''

        if opt == 'week': dates = self._weeks
        if opt == 'month': dates = self._months
        if opt == 'year': dates = self._years

        self.atlog = False
        
        for dt in dates: 
            tdf = self._trd_log.query("order_datetime <= '%s'" % dt).\
                drop_duplicates(['item_code'], keep='last')
            
            if self.rated(tdf, dt):
                if opt == 'week':
                    self._wast_log\
                        = self._wast_log.append(self.atlog, ignore_index='True')
                    print(self._wast_log)
                if opt == 'month':
                    self._mast_log\
                        = self._mast_log.append(self.atlog, ignore_index='True')
                    print(self._mast_log)
                if opt == 'year':
                    self._yast_log\
                        = self._yast_log.append(self.atlog, ignore_index='True')
                    print(self._yast_log)
        
            
                
    def write_atlog(self,
                    nopt:str,
                    path:str,
                    file_name:str=''):        
        '''
        Parameters
        ----------            
        nopt : str
            주간 수익률 -> week
            월간 수익률 -> month
            연간 수익률 -> year
        path : str
            파일을 저장할 경로
        file_name:str
            Asset.json의 파일명을 입력받는다.
            
        Returns
        -------
        None        
        '''
    
        os.makedirs(path+'/Asset'+nopt+'File', exist_ok=True)
        
        if nopt == 'week': adict = self._wast_log.to_dict(orient='records')
        if nopt == 'month': adict = self._mast_log.to_dict(orient='records')
        if nopt == 'year': adict = self._yast_log.to_dict(orient='records')
        
        # json.dumps(tdict, ensure_ascii=False, indent='\t')
        if file_name == '':
            with open(f"{path}/Asset{nopt}File/{self.stock_name[0]}_{self.stock_name[1]}_Asset{nopt}.json", 'w+', encoding='utf-8') as make_file:
                json.dump(adict, make_file, ensure_ascii=False, indent='\t')
        else:
            with open(f"{path}/Asset{nopt}File/{file_name}_Asset{nopt}.json", 'w+', encoding='utf-8') as make_file:
                json.dump(adict, make_file, ensure_ascii=False, indent='\t')

    def get_Wasset(self):
        """
        주간 수익률 중 마지막, 최대, 최소 수익률을 리턴한다.

        Parameters
        ----------

        Returns
        -------
        None.
        """
        return self._wast_log['cumulative profit/loss ratio'].iloc[-1],\
                max(self._wast_log['profit/loss ratio']),\
                min(self._wast_log['profit/loss ratio'])

    def get_Masset(self):
        """
        월간 수익률 중 마지막, 최대, 최소 수익률을 리턴한다.

        Parameters
        ----------

        Returns
        -------
        None.
        """
        return self._mast_log['cumulative profit/loss ratio'].iloc[-1],\
                max(self._mast_log['profit/loss ratio']),\
                min(self._mast_log['profit/loss ratio'])

    def get_Yasset(self):
        """
        연간 수익률 중 마지막, 최대, 최소 수익률을 리턴한다.

        Parameters
        ----------

        Returns
        -------
        None.
        """
        return self._yast_log['cumulative profit/loss ratio'].iloc[-1],\
                max(self._yast_log['profit/loss ratio']),\
                min(self._yast_log['profit/loss ratio'])

    def reset_calculator(self):
        '''
        클래스 멤버변수를 초기화하는 함수이다.

        Parameters
        ----------

        Returns
        -------
        None.           
        '''
        
        self._wast_log = pd.DataFrame(columns=
                                     ['datetime', 
                                      'asset', 
                                      'profit/loss ratio',
                                      'cumulative profit/loss ratio'])
        
        self._mast_log = pd.DataFrame(columns=
                                     ['datetime', 
                                      'asset', 
                                      'profit/loss ratio',
                                      'cumulative profit/loss ratio'])
        
        self._yast_log = pd.DataFrame(columns=
                                     ['datetime', 
                                      'asset', 
                                      'profit/loss ratio',
                                      'cumulative profit/loss ratio'])

        self._weeks = list()
        self._months = list()
        self._years = list()

    def _print_error(self, erc):
        """
        Parameters
        ----------
        erc : TYPE
            DESCRIPTION.

        Returns
        -------
        None.
        
        warning code 1 -> tradingLog file이 존재하지 않음
        warning code
        warning code
        """        
        error = {1 : '거래로그파일이 존재하지 않습니다.'}

        print('calculator warning code {} : {}'.format(erc, error[erc]))

if __name__ == '__main__':
    
    import pandas as pd
    import pathlib
    import json
    import os
    
    # file = pathlib.Path(os.getcwd()+'/TradingLogFile/'+'넥센타이어_d_TradingLog.json')
    # text = file.read_text(encoding='utf-8')
    # js = json.loads(text)
    # trade = pd.DataFrame(js)
    
    mod = Calculator()
    
    # mod.insert_log(trade)
    
    # mod.create_dates()
    # mod.create_weeks()
    # mod.create_months()
    # mod.create_years()

    mod.read_file('넥센타이어_d_TradingLog.json')

    # mod.calculation('week')
    mod.calculation('month')
    #mod.calculation('year')
    
    # mod.write_atlog('week')
    mod.write_atlog('month', 'cwd')
    #mod.write_atlog('year', 'cwd')

    a,b,c = mod.get_Masset()
    print(a, b, c)
