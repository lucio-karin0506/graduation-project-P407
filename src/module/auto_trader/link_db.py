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

    def link_order_count(self, item_list, exchange):
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
                "exchange" TEXT NOT NULL,
            	"side"	TEXT NOT NULL,
                "strategy_name" TEXT NOT NULL,
            	"signal_name"	TEXT NOT NULL,            
            	"count"	INTEGER NOT NULL,
                "last_order_time" TIMESTAMP,
            	PRIMARY KEY("coin","exchange","side","strategy_name", "signal_name")
            );'''
            self.cursor.execute(sql)
            self.con.commit()
            logger.info('<DB> order_count TABLE 생성 완료')
        else:
            sql = '''select coin, exchange, side, strategy_name, signal_name, count, last_order_time from order_count;'''
            db_df = pd.read_sql(sql, self.con, index_col=None)
            # DB의 가장 최근 order_time을 변수에 저장
            for item in item_list:
                item_df = db_df[(db_df['coin']==item.currency_pair)&(db_df['exchange']==exchange)]
                if len(item_df) != 0:
                    for index, row in item_df.iterrows():
                        if row['strategy_name'] in item.strategy_name:
                            item.last_order_time[row['side']][row['strategy_name']][row['signal_name']] = row['last_order_time']
                            item.order_count[row['side']][row['strategy_name']][row['signal_name']] = row['count']
            logger.info('<DB> order_count TABLE 연동 완료')

    def link_wait_order(self, item_list, exchange):
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
                "exchange" TEXT NOT NULL,
            	"id"	TEXT NOT NULL,
                "side" TEXT NOT NULL,
                "strategy_name" TEXT NOT NULL,
                "signal_name" TEXT NOT NULL, 
            	PRIMARY KEY("id")
            );'''
            self.cursor.execute(sql)
            self.con.commit()
            logger.info('<DB> wait_order TABLE 생성 완료')
        else:
            db_df = pd.read_sql("select coin, exchange, id, strategy_name, signal_name, side from wait_order;", self.con, index_col=None)           
            for item in item_list:
                item_df = db_df[(db_df['coin']==item.currency_pair)&(db_df['exchange']==exchange)]
                if len(item_df) != 0:
                    for index, row in item_df.iterrows():
                        if row['strategy_name'] in item.strategy_name:
                            item.wait_orders.append(row['id'])
            logger.info('<DB> wait_order TABLE 연동 완료')

    def write_order_count(self, currency_pair, exchange, side, strategy_name, signal_name, count, last_order_time=None):
        '''
        order_count 테이블에 데이터 저장
        '''
        sql = f'''select count(*) 
        from order_count 
        where coin='{currency_pair}' and side='{side}' and strategy_name='{strategy_name}' and signal_name='{signal_name}';'''
        db_df = pd.read_sql(sql, self.con, index_col=None)
        if db_df['count(*)'].iloc[0] == 1:
            try:
                if last_order_time == None:
                    sql = '''
                    UPDATE order_count
                    SET count=?
                    WHERE coin=? and side=? and signal_name=? and strategy_name=?;'''
                    self.cursor.execute(
                        sql, (count, currency_pair, side, signal_name, strategy_name))
                    self.con.commit()     
                    logger.info(
                        f'''<DB 입력> TABLE=order_count, coin={currency_pair}, side={side},
                        straegy_name={strategy_name}, signal_name={signal_name},count={count}''')
                else:
                    sql = '''
                    UPDATE order_count
                    SET count=?, last_order_time=?
                    WHERE coin=? and side=? and signal_name=? and strategy_name=?;'''
                    self.cursor.execute(
                        sql, (count, last_order_time, currency_pair, side, signal_name, strategy_name))
                    self.con.commit()                    
                logger.info(
                        f'''<DB 입력> TABLE=order_count, coin={currency_pair}, side={side},
                        straegy_name={strategy_name}, signal_name={signal_name},
                        count={count}, last_order_time={last_order_time}''')
            except:
                logger.error('<ERROR> order_count TABLE 데이터 삽입 오류')
        else:
            try:
                self.cursor.execute("INSERT INTO order_count Values(?,?,?,?,?,?,?)",
                                    (currency_pair, exchange, side, strategy_name, signal_name, count, last_order_time))
                self.con.commit()
            except:
                logger.error('<ERROR> order_count TABLE 데이터 삽입 오류')

    def write_wait_order(self, currency_pair, exchange, uuid, side, strategy_name, signal_name):
        '''
        wait_order 테이블에 데이터 저장
        '''

        try:
            self.cursor.execute(
                "INSERT INTO wait_order Values(?,?,?,?,?,?)", (currency_pair, exchange, uuid, side, strategy_name, signal_name))
            self.con.commit()
        except Exception as e:
            logger.error(f'<ERROR> {e}')

    def delete_wait_order(self, uuid):
        '''
        wait_order 테이블에 데이터 삭제
        '''
        try:
            db_df = pd.read_sql(
                f"SELECT * FROM wait_order where id='{uuid}';", self.con, index_col=None).iloc[0]
            self.cursor.execute(
                "DELETE FROM wait_order where id=?;", (uuid,))
            self.con.commit()
            logger.info(f"<DB> coin:{db_df['coin']}, side:{db_df['side']}, signal_name:{db_df['signal_name']}, strategy_name:{db_df['strategy_name']}, uuid:{uuid} 제거")
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