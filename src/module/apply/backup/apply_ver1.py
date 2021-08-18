from module.calculator.calculator import Calculator
from module.order_creator.order_creator import OrderCreator
from module.simulator.simulator import Simulator

import pandas as pd
import os
import pathlib
import json
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
    def __init__(self) -> None:
        """
        클래스 멤버변수를 초기화한다.
        OrderCreator, Simulator, Calculator 객체 생성
        
        Parameters
        ----------

        Returns
        -------
        None.  
        """  
        self.__request_df = pd.DataFrame(columns=
                            ['stockcode', 
                            'startdate', 
                            'enddate', 
                            'interval', 
                            'indicator',
                            'strategy'])

        self.__a_log = pd.DataFrame(columns=
                            ['stockname', 
                            'fin_asset', 
                            'max_asset', 
                            'min_asset', 
                            'buy_count',
                            'sell_count'])
        
        self.__O_mod = OrderCreator(network=True, mix=False)
        self.__S_mod = Simulator()
        self.__C_mod = Calculator()

        self.__krx_df=\
            pd.read_csv(os.getcwd()+'/stockFile/'+'KRX.csv', usecols=['Symbol', 'Market', 'Name'])

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
        file = pathlib.Path(os.getcwd()+'/strategyFile/'+strategy_file)
        
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
            self.__request_df.at[idx, 'indicator'] = df['indicator'][0]

        self.__S_mod.set_option(buying_fee,
                            selling_fee,
                            national_tax,
                            slippage,
                            False)
        
        self.cash = cash
        self.__S_mod.set_cash(self.cash)

    def apply(self) -> None:
        """
        다 종목에 대해 전략을 적용
        
        Parameters
        ----------

        Returns
        -------
        None.  
        """  
        self.__O_mod.read_df(self.__request_df)

        self.__O_mod.make_order()
        
        for idx, stock in enumerate(self.__request_df['stockcode']):
            name = self.__krx_df.loc[self.__krx_df.Symbol == stock, 'Name'].values[0] # 주가 코드에 해당하는 이름을 찾음

            # 시뮬레이션을 다시 켜서 실행해야함
            # 그래도 다시 실행하면 기존 데이터가 존재함
            self.__S_mod.read_file(
                str(name)+'_'+self.__request_df['interval'][0]+'_Order.json')
            
            self.__S_mod.simulation()
            self.__S_mod.write_trlog(tpath='cwd')
            self.__S_mod.write_stlog(spath='cwd')

            buy_count, sell_count = self.__S_mod.get_Tcount()

            self.__a_log.loc[idx, 'stockname'] = name
            self.__a_log.loc[idx, 'buy_count'] = buy_count
            self.__a_log.loc[idx, 'sell_count'] = sell_count

            self.__C_mod.read_file(
                str(name)+'_'+self.__request_df['interval'][0]+'_TradingLog.json')
            
            # self.__C_mod.calculation('week')
            self.__C_mod.calculation('month')
            # self.__C_mod.calculation('year')
            
            # self.__C_mod.write_atlog('week', apath='cwd')
            self.__C_mod.write_atlog('month', apath='cwd')
            # self.__C_mod.write_atlog('year', apath='cwd')

            # fin_asset, max_asset, min_asset = self.__C_mod.get_Wasset()
            fin_asset, max_asset, min_asset = self.__C_mod.get_Masset()
            # fin_asset, max_asset, min_asset = self.__C_mod.get_Yasset()

            self.__a_log.loc[idx, 'fin_asset'] = fin_asset
            self.__a_log.loc[idx, 'max_asset'] = max_asset
            self.__a_log.loc[idx, 'min_asset'] = min_asset

            #reset simulator, calculator
            self.__S_mod.reset_simulator()
            self.__S_mod.set_cash(self.cash)

            self.__C_mod.reset_calculator()

        # order json file 생성
        cwd = os.getcwd()
        os.makedirs(cwd+'/applyFile', exist_ok=True)

        self.__a_log.to_csv(cwd+'/applyFile/result.csv')

    def _print_error(self, erc:int) -> None:
            """        
            Parameters
            ----------
            erc : TYPE
                DESCRIPTION.

            Returns
            -------
            None.
            
            error code 1 -> 전략 파일이 존재하지 않습니다.
            error code 2 -> 
            """        
            error = {1 : '전략파일이 존재하지 않습니다.'}
        
            print('OrderCreator error code {} : {}'.format(erc, error[erc]))


if __name__ == "__main__":
    stock_list = ['000660', # SK하이닉스
                '005930', # 삼성전자
                '005380', # 현대차
                '068270', # 셀트리온
                '051910', # LG화학
                '000270', # 기아차
                '048410', # 현대바이오
                '035420'] # 네이버

    mod = Apply()
    mod.set_option(
        stock_list,
        '2019-01-01',
        '2021-01-01',
        'd',
        'DS_strategy_ver3',
        100000000,
        0.015,
        0.015,
        0.23,
        0.01)

    mod.apply()