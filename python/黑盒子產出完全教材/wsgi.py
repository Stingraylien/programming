#!/usr/bin/env python3
"""
Production WSGI entry point for Azure App Service
"""
import os  # 匯入 os 模組，用於動態處理作業系統目錄名稱
import sys  # 匯入 sys 模組，用於動態存取 Python 環境變數

# Add current directory to Python path
str_current_dir = os.path.dirname(__file__)  # 字串變數，抓取當前此腳本所在的絕對資料夾路徑，避免寫死
sys.path.insert(0, str_current_dir)  # 將該動態路徑強制推入環境變數的順序第一名，確保套件可被發現引用

from api.main import app as flask_app  # 從內部的 api 資料夾匯入 Flask 主實例，並以清楚的別名引入

if __name__ == "__main__":  # 若於本地端直接執行腳本測試 (非 WSGI 託管狀態)
    flask_app.run()  # 則啟動 Flask 的內建開發用伺服器監聽請求
