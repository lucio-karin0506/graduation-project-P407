import talib as ta
'''
autor: 김상혁
log: start: 2020.3.19  last edit: 2021.01.16 
func: 주가데이터로부터 볼린져밴드 값을 구함
parameter: 주가데이터프레임, 이동평균기간, 표준편차의 상향값, 표준편차의 하향값
return: input dataframe에 볼린져 밴드 컬럼 추가    '''
def add_BBands(df, period:int =20, nbdevup:int =2, nbdevdn:int =2, price:str='close'):
    # 볼린져 밴드 값 생성
    ubb, mbb, lbb = ta.BBANDS(df[price], timeperiod=period, nbdevup=nbdevup, nbdevdn=nbdevdn) 

    df['ubb_'+str(period)+'_'+str(nbdevup)+'_'+str(nbdevdn)] = ubb
    df['mbb_'+str(period)+'_'+str(nbdevup)+'_'+str(nbdevdn)] = mbb
    df['lbb_'+str(period)+'_'+str(nbdevup)+'_'+str(nbdevdn)] = lbb

    return df

"""
autor: 김상혁
log: start: 2020.2.20 last edit: 2021.01.16 
func: RSI 값을 가져오는 함수
parameter: 주가 데이터프레임, RSI를 확인할 기간
return: input dataframe에 RSI 컬럼 추가    """
def add_RSI(df, period:int=14, price:str='close'):
    rsi = ta.RSI(df[price], timeperiod=period) # series를 반환한다.    

    df['rsi_'+str(period)] = rsi

    return df

'''
autor: 김상혁
log: start: 2020.2.20 last edit: 2021.01.16 
func: MACD 값을 가져오는 함수
parameter: 주가 데이터프레임, 단기이평기간, 장기이평기간, 단기-장기 값의 이평의 이평기간
return: input dataframe에 MACD 컬럼 추가    '''
def add_MACD(df, fast_period:int=12, slow_period:int=26, signal_period:int=9, price:str='close'):
    macd, macd_signal, macd_hist = ta.MACD(df[price], fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)

    df['macd_'+str(fast_period)+'_'+str(slow_period)+'_'+str(signal_period)] = macd
    df['macd_signal_'+str(fast_period)+'_'+str(slow_period)+'_'+str(signal_period)] = macd_signal
    df['macd_hist_'+str(fast_period)+'_'+str(slow_period)+'_'+str(signal_period)] = macd_hist
    
    return df

'''
autor: 김상혁
log: start: 2020.2.20 last edit: 2021.01.16 
func: stochastic 값을 가져오는 함수
parameter: 주가 데이터프레임, 전체 기간(fastk_period,N), Fask %D, slow %K의 이평기간(slowk_period, M), slow %D의 이평기간(slowd_period, T)
return: input dataframe에 stochastic 컬럼 추가, stochastic 값 [slowk(fast %K를 M기간으로 이동평균), slowd(slow %K를 T기간으로 이동평균)]   '''
def add_STOCH(df, fastk_period:int=5, slowk_period:int=3, slowd_period:int=3, price1:str='high', price2:str='low', price3:str='close'):
    slowk, slowd = ta.STOCH(df[price1], df[price2], df[price3], fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
    
    df['slowk_'+str(fastk_period)+'_'+str(slowk_period)+'_'+str(slowd_period)] = slowk
    df['slowd_'+str(fastk_period)+'_'+str(slowk_period)+'_'+str(slowd_period)] = slowd

    return df

'''
autor: 김상혁
log: start: 2020.2.20 last edit: 2021.01.16 
func: stochastic Fast 값을 가져오는 함수
parameter: 주가 데이터프레임, 전체 기간(fastk_period,N), Fastk %D, Fastd %K
return: input dataframe에 stochastic 컬럼 추가, stochastic 값 [fastk, fastd]   '''
def add_STOCHF(df, fastk_period:int=5, fastd_period:int=3, price1:str='high', price2:str='low', price3:str='close'):
    fastk, fastd = ta.STOCHF(df[price1], df[price2], df[price3], fastk_period=fastk_period, fastd_period=fastd_period)
    
    df['fastk_'+str(fastk_period)+'_'+str(fastd_period)] = fastk
    df['fastd_'+str(fastk_period)+'_'+str(fastd_period)] = fastd

    return df

'''
autor: 김상혁 
log: start: 2021.01.16 
func: MA(moving average) 값을 가져오는 함수
parameter: 주가 데이터프레임, 이동평균 기간
return: input dataframe에 MA 컬럼 추가    '''
def add_MA(df, period:int=10, price:str='close'):
    ma = ta.MA(df[price], timeperiod=period)
    
    # 입력한 기간의 ma를 row의 이름으로 정함
    df['ma_'+str(period)] = ma

    return df


'''
autor: 김상혁 
log: start: 2021.01.19
func: EMA(Exponential moving average) 값을 가져오는 함수
parameter: 주가 데이터프레임, 이동평균 기간
return: input dataframe에 EMA 컬럼 추가    '''
def add_EMA(df, period:int=30, price:str='close'):
    ema = ta.EMA(df[price], timeperiod=period)

    df['ema_'+str(period)] = ema
    
    return df

'''
autor: 김상혁
log: 2021.1.12 시작 last edit: 2021.01.16 
func: CMO(Changed Momentum Oscillator) 값을 가져오는 함수
parameter: 주가 데이터프레임, 기간
return: input dataframe에 CMO 컬럼 추가    '''
def add_CMO(df, period:int=14, price:str='close'):
    cmo = ta.CMO(df[price], timeperiod=period)

    df['cmo_'+str(period)] = cmo

    return df


if __name__ == "__main__":
    import time
    import gatherer
    import pandas as pd
 
    # startTime = time.time()

    mod = gatherer.Gatherer()
    
    df, _ = mod.get_stock('000660', '2020-01-01', interval='d', save=False)

    add_BBands(df, 20, 2, 2)

    # add_RSI(df)

    # add_MACD(df)
        
    # add_EMA(df, 12)
    # add_EMA(df, 26)

    # df['ema12-ema26'] = df['ema_12'] - df['ema_26']
    # add_STOCH(df)

    # add_STOCHF(df)

    add_CMO(df)

    # add_EMA(df)
    
    # df.to_csv('test2.csv')
    # df = pd.read_csv('test.csv')
    # df.reset_index(inplace=True)
    print(df)

    # end_time = time.time()

    # print("WorkingTime: {} sec".format(end_time-startTime))

    # df.to_csv('test.csv')