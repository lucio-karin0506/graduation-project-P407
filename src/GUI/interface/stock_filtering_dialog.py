from PySide2.QtGui import *
from PySide2.QtWidgets import *
import PySide2
import os
import sys
import pandas as pd

'''
다이얼로그
1. 기본 백테스팅 결과물 vs 레이블 백테스팅 결과물 비교 통계 결과
'''
class filter_result(QDialog):
    def __init__(self, df, parent):
        super().__init__(parent)
        self.title = '종목 필터링 결과'
        self.left = 10
        self.top = 10
        self.width = 500
        self.height = 400

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.center()

        layout = QVBoxLayout()

        # 레이블 결과 통계자료표 위젯
        self.static_table_label = QLabel('통계자료표')

        self.stock_trading_list = QTableWidget()
        self.stock_trading_list.resize(290, 290)
        self.stock_trading_list.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 표의 크기를 지정
        self.stock_trading_list.setColumnCount(6)
        self.stock_trading_list.setRowCount(1)

        # 열 제목 지정
        self.stock_trading_list.setHorizontalHeaderLabels(['종목명', '최종 수익률', '최고 수익률', 
                                                        '최저 수익률', '매수 횟수', '매도 횟수'])

        # 통계자료표 내용
        self.df = df

        rows = len(self.df.index)
        columns = len(self.df.columns)

        self.stock_trading_list.setRowCount(rows)
        self.stock_trading_list.setColumnCount(columns)
        
        for i in range(self.stock_trading_list.rowCount()):
            for j in range(self.stock_trading_list.columnCount()):
                x = '{}'.format(df.iloc[i, j])
                self.stock_trading_list.setItem(i, j, QTableWidgetItem(x))

        self.stock_trading_list.resizeColumnsToContents()
        self.stock_trading_list.resizeRowsToContents()

        # 스크롤 설정
        scroll_bar = QScrollBar(self)
        self.stock_trading_list.setVerticalScrollBar(scroll_bar)

        layout.addWidget(self.static_table_label)
        layout.addWidget(self.stock_trading_list)

        # 확인, 취소 버튼
        buttonLayout = QHBoxLayout()
        self.add = QPushButton('확인')
        self.add.clicked.connect(self.confirmIt)

        self.close = QPushButton('취소')
        self.close.clicked.connect(self.closeIt)

        buttonLayout.addWidget(self.add)
        buttonLayout.addWidget(self.close)

        layout.addLayout(buttonLayout)
        self.setLayout(layout)
        
    def update_display(self, text):
        for widget in self.widgets:
            if text.lower() in widget.name.lower():
                widget.show()
            else:
                widget.hide()

    def confirmIt(self):
        filter_result.close(self)

    def closeIt(self):
        filter_result.close(self)

    def showModal(self):
        return super().exec_()

    # 화면 중앙 배치
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = filter_result()
    mainWin.show()
    sys.exit(app.exec_())