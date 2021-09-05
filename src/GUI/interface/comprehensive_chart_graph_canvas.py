from PySide2.QtWidgets import *
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QUrl
from matplotlib.pyplot import legend

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

    '''
        종합차트 합성 그래프
            indf: 내부 data
            outdf: 외부 data
            infile_x: 내부파일 x축
            outfile_x: 외부파일 x축
            infile_y: 내부파일 y축
            outfile_y: 외부파일 y축
            in_state: 내부 그래프 개형 옵션(marker, bar, plot, plot+marker, candle)
            out_state: 외부 그래프 개형 옵션(marker, bar, plot, plot+marker, candle)
    '''
    def draw_merge_graph(self, 
                        root_path,
                        indf, outdf, 
                        infile_x, outfile_x, 
                        infile_y, outfile_y, 
                        in_state, out_state):

        # 내부 파일 데이터프레임
        copy_in_df = copy.deepcopy(indf)
        copy_in_df.set_index(infile_x, inplace=True)

        # 외부 파일 데이터프레임
        copy_out_df = copy.deepcopy(outdf)
        copy_out_df.set_index(outfile_x, inplace=True)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
         # x축
        fig.update_xaxes(title='Date',
                        type='category',
                        categoryorder='category ascending',
                        tickangle=45
                        )

        fig.update_yaxes(title_text=infile_y, secondary_y=False)
        fig.update_yaxes(title_text=outfile_y, secondary_y=True)

        # 내부 그래프 타입
        if in_state == 'marker':
            marker_chart = go.Scatter(x=copy_in_df.index, 
                                      y=copy_in_df[infile_y],
                                      mode='markers', 
                                      name='내부파일', 
                                      showlegend=True
                                      )

            fig.add_trace(marker_chart, secondary_y=False)

        if in_state == 'bar':
            bar_chart = go.Bar(x=copy_in_df.index, 
                                   y=copy_in_df[infile_y], 
                                   name='내부파일', 
                                   showlegend=True
                                   )

            fig.add_trace(bar_chart, secondary_y=False)

        if in_state == 'plot':
            plot_chart = go.Scatter(x=copy_in_df.index, 
                                      y=copy_in_df[infile_y],
                                      mode='lines', 
                                      name='내부파일', 
                                      showlegend=True
                                      )

            fig.add_trace(plot_chart, secondary_y=False)

        if in_state == 'plot+marker':
            plot_marker_chart = go.Scatter(x=copy_in_df.index, 
                                      y=copy_in_df[infile_y],
                                      mode='lines+markers', 
                                      name='내부파일', 
                                      showlegend=True
                                      )

            fig.add_trace(plot_marker_chart, secondary_y=False)

        if in_state == 'candle':
            candle_chart = go.Candlestick(x=copy_in_df.index, 
                                        open=copy_in_df['open'], 
                                        high=copy_in_df['high'], 
                                        low=copy_in_df['low'], 
                                        close=copy_in_df['close'],
                                        increasing={'line':{'color':'red'}},
                                        decreasing={'line':{'color':'blue'}},
                                        name='내부파일',
                                        showlegend=True
                                        )

            fig.add_trace(candle_chart, secondary_y=False)

        # 외부 그래프 타입
        if out_state == 'marker':
            marker_chart = go.Scatter(x=copy_out_df.index, 
                                      y=copy_out_df[outfile_y],
                                      mode='markers', 
                                      name='외부파일', 
                                      showlegend=True
                                      )

            fig.add_trace(marker_chart, secondary_y=True)

        if out_state == 'bar':
            bar_chart = go.Bar(x=copy_out_df.index, 
                                   y=copy_out_df[outfile_y], 
                                   name='외부파일', 
                                   showlegend=True
                                   )

            fig.add_trace(bar_chart, secondary_y=True)

        if out_state == 'plot':
            plot_chart = go.Scatter(x=copy_out_df.index, 
                                      y=copy_out_df[outfile_y],
                                      mode='lines', 
                                      name='외부파일', 
                                      showlegend=True
                                      )

            fig.add_trace(plot_chart, secondary_y=True)

        if out_state == 'plot+marker':
            plot_marker_chart = go.Scatter(x=copy_out_df.index, 
                                      y=copy_out_df[outfile_y],
                                      mode='lines+markers', 
                                      name='외부파일', 
                                      showlegend=True
                                      )

            fig.add_trace(plot_marker_chart, secondary_y=True)

        if out_state == 'candle':
            candle_chart = go.Candlestick(x=copy_out_df.index, 
                                        open=copy_out_df['open'], 
                                        high=copy_out_df['high'], 
                                        low=copy_out_df['low'], 
                                        close=copy_out_df['close'],
                                        increasing={'line':{'color':'red'}},
                                        decreasing={'line':{'color':'blue'}},
                                        name='외부파일',
                                        showlegend=True
                                        )

            fig.add_trace(candle_chart, secondary_y=True)

        os.makedirs(f'{root_path}/graph', exist_ok=True)
        self.file_path = os.path.abspath(os.path.join(f'{root_path}/graph', "merge_chart.html"))
        offline.plot(fig, filename=self.file_path, auto_open=False)
        self.load(QUrl.fromLocalFile(self.file_path))
        self.show()

    '''
        종합차트 병렬 그래프
            indf: 내부 data
            outdf: 외부 data
            infile_x: 내부파일 x축
            outfile_x: 외부파일 x축
            infile_y: 내부파일 y축
            outfile_y: 외부파일 y축
            in_state: 내부 그래프 개형 옵션(marker, bar, plot, plot+marker, candle)
            out_state: 외부 그래프 개형 옵션(marker, bar, plot, plot+marker, candle)
    '''
    def draw_parallel_graph(self, 
                            root_path,
                            indf, outdf, 
                            infile_x, infile_y, 
                            outfile_x, outfile_y, 
                            in_state, out_state
                            ):
        
        # 내부 파일 데이터프레임
        copy_in_df = copy.deepcopy(indf)
        copy_in_df.set_index(infile_x, inplace=True)

        # 외부 파일 데이터프레임
        copy_out_df = copy.deepcopy(outdf)
        copy_out_df.set_index(outfile_x, inplace=True)

        # figure setting
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=('내부파일', '외부파일'))

        # slider 삭제
        fig.update(layout_xaxis_rangeslider_visible=False)

        # 내부 그래프 타입
        if in_state == 'marker':
            marker_chart = go.Scatter(x=copy_in_df.index, 
                                      y=copy_in_df[infile_y],
                                      mode='markers', 
                                      name='내부파일', 
                                      showlegend=False
                                      )

            fig.add_trace(marker_chart, row=1, col=1)

        if in_state == 'bar':
            bar_chart = go.Bar(x=copy_in_df.index, 
                                   y=copy_in_df[infile_y], 
                                   name='내부파일', 
                                   showlegend=False
                                   )

            fig.add_trace(bar_chart, row=1, col=1)

        if in_state == 'plot':
            plot_chart = go.Scatter(x=copy_in_df.index, 
                                      y=copy_in_df[infile_y],
                                      mode='lines', 
                                      name='내부파일', 
                                      showlegend=False
                                      )

            fig.add_trace(plot_chart, row=1, col=1)

        if in_state == 'plot+marker':
            plot_marker_chart = go.Scatter(x=copy_in_df.index, 
                                      y=copy_in_df[infile_y],
                                      mode='lines+markers', 
                                      name='내부파일', 
                                      showlegend=False
                                      )

            fig.add_trace(plot_marker_chart, row=1, col=1)

        if in_state == 'candle':
            candle_chart = go.Candlestick(x=copy_in_df.index, 
                                        open=copy_in_df['open'], 
                                        high=copy_in_df['high'], 
                                        low=copy_in_df['low'], 
                                        close=copy_in_df['close'],
                                        increasing={'line':{'color':'red'}},
                                        decreasing={'line':{'color':'blue'}},
                                        name='내부파일',
                                        showlegend=False
                                        )

            fig.add_trace(candle_chart, row=1, col=1)

        # x축
        fig.update_xaxes(title_text=infile_x,
                        type='category',
                        categoryorder='category ascending',
                        tickangle=45,
                        row=1, col=1
                        )

        # y축
        fig.update_yaxes(title_text=infile_y, row=1, col=1)

        # 외부 그래프 타입
        if out_state == 'marker':
            marker_chart = go.Scatter(x=copy_out_df.index, 
                                      y=copy_out_df[outfile_y],
                                      mode='markers', 
                                      name='외부파일', 
                                      showlegend=False
                                      )

            fig.add_trace(marker_chart, row=2, col=1)

        if out_state == 'bar':
            bar_chart = go.Bar(x=copy_out_df.index, 
                                   y=copy_out_df[outfile_y], 
                                   name='외부파일', 
                                   showlegend=False
                                   )

            fig.add_trace(bar_chart, row=2, col=1)

        if out_state == 'plot':
            plot_chart = go.Scatter(x=copy_out_df.index, 
                                      y=copy_out_df[outfile_y],
                                      mode='lines', 
                                      name='외부파일', 
                                      showlegend=False
                                      )

            fig.add_trace(plot_chart, row=2, col=1)

        if out_state == 'plot+marker':
            plot_marker_chart = go.Scatter(x=copy_out_df.index, 
                                      y=copy_out_df[outfile_y],
                                      mode='lines+markers', 
                                      name='외부파일', 
                                      showlegend=False
                                      )

            fig.add_trace(plot_marker_chart, row=2, col=1)

        if out_state == 'candle':
            candle_chart = go.Candlestick(x=copy_out_df.index, 
                                        open=copy_out_df['open'], 
                                        high=copy_out_df['high'], 
                                        low=copy_out_df['low'], 
                                        close=copy_out_df['close'],
                                        increasing={'line':{'color':'red'}},
                                        decreasing={'line':{'color':'blue'}},
                                        name='외부파일'
                                        )

            fig.add_trace(candle_chart, row=2, col=1)

         # x축
        fig.update_xaxes(title_text=outfile_x,
                        type='category',
                        categoryorder='category ascending',
                        tickangle=45,
                        row=2, col=1
                        )

        # y축
        fig.update_yaxes(title_text=outfile_y, row=2, col=1)
        
        os.makedirs(f'{root_path}/graph', exist_ok=True)
        self.file_path = os.path.abspath(os.path.join(f'{root_path}/graph', "parallel_chart.html"))
        offline.plot(fig, filename=self.file_path, auto_open=False)
        self.load(QUrl.fromLocalFile(self.file_path))
        self.show()