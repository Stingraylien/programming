#!/usr/bin/env python3
# scripts/start_server.py
# Start the Black Box API server

import os  # 匯入 os 模組處理系統變數與環境
import sys  # 匯入 sys 模組以動態塞入執行路徑

# Add parent directory to path
str_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # 字串變數，抓出上層根目錄的絕對路徑
sys.path.insert(0, str_parent_dir)  # 把根目錄推到環境變數第一順位引導套件尋找

from api.main import app as flask_app  # 從 api 模組引入建好的 Flask 主體應用

if __name__ == '__main__':  # 如果是直接呼叫本腳本執行
    int_port = int(os.environ.get('FLASK_PORT', 8000))  # 整數變數，嘗試去抓環境變數的指定 Port 否則預設 8000
    print("Starting Black Box Question Generator API...")  # 印出開啟服務的宣告文字
    print(f"Server running at http://localhost:{int_port}")  # 印出即刻起監聽的本機網址
    print("Press Ctrl+C to stop")  # 提示如何使用快捷鍵強迫中斷服務
    
    flask_app.run(debug=True, host='0.0.0.0', port=int_port)  # 啟動應用伺服器，對外所有網卡開放預設端點