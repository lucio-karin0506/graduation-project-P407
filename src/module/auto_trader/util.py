from logging import handlers, StreamHandler
import logging
import argparse
import datetime
from slacker import Slacker
import sqlite3
import pandas as pd
from cryptography.fernet import Fernet  # symmetric encryption
import re

def floor(decimal, digit):
    if isinstance(decimal, int):
        return decimal
    elif isinstance(decimal, str):
        if '.' in decimal:
            return float(str(decimal)[:len(re.findall('(.*)\..*', decimal)[0]) + digit + 1])
        else:
            return int(decimal)
    elif isinstance(decimal, float):
        return float(str(decimal)[:len(re.findall('(.*)\..*', str(decimal))[0]) + digit + 1])
def CreateLogger(logger_name):
    """
    로그 생성 함수

    Parameters
    ----------
    logger_name : str
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    # Create Logger
    logger = logging.getLogger(logger_name)

    # Check handler exists
    if len(logger.handlers) > 0:
        return logger  # Logger already exists

    logger.setLevel(logging.DEBUG)

    # 로그 format
    formatter = logging.Formatter(
        '[%(levelname)s|%(filename)s:%(lineno)s]\t%(asctime)s >\t%(message)s')

    # Create Handlers
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.INFO)
    streamHandler.setFormatter(formatter)

    logger.addHandler(streamHandler)

    # log를 파일에 출력
    file_handler = logging.handlers.RotatingFileHandler(
        './logfile_{:%Y%m%d}.log'.format(datetime.datetime.now()), maxBytes=1024*10000, backupCount=100, encoding='utf8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# 로그 생성
logger=CreateLogger('util')

def get_arguments():
    """
    콘솔 모드에서 실행 시 각종 설정 변수 처리

    Returns
    -------
    args : TYPE
        DESCRIPTION.

    """

    parser = argparse.ArgumentParser(description='Auto_trader')

    parser.add_argument('--ord_type', required=False,
                        default='limit', help='시장가:market, 지정가:limit')
    parser.add_argument('--buy_price', required=False,
                        default=1, help='매도1호가: 1, 매수1호가: -1, 현재가: 0')
    parser.add_argument('--sell_price', required=False,
                        default=1, help='매도1호가: 1, 매수1호가: -1, 현재가: 0')
    # parser.add_argument('--buy_count', required=False, default=1, help='매수 동일 조건 진입 횟수')
    # parser.add_argument('--sell_count', required=False, default=1, help='매도 동일 조건 진입 횟수')

    args = parser.parse_args()

    return args

class SimpleEnDecrypt:
    # Fernet is basically AES128 in CBC mode with a SHA256 HMAC message authentication code.
    def __init__(self, key=None):
        """
        DBEnDecrypt 클래스에 사용되는 암호화, 복호화 기능

        Parameters
        ----------
        key : str, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        if key is None:  # 키가 없다면
            key = Fernet.generate_key()  # 키를 생성한다
        self.key = key
        self.f = Fernet(self.key)

    def encrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.encrypt(data)  # 바이트형태이면 바로 암호화
        else:
            ou = self.f.encrypt(data.encode('utf-8'))  # 인코딩 후 암호화
        if is_out_string is True:
            return ou.decode('utf-8')  # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou

    def decrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.decrypt(data)  # 바이트형태이면 바로 복호화
        else:
            ou = self.f.decrypt(data.encode('utf-8'))  # 인코딩 후 복호화
        if is_out_string is True:
            return ou.decode('utf-8')  # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou

    def __close__(self):
        self.con.close()


class DBEnDecrypt:
    def __init__(self, access_key=None, secret_key=None, slack_tocken_list=None):
        """
        DB와 연동하여 access_key, secret_key, slack_token 암호화 및 복호화
        - 파라미터가 없는 경우 DB로부터 복호화하여 값 리턴
        - 파라미터가 있는 경우 깂을 암호화하여 DB에 저장
        Parameters
        ----------
        access_key : str, optional
            DESCRIPTION. The default is None.
        secret_key : tr, optional
            DESCRIPTION. The default is None.
        slack_tocken_list : str, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        # 복호화 키
        self.de_key = b'C8lNZN4pa1mwMKkgAxqwZGSIw3SVFmQPxtLbqBMvn9Y='

        # 암호화 객체 생성
        self.endecrypt = SimpleEnDecrypt(self.de_key)

        # 데이터베이스 연결
        try:
            self.con = sqlite3.connect("./auto_trader.db")
            self.cursor = self.con.cursor()
        except Exception as e:
            logger.error(f'<ERROR> {e}')

        if access_key and secret_key and slack_tocken_list:
            # 사용자 access_key
            self.access_key = access_key
            # 사용자 secret_key
            self.secret_key = secret_key
            # 사용자 슬랙 봇
            self.slack_tocken_list = slack_tocken_list
            # 암호화하여 DB에 저장
            self.encrypt()
        else:
            self.decrypt()

    def encrypt(self):
        """
        값 암호화 하여 DB에 저장

        Returns
        -------
        None.

        """

        # 테이블 초기화
        self.cursor.execute('drop table if exists exchange_key')
        self.cursor.execute('drop table if exists slack_tocken')
        self.con.commit()

        sql = '''CREATE TABLE "exchange_key" (
            	"exchange"	TEXT NOT NULL,
            	"access_key"	TEXT NOT NULL,
            	"secret_key"	TEXT NOT NULL,
            	PRIMARY KEY("exchange", "access_key", "secret_key"));'''
        self.cursor.execute(sql)
        self.con.commit()
        sql = '''CREATE TABLE "slack_tocken" (
            	"exchange"	TEXT NOT NULL,
            	"tocken"	TEXT NOT NULL,
            	"channel"	TEXT NOT NULL,
            	PRIMARY KEY("exchange", "tocken", "channel"));'''
        self.cursor.execute(sql)
        self.con.commit()

        # 거래소 키 데이터 존재 X
        count_db = pd.read_sql(
            "SELECT count(*) FROM exchange_key WHERE exchange='upbit';", self.con, index_col=None)
        if count_db['count(*)'][0] == 0:
            # 거래소 키 입력
            sql = '''INSERT INTO exchange_key Values(?,?,?);'''
            self.cursor.execute(sql, ('upbit', self.endecrypt.encrypt(
                self.access_key), self.endecrypt.encrypt(self.secret_key)))
            self.con.commit()

        # 슬랙 봇 데이터 존재 X
        count_db = pd.read_sql(
            "SELECT count(*) FROM slack_tocken WHERE exchange='upbit';", self.con, index_col=None)
        if count_db['count(*)'][0] != len(self.slack_tocken_list):
            # 슬랙 봇 토큰 입력
            sql = '''INSERT INTO slack_tocken Values(?,?,?);'''
            for slack_tocken in self.slack_tocken_list:
                self.cursor.execute(sql, ('upbit', self.endecrypt.encrypt(
                    slack_tocken['tocken']), self.endecrypt.encrypt(slack_tocken['channel'])))
                self.con.commit()

    def decrypt(self):
        """
        데이터 복호화 후 값 저장

        Returns
        -------
        None.

        """
        try:
            sql = '''select * from exchange_key;'''
            db_df = pd.read_sql(sql, self.con, index_col=None)
            self.access_key = self.endecrypt.decrypt(
                db_df.iloc[0]['access_key'])
            self.secret_key = self.endecrypt.decrypt(
                db_df.iloc[0]['secret_key'])

            sql = '''select * from slack_tocken;'''
            db_df = pd.read_sql(sql, self.con, index_col=None)
            self.slack_tocken_list = [{'tocken': self.endecrypt.decrypt(db_df.iloc[i]['tocken']),
                                       'channel':self.endecrypt.decrypt(db_df.iloc[i]['channel'])} for i in range(len(db_df))]
        except Exception as e:
            logger.error(f'<ERROR> {e}')


class Slack():
    def __init__(self, token, channel):
        """
        슬랙 봇 기능

        Parameters
        ----------
        token : str
            DESCRIPTION.
        channel : str
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.token = token
        self.channel = channel
        self.slack = Slacker(token)

    def push_message(self, message):
        """
        슬랙 채널에 메시지 송신

        Parameters
        ----------
        message : str
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.slack.chat.post_message(self.channel, message)



