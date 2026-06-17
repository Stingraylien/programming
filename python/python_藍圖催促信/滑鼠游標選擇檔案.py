import pandas as pd
from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

# 使用滑鼠游標選擇檔案
Tk().withdraw()  # 關閉Tkinter主視窗
file_employee_data_list = askopenfilenames(title="選擇員工數據檔案", filetypes=[("Excel files", "*.xlsx")])