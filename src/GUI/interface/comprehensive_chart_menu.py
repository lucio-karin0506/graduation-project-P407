import PySide2
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

import os
import sys
import pandas as pd
import json
import pathlib

from GUI.interface import comprehensive_chart_graph_canvas
from module.handling_file import get_refined_path

'''
종합 차트 화면 (내부 및 외부 데이터 가져와 다양한 그래프 시각화 제공)
1. 종목 폴더 디렉토리 뷰
2. 그래프 시각화 설정 에디터
3. 그래프 캔버스
'''
class comPreChart(QMainWindow):
    def __init__(self, root_path):
        QMainWindow.__init__(self)
        self.root_path = root_path
        self.title = '종합차트'
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
        vlay = QVBoxLayout(widget)

        # 주문 생성 에디터 위젯 가져오기
        comPreChart = comPreChart_editor(root_path=self.root_path)
        vlay1 = QVBoxLayout()
        vlay1.addWidget(comPreChart)
        vlay.addLayout(vlay1)


class comPreChart_editor(QWidget):
    def __init__(self, root_path, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self.root_path = root_path

        #전체 레이아웃
        layout = QHBoxLayout()

        # Left Layout(vlay1 + vlay2)
        leftLayout = QHBoxLayout()

        # 그래프 시각화 설정 에디터(내부파일, 외부파일, 합성 및 병렬 라디오버튼, 그래프 추가 및 초기화 버튼)
        vlay2 = QVBoxLayout()

        # 내부파일 그룹박스
        self.innerFileGroup = QGroupBox('내부파일')

        self.innerFileEdit = QLineEdit()
        self.innerFileBtn = QPushButton('파일불러오기')
        self.innerFileBtn.clicked.connect(self.get_inFile)
        self.innerFileColBtn = QPushButton('컬럼표시')
        self.innerFileColBtn.clicked.connect(self.display_inFile_column)

        infile_param_lay = QFormLayout()
        self.x1_label = QLabel('x축')
        self.x1_edit = QLineEdit()

        self.y1_label = QLabel('y축')
        self.y1_edit = QLineEdit()

        infile_param_lay.addRow(self.x1_label, self.x1_edit)
        infile_param_lay.addRow(self.y1_label, self.y1_edit)

        # 내부파일 그래프 타입 라디오 옵션
        infile_graph_type_lay = QHBoxLayout()
        self.infile_marker_radio = QRadioButton('산점도')
        self.infile_marker_radio.setChecked(True)
        self.infile_bar_radio = QRadioButton('막대')
        self.infile_plot_radio = QRadioButton('꺾은선')
        self.infile_plot_marker_radio = QRadioButton('꺾은선+점')
        self.infile_candle_radio = QRadioButton('캔들')

        infile_graph_type_lay.addWidget(self.infile_marker_radio)
        infile_graph_type_lay.addWidget(self.infile_bar_radio)
        infile_graph_type_lay.addWidget(self.infile_plot_radio)
        infile_graph_type_lay.addWidget(self.infile_plot_marker_radio)
        infile_graph_type_lay.addWidget(self.infile_candle_radio)

        # 병렬 모드 클릭 시 화면
        self.infile_graph_lay = QVBoxLayout()
        self.infile_x_lay = QHBoxLayout()
        self.infile_y_lay = QHBoxLayout()

        self.infile_x_label = QLabel('x축')
        self.infile_x_label.hide()
        self.infile_x_edit = QLineEdit()
        self.infile_x_edit.hide()
        self.infile_y_label = QLabel('y축')
        self.infile_y_label.hide()
        self.infile_y_edit = QLineEdit()
        self.infile_y_edit.hide()
        self.infile_x_lay.addWidget(self.infile_x_label)
        self.infile_x_lay.addWidget(self.infile_x_edit)
        self.infile_y_lay.addWidget(self.infile_y_label)
        self.infile_y_lay.addWidget(self.infile_y_edit)

        self.infile_graph_lay.addLayout(self.infile_x_lay)
        self.infile_graph_lay.addLayout(self.infile_y_lay)
        self.infile_graph_lay.addLayout(infile_graph_type_lay)

        #----------------------------------------------------------

        self.innerColList = QListWidget()

        innerBox_lay = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.innerFileEdit)
        hbox1.addWidget(self.innerFileBtn)
        hbox1.addWidget(self.innerFileColBtn)

        innerBox_lay.addLayout(hbox1)
        innerBox_lay.addWidget(self.innerColList)
        innerBox_lay.addLayout(infile_param_lay)
        innerBox_lay.addLayout(infile_graph_type_lay)

        # 병렬모드 클릭 시
        innerBox_lay.addLayout(self.infile_graph_lay)
        self.innerFileGroup.setLayout(innerBox_lay)

        # 외부파일 그룹박스
        self.outerFileGroup = QGroupBox('외부파일')

        self.outerFileEdit = QLineEdit()
        self.outerFileBtn = QPushButton('파일불러오기')
        self.outerFileBtn.clicked.connect(self.get_outFile)
        self.outerFileColBtn = QPushButton('컬럼표시')
        self.outerFileColBtn.clicked.connect(self.display_outFile_column)

        outfile_param_lay = QFormLayout()
        self.x2_label = QLabel('x축')
        self.x2_edit = QLineEdit()

        self.y2_label = QLabel('y축')
        self.y2_edit = QLineEdit()

        outfile_param_lay.addRow(self.x2_label, self.x2_edit)
        outfile_param_lay.addRow(self.y2_label, self.y2_edit)

        # 외부파일 그래프 타입 라디오 옵션
        outfile_graph_type_lay = QHBoxLayout()
        self.outfile_marker_radio = QRadioButton('산점도')
        self.outfile_marker_radio.setChecked(True)
        self.outfile_bar_radio = QRadioButton('막대')
        self.outfile_plot_radio = QRadioButton('꺾은선')
        self.outfile_plot_marker_radio = QRadioButton('꺾은선+점')
        self.outfile_candle_radio = QRadioButton('캔들')

        outfile_graph_type_lay.addWidget(self.outfile_marker_radio)
        outfile_graph_type_lay.addWidget(self.outfile_bar_radio)
        outfile_graph_type_lay.addWidget(self.outfile_plot_radio)
        outfile_graph_type_lay.addWidget(self.outfile_plot_marker_radio)
        outfile_graph_type_lay.addWidget(self.outfile_candle_radio)

        # 병렬 모드 클릭 시 화면
        self.outfile_graph_lay = QVBoxLayout()
        self.outfile_x_lay = QHBoxLayout()
        self.outfile_y_lay = QHBoxLayout()

        self.outfile_x_label = QLabel('x축')
        self.outfile_x_label.hide()
        self.outfile_x_edit = QLineEdit()
        self.outfile_x_edit.hide()
        self.outfile_y_label = QLabel('y축')
        self.outfile_y_label.hide()
        self.outfile_y_edit = QLineEdit()
        self.outfile_y_edit.hide()
        self.outfile_x_lay.addWidget(self.outfile_x_label)
        self.outfile_x_lay.addWidget(self.outfile_x_edit)
        self.outfile_y_lay.addWidget(self.outfile_y_label)
        self.outfile_y_lay.addWidget(self.outfile_y_edit)

        self.outfile_graph_lay.addLayout(self.outfile_x_lay)
        self.outfile_graph_lay.addLayout(self.outfile_y_lay)
        self.outfile_graph_lay.addLayout(outfile_graph_type_lay)

        #---------------------------------------------------------

        self.outerColList = QListWidget()
        
        outerBox_lay = QVBoxLayout()
        hbox2 = QHBoxLayout()

        hbox2.addWidget(self.outerFileEdit)
        hbox2.addWidget(self.outerFileBtn)
        hbox2.addWidget(self.outerFileColBtn)

        outerBox_lay.addLayout(hbox2)
        outerBox_lay.addWidget(self.outerColList)
        outerBox_lay.addLayout(outfile_param_lay)
        outerBox_lay.addLayout(outfile_graph_type_lay)

        # 병렬모드 클릭 시
        outerBox_lay.addLayout(self.outfile_graph_lay)
        self.outerFileGroup.setLayout(outerBox_lay)

        # 합성 및 병렬 라디오버튼
        hlay = QHBoxLayout()
        self.graphtypeGroup = QGroupBox('그래프 배치')
        self.mergeRadio = QRadioButton('합성')
        self.mergeRadio.setChecked(True)
        self.parallelRadio = QRadioButton('병렬')
        self.parallelRadio.setChecked(False)
        self.parallelRadio.toggled.connect(self.show_parallelLayout)

        hlay.addWidget(self.mergeRadio)
        hlay.addWidget(self.parallelRadio)

        self.graphtypeGroup.setLayout(hlay)

        # 그래프 x축, y축 파라미터 값 에디트라인(합성 라디오 클릭 시)
        x_hlay = QHBoxLayout()
        
        # 그래프 추가, 초기화 버튼
        self.graph_add_btn = QPushButton('그래프 추가')
        self.graph_add_btn.clicked.connect(self.give_graph_info)
        vlay2.addWidget(self.innerFileGroup)
        vlay2.addWidget(self.graphtypeGroup)
        vlay2.addLayout(x_hlay)
        vlay2.addWidget(self.outerFileGroup)
        vlay2.addWidget(self.graph_add_btn)
        leftLayout.addLayout(vlay2)

        # right layout 그래프 위젯
        rightLayout = QVBoxLayout()

        # 그래프 캔버스 레이아웃 선언
        self.setAcceptDrops(True)        
        self.canvas = comprehensive_chart_graph_canvas.PlotCanvas()        

        self.scroll = QScrollArea()
        mini_vlay = QVBoxLayout()

        mini_vlay.addWidget(self.canvas)

        self.scroll.setLayout(mini_vlay)

        rightLayout.addWidget(self.scroll)

        # 전체 레이아웃 병합 및 조정
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 0)
        layout.setStretchFactor(rightLayout, 1)
        self.setLayout(layout)

    '''
        내부 및 외부 파일 경로를 읽어옴.
    '''
    # 내부파일 경로 정보 얻어옴.
    def get_inFile(self):
        basePath = QFileDialog.getOpenFileName(self, caption='내부파일', dir=self.root_path)
        fileDir = str(basePath[0]).split('/')[-2]

        if (fileDir == 'applyFile' or fileDir == 'AssetmonthFile' or fileDir == 'AssetweekFile' 
        or fileDir == 'AssetyearFile' or fileDir == 'hitTestFile' or fileDir == 'labelFile' 
        or fileDir == 'orderFile' or fileDir == 'statusFile' or fileDir == 'stockFile' 
        or fileDir == 'strategyFile' or fileDir == 'tradingLogFile'):
            self.innerFileEdit.setText(basePath[0])
        else:
            QMessageBox.information(self, "메시지", "P407에서 생성한 내부파일이 아닙니다. 다시 입력해주세요.", QMessageBox.Yes)
            self.innerFileEdit.setText('')

    # 외부파일 경로 정보 얻어옴.
    def get_outFile(self):
        basePath = QFileDialog.getOpenFileName(self, caption='외부파일', dir=self.root_path)
        self.outerFileEdit.setText(basePath[0])

    '''
        1. 내부 및 외부 파일 데이터프레임 전환 및 화면 표시
        2. 기준컬럼 및 x/y축 싱글 에딧라인 위젯에 컬럼 텍스트 표시
    '''
    # 내부파일 데이터프레임 전환 및 화면 표시
    def display_inFile_column(self):
        self.infileType = self.innerFileEdit.text().split('.')[-1]
        self.infileDir = self.innerFileEdit.text().split('/')[-2] # 파일 디렉토리 ex) labelFile, orderFile,...
        self.inFileName = self.innerFileEdit.text().split('/')[-1] # 삼전_d.csv

        if self.infileType == 'csv':
            self.infile_df = pd.read_csv(self.root_path + '/' + self.infileDir + '/' + self.inFileName, index_col=0)
            self.infile_df.reset_index(inplace=True)

        elif self.infileType == 'json':
            file = pathlib.Path(self.root_path + '/' + self.infileDir + '/' + self.inFileName)
            text = file.read_text(encoding='utf-8')
            js = json.loads(text)
            self.infile_df = pd.DataFrame(js)
        else:
            QMessageBox.information(self, "메시지", "올바른 파일형식이 아닙니다. 다시 입력해주세요.", QMessageBox.Yes)

        df_columns = self.infile_df.columns
        self.innerColList.clear()
        self.innerColList.addItems(df_columns)

    # 외부파일 데이터프레임 전환 및 화면 표시
    def display_outFile_column(self):
        self.outfileType = self.outerFileEdit.text().split('.')[-1]
        self.outfileDir = self.outerFileEdit.text().split('/')[-2] # 파일 디렉토리 ex) labelFile, orderFile,...
        self.inFileName = self.outerFileEdit.text().split('/')[-1] # 삼전_d.csv

        if self.outfileType == 'csv':
            self.outfile_df = pd.read_csv(self.outerFileEdit.text(), index_col=0)
            self.outfile_df.reset_index(inplace=True)

        elif self.outfileType == 'json':
            file = pathlib.Path(self.root_path + '/' + self.outfileDir + '/' + self.inFileName)
            text = file.read_text(encoding='utf-8')
            js = json.loads(text)
            self.outfile_df = pd.DataFrame(js)
        else:
            QMessageBox.information(self, "메시지", "올바른 파일형식이 아닙니다. 다시 입력해주세요.", QMessageBox.Yes)

        df_columns = self.outfile_df.columns
        self.outerColList.clear()
        self.outerColList.addItems(df_columns)

    '''
     합성 및 병렬 차트 그리기 위한 graph_canvas로의 정보 전달
    '''
    # 종합차트 그래프 그리기 위한 정보 전달
    def give_graph_info(self):
        # 내부파일 그래프 타입 state
        in_state = ''
        if self.infile_marker_radio.isChecked():
            in_state = 'marker'
        if self.infile_bar_radio.isChecked():
            in_state = 'bar'
        if self.infile_plot_radio.isChecked():
            in_state = 'plot'
        if self.infile_plot_marker_radio.isChecked():
            in_state = 'plot+marker'
        if self.infile_candle_radio.isChecked():
            in_state = 'candle'

        # 외부파일 그래프 타입 state
        out_state = ''
        if self.outfile_marker_radio.isChecked():
            out_state = 'marker'
        if self.outfile_bar_radio.isChecked():
            out_state = 'bar'
        if self.outfile_plot_radio.isChecked():
            out_state = 'plot'
        if self.outfile_plot_marker_radio.isChecked():
            out_state = 'plot+marker'
        if self.outfile_candle_radio.isChecked():
            out_state = 'candle'

        # 그래프 합성 or 병렬 옵션 반영
        # 합성
        if self.mergeRadio.isChecked():
            in_x_grid = self.x1_edit.text()
            out_x_grid = self.x2_edit.text()
            
            in_y_grid = self.y1_edit.text()
            out_y_grid = self.y2_edit.text()

            if self.innerFileEdit.text() == '':
                QMessageBox.information(self, "메시지", "완전한 입력이 아닙니다. 다시 입력해주세요.", QMessageBox.Yes)
            else:
                self.canvas.draw_merge_graph(
                                            root_path=self.root_path,
                                            indf=self.infile_df, 
                                            outdf=self.outfile_df, 
                                            infile_x=in_x_grid, 
                                            infile_y=in_y_grid, 
                                            outfile_x=out_x_grid, 
                                            outfile_y=out_y_grid, 
                                            in_state=in_state, 
                                            out_state=out_state
                                            )

        # 병렬
        elif self.parallelRadio.isChecked():
            # 병렬 모드 클릭 시 각 파일 그래프 x, y 축
            infile_x_grid = self.infile_x_edit.text()
            infile_y_grid = self.infile_y_edit.text()

            outfile_x_grid = self.outfile_x_edit.text()
            outfile_y_grid = self.outfile_y_edit.text()
            
            self.canvas.draw_parallel_graph(
                                            root_path=self.root_path,
                                            indf=self.infile_df, 
                                            outdf=self.outfile_df,
                                            infile_x=infile_x_grid, 
                                            infile_y=infile_y_grid,
                                            outfile_x=outfile_x_grid, 
                                            outfile_y=outfile_y_grid,
                                            in_state=in_state, 
                                            out_state=out_state
                                            )

    # 합성 or 병렬 클릭 시 화면 전환
    def show_parallelLayout(self):
        self.x1_label.hide()
        self.x1_edit.hide()
        self.x2_label.hide()
        self.x2_edit.hide()
        self.y1_label.hide()
        self.y1_edit.hide()
        self.y2_label.hide()
        self.y2_edit.hide()
        
        self.infile_x_label.show()
        self.infile_x_edit.show()
        self.infile_y_label.show()
        self.infile_y_edit.show()
        self.outfile_x_label.show()
        self.outfile_x_edit.show()
        self.outfile_y_label.show()
        self.outfile_y_edit.show()

        if self.mergeRadio.isChecked():
            self.x1_label.show()
            self.x1_edit.show()
            self.x2_label.show()
            self.x2_edit.show()
            self.y1_label.show()
            self.y1_edit.show()
            self.y2_label.show()
            self.y2_edit.show()

            self.infile_x_label.hide()
            self.infile_x_edit.hide()
            self.infile_y_label.hide()
            self.infile_y_edit.hide()
            self.outfile_x_label.hide()
            self.outfile_x_edit.hide()
            self.outfile_y_label.hide()
            self.outfile_y_edit.hide()


sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = comPreChart()
    mainWin.show()
    sys.exit(app.exec_())