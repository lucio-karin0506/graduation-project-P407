import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from module.auto_trader.trader import Trader
from module.auto_trader.upbit_api import Upbit_Api
from module.auto_trader.strategy_monitor import strategy_monitor
from module.auto_trader import util

# log 생성
logger = util.CreateLogger('main')

if __name__ == '__main__':

    # 콘솔모드 입력 값
    args = util.get_arguments()

    ##############################################
    logger.info('<시스템> 시스템 시작')
    ##############################################
    # 시장가, 지정가 선택
    # 시장가:'market', 지정가:'limit'
    ord_type = args.ord_type
    # 주문 가격 선택
    # 시장가로 주문시 상관 X
    # 매도1호가: 1, 매수1호가: -1, 현재가: 0
    buy_price = int(args.buy_price)
    sell_price = int(args.sell_price)
    ###############################################
    # 사용자 access_key
    access_key = 'xPBD01XVAMNUF5mfxOYbc6BR7xCrtb2LRTRJmrHS'
    # 사용자 secret_key
    secret_key = 'CS0cqYUmzPv4wqaaZX4rBX8hZGCz67xfzWvtHYs5'
    # 복호화 키
    de_key = b'C8lNZN4pa1mwMKkgAxqwZGSIw3SVFmQPxtLbqBMvn9Y='
    # 사용자 슬랙 봇
    slack_tocken_list = [
        {'tocken': 'xoxb-1240766744951-1783851340148-glRUmlHL2aRi8wO8qi4wuZFp', 'channel': 'test'}]
    ##################################################
    # 거래소 키 암호화
    util.DBEnDecrypt(access_key, secret_key, slack_tocken_list)
    logger.info('<DB> exchange_key, slack_tocken 암호화')
    # DB로부터 거래소 키와 슬랙 토큰 데이터 복호화
    user_info = util.DBEnDecrypt()
    logger.info('<DB> exchange_key, slack_tocken 복호화')
    ################################################
    # 조회용
    upbit_quotation = Upbit_Api()
    # 거래용
    upbit_exchange = Trader(
        access_key=user_info.access_key, secret_key=user_info.secret_key)
    #####################################################

    # 출금 불가능한 API KEY인지 확인
    if not 'error.message' in list(upbit_exchange.upbit.is_withdraws_api().keys()):
        logger.warning('<API> 현재 exchange_key는 출금 기능을 지원합니다.')
        logger.info('<시스템> 시스템 종료')
    else:
        logger.info('<API> 현재 exchange_key는 출금 기능을 지원하지 않습니다.')
        strategy_monitor(upbit_quotation, upbit_exchange,
             user_info.slack_tocken_list, ord_type, buy_price, sell_price)
