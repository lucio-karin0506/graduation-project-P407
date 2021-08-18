# -*- coding: utf-8 -*-
import pandas as pd
import pathlib
import json
import os
import FinanceDataReader as fdr
import re
"""
Created on Wed Jul 15 16:58:46 2020

@author: giho9
"""

class Simulator:
    '''
    주문서를 입력받으면 과거데이터를 이용하여 수익률 시뮬레이션을 수행한다.
    주식종목, ETF, 가상화폐(미구현)에 대해서 시뮬레이션이 가능하다.
    
    사용 예시
    ----------

    >>> file = pathlib.Path(os.getcwd()+'\\order.json')
    >>> text = file.read_text(encoding='utf-8')
    >>> js = json.loads(text)
    >>> order = pd.DataFrame(js)
    # 주문서를 json file에서 읽어온 뒤 데이터프레임에 저장한다.
    
    order type
    
        buy : 매수
        
        sell : 매도
        
    (buy) order_option
    
        all : 보유현금 기준 최대매수
        
        por : 보유자산의 일정 퍼센트만큼 매수
        
        cash : 지정금액 이하 최대매수
        
        scnt : 보유주식의 일정 주식수 매수

        m_por : 초기자본의 일정 퍼센트만큼 매수
        
    (buy) order_value
    
        all : 0이든 비워놓든 상관없다.
        
        por : 0.5, 0,7과 같이 비율로 설정
        
        cash : 5000000, 1000000과 같이 금액으로 설정
        
        scnt : 100, 500과 같이 매수할 주식 수를 입력

        m_por : 0.5, 0,7과 같이 비율로 설정
        
    (sell) order_option
    
        all : 보유종목 전량매도
        
        por : 보유주식의 일정 퍼센트만큼 매도
        
        scnt : 보유주식의 일정 주식수 매도

        m_por : 초기자본의 일정 퍼센트만큼 매도
        
    (sell) order_value
    
        all : 0이든 비워놓든 상관없다.
        
        por : 0.5, 0.7과 같이 비율로 설정
        
        scnt : 100, 500과 같이 매도할 주식 수를 입력

        m_por : 0.5, 0,7과 같이 비율로 설정
    
    example) order.json
    
    [
    	{
    		"order_datetime": "2018-04-27",
    		"order_type": "buy",
    		"item_code": "032640",
    		"item_name": "LG유플러스",
    		"order_price": "12300",
    		"order_option": "cash",
    		"order_value": "5000000"
    	},
        {
    		"order_datetime": "2018-04-27",
    		"order_type": "sell",
    		"item_code": "032640",
    		"item_name": "LG유플러스",
    		"order_price": "12300",
    		"order_option": "scnt",
    		"order_value": "150"
    	}  
    ]
    
    
    >>> file = pathlib.Path(os.getcwd()+'\\status.json')
    >>> text = file.read_text(encoding='utf-8')
    >>> status = json.loads(text)
    # 보유현금과 보유종목들이 들어있는 Status.json을 사용할 수 있다.
    # Status.json이 없이 초기자본 세팅만으로도 시뮬레이션 진행이 가능하다.
    
    example) status.json
    
    {
    	"cash": 5465000,
    	"stock": [
    		{
    			"item_name": "LG유플러스",
    			"item_code": "032640",
    			"item_count": 200,
    			"avg_price": 13571
    		},
    		{
    			"item_name": "SK하이닉스",
    			"item_code": "000660",
    			"item_count": 200,
    			"avg_price": 84000
    		},
    		{
    			"item_name": "엔씨소프트",
    			"item_code": "036570",
    			"item_count": 100,
    			"avg_price": 400000
    		},
    		{
    			"item_name": "POSCO",
    			"item_code": "005490",
    			"item_count": 200,
    			"avg_price": 245000
    		},
    		{
    			"item_name": "아모레퍼시픽",
    			"item_code": "090430",
    			"item_count": 300,
    			"avg_price": 173000
    		},
    		{
    			"item_name": "셀트리온",
    			"item_code": "068270",
    			"item_count": 200,
    			"avg_price": 210000
    		}
    	]
    }
    
    
    >>> mod = Simulator()
    # 시뮬레이터 클래스 생성
    
    >>> mod.insert_order(order)
    # 주문서 삽입
    
    >>> mod.set_cash(10000000)
    # 초기자본세팅
    
    >>> mod.simulation()
    # 주문서로 시뮬레이션 실행
    # 시뮬레이션이 끝난 후 멤버변수인 _trd_log와 _stu_log에 기록이 담겨있다.    
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
        
        self._trd_log = pd.DataFrame(columns=
                                     ['order_datetime', 
                                      'order_type', 
                                      'item_code', 
                                      'item_name', 
                                      'order_value',
                                      'order_count',
                                      'price', 
                                      'avg_price', 
                                      'res_cash', 
                                      'hold'])
        
        self._stu_log = pd.DataFrame(columns=
                                     ['item_code',
                                      'item_name',
                                      'item_count',
                                      'avg_price',
                                      'buy_count',
                                      'sell_count'])
        
        self.buy_count = 0
        self.sell_count = 0
        self._cash = 0

    def read_file(self,
                file_name:str,                
                path=None,
                full_path=False) -> bool:
        """
        주문파일을 읽어 insert_order 함수에 전달한다.
                
        Parameters
        ----------
        file_name:
            전략파일 이름
        path

        Returns
        -------
        boolean.
        """
        if full_path:
            file = pathlib.Path(path)
            self.stock_name = file_name.split('_')
        else:
            file = pathlib.Path(path+'/orderFile/'+file_name)
            self.stock_name = file_name.split('_')
        
        try:
            text = file.read_text(encoding='utf-8')

        except FileNotFoundError:
            self.print_error(5)
            return False

        js = json.loads(text)
        self.insert_order(pd.DataFrame(js))

        return True
        
    def insert_order(self, odf):        
        '''
        주문서를 입력하는 함수이다.
        
        Parameters
        ----------
        odf : DataFrame
            주문내역이 들어있는 데이터프레임

        Returns
        -------
        None.
        '''
        
        self._order_sheet = odf

    def set_status(self, sdf):        
        '''
        보유금액과 보유종목을 입력할 수 있는 함수이다.
        특정 시뮬레이션을 수행하고 상태를 이어서 진행하고 싶을 때 사용
    
        Parameters
        ----------
        sdf : DataFrame
            보유금액과 보유종목이 들어있는 데이터프레임

        Returns
        -------
        None.
        '''
        
        self._cash = sdf['cash']
        self.CASH = sdf['cash']
        self._stu_log = pd.DataFrame(sdf['stock'])
    
    def set_cash(self, cv):       
        '''
        초기자본금 설정을 위한 함수이다.
        
        Parameters
        ----------
        cv : int
            초기자본금

        Returns
        -------
        None.
        '''
        
        self._cash = cv
        self.CASH = cv
    
    def set_option(self, buying_fee, selling_fee, National_tax,
                   slippage, connect_network):        
        '''
        시뮬레이션 옵션 설정을 위한 함수이다.
        
        Parameters
        ----------
        _b_f : float or int
            매수 수수료
            
        _s_f : float or int
            매도 수수료

        _n_f : float or int
            세금

        _slippage: float or int
            슬리피지

        _c_n : bool
            네트워크 연결 여부

        Returns
        -------
        None.
        '''
        
        self._buying_fee = buying_fee*0.01
        self._selling_fee = selling_fee*0.01
        self._national_tax = National_tax*0.01
        self._weight = self._buying_fee + self._selling_fee + self._national_tax
        self._slippage = slippage
        self._connect_network = connect_network

    def get_price(self, pr):        
        '''
        finance datareader를 이용하여 가격정보를 가져오는 함수이다.

        Parameters
        ----------
        pr : DataFrame(row)
            특정날짜의 주문내역.
            루프가 진행중인 데이터프레임의 한 '행'이다.

        Returns
        -------
        Price : boolean or int
            가격정보가 존재하지 않는다면 False를 반환
        '''       
        if self._connect_network:
            try:
                pdf = fdr.DataReader(pr.item_code, pr.order_datetime, pr.order_datetime)
            except:
                self.print_error(4)
            
            if len(pdf) == 0:
                self.print_error(4)
                return False
            
            ran = int(pr.order_price)*self._slippage
    
            if not int(pdf['High'])+ran > int(pr.order_price) > int(pdf['Low'])-ran:
    
                self.print_error(3)
                return False
            
            return int(pdf['Close'])
        
        elif not self._connect_network:
            return int(pr.order_price)
            
    def trade(self, tr):        
        '''
        매수 or 매도에 따라 거래 실행
        
        Parameters
        ----------
        tr : DataFrame(row)
            특정날짜의 주문내역.
            루프가 진행중인 데이터프레임의 한 '행'이다.

        Returns
        -------
        None.
        '''
        
        if tr.order_type == 'buy': self.buy(tr)
            
        if tr.order_type == 'sell': self.sell(tr)
    
    def buying(self, byr, bvc, bvm):        
        '''
        매수주문금액, 매수주문량을 입력받고 주문결과를 로그에 기록한다.

        Parameters
        ----------
        byr : DataFrame(row)        
            특정날짜의 주문내역.            
            루프가 진행중인 데이터프레임의 한 '행'이다.
            
        bvc : int        
            매수량
            
        bvm : int        
            매수가격

        Returns
        -------
        None.
        '''
        
        if len(self._stu_log[self._stu_log['item_code']==byr.item_code]['item_count']) != 0:
                
            itemvalue\
                =int(self._stu_log[self._stu_log['item_code']==byr.item_code]['item_count']) + bvc

            avgprice\
                =(bvm + (self._stu_log[self._stu_log['item_code']==byr.item_code]['avg_price']
                    * self._stu_log[self._stu_log['item_code']==byr.item_code]['item_count'])) / int(itemvalue)
                
        else:
            itemvalue = bvc
            avgprice = int(byr.order_price)
        
        self.buy_count = self.buy_count + 1

        bslog = {'item_code' : byr.item_code,
                'item_name' : byr.item_name,
                'item_count' : int(itemvalue),
                'avg_price' : int(avgprice),
                'buy_count': self.buy_count,
                'sell_count': self.sell_count}

        btlog = {'order_datetime' : byr.order_datetime, 
                'order_type' : byr.order_type, 
                'item_code' : byr.item_code, 
                'item_name' : byr.item_name, 
                'order_value' : bvm,
                'order_count' : bvc,
                'price' : int(byr.order_price),
                'avg_price' : int(avgprice),
                'res_cash' : int(self._cash - bvm),
                'hold' : int(itemvalue)}
        
        self._cash = int(self._cash - bvm)
        self._stu_log = self._stu_log.append(bslog, ignore_index='True').\
                        drop_duplicates(["item_code"], keep="last")
        self._trd_log = self._trd_log.append(btlog, ignore_index='True')
    
    def buy(self, br):        
        '''
        매수 옵션에 따라 거래 진행

        Parameters
        ----------
        br : DataFrame(row)
            특정날짜의 주문내역.
            루프가 진행중인 데이터프레임의 한 '행'이다.

        Returns
        -------
        None.    
        '''
        volcount = int() # 주문수량
        volmoney = int() # 주문수량 * 주문가
        
        if br.order_option == 'all':
            volcount = int(self._cash / int(br.order_price))
            volmoney = volcount * int(br.order_price)          

            if self._cash < volmoney:
                self.print_error(1)
                return   

        if br.order_option == 'por':            
            polcash = self._cash * float(br.order_value)
            volcount = int(polcash / int(br.order_price))
            volmoney = volcount * int(br.order_price)
            
            if polcash < volmoney:
                self.print_error(1)
                return         
            
        if br.order_option == 'cash':
            volcount = int(int(br.order_value) / int(br.order_price))
            volmoney = volcount * int(br.order_price)

            if self._cash < volmoney:
                # 1주의 가격이 보유 현금보다 작을 땐 리턴
                # or 1주 가격이 입력가격보다 클 때
                if int(br.order_price) > self._cash\
                    or int(br.order_price) > int(br.order_value):  
                    self.print_error(1)
                    return

                else:
                    volcount = int(self._cash / int(br.order_price))
                    volmoney = volcount * int(br.order_price)   

        if br.order_option == 'scnt':
            volcount = int(br.order_value)
            volmoney = volcount * int(br.order_price)

            if self._cash < volmoney:
                if int(br.order_price) > self._cash:
                    self.print_error(1)
                    return
                
                else:
                    volcount = int(self._cash / int(br.order_price))
                    volmoney = volcount * int(br.order_price)

        if br.order_option == 'm_por':
            polcash = self.CASH * float(br.order_value) # 총거래할 수 있는 금액

            volcount = int(polcash / int(br.order_price))
            volmoney = volcount * int(br.order_price)

            '''
            volmoney > self._cash 일 때 
            br.order_price > self._cash인지 확인
            True일 때 return
            False일 때 volcount = self._cash / br.order_price로 계산
            '''

            if self._cash < volmoney:
                if int(br.order_price) > self._cash:
                    self.print_error(1)
                    return
                else:
                    volcount = int(self._cash / int(br.order_price))
                    volmoney = volcount * int(br.order_price)
            
        self.buying(br, volcount, volmoney)
        
    def selling(self, syr, svc, svm):
        '''
        매도주문금액, 매도주문량을 입력받고 주문결과를 로그에 기록한다.

        Parameters
        ----------
        syr : DataFrame(row)
            특정날짜의 주문내역.
            루프가 진행중인 데이터프레임의 한 '행'이다.
        
        svc : int
            매도량
            
        svm :
            매도금액
        
        Returns
        -------
        None.
        '''
        fsvm = int(svm-(svm*self._weight))
        
        itemvalue = int(self._stu_log[self._stu_log['item_code']==syr.item_code]['item_count']) - svc
        
        avgprice = int(self._stu_log[self._stu_log['item_code']==syr.item_code]['avg_price'])

        self.sell_count = self.sell_count + 1
        
        sslog = {'item_code' : syr.item_code,
                'item_name' : syr.item_name,
                'item_count' : int(itemvalue),
                'avg_price' : int(avgprice),
                'buy_count' : self.buy_count,
                'sell_count' : self.sell_count}

        stlog = {'order_datetime' : syr.order_datetime, 
                'order_type' : syr.order_type, 
                'item_code' : syr.item_code, 
                'item_name' : syr.item_name, 
                'order_value' : fsvm,
                'order_count' : svc,
                'price' : int(syr.order_price),
                'avg_price' : int(avgprice),
                'res_cash' : int(self._cash + fsvm),
                'hold' : int(itemvalue)}
        
        self._cash = int(self._cash + fsvm)
        self._stu_log = self._stu_log.append(sslog, ignore_index='True').\
                        drop_duplicates(["item_code"], keep="last")
        self._trd_log = self._trd_log.append(stlog, ignore_index='True')
        
    def sell(self, sr):        
        '''
        매도 옵션에 따라 거래 진행

        Parameters
        ----------
        sr : DataFrame(row)
            특정날짜의 주문내역.
            루프가 진행중인 데이터프레임의 한 '행'이다.

        Returns
        -------
        None.
        '''
        
        if sr.order_option == 'all':
            if self._stu_log.empty:
                self.print_error(2)
                return

            if self._stu_log[self._stu_log['item_code']==sr.item_code]['item_count'].values[0] == 0:
                self.print_error(2)
                return
            
            volcount\
                = int(self._stu_log[self._stu_log['item_code']==sr.item_code]['item_count'])

            volmoney = volcount * int(sr.order_price)
            
            self.selling(sr, volcount, volmoney)
            
        if sr.order_option == 'por':
            if self._stu_log.empty:
                self.print_error(2)
                return

            if self._stu_log[self._stu_log['item_code']==sr.item_code]['item_count'].values[0] == 0:
                self.print_error(2)
                return
            
            volcount\
                = int(int(self._stu_log[self._stu_log['item_code']==sr.item_code]['item_count']) * float(sr.order_value))

            volmoney = volcount * int(sr.order_price)
            
            self.selling(sr, volcount, volmoney)
            
        if sr.order_option == 'scnt':
            if self._stu_log.empty:
                self.print_error(2)
                return

            if self._stu_log[self._stu_log['item_code']==sr.item_code]['item_count'].values[0] == 0 or \
                int(self._stu_log[self._stu_log['item_name']==sr.item_name]['item_count']) < int(sr.order_value):
                self.print_error(2)
                return
            
            volcount = int(sr.order_value)
            volmoney = volcount * int(sr.order_price)
            
            self.selling(sr, volcount, volmoney)

        if sr.order_option == 'm_por':  
            if self._stu_log.empty:
                self.print_error(2)
                return

            if self._stu_log[self._stu_log['item_code']==sr.item_code]['item_count'].values[0] == 0:
                self.print_error(2)
                return
            
            volcount\
                = int(int(self._stu_log[self._stu_log['item_code']==sr.item_code]['item_count']) * float(sr.order_value))

            volmoney = volcount * int(sr.order_price)
            
            self.selling(sr, volcount, volmoney)
        
    def write_trlog(self, path, file_name:str=''):        
        '''
        Write TraingLog.json

        Parameters
        ----------
        tpath:string            
            저장할 경로, default 'cwd'
        file_name:string
            TradingLog.json의 파일명을 입력받는다. 

        Returns
        -------
        None.
        '''

        os.makedirs(path+'/tradingLogFile', exist_ok=True)
        
        if self._trd_log.empty:
            return
        else:
            tdict = self._trd_log.to_dict(orient='records')
            #json.dumps(tdict, ensure_ascii=False, indent='\t')
            if file_name == '':
                with open(f"{path}/tradingLogFile/{self.stock_name[0]}_{self.stock_name[1]}_TradingLog.json", 'w+', encoding='utf-8') as make_file:
                    json.dump(tdict, make_file, ensure_ascii=False, indent='\t')
            else:
                with open(f"{path}/tradingLogFile/{file_name}_TradingLog.json", 'w+', encoding='utf-8') as make_file:
                    json.dump(tdict, make_file, ensure_ascii=False, indent='\t')
    
    def write_stlog(self, path, file_name:str=''):        
        '''
        Write Status.json

        Parameters
        ----------
        path : string            
            저장할 경로, default 'cwd'
        file_name:string
            statusFile.json의 파일명을 입력받는다. 


        Returns
        -------
        None.          
        '''
        os.makedirs(path+'/statusFile', exist_ok=True)        
        
        if self._stu_log.empty:
            return
        else:
            sdict = self._stu_log.to_dict(orient='records')
            sdict = {'cash' : self._cash, 'stock' : sdict}
            #json.dumps(tdict, ensure_ascii=False, indent='\t')
            if file_name == '':
                with open(f"{path}/statusFile/{self.stock_name[0]}_{self.stock_name[1]}_Status.json", 'w+', encoding='utf-8') as make_file:
                    json.dump(sdict, make_file, ensure_ascii=False, indent='\t')
            else:
                with open(f"{path}/statusFile/{file_name}_Status.json", 'w+', encoding='utf-8') as make_file:
                    json.dump(sdict, make_file, ensure_ascii=False, indent='\t')
        
    def get_Tcount(self):
        '''
        return buy and sell count

        Parameters
        ----------

        Returns
        -------
        buy_count, sell_count
            매수, 매도 횟수, integer    
        '''
        try:
            return self._stu_log['buy_count'].values[0], self._stu_log['sell_count'].values[0]
        except IndexError:
            print('거래 기록이 없습니다.')
            return False
        
    def simulation(self):        
        '''
        수익률 시뮬레이션을 수행한다.

        Parameters
        ----------

        Returns
        -------
        None.    
        '''
        
        for _, row in self._order_sheet.iterrows():            
            price = self.get_price(row)

            if not price:
                continue

            self.trade(row)
            print(self._trd_log)

    def reset_simulator(self):
        '''
        클래스 멤버변수를 초기화하는 함수이다.        
        
        Parameters
        ----------

        Returns
        -------
        None.
        '''
        self._trd_log = pd.DataFrame(columns=
                                     ['order_datetime', 
                                      'order_type', 
                                      'item_code', 
                                      'item_name', 
                                      'order_value',
                                      'order_count',
                                      'price', 
                                      'avg_price', 
                                      'res_cash', 
                                      'hold'])
        
        self._stu_log = pd.DataFrame(columns=
                                     ['item_code',
                                      'item_name',
                                      'item_count',
                                      'avg_price',
                                      'buy_count',
                                      'sell_count'])
        
        self.buy_count = 0
        self.sell_count = 0
        self._cash = 0
        
    def print_error(self, erc):
        '''        
        Parameters
        ----------
        erc : TYPE
            DESCRIPTION.

        Returns
        -------
        None.
        
        warning code 1 -> 최소현금이 부족하여 구매불가
        warning code 2 -> 종목을 보유하지 않았거나 보유량이 부족하여 판매불가
        warning code 3 -> 매수 or 매도 희망가격이 고가와 저가 사이가 아님
        warning code 4 -> Finance Data로부터 데이터를 불러올 수 없음
        warning code 5 -> order file이 존재하지 않음
        warning code
        '''
        
        error = {1 : '최소현금이 부족하여 구매불가',
                 2 : '종목을 보유하지 않았거나 보유량이 부족하여 판매불가',
                 3 : '매수 or 매도 희망가격이 고가와 저가 사이가 아님',
                 4 : 'Finance Data로부터 데이터를 불러올 수 없음',
                 5 : '주문파일이 존재하지 않습니다.'}
        
        print('simulator warning code {} : {}'.format(erc, error[erc]))

if __name__ == '__main__':
    
    import pandas as pd
    import pathlib
    import json
    import os

    # file = pathlib.Path(os.getcwd()+'/orderFile/SK하이닉스_d_Order.json')
    # text = file.read_text(encoding='utf-8')
    # js = json.loads(text)
    # order = pd.DataFrame(js)
    
    #file = pathlib.Path(os.getcwd()+'\\statuslog.json')
    #text = file.read_text(encoding='utf-8')
    #status = json.loads(text)
    
    mod = Simulator()
    
    # mod.insert_order(order)
    
    #mod.set_status(status)

    mod.read_file('LG유플러스_d_Order.json')
    
    # 매수수수료, 매도수수료, 국가세금, 슬리피지 허용범위, 네트워크사용 유무
    mod.set_option(0.015, 0.015, 0.23, 0.01, True)
    
    mod.set_cash(10000000)
    
    mod.simulation()
    
    mod.write_trlog()
    
    mod.write_stlog()

    if mod.get_Tcount():
        print('ok')
    else:
        print('nok')