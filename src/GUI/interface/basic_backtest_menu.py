import PySide2
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

import os
import sys
import pathlib
import json
import pandas as pd

from GUI.interface import basic_backtest_graph_canvas, directory_tree
from module.simulator.simulator import Simulator
from module.calculator.calculator import Calculator

'''
기본 백테스트 화면
1. 주문 폴더
2. 백테스트 기본 값 입력
3. 수익률 그래프 창
'''
class basic_backtest(QMainWindow):
    def __init__(self, root_path):
        QMainWindow.__init__(self)
        self.root_path = root_path
        self.title = '기본백테스트'
        self.left = 10
        self.top = 10
        self.width = 1200
        self.height = 900

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 하단 상태바
        # self.statusBar().showMessage('기본백테스트')

        # 메인 창 전체 레이아웃 위젯 변수 선언 및 중앙 배치
        widget = QWidget(self)
        self.setCentralWidget(widget)

        # 메인 창 전체 레이아웃 수평 정렬
        vlay = QVBoxLayout(widget)

        # 주문 생성 에디터 위젯 가져오기
        basic_backtest = basic_backtest_editor(root_path=self.root_path)
        vlay1 = QVBoxLayout()
        vlay1.addWidget(basic_backtest)
        vlay.addLayout(vlay1)


class basic_backtest_editor(QWidget):
    def __init__(self, root_path, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.root_path = root_path

        # 매수횟수, 매도횟수, 최종수익률, 최고수익률, 최저수익률, calculator 기간 설정
        self.buy_count = ''
        self.sell_count = ''
        self.fin_asset = ''
        self.max_asset = ''
        self.min_asset = ''
        self.period = ''
        self.df = ''
        self.trading_df = ''

        #전체 레이아웃
        layout = QHBoxLayout()

        # Left Layout(directory tree, 주문파일 & 초기자본금 입력, 실행버튼)
        leftLayout = QHBoxLayout()

        # 종목 폴더
        vlay1 = QVBoxLayout()

        # (주문파일, 파일입력, 초기자본금, 옵션 그룹박스, 기간 설정 그룹박스, 실행버튼, 손익률 통계자료표)
        vlay2 = QVBoxLayout()

        # 주문파일, 초기자본금 입력, 파일 입력 버튼, 실행버튼
        hlay1 = QHBoxLayout()
        hlay2 = QHBoxLayout()

        # 주문파일
        self.order_file = QLabel('주문파일')
        self.order_file_edit = QLineEdit()
        hlay1.addWidget(self.order_file)
        hlay1.addWidget(self.order_file_edit)

        # 파일입력 버튼
        self.order_file_button = QPushButton('파일불러오기')
        self.order_file_button.clicked.connect(self.get_order_file)

        # 초기자본금
        self.init_money = QLabel('운용금액')
        self.init_money_edit = QLineEdit()
        hlay2.addWidget(self.init_money)
        hlay2.addWidget(self.init_money_edit)

        # 시뮬레이션 옵션 설정 그룹박스
        # 매수 수수료, 매도 수수료, 세금, 슬리피지, 네트워크 연결 여부
        self.option_groupbox = QGroupBox('백테스트 옵션')
        option_lay = QFormLayout()

        self.buying_fee_label = QLabel('매수 수수료(%)')
        self.buying_fee_edit = QLineEdit()
        self.buying_fee_edit.setPlaceholderText('0.015')

        self.selling_fee_label = QLabel('매도 수수료(%)')
        self.selling_fee_edit = QLineEdit()
        self.selling_fee_edit.setPlaceholderText('0.015')

        self.national_tax_label = QLabel('세금(%)')
        self.national_tax_edit = QLineEdit()
        self.national_tax_edit.setPlaceholderText('0.23')

        self.slippage_label = QLabel('슬리피지(%)')
        self.slippage_edit = QLineEdit()
        self.slippage_edit.setPlaceholderText('0.01')

        self.net_radio = QRadioButton('네트워크')

        option_lay.addRow(self.buying_fee_label, self.buying_fee_edit)
        option_lay.addRow(self.selling_fee_label, self.selling_fee_edit)
        option_lay.addRow(self.national_tax_label, self.national_tax_edit)
        option_lay.addRow(self.slippage_label, self.slippage_edit)
        option_lay.addWidget(self.net_radio)

        self.option_groupbox.setLayout(option_lay)

        # 기간 옵션 설정 그룹박스
        # 주별, 월별, 연별
        self.period_option_groupbox = QGroupBox('기간 옵션')
        period_option_lay = QHBoxLayout()

        self.week_radio = QRadioButton('주별')
        self.month_radio = QRadioButton('월별')
        self.year_radio = QRadioButton('연별')

        period_option_lay.addWidget(self.week_radio)
        period_option_lay.addWidget(self.month_radio)
        period_option_lay.addWidget(self.year_radio)

        self.period_option_groupbox.setLayout(period_option_lay)

        # 실행버튼
        self.basic_button = QPushButton('백테스트 실행')
        self.basic_button.clicked.connect(self.get_order_info)

        # 손익률 통계자료표 위젯
        self.static_table_label = QLabel('통계자료표')
        self.static_table = QTableWidget()
        self.static_table.resize(300, 200)

        # 표의 크기를 지정
        self.static_table.setColumnCount(2)
        self.static_table.setRowCount(5)

        # 열 제목 지정
        self.static_table.setHorizontalHeaderLabels(['이름', '값'])

        vlay2.addLayout(hlay1)
        vlay2.addWidget(self.order_file_button)
        vlay2.addLayout(hlay2)
        vlay2.addWidget(self.option_groupbox)
        vlay2.addWidget(self.period_option_groupbox)
        vlay2.addWidget(self.basic_button)
        vlay2.addWidget(self.static_table_label)
        vlay2.addWidget(self.static_table)

        # leftLayout.addLayout(vlay1)
        leftLayout.addLayout(vlay2)

        # 수익률 그래프 위젯
        rightLayout = QVBoxLayout()
        
        # 그래프 캔버스 레이아웃 선언
        self.setAcceptDrops(True)
        self.canvas = basic_backtest_graph_canvas.PlotCanvas()

        # 기본 수익률 그래프 check box
        self.basic_profit_check = QCheckBox('주가 수익률')
        self.basic_profit_check.stateChanged.connect(self.check_basic_profit_graph)

        # 그래프 종류 선택 위젯 레이아웃
        self.cb_option = QComboBox(self)
        self.cb_option.addItem('전략 수익률', 'asset')
        self.cb_option.addItem('기간별 수익률', 'period_profit')
        self.cb_option.currentTextChanged.connect(self.change_subplot)

        self.scroll = QScrollArea()
        mini_vlay = QVBoxLayout()
        mini_hlay = QHBoxLayout()

        # 툴바 + 그래프 종류 선택 옵션
        # mini_hlay.addWidget(self.toolbar)
        mini_hlay.addWidget(self.basic_profit_check)
        mini_hlay.addWidget(self.cb_option)
        
        mini_vlay.addLayout(mini_hlay)
        mini_vlay.addWidget(self.canvas)

        self.scroll.setLayout(mini_vlay)
        
        rightLayout.addWidget(self.scroll)

        # 전체 레이아웃 병합 및 조정
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 0)
        layout.setStretchFactor(rightLayout, 1)
        self.setLayout(layout)

    def get_order_file(self):
        basePath = QFileDialog.getOpenFileName(self, caption='주문파일', dir=self.root_path)
        self.order_file_edit.setText(basePath[0])
        self.file_path = self.order_file_edit.text()

    '''
        1. 거래전략 메뉴에서 생성한 order.json 파일, 운용금액, 백테스트 옵션 입력 받음
        2. simulator 모듈에 전달
        *** treeview item 선택 시 파일정보 받는 것 나중에 생각 일단은 drag&drop 으로 처리
    '''
    def get_order_info(self):
        #file: // / C: / Users / 윤세영 / PycharmProjects / database20 / p407_gui / orderFile / SK하이닉스_d_Order.json
        # simulator infos
        self.file_name = self.file_path.split('/')[-1]
        self.cash = self.init_money_edit.text()
        self.buying_fee = self.buying_fee_edit.text()
        self.selling_fee = self.selling_fee_edit.text()
        self.national_tax = self.national_tax_edit.text()
        self.slippage = self.slippage_edit.text()
        if self.net_radio.isChecked():
            self.net = True
        else:
            self.net = False

        if self.make_simul_json():
            # calculator infos
            # 수익률 기간 옵션
            self.period = ''
            if self.week_radio.isChecked():
                self.period = 'week'
            if self.month_radio.isChecked():
                self.period = 'month'
            if self.year_radio.isChecked():
                self.period = 'year'

            self.make_cal_json()
        else:
            self.min_asset = 0
            self.max_asset = 0
            self.fin_asset = 0
            self.insert_tableInfo()

    def make_simul_json(self):
        simulator = Simulator()
        # 주문 파일 read_file에 simulator에 전달
        # 운용 금액, 백테스트 옵션 simulator에 전달
        simulator.read_file(str(self.file_name),                            
                            path=self.file_path, 
                            full_path=True)

        simulator.set_cash(int(self.cash))
        simulator.set_option(float(self.buying_fee), float(self.selling_fee), float(self.national_tax),
                             float(self.slippage), self.net)

        # simulation 실행
        simulator.simulation()
        simulator.write_trlog(path=self.root_path)
        simulator.write_stlog(path=self.root_path)

        # 매도 및 매수 횟수 얻음.
        if simulator.get_Tcount(): 
            self.buy_count, self.sell_count = simulator.get_Tcount()

            # 통계자료표에 매수횟수, 매도횟수 삽입
            self.insert_tableInfo()
            return True
        else:
            self.buy_count = 0
            self.sell_count = 0
            return False            
            
    def make_cal_json(self):
        calculator = Calculator()

        # tradingLog 파일 calculator에 전달
        self.tradingLog_file = self.file_name.replace('Order', 'TradingLog')
        
        if calculator.read_file(file_name=str(self.tradingLog_file),
                                path=self.root_path):
            # calculation 실행
            calculator.calculation(self.period)
            # asset file 생성
            calculator.write_atlog(self.period, self.root_path)
        else:
            return

        # 기간별 최종, 최대, 최소 손익률 출력
        if self.week_radio.isChecked():
            self.fin_asset, self.max_asset, self.min_asset = calculator.get_Wasset()
        if self.month_radio.isChecked():
            self.fin_asset, self.max_asset, self.min_asset = calculator.get_Masset()
        if self.year_radio.isChecked():
            self.fin_asset, self.max_asset, self.min_asset = calculator.get_Yasset()

        print('최종손익률', self.fin_asset)
        print('최고손익률', self.max_asset)
        print('최저손익률', self.min_asset)

        # 통계자료표에 최저손익률, 최고손익률, 최종손익률 삽입
        self.insert_tableInfo()

        # 일별/월별/연별 누적수익률 그래프 정보 전달
        # 자산 흐름 그래프 정보 전달
        if self.sell_count == 0 and self.buy_count == 0:
            QMessageBox.information(self, "메시지", "거래가 발생하지 않은 전략입니다.", QMessageBox.Yes)
        else:
            self.give_graph_info(calculator)

    def insert_tableInfo(self):
            # 통계자료표 내용
            self.static_table.setItem(0, 0, QTableWidgetItem('매수횟수(회)'))
            self.static_table.setItem(0, 1, QTableWidgetItem(str(self.buy_count)))
            self.static_table.setItem(1, 0, QTableWidgetItem('매도횟수(회)'))
            self.static_table.setItem(1, 1, QTableWidgetItem(str(self.sell_count)))
            self.static_table.setItem(2, 0, QTableWidgetItem('최저손익률(%)'))
            self.static_table.setItem(2, 1, QTableWidgetItem(str(self.min_asset)))
            self.static_table.setItem(3, 0, QTableWidgetItem('최고손익률(%)'))
            self.static_table.setItem(3, 1, QTableWidgetItem(str(self.max_asset)))
            self.static_table.setItem(4, 0, QTableWidgetItem('최종손익률(%)'))
            self.static_table.setItem(4, 1, QTableWidgetItem(str(self.fin_asset)))

    def give_graph_info(self, cal_instance):
        # tradingLog json file to dataframe
        file = pathlib.Path(self.root_path + '/tradingLogFile/' + str(self.tradingLog_file))
        text = file.read_text(encoding='utf-8')
        js = json.loads(text)
        self.trading_df = pd.DataFrame(js)

        if self.week_radio.isChecked():
            self.df = cal_instance._wast_log
            if self.cb_option.currentData() == 'period_profit':
                self.canvas.draw_backtest_graph(self.root_path, self.df, self.trading_df, state = 'period_profit')
            elif self.cb_option.currentData() == 'asset':
                self.canvas.draw_backtest_graph(self.df, self.trading_df)

        if self.month_radio.isChecked():
            self.df = cal_instance._mast_log
            if self.cb_option.currentData() == 'period_profit':
                self.canvas.draw_backtest_graph(self.root_path, self.df, self.trading_df, state = 'period_profit')
            elif self.cb_option.currentData() == 'asset':
                self.canvas.draw_backtest_graph(self.root_path, self.df, self.trading_df)

        if self.year_radio.isChecked():
            self.df = cal_instance._yast_log
            if self.cb_option.currentData() == 'period_profit':
                self.canvas.draw_backtest_graph(self.root_path, self.df, self.trading_df, state = 'period_profit')
            elif self.cb_option.currentData() == 'asset':
                self.canvas.draw_backtest_graph(self.root_path, self.df, self.trading_df)

    def change_subplot(self):
        # 기간별 수익률 아이템 선택
        if self.cb_option.currentData() == 'period_profit':
            self.canvas.draw_backtest_graph(self.root_path, self.df, self.trading_df, state = 'period_profit')
        # 자산흐름 아이템 선택
        elif self.cb_option.currentData() == 'asset':
            self.canvas.draw_backtest_graph(self.root_path, self.df, self.trading_df)


    # 기본 수익률 그래프 체크박스 선택 시
    def check_basic_profit_graph(self):
        if self.basic_profit_check.isChecked():
            self.canvas.draw_backtest_graph(self.root_path, self.df, self.trading_df, state='basic_profit')
        else:
            self.canvas.draw_backtest_graph(self.root_path, self.df, self.trading_df)

    def dropEvent(self, e):
        self.order_file_edit.setText(e.mimeData().text())
        if self.order_file_edit.text().find('file:') == -1:
            self.file_path = self.order_file_edit.text()
        else:
            self.file_path = self.order_file_edit.text().split('///')[1]

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()


sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = basic_backtest()
    mainWin.show()
    sys.exit(app.exec_())