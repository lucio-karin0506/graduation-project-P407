# In[1]:
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
import talib as ta
import module.labeler.core as core
from module.order_creator.gatherer import Gatherer

# In[4]:

def candle_type(df):
    ###################################
    # 봉 종류 레이블
    # column: candle_type
    # category: red(양봉), blue(음봉)
    # parameter: none
    ##################################
    if core.is_df(df):
        df['candle_type'] = False
        df.loc[df[df['close'] > df['open']].index, 'candle_type'] = 'red'
        df.loc[df[df['close'] < df['open']].index, 'candle_type'] = 'blue'
        return df
    else:
        return 0


# In[5]:


def candle_shape(df):
    '''봉 모양 레이블'''
    #################################################
    # 봉 모양 레이블
    # column: candle_shape
    # category: fullred(장대양봉), fullblue(장대음봉)
    # parameter: none
    #################################################
    if core.is_df(df):
        df['candle_shape'] = False
        o_l = df['open'] == df['low']
        c_h = df['close'] == df['high']
        o_h = df['open'] == df['high']
        c_l = df['close'] == df['low']
        df.loc[df[o_l & c_h].index, 'candle_shape'] = 'full_red'
        df.loc[df[o_h & c_l].index, 'candle_shape'] = 'full_blue'
        return df
    else:
        return 0


# In[6]:


def three_red(df, num=3):
    '''적삼병 레이블'''
    #####################################################
    # 적삼병 레이블
    # column: three_red
    # category: 1(적삼병), 0(적삼병 외)
    # parameter: num(적삼병이 나타나는 최소한의 봉 개수)
    #####################################################
    if core.is_df(df) & core.is_pos(num):
        df['three_red'] = False

        def check_tr(ndf):
            ndf.reset_index(inplace=True)
            for i in range(1, len(ndf)):
                con1 = ndf.loc[i - 1, 'low'] < ndf.loc[i, 'low']
                con2 = ndf.loc[i - 1, 'high'] < ndf.loc[i, 'high']
                con3 = ndf.loc[i - 1, 'close'] > ndf.loc[i - 1, 'open']
                con4 = ndf.loc[i, 'close'] > ndf.loc[i, 'open']
                if con1 and con2 and con3 and con4:
                    continue
                else:
                    return 0
            return 1

        row = 0
        while row <= len(df) - num:
            if check_tr(df[row:row + num]):
                df.loc[df.index[row + num - 1], 'three_red'] = 1
            row += 1
        return df
    else:
        return 0


# In[7]:


def three_blue(df, num=3):
    '''흑삼병 레이블'''
    #####################################################
    # 흑삼병 레이블
    # column: three_blue
    # category: 1(흑삼병), 0(적삼병 외)
    # parameter: num(흑삼병이 나타나는 최소한의 봉 개수)
    #####################################################
    if core.is_df(df) & core.is_pos(num):
        df['three_blue'] = False

        def check_tb(ndf, num):
            ndf.reset_index(inplace=True)
            for i in range(1, num):
                con1 = ndf.loc[i - 1, 'low'] > ndf.loc[i, 'low']
                con2 = ndf.loc[i - 1, 'high'] > ndf.loc[i, 'high']
                con3 = ndf.loc[i - 1, 'close'] < ndf.loc[i - 1, 'open']
                con4 = ndf.loc[i, 'close'] < ndf.loc[i, 'open']
                if con1 and con2 and con3 and con4:
                    continue
                else:
                    return 0
            return 1

        row = 0
        while row <= len(df) - num:
            if check_tb(df[row:row + num], num):
                df.loc[df.index[row + num - 1], 'three_blue'] = 1
            row += 1
        return df
    else:
        return 0


# In[8]:


def n_gap(df, num=0):
    '''갭 상승/하락 레이블'''
    #####################################################
    # 갭 상승/하락 레이블
    # column: n%_gap
    # category: gap_up(갭 상승), gap_down(갭 하락)
    # parameter: num(금봉 시가 에 대한 전봉 종가 대비 상승/하락 비율)
    #####################################################
    if core.is_df(df) & (num >= 0) & (core.is_integer(num) | core.is_float(num)):
        c_name = f'gap_{num}%'
        df[c_name] = False
        df.reset_index(inplace=True)
        for i in range(1, len(df)):
            up_con1 = df.loc[i - 1, 'close'] > df.loc[i - 1, 'open']
            up_con2 = df.loc[i, 'close'] > df.loc[i, 'open']
            up_con3 = df.loc[i, 'open'] >= df.loc[i - 1, 'close'] * (1 + num / 100)
            down_con1 = df.loc[i - 1, 'close'] < df.loc[i - 1, 'open']
            down_con2 = df.loc[i, 'close'] < df.loc[i, 'open']
            down_con3 = df.loc[i, 'open'] <= df.loc[i - 1, 'close'] * (1 - num / 100)
            if up_con1 and up_con2 and up_con3:
                df.loc[i, c_name] = 'gap_up'
            elif down_con1 and down_con2 and down_con3:
                df.loc[i, c_name] = 'gap_down'
        df.set_index('Date', inplace=True)
        return df
    else:
        return 0


# In[9]:


def roc(df, period=12, target='close'):
    '''rate of change의 plus/minus 레이블'''
    #####################################################
    # rate of change의 plus/minus 레이블
    # column: roc_{period}({target})
    # category: plus, minus
    # parameter: prev_day(~일 전)
    #####################################################

    if core.is_df(df) & core.is_pos(period) & core.is_dflen(df, period) & core.is_column(df, target):
        df.reset_index(inplace=True)
        if type(target) == str:
            target = [target]
        for tar in target:
            c_name = f'roc_{period}({tar})'
            df[c_name] = False

            roc = ta.ROC(df['close'], timeperiod=14)
            df.loc[df[roc < 0].index, c_name] = 'minus'
            df.loc[df[roc > 0].index, c_name] = 'plus'

        df.set_index('Date', inplace=True)
        return df
    else:
        return 0


# In[10]:


def sma_cross(df, short=5, long=20, target='close'):
    '''단순이동평균 골든크로스/데드크로스 레이블'''
    #####################################################
    # 단순이동평균 골든크로스/데드크로스 레이블
    # column: {short}-{long}_cross
    # category: golden_cross, dead_cross
    # parameter: short(단기이동평균 기간), long(장기이동평균 기간)
    #####################################################

    if core.is_df(df) & core.is_pos(short) & core.is_pos(long) & core.is_dflen(df, [short, long]) & core.is_column(df,
                                                                                                                   target):
        df.reset_index(inplace=True)
        if type(target) == str:
            target = [target]
        for tar in target:
            c_name = f'ma_cross_{short}_{long}({tar})'
            df[c_name] = False

            short_ma = ta.MA(df[tar], timeperiod=short)
            long_ma = ta.MA(df[tar], timeperiod=long)

            df.loc[core.cross_up(short_ma, long_ma), c_name] = 'golden_cross'
            df.loc[core.cross_down(short_ma, long_ma), c_name] = 'dead_cross'

        df.set_index('Date', inplace=True)
        return df
    else:
        return 0


# In[11]:


def dema_cross(df, short=5, long=20, target='close'):
    '''이중지수이동평균 골든크로스/데드크로스 레이블'''
    #####################################################
    # 이중지수이동평균 골든크로스/데드크로스 레이블
    # column: {short}-{long}_cross
    # category: golden_cross, dead_cross
    # parameter: short(단기이중지수이동평균 기간), long(장기이중지수이동평균 기간)
    #####################################################

    if core.is_df(df) & core.is_pos(short) & core.is_pos(long) & core.is_dflen(df, [short, long]) & core.is_column(df,
                                                                                                                   target):
        df.reset_index(inplace=True)
        if type(target) == str:
            target = [target]
        for tar in target:
            c_name = f'dema_cross_{short}_{long}({tar})'
            df[c_name] = False

            short_ma = ta.DEMA(df[tar], timeperiod=short)
            long_ma = ta.DEMA(df[tar], timeperiod=long)

            df.loc[core.cross_up(short_ma, long_ma), c_name] = 'golden_cross'
            df.loc[core.cross_down(short_ma, long_ma), c_name] = 'dead_cross'

        df.set_index('Date', inplace=True)
        return df
    else:
        return 0


# In[12]:


def vwma_cross(df, short=5, long=20, target='close'):
    '''거래량가중이동평균 골든크로스/데드크로스 레이블'''
    #####################################################
    # 거래량가중이동평균 골든크로스/데드크로스 레이블
    # column: {short}-{long}_cross
    # category: golden_cross, dead_cross
    # parameter: short(단기이동평균 기간), long(장기이동평균 기간)
    #####################################################
    if core.is_df(df) & core.is_pos(short) & core.is_pos(long) & core.is_dflen(df, [short, long]) & core.is_column(df,
                                                                                                                   target):
        df.reset_index(inplace=True)
        if type(target) == str:
            target = [target]
        for tar in target:
            c_name = f'vwma_cross_{short}_{long}({tar})'
            df[c_name] = False

            pv = df[tar] * df['volume']
            short_vwma = ta.MA(pv, timeperiod=short) / ta.MA(df['volume'], timeperiod=short)
            long_vwma = ta.MA(pv, timeperiod=long) / ta.MA(df['volume'], timeperiod=long)

            df.loc[core.cross_up(short_vwma, long_vwma), c_name] = 'golden_cross'
            df.loc[core.cross_down(short_vwma, long_vwma), c_name] = 'dead_cross'

        df.set_index('Date', inplace=True)
        return df
    else:
        return 0


# In[13]:


def macd(df, short=12, long=26, target='close'):
    '''MACD 양수/음수 레이블'''
    #####################################################
    # MACD 양수/음수 레이블
    # column: macd(target)
    # category: plus, minus
    # parameter: short(단기지수이동평균 기간), long(장기지수이동평균 기간), target(지표 생성 기준 컬럼)
    #####################################################

    ## 추가: MACD는 상장이후 모든 데이터 생성하여 레이블링한 후 기간에 맞는 컬럼을 인풋 데이터프레임에 추가 후 반환
    if core.is_df(df) & core.is_pos(short) & core.is_pos(short) & core.is_dflen(df, [short, long]) & core.is_column(df,
                                                                                                                    target):
        if type(target) == str:
            target = [target]
        for tar in target:
            col_name = f'macd_{short}_{long}({tar})'
            df[col_name] = False
            macd = ta.EMA(df[tar], short) - ta.EMA(df[tar], long)
            df.loc[macd[macd > 0].index, col_name] = 'plus'
            df.loc[macd[macd < 0].index, col_name] = 'minus'
        return df
    else:
        return 0


# In[14]:


def bbands(df, period=20, multid=2, target='close'):
    '''Bollinger Bands 상한선, 중심선, 하한선 기준 위치 레이블링'''
    #####################################################
    # Bollinger Bands 상한선, 중심선, 하한선 기준 위치 레이블링
    # column: bb_perod_multid(target)
    # category: over_up(상한선 이상), between_center_up(상한선 미만 중심선 이상), between_center_down(중심선 미만 하한선 이상), under_down(하한선 미만)
    # parameter: short(단기이동평균 기간), long(장기이동평균 기간), target(지표 생성 기준 컬럼)
    #####################################################
    if core.is_df(df) & core.is_pos(period) & (multid >= 0) & (
            core.is_integer(multid) | core.is_float(multid)) & core.is_column(df, target):
        if type(target) == str:
            target = [target]
        for tar in target:
            col_name = f'bb_{period}_{multid}({tar})'
            df[col_name] = False
            ubb, mbb, lbb = ta.BBANDS(df[tar], timeperiod=period, nbdevup=multid, nbdevdn=multid)
            over_up = df[tar] >= ubb
            under_up = df[tar] < ubb
            over_center = df[tar] >= mbb
            under_center = df[tar] < mbb
            over_down = df[tar] >= lbb
            under_down = df[tar] < lbb
            df.loc[df[over_up].index, col_name] = 'over_up'
            df.loc[df[under_up & over_center].index, col_name] = 'between_center_up'
            df.loc[df[under_center & over_down].index, col_name] = 'between_center_down'
            df.loc[df[under_down].index, col_name] = 'under_down'
        return df
    else:
        return 0


# In[15]:


def macd_cross(df, short=12, long=26, signal=9, target='close'):
    '''MACD와 MACD_SIGNAL의 골든크로스/데드크로스 레이블'''
    #####################################################
    # MACD와 MACD_SIGNAL의 골든크로스/데드크로스 레이블
    # column: macd_cross_short_long_singal(target)
    # category: golden_cross(MACD가 SIGNAL을 상향돌파), dead_cross(MACD가 SIGNAL을 하향돌파)
    # parameter: short(MACD의 단기지수이동평균 기간), long(MACD의 장기지수이동평균 기간), signal(MACD의 지수이동평균), target(지표 생성 기준 컬럼)
    #####################################################

    if core.is_df(df) & core.is_pos(short) & core.is_pos(long) & core.is_pos(signal) & core.is_dflen(df, [short, long,
                                                                                                          signal]) & core.is_column(
            df, target):
        df.reset_index(inplace=True)
        if type(target) == str:
            target = [target]
        for tar in target:
            c_name = f'macd_cross_{short}_{long}_{signal}({tar})'
            df[c_name] = False
            macd = ta.EMA(df[tar], short) - ta.EMA(df[tar], long)
            macd_sig = ta.EMA(macd, signal)
            df.loc[core.cross_up(macd, macd_sig), c_name] = 'golden_cross'
            df.loc[core.cross_down(macd, macd_sig), c_name] = 'dead_cross'
        df.set_index('Date', inplace=True)
        return df
    else:
        return 0


# In[16]:


def stochf(df, fastk_period=5, fastd_period=3):
    '''FAST STOCHASTING 골든크로스/데드코로스 레이블'''
    #####################################################
    # FAST STOCHASTING 골든크로스/데드코로스 레이블
    # column: stockf_{fastk_period}_{fastd_period}
    # category: golden_cross(%k가 %d를 상향돌파), dead_cross(%k가 %d를 하향돌파)
    # parameter: fastk_period(k곡선 기간), fastd_period(d곡선 기간)
    #####################################################
    if core.is_df(df) & core.is_pos(fastk_period) & core.is_pos(fastd_period) & core.is_dflen(df, [fastk_period,
                                                                                                   fastd_period]):
        df.reset_index(inplace=True)
        c_name = f'stochf_{fastk_period}_{fastd_period}'
        df[c_name] = False
        fastk, fastd = ta.STOCHF(df['high'], df['low'], df['close'], fastk_period=fastk_period,
                                 fastd_period=fastd_period)
        df.loc[core.cross_up(fastk, fastd), c_name] = 'golden_cross'
        df.loc[core.cross_down(fastk, fastd), c_name] = 'dead_cross'
        df.set_index('Date', inplace=True)
        return df
    else:
        return 0


# In[17]:


def stoch(df, fastk_period=5, slowk_period=3, slowd_period=3):
    '''SLOW STOCHASTING 골든크로스/데드크로스 레이블'''
    #####################################################
    # SLOW STOCHASTING 골든크로스/데드코로스 레이블
    # column: stockf_{fastk_period}_{slowk_period}_{slowd_period}
    # category: golden_cross(%k가 %d를 상향돌파), dead_cross(%k가 %d를 하향돌파)
    # parameter: fastk_period(fast_k곡선 기간), slowk_period(slow%k곡선 기간), slowd_period(slow%d곡선 기간)
    #####################################################
    if core.is_df(df) & core.is_pos(fastk_period) & core.is_pos(slowk_period) & core.is_pos(
            slowd_period) & core.is_dflen(df, [fastk_period, slowk_period, slowd_period]):
        df.reset_index(inplace=True)
        c_name = f'stoch_{fastk_period}_{slowk_period}_{slowd_period}'
        df[c_name] = False
        # stochasting 지표 생성
        slowk, slowd = ta.STOCH(df['high'], df['low'], df['close'], fastk_period=fastk_period,
                                slowk_period=slowk_period, slowd_period=slowd_period)
        df.loc[core.cross_up(slowk, slowd), c_name] = 'golden_cross'
        df.loc[core.cross_down(slowk, slowd), c_name] = 'dead_cross'
        df.set_index('Date', inplace=True)
        return df
    else:
        return 0
