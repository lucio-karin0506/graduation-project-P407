from module.auto_trader.check_signal import Item, Strategy
from module.auto_trader import util, link_db
import os
import sys
import re
import pandas as pd
import traceback
import time
sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))

logger = util.CreateLogger('main')


def init_item(buy_price_type: str, sell_price_type: str, trader, state_db, config_file: str, strategy_folder: str = '.', slack_list: list = None):
    """
    설정파일과 전략파일을 통하여 item객체와 strategy객체 생성

    Parameters
    ----------
    buy_price_type : str
        매수 금액 종류
        1: 매도1호가
        0: 현재가
        -1: 매수1호가.
    sell_price_type : str
        매도 금액 종류
        1: 매도1호가
        0: 현재가
        -1: 매수1호가..
    trader : TYPE
        Trader 객체.
    state_db : TYPE
        State_db 객체.
    config_file : str
        설정파일 이름.
    strategy_folder : str, optional
        전략 폴더 경로. The default is '.'.
    slack_list : list, optional
        Slack 객체 리스트. The default is None.

    Returns
    -------
    item_list : TYPE
        Item 객체 리스트.
    strategy_dict : TYPE
        전략 파일 이름과 Strategy객체가 매핑된 dictionary.

    """
    ################################################################
    ######################### 파일 입력 #############################
    try:
        # file = pathlib.Path("C:/Users/Administrator/Desktop/p407-github/P407/src/module/auto_trader/"+config_file)
        # text = file.read_text(encoding='utf-8-sig')

        # js = json.loads(text)
        tradecode_file = pd.read_json(config_file, encoding='utf-8-sig')
        logger.info('<시스템> 자동 거래 파일 입력 완료')
    except Exception as e:
        logger.error(f'<ERROR> {e}')
    # 코드별 객체 리스트 생성
    item_list = [Item(currency_pair=data['coin'],
                      interval=data['interval'],
                      buying_portion=data['buying_portion'],
                      buying_money=data['buying_money'],
                      max_buy_count=data['max_buy_count'],
                      max_sell_count=data['max_sell_count'],
                      buy_pyramiding_rate=data['buy_pyramiding_rate'],
                      sell_pyramiding_rate=data['sell_pyramiding_rate'],
                      strategy_name=[re.findall(
                          '(.*?).json', strategy_file_name)[0] for strategy_file_name in data['strategy']],
                      trader=trader,
                      state_db=state_db,
                      buy_price_type=buy_price_type,
                      sell_price_type=sell_price_type,
                      slack_list=slack_list) for index, data in tradecode_file.iterrows()]

    # 전략별 객체 딕셔너리 생성
    # key: 전략 이름
    # value: 전략, 지표, 조건이 포함되어 있는 객체
    strategy_dict = {}
    for item in item_list:
        for strategy_name in item.strategy_name:
            if strategy_name not in list(strategy_dict.keys()):
                try:
                    # file = pathlib.Path("C:/Users/Administrator/Desktop/p407-github/P407/src/module/auto_trader/"+strategy_name+'.json')
                    # text = file.read_text(encoding='utf-8-sig')
                    # js = json.loads(text)
                    strategy_file = pd.read_json(
                        f'{strategy_folder}/{strategy_name}.json', encoding='utf-8-sig')
                    logger.info(f"<시스템> {item.currency_pair} 전략 파일 입력 완료")
                except Exception as e:
                    logger.error(f'<ERROR> {e}')
                for strategy in strategy_file:
                    strategy_dict[strategy_name] = Strategy(
                        strategy_name, strategy_file['strategy'][0], strategy_file['indicator'][0], strategy_file['condition'][0])
    ################################################################
    ######################매매 조건 이름 설정########################
    for item in item_list:
        item.get_signal_name(strategy_dict)
    ################################################################
    return item_list, strategy_dict


def check_wait_orders(item, user, state_db, slack_list=None):
    """
    체결 대기 중인 주문들 상태 갱신

    Parameters
    ----------
    item : TYPE
        Item 객체.
    user : TYPE
        Trader 객체.
    state_db : TYPE
        State_db 객체.
    slack_list : TYPE, optional
        Slack 객체 리스트. The default is None.

    Returns
    -------
    None.
    """
    wait_orders = user.api.get_orders(item.currency_pair, 'wait')
    done_orders = user.api.get_orders(item.currency_pair, 'done')
    cancelled_orders = user.api.get_orders(item.currency_pair, 'cancel')
    if wait_orders is not None:
        wait_orders = list(wait_orders['id'])
    else:
        wait_orders = []
    if done_orders is not None:
        done_orders = list(done_orders['id'])
    else:
         done_orders = []
    if cancelled_orders is not None:
        cancelled_orders = list(cancelled_orders['id'])
    else:
         cancelled_orders = []
    temp_wait_orders = []
    for wait_order in item.wait_orders:
        if wait_order in wait_orders:
            temp_wait_orders.append(wait_order)
        elif wait_order in done_orders:
            if slack_list is not None:
                for slack in slack_list:
                    slack.push_message(f'{wait_order} 체결 완료')
                logger.info(f'{wait_order} 체결 완료')
                state_db.delete_wait_order(wait_order)
        elif wait_order in cancelled_orders:
            logger.info(f'{wait_order} 체결 취소')
            state_db.delete_wait_order(wait_order)
        else:
            continue
    item.wait_orders = temp_wait_orders


def strategy_monitor(buy_price_type, sell_price_type, trader, slack_list=None):
    """
    자동거래

    Parameters
    ----------
    buy_price_type : TYPE
        DESCRIPTION.
    sell_price_type : TYPE
        DESCRIPTION.
    trader : TYPE
        DESCRIPTION.
    slack_list : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    """
    # user = trader.Trader(exchange='upbit', access_key='xPBD01XVAMNUF5mfxOYbc6BR7xCrtb2LRTRJmrHS', secret_key='CS0cqYUmzPv4wqaaZX4rBX8hZGCz67xfzWvtHYs5')
    # user = trader.Trader(exchange='gate', access_key='60f9f7df5fdb7a4ac64d1efba7bbda7a', secret_key='d4bb73c3aa84f6834f0fd5a056eb3d72789a730cef08492a88a33c3d492f726f')
    slack_list = [util.Slack(token=slack_tocken['tocken'], channel=slack_tocken['channel'])
                  for slack_tocken in slack_list]
    if slack_list is not None:
        for slack in slack_list:
            slack.push_message("auto_trader 시작")
    state_db = link_db.State_db()
    item_list, strategy_dict = init_item(buy_price_type=buy_price_type, sell_price_type=sell_price_type,
                                         slack_list=slack_list, trader=trader, state_db=state_db, config_file='tradecode.json')
    state_db.link_order_count(item_list, trader.exchange)
    state_db.link_wait_order(item_list, trader.exchange)
    for item in item_list:
        check_wait_orders(item, trader, state_db)  # 체결 대기중인 주문 갱신
    try:
        while(1):
            for item in item_list:
                # 주가 데이터
                item.set_df(trader)
                # 지표 컬럼 추가
                item.set_indi(strategy_dict)
                item.set_stop_order(trader.gap_rate_buy2curr(
                    item.currency_pair))     # 현재가와 매수 평균가 차이 비율 컬럼 추가
                # 매매 시그널 발생 여부 확인
                item.check_signal(strategy_dict)
                # 체결 대기중인 주문 갱신
                check_wait_orders(item, trader, state_db, slack_list=None)
            time.sleep(4)
    except Exception as e:
        state_db.con.close()
        print(traceback.format_exc())
        logger.error(f'<ERROR> {e}')
    finally:
        state_db.con.close()
        if slack_list is not None:
            for slack in slack_list:
                slack.push_message("auto_trader 종료")
        logger.info('<시스템> DB 연결 종료')
        logger.info('<시스템> 시스템 종료')
