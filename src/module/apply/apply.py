from logging import root
from module.calculator.calculator import Calculator
from module.order_creator.order_creator import OrderCreator
from module.simulator.simulator import Simulator

import pandas as pd
import os
import pathlib
import json
import FinanceDataReader as fdr

from multiprocessing import Process, Manager
"""
Created on 2021.2.1
@author: 김상혁
"""

class Apply:
    """
    전략을 다 종목에 대해 적용한다.
    
    # 사용 예시
    ----------

    >>> mod = Apply()
    # Apply 클래스 객체 생성
    
    >>> mod.set_option(
        stock_list,
        startdate,
        enddate,
        interval,
        strategy,
        cash,
        buying_fee,
        selling_fee,
        national_tax,
        slippage)
    # option 세팅

    >>> mod.apply()
    # 전략을 다 종목에 적용
    """
    def __init__(self, multi=False, path=None) -> None:
        """
        클래스 멤버변수를 초기화한다.
        OrderCreator, Simulator, Calculator 객체 생성
        
        Parameters
        ----------
        multi
            멀티프로세스 동작을 선택할 수 있다.

        Returns
        -------
        None.  
        """  
        self.root_path = path
        self.__request_df = pd.DataFrame(columns=
                            ['stockcode', 
                            'startdate', 
                            'enddate', 
                            'interval', 
                            'indicator',
                            'strategy'])

        self.__a_log = pd.DataFrame(columns=
                            ['stockname', 
                            'fin_PL_ratio', 
                            'max_PL_ratio',
                            'min_PL_ratio', 
                            'buy_count',
                            'sell_count'])
        
        self.__oc = OrderCreator(network=True, mix=False, root_path=path)
        self.__sim = Simulator()
        self.__cal = Calculator()

        if os.path.isfile(f'{self.root_path}/stockFile/KRX.csv'):
            self.__krx_df =\
                    pd.read_csv(f'{self.root_path}/stockFile/KRX.csv', usecols=['Symbol', 'Market', 'Name'])
        else:
            self.__krx_df = fdr.StockListing('KRX')
        
        self.multi = multi
        manager = Manager()
        self.result = manager.list()

    def set_option(
        self,
        stock_list:list,
        startdate:str,
        enddate:str,
        interval:str,
        strategy_file:str,
        cash:int,
        buying_fee:float,
        selling_fee:float,
        national_tax:float,
        slippage:float
        ) -> None:
        """
        apply 옵션 설정
        - 적용 종목
        - 시작날짜
        - 끝날짜
        - 가격생성 시간단위
        - 적용 전략
        - 시뮬레이션 초기자본금
        - 거래 수수료
        - 세금
        - 슬리피지
        
        Parameters
        ----------
        stock_list: 종목 리스트
        startdate: 시작날짜
        enddate: 끝날짜
        interval: 종목 가격을 생성을 위한 시간단위를 선택 {'d', 'w'}
        strategy: 사용전략
        cash: 초기자본금
        buying_fee: 매수 수수료
        selling_fee: 매도 수수료
        national_tax: 세금
        slippage: 슬리피지

        Returns
        -------
        None.  
        """  

        '''
        strategy_file format 정리가 필요
        '''
        file = pathlib.Path(strategy_file)
        
        try:
            text = file.read_text(encoding='utf-8')

        except FileNotFoundError:
            self._print_error(1)
            return
        
        js = json.loads(text)
        df = pd.DataFrame(js)

        self.__request_df['stockcode'] = stock_list
        self.__request_df['startdate'] = startdate
        self.__request_df['enddate'] = enddate
        self.__request_df['interval'] = interval
        self.__request_df['strategy'] = df['strategy'][0]
        
        for idx in self.__request_df.index:
            try:
                self.__request_df.at[idx, 'indicator'] = df['indicator'][0]
        
            except KeyError:
                self._print_error(2)
                return

        self.__sim.set_option(buying_fee,
                            selling_fee,
                            national_tax,
                            slippage,
                            False)
        
        self.cash = cash
        self.__sim.set_cash(self.cash)

    def appling(self, idx:int, stock:str) -> None:
        """
        다 종목에 대해 전략을 적용
        
        Parameters
        ----------
        idx
            stock code의 index
        stock
            stock code

        Returns
        -------
        None.  
        """ 
        try:
            name = self.__krx_df.loc[self.__krx_df.Symbol == stock, 'Name'].values[0] # 주가 코드에 해당하는 이름을 찾음

        except IndexError:
            name = stock

        if self.__sim.read_file(str(name)+'_'+self.__request_df['interval'][0]+'_Order.json',
                                path=self.root_path):
            self.__sim.simulation()
            self.__sim.write_trlog(path=self.root_path)
            self.__sim.write_stlog(path=self.root_path)

            if self.__sim.get_Tcount():
                buy_count, sell_count = self.__sim.get_Tcount()
            else:
                buy_count, sell_count = 0, 0

            self.__a_log.loc[idx, 'stockname'] = name
            self.__a_log.loc[idx, 'buy_count'] = buy_count
            self.__a_log.loc[idx, 'sell_count'] = sell_count
        else:
            self.__a_log.loc[idx, 'stockname'] = name
            self.__a_log.loc[idx, 'buy_count'] = 0
            self.__a_log.loc[idx, 'sell_count'] = 0
        
        

        if self.__cal.read_file(str(name)+'_'+self.__request_df['interval'][0]+'_TradingLog.json',
                                path=self.root_path):         
            # self.__cal.calculation('week')
            self.__cal.calculation('month')
            # self.__cal.calculation('year')
            
            # self.__cal.write_atlog('week', apath='cwd')
            self.__cal.write_atlog('month', path=self.root_path)
            # self.__cal.write_atlog('year', apath='cwd')

            # fin_PL_ratio, max_PL_ratio, min_PL_ratio = self.__cal.get_Wasset()
            fin_PL_ratio, max_PL_ratio, min_PL_ratio = self.__cal.get_Masset()
            # fin_PL_ratio, max_PL_ratio, min_PL_ratio = self.__cal.get_Yasset()

            self.__a_log.loc[idx, 'fin_PL_ratio'] = fin_PL_ratio
            self.__a_log.loc[idx, 'max_PL_ratio'] = max_PL_ratio
            self.__a_log.loc[idx, 'min_PL_ratio'] = min_PL_ratio
        else:
            self.__a_log.loc[idx, 'fin_PL_ratio'] = 0
            self.__a_log.loc[idx, 'max_PL_ratio'] = 0
            self.__a_log.loc[idx, 'min_PL_ratio'] = 0

        if self.multi:
            self.result.append(self.__a_log.loc[idx].tolist())
            self.__sim.reset_simulator()
            self.__sim.set_cash(self.cash)
            self.__cal.reset_calculator()

        else:
            #reset simulator, calculator
            self.__sim.reset_simulator()
            self.__sim.set_cash(self.cash)
            self.__cal.reset_calculator()
            cwd = self.root_path 
            os.makedirs(cwd+'/applyFile', exist_ok=True)
            self.__a_log.to_csv(cwd+'/applyFile/apply_result.csv', encoding='cp949')
            print(self.__a_log)

    def apply(self) -> None:
        """
        다 종목에 대해 전략을 적용할 수 있도록 appling() 호출
        
        Parameters
        ----------

        Returns
        -------
        None.  
        """        
        # if self.__request_df['indicator'].isna()[0]:
        #     return

        if self.__oc.read_df(self.__request_df, path=self.root_path):
            self.__oc.make_order()     
            
        procs = []
        
        if self.multi:
            for idx, stock in enumerate(self.__request_df['stockcode']):
                proc = Process(target=self.appling, args=(idx, stock))
                procs.append(proc)
                proc.start()

            for proc in procs:
                proc.join()
            
            # order json file 생성
            df = pd.DataFrame(list(self.result),\
                    columns=['stockname', 'fin_PL_ratio', 'max_PL_ratio', 'min_PL_ratio', 'buy_count', 'sell_count'])
            cwd = self.root_path 
            os.makedirs(cwd+'/applyFile', exist_ok=True)
            df.to_csv(cwd+'/applyFile/apply_result.csv', encoding='cp949')
            print(df)

        else:
            for idx, stock in enumerate(self.__request_df['stockcode']):
                self.appling(idx, stock)

    def _print_error(self, erc:int) -> None:
        """        
        Parameters
        ----------
        erc : TYPE
            DESCRIPTION.

        Returns
        -------
        None.
        
        warning code 1 -> 전략 파일이 존재하지 않습니다.
        warning code 2 -> indicator가 존재하지 않습니다.
        """        
        error = {1 : '전략파일이 존재하지 않습니다.',
                2 : 'indicator가 존재하지 않습니다.'}
    
        print('Apply warning code {} : {}'.format(erc, error[erc]))
