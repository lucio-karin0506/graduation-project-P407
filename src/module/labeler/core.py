import pandas

def is_df(df):
    """
    datafrmae 타입 검증 및 데이터 존재 여부 검증

    Parameters
    ----------
    df : Dataframe

    Returns
    -------
    int
        1: 조건 만족
        0: 조건 불만족

    """
    try:
        return 1 if (isinstance(df, pandas.core.frame.DataFrame) and (len(df) != 0)) else 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0

def is_series(series):
    """
    series 타입 검증 및 데이터 존재 여부 검증

    Parameters
    ----------
    series : Series

    Returns
    -------
    int
        1: 조건 만족
        0: 조건 불만족

    """
    try:
        return 1 if (isinstance(series, pandas.core.series.Series) and (len(series) != 0)) else 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0

def is_posint(num, zero=True):
    """
    identify whether num is integer and positive number
    
    Parameters
    ----------
    num : int
        
    zero : Boolen, optional
        True: 0 포함, False: 0 미포함, The default is True.

    Returns
    -------
    int
        1: 조건 만족
        0: 조건 불만족
    """
    try:
        if not isinstance(num, list):
            num = [num]    
        for i in num:
            if isinstance(i, int):
                if (zero==True) and (i<0):
                    return 0
                elif (zero==False) and (i<=0):
                    return 0
            else:
                return 0
        return 1
    except Exception as error:
        print('<Error occurs>', error)
        return 0

def is_posfloat(num, zero=True):
    """
    identify whether num is float and positive number
    
    Parameters
    ----------
    num : float
        
    zero : Boolen, optional
        True: 0 포함, False: 0 미포함, The default is True.

    Returns
    -------
    int
        1: 조건 만족
        0: 조건 불만족

    """
    try:
        if not isinstance(num, list):
            num = [num]
        for i in num:
            if (zero==True) and (i==0):
                continue
            elif isinstance(i, float):
                if (zero==True) and (i<0):
                    return 0
                elif (zero==False) and (i<=0):
                    return 0
            else:
                return 0
        return 1
    except Exception as error:
        print('<Error occurs>', error)
        return 0

def is_pos(num, zero=True):
    '''양의 정수 or 양의 실수 검증'''
    """
    identify whether num is positive number
    
    Parameters
    ----------
    num : int, float
        
    zero : Boolen, optional
        True: 0 포함, False: 0 미포함, The default is True.

    Returns
    -------
    int
        1: 조건 만족
        0: 조건 불만족

    """
    try:
        if not isinstance(num, list):
            num = [num]
        for i in num:
            if isinstance(i, float) or isinstance(i, int):
                if (zero==True) & (i<0):
                    return 0
                elif (zero==False) & (i<=0):
                    return 0
            else:
                return 0
        return 1
    except Exception as error:
        print('<Error occurs>', error)
        return 0

def is_dflen(df, params):
    """
    Dataframe's row 개수 검증
    len(df) >= params
    
    Parameters
    ----------
    df : Datafrmae
        
    params : list(int)
        
    Returns
    -------
    int
        1: 조건 만족
        0: 조건 불만족
    """
    try:
        if is_df(df) and is_pos(params, zero=True):
            if not isinstance(params, list):
                params = [params]
            return 1 if len(df) >= max(params) else 0
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0

def is_column(df, c_name):
    """
    Dataframe's columns name 검증
    identify whether c_name is in df's columns

    Parameters
    ----------
    df : Datafrmae
    c_name : list(str)
        ['column1', 'column2', ...]

    Returns
    -------
    int
        1: 조건 만족
        0: 조건 불만족
    """
    try:
        if isinstance(c_name, str):
            c_name = [c_name]
        for name in c_name:
            if name in df.columns:
                continue
            else:
                return 0
        return 1
    except Exception as error:
        print('<Error occurs>', error)
        return 0

def cross_up(source, target):
    """
    상향돌파
    (prev_target >= prev_source) and (curr_target < curr_sourc)
    Parameters
    ----------
    source : Series
        
    target : Series or Int or Float
        
    Returns
    -------
    index:
        cross_up 조건을 만족하는 인덱스 반환.
    0:
        오류 발생
    """
    # source 타입 오류 체크
    try:
        if is_series(source):
            prev_source = source.shift(1)
            # target 타입 오류 체크
            if isinstance(target, int) or isinstance(target, float):
                prev_target = target
            elif is_series(target):
                prev_target = target.shift(1)
            else:#오류
                return 0
        else:
            return 0
        return source[((prev_source <= prev_target) & (source > target))].index
    except Exception as error:
        print('<Error occurs>', error)
        return 0

def cross_down(source, target):
    """
    하향돌파
    (prev_source >= prev_target) and (curr_source < curr_target)

    Parameters
    ----------
    source : Series
        
    target : Series or Int or Float
        
    Returns
    -------
    index
        cross_down 조건을 만족하는 인덱스 반환.
    0
        오류 발생
    """
    try:
        # source 타입 오류 체크
        if is_series(source):
            prev_source = source.shift(1)
            # target 타입 오류 체크
            if isinstance(target, int) or isinstance(target, float):
                prev_target = target
            elif is_series(target):
                prev_target = target.shift(1)
            else:
                return 0
        else:
            return 0
        return source[((prev_source >= prev_target) & (source < target))].index
    except Exception as error:
        print('<Error occurs>', error)
        return 0

def is_RRPB(df, local_min, local_max, label_target, RRPB):
    """
    RRPB조건 만족 판별
    
    Parameters
    ----------
    df : Dataframe
    local_min : index
        bottom candidate.
    local_max : index
        top candidate.
    label_target : str or list(str)
        column name.
    RRPB : float or int
        Ratio of Rising to Previous Bottom.

    Returns
    -------
    int
        1: RRPB 조건 만족
        0: RROB 조건 불만족
    """
    try:
        if RRPB <= (df.loc[local_max, label_target] / df.loc[local_min, label_target]) - 1:
            return 1
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0



def is_RFPT(df, local_min, local_max, label_target, RFPT):
    """
    RFPT조건 만족 판별
    
    Parameters
    ----------
    df : Dataframe
    local_min : index
        bottom candidate.
    local_max : index
        top candidate.
    label_target : str or list(str)
        column name.
    RFPT : float or int
        Ratio of Fall to Previous Top
        
    Returns
    -------
    int
        1: RFPT조건 만족
        0: RFPT조건 불만족
    """
    try:
        if RFPT <= 1 - (df.loc[local_min, label_target] / df.loc[local_max, label_target]):
            return 1
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0

def ws_cross(gold, dead, size=0):
    """
    cross 연속발생시 선행사건제거 함수

    Parameters
    ----------
    gold : list(index)
        GoldenCross Index
    dead : list(index)
        DeadCross Index
    size : int, optional
        연속발생 횟수. The default is 0.

    Returns
    -------
    (list(index), list(index))
        (GoldenCross_index, DeadCross_index).
    (0, 0)
        오류 발생.

    """
    try:
        if size == 0:
            return gold, dead
        else:
            if not isinstance(gold, list):
                goldl = gold.tolist()
            if not isinstance(dead, list):
                deadl = dead.tolist()
            if isinstance(goldl, list) & isinstance(deadl, list) & (size >= 0) & isinstance(size, int):
                cross = goldl + deadl
                cross.sort()
    
                rem_cross = [i for i in cross[:-size] if (is_inlist(list(range(i+1, i+size+1)), cross) == 0)]
                rem_cross = rem_cross + cross[-size:]
    
                return [i for i in goldl if i in rem_cross], [i for i in deadl if i in rem_cross]
        return 0, 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0, 0

def is_inlist(list1, list2):
    """
    identify wheter all of list1's elements in list2

    Parameters
    ----------
    list1 : list
        
    list2 : list
        
    Returns
    -------
    int
        1: 포함 O
        0: 포함 X

    """
    try:
        for i in list1:
            if i not in list2:
                return 0
        return 1
    except Exception as error:
        print('<Error occurs>', error)
        return 0
