import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import font_manager, rc
from mplfinance.original_flavor import candlestick2_ohlc
import pandas as pd

# plotly import
# import plotly.offline as offline
# import plotly.graph_objects as go
# from datetime import datetime

# 거래 포인트 체크
# ax0.plot(index[df.sell_point == True], df.ubb[df.sell_point == True], 'v', label= 'sell') # 매도 지점에 v표시
# ax0.plot(index[df.buy_point == True], df.lbb[df.buy_point == True], '^', label= 'buy') # 메수 지점에 ^표시

'''
로그: 2020.2.16 시작, 2020.08.12 수정 mplfinance 버전 변경으로 인한 코드 수정
파라미터: 볼린저 밴드 값과 거래 포인트가 추가된 데이터프레임
기능: 볼린저 밴드 값과 거래 포인트가 추가된 데이터프레임을 그래프로 나타냄    '''
def make_graph(df, trade_point='on'):    
    copy_df = df.reset_index()

    # 한글 폰트 지정
    font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
    rc('font', family=font_name)
    fig, ax = plt.subplots()
    
    # x-축 날짜 
    xdate = copy_df.Date.astype('str') 
    for i in range(len(xdate)):
        xdate[i] = xdate[i][2:] # 2020-01-01 => 20-01-01 

    if trade_point == 'bb':        
        ax.plot(xdate, copy_df['ubb_20_2_2'], label="Upper limit", linewidth=0.7, color='k')
        ax.plot(xdate, copy_df['mbb_20_2_2'], label="center line", linewidth=0.7, color='y') 
        ax.plot(xdate, copy_df['lbb_20_2_2'], label="Lower limit", linewidth=0.7, color='k')
        candlestick2_ohlc(ax, copy_df['open'], copy_df['high'], copy_df['low'] ,copy_df['close'], width=0.5, colorup='r', colordown='b')

    elif trade_point == 'ma':
        ax.plot(xdate, copy_df['ma'], label="ma", linewidth=0.7, color='g')
        candlestick2_ohlc(ax, copy_df['open'], copy_df['high'], copy_df['low'] ,copy_df['close'], width=0.5, colorup='r', colordown='b')
    
    else:
        ax.plot(xdate, copy_df['close'], linewidth=0.7, color='k')
        candlestick2_ohlc(ax, copy_df['open'], copy_df['high'], copy_df['low'] ,copy_df['close'], width=0.5, colorup='r', colordown='b')
    
    fig.suptitle("stock chart") 
    ax.set_xlabel("Date") 
    ax.set_ylabel("Price") 
    ax.xaxis.set_major_locator(ticker.MaxNLocator(25))
    ax.legend(loc='best') # legend 위치 

    plt.xticks(rotation = 45) # x-축 글씨 45도 회전 
    plt.grid() # 그리드 표시 
    plt.show()

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
    from  module.gatherer.gatherer import Gatherer
    from module.indicator.indicator import *

    mod = Gatherer()
    df, name = mod.get_stock('000660', '2015-08-01', '2020-08-01', 'D', save=False)

    add_BBands(df)

    # MA(df)    

    # result = gathering.pd.concat([df, ma_df], axis='columns')

    # print(ma_df)
    make_graph(df, 'bb')

    print(df)