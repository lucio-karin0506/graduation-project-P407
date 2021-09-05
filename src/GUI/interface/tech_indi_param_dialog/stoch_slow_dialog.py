from PySide2.QtGui import *
from PySide2.QtWidgets import *
import pandas as pd

import module.indicator.indicator as indicator

'''
다이얼로그
1. stochastic slow 파라미터 설정 다이얼로그
'''
class stoch_slow_Param(QDialog):
    def __init__(self, title, path, parent):
        super().__init__(parent)
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 400

        self.path = path

        self.setWindowTitle(title + ' 파라미터 설정')
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.center()

        layout = QVBoxLayout()
        param_layout = QFormLayout()

        self.price1_label = QLabel('가격 종류1')
        self.price1_option = QComboBox(self)
        self.price1_option.addItem('고가', 'high')
        self.price1_option.addItem('저가', 'low')
        self.price1_option.addItem('종가', 'close')
        self.price1_option.addItem('시가', 'open')

        self.price2_label = QLabel('가격 종류2')
        self.price2_option = QComboBox(self)
        self.price2_option.addItem('저가', 'low')
        self.price2_option.addItem('고가', 'high')
        self.price2_option.addItem('종가', 'close')
        self.price2_option.addItem('시가', 'open')

        self.price3_label = QLabel('가격 종류3')
        self.price3_option = QComboBox(self)
        self.price3_option.addItem('종가', 'close')
        self.price3_option.addItem('시가', 'open')
        self.price3_option.addItem('고가', 'high')
        self.price3_option.addItem('저가', 'low')

        self.fastk_label = QLabel('fastk_period')
        self.fastk_edit = QLineEdit()
        self.fastk_edit.setPlaceholderText('5')

        self.slowk_label = QLabel('slowk_period')
        self.slowk_edit = QLineEdit()
        self.slowk_edit.setPlaceholderText('3')

        self.slowd_label = QLabel('slowd_period')
        self.slowd_edit = QLineEdit()
        self.slowd_edit.setPlaceholderText('3')

        btn_box_hlay = QHBoxLayout()

        self.confirm_btn = QPushButton('확인')
        self.confirm_btn.clicked.connect(self.confirmIt)

        self.close_btn = QPushButton('취소')
        self.close_btn.clicked.connect(self.closeIt)

        param_layout.addRow(self.price1_label, self.price1_option)
        param_layout.addRow(self.price2_label, self.price2_option)
        param_layout.addRow(self.price3_label, self.price3_option)
        param_layout.addRow(self.fastk_label, self.fastk_edit)
        param_layout.addRow(self.slowk_label, self.slowk_edit)
        param_layout.addRow(self.slowd_label, self.slowd_edit)
        param_layout.setVerticalSpacing(45)

        btn_box_hlay.addWidget(self.confirm_btn)
        btn_box_hlay.addWidget(self.close_btn)

        layout.addLayout(param_layout)
        layout.addLayout(btn_box_hlay)
        self.setLayout(layout)

    def confirmIt(self):
        # 1. 기존 csv 파일에 지표 컬럼 추가
        if self.fastk_edit.text() == '' or self.slowk_edit.text() == '' or self.slowd_edit.text() == '':
            QMessageBox.information(self, "메시지", "필요 파라미터가 입력되지 않았습니다.", QMessageBox.Yes)
        else:
            df = pd.read_csv(self.path, index_col='Date')
            gathering_info = {
                                'df': df,
                                'fastk_period': int(self.fastk_edit.text()),
                                'slowk_period': int(self.slowk_edit.text()),
                                'slowd_period': int(self.slowd_edit.text()),
                                'price1': str(self.price1_option.currentData()),
                                'price2': str(self.price2_option.currentData()),
                                'price3': str(self.price3_option.currentData())
                             }

            indicator.add_stoch(gathering_info['df'], gathering_info['fastk_period'], gathering_info['slowk_period'],
                                gathering_info['slowd_period'],
                                gathering_info['price1'], gathering_info['price2'], gathering_info['price3'])
            gathering_info['df'].to_csv(self.path, index_label='Date')

            msg = QMessageBox.information(self, "메시지", "파라미터 설정이 완료되었습니다!", QMessageBox.Yes)
            if msg == QMessageBox.Yes:
                self.close()

    # 화면 중앙 배치
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeIt(self):
        self.close()

    def showModal(self):
        return super().exec_()