"""
Created on 2021.1.23

@author: 김상혁
"""

def crossUp(row:"Series", idx:int, df:"DataFrame", source:str, target:str or int) -> bool:
    """
    source가 target을 상향돌파 했음을 T/F로 반환한다.
    
    Parameters
    ----------
    row: row of DataFrame that is series
    idx: index of row
    df: Stock DataFrame
    source: Column name of DataFrame
        상향돌파를 확인할 컬럼
    target:{string, integer}
        source와 비교할 기준
        문자열이면 데이터프레임의 컬럼이고 정수이면 기준값
        
    Returns
    -------
    bool        
    """ 
    
    if type(target) is int:
        if idx == 0:
            return False
        else:
            if (row[source] > target) and (df.iloc[idx-1][source] < target):
                return True
        
            else:
                return False
    
    elif type(target) is str:
        if idx == 0:
            return False
        else:
            if (row[source] > df.iloc[idx][target]) and (df.iloc[idx-1][source] < df.iloc[idx-1][target]):
                return True
        
            else:
                return False

def crossDown(row:"Series", idx:int, df:"DataFrame", source:str, target:str or int) -> bool:
    """
    source가 target을 하향돌파 했음을 T/F로 반환한다.
    
    Parameters
    ----------
    row: row of DataFrame that is series
    idx: index of row
    df: Stock DataFrame
    source: Column name of DataFrame
        하향돌파를 확인할 컬럼
    target:{string, integer}
        source와 비교할 기준
        문자열이면 데이터프레임의 컬럼이고 정수이면 기준값
        
    Returns
    -------
    bool        
    """ 
    
    if type(target) is int:
        if idx == 0:
            return False
        else:
            if (row[source] < target) and (df.iloc[idx-1][source] > target):
                return True
            
            else:
                return False

    elif type(target) is str:
        if idx == 0:
            return False
        else:
            if (row[source] < df.iloc[idx][target]) and (df.iloc[idx-1][source] > df.iloc[idx-1][target]):
                return True
            
            else:
                return False

if __name__ == "__main__":
    import gatherer
    from indicator import *

    mod = gatherer.Gatherer()
    df, _ = mod.get_stock('000660', '2000-01-01', '2020-01-01', interval='w')


    add_RSI(df)

    # print(df)

    result = df.reset_index()
    for idx, row in result.iterrows():
        # print(idx)
        # if row['rsi'] > 70 and result.iloc[idx-1]['rsi'] < 70:
        #     print(idx, row)
        if crossUp(row, idx, result, 'rsi_14', 70):
            print('상향돌파')
            print(row)