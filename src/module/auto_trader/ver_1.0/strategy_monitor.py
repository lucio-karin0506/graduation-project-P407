import os
import sys
import pandas as pd
import time
import re
import traceback
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from module.auto_trader.link_db import State_db
from module.auto_trader.check_condition import Item, Strategy
from module.auto_trader import util

# log 생성
logger = util.CreateLogger('strategy_monitor')


def stop_loss(item, upbit_exchange, state_db, slack_list):
    '''
    손절 처리 함수
    '''
    if upbit_exchange.get_total_buy_price(item.code) > 0:
        # if 0 > item.stop_profit >= upbit_exchange.gap_price_rate(item.code):
        #     logger.info(f"<익절 처리> coin={item.code}")
        if 0 < item.stop_loss <= upbit_exchange.gap_price_rate(item.code):
            logger.info(f"<손절 처리> coin={item.code}")
            # 슬랙 메시지
            for slack in slack_list:
                slack.push_message(
                    f"<손절 처리> coin={item.code}")                
            # 매수 대기 주문 취소
            wait_order_cancer(
                'buy', item, state_db, upbit_exchange, slack_list)                       
            # 시장가로 모두 매도
            ret = upbit_exchange.sell(market=item.code,
                                      volume_rate='all',
                                      ord_type='market')
            ret = ret.iloc[0]
            state_db.write_wait_order(item.code, ret['uuid'], 'stop_loss', 'sell')
            # uuid 추가                
            if 'stop_loss' in list(item.sell_uuids.keys()):
                item.sell_uuids['stop_loss'].append(ret['uuid'])
            else:
                item.sell_uuids['stop_loss'] = [ret['uuid']]
            # 매수 조건들 카운트 0으로 초기화
            for strategy_file_name in item.strategy_name:
                name = re.findall("(.*?)\.json", strategy_file_name)[0]
                for buy_name in list(item.buy_count.keys()):
                    if name in buy_name:
                        item.buy_count[buy_name] = 0
                        # 매수 조건들 카운트 DB 입력
                        state_db.write_order_count(item.code, 'buy', buy_name, 0)
            # 매수 인터버 조건 초기화                                
            item.last_buy_time={}
            # 손절 횟수 카운트
            if not 'stop_loss' in list(item.sell_count.keys()):
                item.sell_count['stop_loss'] = 1
            else:
                item.sell_count['stop_loss'] += 1
            # 손절 횟수 DB 입력
            now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
            now = datetime.strptime(now, '%Y-%m-%dT%H:%M:%S')
            state_db.write_order_count(item.code, 'sell', 'stop_loss', item.sell_count['stop_loss'], now)

def wait_order_cancer(order_type, item, state_db, upbit_exchange, slack_list):
    '''
    체결 대기 중인 주문 취소 함수
    '''
    if order_type == 'sell':
        uuids = item.sell_uuids
        count = item.sell_count
        time = item.last_sell_time
    elif order_type == 'buy':
        uuids = item.buy_uuids
        count = item.buy_count
        time = item.last_buy_time

    del_uuids = []
    for key, values in uuids.items():
        for uuid in values:
            cancer_ret = upbit_exchange.order_cancel(uuid)
            if not 'error_message' in list(cancer_ret.keys()):
                logger.info(
                    f"<주문 취소> type={order_type}, name={key}, uuid={uuid}")
                for slack in slack_list:
                    slack.push_message(
                        f"<주문 취소> type={order_type}, coin={item.code}, uuid={uuid}")
                # DB에서 제거
                state_db.delete_wait_order(uuid)
                del_uuids.append((key, uuid))
                # 주문 취소 시 매수/매도 조건 카운트 원래대로
                if count[key] > 0:
                    count[key] -= 1
                    
                # 마지막 매수 주문 체결 시간         
                last_order_time = upbit_exchange.get_last_order_time(side=order_type, state='done', item=item)
                # 인터버 조건 처리
                time = {last_order_time:True}  # 마지막 매수 및 매도 주문 체결 시간 저장
                # DB 저장
                state_db.write_order_count(item.code, order_type, key, count[key],  last_order_time)
               

    # 변수에서 제거
    for key, uuid in del_uuids:
        del uuids[key][uuids[key].index(uuid)]


def remove_done_order(order_type, item, state_db, upbit_exchange, slack_list):
    '''
    체결 완료 혹은 취소한 주문 처리 함수
    '''
    if order_type == 'sell':
        uuids = item.sell_uuids
    elif order_type == 'buy':
        uuids = item.buy_uuids
    # 체결 완료 혹은 실패한 거래 처리
    del_uuids = []
    for key, values in uuids.items():
        for uuid in values:
            state = upbit_exchange.get_order_state(uuid)
            if state == 'done':
                for slack in slack_list:
                    slack.push_message(
                        f"<주문 체결> type={order_type}, signal_name={key}, uuid={uuid}")
                state_db.check_order(uuid, state)
                del_uuids.append((key, uuid))
            elif state == 'cancel':
                for slack in slack_list:
                    slack.push_message(
                        f"<주문 취소> type={order_type}, signal_name={key}, uuid={uuid}")
                state_db.check_order(uuid, state)
                del_uuids.append((key, uuid))           
    # 변수에서 제거
    for key, uuid in del_uuids:
        del uuids[key][uuids[key].index(uuid)]


def strategy_monitor(upbit_quotation, upbit_exchange, slack_tocken_list, ord_type, buy_price, sell_price):
    # slack bot 생성

    slack_list = [util.Slack(token=slack_tocken['tocken'], channel=slack_tocken['channel'])
                  for slack_tocken in slack_tocken_list]

    # 자동거래 설정 파일(code와 strategy파일 이름을 매핑한 파일)
    try:
        tradecode = pd.read_json('tradecode.json')
        logger.info('<시스템> 자동 거래 파일 입력 완료')
    except Exception as e:
        logger.error(f'<ERROR> {e}')

    # code별 객체 생성
    item_list = [Item(tradecode['code'][i],
                      tradecode['interval'][i][-1],
                      tradecode['interval'][i][:-1],
                      tradecode['strategy'][i],
                      tradecode['buy_count'][i],
                      tradecode['sell_count'][i],
                      round(tradecode['betting_rate'][i], 4),
                      tradecode['betting_price'][i],
                      tradecode['buy_pyramiding'][i],
                      tradecode['sell_pyramiding'][i],
                      tradecode['stop_loss'][i]) for i in range(len(tradecode))]

    # 전략파일 이름과 전략, 지표 연결
    strategy_dict = {}
    for item in item_list:
        for name in item.strategy_name:
            if name not in strategy_dict.keys():
                try:
                    temp = pd.read_json(name)
                    logger.info('<시스템> 전략 파일 입력 완료')
                except Exception as e:
                    logger.error(f'<ERROR> {e}')
                strategy_dict[name] = Strategy(
                    name, temp['strategy'][0], temp['indicator'][0])

    state_db = State_db()
    state_db.link_order_count(item_list)
    state_db.link_wait_order(upbit_exchange, item_list)
    logger.info('<시스템> DB 연결 완료')

    # 조건 만족 확인 후 주문
    try:
        cnt = 1
        while(1):
            for item in item_list:
                # 가격 정보 저장
                item.set_df(upbit_quotation)
                # 지표 적용
                item.set_indi(strategy_dict)
                # 조건 만족 여부
                for strategy in item.strategy_name:
                    strategy_file_name = re.findall("(.*?)\.", strategy)[0]

                    logger.info(
                        f'<현재 작업> coin={item.code}, strategy={strategy}')
                    # 조건 만족 여부 확인 함수
                    item.check_condition(strategy, strategy_dict)
                    # 매수 신호 발생
                    if len(item.buy_order_volume) != 0:
                        # {시그널이름: 매수량}
                        for signal_name, volume_rate in list(item.buy_order_volume.items()):
                            logger.info(
                                f"<매수 조건 만족> market={item.code}, signal_name={signal_name}")

                            # 매수 신호 발생시 미체결 매도 주문 취소
                            wait_order_cancer(
                                'sell', item, state_db, upbit_exchange, slack_list)

                            # interval기간에 한번만 매수
                            interval_ret = item.interval_order(ord_type='buy')

                            # interver 조건 만족
                            if interval_ret == 1:
                                # 매수 요청
                                ret = upbit_exchange.buy(market=item.code,
                                                         volume_rate=volume_rate,
                                                         betting_rate=item.betting_rate,
                                                         betting_price=item.betting_price,
                                                         ord_type=ord_type,
                                                         ord_price=buy_price)
                                # 정상적 매수 요청
                                if not isinstance(ret, int):
                                    ret = ret.iloc[0]

                                    # 매수 요청 오류
                                    if 'error.message' in list(ret.keys()):
                                        # 매수 횟수 원래대로
                                        if item.buy_count[signal_name] > 0:
                                            item.buy_count[signal_name] -= 1
                                        # 마지막 매수 시간 원래대로
                                        item.last_buy_time = {}
                                        logger.warning(
                                            f"<매수 요청 실패> {ret['error.message']}")
                                    # 정상적 매수 요청
                                    else:
                                        logger.info(
                                            f"<매수 요청 완료> market={ret['market']}, price={ret['price']}, volume={ret['volume']}, ord_type={ret['ord_type']}, buy_price={buy_price}")
                                        for slack in slack_list:
                                            slack.push_message(
                                                f"<매수 요청 완료> market={ret['market']}, price={ret['price']}, volume={ret['volume']}, ord_type={ret['ord_type']}, buy_price={buy_price}")

                                        # sell_count 초기화
                                        # 매수 신호 발생시 매도 조건 진입 횟수 초기화
                                        for sell_name in list(item.sell_count.keys()):
                                            if strategy_file_name in sell_name:
                                                item.sell_count[sell_name] = 0
                                                state_db.write_order_count(item.code,
                                                                   'sell',
                                                                   sell_name,
                                                                   item.sell_count[sell_name])

                                        # last_sell_time 초기화
                                        item.last_sell_time = {}
                                        # uuid 추가
                                        if signal_name in list(item.buy_uuids.keys()):
                                            item.buy_uuids[signal_name].append(
                                                ret['uuid'])
                                        else:
                                            item.buy_uuids[signal_name] = [
                                                ret['uuid']]

                                        # 주문 DB에 입력
                                        state_db.write_wait_order(
                                            code=item.code, uuid=ret['uuid'], signal_name=signal_name, order_type='buy')
                                        # buy_count DB에 입력
                                        state_db.write_order_count(item.code,
                                                                   'buy',
                                                                   signal_name,
                                                                   item.buy_count[signal_name],
                                                                   list(item.last_buy_time.keys())[0])
                                        
                                # 잔고 없음 오류
                                else:
                                    # 매수 횟수 원래대로
                                    if item.buy_count[signal_name] > 0:
                                        item.buy_count[signal_name] -= 1
                                    # 마지막 매수 시간 원래대로
                                    item.last_buy_time = {}
                            else:
                                logger.info("<매수 요청 실패> interval term 조건 오류")
                                if item.buy_count[signal_name] > 0:
                                    item.buy_count[signal_name] -= 1
                                    # 마지막 매수 시간 원래대로
                                    item.last_buy_time = {}

                    # 매도 신호 발생
                    if len(item.sell_order_volume) != 0:
                        # {시그널이름: 매도량}
                        for signal_name, volume_rate in list(item.sell_order_volume.items()):
                            logger.info(
                                f"<매도 조건 만족> market={item.code}, signal_name={signal_name}")

                            # 매도 신호 발생 시 미체결 매수 주문 취소
                            wait_order_cancer(
                                'buy', item, state_db, upbit_exchange, slack_list)

                            interval_ret = item.interval_order(ord_type='sell')
                            # 인터버 조건 만족
                            if interval_ret == 1:
                                # 매도 요청
                                ret = upbit_exchange.sell(market=item.code,
                                                          volume_rate=volume_rate,
                                                          ord_type=ord_type,
                                                          ord_price=sell_price)
                                # 코인 보유량 존재
                                if not isinstance(ret, int):
                                    # return 데이터프레임에 첫번째 컬럼 이름 추출
                                    ret = ret.iloc[0]
                                    # 매도 요청 오류
                                    if 'error.message' in list(ret.keys()):
                                        # 매도 카운트 원래대로
                                        if item.sell_count[signal_name] > 0:
                                            item.sell_count[signal_name] -= 1
                                        # 마지막 매수 시간 원래대로 (이미 interval 조건을 만족했으므로 초기화)
                                        item.last_sell_time = {}

                                        logger.warning(
                                            f"<매도 요청 실패> {ret['error.message']}")
                                    # 정상적 매도 요청
                                    else:
                                        logger.info(
                                            f"<매도 요청 완료> market={ret['market']}, price={ret['price']}, volume={ret['volume']}, ord_type={ret['ord_type']}, sell_price={sell_price}")
                                        for slack in slack_list:
                                            slack.push_message(
                                                f"<매도 요청 완료> market={ret['market']}, price={ret['price']}, volume={ret['volume']}, ord_type={ret['ord_type']}, sell_price={sell_price}")

                                        # buy_count 초기화
                                        # 매도 주문 요청시 매수 조건 진입 횟수 초기화
                                        for buy_name in list(item.buy_count.keys()):
                                            if strategy_file_name in buy_name:
                                                item.buy_count[buy_name] = 0
                                                state_db.write_order_count(item.code,
                                                                   'buy',
                                                                   buy_name,
                                                                   item.buy_count[buy_name])

                                        # last_buy_time 초기화
                                        item.last_buy_time = {}

                                        # uuid 추가
                                        if signal_name in list(item.sell_uuids.keys()):
                                            item.sell_uuids[signal_name].append(
                                                ret['uuid'])
                                        else:
                                            item.sell_uuids[signal_name] = [
                                                ret['uuid']]

                                        # 미체결된 주문 DB에 입력
                                        state_db.write_wait_order(
                                            code=item.code, uuid=ret['uuid'], signal_name=signal_name, order_type='sell')

                                        # sell_count, last_order_time DB에 입력
                                        state_db.write_order_count(item.code,
                                                                   'sell',
                                                                   signal_name,
                                                                   item.sell_count[signal_name],
                                                                   list(item.last_sell_time.keys())[0])

                                        logger.info(
                                            f'<DB 입력> TABLE=order_count, market={item.code}, ord_type=sell, signal_name={signal_name}, count={item.sell_count[signal_name]}')
                                # 잔고 없음 오류
                                else:
                                    # 매도 카운트 원래대로
                                    if item.sell_count[signal_name] > 0:
                                        item.sell_count[signal_name] -= 1
                                    # 마지막 매수 시간 원래대로
                                    item.last_sell_time = {}
                            else:
                                logger.info("<매도 요청 실패> interval term 조건 오류")
                                # 매도 카운트 원래대로
                                if item.sell_count[signal_name] > 0:
                                    item.sell_count[signal_name] -= 1
                                # 마지막 매수 시간 원래대로
                                item.last_sell_time = {}
                    # 신호 미발생
                    else:
                        #logger.info(f"{item.code} 매매 신호 미발생")
                        pass
                    # 거래 수량 초기화
                    item.buy_order_volume = {}
                    item.sell_order_volume = {}

            # 손절 처리
            for item in item_list:
                stop_loss(item, upbit_exchange, state_db, slack_list)

            # 체결 완료 혹은 실패한 주문 처리
            for item in item_list:
                remove_done_order('buy', item, state_db,
                                  upbit_exchange, slack_list)
                remove_done_order('sell', item, state_db,
                                  upbit_exchange, slack_list)

            # 1초에 10번 조회 요청 수 제한
            logger.info(f'<시스템> {cnt}회 종료')
            time.sleep(30)
            cnt = cnt + 1
    except Exception as e:
        state_db.con.close()
        print(traceback.format_exc())
        logger.error(f'<ERROR> {e}')
    finally:
        state_db.con.close()
        for slack in slack_list:
            slack.push_message("auto_trader.py 종료")
        logger.info('<시스템> DB 연결 종료')
        logger.info('<시스템> 시스템 종료')