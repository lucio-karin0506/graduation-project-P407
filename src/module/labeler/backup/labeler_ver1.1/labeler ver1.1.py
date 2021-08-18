#!/usr/bin/env python
# coding: utf-8

# In[1]:


#  차트 설정
import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = (16, 5)
plt.rcParams['lines.linewidth'] = 3
plt.rcParams["axes.grid"] = True

from tqdm import tqdm
import json
import pandas as pd
import os


# In[2]:


def make_label(df, code, dtype, label_target_list, RRPB, RFPT):
    # 형 변환
    if type(label_target_list) != list:
        label_target_list = [label_target_list]
    # label_target 마다 레이블링 작업 실행
    for label_target in label_target_list:
        # column initialize       
        df[label_target + '_top'] = 0
        df[label_target + '_bottom'] = 0
        df[label_target + '_top_zone'] = 0
        df[label_target + '_bottom_zone'] = 0
        df['local_max'] = 0
        df['local_min'] = 0

        # 레이블링 작업 실행
        # local_min, local_max 식별
        df = set_minmax(df, label_target)
        if sum(df['local_max'] == 1) != 0 and sum(df['local_min'] == 1) != 0:
            # top, bottom 레이블링
            df = set_tb(df, label_target, RRPB, RFPT)
        if sum(df[label_target + '_top'] == 1) != 0 and sum(df[label_target + '_bottom'] == 1) != 0:
            # top_zone, bottom_zone 레이블링
            df = set_tbzone(df, label_target, RRPB, RFPT)

    # CSV파일 저장
    # 저장 폴더 여부 확인 후 생성 함수
    def createFolder(directory):
        try:
            if not (os.path.isdir(directory)):
                os.makedirs(os.path.join(directory))
        except OSError as e:
            if e.errno != errno.EEXIST:
                print("Failed to create directory!!!!!")
                raise
                # 저장  

    if (dtype == 'D'):
        createFolder(f"./label_data/label_daily/{code}_label_daily")
        df.to_csv(f'./label_data/label_daily/{code}_label_daily/{code}_{RRPB}_{RFPT}_{dtype}.csv')
    else:
        createFolder(f"./label_data/label_weekly/{code}_label_weekly")
        df.to_csv(f'./label_data/label_weekly/{code}_label_weekly/{code}_{RRPB}_{RFPT}_{dtype}.csv')

    return df


# In[3]:


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


# In[4]:


# local_min, local_max에 대해 RRPB, RFPT를 만족하는 top, bottom을 레이블링 한다.
def set_tb(df, label_target, RRPB, RFPT):
    top_column = label_target + '_top'
    bottom_column = label_target + '_bottom'

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
        # bottom 후보 뒤에 있는 모든 local_max에 대해서 top이 될 수 있는 top 후보 식별

        # local_min이 마지막인데, 마지막 local_min이 cand_min인 경우
        #         if cand_min == local_min[-1] and local_min[-1] > local_max[-1]:
        #             if is_RFPT(df, cand_min, cand_max, label_target, RFPT):
        #                 df.loc[cand_min, bottom_column] = 1
        #                 df.loc[cand_max, top_column] = 1
        #             break
        #         # local_max가 마지막인데, 마지막 local_min이 cand_min인 경우
        #         if cand_min == local_min[-1] and local_max[-1] > local_min[-1]:
        #             if is_RRPB(df, cand_min, local_max[-1], label_target, RRPB):
        #                 df.loc[cand_min, bottom_column] = 1
        #                 df.loc[local_max[-1], top_column] = 1
        #             break

        for cand_max in local_max[local_max > cand_min]:
            for next_cand_min in local_min[local_min > cand_max]:
                #                 print('next_cand_min : ', next_cand_min)
                #                 print('cand_max: ', cand_max)
                #                 print('cand_min: ', cand_min)
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


# In[5]:


# 모든 top, bottom에 대해 top_zone, bottom_zone을 레이블링 한다.
def set_tbzone(df, label_target, RRPB, RFPT):
    df = df.reset_index()
    tzone_column = label_target + '_top_zone'
    bzone_column = label_target + '_bottom_zone'

    top_list = df[df[label_target + '_top'] == 1].index
    bottom_list = df[df[label_target + '_bottom'] == 1].index

    # 첫번째 bottom 오른쪽 ~ 마지막 top 왼쪽
    if bottom_list[-1] > top_list[-1]:
        end_point = len(bottom_list) - 1
    else:
        end_point = len(bottom_list)

    for bottom in bottom_list[:end_point]:
        top = top_list[top_list > bottom][0]
        max_bottom_zone = bottom
        # bottom 오른쪽 bottom_zone
        for point in df[bottom:top + 1].index:
            if df.loc[point, label_target] <= min(
                    ((df.loc[top, label_target] + df.loc[bottom, label_target] * (1 - RRPB)) / 2),
                    df.loc[top, label_target] / (1 + RRPB)):
                if df.loc[point, label_target] >= df.loc[bottom, label_target]:
                    df.loc[point, bzone_column] = 1
                    if df.loc[max_bottom_zone, label_target] < df.loc[point, label_target]:
                        max_bottom_zone = point
        # top 왼쪽 top_zone
        for point in df[bottom:top + 1].index:
            if df.loc[point, label_target] >= df.loc[max_bottom_zone, label_target] * (1 + RRPB):
                if df.loc[point, label_target] <= df.loc[top, label_target]:
                    df.loc[point, tzone_column] = 1

    tzone_list = df[df[tzone_column] == 1].index
    bzone_list = df[df[bzone_column] == 1].index

    # 첫번째 바텀 왼쪽 bototm_zone 제외
    # 탑이 첫번째 일 경우 탑 오른쪽 top_zone 제외
    # 마지막 탑 오른쪽 top_zone 제외
    # bottom으로 끝날 경우 마지막 bottom 왼쪽 bottom_zone 제외
    # top오른쪽 ~ bottom 왼쪽

    # 첫번째가 top일 경우 두번째 top 부터 레이블링
    if top_list[0] < bottom_list[0]:
        start_point = 1
    else:
        start_point = 0

    for top in top_list[start_point:-1]:
        bottom = bottom_list[bottom_list > top][0]
        # top_zone
        # -> 이전 bottom_zone * (1 + RRPB) 이상
        tzone_prev = df.loc[bzone_list[bzone_list < top][-1], label_target] * (1 + RRPB)
        # bottom_zone
        # -> 이후 bottom_zone 이하
        bzone_after = df.loc[bzone_list[bzone_list < top_list[top_list > bottom][0]][-1], label_target]

        # bottom에 가장 가까운 top_zone
        min_top_zone = top

        # top오른쪽 top_zone
        for point in df[top: bottom + 1].index:
            if df.loc[point, label_target] >= tzone_prev and df.loc[point, label_target] <= df.loc[top, label_target]:
                if df.loc[point, label_target] >= max((df.loc[top, label_target] + df.loc[bottom, label_target]) / 2,
                                                      df.loc[bottom, label_target] / (1 - RFPT)):
                    df.loc[point, tzone_column] = 1
                    if df.loc[min_top_zone, label_target] > df.loc[point, label_target]:
                        min_top_zone = point

        # bottom왼쪽 bottom_zone
        for point in df[top: bottom + 1].index:
            if df.loc[point, label_target] <= bzone_after and df.loc[point, label_target] >= df.loc[
                bottom, label_target]:
                if df.loc[point, label_target] <= df.loc[min_top_zone, label_target] * (1 - RFPT):
                    df.loc[point, bzone_column] = 1

    tzone_list = df[df[tzone_column] == 1].index
    bzone_list = df[df[bzone_column] == 1].index

    # 첫번째 bottom 왼쪽 bottom_zone 레이블링
    for point in df[:bottom_list[0] + 1].index:
        if df.loc[point, label_target] <= df.loc[
            bzone_list[bzone_list < top_list[top_list > bottom_list[0]][0]][-1], label_target]:
            df.loc[point, bzone_column] = 1
    # 마지막 탑 오른쪽 top_zone 레이블링
    if top_list[-1] > bottom_list[-1]:
        for point in df[top_list[-1]:].index:
            if df.loc[point, label_target] >= (
                    df.loc[bzone_list[bzone_list < top_list[-1]][-1], label_target] * (1 + RRPB)):
                df.loc[point, tzone_column] = 1
    elif top_list[-1] < bottom_list[-1]:
        for point in df[top_list[-1]:bottom_list[-1]].index:
            if df.loc[point, label_target] >= (
                    df.loc[bzone_list[bzone_list < top_list[-1]][-1], label_target] * (1 + RRPB)):
                df.loc[point, tzone_column] = 1
    # bottom으로 끝날 경우 마지막 bottom 왼쪽 bototm_zone 레이블링
    if bottom_list[-1] > top_list[-1]:
        df.loc[bottom_list[-1], bzone_column] = 1
    # top이 첫번째 일 경우 top 오른쪽 top_zone 레이블링
    if top_list[0] < bottom_list[0]:
        df.loc[top_list[0], tzone_column] = 1
    df = df.set_index('Date')
    return df


# In[6]:


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


# In[7]:


# 차트 시각화
#           데이터프레임, 레이블링 대상, zone 시각화(true : zone시각화, false : top, bottom만 시각화)
def visual_charts(df, label_target, is_zone=False):
    plt.plot(df.index, df[label_target])
    if is_zone == True:
        plt.scatter(df[df[label_target + '_top_zone'] == 1].index,
                    df[df[label_target + '_top_zone'] == 1][label_target], c='r')
        plt.scatter(df[df[label_target + '_bottom_zone'] == 1].index,
                    df[df[label_target + '_bottom_zone'] == 1][label_target], c='g')
        plt.show()
    else:
        plt.scatter(df[df[label_target + '_top'] == 1].index, df[df[label_target + '_top'] == 1][label_target], c='r')
        plt.scatter(df[df[label_target + '_bottom'] == 1].index, df[df[label_target + '_bottom'] == 1][label_target],
                    c='g')
        plt.show()


# In[8]:


def label_init():
    # Labler ver 1.1
    # 주가정보 불러오는 외부 모듈
    import time
    import gathering

    start = time.time()

    gath = gathering.Gathering()

    # confihgg.json(파라미터가 입력되어있는 설정 파일 불러오기)
    with open('config.json', 'r') as f:
        config = json.load(f)

    # CSV파일로 레이블링
    # df = pd.read_csv("./test/csv/SPL10.csv", index_col='Date', encoding='CP949', parse_dates=['Date'])
    # config = config[0]
    # label_df = make_label(df,
    #                           config["name"],
    #                           config["dtype"],
    #                           config["label_target_list"],
    #                           config['RRPB'],
    #                           config['RFPT'],
    #                           config['TBR'],
    #                           config['BBR'])
    # visual_charts(label_df,'Close')

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
                              row['RFPT'])
        print("time :", time.time() - start)
        visual_charts(label_df, 'close')
        #visual_charts(label_df, 'close', True)
    return label_df


# In[9]:

if __name__ == '__main__':
    label_init()
