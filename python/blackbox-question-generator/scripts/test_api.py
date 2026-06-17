#!/usr/bin/env python3
# scripts/test_api.py
# Test script for the Black Box API

import requests  # 匯入發送網路請求的模組
import json  # 匯入處理 JSON 格式的模組
import os  # 匯入處理本地檔案路徑模組
from pathlib import Path  # 匯入現代化路徑操作模組

str_base_url = "http://localhost:8000"  # 字串變數，宣告共用的本地端測試主機位址

def test_health():  # 定義專責測試健康檢查端點之函式
    """Test health check endpoint"""
    print("Testing health check...")  # 提示將要測試何種 API Endpoint
    response_health = requests.get(f"{str_base_url}/api/health")  # 回應變數，對目標位址發出 GET 請求
    print(f"Status: {response_health.status_code}")  # 印出伺服器回應的 HTTP 狀態碼
    print(f"Response: {json.dumps(response_health.json(), indent=2)}\n")  # 印出格式化縮排後的 JSON 雙方交涉結果
    return response_health.status_code == 200  # 若確實回傳 HTTP 200 則核准視為順利

def test_config():  # 定義測試配置檔查詢端點
    """Test config endpoint"""
    print("Testing config endpoint...")  # 印出預告標題
    response_config = requests.get(f"{str_base_url}/api/config")  # 回應變數，連到取得設定檔的路徑
    print(f"Status: {response_config.status_code}")  # 印出此舉獲得之 HTTP 回應狀態
    print(f"Response: {json.dumps(response_config.json(), indent=2)}\n")  # 排版列印此 JSON
    return response_config.status_code == 200  # 當順利拿回設定檔即通過該項考驗

def test_generate_question_bank():  # 模擬真實產出題庫的核心上傳測試
    """Test question bank generation with sample data"""
    print("Testing question bank generation...")  # 紀錄即將啟動物件上傳測試程序
    
    # Create a sample file for upload
    str_sample_file_path = "/tmp/sample_material.txt"  # 字串變數，設立一個無害暫存用的虛擬測資路徑
    with open(str_sample_file_path, 'w') as file_obj:  # 若檔案不存在則創建，存在則覆寫文字用
        file_obj.write("""
        Chapter 1: Introduction to Python
        
        Python is a high-level programming language.
        It is known for its simplicity and readability.
        
        Chapter 2: Basic Concepts
        
        Variables are containers for storing data values.
        Functions are reusable blocks of code.
        """)  # 將預先準備好的教材文章塞入剛開好的測試文字檔之中
    
    # Prepare request data
    with open(str_sample_file_path, 'rb') as file_read:  # 為了真實模擬上傳，用二進位方式再次開啟它準備串流送出
        dict_files = {'materials': (os.path.basename(str_sample_file_path), file_read)}  # 字典變數，將要以 Multipart 形式攜帶的檔案打包
        dict_data = {  # 字典變數，這些是使用者要一併填寫傳交的表單字串設定值
            'question_types': ['true_false', 'single_choice'],  # 指定產出是與單兩款基本題型
            'difficulty': 'medium',  # 設定這包考卷的程度為中間
            'language': 'zh-TW'  # 輸出指定語系支援
        }
        
        response_post = requests.post(  # 回應變數，正式把所有請求內容發射去後台目標網址
            f"{str_base_url}/api/generate-question-bank",  # 路徑精準設定
            files=dict_files,  # 實體夾帶附檔
            data=dict_data  # 字串欄位一併押送
        )
    
    print(f"Status: {response_post.status_code}")  # 印出上傳動作獲得的回應數字碼
    print(f"Response: {json.dumps(response_post.json(), indent=2)}\n")  # 觀察後台有沒有拋出錯誤 JSON
    
    # Clean up
    os.remove(str_sample_file_path)  # 測試完畢不留垃圾強制刪除該測資檔案實體
    
    return response_post.status_code == 200  # 若成功拿到 HTTP 200 就宣判過關

def test_invalid_request():  # 設計一個測試 API 強健程度的防呆腳本
    """Test error handling with invalid request"""
    print("Testing invalid request handling...")  # 看看系統檔不檔得住沒有材料的奧客封包
    
    response_err = requests.post(  # 回應變數，開始這場搞破壞的小小行動
        f"{str_base_url}/api/generate-question-bank",  # 對著主目標丟出請求
        data={'difficulty': 'invalid'}  # 隨意亂塞沒意義的垃圾空殼參數
    )
    
    print(f"Status: {response_err.status_code}")  # 看看它是被正常阻止住
    print(f"Response: {json.dumps(response_err.json(), indent=2)}\n")  # 印出被系統安全擋下的理由宣判
    
    return response_err.status_code == 400  # 順利引發 HTTP 400 Bad Request 才是好的攔截防禦

if __name__ == '__main__':  # 若從外界叫本腳本起來值勤
    print("="*50)  # 視覺裝飾畫上等號底線
    print("Black Box API Test Suite")  # 高掛招牌寫上系統驗明正身測項集結
    print("="*50)  # 將招牌封邊
    print()  # 安插一個美觀純空行
    
    list_tests = [  # 陣列變數，裝載所有要被調教的每個單項測號與指標
        ("Health Check", test_health),  # 第一關
        ("Config Endpoint", test_config),  # 第二關
        ("Invalid Request", test_invalid_request),  # 第三關
    ]
    
    dict_results = {}  # 字典變數，記分板拿來登記成績單專用
    for str_test_name, func_test_func in list_tests:  # 將考題名字跟考官一個個帶出來檢核
        try:  # 替主程式裝掛例外防護套件
            dict_results[str_test_name] = func_test_func()  # 字典變數，紀錄並儲存該項審查是否拿到通關許可
        except Exception as err_test:  # 防範套件壞掉導致戰死意外
            print(f"Error in {str_test_name}: {str(err_test)}\n")  # 印出為何考官會出意外報錯之悲劇警示
            dict_results[str_test_name] = False  # 不管怎樣成績直接登記為紅字
    
    print("="*50)  # 放榜大分隔線
    print("Test Results Summary")  # 大字報宣布這為結案綜合報告書
    print("="*50)  # 封邊
    for str_test_name, bool_passed in dict_results.items():  # 開箱將所有科目與最後生死的判讀值對在一起核對
        str_status = "✓ PASSED" if bool_passed else "✗ FAILED"  # 字串變數，若是順利就給勾勾過關文案
        print(f"{str_test_name}: {str_status}")  # 大功告成印出成績單各科表現狀態
