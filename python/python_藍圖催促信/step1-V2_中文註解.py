import pandas as pd
from datetime import datetime
#####################################################################
# 定義員工數據檔案列表
# 這些檔案包含了需要處理的E-Learning培訓數據
#file_employee_data_list = [
#    r'C:\Users\iec030082\Desktop\2024年E-Learning藍圖未完訓催促自動化建置\report\1223report_20241223_134622.xlsx',
#    r'C:\Users\iec030082\Desktop\2024年E-Learning藍圖未完訓催促自動化建置\report\1223report_20241223_141937.xlsx',
# ]
#######

# 步驟1：載入並合併所有員工數據檔案
all_employee_data = []
for file in file_employee_data_list:
    # 讀取Excel檔案，跳過前5行（標題行）
    employee_data = pd.read_excel(file, skiprows=5)
    # 只保留需要的欄位
    employee_data = employee_data[['部門', '員工編號', '姓名', '藍圖名稱', '應修課程數', '已完成課程數', '完訓率']]
    all_employee_data.append(employee_data)

# 將所有數據合併到一個DataFrame中
employee_data_combined = pd.concat(all_employee_data, ignore_index=True)

# 過濾數據：只保留員工編號以'IEC'開頭的記錄
# 這樣可以刪除佔位符和表頭等無效數據
employee_data_combined = employee_data_combined[employee_data_combined['員工編號'].str.startswith('IEC', na=False)]

# 處理姓名欄位：將姓名拆分為英文名和中文名
# 格式示例：John(張三) -> 英文名=John, 姓名=張三
employee_data_combined[['英文名', '姓名']] = employee_data_combined['姓名'].str.extract(r'([^\(]+)?(?:\(([^)]+)\))?')
# 如果沒有中文名，則使用英文名作為姓名
employee_data_combined['姓名'] = employee_data_combined.apply(lambda x: x['姓名'] if pd.notna(x['姓名']) else x['英文名'], axis=1)
# 如果沒有英文名，則設置為空字串
employee_data_combined['英文名'] = employee_data_combined['英文名'].where(employee_data_combined['英文名'].notna(), '')

# 載入員工郵箱數據並與主數據合併
file_email_data = r'C:\Users\iec030082\Desktop\2024年E-Learning藍圖未完訓催促自動化建置\report\Email data.xlsx'
email_data = pd.read_excel(file_email_data)
# 基於員工編號進行左連接，確保保留所有員工記錄
merged_data = pd.merge(employee_data_combined, email_data[['員工編號', '電子信箱']], on='員工編號', how='left')

# 將應修課程數和已完成課程數轉換為數值類型
# 如果存在非數字數據，將轉換為NaN
merged_data["應修課程數"] = pd.to_numeric(merged_data["應修課程數"], errors='coerce')
merged_data["已完成課程數"] = pd.to_numeric(merged_data["已完成課程數"], errors='coerce')
##
# 計算未完成課程數和完訓率
merged_data["未完成課程數"] = merged_data["應修課程數"] - merged_data["已完成課程數"]
# 計算完訓率並轉換為百分比格式
merged_data["完訓率"] = (merged_data["已完成課程數"] / merged_data["應修課程數"] * 100).fillna(0).astype(int).astype(str) + "%"

# 數據篩選：
# 1. 刪除沒有電子郵箱的記錄
# 2. 刪除完訓率為100%的記錄（已完成培訓的員工）
merged_data = merged_data[merged_data['電子信箱'].notna() & (merged_data['電子信箱'] != '')]
merged_data = merged_data[merged_data['完訓率'] != '100%']

# 重新排列欄位順序，確保輸出格式符合要求
formatted_data = merged_data[["員工編號", "姓名", "英文名", "藍圖名稱", "應修課程數", "已完成課程數", "未完成課程數", "完訓率", "電子信箱"]]

# 生成包含當前日期和時間的檔案名，確保檔案名唯一
current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
new_output_path = fr'C:\Users\iec030082\Desktop\2024年E-Learning藍圖未完訓催促自動化建置\report\output\Formatted_Employee_Training_Data_{current_datetime}.xlsx'

# 將處理後的數據儲存到新的Excel檔案中
formatted_data.to_excel(new_output_path, index=False)

# 顯示處理後的數據
print(formatted_data)
