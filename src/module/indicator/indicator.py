import talib as ta
import talib.stream
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import itertools
from datetime import datetime
from dateutil.relativedelta import relativedelta

"""
Created on 2021.1.23

기술적지표 값을 생성하여 데이터프레임 컬럼에 추가

컬럼명 정의 규칙
-> 가장 많이 사용하는 파라미터 값을 underscore로 연결하여 정한다.
예) 
add_RSI(period=p1, target='close') → 컬럼명은 rsi_p1
add_BBands(period=p1, nbdevup=p2, nbdevdn=p3, target=p4) → 컬럼명은 ubb_p1_p2_p3, mbb_p1_p2_p3, lbb_p1_p2_p3 

@author: 김상혁
"""

def add_bbands(
    df: pd.DataFrame,
    period=20,
    nbdevup=2,
    nbdevdn=2,
    target='close'
    ) -> pd.DataFrame:
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
    target: {'open', 'close', 'high', 'low'} default 'close'
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

    elif target not in ['open', 'high', 'low', 'close']:
        print('BBands error')
        print_error(2)
        return False

    elif type(nbdevup) is not int or type(nbdevdn) is not int:
        print('BBands error')
        print_error(3)
        return False

    # 볼린져 밴드 값 생성
    ubb, mbb, lbb = ta.BBANDS(df[target], timeperiod=period, nbdevup=nbdevup, nbdevdn=nbdevdn) 

    df['ubb_'+str(period)+'_'+str(nbdevup)+'_'+str(nbdevdn)] = ubb
    df['mbb_'+str(period)+'_'+str(nbdevup)+'_'+str(nbdevdn)] = mbb
    df['lbb_'+str(period)+'_'+str(nbdevup)+'_'+str(nbdevdn)] = lbb

    return df

def add_rsi(df: pd.DataFrame, period=14, target='close') -> pd.DataFrame:
    """
    RSI 값을 데이터프레임 컬럼에 추가한다.
    리턴을 받지 않아도 함수의 인자로 준 DataFrame에 컬럼이 추가된다.
    
    Parameters
    ----------
    df: Stock price DataFrame
    period: Period in integer, default 14
        과거 확인 기간     
    target: {'open', 'close', 'high', 'low'} default 'close'
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

    elif target not in ['open', 'high', 'low', 'close']:
        print('RSI error')
        print_error(2)
        return False
    
    rsi = ta.RSI(df[target], timeperiod=period)

    df['rsi_'+str(period)] = rsi

    return df

def add_macd(
    df: pd.DataFrame,
    fast_period=12,
    slow_period=26,
    signal_period=9,
    target='close'
    ) -> pd.DataFrame:
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
    target: {'open', 'close', 'high', 'low'} default 'close'
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

    elif target not in ['open', 'high', 'low', 'close']:
        print('MACD error')
        print_error(2)
        return False
  
    macd, macd_signal, macd_hist = ta.MACD(df[target], fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)

    df['macd_'+str(fast_period)+'_'+str(slow_period)+'_'+str(signal_period)] = macd
    df['macd_signal_'+str(fast_period)+'_'+str(slow_period)+'_'+str(signal_period)] = macd_signal
    df['macd_hist_'+str(fast_period)+'_'+str(slow_period)+'_'+str(signal_period)] = macd_hist
    
    return df

def add_stoch(
    df:pd.DataFrame,
    fastk_period=5,
    slowk_period=3,
    slowd_period=3,
    target1='high',
    target2='low',
    target3='close'
    ) -> pd.DataFrame:
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
    target1: {'open', 'close', 'high', 'low'} default 'high'
        기술적지표를 생성할 기준 가격
    target2: {'open', 'close', 'high', 'low'} default 'low'
        기술적지표를 생성할 기준 가격
    target3: {'open', 'close', 'high', 'low'} default 'close'
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

    elif target1 not in ['open', 'high', 'low', 'close']\
        or target2 not in ['open', 'high', 'low', 'close']\
            or target3 not in ['open', 'high', 'low', 'close']:
        print('STOCH error')
        print_error(2)
        return False

    slowk, slowd = ta.STOCH(df[target1], df[target2], df[target3], fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
    
    df['slowk_'+str(fastk_period)+'_'+str(slowk_period)+'_'+str(slowd_period)] = slowk
    df['slowd_'+str(fastk_period)+'_'+str(slowk_period)+'_'+str(slowd_period)] = slowd

    return df

def add_stochf(df:pd.DataFrame,
    fastk_period=5,
    fastd_period=3,
    target1='high',
    target2='low',
    target3='close'
    ) -> pd.DataFrame:
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
    target1: {'open', 'close', 'high', 'low'} default 'high'
        기술적지표를 생성할 기준 가격
    target2: {'open', 'close', 'high', 'low'} default 'low'
        기술적지표를 생성할 기준 가격
    target3: {'open', 'close', 'high', 'low'} default 'close'
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

    elif target1 not in ['open', 'high', 'low', 'close']\
        or target2 not in ['open', 'high', 'low', 'close']\
            or target3 not in ['open', 'high', 'low', 'close']:
        print('STOCHF error')
        print_error(2)
        return False

    fastk, fastd = ta.STOCHF(df[target1], df[target2], df[target3], fastk_period=fastk_period, fastd_period=fastd_period)
    
    df['fastk_'+str(fastk_period)+'_'+str(fastd_period)] = fastk
    df['fastd_'+str(fastk_period)+'_'+str(fastd_period)] = fastd

    return df

def add_ma(df: pd.DataFrame, period=10, target='close') -> pd.DataFrame:
    """
    MA(moving average) 값을 데이터프레임 컬럼에 추가한다.
    리턴을 받지 않아도 함수의 인자로 준 DataFrame에 컬럼이 추가된다.
    
    Parameters
    ----------
    df: Stock price DataFrame
    period: Period in integer, default 10
        이동평균 기간     
    target: {'open', 'close', 'high', 'low'} default 'close'
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

    # elif target not in ['open', 'high', 'low', 'close']:
    #     print('MA error')
    #     print_error(2)
    #     return False

    ma = ta.MA(df[target], timeperiod=period)
    
    # 입력한 기간의 ma를 row의 이름으로 정함
    df[f'ma_{str(period)}({target})'] = ma

    return df

def add_ema(df: pd.DataFrame, period=30, target='close') -> pd.DataFrame:
    """
    EMA(Exponential moving average) 값을 데이터프레임 컬럼에 추가한다.
    리턴을 받지 않아도 함수의 인자로 준 DataFrame에 컬럼이 추가된다.
    
    Parameters
    ----------
    df: Stock price DataFrame
    period: Period in integer, default 30
        이동평균 기간     
    target: {'open', 'close', 'high', 'low'} default 'close'
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

    elif target not in ['open', 'high', 'low', 'close']:
        print('EMA error')
        print_error(2)
        return False

    ema = ta.EMA(df[target], timeperiod=period)

    df[f'ema_{str(period)}({target})'] = ema
    
    return df

def add_cmo(df: pd.DataFrame, period=14, target='close') -> pd.DataFrame:
    """
    CMO(Chande) Momentum Oscillator) 값을 데이터프레임 컬럼에 추가한다.
    리턴을 받지 않아도 함수의 인자로 준 DataFrame에 컬럼이 추가된다.
    
    Parameters
    ----------
    df: Stock price DataFrame
    period: Period in integer, default 30
        이동평균 기간     
    target: {'open', 'close', 'high', 'low'} default 'close'
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

    elif target not in ['open', 'high', 'low', 'close']:
        print('CMO error')
        print_error(2)
        return False

    cmo = ta.CMO(df[target], timeperiod=period)

    df['cmo_'+str(period)] = cmo

    return df

def add_atr(df, period:int=14):
    """
    ATR 값을 데이터프레임 컬럼에 추가한다.
    리턴을 받지 않아도 함수의 인자로 준 DataFrame에 컬럼이 추가된다.
    
    Parameters
    ----------
    df: Stock price DataFrame
    period: period
                
    Returns
    -------
    DataFrame
        주가가격 데이터프레임
    """
    if type(period) is not int:
        print('ATR error')
        print_error(1)
        return False

    pd.set_option('mode.chained_assignment',  None) # <==== 경고를 끈다
    ready_df = pd.DataFrame(columns=
                                    ['H-L', 
                                    'H-PC', 
                                    'L-PC', 
                                    'TR', 
                                    'ATR',
                                    'Upper Basic',
                                    'Lower Basic', 
                                    'Upper Band', 
                                    'Lower Band'])
    #Calculation of ATR
    ready_df['H-L']=abs(df['high']-df['low'])
    ready_df['L-PC']=abs(df['low']-df['close'].shift(1))
    ready_df['TR']=ready_df[['H-L','H-PC','L-PC']].max(axis=1)

    col_name = 'atr'+str(period)
    df[col_name]=np.nan
    df[col_name][period-1] = ready_df['TR'][:period-1].copy().mean() #.ix is deprecated from pandas verion- 0.19

    for i in range(period,len(df)):
        df[col_name][i] = (df[col_name][i-1]*(period-1)+ ready_df['TR'][i])/period
    
    pd.set_option('mode.chained_assignment', 'warn') # <==== 경고를 킨다.
    
    return df

def add_st(df, factor=3, period:int=7): # df is the dataframe, n is the period, f is the factor; f=3, n=7 are commonly used.
    """
    Super Trand 값을 데이터프레임 컬럼에 추가한다.
    리턴을 받지 않아도 함수의 인자로 준 DataFrame에 컬럼이 추가된다.
    
    Parameters
    ----------
    df: Stock price DataFrame
    factor: factor
    period: period
                
    Returns
    -------
    DataFrame
        주가가격 데이터프레임
    """
    if type(factor) is str:
        print('SuperTrend error')
        print_error(4)
        return False

    if type(period) is not int:
        print('SuperTrend error')
        print_error(1)
        return False

    
    pd.set_option('mode.chained_assignment',  None) # <==== 경고를 끈다
    ready_df = pd.DataFrame(columns=
                                    ['H-L', 
                                    'H-PC', 
                                    'L-PC', 
                                    'TR', 
                                    'ATR',
                                    'Upper Basic',
                                    'Lower Basic', 
                                    'Upper Band', 
                                    'Lower Band'])
    #Calculation of ATR
    ready_df['H-L']=abs(df['high']-df['low'])
    ready_df['H-PC']=abs(df['high']-df['close'].shift(1))
    ready_df['L-PC']=abs(df['low']-df['close'].shift(1))
    ready_df['TR']=ready_df[['H-L','H-PC','L-PC']].max(axis=1)
    ready_df['ATR']=np.nan
    ready_df['ATR'][period-1] = ready_df['TR'][:period-1].copy().mean() #.ix is deprecated from pandas verion- 0.19

    for i in range(period,len(df)):
        ready_df['ATR'][i]=(ready_df['ATR'][i-1]*(period-1)+ ready_df['TR'][i])/period

    #Calculation of SuperTrend
    ready_df['Upper Basic'] = (df['high']+df['low'])/2 + (factor * ready_df['ATR'])
    ready_df['Lower Basic'] = (df['high']+df['low'])/2 - (factor * ready_df['ATR'])
    ready_df['Upper Band'] = ready_df['Upper Basic']
    ready_df['Lower Band'] = ready_df['Lower Basic']
    for i in range(period, len(df)):
        if df['close'][i-1] <= ready_df['Upper Band'][i-1]:
            ready_df['Upper Band'][i] = min(ready_df['Upper Basic'][i],ready_df['Upper Band'][i-1])
        else:
            ready_df['Upper Band'][i] = ready_df['Upper Basic'][i]

    for i in range(period, len(df)):
        if df['close'][i-1] >= ready_df['Lower Band'][i-1]:
            ready_df['Lower Band'][i] = max(ready_df['Lower Basic'][i],ready_df['Lower Band'][i-1])
        else:
            ready_df['Lower Band'][i]=ready_df['Lower Basic'][i]   
    
    col_name = 'st'+str(factor)+'_'+str(period)
    df[col_name]=np.nan
    for i in df[col_name]:
        if df['close'][period-1] <= ready_df['Upper Band'][period-1]:
            df[col_name][period-1] = ready_df['Upper Band'][period-1]
        elif df['close'][period-1] > ready_df['Upper Band'][period]:
            df[col_name][period-1] = ready_df['Lower Band'][period-1]

    for i in range(period,len(df)):
        if df[col_name][i-1] == ready_df['Upper Band'][i-1] and df['close'][i] <= ready_df['Upper Band'][i]:
            df[col_name][i]=ready_df['Upper Band'][i]
        elif  df[col_name][i-1] == ready_df['Upper Band'][i-1] and df['close'][i] >= ready_df['Upper Band'][i]:
            df[col_name][i] = ready_df['Lower Band'][i]
        elif df[col_name][i-1] == ready_df['Lower Band'][i-1] and df['close'][i] >= ready_df['Lower Band'][i]:
            df[col_name][i] = ready_df['Lower Band'][i]
        elif df[col_name][i-1] == ready_df['Lower Band'][i-1] and df['close'][i] <= ready_df['Lower Band'][i]:
            df[col_name][i] = ready_df['Upper Band'][i]
            
    # df['buy'] = df['SuperTrend'] < df['close']
    # df['sell'] = df['SuperTrend'] >= df['close']

    pd.set_option('mode.chained_assignment', 'warn') # <==== 경고를 킨다.
    
    return df

def add_clustering(
    df,
    n_clusters:int=2,
    target:str='close',
    period:str='1y',
    slide_size:str='1m') -> pd.DataFrame:
    """
    target을 n_clusters 개수만큼 군집화하여 centroid를 구한다.

    Parameters
    ----------
    df
        데이터프레임
    n_clusters
        군집개수
    target
        군집대상
        dataframe의 컬럼
    period
        클러스터링 기간
        숫자와 y, m, d를 조합하여 입력한다.(대소문자 구분없음)
        1년: 1y
        6개월: 6m
        30일: 30d
    slide_size
        slide 기간
        숫자와 y, m, d를 조합하여 입력한다.(대소문자 구분없음)
        1년: 1y
        1개월: 1m
        15일: 15d

    Returns
    -------
    DataFrame
    """
    df_list = list()

    c_period = int(period[:-1])
    c_interval = period[-1].lower()

    s_period = int(slide_size[:-1])
    s_interval = slide_size[-1].lower()
    
    fst_loop = True
    pd.set_option('mode.chained_assignment',  None) # <==== 경고를 끈다
    while True:
        if fst_loop:
            fst_end = df.index[0]
            if c_interval == 'y':
                snd_end = datetime.strptime(str(fst_end)[:10], "%Y-%m-%d") + relativedelta(years=c_period)
            elif c_interval == 'm':
                snd_end = datetime.strptime(str(fst_end)[:10], "%Y-%m-%d") + relativedelta(months=c_period)
            elif c_interval == 'd':
                snd_end = datetime.strptime(str(fst_end)[:10], "%Y-%m-%d") + relativedelta(days=c_period)
            
            if s_interval == 'y':
                trd_end = snd_end + relativedelta(years=s_period)
            elif s_interval == 'm':
                trd_end = snd_end + relativedelta(months=s_period)
            elif s_interval == 'd':
                trd_end = snd_end + relativedelta(days=s_period)

            snd_end = snd_end.strftime('%Y-%m-%d')
            trd_end = trd_end.strftime('%Y-%m-%d')

            fst_loop = False

        else:
            if s_interval == 'y':
                fst_end = datetime.strptime(str(fst_end)[:10], "%Y-%m-%d") + relativedelta(years=s_period)
            elif s_interval == 'm':
                fst_end = datetime.strptime(str(fst_end)[:10], "%Y-%m-%d") + relativedelta(months=s_period)
            elif s_interval == 'd':
                fst_end = datetime.strptime(str(fst_end)[:10], "%Y-%m-%d") + relativedelta(days=s_period)
            
            if c_interval == 'y':
                snd_end = fst_end + relativedelta(years=c_period)
            elif c_interval == 'm':
                snd_end = fst_end + relativedelta(months=c_period)
            elif c_interval == 'd':
                snd_end = fst_end + relativedelta(days=c_period)

            if s_interval == 'y':
                trd_end = snd_end + relativedelta(years=s_period)
            elif s_interval == 'm':
                trd_end = snd_end + relativedelta(months=s_period)
            elif s_interval == 'd':
                trd_end = snd_end + relativedelta(days=s_period)
            
            fst_end = fst_end.strftime('%Y-%m-%d')
            snd_end = snd_end.strftime('%Y-%m-%d')
            trd_end = trd_end.strftime('%Y-%m-%d')
        
        '''
        이벤트로 인해 주가데이터가 중간에 비는 경우가 발생함 -> 해결방안?
        1. 슬라이싱을 했을 때 빈데이터프레임이 나오면 continue로 다음 loop에 진입하면되지 않을까?
            1.1 clustering df 와 apply df가 모두 존재하는지 확인해야 함
        2. fst date, snd date, trd date가 모두 존재하는지 확인해야 함
        3. clustering df는 존재함 apply df는 존재하지 않으면 
         -> snd date, trd date를 계속 이동하면서 apply df가 존재할 때까지 이동함 
        '''
        clustering_df = df[fst_end:snd_end] # 클러스터링을 위한 df
        apply_df = df[snd_end:trd_end] # 클러스터링을 결과를 컬럼으로 갖는 df

        x = clustering_df[target].to_numpy().reshape(-1,1)
        km = KMeans(n_clusters=n_clusters)
        km.fit(x)

        centroids = km.cluster_centers_
        centroids = list(itertools.chain(*centroids.reshape(1,-1)))
        centroids = [round(x, 0) for x in centroids]

        apply_df['high_centroid'] = max(centroids)
        apply_df['low_centroid'] = min(centroids)
        df_list.append(apply_df)
        
        if datetime.strptime(str(df.index[-1])[:10], '%Y-%m-%d') < datetime.strptime(trd_end, '%Y-%m-%d'):
            break 

    result = pd.concat(df_list)
    result.reset_index('Date', inplace=True)
    result.drop_duplicates(['Date'], keep='last', inplace=True)
    result.set_index('Date', inplace=True)
    df['high_centroid'] = result['high_centroid']
    df['low_centroid'] = result['low_centroid']
    pd.set_option('mode.chained_assignment', 'warn') # <==== 경고를 킨다.
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
    
    warning code 1 -> 기간을 정수로 입력하지 않음
    warning code 2 -> 가격 이름이 잘못됨
    warning code 3 -> 표준편차에 곱할 값을 정수로 입력해야함
    warning code 4 -> 정수나 실수를 입력하세요 
    """        
    error = {1 : '기간은 정수로 입력하세요.',
            2 : "'open', 'high', 'low', 'close' 중에서 가격을 입력하세요",
            3 : "표준편차에 곱할 값을 정수로 입력하세요",
            4 : "정수나 실수를 입력하세요."}

    print('indicator warning code {} : {}'.format(erc, error[erc]))

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
    # from module.gatherer.gatherer import Gatherer
    import pandas as pd
    import os
    
    # local mode
    df = pd.read_csv(os.getcwd()+'/stockFile/이지홀딩스_d.csv', index_col='Date')
    # add_BBands(df, 20, 2, 2)

    # add_RSI(df, period=14)

    # print(df)
    # df.to_csv(os.getcwd()+'/stockFile/'+'삼성전자_d.csv', index_label='Date')

    # mod = Gatherer()
    
    # df, _ = mod.get_stock('000660', '2020-01-01', interval='d', save=False)   

    # add_MACD(df)
    
    # add_MA(df, period=6, target='rsi_14')

    # add_EMA(df, 12, 'ext')
    # add_EMA(df, 26)

    # df['ema12-ema26'] = df['ema_12'] - df['ema_26']
    # df['signal'] = ta.EMA(df['ema12-ema26'], 9)
    # add_STOCH(df)

    # add_STOCHF(df)

    # add_CMO(df)

    # add_EMA(df)
    
    # add_ATR(df)

    # add_ST(df) 

    add_clustering(df, 2, 'close','1m','1m')

    # df.to_csv(os.getcwd()+'/stockFile/'+'SK하이닉스_d.csv', index_label='Date')

    # df = pd.read_csv(os.getcwd()+'/stockFile/for_clustering/target/'+'웨이브일렉트로_d.csv', index_col='Date')
    print(df)
    # df.to_csv(os.getcwd()+'/stockFile/test_d.csv', index_label='Date')
    