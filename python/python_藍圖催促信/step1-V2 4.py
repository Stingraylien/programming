import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

# 初始化 tkinter 並隱藏主視窗
root = tk.Tk()
root.withdraw()

# 透過 GUI 介面選擇 Excel 檔案
print("Please select the Excel file(s)...")
file_paths = filedialog.askopenfilenames(
    title="Select Excel Files",
    filetypes=[("Excel files", "*.xlsx;*.xls")]
)
file_employee_data_list = list(file_paths)

if not file_employee_data_list:
    print("No file selected")
    exit()

# 步驟 1：載入並合併所有員工資料檔案
all_employee_data = []
for file in file_employee_data_list:
    employee_data = pd.read_excel(file, skiprows=5)
    employee_data = employee_data[['部門', '員工編號', '姓名', '藍圖名稱', '應修課程數', '已完成課程數', '完訓率']]
    all_employee_data.append(employee_data)

# 將所有員工資料合併成單一 DataFrame
employee_data_combined = pd.concat(all_employee_data, ignore_index=True)

# 篩選出 '員工編號' 非以 'IEC' 開頭的列（以移除佔位符和標頭）
employee_data_combined = employee_data_combined[employee_data_combined['員工編號'].str.startswith('IEC', na=False)]

# 將 '姓名' 欄位拆分為 '英文名' 和 '姓名'，處理沒有英文名字的情況
employee_data_combined[['英文名', '姓名']] = employee_data_combined['姓名'].str.extract(r'([^\(]+)?(?:\(([^)]+)\))?')
employee_data_combined['姓名'] = employee_data_combined.apply(lambda x: x['姓名'] if pd.notna(x['姓名']) else x['英文名'], axis=1)
employee_data_combined['英文名'] = employee_data_combined['英文名'].where(employee_data_combined['英文名'].notna(), '')

# 載入 Email 資料並合併
file_email_data = r'C:\Users\iec030082\OneDrive - Inventec Corp\藍圖催促\Email data.xlsx'
email_data = pd.read_excel(file_email_data)
merged_data = pd.merge(employee_data_combined, email_data[['員工編號', '電子信箱']], on='員工編號', how='left')

# 將 '應修課程數' 和 '已完成課程數' 欄位轉換為數值，若有非數值資料則強制轉為 NaN
merged_data["應修課程數"] = pd.to_numeric(merged_data["應修課程數"], errors='coerce')
merged_data["已完成課程數"] = pd.to_numeric(merged_data["已完成課程數"], errors='coerce')

# 計算 "未完成課程數" 和 "完訓率"（使用數值欄位）
merged_data["未完成課程數"] = merged_data["應修課程數"] - merged_data["已完成課程數"]
merged_data["完訓率"] = (merged_data["已完成課程數"] / merged_data["應修課程數"] * 100).fillna(0).astype(int).astype(str) + "%"

# 篩選出缺少電子郵件地址且 "完訓率" 等於 100% 的列
merged_data = merged_data[merged_data['電子信箱'].notna() & (merged_data['電子信箱'] != '')]
merged_data = merged_data[merged_data['完訓率'] != '100%']  # 排除完訓率為 100% 的列

# 重新排列欄位以符合格式結構
formatted_data = merged_data[["員工編號", "姓名", "英文名", "藍圖名稱", "應修課程數", "已完成課程數", "未完成課程數", "完訓率", "電子信箱"]]

# 將資料分割成 500 筆的區塊並儲存
chunk_size = 1000
current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
 
for i, start_row in enumerate(range(0, formatted_data.shape[0], chunk_size)):
    chunk = formatted_data.iloc[start_row:start_row + chunk_size]
    output_path = r'C:\Users\iec030082\OneDrive - Inventec Corp\藍圖催促\output\Formatted_Employee_Training_Data_Chunk_{i+1}_{current_datetime}.xlsx'
    chunk.to_excel(output_path, index=False)
    print(f"Saved chunk {i+1} to {output_path}")


