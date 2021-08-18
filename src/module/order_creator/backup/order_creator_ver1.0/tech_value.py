'''
order_creator 모듈에서 필요한
기술적 지표 값 혹은 기술지표 값 기반 신호를 생성하는 함수들의 모듈
'''
from tech_indi import *
from stock_signal import *

'''
로그: 2020.7.19 시작
기능: 주가데이터로부터 볼린져밴드 값과 볼린져 밴드기반에 전략(기본전략)에 필요한 시그널을 구함
파라미터: 주가데이터프레임, 이동평균기간, 표준편차의 상향값, 표준편차의 하향값, 캔들 상승비율, 캔들 하락비율, 과거를 볼 기간
리턴: 볼린져밴드 기반에 거래신호 데이터프레임   '''
def create_BBcandle(df, period=20, nbdevup=2, nbdevdn=2, up_pct=1.5, down_pct=0.5, check_period=2):
    bbcandle_df = get_BBand(df=df, period=period, nbdevup=nbdevup, nbdevdn=nbdevdn,
                                    up_pct=up_pct, down_pct=down_pct)
    check_bband = check_bbcandle(bbcandle_df, period=check_period) # 현재포함 과거 2일을 확인

    return check_bband

'''
로그: 2020.7.19 시작
파라미터: 주가 데이터프레임, RSI를 확인할 기간, RSI을 판단할 percentage
기능: RSI 지표 생성을 생성한다.
리턴: RSI값 데이터프레임'''
def create_RSI(df, timeperiod=14):  #, up_pct=70, donw_pct=30
    rsi_df = get_RSI(df=df, timeperiod=timeperiod)
    # check_rsi = check_RSI(rsi_df, up_pct=up_pct, donw_pct=donw_pct)

    return rsi_df

'''
로그: 2020.7.19 시작
파라미터: 주가 데이터프레임, 단기이평기간, 장기이평기간, 단기-장기 값의 이평의 이평기간
기능: MACD값을 생성하고
리턴: MACD값 데이터 프레임   '''
def create_MACD(df, fast_period=12, slow_period=26, signal_period=9):
    macd_df = get_MACD(df=df, fast_period=fast_period,
                                slow_period=slow_period, signal_period=signal_period)
    # check_macd = check_MACD(macd_df) # 따로 옵션이 없음

    return macd_df

'''
로그: 2020.7.19 시작
파라미터: 주가 데이터프레임, 전체 기간(fastk_period,N), Fask %D, slow %K의 이평기간(slowk_period, M), slow %D의 이평기간(slowd_period, T)
기능: 스토케스틱 지표를 생성하고 지표 기반에 거래신호를 생성한다.
리턴: 스토케스틱 기반에 거래신호 데이터 프레임    '''
def create_STOCH(df, fastk_period=5, slowk_period=3, slowd_period=3, up_pct=80, down_pct=20):
    stoch_df = get_STOCH(df=df, fastk_period=fastk_period,
                                    slowk_period=slowk_period, slowd_period=slowd_period)
    check_stoch = check_STOCH(stoch_df, up_pct=up_pct, down_pct=down_pct)

    return check_stoch