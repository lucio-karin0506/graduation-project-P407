import labeler
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from module.order_creator import gatherer
gath = gatherer.Gatherer()
df, _ = gath.get_stock('000660', '2020-01-01', '2020-12-31')
labeler.candle_type(df)
labeler.candle_shape(df)
labeler.three_blue(df,4)
labeler.three_red(df,4)
labeler.n_gap(df, 0.05)
labeler.roc(df, 14)
labeler.sma_cross(df, 7, 13, 2)
labeler.dema_cross(df, 3, 15, 1)
labeler.vwma_cross(df, 4, 14)
labeler.bbands(df, 15, 3)
labeler.macd(df, 10 ,30)
labeler.macd_cross(df, 15, 30, 10, 4)
labeler.stochf(df, 7, 4)
labeler.stoch(df, 7, 4, 4, 3)
labeler.top_bottom(df, 0.02, 0.01, 0, 0)
print(df)
