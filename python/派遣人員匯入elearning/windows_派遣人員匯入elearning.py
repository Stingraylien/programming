#!/usr/bin/env python3                    # 指定使用 python3 執行此腳本
# -*- coding: utf-8 -*-                    # 設定檔案編碼為 UTF-8（支援中文）
"""
派遣人員匯入 eLearning 系統
功能：
  1. 到職匯入 – 讀取 Excel，產出到職人員 CSV
  2. 離職匯入 – 讀取 Excel，產出離職人員 CSV（IsDisabled = 1）
"""

# ─────────────────────────── 匯入模組 ───────────────────────────

import os                                  # 作業系統相關功能（檔案路徑處理）
import tkinter as tk                       # tkinter 是 python 的圖形介面函式庫
from tkinter import filedialog, messagebox # filedialog: 檔案選擇對話框, messagebox: 訊息提示框
from datetime import datetime              # datetime: 日期時間處理模組
from openpyxl.utils import get_column_letter  # openpyxl: 取得欄位字母代號（用於設定儲存格格式）
import pandas as pd                        # pandas 是 python 的資料處理函式庫（讀寫 Excel/CSV）


# ─────────────────────────── 常數定義 ───────────────────────────

INT_WINDOW_WIDTH = 360                     # 主視窗寬度（像素）
INT_WINDOW_HEIGHT = 220                    # 主視窗高度（像素）

# 檔案選擇對話框可接受的檔案格式
LIST_FILE_TYPES = [("Excel files", "*.xlsx;*.xls;*.csv")]

# 到職匯入時，Excel 來源檔案必須包含的欄位名稱
LIST_REQUIRED_COLUMNS_ONBOARD = ["工號", "姓名", "到職日", "處級名", "性別", "出生日"]

# 離職匯入時，Excel 來源檔案必須包含的欄位名稱（多了「離職日」）
LIST_REQUIRED_COLUMNS_RESIGN = ["工號", "姓名", "到職日", "處級名", "性別", "出生日", "離職日"]


# ─────────────────────────── 共用工具函式 ───────────────────────────

def _date_to_str(str_date_value) -> str:
    """將 Excel 讀入的日期值轉成 yyyy/mm/dd 字串。"""

    # 如果值是空值（NaN），回傳空字串
    if pd.isna(str_date_value):
        return ""

    # 如果值是 datetime 物件，直接格式化為 yyyy/mm/dd
    if isinstance(str_date_value, datetime):
        return str_date_value.strftime("%Y/%m/%d")

    # 以下處理字串格式的日期
    str_date_string = str(str_date_value).strip()  # 轉為字串並去除前後空白

    # 如果是空字串，回傳空字串
    if not str_date_string:
        return ""

    # 嘗試用 pandas 解析各種日期格式（如 2024-01-15、2024/1/15 等）
    try:
        dt_parsed_date = pd.to_datetime(str_date_string)  # 解析日期字串
        return dt_parsed_date.strftime("%Y/%m/%d")         # 統一輸出為 yyyy/mm/dd
    except Exception:
        return str_date_string  # 解析失敗則原樣回傳


def _gender_code(str_gender_value) -> str:
    """性別轉換：女 → 0，其餘（男） → 1"""
    return "0" if str(str_gender_value).strip() == "女" else "1"


def _read_input(str_input_filepath: str) -> pd.DataFrame:
    """
    讀取 Excel / CSV 檔案。
    第 4 列（index 3）為欄位名稱，第 5 列起為資料。
    所有欄位以字串(str)格式讀入，避免日期或數字被自動轉換。
    """
    # 取得檔案副檔名（轉為小寫）
    str_file_extension = os.path.splitext(str_input_filepath)[1].lower()

    # 根據副檔名選擇讀取方式
    if str_file_extension == ".csv":
        # CSV 檔案用 read_csv 讀取，header=3 表示第 4 列為欄位名稱
        df_source_data = pd.read_csv(str_input_filepath, header=3, dtype=str)
    else:
        # Excel 檔案用 read_excel 讀取（支援 .xlsx 和 .xls）
        df_source_data = pd.read_excel(str_input_filepath, header=3, dtype=str)

    return df_source_data  # 回傳讀取的資料表


def _validate_columns(df_data: pd.DataFrame, list_required: list) -> list:
    """
    檢查 DataFrame 是否包含所有必要欄位。
    回傳缺少的欄位名稱清單，如果全部存在則回傳空清單。
    """
    # 逐一檢查必要欄位是否存在於資料表的欄位名稱中
    list_missing = [col for col in list_required if col not in df_data.columns]
    return list_missing


def _generate_output_filename(str_label: str) -> str:
    """產生輸出檔名，格式：yyyymmdd_HHMMSS_<label>.xlsx"""
    str_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 取得目前時間戳記
    return f"{str_timestamp}_{str_label}.xlsx"                 # 組合檔名


def _build_output_row(row, str_is_disabled: str) -> dict:
    """
    將一筆來源資料（Excel 的一列）轉換為輸出 Excel 的欄位格式。
    參數 str_is_disabled: "0" = 帳號啟用（到職），"1" = 帳號停用（離職）
    回傳值: 一個 dict，對應輸出 Excel 的一列資料
    """
    return {
        "EmployeeNumber": str(row.get("工號", "")).strip(),             # 員工編號 ← 工號
        "Account": str(row.get("工號", "")).strip(),                    # 帳號 ← 工號
        "FirstName": str(row.get("姓名", "")).strip(),                  # 名字 ← 姓名
        "LastName": "",                                                 # 姓氏（留空）
        "OnboardDate": _date_to_str(row.get("到職日", "")),            # 到職日期 ← 到職日
        "Gender(female=0:male=1)": _gender_code(row.get("性別", "")),  # 性別代碼 ← 性別
        "Birthday": _date_to_str(row.get("出生日", "")),               # 生日 ← 出生日
        "Email": "@",                                                   # 電子郵件（預設 @）
        "GradeName": "",                                                # 職等（留空）
        "DutyName": "",                                                 # 職務（留空）
        "Title": "",                                                    # 職稱（留空）
        "Groups(Separate with a comma)": str(row.get("處級名", "")),          # 群組
        "Company": "",                                                  # 公司（留空）
        "OfficePhone": "",                                              # 辦公電話（留空）
        "MobilePhone": "",                                              # 手機（留空）
        "Password": str(row.get("工號", "")).strip(),                   # 密碼 ← 工號（預設）
        "IsDisabled(no=0:yes=1)": str_is_disabled,                     # 是否停用帳號
        "NTAccount": "",                                                # NT 帳號（留空）
        "InductionDate": _date_to_str(row.get("到職日", "")),          # 入職日期 ← 到職日
    }


def _process_file(str_title: str, list_required_columns: list,
                   str_is_disabled: str, str_output_label: str):
    """
    共用的檔案處理流程（到職/離職共用此函式）：
    1. 開啟檔案選擇對話框，讓使用者選擇 Excel 檔案
    2. 讀取檔案內容
    3. 驗證必要欄位是否存在
    4. 逐列轉換資料格式
    5. 輸出為 Excel 檔案（所有儲存格強制為文字格式）
    """
    # ── 步驟 1：開啟檔案選擇對話框 ──
    str_selected_file = filedialog.askopenfilename(
        title=str_title,              # 對話框標題
        filetypes=LIST_FILE_TYPES,    # 可選擇的檔案類型
    )
    if not str_selected_file:
        return  # 使用者按「取消」，直接結束函式

    # ── 步驟 2：讀取 Excel / CSV 檔案 ──
    try:
        df_source_data = _read_input(str_selected_file)  # 讀取來源資料
    except Exception as error:
        # 讀取失敗時顯示錯誤訊息
        messagebox.showerror("讀取失敗", f"無法讀取檔案：\n{error}")
        return

    # ── 步驟 3：驗證必要欄位是否存在 ──
    list_missing = _validate_columns(df_source_data, list_required_columns)
    if list_missing:
        # 如果有缺少的欄位，顯示錯誤訊息並列出缺少的欄位名稱
        str_missing = "、".join(list_missing)  # 將缺少的欄位用頓號串接
        messagebox.showerror("欄位缺少", f"Excel 缺少以下必要欄位：\n{str_missing}")
        return

    # ── 步驟 4：逐列轉換資料 ──
    list_output_rows = []                              # 建立空清單，用來存放轉換後的資料
    for _, row in df_source_data.iterrows():           # 逐列迭代來源資料
        list_output_rows.append(                       # 將轉換後的資料加入清單
            _build_output_row(row, str_is_disabled)    # 呼叫共用函式轉換欄位
        )

    # ── 步驟 5：輸出 Excel 檔案（所有儲存格強制為文字格式） ──
    df_output_data = pd.DataFrame(list_output_rows)    # 將清單轉為 DataFrame
    str_output_filename = _generate_output_filename(str_output_label)   # 產生輸出檔名
    str_output_directory = os.path.dirname(str_selected_file)           # 取得來源檔案所在資料夾
    str_output_filepath = os.path.join(str_output_directory, str_output_filename)  # 組合完整輸出路徑

    # 寫入 Excel 檔案
    with pd.ExcelWriter(str_output_filepath, engine="openpyxl") as writer:             # 建立 Excel 寫入器
        df_output_data.to_excel(writer, index=False, sheet_name="Sheet1")               # 寫入資料
        worksheet = writer.sheets["Sheet1"]                                             # 取得工作表物件
        # 將所有儲存格設定為文字格式（避免 Excel 自動轉換日期或數字）
        for int_col_index in range(1, len(df_output_data.columns) + 1):                 # 迭代每一欄
            str_col_letter = get_column_letter(int_col_index)                            # 取得欄位字母（A, B, C...)
            for cell in worksheet[str_col_letter]:                                       # 迭代該欄的每一個儲存格
                cell.number_format = "@"                                                 # 設定格式為文字（@ = 文字格式）

    # 顯示完成訊息
    messagebox.showinfo("完成", f"{str_output_label} Excel 已產出：\n{str_output_filepath}")


# ─────────────────────────── 到職匯入 ───────────────────────────

def process_onboard():
    """處理到職人員匯入：IsDisabled = 0（帳號啟用）"""
    _process_file(
        str_title="選擇 Excel 檔案（到職）",                   # 對話框標題
        list_required_columns=LIST_REQUIRED_COLUMNS_ONBOARD,   # 到職必要欄位
        str_is_disabled="0",                                    # 0 = 帳號啟用
        str_output_label="到職人員",                            # 輸出檔名標籤
    )


# ─────────────────────────── 離職匯入 ───────────────────────────

def process_resign():
    """處理離職人員匯入：IsDisabled = 1（帳號停用）"""
    _process_file(
        str_title="選擇 Excel 檔案（離職）",                   # 對話框標題
        list_required_columns=LIST_REQUIRED_COLUMNS_RESIGN,    # 離職必要欄位
        str_is_disabled="1",                                    # 1 = 帳號停用
        str_output_label="離職人員",                            # 輸出檔名標籤
    )


# ─────────────────────────── 主選單 GUI ───────────────────────────

def main():
    """程式進入點：建立主視窗並顯示選單按鈕"""

    # 建立主視窗物件
    tk_main_window = tk.Tk()
    tk_main_window.title("派遣人員匯入 eLearning")  # 設定視窗標題
    tk_main_window.resizable(False, False)           # 禁止縮放視窗

    # 計算螢幕中央位置，使視窗置中顯示
    int_screen_x = tk_main_window.winfo_screenwidth() // 2 - INT_WINDOW_WIDTH // 2    # X 座標
    int_screen_y = tk_main_window.winfo_screenheight() // 2 - INT_WINDOW_HEIGHT // 2   # Y 座標
    tk_main_window.geometry(f"{INT_WINDOW_WIDTH}x{INT_WINDOW_HEIGHT}+{int_screen_x}+{int_screen_y}")  # 套用視窗大小與位置

    # 建立標題文字標籤
    tk.Label(tk_main_window, text="請選擇操作", font=("Arial", 16, "bold")).pack(pady=(20, 10))

    # 定義按鈕共用樣式（寬度 20 字元、字體 Arial 12pt）
    dict_button_style = dict(width=20, font=("Arial", 12))

    # 建立三個功能按鈕
    tk.Button(tk_main_window, text="到職匯入", command=process_onboard, **dict_button_style).pack(pady=5)  # 到職匯入按鈕
    tk.Button(tk_main_window, text="離職匯入", command=process_resign, **dict_button_style).pack(pady=5)   # 離職匯入按鈕
    tk.Button(tk_main_window, text="離開", command=tk_main_window.destroy, **dict_button_style).pack(pady=5)  # 離開按鈕

    # 啟動 GUI 事件迴圈（視窗持續顯示，等待使用者操作）
    tk_main_window.mainloop()


# ─────────────────────────── 程式進入點 ───────────────────────────

if __name__ == "__main__":  # 當此檔案被直接執行時（而非被 import 時）
    main()                  # 呼叫 main() 啟動程式
