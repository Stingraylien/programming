import pandas as pd
import os
import shutil  

# 🔹 設定所有測驗 Excel 檔案存放的資料夾路徑
folder_path = os.path.join(os.path.expanduser("~"), "Library", "CloudStorage", "OneDrive-InventecCorp", "測驗題目自動檢查")

# 🔹 設定驗證後檔案儲存的輸出資料夾
output_folder = os.path.join(folder_path, "output")

# 🔹 設定失敗報告的資料夾
failed_folder = os.path.join(folder_path, "failed")

# 確保輸出資料夾存在
for folder in [output_folder, failed_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# 取得所有 Excel 檔案
quiz_files = [f for f in os.listdir(folder_path) if f.endswith(".xlsx")]

# 需要檢查的必要欄位
required_columns = ["Difficulty", "Option Limit Type(for survey):0-no limit;1-max;2-min",
                    "Option Limit Count(for survey)", "Analyze(for QBank)", "NoRandom(for QBank)"]

# 儲存結果
invalid_questions_list = []  # 無效問題清單
low_weight_list = []  # 低權重清單
missing_columns_list = []  # 缺少欄位清單
valid_files = []  # 追蹤有效檔案
error_files = []  # 追蹤有問題的檔案

# 處理每個測驗檔案
for file in quiz_files:
    file_path = os.path.join(folder_path, file)
    
    # 載入 Excel 檔案
    xls = pd.ExcelFile(file_path)
    
    # 找到第一個 "#QTYPE" 出現的位置以移除不必要的列
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0], header=None)
    
    # 找出 "#QTYPE" 第一次出現的列索引
    qtype_row_index = df[df.iloc[:, 0] == "#QTYPE"].index.min()
    
    if pd.isna(qtype_row_index):
        print(f"⚠️ 跳過 {file}: 找不到 '#QTYPE'。")
        error_files.append(file)
        continue  # 如果找不到 #QTYPE 則跳過此檔案

    # 只提取從 "#QTYPE" 開始的相關資料
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0], skiprows=qtype_row_index)

    # 檢查缺少的欄位
    missing_cols = [col for col in required_columns if col not in df.columns]
    
    if missing_cols:
        missing_columns_list.append({"File": file, "Missing Columns": ", ".join(missing_cols)})
        error_files.append(file)
        continue  # 如果缺少必要欄位則跳過處理此檔案

    # 確保 'Subject' 欄位向下填充，使每個選項都對應到其問題
    df["Subject"] = df["Subject"].ffill()

    # 計算每個問題的 'y' 出現次數
    answer_counts = df.groupby("Subject")["Yes/No/Answer"].apply(lambda x: (x == 'y').sum())

    # 識別沒有恰好一個正確答案的問題
    invalid_questions = answer_counts[answer_counts != 1].reset_index()

    # 正確計算總權重
    total_weight = df.groupby("Subject")["Weight"].first().sum()

    has_invalid_questions = not invalid_questions.empty
    has_low_weight = total_weight < 100  # 如果權重低於 100 則報告

    # 如果沒有問題，標記為有效
    if not has_invalid_questions and not has_low_weight:
        valid_files.append(file)  # 追蹤有效檔案

    # 現在包含有任一問題的檔案，而不只是同時有兩個問題的檔案
    if has_invalid_questions or has_low_weight:
        if has_invalid_questions:
            invalid_questions["File"] = file  # 添加檔案名稱以供參考
            invalid_questions_list.append(invalid_questions)
        if has_low_weight:
            low_weight_list.append({"File": file, "Total Weight": total_weight})
        error_files.append(file)  # 追蹤有問題的檔案

# 定義失敗報告的完整輸出檔案路徑
failed_output_file = os.path.join(failed_folder, "Quiz_Validation_Report.xlsx")

# 如果有任何問題，儲存報告
if invalid_questions_list or low_weight_list or missing_columns_list:
    print("❌ 部分測驗檔案有問題。")
    print("以下檔案包含錯誤：")
    for error_file in set(error_files):
        print(f"🔸 {error_file}")  # ✅ 印出錯誤檔案名稱

    # 建立 Excel 寫入器以將所有內容儲存在一個檔案中
    with pd.ExcelWriter(failed_output_file, engine="xlsxwriter") as writer:
        
        # 儲存無效問題
        if invalid_questions_list:
            final_invalid_questions = pd.concat(invalid_questions_list, ignore_index=True)
            final_invalid_questions.to_excel(writer, index=False, sheet_name="Invalid Questions")

        # 儲存低權重檔案
        if low_weight_list:
            low_weight_df = pd.DataFrame(low_weight_list)
            low_weight_df.to_excel(writer, index=False, sheet_name="Low Weight Files")

        # 儲存缺少欄位的檔案
        if missing_columns_list:
            missing_columns_df = pd.DataFrame(missing_columns_list)
            missing_columns_df.to_excel(writer, index=False, sheet_name="Missing Columns")

    print(f"📄 合併報告已儲存至：{failed_output_file}")

# 現在將有效檔案複製到輸出資料夾
if valid_files:
    for file in valid_files:
        source_file = os.path.join(folder_path, file)
        destination_file = os.path.join(output_folder, file)
        shutil.copy2(source_file, destination_file)  # 保留元數據

    print(f"✅ 所有有效的測驗檔案已複製至：{output_folder}")
else:
    print("✅ 沒有找到有效的檔案可以複製。")


