from logging import root
import platform
import PySide2
import sys
import os

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

from GUI.interface import (stock_chart_menu, file_merge_menu, simple_strategy_menu,
                                basic_backtest_menu, label_backtest_menu, comprehensive_chart_menu,
                                stock_filtering_menu, debug_log, directory_tree)

# 운영체제 환경 따른 경로 설정
if platform.system() == 'Windows':
    # Windows pyside env path set
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
    dirname = os.path.dirname(PySide2.__file__)
    plugin_path = os.path.join(dirname, 'plugins', 'platforms')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

elif platform.system() == 'Darwin':
    # mac os pyside env path set
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
    dirname = os.path.dirname(PySide2.__file__)
    plugin_path = os.path.join(dirname, 'Qt', 'plugins', 'platforms')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


'''
전체 GUI 화면
1. 메뉴 바(종목차트, 자료정제, 거래전략(단순전략, 복합전략), 백테스트(기본, 레이블링), 종합차트, 종목필터링)
2. 탭 호스트
'''
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.title = 'P407'
        self.left = 10
        self.top = 10
        self.width = 1600
        self.height = 900

        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('p407-icon.ico'))
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.center()

        self.statusBar().showMessage('Ready')

        # 현재 파일 경로
        self.root_path = ''

        # 탭 생성
        self.tabs = QTabWidget(self, tabsClosable=True)
        self.tabs.tabCloseRequested.connect(self.onTabCloseRequested)
        self.setCentralWidget(self.tabs)

        # tree widget dock widget
        self.trees_widget = directory_tree.DirectoryTreeView()
        self.dockTree = QDockWidget('Directory Tree', self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockTree)
        self.dockTree.setWidget(self.trees_widget)

        # Debug & Processing Log text output dock widget
        self.logDock = QDockWidget("Message Box", self)
        self.logDock.setAllowedAreas(Qt.LeftDockWidgetArea |
                                     Qt.RightDockWidgetArea |
                                     Qt.BottomDockWidgetArea)
        self.textBrowser = QTextBrowser()
        self._stdout = debug_log.debug_log()
        self._stdout.start()
        self._stdout.printOccur.connect(lambda x: self._append_text(x))
        self.logInfo = self.textBrowser
        self.logDock.setWidget(self.logInfo)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.logDock)

        # 메인메뉴 바
        self.createMenus()

    '''
        메인메뉴 셋팅 함수
    '''
    def createMenus(self):
        mainMenu = self.menuBar()
        mainMenu.setNativeMenuBar(False)

        # 프로젝트 메뉴
        projectMenu = mainMenu.addMenu('프로젝트')

        newProject = QAction('&생성', self)
        newProject.setStatusTip("생성")
        newProject.triggered.connect(self.loadProject)

        getProject = QAction('&불러오기', self)
        getProject.setStatusTip("불러오기")
        getProject.triggered.connect(self.loadProject)

        exitProject = QAction('&종료', self)
        exitProject.triggered.connect(self.close)

        projectMenu.addAction(newProject)
        projectMenu.addAction(getProject)
        projectMenu.addAction(exitProject)

        # 종목차트 메뉴
        chartMenu = mainMenu.addMenu('종목차트')
        chart_Menu = QAction('&종목차트', self)
        chart_Menu.setStatusTip('종목차트')
        chart_Menu.triggered.connect(self.chart_tab)
        chartMenu.addAction(chart_Menu)

        # 파일병합 메뉴
        dataCleanMenu = mainMenu.addMenu('자료정제')        
        fileMerge_Menu = QAction('파일병합', self)
        fileMerge_Menu.setStatusTip('파일병합')
        fileMerge_Menu.triggered.connect(self.fileMerge_tab)
        dataCleanMenu.addAction(fileMerge_Menu)

        # 거래전략 메뉴
        orderMenu = mainMenu.addMenu('거래전략')

        simpleStrategy = QAction('단순전략', self)
        simpleStrategy.setStatusTip('단순전략')
        simpleStrategy.triggered.connect(self.simple_strategy_tab)

        multiStrategy = QAction('복합전략', self)
        multiStrategy.setStatusTip('복합전략')

        orderMenu.addAction(simpleStrategy)
        orderMenu.addAction(multiStrategy)

        # 백테스트 메뉴
        backtestMenu = mainMenu.addMenu('백테스트')

        basic_backtest = QAction('&기본백테스트', self)
        basic_backtest.setStatusTip('기본백테스트')
        basic_backtest.triggered.connect(self.basic_tab)
        
        label_backtest = QAction('&레이블백테스트', self)
        label_backtest.setStatusTip('레이블백테스트')
        label_backtest.triggered.connect(self.label_tab)

        backtestMenu.addAction(basic_backtest)
        backtestMenu.addAction(label_backtest)

        # 종합차트 메뉴
        comPreChartMenu = mainMenu.addMenu('종합차트')
        comPreChart_Menu = QAction('&종합차트', self)
        comPreChart_Menu.setStatusTip('종합차트')
        comPreChart_Menu.triggered.connect(self.comPreChart_tab)
        comPreChartMenu.addAction(comPreChart_Menu)

        # 종목찾기 메뉴
        filterMenu = mainMenu.addMenu('종목찾기')
        filter_Menu = QAction('&종목찾기', self)
        filter_Menu.setStatusTip('종목찾기')
        filter_Menu.triggered.connect(self.filter_tab)
        filterMenu.addAction(filter_Menu)

        # 보기 메뉴
        viewMenu = mainMenu.addMenu("&보기")

        fileViewAction = QAction("&파일 디렉토리", self, checkable=True)
        fileViewAction.setStatusTip("파일 디렉토리")
        fileViewAction.setChecked(True)
        fileViewAction.triggered.connect(self.toggleFileView)
        viewMenu.addAction(self.dockTree.toggleViewAction())

        logViewAction = QAction("&메시지박스", self, checkable=True)
        logViewAction.setStatusTip("Message Box")
        logViewAction.setChecked(True)
        logViewAction.triggered.connect(self.toggleLogView)
        viewMenu.addAction(self.logDock.toggleViewAction())


    # 파일 불러오기, 생성
    def loadProject(self):
        self.root_path = QFileDialog.getExistingDirectory(self, self.tr("폴더 불러오기"), self.tr("~/Desktop/"),
                                                            QFileDialog.ShowDirsOnly
                                                            | QFileDialog.DontResolveSymlinks)

        self.trees_widget.change_root_index(self.root_path)

    # 바뀐 파일 경로 받는 함수
    def get_changed_path(self):
        return self.root_path

    # 화면 중앙 배치
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 메뉴 선택 시 탭 생성 함수
    def chart_tab(self):
        if self.root_path == '':
            self.load_Message()
        else:
            chart_tab = stock_chart_menu.stock_chart(self.root_path)
            self.tabs.addTab(chart_tab, '종목차트')

    def fileMerge_tab(self):
        if self.root_path == '':
            self.load_Message()
        else:
            fileMerge_tab = file_merge_menu.file_merge(self.root_path)
            self.tabs.addTab(fileMerge_tab, '파일병합')

    def simple_strategy_tab(self):
        if self.root_path == '':
            self.load_Message()
        else:
            simple_strategy_tab = simple_strategy_menu.simple_strategy(self.root_path)
            self.tabs.addTab(simple_strategy_tab, '단순전략')

    def basic_tab(self):
        if self.root_path == '':
            self.load_Message()
        else:
            basic_tab = basic_backtest_menu.basic_backtest(self.root_path)
            self.tabs.addTab(basic_tab, '기본백테스트')

    def label_tab(self):
        if self.root_path == '':
            self.load_Message()
        else:
            label_tab = label_backtest_menu.label_backtest(self.root_path)
            self.tabs.addTab(label_tab, '레이블백테스트')

    def comPreChart_tab(self):
        if self.root_path == '':
            self.load_Message()
        else:
            comPreChart_tab = comprehensive_chart_menu.comPreChart(self.root_path)
            self.tabs.addTab(comPreChart_tab, '종합차트')

    def filter_tab(self):
        if self.root_path == '':
            self.load_Message()
        else:
            filter_tab = stock_filtering_menu.filtering(self.root_path)
            self.tabs.addTab(filter_tab, '종목찾기')

    # 탭 삭제
    def onTabCloseRequested(self, index):
        widget = self.tabs.widget(index)
        widget.deleteLater()

    # 파일 디렉토리 창 open or close
    def toggleFileView(self, state):
        if state:
            self.dockTree.show()
        else:
            self.dockTree.hide()

    # 로그 창 open or close
    def toggleLogView(self, state):
        if state:
            self.logDock.show()
        else:
            self.logDock.hide()

    # 로그 창 텍스트 추가
    def _append_text(self, msg):
        self.textBrowser.moveCursor(QTextCursor.End)
        self.textBrowser.insertPlainText(msg)
        QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    # 경로 설정 x 시 경고 창 로드
    def load_Message(self):
        QMessageBox.information(self, "메시지", "파일 경로가 지정되지 않았습니다.", QMessageBox.Yes)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())