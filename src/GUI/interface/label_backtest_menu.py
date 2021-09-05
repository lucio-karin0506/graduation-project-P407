import PySide2
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

import os
import sys
import pandas as pd
import json
import pathlib

from GUI.interface import hit_ratio_dialog, label_backtest_graph_canvas
import module.labeler.labeler as label
from module.handling_file import get_refined_path
from module.hit_tester import hit_tester

'''
레이블 백테스트 화면
1. 주문 생성 에디터
2. 디버그 로깅 창
'''
class label_backtest(QMainWindow):
    def __init__(self, root_path):
        QMainWindow.__init__(self)
        self.root_path = root_path
        self.title = '레이블백테스트'
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
        label_backtest = label_backtest_editor(root_path=self.root_path)
        vlay1 = QVBoxLayout()
        vlay1.addWidget(label_backtest)
        vlay.addLayout(vlay1)


class label_backtest_editor(QWidget):
    def __init__(self, root_path, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.root_path = root_path

        #전체 레이아웃
        layout = QHBoxLayout()

        # Left Layout(vlay1 + vlay2)
        leftLayout = QHBoxLayout()

        # 종목 폴더
        vlay1 = QVBoxLayout()

        # 주문폴더, 파일입력버튼, 레이블파라미터 그룹박스, 레이블 그래프 생성버튼
        # 기본 백테스팅 파일, 버튼, 레이블 백테스팅 파일, 버튼, 레이블 백테스팅 실행 버튼
        vlay2 = QVBoxLayout()

        # 주문폴더 입력, 실행버튼
        hlay1 = QHBoxLayout()
        # 기본 백테스팅 파일 입력, 실행버튼
        hlay2 = QHBoxLayout()
        # 레이블 백테스팅 파일 입력, 실행버튼
        hlay3 = QHBoxLayout()

        # 주문폴더
        self.stock_file = QLabel('종목파일')
        self.stock_file_edit = QLineEdit()
        self.stock_file_edit.setReadOnly(False)

        hlay1.addWidget(self.stock_file)
        hlay1.addWidget(self.stock_file_edit)

        # 파일입력 버튼
        self.stock_file_button = QPushButton('파일불러오기')
        self.stock_file_button.clicked.connect(self.get_stock_file)

        # 레이블 파라미터 그룹박스
        self.label_box = QGroupBox('레이블 파라미터')
        box_lay = QFormLayout()

        self.param1_label = QLabel('RRPB(Ratio of Rising to Previous Bottom, %)')
        self.param1_edit = QLineEdit()
        self.param1_edit.setPlaceholderText('3')

        self.param2_label = QLabel('RFPT(Ratio of Fall to Previous Top, %)')
        self.param2_edit = QLineEdit()
        self.param2_edit.setPlaceholderText('2')

        self.param3_label = QLabel('TBR(Top Band Ratio, %)')
        self.param3_edit = QLineEdit()
        self.param3_edit.setPlaceholderText('0.3')

        self.param4_label = QLabel('BBR(Bottom Band Ratio, %)')
        self.param4_edit = QLineEdit()
        self.param4_edit.setPlaceholderText('0.3')

        box_lay.addRow(self.param1_label, self.param1_edit)
        box_lay.addRow(self.param2_label, self.param2_edit)
        box_lay.addRow(self.param3_label, self.param3_edit)
        box_lay.addRow(self.param4_label, self.param4_edit)
        self.label_box.setLayout(box_lay)

        # 레이블 데이터 생성 버튼
        self.label_graph_button = QPushButton('레이블 데이터 생성')
        self.label_graph_button.clicked.connect(self.get_label)

        # 기본 백테스팅 파일
        self.basic_order_file = QLabel('기본 백테스팅 주문 파일(.json)')
        self.basic_order_file_edit = QLineEdit()
        self.basic_order_file_edit.setReadOnly(False)

        hlay2.addWidget(self.basic_order_file)
        hlay2.addWidget(self.basic_order_file_edit)

        # 입력버튼
        self.basic_input_button = QPushButton('파일불러오기')
        self.basic_input_button.clicked.connect(self.get_order_file)

        # 레이블 백테스팅 파일
        # 그룹박스 체크 형식으로 생성
        # 기존에 존재하는 레이블 csv 파일을 사용자가 사용하고 싶을 때 사용할 수 있도록 체크박스 옵션 체크 할 수 있도록 함.
        self.labelFileGroup = QGroupBox('레이블 파일')
        self.labelFileGroup.setCheckable(True)
        self.labelFileGroup.setChecked(False)
        label_lay = QVBoxLayout()
        label_hlay = QHBoxLayout()

        self.label_file = QLabel('레이블 백테스팅 파일(.csv)')
        self.label_file_edit = QLineEdit()
        self.label_file_edit.setReadOnly(False)

        # 파일 입력버튼
        self.label_input_button = QPushButton('파일불러오기')
        self.label_input_button.clicked.connect(self.get_label_file)

        label_hlay.addWidget(self.label_file)
        label_hlay.addWidget(self.label_file_edit)
        label_lay.addLayout(label_hlay)
        label_lay.addWidget(self.label_input_button)

        self.labelFileGroup.setLayout(label_lay)

        hlay3.addWidget(self.labelFileGroup)

        # hit test option 설정 콤보박스
        self.hit_test_opt_lay = QHBoxLayout()
        self.hit_test_opt_label = QLabel('슬리피지')
        self.hit_test_opt = QComboBox(self)
        self.hit_test_opt.addItem('0', '0')
        self.hit_test_opt.addItem('1', '1')
        self.hit_test_opt.addItem('2', '2')
        
        self.hit_test_opt_lay.addWidget(self.hit_test_opt_label)
        self.hit_test_opt_lay.addWidget(self.hit_test_opt)

        # 입력버튼
        self.label_exec = QPushButton('레이블 백테스팅 실행')
        self.label_exec.clicked.connect(self.merge_df)

        # 그래프 타입 
        self.graph_type_lay = QHBoxLayout()

        vlay2.addLayout(hlay1)
        vlay2.addWidget(self.stock_file_button)
        vlay2.addWidget(self.label_box)
        vlay2.addWidget(self.label_graph_button)
        vlay2.addLayout(hlay2)
        vlay2.addWidget(self.basic_input_button)
        vlay2.addLayout(hlay3)
        vlay2.addLayout(self.hit_test_opt_lay)
        vlay2.addWidget(self.label_exec)

        leftLayout.addLayout(vlay1)
        leftLayout.addLayout(vlay2)

        # 수익률 그래프 위젯
        rightLayout = QVBoxLayout()
        
        # 그래프 캔버스 레이아웃 선언
        self.setAcceptDrops(True)

        self.canvas = label_backtest_graph_canvas.PlotCanvas()

        self.scroll = QScrollArea()
        mini_vlay = QVBoxLayout()
        mini_hlay = QHBoxLayout()

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

        self.fileName = ''
        self.fileCore = ''
        self.fileType = ''
        self.fileDir = ''
        self.opt = 0
        self.label_df = ''
        self.stock_file = ''
        self.stock_name = ''
        self.basicOrder_file_stock = ''

    def get_stock_file(self):
        basePath = QFileDialog.getOpenFileName(self, caption='종목파일', dir=self.root_path)
        self.stock_file_edit.setText(basePath[0])

    def get_order_file(self):
        basePath = QFileDialog.getOpenFileName(self, caption='주문파일', dir=self.root_path)
        self.basic_order_file_edit.setText(basePath[0])

    def get_label_file(self):
        basePath = QFileDialog.getOpenFileName(self, caption='레이블파일', dir=self.root_path)
        self.label_file_edit.setText(basePath[0])

    def dropEvent(self, e):
        self.fileName = e.mimeData().text().split('/')[-1] # 삼전_d.csv
        self.fileCore = self.fileName.split('.')[0] # 삼전_d, 삼전_d_label, 삼전_d_Order
        self.fileType = self.fileName.split('.')[-1]  # csv, json
        self.fileDir = self.fileCore.split('_')[-1] # label, Order
        
        if (self.fileDir == 'd' or self.fileDir == 'w') and self.fileType == 'csv':
            self.stock_file_edit.setText(e.mimeData().text())
            self.stock_file_edit.setReadOnly(True)


        if self.fileDir == 'Order' and self.fileType == 'json':
            self.basic_order_file_edit.setText(e.mimeData().text())
            self.basic_order_file_edit.setReadOnly(True)

        if self.fileDir == 'label' and self.fileType == 'csv':
            self.label_file_edit.setText(e.mimeData().text())
            self.label_file_edit.setReadOnly(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def get_hitRatio_dialog(self):
        dialog = hit_ratio_dialog.hit_ratio()
        dialog.showModal()

    '''
        기본 주가 csv 파일 받은 후 labelFile로 저장 (label.csv)
    '''
    def get_label(self):
        stock_filename = self.stock_file_edit.text().split('/')[-1] # 삼성전자_d.csv
        self.stock_name = stock_filename.split('.')[0] # 삼성전자_d
        stock_df = pd.read_csv(self.stock_file_edit.text(), index_col='Date')
        stock_df = stock_df.drop(columns=stock_df.iloc[:,4:])
        os.makedirs(self.root_path+'/labelFile', exist_ok=True)
    
        label_df = label.add_top_bottom(
                                stock_df, 
                                float(self.param1_edit.text()) / 100,
                                float(self.param2_edit.text()) / 100,
                                float(self.param3_edit.text()) / 100,
                                float(self.param4_edit.text()) / 100
                                )

        label_df.to_csv(self.root_path + '/labelFile/' + self.stock_name + '_label.csv', index_label='Date')
        label_file = self.stock_name + '_label.csv'

        QMessageBox.information(self, "메시지", f"{label_file} 파일 생성이 완료되었습니다!", QMessageBox.Yes)

    '''
        hit_test를 수행하기 위한 레이블 붙어있는 csv 종목파일(label.csv) 및 기본 백테스트 주문 파일(order.json) 데이터프레임 병합
        label_df + order_df = result_df

        case 1: 사용자가 기존 레이블 파일 사용할 시 
        case 2: 사용자가 신규 레이블 파일 생성 시 
    '''
    def merge_df(self):
        if self.basic_order_file_edit.text().find('file:') == -1:
            self.file_path = self.basic_order_file_edit.text()
        else:
            self.file_path = self.basic_order_file_edit.text().split('///')[1] 

        self.basic_order_file_name = self.file_path.split('/')[-1] # DB손해보험_d_Order.json
        basicOrder_file_stock_name = self.basic_order_file_name.split('.')[0] # DB손해보험_d_Order
        self.basicOrder_file_stock = basicOrder_file_stock_name.split('_')[0] + '_' + basicOrder_file_stock_name.split('_')[1] # DB손해보험_d

        file = pathlib.Path(self.file_path)
        text = file.read_text(encoding='utf-8')
        js = json.loads(text)
        order_df = pd.DataFrame(js)

        order_df = order_df.drop(columns=order_df.iloc[:,5:])
        order_start = order_df.head(1)['order_datetime'].values[0]
        order_end = order_df.tail(1)['order_datetime'].values[0]
        order_df = order_df.rename({'order_datetime':'Date'}, axis='columns')
        order_df = order_df.drop_duplicates()

        # case 1
        if self.labelFileGroup.isChecked() == True:
            label_file_name = self.label_file_edit.text().split('/')[-1] # DB손해보험_d_label.csv
            label_file_stock_name = label_file_name.split('.')[0] # DB손해보험_d_label
            label_file_stock = label_file_stock_name.split('_')[0] + '_' + label_file_stock_name.split('_')[1]  # DB손해보험_d

            if self.basicOrder_file_stock == label_file_stock:
                # 기본 백테스트 주문 json 파일 종목명 == 레이블 csv 파일 종목명
                label_df = pd.read_csv(self.label_file_edit.text(), index_col='Date')
                label_df = label_df[order_start:order_end]

                result_df = pd.merge(order_df, label_df, on='Date', how='outer')
                result_df = result_df.sort_values(by=['Date'])
                self.exec_hit_test(result_df)
            else:
                QMessageBox.information(self, "메시지", "두 파일은 같은 종목이 아닙니다. 파일을 다시 입력해주세요.", QMessageBox.Yes)

        # case 2
        elif self.labelFileGroup.isChecked() == False:
            stock_filename = self.stock_file_edit.text().split('/')[-1] # 삼성전자_d.csv
            stock_name = stock_filename.split('.')[0] # 삼성전자_d

            if stock_name == self.basicOrder_file_stock:
                # 주가 종목 csv 파일 종목명 == 기본 백테스트 주문 json 파일 종목명
                label_df = pd.read_csv(self.root_path + '/labelFile/' + stock_name + '_label.csv', index_col='Date')
                label_df = label_df[order_start:order_end]

                result_df = pd.merge(order_df, label_df, on='Date', how='outer')
                result_df = result_df.sort_values(by=['Date'])
                self.exec_hit_test(result_df)
            else:
                QMessageBox.information(self, "메시지", "두 파일은 같은 종목이 아닙니다. 파일을 다시 입력해주세요.", QMessageBox.Yes)

    '''
        hit_test 시행
    '''
    def exec_hit_test(self, df):
        if self.hit_test_opt.currentData() == '0':
            self.opt = 0
        if self.hit_test_opt.currentData() == '1':
            self.opt = 1
        if self.hit_test_opt.currentData() == '2':
            self.opt = 2

        # hit_test 시행
        hit_test_df = hit_tester.hit_testing(df, self.opt)

        # hit_test 결과 csv 파일 저장
        os.makedirs(self.root_path + '/hitTestFile', exist_ok=True)

        # case 1
        if self.labelFileGroup.isChecked() == True:
            stock_filename = self.label_file_edit.text().split('/')[-1]
            stock_name = stock_filename.split('_')[0] + '_' + stock_filename.split('_')[1]
            hit_test_df.to_csv(self.root_path + '/hitTestFile/' + stock_name + '_' + str(self.opt) + '_hit_test_result.csv', index_label='Date')
        # case 2
        elif self.labelFileGroup.isChecked() == False:
            stock_filename = self.stock_file_edit.text().split('/')[-1] # 삼성전자_d.csv
            stock_name = stock_filename.split('.')[0] # 삼성전자_d
            hit_test_df.to_csv(self.root_path + '/hitTestFile/' + stock_name + '_' + str(self.opt) + '_hit_test_result.csv', index_label='Date')

        QMessageBox.information(self, "메시지", "완료되었습니다!", QMessageBox.Yes)

        self.make_hit_infos()

    '''
        매수, 매도, 전체 hit 비율(정확도)
        해당 hit_test에 대한 통계 테이블 다이얼로그 호출
        레이블 그래프 생성
    '''
    def make_hit_infos(self):
        if self.labelFileGroup.isChecked():
            stock_filename = self.label_file_edit.text().split('/')[-1]
            stock_name = stock_filename.split('_')[0] + '_' + stock_filename.split('_')[1]
            hit_test_df = pd.read_csv(self.root_path + '/hitTestFile/' + stock_name + '_' + str(self.opt) + '_hit_test_result.csv', index_col='Date')
        else:
            hit_test_df = pd.read_csv(self.root_path + '/hitTestFile/' + self.stock_name + '_' + str(self.opt) + '_hit_test_result.csv', index_col='Date')

        # 매수 정확도
        hit_buy_df = hit_test_df[hit_test_df['buy_hit'] == 1]        
        buy_accuracy = hit_buy_df['buy_hit'].count() / len(hit_test_df[hit_test_df['order_type'] == 'buy'])

        # 매도 정확도
        hit_sell_df = hit_test_df[hit_test_df['sell_hit'] == 1]        
        sell_accuracy = hit_sell_df['sell_hit'].count() / len(hit_test_df[hit_test_df['order_type'] == 'sell'])

        # 전체 정확도
        all_accuracy = (hit_buy_df['buy_hit'].count() + hit_sell_df['sell_hit'].count()) / (len(hit_test_df[hit_test_df['order_type'] == 'buy']) + len(hit_test_df[hit_test_df['order_type'] == 'sell']))

        self.canvas.draw_label_graph(root_path=self.root_path,
                                    df=hit_test_df)
        
        # 통계 다이얼로그 호출
        hit_test = hit_ratio_dialog.hit_ratio(buy_accuracy, sell_accuracy, all_accuracy, self)
        hit_test.showModal()


sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = label_backtest()
    mainWin.show()
    sys.exit(app.exec_())