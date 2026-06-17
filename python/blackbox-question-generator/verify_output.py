#!/usr/bin/env python
# -*- coding: utf-8 -*-
# verify_output.py

import pandas as pd  # 匯入 pandas 模組，用於資料表處理與讀取 Excel
import os  # 匯入 os 模組，用於查詢系統檔案路徑與目錄

# Find the latest generated file
str_output_dir = 'outputs'  # 字串變數，設定存放產出檔案的資料夾名稱
list_files = [f for f in os.listdir(str_output_dir) if f.endswith('.xlsx')]  # 陣列變數，列出輸出目錄下所有副檔名為 xlsx 的檔案名稱
if list_files:  # 如果檔案清單內有資料，表示已產生過檔案
    str_latest_file = sorted(list_files)[-1]  # 字串變數，取得經過字母順序排序後的最後一個 (最新) 檔案名稱
    str_filepath = os.path.join(str_output_dir, str_latest_file)  # 字串變數，動態組合出最新檔案的完整相對路徑
    
    print('=' * 70)  # 印出 70 個等號作為視覺分隔線
    print('📊 生成的 Excel 文件內容驗證')  # 印出驗證開始的標題文字
    print('=' * 70)  # 第二條等號分隔線
    print(f'\n📁 文件: {str_filepath}')  # 在螢幕上印出即將驗證的檔案路徑
    print(f'📏 文件大小: {os.path.getsize(str_filepath):,} bytes\n')  # 動態計算檔案大小並以千分位逗號分隔格式印出
    
    # Read Excel file
    df_excel = pd.read_excel(str_filepath)  # DataFrame變數，將 Excel 內容讀取進記憶體中的二維陣列資料表
    
    print(f'📋 總行數: {len(df_excel)}')  # 印出整份資料表總共的橫向題目數量
    print(f'📊 總列數: {len(df_excel.columns)}')  # 印出資料表直向的屬性欄位總數量
    print(f'\n欄位名稱:')  # 提示即將印出所有欄位表頭名稱
    for int_i, str_col in enumerate(df_excel.columns, 1):  # 迴圈與計數器變數，逐一抓出 DataFrame 的每一列表頭字串
        print(f'  {int_i}. {str_col}')  # 將自動產生的數字序號與該欄位名稱印出在終端機
    
    print(f'\n📝 數據預覽:')  # 提示準備印出前幾筆資料預覽供工程師檢視
    print(df_excel.head(15).to_string())  # 取出資料表的前 15 列，並強制轉為純文字格式化排版後印出
    
    # Statistics
    series_qtype_counts = df_excel['#Qtype'].value_counts()  # Pandas Series變數，計算每一個題型類別出現各自出現幾次的統計值
    print(f'\n📊 題型統計:')  # 提示終端機即將顯示各題型題數分配表
    for str_qtype, int_count in series_qtype_counts.items():  # 開啟迴圈，分離每一種題型名稱字串與對應的高矮計數值
        if pd.notna(str_qtype) and str_qtype != '':  # 防呆機制：若題型名稱不為系統缺失值 (NaN) 且不是純空字串
            print(f'  {str_qtype}: {int_count} 題')  # 則正常印出題型名稱以及其涵蓋的總題數
    
    print('\n✅ Excel 文件驗證完成！')  # 腳本執行告一段落，印出成功結束提示字眼
else:  # 若開頭的 list_files 清單中找不到任何以 xlsx 結尾的檔案
    print('未找到生成的 Excel 文件')  # 在終端機印出警告錯誤，提示使用者或程式尚未產出任何成果檔
