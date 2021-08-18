import numpy as np
from pandas.io.parsers import read_csv

def hit_testing(df:"DataFrame", opt:int) -> "DataFrame":
  """
  가격레이블과 주문이 얼마나 일치하는지 비교한다.
  
  Parameters
  ----------
  df
    레이블DataFrame 주문DataFrame merge된 DataFrame
  opt
    주문과 비교하는 레이블의 여유기간

  Returns
  -------
  DataFrame
      buy, sell hit 컬럼이 추가된 데이터프레임
  """
  if opt == 2:
    df['not_bhit'] = np.where(((df.order_type == 'buy') &
                          ((df.close_top_zone.shift(-2) == 1) |
                          (df.close_top_zone.shift(-1) == 1) |
                          (df.close_top_zone.shift(0) == 1) |
                          (df.close_top_zone.shift(1) == 1) |
                          (df.close_top_zone.shift(2) == 1))), -1, 0)
                            
    df['not_shit'] = np.where(((df.order_type == 'sell') &
                          ((df.close_bottom_zone.shift(-2) == 1) |
                          (df.close_bottom_zone.shift(-1) == 1) |
                          (df.close_bottom_zone.shift(0) == 1) |  
                          (df.close_bottom_zone.shift(1) == 1) |
                          (df.close_bottom_zone.shift(2) == 1))), -1, 0)

    df['buy_hit'] = np.where(((df.order_type == 'buy') &
                          ((df.close_bottom_zone.shift(-2) == 1) |
                          (df.close_bottom_zone.shift(-1) == 1) |
                          (df.close_bottom_zone.shift(0) == 1) |
                          (df.close_bottom_zone.shift(1) == 1) |
                          (df.close_bottom_zone.shift(2) == 1))), 1, 0)
                            
    df['sell_hit'] = np.where(((df.order_type == 'sell') &
                          ((df.close_top_zone.shift(-2) == 1) |
                          (df.close_top_zone.shift(-1) == 1) |
                          (df.close_top_zone.shift(0) == 1) |  
                          (df.close_top_zone.shift(1) == 1) |
                          (df.close_top_zone.shift(2) == 1))), 1, 0)
  elif opt == 1:
    df['not_bhit'] = np.where(((df.order_type == 'buy') &
                          ((df.close_top_zone.shift(-1) == 1) |
                          (df.close_top_zone.shift(0) == 1) |
                          (df.close_top_zone.shift(1) == 1))), -1, 0)
                            
    df['not_shit'] = np.where(((df.order_type == 'sell') &
                          ((df.close_bottom_zone.shift(-1) == 1) |
                          (df.close_bottom_zone.shift(0) == 1) |
                          (df.close_bottom_zone.shift(1) == 1))), -1, 0)

    df['buy_hit'] = np.where(((df.order_type == 'buy') &
                          ((df.close_bottom_zone.shift(-1) == 1) |
                          (df.close_bottom_zone.shift(0) == 1) |
                          (df.close_bottom_zone.shift(1) == 1))), 1, 0)
                            
    df['sell_hit'] = np.where(((df.order_type == 'sell') &
                          ((df.close_top_zone.shift(-1) == 1) |
                          (df.close_top_zone.shift(0) == 1) |
                          (df.close_top_zone.shift(1) == 1))), 1, 0)

  elif opt == 0:
    df['not_bhit'] = np.where(((df.order_type == 'buy') &
                          (df.close_top_zone.shift(0) == 1)), -1, 0)
    
    df['not_shit'] = np.where(((df.order_type == 'sell') &
                          (df.close_bottom_zone.shift(0) == 1)), -1, 0)

    df['buy_hit'] = np.where(((df.order_type == 'buy') &
                          (df.close_bottom_zone.shift(0) == 1)), 1, 0)
                            
    df['sell_hit'] = np.where(((df.order_type == 'sell') &
                          (df.close_top_zone.shift(0) == 1)), 1, 0)

  df['buy_hit'] = df['buy_hit'] + df['not_bhit']
  df['sell_hit'] = df['sell_hit'] + df['not_shit']

  df = df.drop(columns=['not_bhit', 'not_shit'])

  df.set_index('Date', inplace=True)
  return df

if __name__ == "__main__":
  import json
  import os
  import pathlib
  import pandas as pd

  file = pathlib.Path(os.getcwd() + '/orderFile/'+'NAVER_d_Order.json')
  text = file.read_text(encoding='utf-8')
  js = json.loads(text)
  order_df = pd.DataFrame(js)

  order_df = order_df.drop(columns=order_df.iloc[:,5:])
  order_start = order_df.head(1)['order_datetime'].values[0]
  order_end = order_df.tail(1)['order_datetime'].values[0]
  order_df = order_df.rename({'order_datetime':'Date'}, axis='columns')
  label_df = pd.read_csv(os.getcwd()+'/labelFile/'+'NAVER_d_label.csv', index_col='Date')
  label_df = label_df[order_start:order_end]

  result = pd.merge(order_df, label_df, on='Date', how='outer')
  result = result.sort_values(by=['Date'])

  a = hit_testing(result, 0)
  print(a)
  # a.to_csv('test2.csv', index_label='Date')
