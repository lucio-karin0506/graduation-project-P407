import pandas
'''
[return type]
- 1: 오류 없음
- 0: 오류 발생
'''
def is_df(df):
    '''
    datafrmae 타입 검증 및 데이터 존재 여부 검증'''
    return 1 if ((type(df) == pandas.core.frame.DataFrame) and (len(df) != 0)) else 0

def is_series(series):
    '''series 타입 검증 및 데이터 존재 여부 검증'''
    return 1 if ((type(series) == pandas.core.series.Series) and (len(series) != 0)) else 0

def is_integer(integer):
    '''int 타입 검증'''
    return 1 if (type(integer) == int) else 0

def is_pos(integer):
    '''양수 검증'''
    if is_integer(integer):
        return 1 if (integer > 0) else 0

def is_neg(integer):
    ''' 음수 검증'''
    if is_integer(integer):
        return 1 if (integer < 0) else 0

def is_float(num_float):
    '''실수 검증'''
    return 1 if (type(num_float) == float) else 0

def is_dflen(df, params):
    '''데이터 개수 검증'''
    if type(params) != list:
        params = [params]
    return 1 if len(df) >= max(params) else 0

def is_column(df, c_name):
    '''컬럼 명 검증'''
    if type(c_name) == str:
        c_name = [c_name]
    for name in c_name:
        if name in df.columns:
            continue
        else:
            return 0
    return 1

def cross_up(source, target):
    '''상향돌파
    (prev_source <= prev_target) and (curr_source > curr_target)
    source:Series, target:int or float or series'''
    # source 타입 오류 체크
    if is_series(source):
        prev_source = source.shift(1)
        # target 타입 오류 체크
        if is_integer(target) or is_float(target):
            prev_target = target
        elif is_series(target):
            prev_target = target.shift(1)
        else:#오류
            return 0
    else:
        return 0
    return source[((prev_source <= prev_target) & (source > target))].index

def cross_down(source, target):
    '''하향돌파
    (prev_source >= prev_target) and (curr_source < curr_target)
    source:Series, target:int or float or series'''
    # source 타입 오류 체크
    if is_series(source):
        prev_source = source.shift(1)
        # target 타입 오류 체크
        if is_integer(target) or is_float(target):
            prev_target = target
        elif is_series(target):
            prev_target = target.shift(1)
        else:
            return 0
    else:
        return 0
    return source[((prev_source >= prev_target) & (source < target))].index
