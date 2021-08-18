from PySide2.QtGui import *
from PySide2.QtWidgets import *
import PySide2
import os
import sys
import pandas as pd

import module.labeler.labeler as label_indicator

'''
다이얼로그
1. stochastic slow 레이블 파라미터 설정 다이얼로그
'''
class stochastic_slow_label_Param(QDialog):

    def __init__(self, title, path, parent):
        super().__init__(parent)
        self.path = path

        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 400

        self.setWindowTitle(title + ' 파라미터 설정')
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.center()

        layout = QVBoxLayout()
        param_layout = QFormLayout()

        self.fastk_period_label = QLabel('fastk_period', self)
        self.fastk_period_edit = QLineEdit(self)
        self.fastk_period_edit.setPlaceholderText('5')

        self.slowk_period_label = QLabel('slowk_period', self)
        self.slowk_period_edit = QLineEdit(self)
        self.slowk_period_edit.setPlaceholderText('3')

        self.slowd_period_label = QLabel('slowd_period', self)
        self.slowd_period_edit = QLineEdit(self)
        self.slowd_period_edit.setPlaceholderText('3')

        self.window_label = QLabel('윈도우사이즈', self)
        self.window_edit = QLineEdit(self)
        self.window_edit.setPlaceholderText('0')

        btn_box_hlay = QHBoxLayout()

        self.confirm_btn = QPushButton('확인', self)
        self.confirm_btn.clicked.connect(self.confirmIt)

        self.close_btn = QPushButton('취소', self)
        self.close_btn.clicked.connect(self.closeIt)

        param_layout.addRow(self.fastk_period_label, self.fastk_period_edit)
        param_layout.addRow(self.slowk_period_label, self.slowk_period_edit)
        param_layout.addRow(self.slowd_period_label, self.slowd_period_edit)
        param_layout.addRow(self.window_label, self.window_edit)
        param_layout.setVerticalSpacing(45)

        btn_box_hlay.addWidget(self.confirm_btn)
        btn_box_hlay.addWidget(self.close_btn)

        layout.addLayout(param_layout)
        layout.addLayout(btn_box_hlay)
        self.setLayout(layout)

    def confirmIt(self):
        # 1. 기존 csv 파일에 지표 컬럼 추가
        df = pd.read_csv(self.path, index_col='Date')
        gathering_info = {'df': df,
                          'fastk_period': int(self.fastk_period_edit.text()),
                          'slowk_period': int(self.slowk_period_edit.text()),
                          'slowd_period': int(self.slowd_period_edit.text()),
                          'window_size': int(self.window_edit.text())
                         }

        label_indicator.add_stoch_cross(gathering_info['df'], gathering_info['fastk_period'],
                              gathering_info['slowk_period'], gathering_info['slowd_period'], gathering_info['window_size'])
        gathering_info['df'].to_csv(self.path, index_label='Date')

        msg = QMessageBox.information(self, "메시지", "파라미터 설정이 완료되었습니다!", QMessageBox.Yes)
        if msg == QMessageBox.Yes:
            stochastic_slow_label_Param.close(self)
        # 2. 그래프 생성
        # 3. 지표 리스트에 지표 목록 생성

    # 화면 중앙 배치
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeIt(self):
        stochastic_slow_label_Param.close(self)

    def showModal(self):
        return super().exec_()