from PySide2.QtWidgets import *
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QUrl

import pandas as pd
import copy
import os
import numpy as np
from datetime import date, datetime, timedelta
import sys

import plotly.express as px
import plotly.offline as offline
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# 경고문 삭제
import warnings
warnings.filterwarnings('ignore')

import logging
logging.getLogger().setLevel(logging.CRITICAL)

class SimpleStrategyGraph(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.title = '전략 거래 결과 그래프'
        self.left = 10
        self.top = 10
        self.width = 1000
        self.height = 600

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.center()

        layout = QVBoxLayout()

        # plot canvas
        self.canvas = QWebEngineView()

        # 확인, 취소 버튼
        btn_lay = QHBoxLayout()
        self.add = QPushButton('확인')
        self.add.clicked.connect(self.confirmIt)

        self.close = QPushButton('취소')
        self.close.clicked.connect(self.closeIt)

        btn_lay.addWidget(self.add)
        btn_lay.addWidget(self.close)

        layout.addWidget(self.canvas)
        layout.addLayout(btn_lay)
        self.setLayout(layout)

    # 매수, 매도 포인트 그래프
    def draw_strategy_result_graph(self, root_path, stock_df, start, end, df):
        copy_order_df = copy.deepcopy(df)
        copy_order_df.set_index('order_datetime', inplace=True)

        copy_stock_df = copy.deepcopy(stock_df)
        copy_stock_df.set_index('Date', inplace=True)
        copy_stock_df = copy_stock_df[start:end]
        copy_stock_df.reset_index(inplace=True)
        
        merge_df = pd.merge(copy_stock_df, copy_order_df, how='left', left_on='Date', right_on='order_datetime')
        merge_df.set_index('Date', inplace=True)

        # fig = make_subplots(specs=[[{"secondary_y": True}]])

        # stock candle chart
        stock_candle = go.Candlestick(x=merge_df.index, 
                                open=merge_df['open'], 
                                high=merge_df['high'], 
                                low=merge_df['low'], 
                                close=merge_df['close'],
                                increasing={'line':{'color':'red'}},
                                decreasing={'line':{'color':'blue'}},
                                name='candle'
                                )

        fig = go.Figure(data=[stock_candle])

        fig.layout = dict(title='전략 거래 결과 그래프',
                          xaxis=dict(title='Date'),
                          yaxis=dict(title='Price')
                          )

        fig.update_xaxes(title='날짜',
                        type='category',
                        categoryorder='category ascending',
                        tickangle=45
                        )

        fig.update_yaxes(title='가격')

        # 종가 기준 꺾은선그래프
        price_chart = go.Scatter(x=merge_df.index,
                            y=merge_df['close'], 
                            mode='lines', showlegend=False,
                            line=dict(color='black', width=1)
                            )

        fig.add_trace(price_chart)
        
        for i in merge_df[merge_df['order_type'] == 'buy'].index:
            fig.add_vline(x=i, line_color="red")
        for i in merge_df[merge_df['order_type'] == 'sell'].index:
            fig.add_vline(x=i, line_color="blue")

        os.makedirs(f'{root_path}/graph', exist_ok=True)
        self.file_path = os.path.abspath(os.path.join(f'{root_path}/graph', "simple_strategy_chart.html"))
        offline.plot(fig, filename=self.file_path, auto_open=False)
        self.canvas.load(QUrl.fromLocalFile(self.file_path))
        self.canvas.show()

    def confirmIt(self):
        SimpleStrategyGraph.close(self)

    def closeIt(self):
        SimpleStrategyGraph.close(self)

    def showModal(self):
        return super().exec_()

    # 화면 중앙 배치
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())