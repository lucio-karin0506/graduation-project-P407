import PySide2
import sys
import os

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import QtCore

from module.handling_file import get_refined_path
from GUI.interface import stock_add_dialog, indicator_tree, stock_chart_graph_canvas

from GUI.interface.tech_indi_param_dialog import (ma_dialog, ema_dialog, cmo_dialog,
                                                rsi_dialog, bb_dialog, macd_dialog, stoch_fast_dialog,
                                                stoch_slow_dialog, atr_dialog, st_dialog, cluster_dialog)

from GUI.interface.label_indi_param_dialog import (bbands_label_dialog, candle_shape_dialog, candle_type_dialog,
                                                dema_cross_dialog, macd_cross_dialog, macd_label_dialog, n_gap_dialog,
                                                roc_dialog, sma_cross_dialog, stoch_label_dialog, stochf_label_dialog,
                                                three_blue_dialog, three_red_dialog, vwma_cross_dialog)

import warnings
warnings.filterwarnings('ignore')

'''
종목 차트 화면
'''
class stock_chart(QMainWindow):
    def __init__(self, root_path):
        QMainWindow.__init__(self)
        self.root_path = root_path
        self.title = '종목차트'
        self.left = 10
        self.top = 10
        self.width = 1200
        self.height = 900

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 메인 창 전체 레이아웃 위젯 변수 선언 및 중앙 배치
        widget = QWidget(self)
        self.setCentralWidget(widget)

        # 메인 창 전체 레이아웃 수평 정렬
        hlay = QHBoxLayout(widget)

        # 그래프 및 전체 위젯 가져오기
        m = stock_chart_editor(path=root_path)
        hlay.addWidget(m)


class stock_chart_editor(QWidget):
    def __init__(self, path, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self.root_path = path

        # Left Layout (종목 다운로드 버튼, 종목 폴더, 지표 리스트)
        leftLayout = QVBoxLayout()

        # 종목 다운로드 버튼
        self.stock_button = QPushButton('종목다운로드')
        self.stock_button.clicked.connect(self.get_stock_dialog)

        # 파일불러오기 버튼
        self.stock_select_button = QPushButton('파일불러오기')
        self.stock_select_button.clicked.connect(self.get_stock_file)

        # 지표 리스트 위젯
        self.indi_label = QLabel('지표')
        self.indi_tree = indicator_tree.IndicatorTreeView()

        leftLayout.addWidget(self.stock_button)
        leftLayout.addWidget(self.stock_select_button)
        leftLayout.addWidget(self.indi_label)
        leftLayout.addWidget(self.indi_tree)

        # Center Layout (차트 캔버스)
        centerLayout = QVBoxLayout()

        self.setAcceptDrops(True)
        self.canvas = stock_chart_graph_canvas.PlotCanvas()

        self.cb_option = QComboBox(self)
        self.cb_option.addItem('일봉', 'd')
        self.cb_option.addItem('주봉', 'w')
        self.cb_option.currentTextChanged.connect(self.change_subplot)
        
        self.scroll = QScrollArea()
        mini_vlay = QVBoxLayout()
        mini_hlay = QHBoxLayout()

        mini_hlay.addWidget(self.cb_option)
        
        mini_vlay.addLayout(mini_hlay)
        mini_vlay.addWidget(self.canvas)

        self.scroll.setLayout(mini_vlay)

        centerLayout.addWidget(self.scroll)

        # Right Layout (봉 타입 콤보박스, 지표 & 레이블 리스트 위젯, 지표 추가 버튼)
        rightLayout = QVBoxLayout()

        # 기술적 지표 리스트 박스
        self.tech_list_label = QLabel('기술적 지표')
        self.tech_list = QListWidget()
        self.tech_list.addItems(['이동평균', 'RSI', 'MACD', 'BollingerBand', 'Stochastic Fast', 'Stochastic Slow',
                                 'EMA', 'CMO', 'ATR', 'SuperTrend', 'Clustering'])

        self.tech_list_button = QPushButton('추가')
        self.tech_list_button.clicked.connect(self.get_tech_indi_param_dialog)

        # 레이블 지표 리스트 박스
        self.label_list_label = QLabel('레이블 지표')
        self.label_list = QListWidget()
        self.label_list.addItems(['캔들 종류', '캔들 모양', '적삼병', '흑삼병', '갭 상승/하락', '가격 변화 비율', '단순이동평균 Cross',
                                  '이중지수이동평균 Cross', '거래량가중이동평균 Cross', 'MACD', 'BollingerBand', 'MACD Cross',
                                  'Stochastic Fast Cross', 'Stochastic Slow Cross'])

        self.label_list_button = QPushButton('추가')
        self.label_list_button.clicked.connect(self.get_label_indi_param_dialog)

        rightLayout.addWidget(self.tech_list_label)
        rightLayout.addWidget(self.tech_list)
        rightLayout.addWidget(self.tech_list_button)
        rightLayout.addStretch(2)
        rightLayout.addWidget(self.label_list_label)
        rightLayout.addWidget(self.label_list)
        rightLayout.addWidget(self.label_list_button)

        rightLayout.addStretch(1)

        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(centerLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 0)
        layout.setStretchFactor(centerLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)

    # 파일 불러오기 버튼 이벤트
    def get_stock_file(self):
        basePath = QFileDialog.getOpenFileName(self, caption='종목파일', dir=self.root_path)
        self.stock_path = basePath[0]        
        
        stock_file = os.path.split(self.stock_path)
        selected_stock_name = stock_file[1].replace('.csv', '')

        # 일봉 csv 파일 선택 시 일봉 차트
        if selected_stock_name[-1] == 'd':
            self.canvas.draw_graph(self.stock_path,
                                root_path=self.root_path,
                                interval='d')

        # 주봉 csv 파일 선택 시 주봉 차트
        elif selected_stock_name[-1] == 'w':
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                interval='w')

        # 지표 리스트 박스에 파일 경로 정보 전달
        self.indi_tree.get_path(self.stock_path)

    # 차트 일, 주봉 변환
    def change_subplot(self):
        # 일봉 콤보 아이템 선택 시 일봉 차트
        if self.cb_option.currentData() == 'd':            
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                interval='d')

        # 주봉 콤보 아이템 선택 시 주봉 차트
        elif self.cb_option.currentData() == 'w':            
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                interval='w')

    # 종목 추가 버튼 클릭 시 종목 추가 다이얼로그 이동
    def get_stock_dialog(self):
        dialog = stock_add_dialog.stock_add(self.root_path)
        dialog.showModal()

    # 기술적 지표 리스트 박스에서 지표 클릭 시 다이얼로그 이동
    def get_tech_indi_param_dialog(self):
        row = self.tech_list.currentRow()
        item = self.tech_list.item(row)

        if item.text() == '이동평균':
            dialog = ma_dialog.ma_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 지표 목록 추가
            self.ma_target = dialog.price_option.currentData()
            self.ma_period = 'ma_' + dialog.period_edit.text() + f'({self.ma_target})'
            self.ma = QTreeWidgetItem([self.ma_period])
            self.indi_tree.item_ma.addChild(self.ma)

            # 그래프 추가
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='ma', period=str(dialog.period_edit.text()), target=str(self.ma_target))

        elif item.text() == 'RSI':
            dialog = rsi_dialog.rsi_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 지표 목록 추가
            self.rsi_period = 'rsi_' + dialog.period_edit.text()
            self.rsi = QTreeWidgetItem([self.rsi_period])
            self.indi_tree.item_rsi.addChild(self.rsi)

            # 그래프 추가
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='rsi', period=str(self.rsi_period))

        elif item.text() == 'MACD':
            dialog = macd_dialog.macd_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 지표 목록 추가
            self.fast_period = dialog.fast_edit.text()
            self.slow_period = dialog.slow_edit.text()
            self.signal_period = dialog.signal_edit.text()

            self.macd_origin = 'macd_' + self.fast_period + '_' + self.slow_period + '_' + self.signal_period
            self.macd_signal = 'macd_signal_' + self.fast_period + '_' + self.slow_period + '_' + self.signal_period
            self.macd_hist = 'macd_hist_' + self.fast_period + '_' + self.slow_period + '_' + self.signal_period

            self.macd_origin_item = QTreeWidgetItem([self.macd_origin])
            self.macd_signal_item = QTreeWidgetItem([self.macd_signal])
            self.macd_hist_item = QTreeWidgetItem([self.macd_hist])

            self.indi_tree.item_macd.addChild(self.macd_origin_item)
            self.indi_tree.item_macd.addChild(self.macd_signal_item)
            self.indi_tree.item_macd.addChild(self.macd_hist_item)

            # 그래프 추가
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='macd', fast_period=str(self.fast_period), slow_period=str(self.slow_period), signal_period=str(self.signal_period))

        elif item.text() == 'BollingerBand':
            dialog = bb_dialog.bb_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 지표 목록 추가
            self.bb_period = dialog.period_edit.text()
            self.nbdevup = dialog.up_edit.text()
            self.nbdevdn = dialog.down_edit.text()

            self.bb_ubb = 'ubb_' + self.bb_period + '_' + self.nbdevup + '_' + self.nbdevdn
            self.bb_mbb = 'mbb_' + self.bb_period + '_' + self.nbdevup + '_' + self.nbdevdn
            self.bb_lbb = 'lbb_' + self.bb_period + '_' + self.nbdevup + '_' + self.nbdevdn

            self.bb_ubb_item = QTreeWidgetItem([self.bb_ubb])
            self.bb_mbb_item = QTreeWidgetItem([self.bb_mbb])
            self.bb_lbb_item = QTreeWidgetItem([self.bb_lbb])

            self.indi_tree.item_bb.addChild(self.bb_ubb_item)
            self.indi_tree.item_bb.addChild(self.bb_mbb_item)
            self.indi_tree.item_bb.addChild(self.bb_lbb_item)

            # 그래프 추가
            self.canvas.draw_graph(self.stock_path,
                                self.root_path,
                                state='bb', period=str(self.bb_period), nbdevup=str(self.nbdevup),
                                nbdevdn=str(self.nbdevdn))

        elif item.text() == 'Stochastic Fast':
            dialog = stoch_fast_dialog.stoch_fast_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 지표 목록 추가
            self.fastk = dialog.fastk_edit.text()
            self.fastd = dialog.fastd_edit.text()

            self.stochf_fastk = 'fastk_' + self.fastk + '_' + self.fastd
            self.stochf_fastd = 'fastk_' + self.fastk + '_' + self.fastd

            self.stochf_fastk_item = QTreeWidgetItem([self.stochf_fastk])
            self.stochf_fastd_item = QTreeWidgetItem([self.stochf_fastd])

            self.indi_tree.item_stochf.addChild(self.stochf_fastk_item)
            self.indi_tree.item_stochf.addChild(self.stochf_fastd_item)

            # 그래프 추가
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='stochf', fastk_period=str(self.fastk), 
                                fastd_period=str(self.fastd))

        elif item.text() == 'Stochastic Slow':
            dialog = stoch_slow_dialog.stoch_slow_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 지표 목록 추가
            self.stoch_fastk = dialog.fastk_edit.text()
            self.slowk = dialog.slowk_edit.text()
            self.slowd = dialog.slowd_edit.text()

            self.stoch_slowk = 'slowk_' + self.stoch_fastk + '_' + self.slowk + '_' + self.slowd
            self.stoch_slowd = 'slowd_' + self.stoch_fastk + '_' + self.slowk + '_' + self.slowd

            self.stoch_slowk_item = QTreeWidgetItem([self.stoch_slowk])
            self.stoch_slowd_item = QTreeWidgetItem([self.stoch_slowd])

            self.indi_tree.item_stochs.addChild(self.stoch_slowk_item)
            self.indi_tree.item_stochs.addChild(self.stoch_slowd_item)

            # 그래프 추가
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='stoch', fastk_period=str(self.stoch_fastk), 
                                slowk_period=str(self.slowk), slowd_period=str(self.slowd))

        elif item.text() == 'EMA':
            dialog = ema_dialog.ema_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 지표 목록 추가
            self.ema_target = dialog.price_option.currentData()
            self.ema_period = 'ema_' + dialog.period_edit.text() + f'({self.ema_target})'
            self.ema = QTreeWidgetItem([self.ema_period])
            self.indi_tree.item_ema.addChild(self.ema)

            # 그래프 추가
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='ema', period=dialog.period_edit.text(), target=str(self.ema_target))

        elif item.text() == 'CMO':
            dialog = cmo_dialog.cmo_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 지표 목록 추가
            self.cmo_period = 'cmo_' + dialog.period_edit.text()
            self.cmo = QTreeWidgetItem([self.cmo_period])
            self.indi_tree.item_cmo.addChild(self.cmo)

            # 그래프 추가
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='cmo', period=str(self.cmo_period))

        elif item.text() == 'ATR':
            dialog = atr_dialog.atr_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 지표 목록 추가
            self.atr_period = 'atr' + dialog.period_edit.text()
            self.atr = QTreeWidgetItem([self.atr_period])
            self.indi_tree.item_atr.addChild(self.atr)

            # 그래프 추가
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='atr', period=dialog.period_edit.text())

        elif item.text() == 'SuperTrend':
            dialog = st_dialog.st_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 지표 목록 추가
            self.st_period = dialog.period_edit.text()
            self.st_factor = dialog.factor_edit.text()

            self.st_param = 'SuperTrend_' + self.st_factor + '_' + self.st_period

            self.st = QTreeWidgetItem([self.st_param])
            self.indi_tree.item_st.addChild(self.st)

            # 그래프 추가
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='st', period=self.st_period, factor=self.st_factor)

        elif item.text() == 'Clustering':
            dialog = cluster_dialog.cluster_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 지표 목록 추가
            self.n_clusters = dialog.n_clusters_edit.text()
            self.target = dialog.target_option.currentData()
            self.period = dialog.period_edit.text()
            self.slide_size = dialog.slide_size_edit.text()

            self.high_cluster = 'high_centroid' + '_' + str(self.n_clusters) + '_' + str(self.target) + '_' + \
                str(self.period) + '_' + str(self.slide_size)

            self.low_cluster = 'low_centroid' + '_' + str(self.n_clusters) + '_' + str(self.target) + '_' + \
                str(self.period) + '_' + str(self.slide_size)

            self.high_cluster_item = QTreeWidgetItem([self.high_cluster])
            self.low_cluster_item = QTreeWidgetItem([self.low_cluster])

            self.indi_tree.item_cluster.addChild(self.high_cluster_item)
            self.indi_tree.item_cluster.addChild(self.low_cluster_item)

            # 그래프 추가
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='cluster')

    # 레이블 지표 리스트 박스에서 지표 클릭 시 다이얼로그 이동
    def get_label_indi_param_dialog(self):
        row = self.label_list.currentRow()
        item = self.label_list.item(row)
        
        if item.text() == '캔들 종류':
            candle_type_dialog.confirmIt(self.stock_path)
            QMessageBox.information(self, "메시지", "파라미터 설정이 완료되었습니다!", QMessageBox.Yes)

            # 지표 리스트 지표 추가
            self.candle_type_item = QTreeWidgetItem(['candle_type'])
            self.indi_tree.item_candle_type.addChild(self.candle_type_item)

            # 그래프
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='candle_type')

        elif item.text() == '캔들 모양':
            candle_shape_dialog.confirmIt(self.stock_path)
            QMessageBox.information(self, "메시지", "파라미터 설정이 완료되었습니다!", QMessageBox.Yes)

            # 지표 리스트 지표 추가
            self.candle_shape_item = QTreeWidgetItem(['candle_shape'])
            self.indi_tree.item_candle_shape.addChild(self.candle_shape_item)

            # graph
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='candle_shape')

        elif item.text() == '적삼병':
            dialog1 = three_red_dialog.three_red_Param(item.text(), self.stock_path, self)
            dialog1.showModal()

            # 지표 리스트 추가
            self.three_red_num = dialog1.num_edit.text()
            self.three_red_item = QTreeWidgetItem([f'three_red_{str(self.three_red_num)}'])
            self.indi_tree.item_3red.addChild(self.three_red_item)

            # graph
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='three_red', num=int(self.three_red_num))

        elif item.text() == '흑삼병':
            dialog1 = three_blue_dialog.three_blue_Param(item.text(), self.stock_path, self)
            dialog1.showModal()

            # 지표 리스트 추가
            self.three_blue_num = dialog1.num_edit.text()
            self.three_blue_item = QTreeWidgetItem([f'three_blue_{str(self.three_blue_num)}'])
            self.indi_tree.item_3blue.addChild(self.three_blue_item)

            # graph
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='three_blue', num=int(self.three_blue_num))

        elif item.text() == '갭 상승/하락':
            dialog = n_gap_dialog.ngap_label_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 추가
            self.ngap_colName = dialog.num_edit.text()
            self.ngap_num_item = QTreeWidgetItem(['gap_' + str(self.ngap_colName)])
            self.indi_tree.item_ngap.addChild(self.ngap_num_item)

            # graph
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='n_gap', num=int(self.ngap_colName) / 100)

        elif item.text() == '가격 변화 비율':
            dialog = roc_dialog.roc_label_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 추가
            self.roc_prevDay = dialog.period_edit.text()
            self.roc_target = dialog.target_option.currentData()

            self.roc_colName = f'roc_classify_{str(self.roc_prevDay)}({str(self.roc_target)})'

            self.roc_param_item = QTreeWidgetItem([self.roc_colName])
            self.indi_tree.item_roc.addChild(self.roc_param_item)

            # graph
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='roc', period=int(self.roc_prevDay), target=str(self.roc_target))

        elif item.text() == '단순이동평균 Cross':
            dialog = sma_cross_dialog.sma_cross_label_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 추가
            self.sma_short = dialog.short_period_edit.text()
            self.sma_long = dialog.long_period_edit.text()
            self.sma_win_size = dialog.window_size_edit.text()
            self.sma_target = dialog.target_option.currentData()

            self.sma_colName = f'sma_cross_{str(self.sma_short)}_{str(self.sma_long)}_{str(self.sma_win_size)}({str(self.sma_target)})'

            self.sma_param_item = QTreeWidgetItem([self.sma_colName])
            self.indi_tree.item_sma_cross.addChild(self.sma_param_item)

            # graph
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='sma_cross', short=int(self.sma_short), long=int(self.sma_long),
                                window_size=int(self.sma_win_size), target=str(self.sma_target))

        elif item.text() == '이중지수이동평균 Cross':
            dialog = dema_cross_dialog.dema_cross_label_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 추가
            self.dema_short = dialog.short_period_edit.text()
            self.dema_long = dialog.long_period_edit.text()
            self.dema_win_size = dialog.window_size_edit.text()
            self.dema_target = dialog.target_option.currentData()

            self.dema_colName = f'dema_cross_{str(self.dema_short)}_{str(self.dema_long)}_{str(self.dema_win_size)}({str(self.dema_target)})'

            self.dema_param_item = QTreeWidgetItem([self.dema_colName])
            self.indi_tree.item_dema_cross.addChild(self.dema_param_item)

            # graph
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='dema_cross', short=int(self.dema_short), long=int(self.dema_long),
                                window_size=int(self.dema_win_size), target=str(self.dema_target))

        elif item.text() == '거래량가중이동평균 Cross':
            dialog = vwma_cross_dialog.vwma_cross_label_param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 추가
            self.vwma_short = dialog.short_period_edit.text()
            self.vwma_long = dialog.long_period_edit.text()
            self.vwma_win_size = dialog.window_size_edit.text()
            self.vwma_target = dialog.target_option.currentData()

            self.vwma_colName = f'vwma_cross_{str(self.vwma_short)}_{str(self.vwma_long)}_{str(self.vwma_win_size)}({str(self.vwma_target)})'

            self.vwma_param_item = QTreeWidgetItem([self.vwma_colName])
            self.indi_tree.item_vwma_cross.addChild(self.vwma_param_item)

            # graph
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='vwma_cross', short=int(self.vwma_short), long=int(self.vwma_long),
                                window_size=int(self.vwma_win_size), target=str(self.vwma_target))

        elif item.text() == 'MACD':
            dialog = macd_label_dialog.macd_label_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 추가
            self.macdlb_short = dialog.short_period_edit.text()
            self.macdlb_long = dialog.long_period_edit.text()
            self.macdlb_target = dialog.target_option.currentData()

            self.macdlb_colName = f'macd_classify_{str(self.macdlb_short)}_{str(self.macdlb_long)}({str(self.macdlb_target)})'

            self.macdlb_param_item = QTreeWidgetItem([self.macdlb_colName])
            self.indi_tree.item_macd_label.addChild(self.macdlb_param_item)

            # graph
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='macd_label', short=int(self.macdlb_short), long=int(self.macdlb_long),
                                target=str(self.macdlb_target))

        elif item.text() == 'BollingerBand':
            dialog = bbands_label_dialog.bbands_label_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 추가
            self.bblb_period = dialog.period_edit.text()
            self.bblb_multid = dialog.multid_edit.text()
            self.bblb_target = dialog.target_option.currentData()

            self.bblb_colName = f'bbands_classify_{str(self.bblb_period)}_{str(self.bblb_multid)}({str(self.bblb_target)})'

            self.bblb_param_item = QTreeWidgetItem([self.bblb_colName])
            self.indi_tree.item_bb_label.addChild(self.bblb_param_item)

            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='bb_label', period=int(self.bblb_period), multid=int(self.bblb_multid),
                                target=str(self.bblb_target))

        elif item.text() == 'MACD Cross':
            dialog = macd_cross_dialog.macd_cross_label_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 추가
            self.macdCross_short = dialog.short_period_edit.text()
            self.macdCross_long = dialog.long_period_edit.text()
            self.macdCross_signal = dialog.signal_period_edit.text()
            self.macdCross_winSize = dialog.win_size_edit.text()
            self.macdCross_target = dialog.target_option.currentData()

            self.macdCross_colName = f'macd_cross_{str(self.macdCross_short)}_' \
                                     f'{str(self.macdCross_long)}_{str(self.macdCross_signal)}' \
                                     f'_{str(self.macdCross_winSize)}({str(self.macdCross_target)})'

            self.macdCross_param_item = QTreeWidgetItem([self.macdCross_colName])
            self.indi_tree.item_macd_cross.addChild(self.macdCross_param_item)

            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='macd_cross', short=int(self.macdCross_short), long=int(self.macdCross_long),
                                signal=int(self.macdCross_signal), window_size=int(self.macdCross_winSize),
                                target=str(self.macdCross_target))

        elif item.text() == 'Stochastic Fast Cross':
            dialog = stochf_label_dialog.stoch_fast_label_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 추가
            self.stochflb_fastk = dialog.fastk_period_edit.text()
            self.stochflb_fastd = dialog.fastd_period_edit.text()
            self.stochflb_window = dialog.window_edit.text()

            self.stochflb_colName = f'stochf_cross_{str(self.stochflb_fastk)}_{str(self.stochflb_fastd)}_{str(self.stochflb_window)}'

            self.stochflb_param_item = QTreeWidgetItem([self.stochflb_colName])
            self.indi_tree.item_stochf_label.addChild(self.stochflb_param_item)

            # graph
            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='stochf_label', fastk_period=int(self.stochflb_fastk),
                                fastd_period=int(self.stochflb_fastd), window_size=int(self.stochflb_window))

        elif item.text() == 'Stochastic Slow Cross':
            dialog = stoch_label_dialog.stochastic_slow_label_Param(item.text(), self.stock_path, self)
            dialog.showModal()

            # 지표 리스트 추가
            self.stochlb_fastk = dialog.fastk_period_edit.text()
            self.stochlb_slowk = dialog.slowk_period_edit.text()
            self.stochlb_slowd = dialog.slowd_period_edit.text()
            self.stochlb_window = dialog.window_edit.text()

            self.stochlb_colName = f'stoch_cross_{str(self.stochlb_fastk)}_{str(self.stochlb_slowk)}_{str(self.stochlb_slowd)}_{str(self.stochlb_window)}'

            self.stochlb_param_item = QTreeWidgetItem([self.stochlb_colName])
            self.indi_tree.item_stochs_label.addChild(self.stochlb_param_item)

            self.canvas.draw_graph(path=self.stock_path,
                                root_path=self.root_path,
                                state='stoch_label', fastk_period=int(self.stochlb_fastk),
                                slowk_period=int(self.stochlb_slowk), slowd_period=int(self.stochlb_slowd), window_size=int(self.stochlb_window))


sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = stock_chart()
    mainWin.show()
    sys.exit(app.exec_())