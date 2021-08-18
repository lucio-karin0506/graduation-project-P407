#!/usr/bin/env python
# coding: utf-8

# In[1]:


#  차트 설정
import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = (16,5)
plt.rcParams['lines.linewidth'] = 3
plt.rcParams["axes.grid"] = True


# In[2]:


import FinanceDataReader as fdr

# In[3]:


from scipy.signal import argrelextrema
from tqdm import tqdm
import numpy as np
import json
import pandas as pd


# - ### RRPB: Ratio of Rising to Previous Bottom
# - ### RFPT: Ratio of Fall to Previous Top
# - ### TBR: Top Band Ratio
# - ### BBR: Bottom Band Ratio

# In[4]:


# 레이블링 작업 실행 함수
'''
1. config.json(설정 파일)을 불러옴
2. label_target에 따른 top, bottom, top_zone, bottom_zone columns를 생성
3. 모든 label_target에 레이블링 작업 함수인 set_point()를 호출하여 레이블링된 데이터프레임 받음
4. 레이블링 작업이 완료된 Dataframe을 리턴하고, CSV파일을 저장
'''

#   make_label(주가코드, 시작날짜, 종료날짜, 레이블링 대상 리스트, RRPB, RFPT, TBR, BBR)
def make_label(df, label_target_list, RRPB, RFPT, TBR, BBR):
    
    # 형 변환
    if(type(label_target_list) != list):
        label_target_list = [label_target_list]
    
    # (주가 코드, 시작날짜, 종료날짜)차트 Dataframe 형식 으로 불러오기
    #df = df[['open', 'high', 'low', 'Close']]
    
    # local_minmax column 추가
    # df['local_max'] = 0
    # df['local_min'] = 0
    
    # Flag columns 생성
    #                매도 지점, 매수지점,   매도 구역,  매수 구역
    columnname_list = ['_top', '_bottom', '_top_zone', '_bottom_zone']    
    for label_target in label_target_list:
        # <ERROR> 데이터 프레임에 없는 label_target(레이블링 대상) 입력
        assert label_target in df.columns, f"<ERROR> {label_target} not in columns!"
        # Flag column 초기화
        for name in columnname_list:
            df[label_target + name] = 0
    
    
    # label_target에 들어있는 모든 레이블링 대상을 레이블링
    for label_target in label_target_list:
        df = set_point(df, RRPB, RFPT, TBR, BBR, label_target)
    
    # CSV파일 저장
    #df.to_csv("./SPL.csv")
    
    # Dataframe return
    return df




# In[63]:


#label_target을 기준으로 데이터프레임의 모든 row에 대해 top, bottom, top_zone, bottom_zone을 레이블링 함
'''
1. label_target을 기준으로 모든 row에 대해 상대 극한에 해당하는 index를 구한다.
2. local_minmax가 없을 경우
3. local_max가 첫번째 local_minmax인 경우 차트의 첫번째 인덱스를 local_min으로 선정
3-1. local_min이 첫번째 local_minmax인 경우 차트의 첫번째 인덱스를 top으로 선정
4. set_RRPB() -> RRPB조건을 기준으로 top, bottom 레이블링,
   set_RFPT() -> RFPT조건을 기준으로 top, bottom 레이블링, 
   set_tb_zone() -> TBR, BBR을 기준으로 top_zone, bottom_zone 레이블링
5. 레이블링 작업한 데이터프레임 리턴
'''
#   set_point(데이터프레임, RRPB, RFPT, TBR, BBR, 레이블링 대상)
def set_point(df, RRPB, RFPT, TBR, BBR, label_target):  
    
    # 모든 row에 대해서 상대 극한에 해당하는 index 리턴
    local_max = argrelextrema(df[label_target].values, np.greater)[0]
    local_min = argrelextrema(df[label_target].values, np.less)[0]
    

    df.reset_index(inplace=True)
    df.loc[local_max,'local_max'] = 1
    df.loc[local_min,'local_min'] = 1
    df.set_index('Date', inplace=True)
    
    
    # local_minmax가 없을 경우
    if(len(local_max) == 0 or len(local_min) == 0):
        # local_max만 없을 경우
        if(len(local_max) == 0 and len(local_min) > 0):
            df.loc[df.index[0], label_target + '_top'] = 1
            local_max = np.append(local_max, len(df) -1)
        # local_min만 없을 경우
        elif(len(local_max) > 0 and len(local_min) == 0):
            local_min = np.insert(local_min, 0, 0)
            df.loc[df.index[-1], label_target + '_bottom'] = 1
        # local_min, local_max가 없을 경우
        elif(len(local_max) == 0 and len(local_min) == 0):
            if(df.loc[df.index[0], label_target] <= df.loc[df.index[-1], label_target]):
                if(df.loc[df.index[-1], label_target] >= df.loc[df.index[0], label_target] * (1 + RRPB)):
                    df.loc[df.index[0], label_target + '_bottom'] = 1
                    df.loc[df.index[-1], label_target + '_top'] = 1
            else:
                if (df.loc[df.index[-1], label_target] <= df.loc[df.index[0], label_target] * (1 - RFPT)):
                    df.loc[df.index[0], label_target + '_top'] = 1
                    df.loc[df.index[-1], label_target + '_bottom'] = 1
            df = set_tb_zone(df, TBR, BBR, label_target)
            return df
            
    else:
        # 첫번째 저고점과 비교 대상 선정
        # 1. 첫번째 저고점이 고점일 경우
        #   - 차트의 첫번째 인덱스를 저점으로 선정 후 비교
        # 2. 첫번째 저고점이 저점일 경우
        #   - 차트의 첫번째 인덱스를 top으로 선정
        #   - 이후 top과 bottom을 비교하는 RFPT 조건 만족하면 유지, 불만족하면 제거(top만 제거, bottom은 유지)
        if(local_max[0] < local_min[0]):
            local_min = np.insert(local_min, 0, 0)
        else:
            df.loc[df.index[0], label_target + '_top'] = 1

        # 차트의 마지막 지점과 비교하기 위해 마지막 지점 종류 선정
        if(local_max[-1] < local_min[-1]):
            local_max = np.append(local_max, len(df)-1)
        else:
            df.loc[df.index[-1], label_target + '_bottom'] = 1

      
    # set top 
    df = set_RRPB(df, local_max, local_min, RRPB, label_target)

    # top, bottom이 없을 경우
    if sum(df[label_target+'_top']) == 0 and sum(df[label_target + '_bottom']) == 0:
        print("top, bottom이 없습니다.")
        return df
    
    # set bottom
    df = set_RFPT(df, RFPT, label_target)
    
    # top, bottom이 없을 경우
    if sum(df[label_target+'_top']) == 0 and sum(df[label_target + '_bottom']) == 0:
        print("top, bottom이 없습니다.")
        return df
    # set top_zone, bottom_zone
    df = set_tb_zone(df, TBR, BBR, label_target)

    return df


# In[6]:


# 차트의 모든 local_max(고점), local_min(저점)에서 RRPB 조건에 맞는 local_max, local_min을 데이터 프레임의 top, bottom 컬럼에 set함
'''
1. label_target에 따른 레이블링 작업을 set할 column 설정
2. (직전 고점 < 저점들 < 현재 고점)인 저점들과 현재 고점을 비교
3. 고점 >= 저점 * (1 + RRPB)에 해당되는 고점과 저점을 top, bottom 컬럼에 레이블링
4. 데이터프레임 리턴
'''
def set_RRPB(df, local_max, local_min, RRPB, label_target):
    i,j = 0, 0 # i = 저점 포인트, j = 고점 포인트
    df.reset_index(inplace=True)
    
    # column name 설정
    top_column, bottom_column = label_target + '_top', label_target + '_bottom'
    
    # local_min[0] < local_max[0]
    while(True):
        # (고점 >= 전 저점 * (1 + RRPB)) 에 해당되는 local_max, local_min 을 top, bottom 컬럼에 레이블링
        if(df.loc[local_max[j], label_target] >= df.loc[local_min[i], label_target] * (1 + RRPB)):
            df.loc[local_max[j], top_column] = 1
            df.loc[local_min[i], bottom_column] = 1

        if((i+1 >= len(local_min)) or (j+1 >= len(local_max))): ### 차트의 마지막 까지 찾았으면 종료
            break
        elif(local_min[i+1] > local_max[j+1]): ### 저점의 다음 인덱스가 고점의 다음 인덱스보다 클때 -> 저점 인덱스 유지
            j += 1
        elif(local_min[i+1] < local_max[j]): ### 저점의 다음 인덱스가 고점의 현재 인덱스보다 작을 때 -> 고점 인덱스 유지
            i += 1
        else:
            i += 1
            j += 1

    df.set_index('Date', inplace=True)
    return df


# In[7]:


# set_RRPB에서 구한 top, bottom 중에서 RFPT 조건에 맞지 않는 top, bottom을 데이터 프레임의 top, bottom 컬럼에서 제거함
'''
1. label_target에 따른 레이블링 작업을 set할 column 설정
2. set_RRPB에서 구한 top, bottom을 가져옴
3. local_min이 local_minmax의 시작이었던 경우 첫번째 인덱스를 top으로 선정하였을 때 처리
3-1. 첫번째 bottom과 비교하여 RFPT조건을 만족하면 top유지, 불만족하면 top 제거
4. local_max가 local_minmax의 끝이었던 경우 마지막 인덱스를 bottom으로 선정하였을 때 처리
4-1. 마지막 top과 비교하여 RFPT조건을 만족하면 bottom유지, 불만족하면 bottom 제거
5. (직전 bottom < top < 현재 bottom)인 top 과 현재 bottom을 비교
6. (top - bottom >= top * RFPT) 을 만족하지 못하는 top과 bottom을 top,bottom column에서 제거
7. 데이터프레임 리턴
'''
def set_RFPT(df, RFPT, label_target):
    df.reset_index(inplace=True)
    
    top_column, bottom_column = label_target + '_top', label_target + '_bottom'
    
    # top과 bottom을 가져옴
    top_index = df[df[top_column] == 1].index
    bottom_index = df[df[bottom_column] == 1].index

    # 차트의 첫번째 지점 비교
    # 인덱스 0 이 top 일 경우
    # RFPT 조건에 맞지 않으면 인덱스 0 top 제거
    if(top_index[0] < bottom_index[0]):
        if(df.loc[bottom_index[0], label_target] > df.loc[top_index[0], label_target] * (1 - RFPT)):
            df.loc[top_index[0], top_column] = 0

    # 차트의 마지막 지점 비교
    # 만약 bottom마지막이 top마지막보다 마지막일 경우
    # 마지막 bottom의 RFPT조건이 안맞으면 bottom만 제거
    if(top_index[-1] < bottom_index[-1]):
        # 차트의 마지막이 bottom 인 경우
        bottom_len = len(bottom_index) -1
        if(df.loc[bottom_index[-1], label_target] > df.loc[top_index[-1], label_target] * (1 - RFPT)):
            df.loc[bottom_index[-1], bottom_column] = 0
    else:
        bottom_len = len(bottom_index)
    
    
    # 레이블링 작업 할 bottom 설정
    # i: bottom, k: top
    for i in range(1, bottom_len):
        # 현재 bottom 전의 top
        for k in range(len(top_index)):
            if(top_index[k] > bottom_index[i-1]) and (top_index[k] < bottom_index[i]):
            # top - bottom < top * RFPT
                if (df.loc[bottom_index[i], label_target] > df.loc[top_index[k], label_target] * (1 - RFPT)):
                    df.loc[top_index[k], top_column] = 0
                    df.loc[bottom_index[i], bottom_column] = 0
    
    df.set_index('Date', inplace=True)
    return df


# In[8]:


# 설정된 top과 bottom을 기준으로 top_zone, bottom_zone을 구한다.
'''
1. top과 bottom에 해당하는 인덱스를 가져온다
2. get_tb_zone 함수를 호출하여 top_zone, bottom_zone을 레이블링한다.
3. 데이터프레임 리턴
'''
def set_tb_zone(df, TBR, BBR, label_target):
    df.reset_index(inplace=True)
    top_index = df[df[label_target + '_top'] == 1].index
    bottom_index = df[df[label_target + '_bottom'] == 1].index
    df.set_index('Date', inplace=True)
    
    # 매도 지점과 매수 지점과 차이가 TBR ,BBR 내에 있는 지점들 식별
    df = get_tb_zone(df, top_index, TBR, BBR, label_target, 1)
    df = get_tb_zone(df, bottom_index, TBR, BBR, label_target, -1)

    return df


# In[9]:


# top_zone, bottom_zone에 해당하는 row을 레이블링 한다.
'''
1. tb_flag: 1 -> top_zone 레이블링
   tb_flag: 2 -> bottom_zone 레이블링
2. point >=top * (1 - TBR) 인 point을 top_zone으로 레이블링
    - point는 top과 시간적인 개념으로 연속적이 어야 한다.
    - top_zone과 top 사이에는 top_zone이 아닌 지점이 존재 할 수 없다.
3. point <= bottom * (1 + BBR) 인 point을 bottom_zone으로 레이블링
    - point는 bottom과 시간적인 개념으로 연속적이 어야 한다.
    - bottom_zone과 bottom 사이에는 bottom_zone이 아닌 지점이 존재 할 수 없다.
4. 데이터프레임 리턴
'''
def get_tb_zone(df, tb_list, TBR, BBR, label_target, tb_flag):
    df.reset_index(inplace=True)
    for curr in tb_list:
        # top_zone이면
        if(tb_flag == 1):
            # 연속된 이전 지점들과 비교
            for prev in range(curr, -1, -1):
                # TBR 조건에 맞으면 해당 지점 레이블링
                if(df.loc[prev, label_target] >= df.loc[curr, label_target] * (1 - TBR))  and (df.loc[prev,label_target] <= df.loc[curr, label_target]):
                    df.loc[prev, label_target + '_top_zone'] = 1
                else:
                    break
            # 연속된 이후 지점들과 비교
            for after in range(curr+1, len(df)):
                if(df.loc[after, label_target] >= df.loc[curr, label_target] * (1 - TBR))  and (df.loc[after,label_target] <= df.loc[curr, label_target]):
                    df.loc[after, label_target + '_top_zone'] = 1
                else:
                    break
        elif(tb_flag == -1):
            for prev in range(curr, -1, -1):
                if(df.loc[prev, label_target] <= df.loc[curr, label_target] *(1 + BBR)) and (df.loc[prev,label_target] >= df.loc[curr, label_target]):
                    df.loc[prev, label_target + '_bottom_zone'] = 1
                else:
                    break
            for after in range(curr+1, len(df)):
                if(df.loc[after, label_target] <= df.loc[curr, label_target] * (1 + BBR))  and (df.loc[after,label_target] >= df.loc[curr, label_target]):
                    df.loc[after, label_target + '_bottom_zone'] = 1
                else:
                    break
    df.set_index('Date', inplace=True)
    return df


# In[13]:


# 차트 시각화
def visual_charts(df):
    df['Close'].plot()
    plt.scatter(df[df['Close_top'] == 1].index, df[df['Close_top'] == 1]['Close'], c ='r')
    plt.scatter(df[df['Close_bottom'] == 1].index, df[df['Close_bottom'] == 1]['Close'], c ='g')
    #plt.scatter(df[df[label_target + '_top_zone'] == 1].index, df[df[label_target + '_top_zone'] == 1]['Close'], c ='r')
    #plt.scatter(df[df[label_target + '_bottom_zone'] == 1].index, df[df[label_target + '_bottom_zone'] == 1]['Close'], c ='g')
    plt.show()


# In[14]:


def visual_charts_zone(df):
    df['Close'].plot()
    plt.scatter(df[df['Close_top_zone'] == 1].index, df[df['Close_top_zone'] == 1]['Close'], c ='r')
    plt.scatter(df[df['Close_bottom_zone'] == 1].index, df[df['Close_bottom_zone'] == 1]['Close'], c ='g')
    plt.show()


# In[99]:


# config.json(파라미터가 입력되어있는 설정 파일 불러오기)
# with open('config.json', 'r') as f:
#     config = json.load(f)
#
# df = pd.read_csv("./test/csv/SPL7.csv", index_col='Date', encoding='CP949')
# df.index = pd.to_datetime(df.index, format='%Y-%m-%d', errors='raise')
# label_df = make_label(df,
#                       config['label_target_list'],
#                       config['RRPB'],
#                       config['RFPT'],
#                       config['TBA'],
#                       config['BBR'])
# visual_charts_zone(label_df)

