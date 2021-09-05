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

    # 레이블 백테스트 - 레이블 그래프
    def draw_label_graph(self, root_path, df, target='close', state=''):
        copy_df = copy.deepcopy(df)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.layout = dict(title='레이블 그래프',
                          xaxis=dict(title='Date'),
                          yaxis=dict(title='Price')
                          )

        # stock chart
        stock_chart = go.Scatter(x=copy_df.index, y=copy_df[target],
                                mode='lines', showlegend=False,
                                name='stock chart',
                                line=dict(color='black')
                                )

        fig.add_trace(stock_chart, secondary_y=False)

        # top, bottom label marker
        top_label_chart = go.Scatter(x=copy_df[copy_df[f'{target}_top']==1].index, 
                                y=copy_df[copy_df[f'{target}_top']==1][target],
                                mode='markers', showlegend=True,
                                name='top',
                                marker=dict(color='lightblue', size=10)
                                )

        bottom_label_chart = go.Scatter(x=copy_df[copy_df[f'{target}_bottom']==1].index, 
                                y=copy_df[copy_df[f'{target}_bottom']==1][target],
                                mode='markers', showlegend=True,
                                name='bottom',
                                marker=dict(color='brown', size=10)
                                )

        fig.add_trace(top_label_chart, secondary_y=False)
        fig.add_trace(bottom_label_chart, secondary_y=False)

        # buy & sell label marker
        buy_label_chart = go.Scatter(x=copy_df[copy_df['order_type'] == 'buy'].index,
                            y=copy_df[copy_df['order_type'] == 'buy'][target], 
                            mode='markers', showlegend=True,
                            name='buy',
                            marker=dict(color='red', symbol='arrow-up', size=10)
                            )

        sell_label_chart = go.Scatter(x=copy_df[copy_df['order_type'] == 'sell'].index,
                            y=copy_df[copy_df['order_type'] == 'sell'][target], 
                            mode='markers', showlegend=True,
                            name='sell',
                            marker=dict(color='blue', symbol='arrow-down', size=10)
                            )

        fig.add_trace(buy_label_chart, secondary_y=False)
        fig.add_trace(sell_label_chart, secondary_y=False)

        # top & bottom zone label marker
        topzone_label_chart = go.Scatter(x=copy_df[copy_df[f'{target}_top_zone'] == 1].index,
                            y=copy_df[copy_df[f'{target}_top_zone'] == 1][target], 
                            mode='markers', showlegend=True,
                            name='top zone',
                            marker=dict(color='gray', size=10)
                            )

        bottomzone_label_chart = go.Scatter(x=copy_df[copy_df[f'{target}_bottom_zone'] == 1].index,
                            y=copy_df[copy_df[f'{target}_bottom_zone'] == 1][target], 
                            mode='markers', showlegend=True,
                            name='bottom zone',
                            marker=dict(color='yellow', size=10)
                            )

        fig.add_trace(topzone_label_chart, secondary_y=False)
        fig.add_trace(bottomzone_label_chart, secondary_y=False)

        os.makedirs(f'{root_path}/graph', exist_ok=True)
        self.file_path = os.path.abspath(os.path.join(f'{root_path}/graph', "basic_profit_chart.html"))
        offline.plot(fig, filename=self.file_path, auto_open=False)
        self.load(QUrl.fromLocalFile(self.file_path))
        self.show()