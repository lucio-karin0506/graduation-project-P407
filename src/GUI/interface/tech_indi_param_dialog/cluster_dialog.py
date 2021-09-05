from PySide2.QtGui import *
from PySide2.QtWidgets import *
import pandas as pd

import module.indicator.indicator as indicator

'''
다이얼로그
1. 클러스터 파라미터 설정 다이얼로그
'''
class cluster_Param(QDialog):
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

        self.n_clusters_label = QLabel('군집개수')
        self.n_clusters_edit = QLineEdit()

        self.target_label = QLabel('군집대상')
        self.target_option = QComboBox(self)
        self.target_option.addItem('종가', 'close')
        self.target_option.addItem('시가', 'open')
        self.target_option.addItem('고가', 'high')
        self.target_option.addItem('저가', 'low')

        self.period_label = QLabel('클러스터링 기간')
        self.period_edit = QLineEdit()
        self.period_edit.setPlaceholderText('1y')

        self.slide_size_label = QLabel('슬라이드 기간')
        self.slide_size_edit = QLineEdit()
        self.slide_size_edit.setPlaceholderText('1m')

        self.explain_label = QLabel('클러스터링 기간: 숫자와 y, m, d를 조합하여 입력(대소문자 구분없음) 1년: 1y, 6개월: 6m, 30일: 30d\n슬라이드 기간: 숫자와 y, m, d를 조합하여 입력(대소문자 구분없음) 1년: 1y, 1개월: 1m, 15일: 15d')
        self.explain_label.setGeometry(200, 250, 100, 50)
        self.explain_label.setWordWrap(True)

        btn_box_hlay = QHBoxLayout()

        self.confirm_btn = QPushButton('확인')
        self.confirm_btn.clicked.connect(self.confirmIt)

        self.close_btn = QPushButton('취소')
        self.close_btn.clicked.connect(self.closeIt)

        param_layout.addRow(self.n_clusters_label, self.n_clusters_edit)
        param_layout.addRow(self.target_label, self.target_option)
        param_layout.addRow(self.period_label, self.period_edit)
        param_layout.addRow(self.slide_size_label, self.slide_size_edit)
        param_layout.setVerticalSpacing(45)

        btn_box_hlay.addWidget(self.confirm_btn)
        btn_box_hlay.addWidget(self.close_btn)

        layout.addLayout(param_layout)
        layout.addWidget(self.explain_label)
        layout.addLayout(btn_box_hlay)
        self.setLayout(layout)

    def confirmIt(self):
        # 기존 csv 파일에 지표 컬럼 추가
        if self.n_clusters_edit.text() == '' or self.period_edit.text() == '' or self.slide_size_edit.text() == '':
            QMessageBox.information(self, "메시지", "필요 파라미터가 입력되지 않았습니다.", QMessageBox.Yes)
        else:
            df = pd.read_csv(self.path, index_col='Date')
            gathering_info = {
                                'df': df,
                                'n_clusters': int(self.n_clusters_edit.text()),
                                'target': str(self.target_option.currentData()),
                                'period': str(self.period_edit.text()),
                                'slide_size': str(self.slide_size_edit.text())
                             }

            indicator.add_clustering(gathering_info['df'], gathering_info['n_clusters'], gathering_info['target'],
                                    gathering_info['period'], gathering_info['slide_size'])
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