from PySide2.QtGui import *
from PySide2.QtWidgets import *
import PySide2
import os
import sys

'''
다이얼로그
1. 내부 및 외부 파일을 병합한 데이터프레임 변환 및 테이블로 보여줌
2. 확인 버튼 클릭 시 csv 파일로 저장
'''
class file_columns(QDialog):
    def __init__(self, df, root_path, infile, outfile, parent):
        super().__init__(parent)
        self.root_path = root_path
        self.title = '병합 파일'
        self.left = 10
        self.top = 10
        self.width = 700
        self.height = 700

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.center()

        layout = QVBoxLayout()

        # 레이블 결과 통계자료표 위젯
        self.columns_label = QLabel('컬럼리스트')

        self.column_list = QTableWidget()
        self.column_list.resize(290, 290)
        self.column_list.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 표의 크기를 지정
        self.column_list.setColumnCount(len(df.columns))
        self.column_list.setRowCount(len(df.index))

        # 열 제목 지정
        self.column_list.setHorizontalHeaderLabels(df.columns)

        # 통계자료표 내용
        self.df = df

        rows = len(self.df.index)
        columns = len(self.df.columns)

        self.column_list.setRowCount(rows)
        self.column_list.setColumnCount(columns)
        
        for i in range(self.column_list.rowCount()):
            for j in range(self.column_list.columnCount()):
                x = '{}'.format(df.iloc[i, j])
                self.column_list.setItem(i, j, QTableWidgetItem(x))

        self.column_list.resizeColumnsToContents()
        self.column_list.resizeRowsToContents()

        # 스크롤 설정
        scroll_bar = QScrollBar(self)
        self.column_list.setVerticalScrollBar(scroll_bar)

        layout.addWidget(self.columns_label)
        layout.addWidget(self.column_list)

        columns_check_hlay = QHBoxLayout()
        
        layout.addLayout(columns_check_hlay)

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

        self.infile = infile
        self.outfile = outfile

    def confirmIt(self):
        os.makedirs(self.root_path + '/mergeFile', exist_ok=True)

        self.df.to_csv(self.root_path + '/mergeFile/' + self.infile + '_' + self.outfile + '_Merge.csv')

        mergeFileDir = self.infile + '_' + self.outfile + '_Merge.csv'
        QMessageBox.information(self, "메시지", f"{mergeFileDir} 파일이 생성되었습니다.", QMessageBox.Yes)
        file_columns.close(self)

    def closeIt(self):
        file_columns.close(self)

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
    mainWin = file_columns()
    mainWin.show()
    sys.exit(app.exec_())