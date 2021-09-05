from PySide2.QtGui import *
from PySide2.QtWidgets import *
import PySide2
import os
import sys

'''
다이얼로그
1. 기본 백테스팅 결과물 vs 레이블 백테스팅 결과물 비교 통계 결과
'''
class hit_ratio(QDialog):
    def __init__(self, buy_accuracy, sell_accuracy, all_accuracy, parent):
        super().__init__(parent)
        self.title = '레이블 백테스팅 결과'
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

        self.static_table = QTableWidget()
        self.static_table.resize(300, 200)
        # 표의 크기를 지정
        self.static_table.setColumnCount(2)
        self.static_table.setRowCount(3)
        # 열 제목 지정
        self.static_table.setHorizontalHeaderLabels(['이름', '값'])

        # 통계자료표 내용
        self.buy_accuracy = buy_accuracy * 100
        self.sell_accuracy = sell_accuracy * 100
        self.all_accuracy = all_accuracy * 100

        self.static_table.setItem(0, 0, QTableWidgetItem('매수정확도(%)'))
        self.static_table.setItem(1, 0, QTableWidgetItem('매도정확도(%)'))
        self.static_table.setItem(2, 0, QTableWidgetItem('전체정확도(%)'))

        self.static_table.setItem(0, 1, QTableWidgetItem(str(round(self.buy_accuracy, 2)) + '%'))
        self.static_table.setItem(1, 1, QTableWidgetItem(str(round(self.sell_accuracy, 2))+ '%'))
        self.static_table.setItem(2, 1, QTableWidgetItem(str(round(self.all_accuracy, 2)) + '%'))

        # 스크롤 설정
        scroll_bar = QScrollBar(self)
        self.static_table.setVerticalScrollBar(scroll_bar)

        layout.addWidget(self.static_table_label)
        layout.addWidget(self.static_table)

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
        hit_ratio.close(self)

    def closeIt(self):
        hit_ratio.close(self)

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
    mainWin = hit_ratio()
    mainWin.show()
    sys.exit(app.exec_())