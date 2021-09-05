from PySide2.QtGui import *
from PySide2.QtWidgets import *
import pandas as pd

import module.indicator.indicator as indicator

'''
다이얼로그
1. macd 파라미터 설정 다이얼로그
'''
class macd_Param(QDialog):
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

        self.price_label = QLabel('가격 종류')
        self.price_option = QComboBox(self)
        self.price_option.addItem('종가', 'close')
        self.price_option.addItem('시가', 'open')
        self.price_option.addItem('고가', 'high')
        self.price_option.addItem('저가', 'low')

        self.fast_label = QLabel('fast_period')
        self.fast_edit = QLineEdit()
        self.fast_edit.setPlaceholderText('12')

        self.slow_label = QLabel('slow_period')
        self.slow_edit = QLineEdit()
        self.slow_edit.setPlaceholderText('26')

        self.signal_label = QLabel('signal_period')
        self.signal_edit = QLineEdit()
        self.signal_edit.setPlaceholderText('9')

        btn_box_hlay = QHBoxLayout()

        self.confirm_btn = QPushButton('확인')
        self.confirm_btn.clicked.connect(self.confirmIt)

        self.close_btn = QPushButton('취소')
        self.close_btn.clicked.connect(self.closeIt)

        param_layout.addRow(self.price_label, self.price_option)
        param_layout.addRow(self.fast_label, self.fast_edit)
        param_layout.addRow(self.slow_label, self.slow_edit)
        param_layout.addRow(self.signal_label, self.signal_edit)
        param_layout.setVerticalSpacing(45)

        btn_box_hlay.addWidget(self.confirm_btn)
        btn_box_hlay.addWidget(self.close_btn)

        layout.addLayout(param_layout)
        layout.addLayout(btn_box_hlay)
        self.setLayout(layout)

    def confirmIt(self):
        # 1. 기존 csv 파일에 지표 컬럼 추가
        if self.fast_edit.text() == '' or self.slow_edit.text() == '' or self.signal_edit.text() == '':
            QMessageBox.information(self, "메시지", "필요 파라미터가 입력되지 않았습니다.", QMessageBox.Yes)
        else:
            df = pd.read_csv(self.path, index_col='Date')
            gathering_info = {
                                'df': df,
                                'fast_period': int(self.fast_edit.text()),
                                'slow_period': int(self.slow_edit.text()),
                                'signal_period': int(self.signal_edit.text()),
                                'price': str(self.price_option.currentData())
                            }

            indicator.add_macd(gathering_info['df'], gathering_info['fast_period'], gathering_info['slow_period'],
                                gathering_info['signal_period'], gathering_info['price'])
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