import pandas as pd
import talib as ta
import gathering

'''
로그: 2020.3.19시작
기능: 주가데이터로부터 볼린져밴드 값과 볼린져 밴드기반에 전략(기본전략)에 필요한 시그널을 구함
파라미터: 주가데이터프레임, 이동평균기간, 표준편차의 상향값, 표준편차의 하향값, 캔들 상승비율, 캔들 하락비율
리턴: 볼린져밴드 값+기본전략 시그널을 저장한 데이터프레임    '''
def get_BBand(df, period=20, nbdevup=2, nbdevdn=2, up_pct=1.5, down_pct=0.5):
    # 볼린져 밴드 값 생성
    ubb, mbb, lbb = ta.BBANDS(df['close'], period, nbdevup, nbdevdn) 
    # bband_df = pd.DataFrame(data={'ubb':ubb, 'mbb':mbb, 'lbb':lbb})
    df['ubb'] = ubb; df['mbb'] = mbb; df['lbb'] = lbb

    '''
    로그: 2020.2.8시작, 2.20 수정
    수정: type인자 삭제 - 매수 매도를 모두 구한후 이후 출력할 때 필터링하는 방식으로 변경
    기능: 주가데이터에서 어떤 캔들(양봉,음봉)인지 체크
    파라미터: 주가데이터프레임, 상승비율, 하락비율
    리턴: 해당 인덱스(date)가 음봉인지 양봉인지 체크한 데이터프레임    '''
    def check_candle(df, up_pct=1.5, down_pct=0.5):       
        down_candle = df['open'] * (1 - down_pct * 0.01) >= df['close'] # 시가기준 종가가 x% 하락한 음봉을 체크
        # df_sell = df_sell[df_sell.check == True] # 데이터프레임에 음봉인 경우만 남김
        up_candle = df['open'] * (1 + up_pct * 0.01) <= df['close'] # 시가기준 종가가 x% 상승한 양봉을 체크
        # df_buy = df_buy[df_buy.check == True] # 데이터프레임에 양봉 경우만 남김

        check_candle = pd.DataFrame({'up_candle':up_candle, 'down_candle':down_candle})

        return check_candle
    '''
    로그: 2020.2.8시작, 2.20 수정
    수정: type인자 삭제 - 매수 매도를 모두 구한후 이후 출력할 때 필터링하는 방식으로 변경
    기능: 주가데이터에서 어떤 돌파(상향, 하향)인지 체크
    파라미터: 주가데이터프레임
    리턴: 해당 인덱스(date)가 상향돌파인지 하향돌파인지 체크한 데이터프레임    '''
    def check_bbcross(df):
        up_cross = df['ubb'] <= df['high']
        # df_up_cross.reset_index(inplace=True)        
        down_cross = df['lbb'] >= df['low']
        # df_down_cross.reset_index(inplace=True)

        check_bbcross = pd.DataFrame({'up_cross':up_cross, 'down_cross':down_cross})

        return check_bbcross

    check_candle = check_candle(df, up_pct=up_pct, down_pct=down_pct)
    check_bbcross = check_bbcross(df)
    
    bband_df = gathering.merge_all_df(df, check_candle, check_bbcross)

    return bband_df

"""
로그: 2020.2.20 시작
파라미터: 주가 데이터프레임, RSI를 확인할 기간
기능: RSI 값을 가져오는 함수
리턴: RSI 값을 저장한 데이터프레임    """
def get_RSI(df, timeperiod=14):
    rsi = ta.RSI(df['close'], timeperiod) # series를 반환한다.
    rsi_df = pd.DataFrame(rsi, columns = ['rsi'])

    return rsi_df
'''
로그: 2020.2.20 시작
파라미터: 주가 데이터프레임, 단기이평기간, 장기이평기간, 단기-장기 값의 이평의 이평기간
기능: MACD 값을 가져오는 함수
리턴: MACD 값을 저장한 데이터프레임    '''
def get_MACD(df, fast_period=12, slow_period=26, signal_period=9):
    macd, macd_signal, macd_hist = ta.MACD(df['close'],fast_period, slow_period, signal_period)
    macd_df = pd.DataFrame({'macd':macd, 'macd_sig':macd_signal, 'macd_hist':macd_hist})

    return macd_df
'''
로그: 2020.2.20 시작
파라미터: 주가 데이터프레임, 전체 기간(fastk_period,N), Fask %D, slow %K의 이평기간(slowk_period, M), slow %D의 이평기간(slowd_period, T)
기능: stochastic 값을 가져오는 함수
리턴: stochastic 값(slowk(fast %K를 M기간으로 이동평균), slowd(slow %K를 T기간으로 이동평균))을 저장한 데이터프레임    '''
def get_STOCH(df, fastk_period=5, slowk_period=3, slowd_period=3):
    slowk, slowd = ta.STOCH(df['high'], df['low'], df['close'], fastk_period, slowk_period, slowd_period)
    stoch_df = pd.DataFrame({'slow_K':slowk, 'slow_D':slowd})

    return stoch_df