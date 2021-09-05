import json
import PySide2
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

import os
import sys
import pandas as pd
import pathlib
import FinanceDataReader as fdr

from module.handling_file import get_refined_path
from module.apply.apply import Apply
from GUI.interface import stock_filtering_dialog

'''
종목 필터링 화면 (상장되어 있는 모든 종목 사용자 전략에 맞추어 필터링)
'''
class filtering(QMainWindow):
    def __init__(self, root_path):
        QMainWindow.__init__(self)
        self.root_path = root_path
        self.title = '종목찾기'
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

        # 종목 필터링 에디터 위젯 가져오기
        filtering = filtering_editor(root_path=self.root_path)
        vlay1 = QVBoxLayout()
        vlay1.addWidget(filtering)
        vlay.addLayout(vlay1)


class filtering_editor(QWidget):
    def __init__(self, root_path, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.root_path = root_path
        #전체 레이아웃
        layout = QHBoxLayout()

        # Left Layout(vlay1)
        leftLayout = QHBoxLayout()

        # 종목이름 검색 & 전체선택 체크버튼 & 종목폴더(상장된 주가 종목 리스트 받아옴)
        vlay1 = QVBoxLayout()

        # 종목 이름 리스트
        if os.path.isfile(f'{self.root_path}/stockFile/KRX.csv'):
            code_data = pd.read_csv(self.root_path+'/stockFile/KRX.csv', dtype={'Symbol': str})
        else:
            code_data = fdr.StockListing('KRX')
        
        code_data = code_data[['Symbol', 'Name']]
        code_data = code_data.values.tolist()
        self.widget_names = []
        for i in code_data:
            stock_names = ' '.join(i)
            self.widget_names.append(stock_names)
        self.widgets = []

        # 종목 이름 검색
        stock_hlay = QHBoxLayout()
        self.stock_name = QLabel('종목코드')

        self.stock_name_edit = QLineEdit()
        self.stock_name_edit.textChanged.connect(self.update_display)

        # 검색어 자동완성
        self.completer = QCompleter(self.widget_names)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.stock_name_edit.setCompleter(self.completer)

        stock_hlay.addWidget(self.stock_name)
        stock_hlay.addWidget(self.stock_name_edit)

        # 전체선택 체크
        self.stock_check_all = QCheckBox('전체선택')
        self.stock_check_all.stateChanged.connect(self.check_all)

        # 종목폴더 리스트
        self.stock_label = QLabel('종목폴더')
        self.stock_list = QListWidget()
        for name in self.widget_names:
            self.stock_list.addItem(name)

        # 종목폴더 리스트 아이템 선택 옵션
        self.stock_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.stock_list.itemSelectionChanged.connect(self.on_change)

        # 스크롤 설정
        scroll_bar = QScrollBar(self)
        self.stock_list.setVerticalScrollBar(scroll_bar)

        vlay1.addLayout(stock_hlay)
        vlay1.addWidget(self.stock_check_all)
        vlay1.addWidget(self.stock_label)
        vlay1.addWidget(self.stock_list)
        leftLayout.addLayout(vlay1)

        '''
            right layout 
            1. 전략 파일 에디터, 운용기간, 봉 타입
            2. 현금보유, buying fee, selling fee, national tax, slippage, 파일 추가 버튼, 실행 버튼
        '''
        self.rightLayout = QVBoxLayout()

        # 전략 파일 에디터(전략 파일 불러오기)
        self.strategy_hlay = QHBoxLayout()
        self.filter_btn_hlay = QHBoxLayout()

        self.strategy_label = QLabel('전략 파일')
        self.strategy_edit = QLineEdit()
        self.setAcceptDrops(True)

        self.strategy_file_btn = QPushButton('불러오기')
        self.strategy_file_btn.clicked.connect(self.get_strategy_file)

        self.strategy_add_btn = QPushButton('전략표시')
        self.strategy_add_btn.clicked.connect(self.show_strategy_text)

        # 운용기간
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

        # 봉 타입 그룹박스
        self.typeGroupBox = QGroupBox('봉 타입')
        self.intervalLayout = QHBoxLayout()
        self.dailyRadio = QRadioButton('일봉')
        self.dailyRadio.setChecked(True)
        self.weeklyRadio = QRadioButton('주봉')
        self.intervalLayout.addWidget(self.dailyRadio)
        self.intervalLayout.addWidget(self.weeklyRadio)
        self.typeGroupBox.setLayout(self.intervalLayout)

        self.strategy_hlay.addWidget(self.strategy_label)
        self.strategy_hlay.addWidget(self.strategy_edit)
        self.strategy_hlay.addWidget(self.strategy_file_btn)
        self.strategy_hlay.addWidget(self.strategy_add_btn)
        self.strategy_hlay.addWidget(self.order_period_label)
        self.strategy_hlay.addWidget(self.start_date)
        self.strategy_hlay.addWidget(self.order_interval)
        self.strategy_hlay.addWidget(self.end_date)
        self.strategy_hlay.addWidget(self.typeGroupBox)

        # 종목필터링 옵션 설정 그룹박스
        # 초기자본금, 매수 수수료, 매도 수수료, 세금, 슬리피지, 멀티프로세스 동작 여부
        left_lay = QVBoxLayout()
        self.option_groupbox = QGroupBox('백테스트 옵션')
        option_lay = QFormLayout()

        self.init_money_label = QLabel('운용 금액')
        self.init_money_edit = QLineEdit()
        option_lay.addRow(self.init_money_label, self.init_money_edit)

        self.buying_fee_label = QLabel('매수 수수료(%)')
        self.buying_fee_edit = QLineEdit()
        self.buying_fee_edit.setPlaceholderText('0.015')
        option_lay.addRow(self.buying_fee_label, self.buying_fee_edit)

        self.selling_fee_label = QLabel('매도 수수료(%)')
        self.selling_fee_edit = QLineEdit()
        self.selling_fee_edit.setPlaceholderText('0.015')
        option_lay.addRow(self.selling_fee_label, self.selling_fee_edit)

        self.national_tax_label = QLabel('세금(%)')
        self.national_tax_edit = QLineEdit()
        self.national_tax_edit.setPlaceholderText('0.23')
        option_lay.addRow(self.national_tax_label, self.national_tax_edit)

        self.slippage_label = QLabel('슬리피지(%)')
        self.slippage_edit = QLineEdit()
        self.slippage_edit.setPlaceholderText('0.01')
        option_lay.addRow(self.slippage_label, self.slippage_edit)

        self.multi_radio = QRadioButton('멀티 프로세스')
        option_lay.addWidget(self.multi_radio)

        # 그룹박스 위젯 레이아웃 간격 조정
        option_lay.setVerticalSpacing(45)

        self.option_groupbox.setLayout(option_lay)

        # 전략표시 버튼 클릭 시 전략 텍스트 띄움, 실행버튼 클릭 시 통계자료표 띄움
        right_lay = QVBoxLayout()
        self.strategy_text = QPlainTextEdit()
        right_lay.addWidget(self.strategy_text)

        # 실행버튼 
        self.filter_exec = QPushButton('실행')
        self.filter_exec.clicked.connect(self.get_filtering_info)
        
        left_lay.addWidget(self.option_groupbox)
        left_lay.addWidget(self.filter_exec)

        self.filter_btn_hlay.addLayout(left_lay)
        self.filter_btn_hlay.addLayout(right_lay)
        self.filter_btn_hlay.setStretchFactor(left_lay, 0)
        self.filter_btn_hlay.setStretchFactor(right_lay, 1)

        self.rightLayout.addLayout(self.strategy_hlay)
        self.rightLayout.addLayout(self.filter_btn_hlay)

        # 전체 레이아웃 병합 및 조정
        layout.addLayout(leftLayout)
        layout.addLayout(self.rightLayout)
        layout.setStretchFactor(leftLayout, 0)
        layout.setStretchFactor(self.rightLayout, 1)
        self.setLayout(layout)

    def get_strategy_file(self):
        self.basePath = QFileDialog.getOpenFileName(self, caption='전략파일', dir=self.root_path)
        self.strategy_path = self.strategy_edit.setText(self.basePath[0])

    # 검색어 자동완성 시 입력 에디터 하단에 생성되는 검색어 표시줄
    def update_display(self, text):
        for widget in self.widgets:
            if text.lower() in widget.name.lower():
                widget.show()
            else:
                widget.hide()

    # 종목 리스트 아이템 선택 시 이벤트
    def on_change(self):
        self.selected_stock = [item.text()[0:6] for item in self.stock_list.selectedItems()]
        self.stock_name_edit.setText(str(self.selected_stock))

    # 전체선택 체크 이벤트
    def check_all(self):
        stock_list = []
        if self.stock_check_all.isChecked():
            for i in self.widget_names:
                stock_list.append(i[0:6])
                self.stock_name_edit.setText(str(stock_list))
        else:
            self.stock_name_edit.setText('')

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        self.strategy_edit.setText(e.mimeData().text())

        file_path = self.strategy_edit.text()
        file_type = file_path.split('.')[-1]

        if file_type == 'json':
            pass
        else:
            QMessageBox.information(self, "메시지", "올바르지 않은 파일 형식입니다. 다시 입력하세요.", QMessageBox.Yes)
            self.strategy_edit.setText('')

    # strategy text 에디터에 추가버튼 클릭 시 파일 내용 나오도록 함.
    def show_strategy_text(self):
        if  self.strategy_edit.text().find('file:') == -1:
            file_name =  self.strategy_edit.text()
        else:
            file_name =  self.strategy_edit.text().split('///')[1]    
        file = pathlib.Path(file_name)

        text = file.read_text(encoding='utf-8')
        js = json.loads(text)
        
        js_dic = js[0]

        if js_dic['indicator'] == '':
            QMessageBox.information(self, "메시지", "사용할 지표가 표시되어 있지 않은 파일입니다.", QMessageBox.Yes)
            self.strategy_edit.setText('')
            self.strategy_text.setPlainText('')
        else:
            strategy = js_dic['strategy']
            self.strategy_text.setPlainText(strategy)
            QMessageBox.information(self, "메시지", "전략 텍스트가 추가되었습니다.", QMessageBox.Yes)

    # apply.py 에 전달할 정보 취합
    def get_filtering_info(self):

        self.startDate = self.start_date.text()
        self.endDate = self.end_date.text()
        self.interval = ''

        if self.dailyRadio.isChecked():
            self.interval = 'd'
        elif self.weeklyRadio.isChecked():
            self.interval = 'w'

        if self.strategy_edit.text().find('file:') == -1:
            self.strategy_file = self.strategy_edit.text()
        else:
            self.strategy_file = self.strategy_edit.text().split('///')[1]

        self.cash = self.init_money_edit.text()
        self.buying_fee = self.buying_fee_edit.text()
        self.selling_fee = self.selling_fee_edit.text()
        self.national_tax = self.national_tax_edit.text()
        self.slippage = self.slippage_edit.text()

        # 멀티 프로세스 체크 여부 확인
        if self.multi_radio.isChecked():
            multi = True
        else:
            multi = False

        apply = Apply(multi=multi, path=self.root_path)
        apply.set_option(
                        self.selected_stock,
                        str(self.startDate),
                        str(self.endDate),
                        str(self.interval),
                        str(self.strategy_file),
                        int(self.cash),
                        float(self.buying_fee),
                        float(self.selling_fee),
                        float(self.national_tax),
                        float(self.slippage)
                        )

        apply.apply()

        df = pd.read_csv(self.root_path + '/applyFile/apply_result.csv', encoding='cp949', index_col=0)

        QMessageBox.information(self, "메시지", "apply_result.csv 파일이 생성되었습니다.", QMessageBox.Yes)

        filter_dialog = stock_filtering_dialog.filter_result(df, self)
        filter_dialog.showModal()


sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = filtering()
    mainWin.show()
    sys.exit(app.exec_())