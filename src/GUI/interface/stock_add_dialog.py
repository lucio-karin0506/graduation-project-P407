from PySide2.QtGui import *
from PySide2.QtWidgets import *
import PySide2
import os
import sys
import pandas as pd
import FinanceDataReader as fdr

from module.gatherer.gatherer import Gatherer
from GUI.interface import directory_tree
# from module.auto_trader.upbit_api import Upbit_Api

'''
다이얼로그
1. 주가 종목 검색
2. 추가버튼 클릭 후 csv 파일 생성 in directory tree
'''
class stock_add(QDialog):
    def __init__(self, root_path):
        QDialog.__init__(self)
        self.root_path = root_path
        self.title = '종목다운로드'
        self.left = 10
        self.top = 10
        self.width = 700
        self.height = 700

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.center()
        layout = QVBoxLayout()

        # 종목 이름 리스트
        # code_data = fdr.StockListing('KRX')
        self.gathering = Gatherer(krx=True, path=self.root_path)
        self.trees_widget = directory_tree.DirectoryTreeView()

        code_data = pd.read_csv(self.root_path + '/stockFile/KRX.csv', dtype={'Symbol': str})
        code_data = code_data[['Symbol', 'Name']]
        code_data = code_data.values.tolist()
        widget_names = []
        for i in code_data:
            stock_names = ' '.join(i)
            widget_names.append(stock_names)
        self.widgets = []

        # upbit 종목 리스트
        # self.upbit_api = Upbit_Api()
        # self.upbit_df = self.upbit_api.get_market_list()
        # self.upbit_df = self.upbit_df[['market', 'korean_name']]
        # self.upbit_list = self.upbit_df.values.tolist()
        # coin_names = []
        # for i in self.upbit_list:
        #     code_names = ' '.join(i)
        #     coin_names.append(code_names)
        # self.coin_widgets = []

        # 주식, 코인 라디오버튼
        radio_lay = QHBoxLayout()
        self.stock_radio = QRadioButton('주식')
        self.stock_radio.setChecked(True)
        # self.coin_radio = QRadioButton('가상화폐')
        # self.coin_radio.setChecked(False)
        # self.coin_radio.setCheckable(False)
        # self.coin_radio.toggled.connect(self.clickCoinRadio)

        radio_lay.addWidget(self.stock_radio)
        # radio_lay.addWidget(self.coin_radio)
        layout.addLayout(radio_lay)

        # 종목 이름 검색
        upperLayout = QHBoxLayout()
        self.stock_code_label = QLabel('종목이름')

        self.stock_code_edit = QLineEdit()
        self.stock_code_edit.textChanged.connect(self.update_display)

        # coin 이름 검색
        # self.coin_code_edit = QLineEdit()
        # self.coin_code_edit.textChanged.connect(self.update_coin_display)
        # self.coin_code_edit.hide()

        # 검색어 자동완성
        self.completer = QCompleter(widget_names)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.stock_code_edit.setCompleter(self.completer)

        # # 코인 검색 자동완성
        # self.coin_completer = QCompleter(coin_names)
        # self.coin_completer.setCaseSensitivity(Qt.CaseInsensitive)
        # self.coin_code_edit.setCompleter(self.completer)

        upperLayout.addWidget(self.stock_code_label)
        upperLayout.addWidget(self.stock_code_edit)
        # upperLayout.addWidget(self.coin_code_edit)
        layout.addLayout(upperLayout)

        # 종목 이름 리스트 위젯에 삽입
        self.stock_box = QListWidget()
        for name in widget_names:
            self.stock_box.addItem(name)

        # coin 이름 리스트 위젯에 삽입
        # self.coin_box = QListWidget()
        # for name in coin_names:
        #     self.coin_box.addItem(name)
        # self.coin_box.hide()

        # 스크롤 설정
        scroll_bar = QScrollBar(self)
        self.stock_box.setVerticalScrollBar(scroll_bar)
        # self.coin_box.setVerticalScrollBar(scroll_bar)

        # 종목 이름 리스트 아이템 선택
        self.stock_box.itemSelectionChanged.connect(self.on_change)

        # coin 이름 리스트 아이템 선택
        # self.coin_box.itemSelectionChanged.connect(self.on_coin_change)

        # 종목 이름 리스트 위젯 레이아웃 설정
        stock_box_layout = QVBoxLayout()
        stock_box_layout.addWidget(self.stock_box)
        # stock_box_layout.addWidget(self.coin_box)
        layout.addLayout(stock_box_layout)

        # 다운로드 진행바
        self.progress = QProgressBar(self)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # 다운로드, 취소 버튼
        buttonLayout = QHBoxLayout()
        self.downlaod = QPushButton('다운로드')
        self.downlaod.clicked.connect(self.stock_download)

        self.close = QPushButton('취소')
        self.close.clicked.connect(self.closeIt)

        buttonLayout.addWidget(self.downlaod)
        buttonLayout.addWidget(self.close)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def on_change(self):
        self.stock_box_item = ''
        for item in self.stock_box.selectedItems():
            self.stock_box_item = item.text()
            self.stock_code_edit.setText(str(self.stock_box_item))

    # def on_coin_change(self):
    #     self.coin_box_item = ''
    #     for item in self.coin_box.selectedItems():
    #         self.coin_box_item = item.text()
    #         self.coin_code_edit.setText(str(self.coin_box_item))

    # 화면 중앙 배치
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 검색어 자동완성 시 입력 에디터 하단에 생성되는 검색어 표시줄
    def update_display(self, text):
        for widget in self.widgets:
            if text.lower() in widget.name.lower():
                widget.show()
            else:
                widget.hide()

    # 검색어 자동완성 시 입력 에디터 하단에 생성되는 검색어 표시줄
    # def update_coin_display(self, text):
    #     for widget in self.coin_widgets:
    #         if text.lower() in widget.name.lower():
    #             widget.show()
    #         else:
    #             widget.hide()

    def stock_download(self):
        # 주식 라디오 클릭 시
        if self.stock_radio.isChecked():
            self.progress.setMaximum(len(self.stock_code_edit.text()))

            stock_code = str(self.stock_code_edit.text())[0:6]
            start_date = '1990-01-01'
            end_date = 'today'
            self.run_gathering(stock_code, start_date, end_date, state='stock')

            self.progress.setValue(len(self.stock_code_edit.text()))
        
        # 코인 라디오 클릭 시
        # if self.coin_radio.isChecked():
        #     self.progress.setValue(len(self.coin_code_edit.text()))

        #     coin_code = str(self.coin_code_edit.text())[0:7]
        #     # start_date = '1990-01-01'
        #     # end_date = 'today'
        #     self.run_gathering(coin_code, state='coin')

        #     self.progress.setValue(len(self.coin_code_edit.text()))

        msg = QMessageBox.information(self, "메시지", "다운로드가 완료되었습니다!", QMessageBox.Yes)
        if msg == QMessageBox.Yes:
            stock_add.close(self)

    def run_gathering(self, code, start_date='', end_date='', state='stock'):
        if state == 'stock':
            # gathering = Gatherer()
            self.gathering.get_stock(code, start_date, end_date, 'd', self.root_path)
            self.gathering.get_stock(code, start_date, end_date, 'w', self.root_path)
        
        # if state == 'coin':
        #     # self.upbit_daily_df = self.upbit_api.get_candle_day(market=code)
        #     # date_col = self.upbit_daily_df['Date'].values.tolist()
        #     # update_date_col = [i[0:10] for i in date_col]
        #     # self.upbit_daily_df['Date'] = update_date_col
        #     os.makedirs(os.getcwd() + '/upbitFile', exist_ok=True)
        #     self.upbit_daily_df.to_csv(os.getcwd()+ '/upbitFile/' + code + '_d.csv', index_label='Date')

    def closeIt(self):
        stock_add.close(self)

    def showModal(self):
        return super().exec_()

    # def clickCoinRadio(self):
    #     self.stock_code_edit.hide()
    #     self.stock_box.hide()
    #     self.coin_code_edit.show()
    #     self.coin_box.show()
    #     if self.stock_radio.isChecked():
    #         self.coin_code_edit.hide()
    #         self.coin_box.hide()
    #         self.stock_code_edit.show()
    #         self.stock_box.show()


sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = stock_add()
    mainWin.show()
    sys.exit(app.exec_())