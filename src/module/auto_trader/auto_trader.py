import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from module.auto_trader.trader import Trader
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
    buy_price_type = int(args.buy_price)
    sell_price_type = int(args.sell_price)
    ###############################################
    # user = trader.Trader(exchange='upbit', access_key='xPBD01XVAMNUF5mfxOYbc6BR7xCrtb2LRTRJmrHS', secret_key='CS0cqYUmzPv4wqaaZX4rBX8hZGCz67xfzWvtHYs5')
    # user = trader.Trader(exchange='gate', access_key='60f9f7df5fdb7a4ac64d1efba7bbda7a', secret_key='d4bb73c3aa84f6834f0fd5a056eb3d72789a730cef08492a88a33c3d492f726f')
    # 사용자 access_key
    access_key = 'xPBD01XVAMNUF5mfxOYbc6BR7xCrtb2LRTRJmrHS'     #upbit
    # access_key = '60f9f7df5fdb7a4ac64d1efba7bbda7a'     #gate
    # 사용자 secret_key
    secret_key = 'CS0cqYUmzPv4wqaaZX4rBX8hZGCz67xfzWvtHYs5'     #upbit
    # secret_key = 'd4bb73c3aa84f6834f0fd5a056eb3d72789a730cef08492a88a33c3d492f726f' #gate
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
    # 거래소 통신 객체 생성
    trader = Trader(exchange='upbit', access_key=user_info.access_key, secret_key=user_info.secret_key)
    #####################################################

    # 출금 불가능한 API KEY인지 확인
    if trader.is_withdrwas():
        logger.warning('<API> 현재 계정은 출금 기능을 지원합니다.')
        logger.info('<시스템> 시스템 종료')
    else:
        logger.info('<API> 현재 계정은 출금 기능을 지원하지 않습니다.')
        strategy_monitor(buy_price_type, sell_price_type, trader, user_info.slack_tocken_list)