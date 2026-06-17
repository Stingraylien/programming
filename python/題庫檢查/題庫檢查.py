import pandas as pd

# 題型代碼對照表
valid_question_types = [
    '[TrueFalse]', '[SingleChoice]', '[MultipleChoice]', '[FillInBlank]', '[Essay]'
]

# 檢查題庫的主函數
def check_question_bank(file_path):
    # 讀取檔案
    df = pd.read_excel(file_path, sheet_name=0)
    errors = []

    # 遍歷每一列，檢查格式
    for index, row in df.iterrows():
        # 檢查題型代碼
        if '#QTYPE' in str(row[0]):
            question_type = row[1]
            if question_type not in valid_question_types:
                errors.append(f'第{index + 1}行: 無效的題型代碼 {question_type}')

        # 若是選擇題型，檢查選項
        elif 'Option' in str(row[0]):
            if pd.isna(row[1]):
                errors.append(f'第{index + 1}行: 選項內容為空')

        # 若是填充題型，檢查答案
        elif '#ANSWER' in str(row[0]):
            if pd.isna(row[1]):
                errors.append(f'第{index + 1}行: 缺少答案內容')

    # 顯示結果
    if errors:
        print('檢查結果發現錯誤:')
        for error in errors:
            print(error)
    else:
        print('檢查通過，無錯誤！')

# 測試執行
file_path = '/mnt/data/旭聯平台考題範本.xlsx'
check_question_bank(file_path)
