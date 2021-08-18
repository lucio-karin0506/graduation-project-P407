'''
autor: 김상혁
log: start: 2021.1.8
func: 주가데이터에서 비교1이 비교2를 상향돌파 했는지 확인하는 함수
parameter: row of dataframe, index of row, dataframe, 비교1(source), 비교2(target)
return: boolean    '''    
def crossUp(row, idx, df, source, target):
    ''' target이 정수일 때와 문자열(df의 row)일 때를 구분해야 함 '''
    
    if type(target) is int:
        if row[source] > target and df.iloc[idx-1][source] < target:
            return True
    
        else:
            return False
    
    elif type(target) is str:
        if row[source] >  df.iloc[idx][target] and df.iloc[idx-1][source] < df.iloc[idx-1][target]:
            return True
    
        else:
            return False

'''
autor: 김상혁
log: start: 2021.1.8
func: 주가데이터에서 비교1이 비교2를 하향돌파 했는지 확인하는 함수
parameter: row of dataframe, index of dataframe, dataframe, 비교1(source), 비교2(target)
return: boolean    ''' 
def crossDown(row, idx, df, source, target):
    ''' target이 정수일 때와 문자열(df의 row)일 때를 구분해야 함 '''
    
    if type(target) is int:            
        if row[source] < target and df.iloc[idx-1][source] > target:
            return True
        
        else:
            return False

    elif type(target) is str:
        if row[source] < df.iloc[idx][target] and df.iloc[idx-1][source] > df.iloc[idx-1][target]:
            return True
        
        else:
            return False
        
    # '''
    # 로그: 2020.2.8시작, 2.20 수정
    # 수정: type인자 삭제 - 매수 매도를 모두 구한후 이후 출력할 때 필터링하는 방식으로 변경
    # 기능: 주가데이터에서 어떤 캔들(양봉,음봉)인지 체크
    # 파라미터: 주가데이터프레임, 상승비율, 하락비율
    # return: 해당 인덱스(date)가 음봉인지 양봉인지 체크한 데이터프레임    '''
    # def check_candle(self, df, up_pct, down_pct):       
    #     down_candle = df['open'] * (1 - down_pct * 0.01) >= df['close'] # 시가기준 종가가 x% 하락한 음봉을 체크        
    #     up_candle = df['open'] * (1 + up_pct * 0.01) <= df['close'] # 시가기준 종가가 x% 상승한 양봉을 체크

    #     # df_sell = df_sell[df_sell.check == True] # 데이터프레임에 음봉인 경우만 남김
    #     # df_buy = df_buy[df_buy.check == True] # 데이터프레임에 양봉 경우만 남김

    #     check_candle = pd.DataFrame({'up_candle':up_candle, 'down_candle':down_candle})

    #     return check_candle

    # '''
    # 로그: 2020.2.8시작, 2.20 수정
    # 수정: type인자 삭제 - 매수 매도를 모두 구한후 이후 출력할 때 필터링하는 방식으로 변경
    # 기능: 주가데이터에서 어떤 돌파(상향, 하향)인지 체크
    # 파라미터: 주가데이터프레임
    # return: 해당 인덱스(date)가 상향돌파인지 하향돌파인지 체크한 데이터프레임    '''
    # def check_bbcross(self, df):
    #     up_cross = df['ubb'] <= df['high']         
    #     down_cross = df['lbb'] >= df['low']

    #     check_bbcross = pd.DataFrame({'up_cross':up_cross, 'down_cross':down_cross})

    #     return check_bbcross

if __name__ == "__main__":
    import gathering
    import indicator

    mod = gathering.Gathering()
    mod.get_stock('000660', '2000-01-01', '2020-01-01', interval='w')


    tech_indi.RSI(mod.df)

    print(mod.df)

    result = mod.df.reset_index()
    for idx, row in result.iterrows():
        # print(idx)
        # if row['rsi'] > 70 and result.iloc[idx-1]['rsi'] < 70:
        #     print(idx, row)
        if crossUp(row, idx, result, 'rsi', 70):
            print('상향돌파')
            print(row)
    
    