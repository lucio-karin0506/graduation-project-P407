from PySide2.QtGui import *
from PySide2.QtWidgets import *
import pandas as pd

import module.labeler.labeler as label_indicator

'''
다이얼로그
1. macd 레이블 파라미터 설정 다이얼로그
'''
class macd_label_Param(QDialog):
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

        self.target_label = QLabel('레이블 대상', self)
        self.target_option = QComboBox(self)
        self.target_option.addItem('종가', 'close')
        self.target_option.addItem('시가', 'open')
        self.target_option.addItem('고가', 'high')
        self.target_option.addItem('저가', 'low')

        self.short_period_label = QLabel('단기지수이평기간', self)
        self.short_period_edit = QLineEdit(self)
        self.short_period_edit.setPlaceholderText('12')

        self.long_period_label = QLabel('장기지수이평기간', self)
        self.long_period_edit = QLineEdit(self)
        self.long_period_edit.setPlaceholderText('26')

        btn_box_hlay = QHBoxLayout()

        self.confirm_btn = QPushButton('확인', self)
        self.confirm_btn.clicked.connect(self.confirmIt)

        self.close_btn = QPushButton('취소', self)
        self.close_btn.clicked.connect(self.closeIt)

        param_layout.addRow(self.target_label, self.target_option)
        param_layout.addRow(self.short_period_label, self.short_period_edit)
        param_layout.addRow(self.long_period_label, self.long_period_edit)
        param_layout.setVerticalSpacing(45)

        btn_box_hlay.addWidget(self.confirm_btn)
        btn_box_hlay.addWidget(self.close_btn)

        layout.addLayout(param_layout)
        layout.addLayout(btn_box_hlay)
        self.setLayout(layout)

    def confirmIt(self):
        # 1. 기존 csv 파일에 지표 컬럼 추가
        if self.short_period_edit.text() == '' or self.long_period_edit.text() == '':
            QMessageBox.information(self, "메시지", "필요 파라미터가 입력되지 않았습니다.", QMessageBox.Yes)
        else:
            df = pd.read_csv(self.path, index_col='Date')
            gathering_info = {
                                'df': df,
                                'short': int(self.short_period_edit.text()),
                                'long': int(self.long_period_edit.text()),
                                'target': str(self.target_option.currentData())
                            }

            label_indicator.add_macd_classify(gathering_info['df'], gathering_info['short'], gathering_info['long'],
                                    gathering_info['target'])
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