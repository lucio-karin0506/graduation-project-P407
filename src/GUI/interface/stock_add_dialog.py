from PySide2.QtGui import *
from PySide2.QtWidgets import *
import PySide2
import os
import sys
import pandas as pd

from module.gatherer.gatherer import Gatherer
from GUI.interface import directory_tree

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
        
        # 종목 이름 검색
        upperLayout = QHBoxLayout()
        self.stock_code_label = QLabel('종목이름')

        self.stock_code_edit = QLineEdit()
        self.stock_code_edit.textChanged.connect(self.update_display)

        # 검색어 자동완성
        self.completer = QCompleter(widget_names)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.stock_code_edit.setCompleter(self.completer)

        upperLayout.addWidget(self.stock_code_label)
        upperLayout.addWidget(self.stock_code_edit)
        layout.addLayout(upperLayout)

        # 종목 이름 리스트 위젯에 삽입
        self.stock_box = QListWidget()
        for name in widget_names:
            self.stock_box.addItem(name)

        # 스크롤 설정
        scroll_bar = QScrollBar(self)
        self.stock_box.setVerticalScrollBar(scroll_bar)
        
        # 종목 이름 리스트 아이템 선택
        self.stock_box.itemSelectionChanged.connect(self.on_change)

        # 종목 이름 리스트 위젯 레이아웃 설정
        stock_box_layout = QVBoxLayout()
        stock_box_layout.addWidget(self.stock_box)
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

    # 종목 클릭 시 해당 종목 텍스트 받아옴
    def on_change(self):
        self.stock_box_item = ''
        for item in self.stock_box.selectedItems():
            self.stock_box_item = item.text()
            self.stock_code_edit.setText(str(self.stock_box_item))

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

    # 종목 다운로드 실행
    def stock_download(self):
        self.progress.setMaximum(len(self.stock_code_edit.text()))

        stock_code = str(self.stock_code_edit.text())[0:6]
        start_date = '1990-01-01'
        end_date = 'today'
        self.run_gathering(stock_code, start_date, end_date)

        self.progress.setValue(len(self.stock_code_edit.text()))

        msg = QMessageBox.information(self, "메시지", "다운로드가 완료되었습니다!", QMessageBox.Yes)
        if msg == QMessageBox.Yes:
            stock_add.close(self)

    def run_gathering(self, code, start_date='', end_date=''):        
        self.gathering.get_stock(code, start_date, end_date, 'd', self.root_path)
        self.gathering.get_stock(code, start_date, end_date, 'w', self.root_path) 

    def closeIt(self):
        stock_add.close(self)

    def showModal(self):
        return super().exec_()


sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = stock_add()
    mainWin.show()
    sys.exit(app.exec_())