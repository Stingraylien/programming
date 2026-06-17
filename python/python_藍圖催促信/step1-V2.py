import pandas as pd
from datetime import datetime

# List of employee data files
file_employee_data_list = [
    r'C:\Users\iec030082\Desktop\2024年E-Learning藍圖未完訓催促自動化建置\report\1223report_20241223_134622.xlsx',r'C:\Users\iec030082\Desktop\2024年E-Learning藍圖未完訓催促自動化建置\report\1223report_20241223_141937.xlsx',
]

# Step 1: Load and concatenate all employee data files
all_employee_data = []
for file in file_employee_data_list:
    employee_data = pd.read_excel(file, skiprows=5)
    employee_data = employee_data[['部門', '員工編號', '姓名', '藍圖名稱', '應修課程數', '已完成課程數', '完訓率']]
    all_employee_data.append(employee_data)

# Concatenate all employee data into a single DataFrame
employee_data_combined = pd.concat(all_employee_data, ignore_index=True)

# Filter out rows where '員工編號' does not start with 'IEC' (to remove placeholders and headers)
employee_data_combined = employee_data_combined[employee_data_combined['員工編號'].str.startswith('IEC', na=False)]

# Splitting the '姓名' column into '英文名' and '姓名', handling cases without an English name
employee_data_combined[['英文名', '姓名']] = employee_data_combined['姓名'].str.extract(r'([^\(]+)?(?:\(([^)]+)\))?')
employee_data_combined['姓名'] = employee_data_combined.apply(lambda x: x['姓名'] if pd.notna(x['姓名']) else x['英文名'], axis=1)
employee_data_combined['英文名'] = employee_data_combined['英文名'].where(employee_data_combined['英文名'].notna(), '')

# Load email data and merge
file_email_data = r'C:\Users\iec030082\Desktop\2024年E-Learning藍圖未完訓催促自動化建置\report\Email data.xlsx'
email_data = pd.read_excel(file_email_data)
merged_data = pd.merge(employee_data_combined, email_data[['員工編號', '電子信箱']], on='員工編號', how='left')

# Convert '應修課程數' and '已完成課程數' columns to numeric, coercing errors to NaN if any non-numeric data exists
merged_data["應修課程數"] = pd.to_numeric(merged_data["應修課程數"], errors='coerce')
merged_data["已完成課程數"] = pd.to_numeric(merged_data["已完成課程數"], errors='coerce')

# Calculate "未完成課程數" and "完訓率" with numeric columns
merged_data["未完成課程數"] = merged_data["應修課程數"] - merged_data["已完成課程數"]
merged_data["完訓率"] = (merged_data["已完成課程數"] / merged_data["應修課程數"] * 100).fillna(0).astype(int).astype(str) + "%"

# Filter out rows with missing email addresses and "完訓率" equal to 100%
merged_data = merged_data[merged_data['電子信箱'].notna() & (merged_data['電子信箱'] != '')]
merged_data = merged_data[merged_data['完訓率'] != '100%']  # Exclude rows where 完訓率 is 100%

# Reorder columns to match the format structure
formatted_data = merged_data[["員工編號", "姓名", "英文名", "藍圖名稱", "應修課程數", "已完成課程數", "未完成課程數", "完訓率", "電子信箱"]]

# Generate a filename with the current date and time to ensure uniqueness
current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
new_output_path = fr'C:\Users\iec030082\Desktop\2024年E-Learning藍圖未完訓催促自動化建置\report\output\Formatted_Employee_Training_Data_{current_datetime}.xlsx'

# Save the result to the new file with the date and time in the name
formatted_data.to_excel(new_output_path, index=False)

# Display the resulting DataFrame
print(formatted_data)
