#!/usr/bin/env python
# coding: utf-8

# In[49]:


#  차트 설정
import matplotlib.pyplot as plt
import json
import pandas as pd


# In[161]:


def make_label(df, code, dtype, label_target_list, RRPB, RFPT, TBR, BBR):
    # 형 변환
    if type(label_target_list) != list:
        label_target_list = [label_target_list]
    result_df = pd.DataFrame()
    # label_target 마다 레이블링 작업 실행
    for label_target in label_target_list:
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

        df.drop(['local_max', 'local_min'], axis='columns', inplace=True)
        df['label_target'] = label_target
        result_df = pd.concat([result_df, df], axis=0)

    result_df['code'] = code
    result_df['dType'] = dtype
    result_df['RRPB'] = RRPB
    result_df['RFPT'] = RFPT
    result_df['TBR'] = TBR
    result_df['BBR'] = BBR

    return result_df


# In[52]:


# 데이터프레임의 모든 열에 대해서 local_min, local_max를 식별한다.
def set_minmax(df, label_target):
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


# In[53]:


# local_min, local_max에 대해 RRPB, RFPT를 만족하는 top, bottom을 레이블링 한다.
def set_tb(df, label_target, RRPB, RFPT):
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

                if is_RRPB(df, cand_min, cand_max, label_target, RRPB) == 1:
                    if is_RFPT(df, next_cand_min, cand_max, label_target, RFPT) == 1:
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
                        if is_RRPB(df, cand_min, local_max[-1], label_target, RRPB):
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
                if is_RRPB(df, cand_min, cand_max, label_target, RRPB) == 1:
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
            if is_RFPT(df, bottom_list[0], point, label_target, RFPT) == 1 and df.loc[point, label_target] > df.loc[
                bottom_list[0], label_target]:
                if df.loc[point, label_target] > df.loc[temp, label_target]:
                    temp = point
        if temp != bottom_list[0]:
            df.loc[temp, top_column] = 1
    # top이 마지막일때 마지막 bottom 레이블링        
    if top_list[-1] > bottom_list[-1]:
        temp = top_list[-1]
        for point in df[top_list[-1]:].index:
            if is_RFPT(df, point, top_list[-1], label_target, RFPT) == 1 and df.loc[point, label_target] < df.loc[
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


# 모든 top, bottom에 대해 top_zone, bottom_zone을 레이블링 한다.
def set_tbzone(df, label_target, TBR, BBR):
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


# In[55]:


# RRPB조건 만족 판별
def is_RRPB(df, local_min, local_max, label_target, RRPB):
    if RRPB <= (df.loc[local_max, label_target] / df.loc[local_min, label_target]) - 1:
        return 1
    else:
        return 0


# RFPT조건 만족 판별
def is_RFPT(df, local_min, local_max, label_target, RFPT):
    if RFPT <= 1 - (df.loc[local_min, label_target] / df.loc[local_max, label_target]):
        return 1
    else:
        return 0


# In[110]:


# 차트 시각화
#           데이터프레임, 레이블링 대상, zone 시각화(true : zone시각화, false : top, bottom만 시각화)
def visual_charts(df, label_target, is_zone=False):
    df = df[df['label_target'] == label_target]
    plt.plot(df.index, df[label_target])
    if is_zone == True:
        plt.scatter(df[df['top_zone'] == 1].index, df[df['top_zone'] == 1][label_target], c='r')
        plt.scatter(df[df['bottom_zone'] == 1].index, df[df['bottom_zone'] == 1][label_target], c='g')
        plt.show()
    else:
        plt.scatter(df[df['top'] == 1].index, df[df['top'] == 1][label_target], c='r')
        plt.scatter(df[df['bottom'] == 1].index, df[df['bottom'] == 1][label_target], c='g')
        plt.show()


# In[162]:


def label_init():
    # Labler ver 1.1
    # 주가정보 불러오는 외부 모듈
    import time
    import os, sys

    start = time.time()
    from OrderCreator import gathering
    gath = gathering.Gathering()

    # confihgg.json(파라미터가 입력되어있는 설정 파일 불러오기)
    with open('config.json', 'r') as f:
        config = json.load(f)

    # 설정파일 주가차트로 레이블링
    for row in config:
        # 외부모듈 gathering을 이용해 주가코드 데이터프레임 불러오기
        df = gath.get_stock(row['code'], row['start_date'], row['end_date'], row['dtype'])

        # 레이블링 작업
        label_df = make_label(df,
                              row["code"],
                              row["dtype"],
                              row['label_target_list'],
                              row['RRPB'],
                              row['RFPT'],
                              row['TBR'],
                              row['BBR'])
        print("time :", time.time() - start)

    return label_df

# if __name__ == '__main__':
#     plt.rcParams["figure.figsize"] = (16, 5)
#     plt.rcParams['lines.linewidth'] = 3
#     plt.rcParams["axes.grid"] = True
#     label_df = label_init()
#     visual_charts(label_df, 'close')
#     visual_charts(label_df, 'close', True)
