from PySide2.QtWidgets import *
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QUrl

import copy
import os

import plotly.offline as offline
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# 경고문 삭제
import warnings
warnings.filterwarnings('ignore')

import logging
logging.getLogger().setLevel(logging.CRITICAL)

class PlotCanvas(QWebEngineView):

    def __init__(self):
        super().__init__()

    # 기본 백테스트 메뉴 - 기간별 수익률 그래프(거래 o) & 기본 주가 수익률(거래 x)
    def draw_backtest_graph(self, root_path, df, trading_df, state=''):
        copy_df = copy.deepcopy(df)
        copy_df.set_index('datetime', inplace=True)

        copy_trading_df = copy.deepcopy(trading_df)
        copy_trading_df.set_index('order_datetime', inplace=True)

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.update_xaxes(title='Date')
        asset_chart = go.Scatter(x=copy_df.index, y=copy_df['cumulative profit/loss ratio'],
                            mode='lines+markers', showlegend=True,
                            name='전략 수익률',
                            line=dict(color='green'),
                            marker=dict(color='green')
                            )

        fig.add_trace(asset_chart, secondary_y=False)
        fig.update_yaxes(title='Profit Ratio(%)', secondary_y=False)

        # 기간별 수익률
        if state == 'period_profit':
            profit_chart = go.Scatter(x=copy_df.index, y=copy_df['profit/loss ratio'],
                                    mode='lines+markers', showlegend=True,
                                    name='기간별 수익률',
                                    line=dict(color='red'),
                                    marker=dict(color='red')
                                    )

            fig.add_trace(profit_chart, secondary_y=False)
            fig.update_yaxes(title='Profit Ratio(%)', secondary_y=False)

        # 기본 주가 수익률
        if state == 'basic_profit':            
            copy_trading_df.reset_index(inplace=True)            
            copy_trading_df['basic_profit'] = ((copy_trading_df.loc[:, ['price']] / copy_trading_df.loc[0, ['price']]) - 1) * 100            
            copy_trading_df.set_index('order_datetime', inplace=True)
            basic_profit_chart = go.Scatter(x=copy_trading_df.index, y=copy_trading_df['basic_profit'],
                                mode='lines+markers', showlegend=True,
                                name='주가 수익률',
                                line=dict(color='blue'),
                                marker=dict(color='blue')
                                )

            fig.add_trace(basic_profit_chart, secondary_y=False)
            fig.update_yaxes(title='Profit Ratio(%)', secondary_y=False)
        
        os.makedirs(f'{root_path}/graph', exist_ok=True)
        self.file_path = os.path.abspath(os.path.join(f'{root_path}/graph', "basic_profit_chart.html"))
        offline.plot(fig, filename=self.file_path, auto_open=False)
        self.load(QUrl.fromLocalFile(self.file_path))
        self.show()