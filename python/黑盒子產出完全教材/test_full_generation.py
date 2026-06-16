#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_full_generation.py
# 完整的題庫生成測試

import sys  # 匯入 sys 模組以設定引用路徑
import io  # 匯入 io 模組以處理記憶體內的位元組流
import os  # 匯入 os 模組以處理路徑與檔案檢查

sys.path.insert(0, '.')  # 將當前目錄加入引用路徑最前方

from api.main import app  # 從 api 模組匯入 Flask 實例 (app)

def test_full_generation():  # 定義測試完整生成流程的主函式
    """測試完整的題庫生成流程"""
    print('=' * 60)  # 印出 60 個等號作為視覺分隔線
    print('黑盒子題庫產生器 - 完整功能測試')  # 印出測試程式的標題
    print('=' * 60)  # 印出 60 個等號作為視覺分隔線
    print()  # 印出空白行
    
    with app.test_client() as client_test:  # 開啟 Flask 的測試用戶端，命名為 client_test 以進行測試模擬請求
        # Test 1: Health Check
        print('1️⃣  健康檢查端點')  # 提示即將進行健康檢查端點測試
        response_health = client_test.get('/api/health')  # 測試響應變數，對 health 端點發送 GET 請求
        print(f'   ✓ 狀態碼: {response_health.status_code}')  # 印出健康檢查的狀態碼
        print(f'   ✓ 狀態: {response_health.json["status"]}')  # 印出回傳 JSON 中的狀態文字
        print()  # 印出空白行
        
        # Test 2: Config
        print('2️⃣  配置信息端點')  # 提示即將進行配置設定端點測試
        response_config = client_test.get('/api/config')  # 測試響應變數，對 config 端點發送 GET 請求
        dict_config = response_config.json  # 字典變數，取得回傳的配置資訊 JSON 內容
        print(f'   ✓ 狀態碼: {response_config.status_code}')  # 印出配置測試的狀態碼
        print(f'   ✓ 支持題型: {len(dict_config["supported_question_types"])} 種')  # 印出系統所支援的題型數量
        for str_qt in dict_config["supported_question_types"]:  # 迴圈與字串變數，逐一印出支援的題型名稱
            print(f'      - {str_qt}')  # 縮排印出題型
        print()  # 印出空白行
        
        # Test 3: Generate Question Bank
        print('3️⃣  完整題庫生成測試')  # 提示進入主要生成測試
        print('   準備測試數據...')  # 印出測試資料準備中的提示
        
        bytes_test_content = b'''# Chapter 1: Python Basics
        
Python is a high-level programming language.
It is known for its simplicity and readability.

# Chapter 2: Data Types

Variables are containers for storing data.
Functions are reusable blocks of code.

# Chapter 3: Control Flow

If statements help make decisions.
Loops are used for repetition.
'''  # 位元組變數，模擬一份上傳文件的純文字資料流
        
        # Prepare file
        dict_post_data = {  # 字典變數，準備透過表單 (form-data) 上傳的資料組合
            'question_types': ['true_false', 'single_choice'],  # 陣列變數，要求測試兩種題型
            'difficulty': 'medium',  # 字串變數，要求難易度為中等
            'language': 'zh-TW',  # 字串變數，要求語言為繁體中文
            'materials': (io.BytesIO(bytes_test_content), 'test_material.txt')  # 將位元組虛擬化為實體上傳檔案
        }
        
        print('   發送生成請求...')  # 提示開始發送模擬的上傳請求
        response_generate = client_test.post(  # 測試響應變數，發送產題 API 請求並接回回應
            '/api/generate-question-bank',  # 目標 API 接收路徑
            data=dict_post_data,  # 帶入準備好的表單資料
            content_type='multipart/form-data'  # 設定傳輸通訊協定格式
        )
        
        print(f'   ✓ 狀態碼: {response_generate.status_code}')  # 印出產題請求的 HTTP 狀態碼
        
        if response_generate.status_code == 200:  # 若回應成功 (HTTP 200 OK)
            dict_result = response_generate.json  # 字典變數，取得產題成功的詳細結果 JSON 物件
            print(f'   ✓ 消息: {dict_result["message"]}')  # 印出伺服器宣稱成功的訊息文字
            print(f'   ✓ 生成的題目數: {dict_result["questions_count"]}')  # 印出系統回報的考題總數
            print(f'   ✓ 輸出文件: {dict_result["output_file"]}')  # 印出系統回報的 Excel 檔案名稱
            
            # Check if file exists
            str_output_file_path = os.path.join('outputs', dict_result['output_file'])  # 字串變數，動態組合出實體檔案的系統相對路徑
            if os.path.exists(str_output_file_path):  # 若該組合出的路徑檔案確實存在於硬碟中
                int_file_size = os.path.getsize(str_output_file_path)  # 整數變數，取得實體檔案的所佔用位元組大小
                print(f'   ✓ 文件大小: {int_file_size:,} bytes')  # 附帶千分位印出檔案大小資訊
                print(f'   ✓ 文件路徑: {str_output_file_path}')  # 印出最終輸出的相對路徑
            else:  # 若伺服器宣稱成功，但檔案實際上不存在
                print(f'   ⚠️  文件不存在: {str_output_file_path}')  # 印出警告訊息提醒使用者
        else:  # 若 API 回應失敗 (非 HTTP 200)
            print(f'   ✗ 生成失敗: {response_generate.json}')  # 直接印出報錯的詳細 JSON 變數內容
        
        print()  # 印出空白行
        
        # Test 4: Error Handling
        print('4️⃣  錯誤處理測試')  # 提示進入無效異常資料測試階段
        response_error = client_test.post('/api/generate-question-bank', data={'invalid': 'data'})  # 測試響應變數，故意送錯誤參數測試其防呆機制
        print(f'   ✓ 狀態碼: {response_error.status_code} (應為 400)')  # 確認是否有正常擋掉攔截 (應為 HTTP 400 Bad Request)
        print(f'   ✓ 錯誤信息: {response_error.json.get("error")}')  # 印出其被擋下退回的理由說明
        print()  # 印出空白行
        
    print('=' * 60)  # 印出 60 個等號作為視覺分隔線結尾
    print('✅ 所有測試完成！')  # 印出最終全部順利的提示字眼
    print('=' * 60)  # 印出 60 個等號作為視覺分隔線

if __name__ == '__main__':  # 若本腳本為在終端機被直接執行 (非作為模組引用)
    test_full_generation()  # 則啟動主測試函式開啟完整檢驗
