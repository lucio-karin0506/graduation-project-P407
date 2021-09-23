from PySide2.QtWidgets import *
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QUrl

import pandas as pd
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

    def draw_graph(self, path, root_path, interval='', state='', 
                  period='', target='', 
                  nbdevup='', nbdevdn='',
                  fast_period='', slow_period='', signal_period='',
                  fastk_period='', fastd_period='',
                  slowk_period='', slowd_period='', target1='', target2='', target3='',
                  factor='',
                  num='', 
                  short='', long='', window_size='', signal='', 
                  multid=''
                  ):

        stock_file = os.path.split(path)        
        selected_stock_name = stock_file[1].replace('.csv', '')        
        stock_file = path.split('/')[-1]

        # 일봉 파일
        if selected_stock_name[-1] == 'd':
            if interval == 'd':
                pass
            elif interval == 'w':
                path = path.replace('_d', '_w')

        # 주봉 파일
        elif selected_stock_name[-1] == 'w':
            if interval == 'd':
                path = path.replace('_w', '_d')
            elif interval == 'w':
                pass
        
        # read stock data
        df = pd.read_csv(path)
        copy_df = copy.deepcopy(df)
        copy_df.set_index('Date', inplace=True)

        # figure setting
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.update_xaxes(title='Date',
                        type='category',
                        categoryorder='category ascending',
                        tickangle=45
                        )

        fig.update_yaxes(title='Price')

        # 주가 캔들 차트
        stock_candle = go.Candlestick(x=copy_df.index, 
                                open=copy_df['open'], 
                                high=copy_df['high'], 
                                low=copy_df['low'], 
                                close=copy_df['close'],
                                increasing={'line':{'color':'red'}},
                                decreasing={'line':{'color':'blue'}},
                                name='candle'
                                )

        # 거래량
        volume_chart = go.Bar(x=copy_df.index, y=copy_df['volume'],
                                showlegend=True,
                                name='거래량', yaxis='y2'
                                )
    
        fig.add_trace(stock_candle, secondary_y=False)
        fig.add_trace(volume_chart)

        # 기술적 지표
        # 이평선
        if state == 'ma':
            ma_chart  = go.Scatter(x=copy_df.index, y=copy_df[f'ma_{str(period)}({target})'], 
                                    mode='lines', name='ma_'+period, showlegend=True,
                                    line=go.scatter.Line(color='green')
                                    )
            fig.add_trace(ma_chart, row=1, col=1)

        # rsi
        if state == 'rsi':
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.1, row_heights=[0.7, 0.3])

            fig.update_xaxes(title='Date',
                        type='category',
                        categoryorder='category ascending',
                        tickangle=45
                        )

            fig.update_yaxes(title='Price')

            # 주가 차트
            stock_candle = go.Candlestick(x=copy_df.index, 
                                open=copy_df['open'], 
                                high=copy_df['high'], 
                                low=copy_df['low'], 
                                close=copy_df['close'],
                                increasing={'line':{'color':'red'}},
                                decreasing={'line':{'color':'blue'}},
                                name='candle'
                                )

            # rsi
            rsi_chart = go.Scatter(x=copy_df.index, y=copy_df[period], mode='lines', name=period, showlegend=True)

            fig.add_trace(stock_candle, row=1, col=1)
            fig.add_trace(rsi_chart, row=2, col=1)
            fig.update(layout_xaxis_rangeslider_visible=False)

        if state == 'macd':
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.1, row_heights=[0.7, 0.15, 0.15])

            fig.update_xaxes(title='Date',
                        type='category',
                        categoryorder='category ascending',
                        tickangle=45
                        )

            fig.update_yaxes(title='Price')

            # 주가 차트
            stock_candle = go.Candlestick(x=copy_df.index, 
                                open=copy_df['open'], 
                                high=copy_df['high'], 
                                low=copy_df['low'], 
                                close=copy_df['close'],
                                increasing={'line':{'color':'red'}},
                                decreasing={'line':{'color':'blue'}},
                                name='candle'
                                )

            macd_chart = go.Scatter(x=copy_df.index, y=copy_df['macd_' + str(fast_period) + '_' + str(slow_period) + '_' + str(signal_period)],
                                    mode='lines', name='MACD', showlegend=True)

            macd_signal_chart = go.Scatter(x=copy_df.index, y=copy_df['macd_signal_' + str(fast_period) + '_' + str(slow_period) + '_' + str(signal_period)],
                                    mode='lines', name='MACD Signal', showlegend=True)

            macd_oscillator = copy_df['macd_hist_' + str(fast_period) + '_' + str(slow_period) + '_' + str(signal_period)]
            macd_oscillator_bar1 = go.Bar(x=list(copy_df.index), y=macd_oscillator.where(list(macd_oscillator > 0)), 
                                        name='oscillator1', showlegend=True)
            macd_oscillator_bar2 = go.Bar(x=list(copy_df.index), y=macd_oscillator.where(list(macd_oscillator < 0)),
                                        name='oscillator2', showlegend=True)

            fig.add_trace(stock_candle, row=1, col=1)
            fig.add_trace(macd_chart, row=2, col=1)
            fig.add_trace(macd_signal_chart, row=2, col=1)
            fig.add_trace(macd_oscillator_bar1, row=3, col=1)
            fig.add_trace(macd_oscillator_bar2, row=3, col=1)
            fig.update(layout_xaxis_rangeslider_visible=False)

        if state == 'bb':
            bb_upper_chart = go.Scatter(x=copy_df.index, y=copy_df['ubb_' + period + '_' + nbdevup + '_' + nbdevdn],
                                        mode='lines', name='상한선', showlegend=True, line=go.scatter.Line(color='black'))
            bb_middle_chart = go.Scatter(x=copy_df.index, y=copy_df['mbb_' + period + '_' + nbdevup + '_' + nbdevdn],
                                        mode='lines', name='중심선', showlegend=True, line=go.scatter.Line(color='green'))
            bb_lower_chart = go.Scatter(x=copy_df.index, y=copy_df['lbb_' + period + '_' + nbdevup + '_' + nbdevdn],
                                        mode='lines', name='하한선', showlegend=True, line=go.scatter.Line(color='black'))

            fig.add_trace(bb_upper_chart, row=1, col=1)
            fig.add_trace(bb_middle_chart, row=1, col=1)
            fig.add_trace(bb_lower_chart, row=1, col=1)

        if state == 'ema':
            ema_chart  = go.Scatter(x=copy_df.index, y=copy_df[f'ema_{str(period)}({target})'], 
                                    mode='lines', name='ema_'+period, showlegend=True,
                                    line=go.scatter.Line(color='green')
                                    )
            fig.add_trace(ema_chart, row=1, col=1)

        if state == 'cmo':
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.1, row_heights=[0.7, 0.3])

            fig.update_xaxes(title='Date',
                        type='category',
                        categoryorder='category ascending',
                        tickangle=45
                        )

            fig.update_yaxes(title='Price')

            # 주가 차트
            stock_candle = go.Candlestick(x=copy_df.index, 
                                open=copy_df['open'], 
                                high=copy_df['high'], 
                                low=copy_df['low'], 
                                close=copy_df['close'],
                                increasing={'line':{'color':'red'}},
                                decreasing={'line':{'color':'blue'}},
                                name='candle'
                                )

            # cmo
            cmo_chart = go.Scatter(x=copy_df.index, y=copy_df[period], mode='lines', name=period, showlegend=True)

            fig.add_trace(stock_candle, row=1, col=1)
            fig.add_trace(cmo_chart, row=2, col=1)
            fig.update(layout_xaxis_rangeslider_visible=False)

        if state == 'stochf':
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.1, row_heights=[0.7, 0.3])

            fig.update_xaxes(title='Date',
                        type='category',
                        categoryorder='category ascending',
                        tickangle=45
                        )

            fig.update_yaxes(title='Price')

            # 주가 차트
            stock_candle = go.Candlestick(x=copy_df.index, 
                                open=copy_df['open'], 
                                high=copy_df['high'], 
                                low=copy_df['low'], 
                                close=copy_df['close'],
                                increasing={'line':{'color':'red'}},
                                decreasing={'line':{'color':'blue'}},
                                name='candle'
                                )

            # stochf
            stochf_k_chart = go.Scatter(x=copy_df.index, y=copy_df['fastk_'+str(fastk_period)+'_'+str(fastd_period)], 
                                    mode='lines', name='%K', showlegend=True)
            stochf_d_chart = go.Scatter(x=copy_df.index, y=copy_df['fastd_'+str(fastk_period)+'_'+str(fastd_period)], 
                                    mode='lines', name='%D', showlegend=True)

            fig.add_trace(stock_candle, row=1, col=1)
            fig.add_trace(stochf_k_chart, row=2, col=1)
            fig.add_trace(stochf_d_chart, row=2, col=1)
            fig.update(layout_xaxis_rangeslider_visible=False)

        if state == 'stoch':
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.1, row_heights=[0.7, 0.3])

            fig.update_xaxes(title='Date',
                        type='category',
                        categoryorder='category ascending',
                        tickangle=45
                        )

            fig.update_yaxes(title='Price')

            # 주가 차트
            stock_candle = go.Candlestick(x=copy_df.index, 
                                open=copy_df['open'], 
                                high=copy_df['high'], 
                                low=copy_df['low'], 
                                close=copy_df['close'],
                                increasing={'line':{'color':'red'}},
                                decreasing={'line':{'color':'blue'}},
                                name='candle'
                                )

            # stoch
            stoch_k_chart = go.Scatter(x=copy_df.index, 
                                        y=copy_df['slowk_'+str(fastk_period)+'_'+str(slowk_period)+'_'+str(slowd_period)], 
                                        mode='lines', name='%K', showlegend=True)
            stoch_d_chart = go.Scatter(x=copy_df.index, 
                                        y=copy_df['slowd_'+str(fastk_period)+'_'+str(slowk_period)+'_'+str(slowd_period)], 
                                        mode='lines', name='%D', showlegend=True)

            fig.add_trace(stock_candle, row=1, col=1)
            fig.add_trace(stoch_k_chart, row=2, col=1)
            fig.add_trace(stoch_d_chart, row=2, col=1)
            fig.update(layout_xaxis_rangeslider_visible=False)

        if state == 'atr':
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.1, row_heights=[0.7, 0.3])

            fig.update_xaxes(title='Date',
                        type='category',
                        categoryorder='category ascending',
                        tickangle=45
                        )

            fig.update_yaxes(title='Price')

            # 주가 차트
            stock_candle = go.Candlestick(x=copy_df.index, 
                                open=copy_df['open'], 
                                high=copy_df['high'], 
                                low=copy_df['low'], 
                                close=copy_df['close'],
                                increasing={'line':{'color':'red'}},
                                decreasing={'line':{'color':'blue'}},
                                name='candle'
                                )

            # atr
            atr_chart = go.Scatter(x=copy_df.index, y=copy_df['atr'+str(period)], mode='lines', name='atr_'+period, showlegend=True)

            fig.add_trace(stock_candle, row=1, col=1)
            fig.add_trace(atr_chart, row=2, col=1)
            fig.update(layout_xaxis_rangeslider_visible=False)

        if state == 'st':
            st_chart  = go.Scatter(x=copy_df.index, y=copy_df['st' + str(factor) + '_' + str(period)], 
                                    mode='lines', name='st_'+period, showlegend=True,
                                    line=go.scatter.Line(color='green')
                                    )
            fig.add_trace(st_chart, row=1, col=1)

        if state == 'cluster':
            high_centroid_chart  = go.Scatter(x=copy_df.index, y=copy_df['high_centroid'], 
                                    mode='lines', name='high_centroid', showlegend=True,
                                    line=go.scatter.Line(color='red')
                                    )
            low_centroid_chart  = go.Scatter(x=copy_df.index, y=copy_df['low_centroid'], 
                                    mode='lines', name='low_centroid', showlegend=True,
                                    line=go.scatter.Line(color='blue')
                                    )
            fig.add_trace(high_centroid_chart, row=1, col=1)
            fig.add_trace(low_centroid_chart, row=1, col=1)

        # label indicator
        if state == 'candle_type':
            candle_type_red_chart = go.Scatter(x=copy_df[copy_df['candle_type'] == 1].index, 
                                        y=copy_df[copy_df['candle_type'] == 1]['close'],
                                        mode='markers', name='양봉', showlegend=True, marker=dict(color='red')
                                        )
            candle_type_blue_chart = go.Scatter(x=copy_df[copy_df['candle_type'] == -1].index, 
                                        y=copy_df[copy_df['candle_type'] == -1]['close'], 
                                        mode='markers', name='음봉', showlegend=True, marker=dict(color='blue')
                                        )

            fig.add_trace(candle_type_red_chart, row=1, col=1)
            fig.add_trace(candle_type_blue_chart, row=1, col=1)

        if state == 'candle_shape':
            candle_shape_red_chart = go.Scatter(x=copy_df[copy_df['candle_shape'] == 1].index, 
                                        y=copy_df[copy_df['candle_shape'] == 1]['close'],
                                        mode='markers', name='장대양봉', showlegend=True, marker=dict(color='red')
                                        )
            candle_shape_blue_chart = go.Scatter(x=copy_df[copy_df['candle_shape'] == -1].index, 
                                        y=copy_df[copy_df['candle_shape'] == -1]['close'], 
                                        mode='markers', name='장대음봉', showlegend=True, marker=dict(color='blue')
                                        )

            fig.add_trace(candle_shape_red_chart, row=1, col=1)
            fig.add_trace(candle_shape_blue_chart, row=1, col=1)

        if state == 'three_red':
            three_red_chart = go.Scatter(x=copy_df[copy_df[f'three_red_{num}'] == 1].index, 
                                        y=copy_df[copy_df[f'three_red_{num}'] == 1]['close'],
                                        mode='markers', name='적삼병', showlegend=True, marker=dict(color='red')
                                        )

            fig.add_trace(three_red_chart, row=1, col=1)

        if state == 'three_blue':
            three_blue_chart = go.Scatter(x=copy_df[copy_df[f'three_blue_{num}'] == 1].index, 
                                        y=copy_df[copy_df[f'three_blue_{num}'] == 1]['close'],
                                        mode='markers', name='흑삼병', showlegend=True, marker=dict(color='blue')
                                        )

            fig.add_trace(three_blue_chart, row=1, col=1)

        if state == 'n_gap':
            gap_up_chart = go.Scatter(x=copy_df[copy_df[f'gap_{num}'] == 1].index, 
                                        y=copy_df[copy_df[f'gap_{num}'] == 1]['close'],
                                        mode='markers', name='갭 상승', showlegend=True, marker=dict(color='red')
                                        )
            gap_down_chart = go.Scatter(x=copy_df[copy_df[f'gap_{num}'] == -1].index, 
                                        y=copy_df[copy_df[f'gap_{num}'] == -1]['close'], 
                                        mode='markers', name='갭 하락', showlegend=True, marker=dict(color='blue')
                                        )

            fig.add_trace(gap_up_chart, row=1, col=1)
            fig.add_trace(gap_down_chart, row=1, col=1)

        if state == 'roc':
            roc_up_chart = go.Scatter(x=copy_df[copy_df[f'roc_classify_{period}({target})'] == 1].index, 
                                        y=copy_df[copy_df[f'roc_classify_{period}({target})'] == 1]['close'],
                                        mode='markers', name='plus', showlegend=True, marker=dict(color='red')
                                        )
            roc_down_chart = go.Scatter(x=copy_df[copy_df[f'roc_classify_{period}({target})'] == -1].index, 
                                        y=copy_df[copy_df[f'roc_classify_{period}({target})'] == -1]['close'], 
                                        mode='markers', name='minus', showlegend=True, marker=dict(color='blue')
                                        )

            fig.add_trace(roc_up_chart, row=1, col=1)
            fig.add_trace(roc_down_chart, row=1, col=1)

        if state == 'sma_cross':
            sma_up_chart = go.Scatter(x=copy_df[copy_df[f'sma_cross_{short}_{long}_{window_size}({target})'] == 1].index, 
                                        y=copy_df[copy_df[f'sma_cross_{short}_{long}_{window_size}({target})'] == 1]['close'],
                                        mode='markers', name='golden cross', showlegend=True, marker=dict(color='red')
                                        )
            sma_down_chart = go.Scatter(x=copy_df[copy_df[f'sma_cross_{short}_{long}_{window_size}({target})'] == -1].index, 
                                        y=copy_df[copy_df[f'sma_cross_{short}_{long}_{window_size}({target})'] == -1]['close'], 
                                        mode='markers', name='dead cross', showlegend=True, marker=dict(color='blue')
                                        )

            fig.add_trace(sma_up_chart, row=1, col=1)
            fig.add_trace(sma_down_chart, row=1, col=1)

        if state == 'dema_cross':
            dema_up_chart = go.Scatter(x=copy_df[copy_df[f'dema_cross_{short}_{long}_{window_size}({target})'] == 1].index, 
                                        y=copy_df[copy_df[f'dema_cross_{short}_{long}_{window_size}({target})'] == 1]['close'],
                                        mode='markers', name='golden cross', showlegend=True, marker=dict(color='red')
                                        )
            dema_down_chart = go.Scatter(x=copy_df[copy_df[f'dema_cross_{short}_{long}_{window_size}({target})'] == -1].index, 
                                        y=copy_df[copy_df[f'dema_cross_{short}_{long}_{window_size}({target})'] == -1]['close'], 
                                        mode='markers', name='dead cross', showlegend=True, marker=dict(color='blue')
                                        )

            fig.add_trace(dema_up_chart, row=1, col=1)
            fig.add_trace(dema_down_chart, row=1, col=1)

        if state == 'vwma_cross':
            vwma_up_chart = go.Scatter(x=copy_df[copy_df[f'vwma_cross_{short}_{long}_{window_size}({target})'] == 1].index, 
                                        y=copy_df[copy_df[f'vwma_cross_{short}_{long}_{window_size}({target})'] == 1]['close'],
                                        mode='markers', name='golden cross', showlegend=True, marker=dict(color='red')
                                        )
            vwma_down_chart = go.Scatter(x=copy_df[copy_df[f'vwma_cross_{short}_{long}_{window_size}({target})'] == -1].index, 
                                        y=copy_df[copy_df[f'vwma_cross_{short}_{long}_{window_size}({target})'] == -1]['close'], 
                                        mode='markers', name='dead cross', showlegend=True, marker=dict(color='blue')
                                        )

            fig.add_trace(vwma_up_chart, row=1, col=1)
            fig.add_trace(vwma_down_chart, row=1, col=1)

        if state == 'bb_label':
            bb_up_chart = go.Scatter(x=copy_df[copy_df[f'bbands_classify_{period}_{multid}({target})'] == 2].index, 
                                        y=copy_df[copy_df[f'bbands_classify_{period}_{multid}({target})'] == 2]['close'],
                                        mode='markers', name='상한선 이상', showlegend=True, marker=dict(color='black')
                                        )
            bb_middle_up_chart = go.Scatter(x=copy_df[copy_df[f'bbands_classify_{period}_{multid}({target})'] == 1].index, 
                                        y=copy_df[copy_df[f'bbands_classify_{period}_{multid}({target})'] == 1]['close'], 
                                        mode='markers', name='상한선 미만 중심선 이상', showlegend=True, marker=dict(color='yellow')
                                        )
            bb_middle_down_chart = go.Scatter(x=copy_df[copy_df[f'bbands_classify_{period}_{multid}({target})'] == -1].index, 
                                        y=copy_df[copy_df[f'bbands_classify_{period}_{multid}({target})'] == -1]['close'], 
                                        mode='markers', name='중심선 미만 하한선 이상', showlegend=True, marker=dict(color='yellow')
                                        )
            bb_down_chart = go.Scatter(x=copy_df[copy_df[f'bbands_classify_{period}_{multid}({target})'] == -2].index, 
                                        y=copy_df[copy_df[f'bbands_classify_{period}_{multid}({target})'] == -2]['close'],
                                        mode='markers', name='하한선 미만', showlegend=True, marker=dict(color='black')
                                        )

            fig.add_trace(bb_up_chart, row=1, col=1)
            fig.add_trace(bb_middle_up_chart, row=1, col=1)
            fig.add_trace(bb_middle_down_chart, row=1, col=1)
            fig.add_trace(bb_down_chart, row=1, col=1)

        if state == 'macd_label':
            macd_up_chart = go.Scatter(x=copy_df[copy_df[f'macd_classify_{short}_{long}({target})'] == 1].index, 
                                        y=copy_df[copy_df[f'macd_classify_{short}_{long}({target})'] == 1]['close'],
                                        mode='markers', name='plus', showlegend=True, marker=dict(color='red')
                                        )
            macd_down_chart = go.Scatter(x=copy_df[copy_df[f'macd_classify_{short}_{long}({target})'] == -1].index, 
                                        y=copy_df[copy_df[f'macd_classify_{short}_{long}({target})'] == -1]['close'], 
                                        mode='markers', name='minus', showlegend=True, marker=dict(color='blue')
                                        )

            fig.add_trace(macd_up_chart, row=1, col=1)
            fig.add_trace(macd_down_chart, row=1, col=1)

        if state == 'macd_cross':
            macd_cross_up_chart = go.Scatter(x=copy_df[copy_df[f'macd_cross_{short}_{long}_{signal}_{window_size}({target})'] == 1].index, 
                                        y=copy_df[copy_df[f'macd_cross_{short}_{long}_{signal}_{window_size}({target})'] == 1]['close'],
                                        mode='markers', name='golden cross', showlegend=True, marker=dict(color='red')
                                        )
            macd_cross_down_chart = go.Scatter(x=copy_df[copy_df[f'macd_cross_{short}_{long}_{signal}_{window_size}({target})'] == -1].index, 
                                        y=copy_df[copy_df[f'macd_cross_{short}_{long}_{signal}_{window_size}({target})'] == -1]['close'], 
                                        mode='markers', name='dead cross', showlegend=True, marker=dict(color='blue')
                                        )

            fig.add_trace(macd_cross_up_chart, row=1, col=1)
            fig.add_trace(macd_cross_down_chart, row=1, col=1)

        if state == 'stochf_label':
            stochf_up_chart = go.Scatter(x=copy_df[copy_df[f'stochf_cross_{fastk_period}_{fastd_period}_{window_size}'] == 1].index, 
                                        y=copy_df[copy_df[f'stochf_cross_{fastk_period}_{fastd_period}_{window_size}'] == 1]['close'],
                                        mode='markers', name='golden cross', showlegend=True, marker=dict(color='red')
                                        )
            stochf_down_chart = go.Scatter(x=copy_df[copy_df[f'stochf_cross_{fastk_period}_{fastd_period}_{window_size}'] == -1].index, 
                                        y=copy_df[copy_df[f'stochf_cross_{fastk_period}_{fastd_period}_{window_size}'] == -1]['close'], 
                                        mode='markers', name='dead cross', showlegend=True, marker=dict(color='blue')
                                        )

            fig.add_trace(stochf_up_chart, row=1, col=1)
            fig.add_trace(stochf_down_chart, row=1, col=1)

        if state == 'stoch_label':
            stoch_up_chart = go.Scatter(x=copy_df[copy_df[f'stoch_cross_{fastk_period}_{slowk_period}_{slowd_period}_{window_size}'] == 1].index, 
                                        y=copy_df[copy_df[f'stoch_cross_{fastk_period}_{slowk_period}_{slowd_period}_{window_size}'] == 1]['close'],
                                        mode='markers', name='golden cross', showlegend=True, marker=dict(color='red')
                                        )
            stoch_down_chart = go.Scatter(x=copy_df[copy_df[f'stoch_cross_{fastk_period}_{slowk_period}_{slowd_period}_{window_size}'] == -1].index, 
                                        y=copy_df[copy_df[f'stoch_cross_{fastk_period}_{slowk_period}_{slowd_period}_{window_size}'] == -1]['close'], 
                                        mode='markers', name='dead cross', showlegend=True, marker=dict(color='blue')
                                        )

            fig.add_trace(stoch_up_chart, row=1, col=1)
            fig.add_trace(stoch_down_chart, row=1, col=1)

        os.makedirs(f'{root_path}/graph', exist_ok=True)
        self.file_path = os.path.abspath(os.path.join(f'{root_path}/graph', "stock_chart.html"))        
        offline.plot(fig, filename=self.file_path, auto_open=False)
        self.load(QUrl.fromLocalFile(self.file_path))
        self.show()