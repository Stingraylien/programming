# config.py
# Configuration settings for the Black Box Question Generator

import os  # 匯入內建作業系統模組以處理環境變數與路徑

# Flask settings
str_flask_env = os.getenv('FLASK_ENV', 'development')  # 字串變數，從環境變數取得 FLASK_ENV，若無則預設為開發環境
bool_debug = str_flask_env == 'development'  # 布林變數，若環境為開發環境則開啟除錯模式
bool_testing = os.getenv('TESTING', False)  # 布林變數，從環境變數決定是否開啟測試模式

# File upload settings
str_upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')  # 字串變數，動態組合上傳資料夾的絕對路徑
str_output_folder = os.path.join(os.path.dirname(__file__), 'outputs')  # 字串變數，動態組合產出資料夾的絕對路徑
int_max_content_length = 100 * 1024 * 1024  # 整數變數，限制最大上傳檔案大小為 100MB
set_allowed_extensions = {'pdf', 'pptx', 'docx', 'mp4', 'txt'}  # 集合變數，定義系統允許處理的檔案副檔名

# Question generation settings
str_default_difficulty = 'medium'  # 字串變數，設定預設出題難易度為中等
str_default_language = 'zh-TW'  # 字串變數，設定預設輸出語言為繁體中文
int_min_questions = 1  # 整數變數，限制每次最少產生測驗題數
int_max_questions = 100  # 整數變數，限制每次最多產生測驗題數

# Supported options
list_supported_question_types = ['true_false', 'single_choice', 'multiple_choice', 'fill_in_blank', 'essay']  # 陣列變數，系統支援的所有題型代碼
list_supported_difficulties = ['easy', 'medium', 'hard']  # 陣列變數，支援的三種難度分級
list_supported_languages = ['zh-TW', 'en-US']  # 陣列變數，支援的語言清單

# Generation strategy
str_generation_strategy = 'rule_based'  # 字串變數，設定目前的出題策略為規則導向 (rule_based)

# API version
str_api_version = '1.0.0'  # 字串變數，標示當前 API 服務的主要版本號