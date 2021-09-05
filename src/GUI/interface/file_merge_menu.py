import PySide2
import sys
import os
import pandas as pd
import json
import pathlib

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from GUI.interface import file_columns_dialog
from module.handling_file import get_refined_path

'''
종목 차트 화면
'''
class file_merge(QMainWindow):
    def __init__(self, root_path):
        self.root_path = root_path
        QMainWindow.__init__(self)
        self.title = '파일병합'
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
        hlay = QHBoxLayout(widget)

        # 그래프 및 전체 위젯 가져오기
        m = file_merge_editor(root_path=self.root_path)
        hlay.addWidget(m)


class file_merge_editor(QWidget):
    def __init__(self, root_path, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.root_path = root_path

        #전체 레이아웃
        layout = QVBoxLayout()

        '''
            file_edit layout 
            1. 내부 파일 & 외부 파일 입력 위젯
            2. 라벨, 싱글라인에디터, 파일불러오기 버튼, 컬럼표시 버튼
        '''
        file_edit_lay = QHBoxLayout()

        self.inFile_label = QLabel('내부파일')
        self.inFile_edit = QLineEdit()
        self.setAcceptDrops(True)
        self.inFile_edit.setReadOnly(False)

        self.inFile_get_file_btn = QPushButton('파일불러오기')
        self.inFile_get_file_btn.clicked.connect(self.get_inFile)

        self.inFile_col_btn = QPushButton('컬럼표시')
        self.inFile_col_btn.clicked.connect(self.display_inFile_column)

        self.outFile_label = QLabel('외부파일')
        self.outFile_edit = QLineEdit()
        self.setAcceptDrops(True)
        self.outFile_edit.setReadOnly(False)

        self.outFile_get_file_btn = QPushButton('파일불러오기')
        self.outFile_get_file_btn.clicked.connect(self.get_outFile)

        self.outFile_col_btn = QPushButton('컬럼표시')
        self.outFile_col_btn.clicked.connect(self.display_outFile_column)

        file_edit_lay.addWidget(self.inFile_label)
        file_edit_lay.addWidget(self.inFile_edit)
        file_edit_lay.addWidget(self.inFile_get_file_btn)
        file_edit_lay.addWidget(self.inFile_col_btn)

        file_edit_lay.addWidget(self.outFile_label)
        file_edit_lay.addWidget(self.outFile_edit)
        file_edit_lay.addWidget(self.outFile_get_file_btn)
        file_edit_lay.addWidget(self.outFile_col_btn)
        
        '''
            1. file_merge_lay
            2. 내, 외부 파일 컬럼 표시 테이블 위젯
            3. 병합 옵션 체크박스 2개(조인 옵션, 공백 데이터 옵션)
        '''
        file_merge_lay = QHBoxLayout()

        # 내부 파일 컬럼 표시 테이블
        inFile_table_lay = QVBoxLayout()
        self.inFile_col_label = QLabel('내부파일')
        self.inFile_col_table = QTableWidget()
        self.inFile_col_table.resize(290, 290)
        self.inFile_col_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        in_join_col_lay = QHBoxLayout()
        self.inFile_join_col_label = QLabel('조인컬럼')
        self.inFile_join_col_edit = QLineEdit()

        in_join_col_lay.addWidget(self.inFile_join_col_label)
        in_join_col_lay.addWidget(self.inFile_join_col_edit)
        
        inFile_table_lay.addWidget(self.inFile_col_label)
        inFile_table_lay.addWidget(self.inFile_col_table)
        inFile_table_lay.addLayout(in_join_col_lay)

        # 외부 파일 컬럼 표시 테이블
        outFile_table_lay = QVBoxLayout()
        self.outFile_col_label = QLabel('외부파일')
        self.outFile_col_table = QTableWidget()
        self.outFile_col_table.resize(290, 290)
        self.outFile_col_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        out_join_col_lay = QHBoxLayout()
        self.outFile_join_col_label = QLabel('조인컬럼')
        self.outFile_join_col_edit = QLineEdit()

        out_join_col_lay.addWidget(self.outFile_join_col_label)
        out_join_col_lay.addWidget(self.outFile_join_col_edit)

        outFile_table_lay.addWidget(self.outFile_col_label)
        outFile_table_lay.addWidget(self.outFile_col_table)
        outFile_table_lay.addLayout(out_join_col_lay)

        # 병합 온션 체크박스 2개, 파일병합 버튼
        file_merge_opt_lay = QVBoxLayout()

        # 데이터프로엠 조인 옵션 그룹박스
        self.df_join_groupbox = QGroupBox('조인 옵션')
        df_join_layout = QVBoxLayout()

        self.df_join_inner_radio = QRadioButton('inner')
        self.df_join_inner_radio.setCheckable(False)
        self.df_join_outer_radio = QRadioButton('outer')
        self.df_join_outer_radio.setCheckable(False)
        self.df_join_left_radio = QRadioButton('left')
        self.df_join_left_radio.setCheckable(True)
        self.df_join_left_radio.setChecked(True)
        self.df_join_right_radio = QRadioButton('right')
        self.df_join_right_radio.setCheckable(False)

        df_join_layout.addWidget(self.df_join_inner_radio)
        df_join_layout.addWidget(self.df_join_outer_radio)
        df_join_layout.addWidget(self.df_join_left_radio)
        df_join_layout.addWidget(self.df_join_right_radio)

        self.df_join_groupbox.setLayout(df_join_layout)

        # 공백 데이터 옵션 체크박스 그룹박스
        self.null_data_groupbox = QGroupBox('공백데이터 옵션')
        null_data_layout = QVBoxLayout()

        self.null_radio = QRadioButton('Null')
        self.null_radio.setChecked(True)
        self.avg_radio = QRadioButton('평균값')
        self.forward_radio = QRadioButton('forwardfill')
        self.backward_radio = QRadioButton('backwardfill')
        self.default_radio = QRadioButton('default')
        self.default_edit = QLineEdit()
        self.default_edit.setEnabled(False)
        self.default_radio.toggled.connect(self.default_edit.setEnabled)

        null_data_layout.addWidget(self.null_radio)
        null_data_layout.addWidget(self.avg_radio)
        null_data_layout.addWidget(self.forward_radio)
        null_data_layout.addWidget(self.backward_radio)
        null_data_layout.addWidget(self.default_radio)
        null_data_layout.addWidget(self.default_edit)
        
        self.null_data_groupbox.setLayout(null_data_layout)

        # 병합 미리보기, 실행 버튼
        self.merge_display_btn = QPushButton('미리보기')
        self.merge_display_btn.clicked.connect(self.merge_file)

        # 조인옵션 그룹박스 + 공백 옵션 그룹박스 + 미리보기 버튼
        file_merge_opt_lay.addWidget(self.df_join_groupbox)
        file_merge_opt_lay.addWidget(self.null_data_groupbox)
        file_merge_opt_lay.addWidget(self.merge_display_btn)

        # 내부 + file_merge_opt_lay + 외부
        file_merge_lay.addLayout(inFile_table_lay)
        file_merge_lay.addLayout(file_merge_opt_lay)
        file_merge_lay.addLayout(outFile_table_lay)
        file_merge_lay.setStretchFactor(inFile_table_lay, 1)
        file_merge_lay.setStretchFactor(file_merge_opt_lay, 0)
        file_merge_lay.setStretchFactor(outFile_table_lay, 1)

        # 전체 레이아웃 병합 및 조정
        layout.addLayout(file_edit_lay)
        layout.addLayout(file_merge_lay)
        layout.setStretchFactor(file_edit_lay, 0)
        layout.setStretchFactor(file_merge_lay, 1)
        self.setLayout(layout)

    '''
        내부 및 외부파일 읽어옴.
    '''
    def get_inFile(self):
        basePath = QFileDialog.getOpenFileName(self, caption='내부파일', dir=self.root_path)
        fileDir = str(basePath[0]).split('/')[-2]

        if (fileDir == 'applyFile' or fileDir == 'AssetmonthFile' or fileDir == 'AssetweekFile' 
        or fileDir == 'AssetyearFile' or fileDir == 'hitTestFile' or fileDir == 'labelFile' 
        or fileDir == 'orderFile' or fileDir == 'statusFile' or fileDir == 'stockFile' 
        or fileDir == 'strategyFile' or fileDir == 'tradingLogFile'):
            self.inFile_edit.setText(basePath[0])
        else:
            QMessageBox.information(self, "메시지", "P407에서 생성한 내부파일이 아닙니다. 다시 입력해주세요.", QMessageBox.Yes)
            self.inFile_edit.setText('')

    def get_outFile(self):
        basePath = QFileDialog.getOpenFileName(self, caption='외부파일', dir=self.root_path)
        self.outFile_edit.setText(basePath[0])

    '''
        내부 및 외부 파일 drag & drop 하여 파일 텍스트 표시
    '''
    def dropEvent(self, e: QDropEvent):
        self.fileDir = e.mimeData().text().split('/')[-2] # 파일 디렉토리 ex) labelFile, orderFile,...
        self.fileName = e.mimeData().text().split('/')[-1] # 삼전_d.csv
        self.fileType = self.fileName.split('.')[-1]  # csv, json

        if (self.fileDir == 'applyFile' or self.fileDir == 'AssetmonthFile' or self.fileDir == 'AssetweekFile' 
        or self.fileDir == 'AssetyearFile' or self.fileDir == 'hitTestFile' or self.fileDir == 'labelFile' 
        or self.fileDir == 'orderFile' or self.fileDir == 'statusFile' or self.fileDir == 'stockFile' 
        or self.fileDir == 'strategyFile' or self.fileDir == 'tradingLogFile'):
            self.inFile_edit.setText(e.mimeData().text())

        else:
            self.outFile_edit.setText(e.mimeData().text())

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    # 사용자가 입력한 내부파일에 대하여 컬럼 리스트 보여줌
    def display_inFile_column(self):
        fileDir = self.inFile_edit.text()
        self.inFileName = self.inFile_edit.text().split('/')[-1] # 삼전_d.csv

        # 다이얼로그 종료 시 저장할 때 필요한 이름 정보 전달에 사용
        self.inFile = self.inFileName.split('.')[0]
        fileType = self.inFile_edit.text().split('.')[-1] # csv, json

        if fileType == 'csv':
            df = pd.read_csv(fileDir, index_col=0)
            df.reset_index(inplace=True)
        elif fileType == 'json':
            file = pathlib.Path(fileDir)
            text = file.read_text(encoding='utf-8')
            js = json.loads(text)
            df = pd.DataFrame(js)
        else:
            QMessageBox.information(self, "메시지", "올바른 파일형식이 아닙니다. 다시 입력해주세요.", QMessageBox.Yes)

        # 표의 크기를 지정
        self.inFile_col_table.setColumnCount(len(df.columns))
        self.inFile_col_table.setRowCount(len(df.index))

        # 열 제목 지정
        self.inFile_col_table.setHorizontalHeaderLabels(df.columns)

        # 통계자료표 내용
        self.inFile_df = df

        rows = len(self.inFile_df.index)
        columns = len(self.inFile_df.columns)

        self.inFile_col_table.setRowCount(rows)
        self.inFile_col_table.setColumnCount(columns)
        
        for i in range(self.inFile_col_table.rowCount()):
            for j in range(self.inFile_col_table.columnCount()):
                x = '{}'.format(df.iloc[i, j])
                self.inFile_col_table.setItem(i, j, QTableWidgetItem(x))

        self.inFile_col_table.resizeColumnsToContents()
        self.inFile_col_table.resizeRowsToContents()

        # 스크롤 설정
        scroll_bar = QScrollBar(self)
        self.inFile_col_table.setVerticalScrollBar(scroll_bar)

    # 사용자가 입력한 외부파일에 대하여 컬럼 리스트 보여줌
    def display_outFile_column(self):
        fileDir = self.outFile_edit.text()
        fileType = self.outFile_edit.text().split('.')[-1] # csv, json
        self.outFileName = self.outFile_edit.text().split('/')[-1]

        # 다이얼로그에 파일 저장 시 필요한 이름
        self.outFile = self.outFileName.split('.')[0]

        if fileType == 'csv':
            df = pd.read_csv(fileDir, index_col=0)
            df.reset_index(inplace=True)

        elif fileType == 'json':
            file = pathlib.Path(fileDir)
            text = file.read_text(encoding='utf-8')
            js = json.loads(text)
            df = pd.DataFrame(js)
        else:
            QMessageBox.information(self, "메시지", "올바른 파일형식이 아닙니다. 다시 입력해주세요.", QMessageBox.Yes)

        # 표의 크기를 지정
        self.outFile_col_table.setColumnCount(len(df.columns))
        self.outFile_col_table.setRowCount(len(df.index))

        # 열 제목 지정
        self.outFile_col_table.setHorizontalHeaderLabels(df.columns)

        # 통계자료표 내용
        self.outFile_df = df

        rows = len(self.outFile_df.index)
        columns = len(self.outFile_df.columns)

        self.outFile_col_table.setRowCount(rows)
        self.outFile_col_table.setColumnCount(columns)
        
        for i in range(self.outFile_col_table.rowCount()):
            for j in range(self.outFile_col_table.columnCount()):
                x = '{}'.format(df.iloc[i, j])
                self.outFile_col_table.setItem(i, j, QTableWidgetItem(x))

        self.outFile_col_table.resizeColumnsToContents()
        self.outFile_col_table.resizeRowsToContents()

        # 스크롤 설정
        scroll_bar = QScrollBar(self)
        self.outFile_col_table.setVerticalScrollBar(scroll_bar)

    '''
        입력받은 내부 및 외부 파일들을 병합하여 데이터프레임으로 변환
        데이터프레임 병합은 merge 메소드 파라미터 기준으로 시행
    '''
    def merge_file(self):
        self.left_join = ''
        self.left_on = self.inFile_join_col_edit.text()
        self.right_on = self.outFile_join_col_edit.text()

        # 조인 옵션 반영
        if self.df_join_left_radio.isChecked():
            self.left_join = 'left'

        if self.left_on == '' or self.right_on == '':
            QMessageBox.information(self, "메시지", "조인할 컬럼을 지정하지 않았습니다. 컬럼명을 입력해주세요.", QMessageBox.Yes)

        if self.inFile_df[self.left_on].dtype == self.outFile_df[self.right_on].dtype:
            merge_df = pd.merge(self.inFile_df, self.outFile_df, how=self.left_join, left_on=str(self.left_on), right_on=str(self.right_on))            
        else:
            QMessageBox.information(self, "메시지", "두 컬럼의 데이터 종류가 다릅니다. 다시 입력해주세요.", QMessageBox.Yes)
            self.inFile_join_col_edit.setText('')
            self.outFile_join_col_edit.setText('')       

        # 공백 데이터 옵션 반영
        if self.null_radio.isChecked():
            merge_df = merge_df
        if self.avg_radio.isChecked():
            merge_df.fillna(merge_df.mean(), inplace=True)
        if self.forward_radio.isChecked():
            merge_df.fillna(method='ffill', inplace=True)
        if self.backward_radio.isChecked():
            merge_df.fillna(method='bfill', inplace=True)
        if self.default_radio.isChecked():
            default_val = self.default_edit.text()
            merge_df.fillna(int(default_val), inplace=True)

        self.display_merge_df(merge_df)

    '''
        데이터프레임 표시하는 다이얼로그에 정보 전달
    '''
    def display_merge_df(self, df):
        merge_dialog = file_columns_dialog.file_columns(df, self.root_path, self.inFile, self.outFile, self)
        merge_dialog.showModal()

        
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = file_merge()
    mainWin.show()
    sys.exit(app.exec_())