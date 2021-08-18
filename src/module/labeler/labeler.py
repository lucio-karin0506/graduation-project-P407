import talib as ta
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from module.labeler import core


def add_candle_type(df):
    ###################################
    # 봉 종류 레이블
    # column: candle_type
    # category: red(양봉), blue(음봉)
    # parameter: none
    ##################################
    try:
        if core.is_df(df):
            df['candle_type'] = 0
            df.loc[df[df['close'] > df['open']].index,'candle_type'] = 1
            df.loc[df[df['close'] < df['open']].index,'candle_type'] = -1
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0
    
def add_candle_shape(df):
    '''봉 모양 레이블'''
    #################################################
    # 봉 모양 레이블
    # column: candle_shape
    # category: fullred(장대양봉), fullblue(장대음봉)
    # parameter: none
    #################################################
    try:
        if core.is_df(df):
            df['candle_shape'] = 0
            o_l = df['open'] == df['low']
            c_h = df['close'] == df['high']
            o_h = df['open'] == df['high']
            c_l = df['close'] == df['low']
            df.loc[df[o_l & c_h].index, 'candle_shape'] = 1
            df.loc[df[o_h & c_l].index, 'candle_shape'] = -1
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0
    
def add_three_red(df, num=3):
    '''적삼병 레이블'''
    #####################################################
    # 적삼병 레이블
    # column: three_red
    # category: 1(적삼병), 0(외)
    # parameter: num(적삼병이 나타나는 최소한의 봉 개수)
    #####################################################
    try:
        if core.is_df(df) & core.is_posint(num, zero=False):
            df[f'three_red_{num}'] = 0
            def check_tr(ndf):
                ndf.reset_index(inplace=True)
                for i in range(1, len(ndf)):
                    con1 = ndf.loc[i-1, 'low'] < ndf.loc[i,'low']
                    con2 = ndf.loc[i-1, 'high'] < ndf.loc[i, 'high']
                    con3 = ndf.loc[i-1, 'close'] > ndf.loc[i-1, 'open']
                    con4 = ndf.loc[i, 'close'] > ndf.loc[i, 'open']
                    if con1 and con2 and con3 and con4:
                        continue
                    else:
                        return 0
                return 1
            row = 0
            while row <= len(df)-num:
                if check_tr(df[row:row+num]):
                    df.loc[df.index[row+num-1], f'three_red_{num}'] = 1
                row += 1
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0
    
def add_three_blue(df, num=3):
    '''흑삼병 레이블'''
    #####################################################
    # 흑삼병 레이블
    # column: three_blue
    # category: 1(흑삼병), 0(적삼병 외)
    # parameter: num(흑삼병이 나타나는 최소한의 봉 개수)
    #####################################################
    try:
        if core.is_df(df) & core.is_posint(num, zero=False):
            df[f'three_blue_{num}'] = 0
            def check_tb(ndf, num):
                ndf.reset_index(inplace=True)
                for i in range(1, num):
                    con1 = ndf.loc[i-1, 'low'] > ndf.loc[i,'low']
                    con2 = ndf.loc[i-1, 'high'] > ndf.loc[i, 'high']
                    con3 = ndf.loc[i-1, 'close'] < ndf.loc[i-1, 'open']
                    con4 = ndf.loc[i, 'close'] < ndf.loc[i, 'open']
                    if con1 and con2 and con3 and con4:
                        continue
                    else:
                        return 0
                return 1
            row = 0
            while row <= len(df)-num:
                if check_tb(df[row:row+num], num):
                    df.loc[df.index[row+num-1], f'three_blue_{num}'] = 1
                row += 1
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0
    
def add_n_gap(df, num=0):
    '''갭 상승/하락 레이블'''
    #####################################################
    # 갭 상승/하락 레이블
    # column: n%_gap
    # category: gap_up(갭 상승), gap_down(갭 하락)
    # parameter: num(금봉 시가 에 대한 전봉 종가 대비 상승/하락 비율)
    #####################################################
    try:
        if core.is_df(df) & core.is_pos(num, zero=True):
            c_name = f'gap_{num}'
            df[c_name] = 0
            df.reset_index(inplace=True)
            for i in range(1, len(df)):
                up_con1 = df.loc[i-1,'close'] > df.loc[i-1, 'open']
                up_con2 = df.loc[i, 'close'] > df.loc[i, 'open']
                up_con3 = df.loc[i, 'open'] >= df.loc[i-1, 'close'] * (1 + num)
                down_con1 = df.loc[i-1, 'close'] < df.loc[i-1, 'open']
                down_con2 = df.loc[i, 'close'] < df.loc[i, 'open']
                down_con3 = df.loc[i, 'open'] <= df.loc[i-1, 'close'] * (1 - num)
                if up_con1 and up_con2 and up_con3:
                    df.loc[i, c_name] = 1  
                elif down_con1 and down_con2 and down_con3:
                    df.loc[i, c_name] = -1
            df.set_index('Date', inplace=True)
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0
    
def add_roc_classify(df, period=12, target='close'):
    '''rate of change의 plus/minus 레이블'''
    #####################################################
    # rate of change의 plus/minus 레이블
    # column: roc_{period}({target})
    # category: plus, minus
    # parameter: prev_day(~일 전)
    #####################################################
    try:
        if core.is_df(df) & core.is_posint(period, zero=False) & core.is_dflen(df, period) & core.is_column(df, target):
            df.reset_index(inplace=True)
            if isinstance(target, str):
                target = [target]
            for tar in target:
                c_name = f'roc_classify_{period}({tar})'
                df[c_name] = 0
    
                roc = ta.ROC(df['close'], timeperiod=14)
                df.loc[df[roc<0].index, c_name] = 1
                df.loc[df[roc>0].index, c_name] = -1
    
            df.set_index('Date', inplace=True)
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0
    
def add_sma_cross(df, short=5, long=20, window_size=0, target='close'):
    '''단순이동평균 골든크로스/데드크로스 레이블'''
    #####################################################
    # 단순이동평균 골든크로스/데드크로스 레이블
    # column: {short}-{long}_cross
    # category: golden_cross, dead_cross
    # parameter: short(단기이동평균 기간), long(장기이동평균 기간)
    #####################################################
    try:
        if core.is_df(df) & core.is_posint([short, long], zero=False) & core.is_posint(window_size, zero=True) & core.is_dflen(df, [short, long]) & core.is_column(df, target):
            df.reset_index(inplace=True)
            if isinstance(target, str):
                target = [target]
            for tar in target:
                c_name = f'sma_cross_{short}_{long}_{window_size}({tar})'
                df[c_name] = 0
                
                short_ma = ta.MA(df[tar], timeperiod = short)
                long_ma = ta.MA(df[tar], timeperiod = long)
                gold, dead = core.ws_cross(core.cross_up(short_ma, long_ma), core.cross_down(short_ma, long_ma), window_size)
                df.loc[gold, c_name] = 1
                df.loc[dead, c_name] = -1
    
            df.set_index('Date', inplace=True)
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0
    
def add_dema_cross(df, short=5, long=20, window_size=0, target='close'):
    '''이중지수이동평균 골든크로스/데드크로스 레이블'''
    #####################################################
    # 이중지수이동평균 골든크로스/데드크로스 레이블
    # column: {short}-{long}_cross
    # category: golden_cross, dead_cross
    # parameter: short(단기이중지수이동평균 기간), long(장기이중지수이동평균 기간)
    #####################################################
    try:
        if core.is_df(df) & core.is_posint([short,long], zero=False) & core.is_posint(window_size, zero=True) & core.is_dflen(df, [short, long]) & core.is_column(df, target):
            df.reset_index(inplace=True)
            if isinstance(target, str):
                target = [target]
            for tar in target:
                c_name = f'dema_cross_{short}_{long}_{window_size}({tar})'
                df[c_name] = 0
    
                short_ma = ta.DEMA(df[tar], timeperiod = short)
                long_ma = ta.DEMA(df[tar], timeperiod = long)
                
                gold, dead = core.ws_cross(core.cross_up(short_ma, long_ma), core.cross_down(short_ma, long_ma), window_size)
                df.loc[gold, c_name] = 1
                df.loc[dead, c_name] = -1
    
            df.set_index('Date', inplace=True)
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0
    
def add_vwma_cross(df, short=5, long=20, window_size=0, target='close'):
    '''거래량가중이동평균 골든크로스/데드크로스 레이블'''
    #####################################################
    # 거래량가중이동평균 골든크로스/데드크로스 레이블
    # column: {short}-{long}_cross
    # category: golden_cross, dead_cross
    # parameter: short(단기이동평균 기간), long(장기이동평균 기간)
    #####################################################
    try:
        if core.is_df(df) & core.is_posint([short, long], zero=False)& core.is_posint(window_size, zero=True) & core.is_dflen(df, [short, long]) & core.is_column(df, target):
            df.reset_index(inplace=True)
            if isinstance(target, str):
                target = [target]
            for tar in target:
                c_name = f'vwma_cross_{short}_{long}_{window_size}({tar})'
                df[c_name] = 0
                
                pv = df[tar] * df['volume']
                short_ma = ta.MA(pv, timeperiod=short) / ta.MA(df['volume'], timeperiod=short)
                long_ma = ta.MA(pv, timeperiod=long) / ta.MA(df['volume'], timeperiod = long)
                
                gold, dead = core.ws_cross(core.cross_up(short_ma, long_ma), core.cross_down(short_ma, long_ma), window_size)
                df.loc[gold, c_name] = 1
                df.loc[dead, c_name] = -1
    
            df.set_index('Date', inplace=True)
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0
    
def add_macd_classify(df, short=12, long=26, target='close'):
    '''MACD 양수/음수 레이블'''
    #####################################################
    # MACD 양수/음수 레이블
    # column: macd(target)
    # category: plus, minus
    # parameter: short(단기지수이동평균 기간), long(장기지수이동평균 기간), target(지표 생성 기준 컬럼)
    #####################################################
    try:
        if core.is_df(df) & core.is_posint([short, long], zero=False) & core.is_dflen(df, [short, long]) & core.is_column(df, target):
            if isinstance(target, str):
                target = [target]
            for tar in target:
                col_name = f'macd_classify_{short}_{long}({tar})'
                df[col_name] = 0
                macd = ta.EMA(df[tar], short)- ta.EMA(df[tar], long)
                df.loc[macd[macd > 0].index, col_name] = 1
                df.loc[macd[macd < 0].index, col_name] = -1
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0

def add_macd_cross(df, short=12, long=26, signal=9, window_size=0, target='close'):
    '''MACD와 MACD_SIGNAL의 골든크로스/데드크로스 레이블'''
    #####################################################
    # MACD와 MACD_SIGNAL의 골든크로스/데드크로스 레이블
    # column: macd_cross_short_long_singal(target)
    # category: golden_cross(MACD가 SIGNAL을 상향돌파), dead_cross(MACD가 SIGNAL을 하향돌파)
    # parameter: short(MACD의 단기지수이동평균 기간), long(MACD의 장기지수이동평균 기간), signal(MACD의 지수이동평균), target(지표 생성 기준 컬럼)
    #####################################################
    try:
        if core.is_df(df) & core.is_posint([short, long, signal], zero=False) & core.is_posint(window_size, zero=True) & core.is_dflen(df, [short, long, signal]) & core.is_column(df, target):
            df.reset_index(inplace=True)
            if isinstance(target, str):
                target = [target]
            for tar in target:
                c_name = f'macd_cross_{short}_{long}_{signal}_{window_size}({tar})'
                df[c_name] = 0
                macd = ta.EMA(df[tar], short) - ta.EMA(df[tar], long)
                macd_sig = ta.EMA(macd, signal)
                gold, dead = core.ws_cross(core.cross_up(macd, macd_sig), core.cross_down(macd, macd_sig), window_size)
                df.loc[gold, c_name] = 1
                df.loc[dead, c_name] = -1
                
            df.set_index('Date', inplace=True)
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0
    
    
def add_bbands_classify(df, period=20, multid=2, target='close'):
    '''Bollinger Bands 상한선, 중심선, 하한선 기준 위치 레이블링'''
    #####################################################
    # Bollinger Bands 상한선, 중심선, 하한선 기준 위치 레이블링
    # column: bb_perod_multid(target)
    # category: over_up(상한선 이상), between_center_up(상한선 미만 중심선 이상), between_center_down(중심선 미만 하한선 이상), under_down(하한선 미만)
    # parameter: short(단기이동평균 기간), long(장기이동평균 기간), target(지표 생성 기준 컬럼)
    #####################################################
    try:
        if core.is_df(df) & core.is_posint(period, zero=False) & core.is_pos(multid, zero=False) & core.is_column(df, target):
            if isinstance(target, str):
                target = [target]
            for tar in target:
                col_name = f'bbands_classify_{period}_{multid}({tar})'
                df[col_name] = 0
                ubb, mbb, lbb = ta.BBANDS(df[tar], timeperiod=period, nbdevup=multid, nbdevdn=multid)
                over_up = df[tar] >= ubb
                under_up = df[tar] < ubb
                over_center = df[tar] >= mbb
                under_center = df[tar] < mbb
                over_down = df[tar] >= lbb
                under_down = df[tar] < lbb
                df.loc[df[over_up].index, col_name] = 2
                df.loc[df[under_up & over_center].index, col_name] = 1
                df.loc[df[under_center & over_down].index, col_name] = -1
                df.loc[df[under_down].index, col_name] = -2
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0
    
def add_stochf_cross(df, fastk_period=5, fastd_period=3, window_size=0):
    '''FAST STOCHASTING 골든크로스/데드코로스 레이블'''
    #####################################################
    # FAST STOCHASTING 골든크로스/데드코로스 레이블
    # column: stockf_{fastk_period}_{fastd_period}
    # category: golden_cross(%k가 %d를 상향돌파), dead_cross(%k가 %d를 하향돌파)
    # parameter: fastk_period(k곡선 기간), fastd_period(d곡선 기간)
    #####################################################
    try:
        if core.is_df(df) & core.is_posint([fastk_period, fastd_period], zero=False) & core.is_posint(window_size, zero=True)& core.is_dflen(df, [fastk_period, fastd_period]):
            df.reset_index(inplace=True)
            c_name = f'stochf_cross_{fastk_period}_{fastd_period}_{window_size}'
            df[c_name] = 0
            fastk, fastd = ta.STOCHF(df['high'], df['low'], df['close'], fastk_period=fastk_period, fastd_period=fastd_period)
            
            gold, dead = core.ws_cross(core.cross_up(fastk, fastd), core.cross_down(fastk, fastd), window_size)
            df.loc[gold, c_name] = 1
            df.loc[dead, c_name] = -1
            df.set_index('Date', inplace=True)
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0
    
def add_stoch_cross(df, fastk_period=5, slowk_period=3, slowd_period=3, window_size=0):
    '''SLOW STOCHASTING 골든크로스/데드크로스 레이블'''
    #####################################################
    # SLOW STOCHASTING 골든크로스/데드코로스 레이블
    # column: stockf_{fastk_period}_{slowk_period}_{slowd_period}
    # category: golden_cross(%k가 %d를 상향돌파), dead_cross(%k가 %d를 하향돌파)
    # parameter: fastk_period(fast_k곡선 기간), slowk_period(slow%k곡선 기간), slowd_period(slow%d곡선 기간)
    #####################################################
    try:
        if core.is_df(df) & core.is_posint([fastk_period, slowk_period, slowd_period], zero=False) & core.is_posint(window_size, zero=True)& core.is_dflen(df, [fastk_period, slowk_period, slowd_period]):
            df.reset_index(inplace=True)

            c_name = f'stoch_cross_{fastk_period}_{slowk_period}_{slowd_period}_{window_size}'

            df[c_name] = 0
            # stochasting 지표 생성
            slowk, slowd = ta.STOCH(df['high'], df['low'], df['close'], fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
            
            gold, dead = core.ws_cross(core.cross_up(slowk, slowd), core.cross_down(slowk, slowd), window_size)
            df.loc[gold, c_name] = 1
            df.loc[dead, c_name] = -1
            
            df.set_index('Date', inplace=True)
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0
    
def add_top_bottom(df, RRPB=0.03, RFPT=0.02, TBR=0.003, BBR=0.003, target='close'):
    '''최소 수익률 point 레이블'''
    #####################################################
    # 최소 수익률 point 레이블
    # column: top, bottom, top_zone, bottom_zone
    # category: 1(True), 0(False)
    # parameter: RRPB(최소 수익률), RFPT(횡보구간 비중), TBR(Top 주변 비율), BBR(Bottom 주변 비율)
    #####################################################
    def set_minmax(df, label_target):
        '''데이터프레임의 모든 열에 대해서 local_min, local_max를 식별한다.'''
        df = df.reset_index()
        # 모든 열에 대해서
        for i in range(1, len(df) - 1):
            # 직전 지점
            prev = df.loc[i - 1, label_target]
            # 현재 지점
            curr = df.loc[i, label_target]
            # 직후 지점
            next = df.loc[i + 1, label_target]

            ### 1. 좌상우평
            if prev > curr and next == curr:
                df.loc[i, 'local_min'] = 1
            ### 2. 좌평우상
            elif prev == curr and next > curr:
                df.loc[i, 'local_min'] = 1
            ### 3. 좌하우평
            elif prev < curr and next == curr:
                df.loc[i, 'local_max'] = 1
            ### 4. 좌평우하
            elif prev == curr and next < curr:
                df.loc[i, 'local_max'] = 1
            ### 5. V자
            elif prev > curr and next > curr:
                df.loc[i, 'local_min'] = 1
            ### 6. 역V자
            elif prev < curr and next < curr:
                df.loc[i, 'local_max'] = 1

        if df[df['local_max'] == 1].index[0] < df[df['local_min'] == 1].index[0]:
            if df.loc[0, label_target] < df.loc[df[df['local_max'] == 1].index[0], label_target]:
                df.loc[0, 'local_min'] = 1
        else:
            if df.loc[0, label_target] > df.loc[df[df['local_min'] == 1].index[0], label_target]:
                df.loc[0, 'local_max'] = 1
        if df[df['local_max'] == 1].index[-1] > df[df['local_min'] == 1].index[-1]:
            if df.loc[len(df) - 1, label_target] < df.loc[df[df['local_max'] == 1].index[-1], label_target]:
                df.loc[len(df) - 1, 'local_min'] = 1
        else:
            if df.loc[len(df) - 1, label_target] > df.loc[df[df['local_min'] == 1].index[-1], label_target]:
                df.loc[len(df) - 1, 'local_max'] = 1

        df = df.set_index('Date')
        return df



    def set_tb(df, label_target, RRPB, RFPT):
        '''local_min, local_max에 대해 RRPB, RFPT를 만족하는 top, bottom을 레이블링 한다.'''
        top_column = 'top'
        bottom_column = 'bottom'

        df = df.reset_index()

        # 모든 local_min, local_max를 리스트에 저장
        local_max = df[df['local_max'] == 1].index
        local_min = df[df['local_min'] == 1].index

        # bottom 후보
        cand_min = local_min[0]

        # flag = 반복문을 빠져나오기 위한 변수
        # 마지막 local_min, local_max 까지 레이블링을 하였을 경우 flag를 0으로 만들고 종료
        w_flag = 1
        # 레이블링 작업
        while (w_flag == 1):
            f_flag = 1
            if cand_min == local_min[-1]:
                break

            for cand_max in local_max[local_max > cand_min]:
                for next_cand_min in local_min[local_min > cand_max]:

                    if core.is_RRPB(df, cand_min, cand_max, label_target, RRPB) == 1:
                        if core.is_RFPT(df, next_cand_min, cand_max, label_target, RFPT) == 1:
                            df.loc[cand_min, bottom_column] = 1
                            df.loc[cand_max, top_column] = 1
                            cand_min = next_cand_min
                            f_flag = 0
                            break
                        elif next_cand_min == local_min[-1]:
                            df.loc[cand_min, bottom_column] = 1
                            df.loc[cand_max, top_column] = 1
                            w_flag = 0
                            f_flag = 0
                            break
                        elif df.loc[local_max[local_max > next_cand_min][0], label_target] >= df.loc[
                            cand_max, label_target]:
                            break
                        elif df.loc[next_cand_min, label_target] <= df.loc[cand_min, label_target]:
                            cand_min = next_cand_min
                            f_flag = 0
                            break
                    elif next_cand_min == local_min[-1]:
                        if df.loc[next_cand_min, label_target] < df.loc[cand_min, label_target]:
                            cand_min = next_cand_min
                        if local_max[-1] > local_min[-1]:
                            if core.is_RRPB(df, cand_min, local_max[-1], label_target, RRPB):
                                df.loc[cand_min, bottom_column] = 1
                                df.loc[local_max[-1], top_column] = 1
                        f_flag = 0
                        w_flag = 0
                        break
                    elif df.loc[next_cand_min, label_target] < df.loc[cand_min, label_target]:
                        cand_min = next_cand_min
                        f_flag = 0
                        break
                    elif next_cand_min < local_min[-1]:
                        if (df.loc[local_max[local_max > next_cand_min][0], label_target] >= df.loc[
                            cand_max, label_target]):
                            break
                # 마지막 local_max까지 왔는데 못찾았으면 RRPB조건 만족시 레이블링
                if cand_max == local_max[-1] and local_max[-1] > local_min[-1]:
                    if core.is_RRPB(df, cand_min, cand_max, label_target, RRPB) == 1:
                        df.loc[cand_min, bottom_column] = 1
                        df.loc[cand_max, top_column] = 1
                    w_flag = 0
                    break
                if f_flag == 0:
                    break

        if sum(df[top_column] == 1) == 0 or sum(df[bottom_column] == 1) == 0:
            df = df.set_index('Date')
            return df

        # bottom이 첫번째 일 때, bottom이전의 top 레이블링
        top_list = df[df[top_column] == 1].index
        bottom_list = df[df[bottom_column] == 1].index
        if bottom_list[0] > 0:
            temp = bottom_list[0]
            for point in df[:bottom_list[0]].index:
                if core.is_RFPT(df, bottom_list[0], point, label_target, RFPT) == 1 and df.loc[
                    point, label_target] > \
                        df.loc[
                            bottom_list[0], label_target]:
                    if df.loc[point, label_target] > df.loc[temp, label_target]:
                        temp = point
            if temp != bottom_list[0]:
                df.loc[temp, top_column] = 1
        # top이 마지막일때 마지막 bottom 레이블링
        if top_list[-1] > bottom_list[-1]:
            temp = top_list[-1]
            for point in df[top_list[-1]:].index:
                if core.is_RFPT(df, point, top_list[-1], label_target, RFPT) == 1 and df.loc[point, label_target] < \
                        df.loc[
                            top_list[-1], label_target]:
                    if df.loc[point, label_target] < df.loc[temp, label_target]:
                        temp = point
            if temp != top_list[-1]:
                df.loc[temp, bottom_column] = 1

        # top보다 높은 top X
        # bottom보다 낮은 bottom X
        for _ in range(2):
            top_list = df[df[top_column] == 1].index
            bottom_list = df[df[bottom_column] == 1].index
            for bottom in bottom_list:
                temp_bottom = bottom
                if bottom == bottom_list[-1] and bottom_list[-1] > top_list[-1]:
                    for point in df[top_list[top_list < bottom][-1]: bottom + 1].index:
                        if df.loc[point, label_target] <= df.loc[temp_bottom, label_target]:
                            df.loc[temp_bottom, bottom_column] = 0
                            df.loc[point, bottom_column] = 1
                            temp_bottom = point
                else:
                    for point in df[bottom + 1: top_list[top_list > bottom][0]].index:
                        if df.loc[point, label_target] <= df.loc[temp_bottom, label_target]:
                            df.loc[temp_bottom, bottom_column] = 0
                            df.loc[point, bottom_column] = 1
                            temp_bottom = point
            for top in top_list:
                temp_top = top
                if top == top_list[-1] and top_list[-1] > bottom_list[-1]:
                    for point in df[bottom_list[bottom_list < top][-1]:].index:
                        if df.loc[point, label_target] >= df.loc[temp_top, label_target]:
                            df.loc[temp_top, top_column] = 0
                            df.loc[point, top_column] = 1
                            temp_top = point
                else:
                    for point in df[top + 1: bottom_list[bottom_list > top][0]].index:
                        if df.loc[point, label_target] >= df.loc[temp_top, label_target]:
                            df.loc[temp_top, top_column] = 0
                            df.loc[point, top_column] = 1
                            temp_top = point
        # visual_charts(df, label_target)
        df = df.set_index('Date')
        return df

    # In[130]:


    def set_tbzone(df, label_target, TBR, BBR):
        '''모든 top, bottom에 대해 top_zone, bottom_zone을 레이블링 한다.'''
        df = df.reset_index()
        top_list = df[df['top'] == 1].index
        bottom_list = df[df['bottom'] == 1].index

        for top in top_list:
            top_target = df.loc[top, label_target]
            for prev in range(top, -1, -1):
                prev_target = df.loc[prev, label_target]
                if prev_target <= top_target and prev_target >= top_target * (1 - TBR):
                    df.loc[prev, 'top_zone'] = 1
                else:
                    break
            for next in range(top, len(df)):
                next_target = df.loc[next, label_target]
                if next_target <= top_target and next_target >= top_target * (1 - TBR):
                    df.loc[next, 'top_zone'] = 1
                else:
                    break

        for bottom in bottom_list:
            bottom_target = df.loc[bottom, label_target]
            for prev in range(bottom, -1, -1):
                prev_target = df.loc[prev, label_target]
                if prev_target >= bottom_target and prev_target <= bottom_target * (1 + BBR):
                    df.loc[prev, 'bottom_zone'] = 1
                else:
                    break
            for next in range(bottom, len(df)):
                next_target = df.loc[next, label_target]
                if next_target >= bottom_target and next_target <= bottom_target * (1 + BBR):
                    df.loc[next, 'bottom_zone'] = 1
                else:
                    break

        df = df.set_index('Date')
        return df
    # main
    try:
        if core.is_df(df) & core.is_column(df, target) & core.is_pos([RRPB, RFPT, TBR, BBR], zero=True):
            if isinstance(target, str):
                target = [target]
            # label_target 마다 레이블링 작업 실행
            for label_target in target:
                # column initialize
                df['top'] = 0
                df['bottom'] = 0
                df['top_zone'] = 0
                df['bottom_zone'] = 0
                df['local_max'] = 0
                df['local_min'] = 0
    
                # 레이블링 작업 실행
                # local_min, local_max 식별
                df = set_minmax(df, label_target)
                if sum(df['local_max'] == 1) != 0 and sum(df['local_min'] == 1) != 0:
                    # top, bottom 레이블링
                    df = set_tb(df, label_target, RRPB, RFPT)
                if sum(df['top'] == 1) != 0 and sum(df['bottom'] == 1) != 0:
                    # top_zone, bottom_zone 레이블링
                    df = set_tbzone(df, label_target, TBR, BBR)
                df[f'{label_target}_top'] = df['top']
                df[f'{label_target}_bottom'] = df['bottom']
                df[f'{label_target}_top_zone'] = df['top_zone']
                df[f'{label_target}_bottom_zone'] = df['bottom_zone']
                df.drop(['local_max', 'local_min', 'top', 'bottom', 'top_zone', 'bottom_zone'], axis='columns', inplace=True)
    
            return df
        else:
            return 0
    except Exception as error:
        print('<Error occurs>', error)
        return 0
