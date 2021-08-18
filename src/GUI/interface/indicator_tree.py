import sys
import os
import pandas as pd

import PySide2
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2 import QtWidgets

class IndicatorTreeView(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setAlternatingRowColors(True)
        self.header().setVisible(False)
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.header().setStretchLastSection(False)

    def get_path(self, path):
        stock_file = os.path.split(path)
        selected_stock_name = stock_file[1].replace('.csv', '')
        file_type = stock_file[1].split('.')[1]

        stock_name = QTreeWidgetItem([selected_stock_name])
        self.addTopLevelItem(stock_name)

        # 지표 리스트 박스에서 종목 아래에 기술적지표 텍스트 추가 & 각 지표 아이템 추가
        stock_tech_indi = QTreeWidgetItem(['기술적지표'])
        stock_name.addChild(stock_tech_indi)

        self.item_ma = QTreeWidgetItem(stock_tech_indi)
        self.item_ma.setText(0, '이동평균')
        self.item_rsi = QTreeWidgetItem(stock_tech_indi)
        self.item_rsi.setText(0, 'RSI')
        self.item_macd = QTreeWidgetItem(stock_tech_indi)
        self.item_macd.setText(0, 'MACD')
        self.item_bb = QTreeWidgetItem(stock_tech_indi)
        self.item_bb.setText(0, 'BollingerBand')
        self.item_stochf = QTreeWidgetItem(stock_tech_indi)
        self.item_stochf.setText(0, 'Stochastic Fast')
        self.item_stochs = QTreeWidgetItem(stock_tech_indi)
        self.item_stochs.setText(0, 'Stochastic Slow')
        self.item_ema = QTreeWidgetItem(stock_tech_indi)
        self.item_ema.setText(0, 'EMA')
        self.item_cmo = QTreeWidgetItem(stock_tech_indi)
        self.item_cmo.setText(0, 'CMO')
        self.item_atr = QTreeWidgetItem(stock_tech_indi)
        self.item_atr.setText(0, 'ATR')
        self.item_st = QTreeWidgetItem(stock_tech_indi)
        self.item_st.setText(0, 'SuperTrend')
        self.item_cluster = QTreeWidgetItem(stock_tech_indi)
        self.item_cluster.setText(0, 'Clustering')

        # 지표 리스트 박스에서 종목 아래에 레이블지표 텍스트 추가 & 각 지표 아이템 추가
        stock_label_indi = QTreeWidgetItem(['레이블지표'])
        stock_name.addChild(stock_label_indi)

        self.item_candle_type = QTreeWidgetItem(stock_label_indi)
        self.item_candle_type.setText(0, '캔들 종류')
        self.item_candle_shape = QTreeWidgetItem(stock_label_indi)
        self.item_candle_shape.setText(0, '캔들 모양')
        self.item_3red = QTreeWidgetItem(stock_label_indi)
        self.item_3red.setText(0, '적삼병')
        self.item_3blue = QTreeWidgetItem(stock_label_indi)
        self.item_3blue.setText(0, '흑삼병')
        self.item_ngap = QTreeWidgetItem(stock_label_indi)
        self.item_ngap.setText(0, '갭 상승/하락')
        self.item_roc = QTreeWidgetItem(stock_label_indi)
        self.item_roc.setText(0, '가격 변화 비율')
        self.item_sma_cross = QTreeWidgetItem(stock_label_indi)
        self.item_sma_cross.setText(0, '단순이동평균 Cross')
        self.item_dema_cross = QTreeWidgetItem(stock_label_indi)
        self.item_dema_cross.setText(0, '이중지수이동평균 Cross')
        self.item_vwma_cross = QTreeWidgetItem(stock_label_indi)
        self.item_vwma_cross.setText(0, '거래량가중이동평균 Cross')
        self.item_macd_label = QTreeWidgetItem(stock_label_indi)
        self.item_macd_label.setText(0, 'MACD')
        self.item_bb_label = QTreeWidgetItem(stock_label_indi)
        self.item_bb_label.setText(0, 'BollingerBand')
        self.item_macd_cross = QTreeWidgetItem(stock_label_indi)
        self.item_macd_cross.setText(0, 'MACD Cross')
        self.item_stochf_label = QTreeWidgetItem(stock_label_indi)
        self.item_stochf_label.setText(0, 'Stochastic Fast Cross')
        self.item_stochs_label = QTreeWidgetItem(stock_label_indi)
        self.item_stochs_label.setText(0, 'Stochastic Slow Cross')

        # 다이얼로그 파라미터 입력 후 파일에 기존에 존재한 지표를 지표리스트에 추가=================================
        import re
        # 각 컬럼 제목 문자에 매칭하는 규칙 설정
        self.ma_col_text = re.compile(r'^ma[^cd][^_cross]')
        self.rsi_col_text = re.compile(r'^rsi')
        self.macd_col_text = re.compile(r'^(macd|^macd_signal|^macd_hist)_\d{1,3}_\d{1,3}_\d{1,3}$')
        self.bb_col_text = re.compile(r'^ubb|^lbb|^mbb')
        self.stochf_col_text = re.compile(r'^fastk|^fastd')
        self.stochs_col_text = re.compile(r'^slowk|^slowd')
        self.ema_col_text = re.compile(r'^ema')
        self.cmo_col_text = re.compile(r'^cmo')
        self.atr_col_text = re.compile(r'^atr')
        self.st_col_text = re.compile(r'^st')
        self.cluster_col_text = re.compile(r'^high|^low')

        self.candleType_col_text = re.compile(r'^candle_type')
        self.candleShape_col_text = re.compile(r'^candle_shape')
        self.red3_col_text = re.compile(r'^three_red')
        self.blue3_col_text = re.compile(r'^three_blue')
        self.ngap_col_text = re.compile(r'^gap')
        self.roc_col_text = re.compile(r'^roc')
        self.sma_col_text = re.compile(r'^ma_cross')
        self.dema_col_text = re.compile(r'^dema_cross')
        self.vwma_col_text = re.compile(r'^vwma_cross')
        self.macd_label_col_text = re.compile(r'^macd_\d{1,3}_\d{1,3}\D[a-z]\D')
        self.bb_label_col_text = re.compile(r'^bb')
        self.macd_cross_col_text = re.compile(r'^macd_cross')
        self.stochf_label_col_text = re.compile(r'^stochf')
        self.stoch_label_col_text = re.compile(r'^stoch[^f]')

        df = pd.read_csv(path, index_col='Date')
        indi_columns = list(df.columns)[6:]

        for i in indi_columns:
            # 기술적 지표
            if self.ma_col_text.match(i):
                self.ma = QTreeWidgetItem(self.item_ma)
                self.ma.setText(0, i)
            if self.rsi_col_text.match(i):
                self.rsi = QTreeWidgetItem(self.item_rsi)
                self.rsi.setText(0, i)
            if self.macd_col_text.match(i):
                self.macd = QTreeWidgetItem(self.item_macd)
                self.macd.setText(0, i)
            if self.bb_col_text.match(i):
                self.bb = QTreeWidgetItem(self.item_bb)
                self.bb.setText(0, i)
            if self.stochf_col_text.match(i):
                self.stochf = QTreeWidgetItem(self.item_stochf)
                self.stochf.setText(0, i)
            if self.stochs_col_text.match(i):
                self.stochs = QTreeWidgetItem(self.item_stochs)
                self.stochs.setText(0, i)
            if self.ema_col_text.match(i):
                self.ema = QTreeWidgetItem(self.item_ema)
                self.ema.setText(0, i)
            if self.cmo_col_text.match(i):
                self.cmo = QTreeWidgetItem(self.item_cmo)
                self.cmo.setText(0, i)
            if self.atr_col_text.match(i):
                self.atr = QTreeWidgetItem(self.item_atr)
                self.atr.setText(0, i)
            if self.st_col_text.match(i):
                self.st = QTreeWidgetItem(self.item_st)
                self.st.setText(0, i)
            if self.cluster_col_text.match(i):
                self.cluster = QTreeWidgetItem(self.item_cluster)
                self.cluster.setText(0, i)

            # 레이블 지표
            if self.candleType_col_text.match(i):
                self.candleType = QTreeWidgetItem(self.item_candle_type)
                self.candleType.setText(0, i)
            if self.candleShape_col_text.match(i):
                self.candleShape = QTreeWidgetItem(self.item_candle_shape)
                self.candleShape.setText(0, i)
            if self.red3_col_text.match(i):
                self.red3 = QTreeWidgetItem(self.item_3red)
                self.red3.setText(0, i)
            if self.blue3_col_text.match(i):
                self.blue3 = QTreeWidgetItem(self.item_3blue)
                self.blue3.setText(0, i)
            if self.ngap_col_text.match(i):
                self.ngap = QTreeWidgetItem(self.item_ngap)
                self.ngap.setText(0, i)
            if self.roc_col_text.match(i):
                self.roc = QTreeWidgetItem(self.item_roc)
                self.roc.setText(0, i)
            if self.sma_col_text.match(i):
                self.sma = QTreeWidgetItem(self.item_sma_cross)
                self.sma.setText(0, i)
            if self.dema_col_text.match(i):
                self.dema = QTreeWidgetItem(self.item_dema_cross)
                self.dema.setText(0, i)
            if self.vwma_col_text.match(i):
                self.vwma = QTreeWidgetItem(self.item_vwma_cross)
                self.vwma.setText(0, i)
            if self.macd_label_col_text.match(i):
                self.macd_label = QTreeWidgetItem(self.item_macd_label)
                self.macd_label.setText(0, i)
            if self.bb_label_col_text.match(i):
                self.bb_label = QTreeWidgetItem(self.item_bb_label)
                self.bb_label.setText(0, i)
            if self.macd_cross_col_text.match(i):
                self.macd_cross = QTreeWidgetItem(self.item_macd_cross)
                self.macd_cross.setText(0, i)
            if self.stochf_label_col_text.match(i):
                self.stochf_label = QTreeWidgetItem(self.item_stochf_label)
                self.stochf_label.setText(0, i)
            if self.stoch_label_col_text.match(i):
                self.stoch_label = QTreeWidgetItem(self.item_stochs_label)
                self.stoch_label.setText(0, i)


sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = IndicatorTreeView()
    mainWindow.show()
    app.exec_()