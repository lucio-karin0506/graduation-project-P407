import pandas as pd 
import FinanceDataReader as fdr
import copy
import gathering
from tech_indi import *

'''
로그: 2020.2.8시작, 2.24 수정
파라미터: 볼린져밴드와 보조지표가 모두 추가된 데이터프레임, 과거를 볼 기간
기능: 기본전략(볼린져 밴드)을 이용하여 매수, 매도 타이밍 체크
리턴 매수, 매도 시점을 저장한 데이터프레임을 리턴
'''
def check_bbcandle(df, period=2): 
    df.reset_index(inplace=True)
    # sell_check
    sindex_list = df[df.down_candle == True].index # for문에 사용할 범위를 생성

    sell_point = {} # 매도 시점을 파악하기 위한 dict
    df_in_func = df.reset_index() # 슬라이싱을 하기위해 date인덱스를 컬럼으로 변경

    cross_signal = False # 돌파가 발생했을 때 체크하는 시그널
    candle_signal = False # 돌파이후 현재값이 첫번째 시그널 캔들인지 체크하는 시그널
    try:
        for j in range(0, len(sindex_list)): # 음봉이 발생한 경우만 확인한다.
            # loop_count = 0 # period 루프가 돌아가는 횟수를 체크 
            if j - period < 0: # 처음 인덱스는 이전 데이터를 확인할 수 없으므로 넘어가도록 함
                continue

            for i in range(sindex_list[j] - period, sindex_list[j] + 1): # 정해진 기간내에서 상향돌파를 발생했는지 확인, 자신포함
                if df.loc[i, 'up_cross']: # 상향돌파한 경우
                    cross_signal = True # 매도 신호 발생
                    cross_point = i  # 돌파한 시점의 인덱스

                    ''' 현재 시점 바로 이전에 돌파가 발생한 경우에 시그널을 주게 되면 첫번째 음봉체크가 불분명해진다. 때문에 현재도 확인을 해야함'''
                    # 자기 자신에서 상향돌파가 발생
                    if sindex_list[j] - cross_point == 0: # 현재시점 캔들(자기자신)에서 돌파가 발생 & 과거에 같은 경우(음봉이면서 상향돌파)가 있는지 확인해야한다.
                        for k in range(sindex_list[j] - period, cross_point): # sindex_list[j] == cross_point이므로 혼합하여 사용해도 된다.
                            # sell_point에 저장된 값이 있는지 확인하여 과거에 매도시점이 있는지 체크
                            if df_in_func['Date'].iloc[k] in sell_point:
                                candle_signal = False
                                break # 한 번이라도 False가 나오면 매도신호에 맞지 않는다.
                            else:
                                candle_signal = True

                        if not candle_signal: # 한 번이라도 False가 나오면 매도신호에 맞지 않는다.
                            break

                    else: # 돌파한 인덱스와 현재캔들 인덱스 사이에 음봉이 있는지 확인 
                        for k in range(cross_point, sindex_list[j]): 
                            if k in sindex_list: # 사이에 음봉이 있는지 확인
                                candle_signal = False
                                break
                                # print('사이에 음봉이 있습니다.')
                            else:
                                candle_signal = True
                                # print('사이에 음봉이 없습니다.')

                        if not candle_signal: # 한 번이라도 False가 나오면(돌파시점과 현재시점사이에 한개에 음봉이라도 존재하는 경우) 매도신호에 맞지 않는다.
                            break
                        
            if cross_signal and candle_signal:
                # print(j, str(df_in_func['Date'].iloc[sindex_list[j]].strftime("%Y-%m-%d")) + ' SELL')
                # print(df_in_func['Date'].iloc[sindex_list[j]])
                sell_point[df_in_func['Date'].iloc[sindex_list[j]]] = True # 매도 시점을 저장
                cross_signal = False
                candle_signal = False
            # else:
                # print(str(df_in_func['Date'].iloc[sindex_list[j]].strftime("%Y-%m-%d")) + ' HOLD')
            # print('-----------------------------')
    except IndexError: # 데이터프레임에 존재하지 않는 인덱스를 확인할 때 발생하는 에러를 무시
        pass

    # check_buy
    bindex_list = df[df.up_candle == True].index # for문에 사용할 범위를 생성

    buy_point = {} # 매수 시점을 파악하기 위한 dict
    cross_signal = False # 돌파가 발생했을 때 체크하는 시그널
    candle_signal = False # 돌파이후 현재값이 첫번째 시그널 캔들인지 체크하는 시그널

    try: 
        for j in range(0, len(bindex_list)):
            if j - period < 0: # 처음 인덱스는 이전 데이터를 확인할 수 없으므로 넘어가도록 함
                continue

            for i in range(bindex_list[j] - period, bindex_list[j] + 1): # 정해진 기간내에서 하향돌파를 발생했는지 확인, 자신포함
                if df.loc[i, 'down_cross']: # 하향돌파한 경우
                    cross_signal = True # 매수 신호 발생
                    cross_point = i # 돌파한 시점의 인덱스

                    ''' 현재 시점 바로 이전에 돌파가 발생한 경우에 시그널을 주게 되면 첫번째 음봉체크가 불분명해진다.'''
                    if bindex_list[j] - cross_point == 0: # 현재시점 캔들에서 돌파가 발생하면 매도시그널 & 과거에도 같은 경우가 있는지 확인해야한다.
                        # buy_point에 저장된 값이 있는지 확인한다.
                        for k in range(bindex_list[j] - period, cross_point): # bindex_list[j] == cross_point이므로 혼합하여 사용해도 된다.
                            if df_in_func['Date'].iloc[k] in buy_point:
                                candle_signal = False
                                break
                            else:
                                candle_signal = True

                        if not candle_signal: # 한 번이라도 False가 나오면 매수신호에 맞지 않는다.
                            break
                    else:
                        for k in range(cross_point, bindex_list[j]): # 돌파한 인덱스와 현재캔들 인덱스 사이에 양봉이 있는지 확인
                            if k in bindex_list: # 사이에 값이 양봉이 있는지 확인
                                candle_signal = False
                                break # print('사이에 양봉이 있습니다.')                                
                            else:
                                candle_signal = True
                                # print('사이에 양봉이 없습니다.')

                        if not candle_signal: # 한 번이라도 False가 나오면 매수신호에 맞지 않는다.
                            break
                    
            if cross_signal and candle_signal: # 돌파이후 현재 캔들이 첫번째 시그널캔들(양봉)인지를 확인
                # print(j, str(df_in_func['Date'].iloc[bindex_list[j]].strftime("%Y-%m-%d")) + " BUY")
                buy_point[df_in_func['Date'].iloc[bindex_list[j]]] = True
                cross_signal = False
                candle_signal = False
            # else:
            #     print(str(df_in_func['Date'].iloc[bindex_list[j]].strftime("%Y-%m-%d")) + " HOLD")
            # print('-----------------------------')
    except IndexError: # 데이터프레임에 존재하지 않는 인덱스를 확인할 때 발생하는 에러를 무시
        pass
    
    # 매수, 매도 시점을 저장한 딕셔너리를 dataframe으로 만듬
    bbcandle_buy = pd.DataFrame(buy_point.items(), columns=['Date', 'bbcandle_buy'])
    bbcandle_buy.set_index('Date', inplace=True)

    bbcandle_sell = pd.DataFrame(sell_point.items(), columns=['Date', 'bbcandle_sell'])
    bbcandle_sell.set_index('Date', inplace=True)

    result = pd.concat([bbcandle_buy, bbcandle_sell], axis='columns', join='outer')
    result.fillna(value=False, inplace=True)
    return result

'''
로그: 2020.02.20 시작
파라미터: RIS지표데이터프레임, RSI을 판단할 percentage
기능: RIS 지표를 갖고 매수 매도 판단 시그널을 만든다.
리턴: 데이터프레임에 매수매도 판단 시그널을 생성    '''
def check_RSI(df, up_pct=70, donw_pct=30):
    rsi_buy = df.rsi <= donw_pct # 30
    rsi_buy_df = pd.DataFrame({'rsi_buy':rsi_buy})

    rsi_sell = df.rsi >= up_pct # 70
    rsi_sell_df = pd.DataFrame({'rsi_sell':rsi_sell})

    result = pd.concat([rsi_buy_df, rsi_sell_df], axis='columns')
    return result

'''
로그: 2020.02.20 시작 2020.03.03 수정
파라미터: MACD 주가데이터프레임
기능: MACD 지표를 갖고 하락세인지만 판단하도록 한다. (이유: 다른 지표들에서 더 좋은 거래 신호를 생성하기 때문에 )
리턴: 데이터프레임에 매수매도 판단 시그널을 생성    '''
def check_MACD(df):
    df.reset_index(inplace=True) # 인덱스 비교를 
    # macd < 0일땐 하락세인 것으로 예측하고 어떠한 거래를 하지 않도록 한다.
    macd_under_zero = df.macd< 0
    down_trend = {}
    for i in macd_under_zero[macd_under_zero == True].index: # macd<0인 날짜이므로 거래를 시키지 않는다.
        down_trend[df.loc[i,'Date']] = True
    down_trend_df = pd.DataFrame(down_trend.items(), columns=['Date', 'macd_DT'])
    down_trend_df.set_index('Date', inplace=True)

    return down_trend_df

'''
로그: 2020.02.20 시작 2020.07.22 수정(함수 split)
파라미터: stochastic 주가데이터와 stochastic 판단 percentage
기능: stochastic 지표를 갖고 매수 매도 판단 시그널을 만든다.
리턴: 데이터프레임에 매수매도 판단 시그널 데이터프레임    '''
def check_STOCH(df, up_pct=80, down_pct=20):
    # case1은 결과가 좋지 않아서 사용하려면 수정이 필요...
    # case2의 결과가 좋으므로 현재 case2만 사용
    # case3과 case4는 미 구현

    result_df = check_STOCH_CASE2(df, up_pct=up_pct, down_pct=down_pct)

    return result_df

'''case 1: 
slow_K가 20 이하이면 과매도구간 slow_K가 slow_D를 상향돌파하면 매수
slow_K가 80 이상이면 과매수구간 slow_K가 slow_D를 하향돌파하면 매도 '''
def check_STOCH_CASE1(df, up_pct=80, down_pct=20):
    df_case1 = copy.deepcopy(df)
    df_case1.reset_index(inplace=True)

    # print(df_case1)
    stoch_under_down = df_case1.slow_K <= down_pct
    # print(stoch_under_down)
    stoch_buy1 = {}

    for i in stoch_under_down[stoch_under_down.values == True].index:
        # print(df_case1.loc[i-1, 'slow_K'] < down_pct)
        # print(df_case1.loc[i, 'slow_K'] > down_pct); print()
        if df_case1.loc[i-1, 'slow_K'] < down_pct and df_case1.loc[i, 'slow_K'] > down_pct:
            # print('20아래', df_case1.loc[i, 'Date'], df_case1.loc[i, 'slow_K'])
            # print('상향돌파', df_case1.loc[i+1, 'Date'], df_case1.loc[i+1, 'slow_K'])
            stoch_buy1[df_case1.loc[i, 'Date']] = True # 매수신호

    stoch_buy1_df = pd.DataFrame(stoch_buy1.items(), columns=['Date', 'stoch_1_buy'])
    stoch_buy1_df.set_index('Date', inplace=True)

    stoch_over_up = df_case1.slow_K >= up_pct
    stoch_sell1 = {}

    for i in stoch_over_up[stoch_over_up.values == True].index:
        if df_case1.loc[i-1, 'slow_K'] > up_pct and df_case1.loc[i, 'slow_K'] < up_pct:
            # print('80이상', df.loc[i,'Date'], df.loc[i, 'slow_K'])
            # print('하향돌파', df.loc[i+1, 'Date'], df.loc[i+1, 'slow_K'])
            stoch_sell1[df_case1.loc[i, 'Date']] = True # 매도신호

    stoch_sell1_df = pd.DataFrame(stoch_sell1.items(), columns=['Date', 'stoch_1_sell'])
    stoch_sell1_df.set_index('Date', inplace=True)

    result_case1_df = gathering.merge_all_df(stoch_buy1_df, stoch_sell1_df)
    return result_case1_df

'''case 2: 
slow_K <= 20이고 slow_K가 slow_D를 상향돌파 하면 매수
slow_K >= 80이고 slow_K가 slow_D를 하향돌파 하면서 매도 '''
def check_STOCH_CASE2(df, up_pct=80, down_pct=20):
    df_case2 = copy.deepcopy(df)
    df_case2.reset_index(inplace=True)

    stoch_under_down = df_case2.slow_K <= down_pct
    # print(stoch_under_down); return
    stoch_buy2 = {}

    for i in stoch_under_down[stoch_under_down.values == True].index:
        # print(df_case2.loc[i-1, 'slow_K'] < df_case2.loc[i-1, 'slow_D'])
        # print(df_case2.loc[i, 'slow_K'] > df_case2.loc[i, 'slow_D']); print()
        if df_case2.loc[i-1, 'slow_K'] < df_case2.loc[i-1, 'slow_D'] and df_case2.loc[i, 'slow_K'] > df_case2.loc[i, 'slow_D']:
            # print('20아래', df_case2.loc[i-1, 'Date'], df_case2.loc[i-1, 'slow_K'], df_case2.loc[i-1, 'slow_D'])
            # print('상향돌파', df_case2.loc[i, 'Date'], df_case2.loc[i, 'slow_K'], df_case2.loc[i, 'slow_D'])
            stoch_buy2[df_case2.loc[i, 'Date']] = True

    stoch_buy2_df = pd.DataFrame(stoch_buy2.items(), columns=['Date', 'stoch_buy'])
    stoch_buy2_df.set_index('Date', inplace=True)

    stoch_over_up = df_case2.slow_K >= up_pct
    stoch_sell2 = {}

    for i in stoch_over_up[stoch_over_up.values == True].index:
        if df_case2.loc[i-1, 'slow_K'] > df_case2.loc[i-1, 'slow_D'] and df_case2.loc[i, 'slow_K'] < df_case2.loc[i, 'slow_D']:
            # print('80이상', df.loc[i,'Date'], df.loc[i, 'slow_K'], df.loc[i, 'slow_D'])
            # print('하향돌파', df.loc[i+1, 'Date'], df.loc[i+1, 'slow_K'], df.loc[i+1, 'slow_D'])
            stoch_sell2[df_case2.loc[i, 'Date']] = True

    stoch_sell2_df = pd.DataFrame(stoch_sell2.items(), columns=['Date', 'stoch_sell'])
    stoch_sell2_df.set_index('Date', inplace=True)

    result_case2_df = gathering.merge_all_df(stoch_buy2_df, stoch_sell2_df)
    return result_case2_df

''' case 1, 2의 결과가 좋지 않으면 case 3, 4번도 추가예정
case 3: 
df['close']는 저점을 갱신하면서 하락 slow_K는 전저점을 갱신하지 못한경우 -> 매수
df['close']는 고점을 갱신하면서 상승 slow_K는 전고점을 갱신하지 못한경우 -> 매도'''



'''     
로그: 2020.03.09 시작 2020.03.26 수정
파라미터: 주식마켓 또는 stockcodelist, 확인할 시간, 가져올 기준시간(일봉 or 주봉)
기능: 오늘기준으로 주식들의 시그널을 확인한다.
리턴: 각각의 주식에대한 시그널    '''
def check_stock(stockmarket=None, item_list=None, check_date='today', dtype='D'):
    gathering = Gathering()
    if item_list is None:
        stocklist_df = fdr.StockListing(stockmarket)
        stocklist = stocklist_df.Symbol
    elif stockmarket is None:
        stocklist = item_list
    
    def make_signal(df):
        bband = get_BBand(df=df)
        rsi = get_RSI(df=df)
        macd = get_MACD(df=df)
        stoch = get_STOCH(df=df)  

        # 기본전략 시그널
        bbcandle = check_bbcandle(df=bband)
        # 보조지표 시그널
        rsi = check_RSI(df=rsi)
        macd = check_MACD(df=macd)    
        stoch = check_STOCH(df=stoch)

        return_df = gathering.merge_all_df(bbcandle, rsi, macd, stoch)

        return return_df

    code_data = {} # 각 주식코드의 시그널을 담기위한 dictionary
    if dtype == 'D':
        for no, stock in enumerate(stocklist):
            df = gathering.get_stock(code=stock, startdate=check_date, enddate=check_date)
            
            df_for_trade = make_signal(df=df)

            code_data[stock] = df_for_trade.iloc[-1]

    elif dtype == 'W':
        for no, stock in enumerate(stocklist):
            df = gathering.get_stock(code=stock, startdate=check_date, enddate=check_date, dtype='W')

            df_for_trade = make_signal(df=df)
            # print(df_for_trade)
            # print(stock, df_for_trade.iloc[-1])
            code_data[stock] = df_for_trade.iloc[-1]

    result = pd.DataFrame.from_dict(code_data)
    result = result.T
    result.index.names = ['stockcode']
    return result

if __name__ == "__main__": 
    mod = gathering.Gathering()
    df = mod.get_stock('000660', '2015-01-01')
    # print(df)
    
    import tech_indi
    bbcandle = tech_indi.get_BBand(df)
    # print(bbcandle)
    # stoch = get_STOCH(df)
    # # print(stoch)
    # a = check_STOCH(df=stoch)

    a = check_bbcandle(bbcandle)
    print(a)

    b = gathering.merge_all_df(df, a)
    b.to_csv('test.csv')
    # print(b)