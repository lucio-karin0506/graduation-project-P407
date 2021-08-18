import pathlib
import json
import pandas as pd
file_name = 'strategy_1.json'


file = pathlib.Path("C:/Users/Administrator/Desktop/p407-github/P407/src/module/auto_trader/"+file_name)
text = file.read_text(encoding='utf-8-sig')

js = json.loads(text)
df = pd.DataFrame(js)
df