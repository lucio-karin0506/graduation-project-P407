import PySide2
from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

import os
import sys
import pandas as pd
import json
import FinanceDataReader as fdr

from GUI.interface import simple_strategy_chart_dialog
from module.order_creator.order_creator import OrderCreator

'''
주문 생성 화면
1. 주문 생성 에디터
2. 디버그 로깅 창
'''
class simple_strategy(QMainWindow):
    def __init__(self, root_path):
        QMainWindow.__init__(self)
        self.root_path = root_path
        self.title = '단순전략'
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
        vlay = QVBoxLayout(widget)

        # 주문 생성 에디터 위젯 가져오기
        order_create = order_editor(self.root_path)
        vlay1 = QVBoxLayout()
        vlay1.addWidget(order_create)
        vlay.addLayout(vlay1)


class order_editor(QWidget):
    def __init__(self, root_path, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.root_path = root_path

        #전체 레이아웃
        layout = QHBoxLayout()

        # Left Layout(데이터 불러오기 옵션 라디오버튼, directory tree, 지표 리스트)
        leftLayout = QVBoxLayout()

        # 데이터 불러오는 옵션 라디오 버튼
        optionLayout = QHBoxLayout()
        self.local_Mode = QRadioButton('로컬파일모드')
        self.local_Mode.setChecked(True)
        self.net_Mode = QRadioButton('네트워크모드')
        self.net_Mode.setChecked(False)
        self.net_Mode.toggled.connect(self.netModeLayout)
        optionLayout.addWidget(self.local_Mode)
        optionLayout.addWidget(self.net_Mode)

        self.indi_label = QLabel('지표')

        # 네트워크 모드일 시 제공하는 모든 지표 표시하도록 함.
        self.indi_display_tree = QTreeWidget()
        self.indi_display_tree.setAlternatingRowColors(True)
        self.indi_display_tree.header().setVisible(False)
        self.indi_display_tree.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.indi_display_tree.header().setStretchLastSection(False)

        stock_tech_indi = QTreeWidgetItem(['기술적지표'])
        self.indi_display_tree.addTopLevelItem(stock_tech_indi)

        self.item_ma = QTreeWidgetItem(stock_tech_indi)
        self.item_ma.setText(0, '이동평균')
        self.item_ma_ex = QTreeWidgetItem(self.item_ma)
        self.item_ma_ex.setText(0, 'MA(period=10)')

        self.item_rsi = QTreeWidgetItem(stock_tech_indi)
        self.item_rsi.setText(0, 'RSI')
        self.item_rsi_ex = QTreeWidgetItem(self.item_rsi)
        self.item_rsi_ex.setText(0, 'RSI(period=14)')

        self.item_macd = QTreeWidgetItem(stock_tech_indi)
        self.item_macd.setText(0, 'MACD')
        self.item_macd_ex = QTreeWidgetItem(self.item_macd)
        self.item_macd_ex.setText(0, 'MACD(fast_period=12, slow_period=26, signal_period=9)')

        self.item_bb = QTreeWidgetItem(stock_tech_indi)
        self.item_bb.setText(0, 'BollingerBand')
        self.item_bb_ex = QTreeWidgetItem(self.item_bb)
        self.item_bb_ex.setText(0, 'BBands(period=20, nbdevup=2, nbdevdn=2)')

        self.item_stochf = QTreeWidgetItem(stock_tech_indi)
        self.item_stochf.setText(0, 'Stochastic Fast')
        self.item_stochf_ex = QTreeWidgetItem(self.item_stochf)
        self.item_stochf_ex.setText(0, "STOCHF(fastk_period=5, fastd_period=3, target1='high', target2='low', target3='close')")

        self.item_stochs = QTreeWidgetItem(stock_tech_indi)
        self.item_stochs.setText(0, 'Stochastic Slow')
        self.item_stochs_ex = QTreeWidgetItem(self.item_stochs)
        self.item_stochs_ex.setText(0, "STOCH(fastk_period=5, slowk_period=3, slowd_period=3, target1='high', target2='low', target3='close')")

        self.item_ema = QTreeWidgetItem(stock_tech_indi)
        self.item_ema.setText(0, 'EMA')
        self.item_ema_ex = QTreeWidgetItem(self.item_ema)
        self.item_ema_ex.setText(0, 'EMA(period=30)')

        self.item_cmo = QTreeWidgetItem(stock_tech_indi)
        self.item_cmo.setText(0, 'CMO')
        self.item_cmo_ex = QTreeWidgetItem(self.item_cmo)
        self.item_cmo_ex.setText(0, 'CMO(period=14)')

        self.item_atr = QTreeWidgetItem(stock_tech_indi)
        self.item_atr.setText(0, 'ATR')
        self.item_atr_ex = QTreeWidgetItem(self.item_atr)
        self.item_atr_ex.setText(0, 'ATR(period=14)')

        self.item_st = QTreeWidgetItem(stock_tech_indi)
        self.item_st.setText(0, 'SuperTrend')
        self.item_st_ex = QTreeWidgetItem(self.item_st)
        self.item_st_ex.setText(0, 'ST(factor=3, period=14)')

        self.item_cluster = QTreeWidgetItem(stock_tech_indi)
        self.item_cluster.setText(0, 'Clustering')
        self.item_cluster_ex = QTreeWidgetItem(self.item_cluster)
        self.item_cluster_ex.setText(0, 'clustering(n_clusters=2, target="close", period="1y", slide_size="1m")')

        #--------------------------------------------------------------------------------------------------------------
        stock_label_indi = QTreeWidgetItem(['레이블지표'])
        self.indi_display_tree.addTopLevelItem(stock_label_indi)

        self.item_candle_type = QTreeWidgetItem(stock_label_indi)
        self.item_candle_type.setText(0, '캔들 종류')
        self.item_candle_type_ex = QTreeWidgetItem(self.item_candle_type)
        self.item_candle_type_ex.setText(0, 'candle_type()')

        self.item_candle_shape = QTreeWidgetItem(stock_label_indi)
        self.item_candle_shape.setText(0, '캔들 모양')
        self.item_candle_shape_ex = QTreeWidgetItem(self.item_candle_shape)
        self.item_candle_shape_ex.setText(0, 'candle_shape()')

        self.item_3red = QTreeWidgetItem(stock_label_indi)
        self.item_3red.setText(0, '적삼병')
        self.item_3red_ex = QTreeWidgetItem(self.item_3red)
        self.item_3red_ex.setText(0, 'three_red(num=3)')

        self.item_3blue = QTreeWidgetItem(stock_label_indi)
        self.item_3blue.setText(0, '흑삼병')
        self.item_3blue_ex = QTreeWidgetItem(self.item_3blue)
        self.item_3blue_ex.setText(0, 'three_blue(num=3)')

        self.item_ngap = QTreeWidgetItem(stock_label_indi)
        self.item_ngap.setText(0, '갭 상승/하락')
        self.item_ngap_ex = QTreeWidgetItem(self.item_ngap)
        self.item_ngap_ex.setText(0, 'n_gap(num=0)')

        self.item_roc = QTreeWidgetItem(stock_label_indi)
        self.item_roc.setText(0, '가격 변화 비율')
        self.item_roc_ex = QTreeWidgetItem(self.item_roc)
        self.item_roc_ex.setText(0, 'roc_classify(period=12, target="close")')

        self.item_sma_cross = QTreeWidgetItem(stock_label_indi)
        self.item_sma_cross.setText(0, '단순이동평균 Cross')
        self.item_sma_cross_ex = QTreeWidgetItem(self.item_sma_cross)
        self.item_sma_cross_ex.setText(0, 'sma_cross(short=5, long=20, window_size=0, target="close")')

        self.item_dema_cross = QTreeWidgetItem(stock_label_indi)
        self.item_dema_cross.setText(0, '이중지수이동평균 Cross')
        self.item_dema_cross_ex = QTreeWidgetItem(self.item_dema_cross)
        self.item_dema_cross_ex.setText(0, 'dema_cross(short=5, long=20, window_size=0, target="close")')

        self.item_vwma_cross = QTreeWidgetItem(stock_label_indi)
        self.item_vwma_cross.setText(0, '거래량가중이동평균 Cross')
        self.item_vwma_cross_ex = QTreeWidgetItem(self.item_vwma_cross)
        self.item_vwma_cross_ex.setText(0, 'vwma_cross(short=5, long=20, window_size=0, target="close")')

        self.item_macd_label = QTreeWidgetItem(stock_label_indi)
        self.item_macd_label.setText(0, 'MACD')
        self.item_macd_label_ex = QTreeWidgetItem(self.item_macd_label)
        self.item_macd_label_ex.setText(0, 'macd_classify(short=12, long=26, target="close")')

        self.item_bb_label = QTreeWidgetItem(stock_label_indi)
        self.item_bb_label.setText(0, 'BollingerBand')
        self.item_bb_label_ex = QTreeWidgetItem(self.item_bb_label)
        self.item_bb_label_ex.setText(0, 'bbands_classify(period=20, multid=2, target="close")')

        self.item_macd_cross = QTreeWidgetItem(stock_label_indi)
        self.item_macd_cross.setText(0, 'MACD Cross')
        self.item_macd_cross_ex = QTreeWidgetItem(self.item_macd_cross)
        self.item_macd_cross_ex.setText(0, 'macd_cross(short=12, long=26, signal=9, window_size=0, target="close")')

        self.item_stochf_label = QTreeWidgetItem(stock_label_indi)
        self.item_stochf_label.setText(0, 'Stochastic Fast Cross')
        self.item_stochf_label_ex = QTreeWidgetItem(self.item_stochf_label)
        self.item_stochf_label_ex.setText(0, 'stochf_cross(fastk_period=5, fastd_period=3, window_size=0)')

        self.item_stochs_label = QTreeWidgetItem(stock_label_indi)
        self.item_stochs_label.setText(0, 'Stochastic Slow Cross')
        self.item_stochs_label_ex = QTreeWidgetItem(self.item_stochs_label)
        self.item_stochs_label_ex.setText(0, 'stoch_cross(fastk_period=5, slowk_period=3, slowd_period=3, window_size=0)')

        leftLayout.addLayout(optionLayout)
        leftLayout.addWidget(self.indi_label)
        leftLayout.addWidget(self.indi_display_tree)

        # right Layout(주문 생성 정보 입력, 에디터)
        rightLayout = QVBoxLayout()

        # 주문기간, 봉 타입, 적용 종목(라디오버튼)
        inputLayout = QVBoxLayout()

        # 적용 종목
        self.periodLayout = QHBoxLayout()

        # local mode
        self.stock_use_label = QLabel('적용종목')
        self.stock_use_local_edit = QLineEdit()
        self.setAcceptDrops(True)
        self.stock_file_btn = QPushButton('파일불러오기')
        self.stock_file_btn.clicked.connect(self.get_stock_file)
        self.stock_indi_btn = QPushButton('지표표시')
        self.stock_indi_btn.clicked.connect(self.display_local_indi)

        # network mode
        self.stock_use_net_edit = QLineEdit()
        # 네트워크 모드 시 검색어 자동완성 추가
        # 검색어 자동완성
        if os.path.isfile(f'{self.root_path}/stockFile/KRX.csv'):
            self.KRX_df = pd.read_csv(f'{self.root_path}/stockFile/KRX.csv')
        else:
            self.KRX_df = fdr.StockListing('KRX')
        
        stock_name_code = self.KRX_df[['Symbol', 'Name']]
        code_data = stock_name_code.values.tolist()
        widget_names = []
        for i in code_data:
            stock_names = ' '.join(i)
            widget_names.append(stock_names)
        self.widgets = []

        self.stock_use_net_edit.textChanged.connect(self.update_display)
        self.completer = QCompleter(widget_names)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.stock_use_net_edit.setCompleter(self.completer)
        self.stock_use_net_edit.hide()

        hlay = QHBoxLayout()
        hlay.addWidget(self.stock_use_label)
        hlay.addWidget(self.stock_use_local_edit)
        hlay.addWidget(self.stock_file_btn)
        hlay.addWidget(self.stock_indi_btn)
        hlay.addWidget(self.stock_use_net_edit)
        self.periodLayout.addLayout(hlay)

        # 네트워크 모드 시 봉타입
        self.typeGroupBox = QGroupBox('봉 타입')
        self.intervalLayout = QHBoxLayout()
        self.dailyRadio = QRadioButton('일봉')
        self.dailyRadio.setChecked(True)
        self.weeklyRadio = QRadioButton('주봉')
        self.intervalLayout.addWidget(self.dailyRadio)
        self.intervalLayout.addWidget(self.weeklyRadio)
        self.typeGroupBox.setLayout(self.intervalLayout)
        self.typeGroupBox.hide()
        self.periodLayout.addWidget(self.typeGroupBox)

        # 주문기간
        self.order_period_label = QLabel('운용 기간')
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate(2020, 1, 1))
        self.start_date.setDisplayFormat('yyyy-MM-dd')
        self.start_date.setCalendarPopup(True)

        self.order_interval = QLabel('~')
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate(2021, 1, 1))
        self.end_date.setDisplayFormat('yyyy-MM-dd')
        self.end_date.setCalendarPopup(True)

        self.periodLayout.addWidget(self.order_period_label)
        self.periodLayout.addWidget(self.start_date)
        self.periodLayout.addWidget(self.order_interval)
        self.periodLayout.addWidget(self.end_date)

        inputLayout.addLayout(self.periodLayout)
        rightLayout.addLayout(inputLayout)

        # 지표 선언식(netmode), 전략 조건식, 전략 조건식 검증 버튼, 주문 생성 버튼 레이아웃
        # 지표 선언식
        # 지표 선언식 로컬파일모드용 포함.
        self.indi_local_edit_label = QLabel('지표 선언식')
        self.indi_local_edit_text = QPlainTextEdit()

        self.indi_edit_label = QLabel('지표 선언식')
        self.indi_edit_text = QPlainTextEdit()
        self.indi_edit_label.hide()
        self.indi_edit_text.hide()
        vlay0 = QVBoxLayout()
        vlay0.addWidget(self.indi_local_edit_label)
        vlay0.addWidget(self.indi_local_edit_text)

        vlay0.addWidget(self.indi_edit_label)
        vlay0.addWidget(self.indi_edit_text)
        rightLayout.addLayout(vlay0)

        # 전략 조건식(local_file_mode)
        self.strategy_edit_label = QLabel('거래 전략 편집기')
        self.strategy_edit_text = QPlainTextEdit()

        # 전략 조건식(net_mode)
        self.strategy_net_edit_text = QPlainTextEdit()
        self.strategy_net_edit_text.hide()

        vlay = QVBoxLayout()
        vlay.addWidget(self.strategy_edit_label)
        vlay.addWidget(self.strategy_edit_text)
        vlay.addWidget(self.strategy_net_edit_text)
        rightLayout.addLayout(vlay)

        # 전략 조건식 검증, 주문 생성 버튼
        self.strategy_test_button = QPushButton('전략 조건식 검증')
        self.order_create_button = QPushButton('주문 생성')
        self.order_create_button.clicked.connect(self.get_strategy_info)

        hlay3 = QHBoxLayout()
        hlay3.addWidget(self.strategy_test_button)
        hlay3.addWidget(self.order_create_button)
        rightLayout.addLayout(hlay3)

        # 전체 레이아웃 병합 및 조정
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 0)
        layout.setStretchFactor(rightLayout, 1)
        self.setLayout(layout)

    # 파일 불러오기 버튼 이벤트
    def get_stock_file(self):
        basePath = QFileDialog.getOpenFileName(self, caption='종목파일', dir=self.root_path)
        self.stock_path = basePath[0]
        self.stock_use_local_edit.setText(self.stock_path)

    '''
        1. 종목차트에서 추가한 지표 컬럼 텍스트로 읽어와 선언식에 표시
        2. 종목차트 선언식에서 추가한 컬럼 리스트로 수정하여 모듈에 넘기고 가공
        3. 향후 로컬파일모드에서 생성한 strategy.json 파일을 종목찾기 메뉴에서 필터링 과정을 수행시키기 위함
    '''
    def display_local_indi(self):
        file_path = self.stock_use_local_edit.text()

        # stock csv 파일에서 추가된 지표를 읽어와 지표 리스트 추가
        df = pd.read_csv(file_path)
        label_df = df.drop(columns=['Date', 'open', 'high', 'low', 'close', 'volume', 'change'])
        label_col_list = label_df.columns.tolist()

        # 모듈에서 컬럼 이름 정제하는 부분 추가
        modified_label_col_list = self.modify_name(label_col_list)

        # 모듈에서 정제한 컬럼 지표 선언식에 표시
        self.indi_local_edit_text.setPlainText("\n".join(modified_label_col_list))

    '''
        1. csv 파일에 추가된 지표 컬럼들을 읽어와 선언식에 표시
    '''
    def modify_name(self, colName_list):
        import re
        funcName_list = []

        for colName in colName_list:
            col = colName.split('_')
            if col[0] == 'lbb':
                name = f"bbands({col[1]},{col[2]},{col[3]})"
                funcName_list.append(name)

            elif col[0] == 'rsi':
                name = f"rsi({col[1]})"
                funcName_list.append(name)

            elif col[0] == 'macd':
                macd_2_param = col[1]
                new_macd_2_param = re.sub(r'[^0-9]', '', macd_2_param)
                if new_macd_2_param != '':
                    name = f"macd({new_macd_2_param},{col[2]},{col[3]})"
                    funcName_list.append(name)

            elif col[0] == 'slowk':
                name = f"stoch({col[1]},{col[2]},{col[3]})"
                funcName_list.append(name)

            elif col[0] == 'fastk':
                name = f"stochf({col[1]},{col[2]})"
                funcName_list.append(name)

            elif col[0] == 'ma':
                ma_param = col[1]
                name = f"ma({ma_param[:-7]})"
                funcName_list.append(name)

            elif col[0] == 'ema':
                ema_param = col[1]
                name = f"ema({ema_param[:-7]})"
                funcName_list.append(name)

            elif col[0] == 'cmo':
                name = f"cmo({col[1]})"
                funcName_list.append(name)

            elif colName[0:3] == 'ATR':
                name = f"atr({colName[3:]})"
                funcName_list.append(name)

            elif col[0] == 'SuperTrend':
                name = f"st({col[1]},{col[2]})"
                funcName_list.append(name)

            elif colName == 'high_centroid':
                name = "clustering()"
                funcName_list.append(name)

            elif col[0] == 'candle' and col[1] == 'type':
                name = 'candle_type()'
                funcName_list.append(name)

            elif col[0] == 'candle' and col[1] == 'shape':
                name = "candle_shape()"
                funcName_list.append(name)

            elif col[0] == 'three' and col[1] == 'red':
                name = f'three_red({col[2]})'
                funcName_list.append(name)

            elif col[0] == 'three' and col[1] == 'blue':
                name = f'three_blue({col[2]})'
                funcName_list.append(name)

            elif col[0] == 'gap':
                name = f'n_gap({col[1]})'
                funcName_list.append(name)

            elif col[0] == 'roc':
                roc_param_name = col[2]
                roc_param_name_new = ''.join(filter(str.isalnum, roc_param_name))
                name = f'roc_classify({roc_param_name_new[:-5]}, "{roc_param_name_new[-5:]}")'
                funcName_list.append(name)

            elif col[0] == 'sma':
                sma_param_name = col[4]
                sma_param_name_new = ''.join(filter(str.isalnum, sma_param_name))
                name = f'sma_cross({col[2]}, {col[3]}, {sma_param_name_new[:-5]}, "{sma_param_name_new[-5:]}")'
                funcName_list.append(name)

            elif col[0] == 'dema':
                dema_param_name = col[4]
                dema_param_name_new = ''.join(filter(str.isalnum, dema_param_name))
                name = f'dema_cross({col[2]}, {col[3]}, {dema_param_name_new[:-5]}, "{dema_param_name_new[-5:]}")'
                funcName_list.append(name)

            elif col[0] == 'vwma':
                vwma_param_name = col[4]
                vwma_param_name_new = ''.join(filter(str.isalnum, vwma_param_name))
                name = f'vwma_cross({col[2]}, {col[3]}, {vwma_param_name_new[:-5]}, "{vwma_param_name_new[-5:]}")'
                funcName_list.append(name)

            elif col[0] == 'macd' and col[1] == 'classify':
                macd_param_name = col[3]
                macd_param_name_new = ''.join(filter(str.isalnum, macd_param_name))
                name = f'macd_classify({col[2]}, {macd_param_name_new[:-5]}, "{macd_param_name_new[-5:]}")'
                funcName_list.append(name)

            elif col[0] == 'macd' and col[1] == 'cross':
                macdCro_param_name = col[5]
                macdCro_param_name_new = ''.join(filter(str.isalnum, macdCro_param_name))
                name = f'macd_cross({col[2]}, {col[3]}, {col[4]}, {macdCro_param_name_new[:-5]}, "{macdCro_param_name_new[-5:]}")'
                funcName_list.append(name)

            elif col[0] == 'bbands' and col[1] == 'classify':
                bb_param_name = col[3]
                bb_param_name_new = ''.join(filter(str.isalnum, bb_param_name))
                name = f'bbands_classify({col[2]}, {bb_param_name_new[:-5]}, "{bb_param_name_new[-5:]}")'
                funcName_list.append(name)

            elif col[0] == 'stochf' and col[1] == 'cross':
                name = f'stochf_cross({col[2]}, {col[3]}, {col[4]})'
                funcName_list.append(name)

            elif col[0] == 'stoch' and col[1] == 'cross':
                name = f'stoch_cross({col[2]}, {col[3]}, {col[4]}, {col[5]})'
                funcName_list.append(name)

        return funcName_list

    '''
        drag & drop한 종목 파일을 정제하여 stockcode, startdate, enddate, interval 정보 취합
        파일 input text example: file:///C:/Users/윤세영/PycharmProjects/database20/p407_gui/stockFile/AJ네트웍스_d.csv
        
        1. stock_code => strategy.json 파일 포맷에 맞추기 위해 stock_name에서 stock_code로 변환 
        2. startDate 
        3. endDate 
        4. stock_interval
    '''
    def get_strategy_info(self):
        if self.local_Mode.isChecked():           
            if self.stock_use_local_edit.text().find('file:') == -1:
                file_path = self.stock_use_local_edit.text()
            else:
                file_path = self.stock_use_local_edit.text().split('///')[1]

            file_name = file_path.split('/')[-1]

            self.stock_name = file_name.replace('.csv', '')[:-2]
            self.stock_interval = file_name.replace('.csv', '')[-1]
            self.startDate = self.start_date.text()
            self.endDate = self.end_date.text()

            # stock_name을 KRX 파일을 참조하여 stock_code로 변환
            stock_df = self.KRX_df[['Symbol', 'Name']]
            self.stock_code = stock_df.loc[stock_df.Name == self.stock_name, 'Symbol'].values[0]

             # 지표 선언식 문자열 가공
            self.indi_local_info = self.indi_local_edit_text.toPlainText().strip()
            self.indi_local_info = self.indi_local_info.split('\n')
            self.indi_local_info_list = []
            for i in self.indi_local_info:
                self.indi_local_info_list.append(i)

            self.network = False   
         
            self.make_json(file_path)

        elif self.net_Mode.isChecked():
            self.stock_code = self.stock_use_net_edit.text()[0:6]
            self.startDate = self.start_date.text()
            self.endDate = self.end_date.text()

            if self.dailyRadio.isChecked():
                self.stock_interval = 'd'
            elif self.weeklyRadio.isChecked():
                self.stock_interval = 'w'

            # 입력한 stock_code를 KRX 파일을 참조하여 stock_name으로 변환
            stock_df = self.KRX_df
            stock_df = stock_df[['Symbol', 'Name']]
            self.stock_name = stock_df.loc[stock_df.Symbol == self.stock_code, 'Name'].values[0]

            # 지표 선언식 문자열 가공
            self.indi_info = self.indi_edit_text.toPlainText().strip()
            self.indi_info = self.indi_info.split('\n')
            self.indi_info_list = []
            for i in self.indi_info:
                self.indi_info_list.append(i)

            self.network = True

            self.make_json()

    '''
        1. strategy.json 생성 및 저장
        2. order_creator 모듈에 전달
    '''
    def make_json(self, file_path=False):
        if self.local_Mode.isChecked():
            strategy_dic = {
                            'stockcode': str(self.stock_code),
                            'startdate': str(self.startDate),
                            'enddate': str(self.endDate),
                            'interval': str(self.stock_interval),
                            'indicator': self.indi_local_info_list,
                            'strategy': str(self.strategy_edit_text.toPlainText())
                           }

        elif self.net_Mode.isChecked():
            strategy_dic = {
                            'stockcode': str(self.stock_code),
                            'startdate': str(self.startDate),
                            'enddate': str(self.endDate),
                            'interval': str(self.stock_interval),
                            'indicator': self.indi_info_list,
                            'strategy': str(self.strategy_net_edit_text.toPlainText())
                           }

        strategy_list_dic = [strategy_dic]

        # strategy.json file 생성 및 저장
        os.makedirs(self.root_path + '/strategyFile', exist_ok=True)

        if self.stock_interval == 'd':
            strategy_file = f'{self.root_path}/strategyFile/{self.stock_name}_d_Strategy.json'
            with open(strategy_file, 'w+',
                      encoding='utf-8') as make_file:
                json.dump(strategy_list_dic, make_file, ensure_ascii=False, indent='\t')
            order_file_name = f'{self.stock_name}_d_Order.json'

        elif self.stock_interval == 'w':
            strategy_file = f'{self.root_path}/strategyFile/{self.stock_name}_w_Strategy.json'
            with open(strategy_file, 'w+',
                      encoding='utf-8') as make_file:
                json.dump(strategy_list_dic, make_file, ensure_ascii=False, indent='\t')
            order_file_name = f'{self.stock_name}_w_Order.json'

        # order creator 모듈에 json 파일 전달
        order_creator = OrderCreator(
                                        network=self.network,
                                        mix=False,
                                        root_path=self.root_path
                                    )

        if self.network == True:            
            order_creator.read_file(strategy_file, full_path=True)
        else:            
            order_creator.read_file(file_name=strategy_file, full_path=True, stock_file=file_path)
        order_creator.make_order()

        QMessageBox.information(self, "메시지", f"{order_file_name} 파일이 생성되었습니다!", QMessageBox.Yes)

        # 거래전략 결과 그래프 다이얼로그 호출
        import pathlib
        if self.stock_interval == 'd':
            file = pathlib.Path(self.root_path + '/orderFile/' + self.stock_name + '_d_Order.json')
            text = file.read_text(encoding='utf-8')
            js = json.loads(text)
            df = pd.DataFrame(js)

        elif self.stock_interval == 'w':
            file = pathlib.Path(self.root_path + '/orderFile/' + self.stock_name + '_w_Order.json')
            text = file.read_text(encoding='utf-8')
            js = json.loads(text)
            df = pd.DataFrame(js)

        simple_graph = simple_strategy_chart_dialog.SimpleStrategyGraph(self)
        stock_df = order_creator.order_requests[0].stock_df
        simple_graph.draw_strategy_result_graph(self.root_path, stock_df, self.startDate, self.endDate, df)
        simple_graph.showModal()

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        file_path = e.mimeData().text()
        file_type = file_path.split('.')[-1]

        if file_type == 'csv':
            self.stock_use_local_edit.setText(e.mimeData().text())
        else:
            QMessageBox.information(self, "메시지", "올바르지 않은 파일 형식입니다. 다시 입력하세요.", QMessageBox.Yes)
            self.stock_use_local_edit.setText('')

    # 검색어 자동완성 시 입력 에디터 하단에 생성되는 검색어 표시줄
    def update_display(self, text):
        for widget in self.widgets:
            if text.lower() in widget.name.lower():
                widget.show()
            else:
                widget.hide()

    # 네트워크 모드 클릭 시 화면 전환
    def netModeLayout(self):
        self.indi_local_edit_label.hide()
        self.indi_local_edit_text.hide()
        self.stock_file_btn.hide()
        self.stock_indi_btn.hide()
        self.strategy_edit_text.hide()
        self.stock_use_local_edit.hide()
        self.indi_edit_label.show()
        self.indi_edit_text.show()
        self.typeGroupBox.show()
        self.stock_use_net_edit.show()
        self.strategy_net_edit_text.show()

        if self.local_Mode.isChecked():
            self.indi_edit_label.hide()
            self.indi_edit_text.hide()
            self.typeGroupBox.hide()
            self.stock_use_net_edit.hide()
            self.strategy_net_edit_text.hide()
            self.stock_file_btn.show()
            self.stock_indi_btn.show()
            self.indi_local_edit_label.show()
            self.indi_local_edit_text.show()
            self.stock_use_local_edit.show()
            self.strategy_edit_text.show()


sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = simple_strategy()
    mainWin.show()
    sys.exit(app.exec_())