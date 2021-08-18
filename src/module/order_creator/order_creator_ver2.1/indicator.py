import talib as ta

"""
Created on 2021.1.23

기술적지표 값을 생성하여 데이터프레임 컬럼에 추가

컬럼명 정의 규칙
-> 가장 많이 사용하는 파라미터 값을 underscore로 연결하여 정한다.
예) 
add_RSI(period=p1, price='close') → 컬럼명은 rsi_p1
add_BBands(period=p1, nbdevup=p2, nbdevdn=p3, price=p4) → 컬럼명은 ubb_p1_p2_p3, mbb_p1_p2_p3, lbb_p1_p2_p3 

@author: 김상혁
"""

def add_BBands(
    df: "DataFrame",
    period=20,
    nbdevup=2,
    nbdevdn=2,
    price='close'
    ) -> "DataFrame":
    """
    볼린져밴드(상단선, 중심선, 하단선) 값을 데이터프레임 컬럼에 추가한다.
    리턴을 받지 않아도 함수의 인자로 준 DataFrame에 컬럼이 추가된다.
    
    Parameters
    ----------
    df: Stock price DataFrame
    period: Period in integer, default 20
        이동평균 기간
    nbdevup: Integer to multiply, defalut 2
        표준편차에 곱할 값(상단)
    nbdevdn: Integer to multiply, defalut 2
        표준편차에 곱할 값(하단)        
    price: {'open', 'close', 'high', 'low'} default 'close'
        기술적지표를 생성할 기준 가격
        
    Returns
    -------
    DataFrame
        주가가격 데이터프레임
    """
    if type(period) is not int:
        print('BBands error')
        print_error(1)
        return False

    elif price not in ['open', 'high', 'low', 'close']:
        print('BBands error')
        print_error(2)
        return False

    elif type(nbdevup) is not int or type(nbdevdn) is not int:
        print('BBands error')
        print_error(3)
        return False

    # 볼린져 밴드 값 생성
    ubb, mbb, lbb = ta.BBANDS(df[price], timeperiod=period, nbdevup=nbdevup, nbdevdn=nbdevdn) 

    df['ubb_'+str(period)+'_'+str(nbdevup)+'_'+str(nbdevdn)] = ubb
    df['mbb_'+str(period)+'_'+str(nbdevup)+'_'+str(nbdevdn)] = mbb
    df['lbb_'+str(period)+'_'+str(nbdevup)+'_'+str(nbdevdn)] = lbb

    return df

def add_RSI(df: "DataFrame", period=14, price='close') -> "DataFrame":
    """
    RSI 값을 데이터프레임 컬럼에 추가한다.
    리턴을 받지 않아도 함수의 인자로 준 DataFrame에 컬럼이 추가된다.
    
    Parameters
    ----------
    df: Stock price DataFrame
    period: Period in integer, default 14
        과거 확인 기간     
    price: {'open', 'close', 'high', 'low'} default 'close'
        기술적지표를 생성할 기준 가격
        
    Returns
    -------
    DataFrame
        주가가격 데이터프레임
    """
    if type(period) is not int:
        print('RSI error')
        print_error(1)
        return False

    elif price not in ['open', 'high', 'low', 'close']:
        print('RSI error')
        print_error(2)
        return False
    
    rsi = ta.RSI(df[price], timeperiod=period)

    df['rsi_'+str(period)] = rsi

    return df

def add_MACD(
    df: "DataFrame",
    fast_period=12,
    slow_period=26,
    signal_period=9,
    price='close'
    ) -> "DataFrame":
    """
    MACD(macd, macd_signal, macd_hist) 값을 데이터프레임 컬럼에 추가한다.
    리턴을 받지 않아도 함수의 인자로 준 DataFrame에 컬럼이 추가된다.
    
    Parameters
    ----------
    df: Stock price DataFrame
    fast_period: Period in integer, default 12
        단기 이동평균 기간
    slow_period: Integer to multiply, defalut 26
        장기 이동평균 기간
    signal_period: Integer to multiply, defalut 9
        macd에 적용할 이동평균 기간
    price: {'open', 'close', 'high', 'low'} default 'close'
        기술적지표를 생성할 기준 가격
        
    Returns
    -------
    DataFrame
        주가가격 데이터프레임
    """
    if type(fast_period) is not int\
    or type(slow_period) is not int\
    or type(signal_period) is not int:
        print('MACD error')
        print_error(1)
        return False

    elif price not in ['open', 'high', 'low', 'close']:
        print('MACD error')
        print_error(2)
        return False
  
    macd, macd_signal, macd_hist = ta.MACD(df[price], fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)

    df['macd_'+str(fast_period)+'_'+str(slow_period)+'_'+str(signal_period)] = macd
    df['macd_signal_'+str(fast_period)+'_'+str(slow_period)+'_'+str(signal_period)] = macd_signal
    df['macd_hist_'+str(fast_period)+'_'+str(slow_period)+'_'+str(signal_period)] = macd_hist
    
    return df

def add_STOCH(
    df:"DataFrame",
    fastk_period=5,
    slowk_period=3,
    slowd_period=3,
    price1='high',
    price2='low',
    price3='close'
    ) -> "DataFrame":
    """
    Stochastic(slowk(fast %K를 M기간으로 이동평균), slowd(slow %K를 T기간으로 이동평균)) 값을 데이터프레임 컬럼에 추가한다.
    리턴을 받지 않아도 함수의 인자로 준 DataFrame에 컬럼이 추가된다.
    
    Parameters
    ----------
    df: Stock price DataFrame
    fast_period: Period in integer, default 5
        과거 확인 기간(N)
    slow_period: Integer to multiply, defalut 3
        fastk 이동평균 기간(M)
    signal_period: Integer to multiply, defalut 3
        slowk 이동평균 기간(T)
    price1: {'open', 'close', 'high', 'low'} default 'high'
        기술적지표를 생성할 기준 가격
    price2: {'open', 'close', 'high', 'low'} default 'low'
        기술적지표를 생성할 기준 가격
    price3: {'open', 'close', 'high', 'low'} default 'close'
        기술적지표를 생성할 기준 가격
        
    Returns
    -------
    DataFrame
        주가가격 데이터프레임
    """
    if type(fastk_period) is not int\
        or type(slowk_period) is not int\
            or type(slowd_period) is not int:
        print('STOCH error')
        print_error(1)
        return False

    elif price1 not in ['open', 'high', 'low', 'close']\
        or price2 not in ['open', 'high', 'low', 'close']\
            or price3 not in ['open', 'high', 'low', 'close']:
        print('STOCH error')
        print_error(2)
        return False

    slowk, slowd = ta.STOCH(df[price1], df[price2], df[price3], fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
    
    df['slowk_'+str(fastk_period)+'_'+str(slowk_period)+'_'+str(slowd_period)] = slowk
    df['slowd_'+str(fastk_period)+'_'+str(slowk_period)+'_'+str(slowd_period)] = slowd

    return df

def add_STOCHF(df:"DataFrame",
    fastk_period=5,
    fastd_period=3,
    price1='high',
    price2='low',
    price3='close'
    ) -> "DataFrame":
    """
    Stochastic Fast(fastk(fast %K를 M기간으로 이동평균), fastd(slow %K를 T기간으로 이동평균)) 값을 데이터프레임 컬럼에 추가한다.
    리턴을 받지 않아도 함수의 인자로 준 DataFrame에 컬럼이 추가된다.
    
    Parameters
    ----------
    df: Stock price DataFrame
    fastk_period: Period in integer, default 5
        과거 확인 기간(N)
    fastd_period: Integer to multiply, defalut 3
        fastk 이동평균 기간(M)    
    price1: {'open', 'close', 'high', 'low'} default 'high'
        기술적지표를 생성할 기준 가격
    price2: {'open', 'close', 'high', 'low'} default 'low'
        기술적지표를 생성할 기준 가격
    price3: {'open', 'close', 'high', 'low'} default 'close'
        기술적지표를 생성할 기준 가격
        
    Returns
    -------
    DataFrame
        주가가격 데이터프레임
    """
    if type(fastk_period) is not int\
        or type(fastd_period) is not int:
        print('STOCHF error')
        print_error(1)        
        return False

    elif price1 not in ['open', 'high', 'low', 'close']\
        or price2 not in ['open', 'high', 'low', 'close']\
            or price3 not in ['open', 'high', 'low', 'close']:
        print('STOCHF error')
        print_error(2)
        return False

    fastk, fastd = ta.STOCHF(df[price1], df[price2], df[price3], fastk_period=fastk_period, fastd_period=fastd_period)
    
    df['fastk_'+str(fastk_period)+'_'+str(fastd_period)] = fastk
    df['fastd_'+str(fastk_period)+'_'+str(fastd_period)] = fastd

    return df

def add_MA(df: "DataFrame", period=10, price='close') -> "DataFrame":
    """
    MA(moving average) 값을 데이터프레임 컬럼에 추가한다.
    리턴을 받지 않아도 함수의 인자로 준 DataFrame에 컬럼이 추가된다.
    
    Parameters
    ----------
    df: Stock price DataFrame
    period: Period in integer, default 10
        이동평균 기간     
    price: {'open', 'close', 'high', 'low'} default 'close'
        기술적지표를 생성할 기준 가격
        
    Returns
    -------
    DataFrame
        주가가격 데이터프레임
    """
    if type(period) is not int:
        print('MA error')
        print_error(1)
        return False

    elif price not in ['open', 'high', 'low', 'close']:
        print('MA error')
        print_error(2)
        return False

    ma = ta.MA(df[price], timeperiod=period)
    
    # 입력한 기간의 ma를 row의 이름으로 정함
    df['ma_'+str(period)] = ma

    return df

def add_EMA(df: "DataFrame", period=30, price='close') -> "DataFrame":
    """
    EMA(Exponential moving average) 값을 데이터프레임 컬럼에 추가한다.
    리턴을 받지 않아도 함수의 인자로 준 DataFrame에 컬럼이 추가된다.
    
    Parameters
    ----------
    df: Stock price DataFrame
    period: Period in integer, default 30
        이동평균 기간     
    price: {'open', 'close', 'high', 'low'} default 'close'
        기술적지표를 생성할 기준 가격
        
    Returns
    -------
    DataFrame
        주가가격 데이터프레임
    """
    if type(period) is not int:
        print('EMA error')
        print_error(1)
        return False

    elif price not in ['open', 'high', 'low', 'close']:
        print('EMA error')
        print_error(2)
        return False

    ema = ta.EMA(df[price], timeperiod=period)

    df['ema_'+str(period)] = ema
    
    return df

def add_CMO(df: "DataFrame", period=14, price='close') -> "DataFrame":
    """
    CMO(Chande) Momentum Oscillator) 값을 데이터프레임 컬럼에 추가한다.
    리턴을 받지 않아도 함수의 인자로 준 DataFrame에 컬럼이 추가된다.
    
    Parameters
    ----------
    df: Stock price DataFrame
    period: Period in integer, default 30
        이동평균 기간     
    price: {'open', 'close', 'high', 'low'} default 'close'
        기술적지표를 생성할 기준 가격
        
    Returns
    -------
    DataFrame
        주가가격 데이터프레임
    """
    if type(period) is not int:
        print('CMO error')
        print_error(1)
        return False

    elif price not in ['open', 'high', 'low', 'close']:
        print('CMO error')
        print_error(2)
        return False

    cmo = ta.CMO(df[price], timeperiod=period)

    df['cmo_'+str(period)] = cmo

    return df

def print_error(erc:int) -> None:
    """        
    Parameters
    ----------
    erc : TYPE
        DESCRIPTION.

    Returns
    -------
    None.
    
    error code 1 -> 기간을 정수로 입력하지 않음
    error code 2 -> 가격 이름이 잘못됨
    error code 3 -> 표준편차에 곱할 값을 정수로 입력해야함
    error code 4 -> 
    error code 5 -> 
    """        
    error = {1 : '기간은 정수로 입력하세요.',
            2 : "'open', 'high', 'low', 'close' 중에서 가격을 입력하세요",
            3 : "표준편차에 곱할 값을 정수로 입력하세요"}

    print('indicator error code {} : {}'.format(erc, error[erc]))

if __name__ == "__main__":
    from core.order_creator.gatherer import Gatherer
    import time    
    import pandas as pd
    import os
    
    # local mode
    # df = pd.read_csv(os.getcwd()+'/stockFile/'+'SK하이닉스_d.csv', index_col='Date')
    # add_BBands(df, 20, 2, 2)

    # add_RSI(df)

    # df.to_csv(os.getcwd()+'/stockFile/'+'SK하이닉스_d.csv', index_label='Date')

    # startTime = time.time()

    mod = Gatherer()
    
    df, _ = mod.get_stock('000660', '2020-01-01', interval='d', save=False)   

    # add_MACD(df)
        
    # add_EMA(df, 12, 'ext')
    # add_EMA(df, 26)

    # df['ema12-ema26'] = df['ema_12'] - df['ema_26']
    # df['signal'] = ta.EMA(df['ema12-ema26'], 9)
    # add_STOCH(df)

    # add_STOCHF(df)

    # add_CMO(df)

    # add_EMA(df)
    
    # end_time = time.time()

    # print("WorkingTime: {} sec".format(end_time-startTime))

    print(df)

    