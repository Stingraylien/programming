import requests  # 匯入 HTTP 請求模組，用於向本地 API 伺服器發送測試請求
import os  # 匯入 os 模組，用於動態組合路徑與管理暫存測試檔案

str_api_url = "http://127.0.0.1:8000/api/generate-question-bank"  # 字串變數，定義本地測試伺服器的 API 端點位址
str_course_name = "範例課程 101"  # 字串變數，設定用於本次測試的假課程名稱

dict_form_data = {  # 字典變數，定義要傳送給 API 的 HTTP 表單請求參數
    "course_name": str_course_name,  # 帶入課程名稱字串
    "question_types": ["true_false", "single_choice", "multiple_choice", "fill_in_blank", "essay"],  # 陣列，列出所有要測試的題型種類
    "difficulty": "medium",  # 字串，設定本次測試採用中等難度
    "language": "zh-TW"  # 字串，指定輸出語言為繁體中文
}

def test_generate():  # 定義進行 API 整合測試的主函式
    """執行完整的 API 端點測試，模擬真實使用者上傳教材並驗證回應格式。"""
    str_dummy_file_path = os.path.join(os.path.dirname(__file__), "dummy_mock.txt")  # 字串變數，動態組合暫存假教材文字檔的絕對路徑

    # 建立假教材測試檔案
    with open(str_dummy_file_path, "w", encoding="utf-8") as obj_file:  # 物件變數，以 UTF-8 寫入模式建立假教材文字檔
        obj_file.write(  # 將模擬教材內容寫入暫存檔
            "這個課程介紹基礎的人工智慧概念。"
            "章節包含機器學習、深度學習。"
            "重點目標是理解神經網路的運作原理。\n" * 10  # 重複十次使內容具有足夠的段落量
        )

    # 發送 API 請求並取得回應
    try:  # 建立例外保護，確保測試結束後暫存檔一定被清除
        with open(str_dummy_file_path, "rb") as obj_file:  # 物件變數，以二進位模式重新開啟檔案以利 multipart 上傳
            dict_files = {"materials": (str_dummy_file_path, obj_file, "text/plain")}  # 字典變數，封裝符合 multipart/form-data 格式的上傳檔案物件
            print(f"Sending request to {str_api_url} with course_name='{str_course_name}'...")  # 顯示測試開始資訊，確認目標 URL 和課程名稱
            obj_response = requests.post(str_api_url, data=dict_form_data, files=dict_files)  # 物件變數，發送 POST 請求至 API 並接收 HTTP 回應物件

    finally:  # 無論請求成敗，都要清理暫存測試檔案
        if os.path.exists(str_dummy_file_path):  # 確認暫存測試檔案確實存在再執行刪除
            os.remove(str_dummy_file_path)  # 刪除暫存假教材文字檔，保持專案目錄整潔

    # 解析並顯示回應結果
    print(f"Status Code: {obj_response.status_code}")  # 印出 HTTP 狀態碼，確認 API 是否正常回應
    print("Response JSON:")  # 提示即將印出回應內容
    try:  # 嘗試解析 JSON 格式的回應內容
        print(obj_response.json())  # 若回應為合法 JSON 則直接格式化印出
    except Exception:  # 若回應不是 JSON 格式（如 HTML 錯誤頁面）
        print(obj_response.text)  # 改以純文字模式印出原始回應內容供除錯

if __name__ == "__main__":  # 只有當此腳本被直接執行時（非被 import 時）才啟動測試
    test_generate()  # 呼叫主測試函式，開始執行 API 整合測試流程
