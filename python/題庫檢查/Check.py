import pandas as pd                                  # 匯入 pandas 模組，用於讀取與處理 Excel 與資料表
import os                                            # 匯入 os 模組，用於作業系統路徑與檔案操作
import shutil                                        # 匯入 shutil 模組，用於檔案複製操作
import tkinter as tk                                 # 匯入 tkinter 模組，用於建立圖形化使用者介面 (GUI)
from tkinter import filedialog, messagebox           # 從 tkinter 匯入 filedialog (選取檔案視窗) 與 messagebox (跳出提示訊息)

def main():                                          # 定義主程式函式
    tk_main_window = tk.Tk()                         # 建立一個 tkinter 根視窗 (主視窗) 物件
    tk_main_window.withdraw()                        # 將主視窗隱藏，因為我們只需要檔案選擇對話框，不需要空白視窗

    # 建立開場畫面 (Splash Screen)
    splash = tk.Toplevel(tk_main_window)
    # 設定視窗大小與置中
    window_width = 450
    window_height = 250
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)
    splash.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # 隱藏標題列邊框，顯示為無邊框啟動畫面
    splash.overrideredirect(True)
    
    # 加入提示文字標籤
    tk.Label(splash, text="旭聯學習題庫檢驗程式\n\n構想： 連偉翔\n\n實際執行: Google Antigravity\n\n 2026/3/24 Beta version", font=("微軟正黑體", 18, "bold"), justify="center").pack(expand=True)
    
    # 設定 5 秒 (5000毫秒) 後自動關閉
    splash.after(5000, splash.destroy)
    
    # 確保畫面在最上層並強制更新顯示此視窗
    splash.attributes('-topmost', True)
    splash.update()
    
    # 暫停程式執行直到開場畫面自動關閉，才會繼續接下來的動作
    tk_main_window.wait_window(splash)

    # 1. 彈出對話框，讓使用者自由選擇多個 Excel 檔案
    list_selected_excel_paths = filedialog.askopenfilenames(  # 呼叫檔案選擇器，允許使用者選擇多個檔案，並將路徑存成清單
        title="請選擇要檢查的測驗 Excel 檔案 (可多選)",       # 設定檔案選擇對話框的標題文字
        filetypes=[("Excel files", "*.xlsx;*.xls")]  # 限制對話框只能選擇 .xlsx 或 .xls 結尾的舊版/新版 Excel 檔案
    )

    if not list_selected_excel_paths:                # 如果清單為空 (使用者按了取消或直接關閉視窗)
        print("使用者取消選擇, 程式結束。")            # 在終端機印出取消訊息
        return                                       # 結束 main 函式，停止程式執行

    # 2. 取得第一個選擇檔案的所在資料夾，用來建立動態的 output 和 failed 目錄
    str_parent_directory = os.path.dirname(list_selected_excel_paths[0])  # 取得第一個被選取檔案的「所在資料夾絕對路徑」
    str_success_output_dir = os.path.join(str_parent_directory, "output") # 將資料夾路徑加上 "output" 作為成功檔案區
    str_error_report_dir = os.path.join(str_parent_directory, "failed")   # 將資料夾路徑加上 "failed" 作為錯誤報告區

    for dir_path in [str_success_output_dir, str_error_report_dir]:       # 走訪這兩個即將建立的資料夾路徑
        if not os.path.exists(dir_path):             # 如果該資料夾路徑在電腦中尚未存在
            os.makedirs(dir_path)                    # 則自動建立該資料夾

    # 定義標準的 A 到 J 欄預期順序與全稱 (這是嚴格欄位順序守門員的黃金標準)
    list_strict_expected_headers = [
        "#QTYPE",                                               # 欄 A (0)
        "Subject",                                              # 欄 B (1)
        "Option",                                               # 欄 C (2)
        "Weight",                                               # 欄 D (3)
        "Difficulty",                                           # 欄 E (4)
        "Yes/No/Answer",                                        # 欄 F (5)
        "Option Limit Type(for survey):0-no limit;1-max;2-min", # 欄 G (6)
        "Option Limit Count(for survey)",                       # 欄 H (7)
        "Analyze(for QBank)",                                   # 欄 I (8)
        "NoRandom(for QBank)"                                   # 欄 J (9)
    ]
    
    # 常用欄名變數，方便下方拿取數值使用
    str_col_limit_type = list_strict_expected_headers[6]      # 取得限制類型名稱字串
    str_col_limit_count = list_strict_expected_headers[7]     # 取得限制個數名稱字串
    str_col_no_random = list_strict_expected_headers[9]       # 取得隨機排序名稱字串

    # 儲存結果
    list_invalid_questions_df = []                   # 建立一個空清單，用來收集所有包含錯誤的「題目 DataFrame」
    list_low_score_quizzes = []                      # 建立一個空清單，用來記錄總分低於 100 分的考卷名單
    list_missing_columns_quizzes = []                # 建立一個空清單，用來記錄缺少必填欄位的考卷名單
    list_valid_file_paths = []                       # 建立一個空清單，用來記錄通過所有檢查的檔案完整路徑
    list_error_file_names = []                       # 建立一個空清單，用來記錄有出現任何錯誤的檔案純檔名

    # 3. 變更迴圈：逐一處理使用者「選擇出的檔案們」
    for str_excel_file_path in list_selected_excel_paths:  # 將使用者選擇的路徑清單，逐一拿出來處理
        str_excel_file_name = os.path.basename(str_excel_file_path) # 把完整路徑的最尾端 (純檔名+副檔名) 萃取出來
        
        try:                                         # 嘗試執行以下讀取 Excel 的動作，攔截可能的讀取崩潰
            excel_workbook = pd.ExcelFile(str_excel_file_path) # 將該路徑的 Excel 檔案載入到記憶體變成 pandas 活頁簿物件
            # 先讀取全部資料(統一為字串格式)以尋找 #QTYPE 存在於哪一列
            df_quiz_data = pd.read_excel(excel_workbook, sheet_name=excel_workbook.sheet_names[0], header=None, dtype=str) # 讀取第一個工作表，不預設標題列
        except Exception as e:                       # 萬一遇到開檔錯誤 (例如檔案損毀或被其他軟體鎖定)
            print(f"⚠️ 跳過 {str_excel_file_name}: 無法讀取 Excel ({e})。") # 在終端機印出錯誤且附帶原本的錯誤訊息 e
            list_error_file_names.append(str_excel_file_name)  # 把這個打不開的檔案名稱加進「錯誤名單」
            continue                                 # 直接略過這個檔案，重新下一輪迴圈處理下一個檔案
            
        # 找到第一次出現 "#QTYPE" 的列索引，因為之前的列可能是測驗的說明文字
        int_header_row_index = None                  # 設定標題列的行數變數，預設為空 (None)
        for i in range(len(df_quiz_data)):           # 從第 0 列開始往下逐列掃描讀進來的 DataFrame
            if str(df_quiz_data.iloc[i, 0]).strip() == "#QTYPE": # 如果那一列的第一個儲存格內容去除空白後等於 "#QTYPE"
                int_header_row_index = i             # 記錄下這個列數 (索引值 i)
                break                                # 既然找到了就立刻中斷尋找迴圈，不往下找了
                
        if int_header_row_index is None:             # 如果掃描完全部列都找不到 "#QTYPE"
            print(f"⚠️ 跳過 {str_excel_file_name}: 第一欄找不到 '#QTYPE'。") # 印出找不到標記的警告訊息
            list_error_file_names.append(str_excel_file_name) # 將此檔案歸類為錯誤檔案
            continue                                 # 跳掉這個檔案不做後續檢查

        # 從 "#QTYPE" 開始重新載入，並將該列設為欄位名稱
        df_quiz_data = pd.read_excel(excel_workbook, sheet_name=excel_workbook.sheet_names[0], skiprows=int_header_row_index, dtype=str) # 重新讀檔，丟掉標題列上方(skiprows)的說明贅字
        
        # 填補空值以利後續操作
        df_quiz_data = df_quiz_data.fillna("")       # 將讀取進來的空值 (NaN) 全部替換成空字串 ("") 方便文字長度判斷
        
        # 核心邏輯 1：過濾掉以 "$" 開頭的註解列
        if not df_quiz_data.empty and len(df_quiz_data.columns) > 0: # 確保剛剛讀進來的資料表不是完全空白的
            str_first_column_name = df_quiz_data.columns[0]          # 取得資料表第一個欄位的正確名稱 (此時應該要是 "#QTYPE")
            # 只保留第一欄「開頭不是 $」的資料，把 $ 開頭的當作註解砍掉
            df_quiz_data = df_quiz_data[~df_quiz_data[str_first_column_name].astype(str).str.strip().str.startswith("$")] # 使用波浪號 ~ 進行布林反向選擇過濾
            
        # 核心邏輯 2：【嚴格欄位順序守門員】
        list_actual_headers = [str(col).strip() for col in df_quiz_data.columns] # 取得當下這份 Excel 頭尾去空白的實體表頭陣列
        str_format_error_msg = ""                    # 初始化順序錯誤的訊息變數
        
        for int_col_idx, str_expected_header in enumerate(list_strict_expected_headers): # 將黃金標準的欄位名稱與索引逐一拿出來比對
            if int_col_idx >= len(list_actual_headers): # 如果檔案實際的欄位數量不足 10 欄
                str_format_error_msg = f"缺少 {chr(65+int_col_idx)} 欄或以後的必填表頭 ({str_expected_header})" # chr(65) 就是字元 'A'，動態推算欄名 A~J 給出錯誤
                break                                # 立刻放棄後續欄位檢查，拋出錯誤
            elif list_actual_headers[int_col_idx] != str_expected_header: # 如果在同一個索引位置的文字跟預期的黃金標準「完全不一致」
                str_format_error_msg = f"{chr(65+int_col_idx)} 欄位置錯誤 (應為: {str_expected_header}，實際卻寫成: {list_actual_headers[int_col_idx]})" # 定位錯誤欄位(例如：B 欄位置錯誤) 
                break                                # 攔截成功，跳出檢查
                
        if str_format_error_msg:                     # 若守門員發現欄位順序有任何錯位或名稱打錯
            list_missing_columns_quizzes.append({"File": str_excel_file_name, "Missing Columns": f"【嚴重格式錯誤】{str_format_error_msg}"}) # 記錄嚴重順序錯誤至缺欄報表 (在此充當格式報表)
            list_error_file_names.append(str_excel_file_name) # 將考卷列入無情淘汰名單
            continue                                 # 終止後續的選題內容計分防呆，讓製卷者直接去修表頭
            
        # 核心邏輯 3：將題目群組化 (Grouping)
        # 上方的守門員保證了前 10 欄 A~J 的排序是正確的，所以底下能毫無懸念安全抓取
        list_cols_to_fill_downward = ["#QTYPE", "Subject", "Weight", "Difficulty", str_col_limit_type, str_col_limit_count, str_col_no_random] # 定義一定要向下拉滿空白的題頭共用屬性

        for col in list_cols_to_fill_downward:       # 走訪這些需要向下填滿的欄位名稱
            df_quiz_data[col] = df_quiz_data[col].replace(r'^\s*$', pd.NA, regex=True).ffill() # 將純空白換成系統空值 NaN，再用 ffill() (向前填充) 將第一列的資料往下拉滿到選項列
            
        list_current_quiz_errors = []                # 準備一個清單收集「當下」這份正在檢查的考卷內部的題目錯誤
        bool_has_invalid_questions = False           # 建立變數用來判定這份考卷到底有沒有任何無效的題目，預設為否
        float_quiz_total_score = 0.0                 # 將總分計數器歸零
        
        df_grouped_by_subject = df_quiz_data.groupby("Subject", sort=False) # 利用 "Subject" (考題題目) 這個欄位把行合併成分組，同一題的文字跟選項會被歸在同一個小 DataFrame
        
        # 核心邏輯 4：根據題型逐題驗證
        for str_question_subject, df_question_rows in df_grouped_by_subject: # 逐一把剛剛分好群的題目標題(subject)與群組內容(df_question_rows)抓出來看
            str_question_type = str(df_question_rows["#QTYPE"].iloc[0]).strip()     # 題型為該題群的第一列 #QTYPE，並去除前後空白
            str_question_score = str(df_question_rows["Weight"].iloc[0]).strip()    # 分數為該題群的第一列 Weight，並去除前後空白
            str_question_difficulty = str(df_question_rows["Difficulty"].iloc[0]).strip() # 難度為該題群的第一列 Difficulty，並去除前後空白
            
            # 安全地取得選項限制欄位的值
            str_limit_type = str(df_question_rows[str_col_limit_type].iloc[0]).strip() # 由於表頭必為正確排序，直接透過確定存在的欄名拿取限制種類 (0, 1, 或 2)
            str_limit_count = str(df_question_rows[str_col_limit_count].iloc[0]).strip() # 直接拿取限制個數數量 ("" 或是某個數字字串)
            
            # 安全地取得選項是否隨機欄位的值
            str_no_random_val = str(df_question_rows[str_col_no_random].iloc[0]).strip() # 抓出是否不隨機排序 (0 或 1)

            # 1. 檢查 Difficulty 是否介於 1~5
            try:                                     # 嘗試將文字難度轉為純數字的浮點數
                float_question_difficulty = float(str_question_difficulty) # 轉型為 floats
                if not (1 <= float_question_difficulty <= 5): # 判斷數值是否未落在 1 到 5 之間
                    list_current_quiz_errors.append({"Subject": str_question_subject, "Error": f"Difficulty ({str_question_difficulty}) 不在 1~5 之間"}) # 若不符合則加上錯誤描述
            except ValueError:                       # 文字不是數字 (如空字串或英文字) 會跳出 ValueError
                list_current_quiz_errors.append({"Subject": str_question_subject, "Error": "Difficulty 格式不正確或為空"}) # 寫入格式錯誤描述
                
            # 2. 計算考卷總分
            try:                                     # 嘗試將該題的文字配分轉為數字
                float_quiz_total_score += float(str_question_score) # 轉換成 float 並累加進整份考卷的總分計數器
            except ValueError:                       # 分數為空白或是文字導致無法轉為數字
                list_current_quiz_errors.append({"Subject": str_question_subject, "Error": "Weight 格式不正確或為空"}) # 寫下格式錯誤
                
            # 3. 計算正確答案 (y) 的數量與選項數
            str_answer_column_name = "Yes/No/Answer" # 定義答案欄位名稱防呆變數
            series_all_answers = df_question_rows[str_answer_column_name].astype(str).str.strip().str.lower() # 把這題所有答案格變成字串，清掉空白，強迫轉小寫 (大小寫 y 皆視為 y)
            int_correct_answer_count = (series_all_answers == 'y').sum() # 計算這個 pandas Series 裡頭有幾個字元是剛好等於 'y'
            
            series_non_empty_options = df_question_rows["Option"].astype(str).str.strip() # 撈出該題所有的選項文字欄位
            int_valid_option_count = len(series_non_empty_options[series_non_empty_options != ""]) # 計算剔除空字串後，這題實際上到底有幾個真實的選項存在
            
            # 4. 依照題型實作檢查規則
            if "[TrueFalse]" in str_question_type:   # 解析：如果是判斷題/是非題
                if int_valid_option_count > 2:       # 是非題選項最多只能有 2 個 (圈或叉)
                    list_current_quiz_errors.append({"Subject": str_question_subject, "Error": f"是非題選項超過2個 (共{int_valid_option_count}個)"}) # 寫入超額選項錯誤
                if int_correct_answer_count != 1:    # 正確答案的數量 ( y ) 必須不多不少剛好等於 1
                    list_current_quiz_errors.append({"Subject": str_question_subject, "Error": f"是非題未設定唯一解答"}) # 寫入未設定解答的報錯
                    
            elif "[SingleChoice]" in str_question_type: # 解析：如果是單選題
                if int_valid_option_count > 9:       # 規則明訂單選題選項不得超過 9 個
                    list_current_quiz_errors.append({"Subject": str_question_subject, "Error": f"單選題選項超過9個 (共{int_valid_option_count}個)"}) # 寫入超額錯誤
                if int_correct_answer_count != 1:    # 單選題只能有一個標準答案，y 必須剛好為 1
                    list_current_quiz_errors.append({"Subject": str_question_subject, "Error": f"單選題未設定唯一解答"}) # 報錯提醒沒有正確標示單選解答
                if str_no_random_val not in ["", "0", "1"]: # 檢查隨機屬性是否合法 (如果沒有填就是空字串，也算合法)
                    list_current_quiz_errors.append({"Subject": str_question_subject, "Error": f"單選題 NoRandom 設定錯誤 ({str_no_random_val})，只能填 0 或 1"}) # 當不為 0 或 1 則報錯
                    
            elif "[MultipleChoice]" in str_question_type: # 解析：如果是複選題/多選題
                if int_valid_option_count > 9:       # 複選題跟單選題一樣選項不能超過 9 個
                    list_current_quiz_errors.append({"Subject": str_question_subject, "Error": f"複選題選項超過9個 (共{int_valid_option_count}個)"}) # 寫下錯誤 
                if int_correct_answer_count < 1:     # 複選題必須至「至少有 1 個」解答，y 數量必須 >= 1
                    list_current_quiz_errors.append({"Subject": str_question_subject, "Error": f"複選題未設定解答"}) # 若連一個 y 都沒有，則視為錯誤
                if str_no_random_val not in ["", "0", "1"]: # 檢查隨機屬性是否合法
                    list_current_quiz_errors.append({"Subject": str_question_subject, "Error": f"複選題 NoRandom 設定錯誤 ({str_no_random_val})，只能填 0 或 1"}) # 當不為 0 或 1 則報錯
                
                # 新增邏輯：複選題選項限制判斷 (Option Limit)
                if str_limit_type in ["1", "2"]:     # 判斷如果有啟動最高限制 (1) 或 最低限制 (2)
                    try:                             # 嘗試將輸入的限制數量轉換為安全整數
                        int_limit_count = int(float(str_limit_count or 0)) # 先處理成 float 再轉 int, 避免 '3.0' 或空字串造成報錯
                        if int_limit_count <= 0:     # 有啟動限制，但使用者忘記填入數字或是填了負數
                            list_current_quiz_errors.append({"Subject": str_question_subject, "Error": f"啟用了複選限制類型({str_limit_type})，但未填寫有效下限制個數({str_limit_count})"}) # 發出詳細警示
                    except ValueError:               # 若填入的根本不是數字 (例如英文字母)
                        list_current_quiz_errors.append({"Subject": str_question_subject, "Error": f"限制個數格式錯誤({str_limit_count})"}) # 直接報錯通知製卷者
                    
            elif "[FillInBlank]" in str_question_type: # 解析：如果是填充題
                # 填充題答案必填於第二行的 Yes/No/Answer 欄位
                if len(df_question_rows) < 2 or str(df_question_rows.iloc[1][str_answer_column_name]).strip() == "": # 若題目群總共不到2行，或是第2行的答案格為空字串
                    list_current_quiz_errors.append({"Subject": str_question_subject, "Error": "填充題未填寫答案 (需填於第二行)"}) # 彈出格式錯誤提示
                    
            elif "[Essay]" in str_question_type:     # 解析：如果是簡答題/問答題
                # 問答題與填充題邏輯雷同，需有第二行的參考答案才能建立
                if len(df_question_rows) < 2 or str(df_question_rows.iloc[1][str_answer_column_name]).strip() == "": # 若缺乏第二行或該行欄位為空
                    list_current_quiz_errors.append({"Subject": str_question_subject, "Error": "問答題未填寫參考答案 (需填於第二行)"}) # 詳細紀錄缺漏哪一項
                    
            else:                                    # 解析：如果前面的 if 通通沒配對到
                list_current_quiz_errors.append({"Subject": str_question_subject, "Error": f"無法識別的題型代碼: {str_question_type}"}) # 報錯此題型未被規則涵蓋 (或使用者打錯中括號內容)
                
        # 檢查整份考卷權重是否足夠 100
        bool_has_low_score = float_quiz_total_score < 100 # 如果累加的 float_quiz_total_score 小於 100 分，布林設為 True
        
        # 將有問題的題目彙整寫入 Invalid 清單
        if list_current_quiz_errors:                 # 剛剛建立的暫時性錯誤清單如果不為空 (代表此考卷真的有壞錯題目)
            bool_has_invalid_questions = True        # 立刻豎起有錯旗標 True
            df_error_details = pd.DataFrame(list_current_quiz_errors) # 將題目對應文字錯誤的 dict 清單，轉換回 pandas 的 DataFrame 物件
            df_error_details.insert(0, "File", str_excel_file_name) # 在這份報表的最前面塞入第一欄「檔案名稱」，方便追蹤出處
            list_invalid_questions_df.append(df_error_details)  # 把這份局部的有錯 df 加進總清單當中
            
        if bool_has_low_score:                       # 如果權重總計剛剛判定不足 100 分
            list_low_score_quizzes.append({"File": str_excel_file_name, "Total Weight": float_quiz_total_score}) # 把考卷名字跟實際總分丟進特製的少分提醒名單中
            
        if not bool_has_invalid_questions and not bool_has_low_score: # 大關卡：如果考卷「沒有任何壞題目」而且「分數超過一百分」
            list_valid_file_paths.append(str_excel_file_path) # 這就是一份完美合規的考試卷，將完整路徑加進合格過關名單
        else:                                        # 否則 (要嘛有錯題，要嘛權重太低)
            list_error_file_names.append(str_excel_file_name) # 則無情地把這份考卷丟進大錯誤名單當中

    # ---------------------------------------------------------
    # 輸出報告與 UI 提示
    # ---------------------------------------------------------
    str_final_error_report_path = os.path.join(str_error_report_dir, "Quiz_Validation_Report.xlsx") # 組裝未來要輸出的錯誤報告完整絕對路徑 (.xlsx 檔案)

    if list_invalid_questions_df or list_low_score_quizzes or list_missing_columns_quizzes: # 只要上面這三個名冊「其中有一個有東西」(也就是不是全軍平安)
        print("❌ 一些測驗檔案有問題。")                # 印出紅色叉叉表示有壞考卷存在
        for str_err_file in set(list_error_file_names): # 把有錯名字的清單過在 set 將重複的名字吃掉 (unique) 後迴圈印出
            print(f"🔸 {str_err_file}")              # 在每一個有錯的檔名前面加上小橘點裝飾印出

        with pd.ExcelWriter(str_final_error_report_path, engine="xlsxwriter") as excel_writer: # 使用 xlsxwriter 引擎開啟一個空的 Excel 寫入器，並準備寫往組好的這個路徑
            if list_invalid_questions_df:            # 若有非法題目 df 存在
                df_final_invalid_questions = pd.concat(list_invalid_questions_df, ignore_index=True) # 用 concat 將很多考卷合併進來的清單合併成一整個超大表、忽略原始 Index
                df_final_invalid_questions.to_excel(excel_writer, index=False, sheet_name="Invalid Questions") # 寫入名為 "Invalid Questions" 的工作表 (分頁) 中
            if list_low_score_quizzes:               # 若有分數偏低考卷 df 存在
                df_low_weight = pd.DataFrame(list_low_score_quizzes) # 轉為表格型態
                df_low_weight.to_excel(excel_writer, index=False, sheet_name="Low Weight Files") # 寫入名為 "Low Weight Files" 的過低名單專用分頁
            if list_missing_columns_quizzes:         # 若有缺少必要欄位的檔案存在
                df_missing_columns = pd.DataFrame(list_missing_columns_quizzes) # 將紀錄缺了甚麼的清單轉成表
                df_missing_columns.to_excel(excel_writer, index=False, sheet_name="Missing Columns") # 存在另一個分頁 "Missing Columns" 當中讓製卷人員自我調整

        str_message = f"檢查完畢！\n\n共發現 {len(set(list_error_file_names))} 份錯誤檔案。\n綜合錯誤報告已保存至：\n{str_final_error_report_path}" # 設計結案的彈跳視窗文字
        messagebox.showwarning("發現錯誤", str_message) # 使用 warning 層級跳出提示告訴使用者有抓到錯誤
        print(f"📄 綜合報告已保存至: {str_final_error_report_path}") # 在終端機備份顯示檔案匯出路徑
    else:                                            # 如果上述三個名冊都是空空的，代表非常完美全部通過
        str_message = "太棒了！所有選擇的測驗檔案皆無錯誤。"  # 設計鼓舞人心的滿分字眼
        messagebox.showinfo("檢查通過", str_message)   # 用 info 高層級綠色藍色通知彈跳出來讓使用者知道全數沒問題

    # 將完全沒有問題的檔案複製到 output 資料夾
    if list_valid_file_paths:                        # 如果我們有抓到通過驗證的好檔案清單
        for str_file_path in list_valid_file_paths:  # 將每一個好檔案路徑迴圈抓出
            str_file_name = os.path.basename(str_file_path) # 提煉原本只有檔案名稱的短名
            str_destination_file = os.path.join(str_success_output_dir, str_file_name) # 把檔名結合進剛剛建立的安全屋 (output資料夾) 內產生終點路徑
            shutil.copy2(str_file_path, str_destination_file) # 將該檔案「連同原始的創建日期、修改日期中介資料元」一起完整無損複製過去
        
        str_success_message = f"已將 {len(list_valid_file_paths)} 份無錯誤之檔案複製至：\n{str_success_output_dir}" # 文字排版告訴使用者搬了幾份檔案
        messagebox.showinfo("複製完成", str_success_message) # 彈跳對話框慶祝搬檔成功
        print(f"✅ 所有有效的測驗檔案已複製到: {str_success_output_dir}") # 在文字終端機同步此訊息
    else:                                            # 如果過關清單是空的，完全沒有過關的檔案時
        print("✅ 沒有找到要複製的有效檔案。")           # 印出提醒我們甚麼都沒般，代表全軍覆沒

if __name__ == "__main__":                           # 標準 python 起手式，當本支程式是被直接執行，而非被其他模組 import 當成庫時
    main()                                           # 正式執行 main 主函式
