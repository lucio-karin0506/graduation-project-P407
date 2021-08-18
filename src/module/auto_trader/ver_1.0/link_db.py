import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from module.auto_trader import util

logger = util.CreateLogger('link_db')

class State_db():
    def __init__(self):
        """
        sqlite3 DataBase와 연동

        Returns
        -------
        None.

        """

        try:
            self.con = sqlite3.connect("./auto_trader.db")
            self.cursor = self.con.cursor()
        except Exception as e:
            logger.error(f'<ERROR> {e}')

    def link_order_count(self, item_list):
        '''
        order_count 테이블 연동

        Parameters
        ----------
        item_list : list(item)
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        # order_count 테이블 처리
        sql = '''SELECT name 
        FROM sqlite_master 
        WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table', 'view') ORDER BY 1;'''
        table_name = pd.read_sql(sql, self.con, index_col=None)
        if 'order_count' not in list(table_name['name']):
            sql = '''
            CREATE TABLE "order_count" (
            	"coin"	TEXT NOT NULL,
            	"order_type"	TEXT NOT NULL,
            	"signal_name"	TEXT NOT NULL,
            	"count"	INTEGER NOT NULL,
                "last_order_time" TIMESTAMP,
            	PRIMARY KEY("coin","order_type","signal_name")
            );'''
            self.cursor.execute(sql)
            self.con.commit()
            logger.info('<DB> order_count TABLE 생성 완료')
        else:

            # DB의 가장 최근 order_time을 변수에 저장
            for item in item_list:
                code = f'{item.code}'
                sql = f'''select last_order_time from order_count where coin='{code}' and order_type='sell' order by last_order_time asc;'''
                db_df = pd.read_sql(sql, self.con, index_col=None)
                if len(db_df) != 0:
                    last_order_time = db_df.iloc[0]['last_order_time']
                    last_sell_time = datetime.strptime(
                        last_order_time.replace(' ', 'T'), '%Y-%m-%dT%H:%M:%S')
                    item.last_sell_time[last_sell_time] = True

                sql = f'''select last_order_time from order_count where coin='{code}' and order_type='buy' order by last_order_time asc;'''
                db_df = pd.read_sql(sql, self.con, index_col=None)
                if len(db_df) != 0:
                    last_order_time = db_df.iloc[0]['last_order_time']
                    last_buy_time = datetime.strptime(
                        last_order_time.replace(' ', 'T'), '%Y-%m-%dT%H:%M:%S')
                    item.last_buy_time[last_buy_time] = True

            db_df = pd.read_sql("select * from order_count",
                                self.con, index_col=None)
            for index, row_df in db_df.iterrows():
                for item in item_list:
                    if item.code == row_df['coin']:
                        if row_df['order_type'] == 'sell':
                            item.sell_count[row_df['signal_name']
                                            ] = row_df['count']
                            break
                        elif row_df['order_type'] == 'buy':
                            item.buy_count[row_df['signal_name']
                                           ] = row_df['count']
                            break
            logger.info('<DB> order_count TABLE 연동 완료')

    def link_wait_order(self, upbit_exchange, item_list):
        """
        wait_order 테이블 연동
        """
        # wait_order 테이블 처리
        sql = '''SELECT name 
        FROM sqlite_master 
        WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table', 'view') ORDER BY 1;'''
        table_name = pd.read_sql(sql, self.con, index_col=None)
        if 'wait_order' not in list(table_name['name']):
            sql = '''
            CREATE TABLE "wait_order" (
            	"coin"	TEXT NOT NULL,
            	"uuid"	TEXT NOT NULL,
                "signal_name" TEXT NOT NULL,
                "order_type" TEXT NOT NULL,
            	PRIMARY KEY("uuid")
            );'''
            self.cursor.execute(sql)
            self.con.commit()
            logger.info('<DB> wait_order TABLE 생성 완료')
        else:
            db_df = pd.read_sql("select * from wait_order;",
                                self.con, index_col=None)
            for index, row_df in db_df.iterrows():
                uuid = row_df['uuid']
                state = upbit_exchange.get_order_state(uuid)
                # 미체결 주문 연동
                if state == 'wait':
                    for item in item_list:
                        if item.code == row_df['coin']:
                            if row_df['order_type'] == 'buy':
                                item.buy_uuids[row_df['signal_name']] = [
                                    row_df['uuid']]
                            elif row_df['order_type'] == 'sell':
                                item.sell_uuids[row_df['signal_name']] = [
                                    row_df['uuid']]
                        break
                self.check_order(uuid, state)

            logger.info('<DB> wait_order TABLE 연동 완료')

    def write_order_count(self, code, order_type, signal_name, count, last_order_time=None):
        '''
        order_coubt 테이블에 데이터 저장
        '''
        sql = f'''select count(*) 
        from order_count 
        where coin='{code}' and order_type='{order_type}' and signal_name='{signal_name}';'''
        #last_order_time = datetime.strftime(last_order_time, '%Y-%m-%d %H:%M:%S')
        count_data = pd.read_sql(sql, self.con)
        if count_data['count(*)'].iloc[0] == 1:
            try:
                if last_order_time == None:
                    sql = '''
                    UPDATE order_count
                    SET count=?
                    WHERE coin=? and order_type=? and signal_name=?;'''
                    self.cursor.execute(
                        sql, (count, code, order_type, signal_name))
                    self.con.commit()                    
                else:
                    sql = '''
                    UPDATE order_count
                    SET count=?, last_order_time=?
                    WHERE coin=? and order_type=? and signal_name=?;'''
                    self.cursor.execute(
                        sql, (count, last_order_time, code, order_type, signal_name))
                    self.con.commit()                    
                logger.info(
                        f'<DB 입력> TABLE=order_count, market={code}, order_type={order_type}, signal_name={signal_name}, count={count}')
            except:
                logger.error('<ERROR> order_count TABLE 데이터 삽입 오류')
        else:
            try:
                self.cursor.execute("INSERT INTO order_count Values(?,?,?,?,?)",
                                    (code, order_type, signal_name, count, last_order_time))
                self.con.commit()
            except:
                logger.error('<ERROR> order_count TABLE 데이터 삽입 오류')

    def write_wait_order(self, code, uuid, signal_name, order_type):
        '''
        wait_order 테이블에 데이터 저장
        '''

        try:
            self.cursor.execute(
                "INSERT INTO wait_order Values(?,?,?, ?)", (code, uuid, signal_name, order_type))
            self.con.commit()
        except Exception as e:
            logger.error(f'<ERROR> {e}')

    def delete_wait_order(self, uuid):
        '''
        wait_order 테이블에 데이터 삭제
        '''
        try:
            signal_name = pd.read_sql(
                f"SELECT signal_name FROM wait_order where uuid='{uuid}';", self.con, index_col=None).iloc[0]['signal_name']
            self.cursor.execute(
                "DELETE FROM wait_order where uuid=?;", (uuid,))
            self.con.commit()
            logger.info(f'<DB> signal_name:{signal_name}, uuid:{uuid} 제거')
        except Exception as e:
            logger.error(f'<ERROR> {e}')

    def check_order(self, uuid, state):
        '''
        wait_order 테이블에서 거래 취소 혹은 거래 완료된 주문 삭제
        '''
        if state == 'done':
            self.delete_wait_order(uuid)
        elif state == 'cancel':
            self.delete_wait_order(uuid)
        elif state == 'error':
            self.delete_wait_order(uuid)
        else:
            pass