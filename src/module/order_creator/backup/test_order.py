# 내부 모듈
import gathering
from tech_indi import *
from stock_signal import *



if __name__ == "__main__":
    mod = gathering.Gathering()
    df = mod.get_stock('000660', '2000-01-01', '2020-01-01', interval='w')
    # print(df)
    
    RSI(df)   

    # print(mod.df)

    trade_df = df.reset_index() # 날짜데이터가 인덱스이므로 컬럼으로 바꿈
    # trade_df['Date'] = trade_df['Date'].apply(lambda x: x.strftime('%Y-%m-%d')) # json파일에서 datetime형식은 깨지므로 문자열로 변환

    # trade_df.to_csv('trade_df.csv')

    for idx, trade in trade_df.iterrows():
        if crossUp(trade, idx, trade_df, 'rsi', 70): 
            # print('rsi 상향돌파 발생')
            print(idx, trade)