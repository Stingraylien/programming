vibe_cody_題目檢查.py
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# 讀取 "旭聯平台考題範本.xlsx - Sheet0.csv" 檔案
df = pd.read_csv("旭聯平台考題範本.xlsx - Sheet0.csv")

# 顯示 "旭聯平台考題範本.xlsx - Sheet0.csv" 檔案的內容
print(df.to_markdown(index=False, numalign="left", stralign="left"))