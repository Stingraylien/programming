from flask import Flask, request, jsonify, send_file  # 從 flask 匯入建立服務、接收請求、回傳 JSON 與寄送檔案的核心模組
import os  # 匯入 os 模組以處理系統路徑操作
import sys  # 匯入 sys 模組以動態修改套件引用路徑
from werkzeug.utils import secure_filename  # 匯入 secure_filename 函數以確保使用者上傳的檔名不具備惡意漏洞
from datetime import datetime  # 匯入 datetime 模組以取得目前的系統時間提供給檔名戳記

# Add src to path for imports
str_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # 字串變數，動態抓取上層的 src 資料夾絕對路徑
sys.path.insert(0, str_src_path)  # 將計算出的目錄推入環境變數頂端，讓本腳本能無縫載入其他內部套件

from src.input_adapter import process_file  # 匯入 Input Adapter 模組負責初步解析各類實體檔案
from src.canonical_content import standardize_content  # 匯入 Content 模組負責將異質文本內容轉為標準化資料
from src.question_generator import QuestionGenerator  # 匯入出題引擎物件
from src.xulink_exporter import export_to_excel  # 匯入 Excel 輸出模組負責將題庫打包匯出

flask_app = Flask(__name__)  # Flask實例變數，建立網路應用程式伺服器
flask_app.config['UPLOAD_FOLDER'] = 'uploads/'  # 字串變數，寫進 Flask config 設定暫存上傳資料夾的相對目錄
flask_app.config['OUTPUT_FOLDER'] = 'outputs/'  # 字串變數，寫入 Flask config 定義匯出檔案儲存目錄

# Ensure folders exist
os.makedirs(flask_app.config['UPLOAD_FOLDER'], exist_ok=True)  # 若指定之上傳資料夾尚不存在，則啟動時自動建立之
os.makedirs(flask_app.config['OUTPUT_FOLDER'], exist_ok=True)  # 若指定之輸出資料夾尚不存在，同理一併安全建立

set_allowed_extensions = {'pdf', 'pptx', 'docx', 'mp4', 'txt'}  # 集合變數，全局定義此 API 系統接受的所有檔案副檔名清單

def allowed_file(str_filename):  # 字串參數，此函式負責檢查上傳檔案名稱合法性
    """檢查上傳檔案的副檔名是否在系統核可的白名單內"""
    bool_has_dot = '.' in str_filename  # 布林變數，確認檔名字串內是否至少含有一個小數點
    bool_is_allowed = str_filename.rsplit('.', 1)[1].lower() in set_allowed_extensions  # 布林變數，從右邊切開小數點取得副檔名並轉小寫比對集合清單
    return bool_has_dot and bool_is_allowed  # 唯有檔名含小數點且為合規格式時，才回傳 True 准予通行

@flask_app.route('/api/health', methods=['GET'])  # 裝飾器設定，宣告監聽檢查伺服器健康狀態的 GET 端點
def health_check():  # 執行健康檢查回覆的核心函式
    """Health check endpoint"""
    dict_health_status = {'status': 'healthy', 'timestamp': datetime.now().isoformat()}  # 字典變數，包裝代表伺服器活著的文字與機器時間戳記
    return jsonify(dict_health_status)  # 利用 jsonify 將字典轉成 JSON 字串格式並傳送回前端瀏覽器

@flask_app.route('/api/generate-question-bank', methods=['POST'])  # 裝飾器設定，定義執行產出題庫工作任務的核心 POST API
def generate_question_bank():  # 定義接收源始檔案並控制四大引擎產出之主控制器
    """Generate XuLink question bank from uploaded materials."""
    try:  # 建立基礎 try-catch 結構，阻擋整體產出流程無預期的大崩潰
        # Validate request
        if 'materials' not in request.files:  # 確認發送來的封包欄位中，是否遺漏了名為 materials 的上傳實體欄位
            dict_err_no_materials = {'error': 'No materials uploaded'}  # 字典變數，設定對應之錯誤訊息說明物件
            return jsonify(dict_err_no_materials), 400  # 將錯訊轉 JSON 並向前端直接退回 HTTP 400 Bad Request
        
        list_files = request.files.getlist('materials')  # 陣列物件變數，利用套件一次性取得使用者丟上來的所有各類夾檔
        bool_all_empty = all(file_obj.filename == '' for file_obj in list_files)  # 布林變數，迭代檢查這包陣列內的檔名是否通通為空（沒點選）
        if not list_files or bool_all_empty:  # 如果清單空蕩蕩或確認都沒有點擊目標檔案
            dict_err_no_selection = {'error': 'No files selected'}  # 字典變數，封裝「未選取檔案」的白話報錯訊息
            return jsonify(dict_err_no_selection), 400  # 一樣立刻送出 JSON 擋回並顯示 HTTP 400 警告前端開發者
        
        # Get parameters
        list_question_types = request.form.getlist('question_types')  # 陣列字串變數，抓取 HTTP 表單夾帶之希望輸出的目標題型陣列
        str_difficulty = request.form.get('difficulty', 'medium')  # 字串變數，獲取單選之出題難度選項，若未指定則妥協為預設中等
        str_language = request.form.get('language', 'zh-TW')  # 字串變數，獲取希望使用的操作或出題語系，無指定即為預設繁體中文
        
        if not list_question_types:  # 如果客戶端粗心連一個所選題型都不給
            dict_err_no_types = {'error': 'No question types specified'}  # 字典變數，建立缺乏目標產出題型的專屬警告回覆
            return jsonify(dict_err_no_types), 400  # 原地返回對應 JSON 並附上 HTTP 400 提示使用者修正參數
        
        # Process files
        list_all_canonical_content = []  # 陣列變數，開一個空籃子準備蒐集來自所有四散檔案提煉出的乾淨標準化文字內容
        for file_obj in list_files:  # 建立迴圈，開始地毯式走訪前端丟來的每一份可能夾帶的各類檔案實體
            if file_obj and allowed_file(file_obj.filename):  # 驗證該檔案存在且其副檔名安全在我們定義白名單範圍內
                # Save uploaded file
                str_secure_name = secure_filename(file_obj.filename)  # 字串變數，先用套件剔除掉包含攻擊性等怪異路徑字元的安全副檔名
                str_timestamp = str(datetime.now().timestamp())  # 字串變數，取出當前含有小數點的機器秒數以作為防止覆蓋的專屬前綴字
                str_save_path = os.path.join(flask_app.config['UPLOAD_FOLDER'], f"{str_timestamp}_{str_secure_name}")  # 字串變數，利用 OS 套件動態串起系統認可之下傳絕對路徑
                file_obj.save(str_save_path)  # 將剛才記憶體內懸浮的上傳封包，實打實地落實寫入至此 Server 後台實體空間
                
                # Process through pipeline
                try:  # 追加一層細緻的 try-catch，就怕單份壞檔案不慎毒死整缸解析的進度
                    # Step 1: Input Adapter
                    mix_intermediate_data = process_file(str_save_path)  # 混合型結構變數，委任 Adapter 模組解析到底這堆 Bytes 要抽出影像字幕還是投影片文字塊
                    
                    # Step 2: Canonical Content
                    dict_canonical_data = standardize_content(mix_intermediate_data)  # 字典變數，要求 Content 模組將亂七八糟解算出的毛邊，統一推平為系統統一認知之大綱結構
                    list_all_canonical_content.append(dict_canonical_data)  # 開開心心將此單份教材解好之純淨內容裝載進入此批次大總匯籃子內
                except Exception as err_process:  # 無論遭遇多離奇的不兼容，解析引擎卡死了就捕捉那刻的例外變數
                    dict_err_process = {'error': f'Error processing {str_secure_name}: {str(err_process)}'}  # 字典變數，打包註明是由哪一個檔名造成的哪一種 Exception 文字
                    return jsonify(dict_err_process), 500  # 向客戶端舉白旗表示 HTTP 500，該檔案解析超乎這台伺服器本領並終止
            else:  # 若這個單獨檔案好死不死傳了個不相干的格式 (例如 .exe 壓軸)
                dict_err_invalid_type = {'error': f'Invalid file type: {file_obj.filename}'}  # 字典變數，特製告訴使用者哪份上傳清單是老鼠屎
                return jsonify(dict_err_invalid_type), 400  # 高舉 HTTP 400 斥回這份不合乎規定之表單請求
        
        # Step 3: Question Generator
        obj_generator = QuestionGenerator(strategy="rule_based")  # 物件實例變數，生出一台依靠指定系統規則而生之智能寫題出題機
        list_all_questions = []  # 陣列變數，開一個空清單好來容納待會工廠各產線熱騰騰端出之考題
        for dict_content in list_all_canonical_content:  # 從籃子裡逐一把剛剛抽好的教科書精華文稿翻找出來檢視
            list_questions = obj_generator.generate_questions(dict_content, list_question_types, str_difficulty, str_language)  # 陣列字典變數，督促出題機吐出配合題型與設定好三圍屬性的實體考點陣列
            list_all_questions.extend(list_questions)  # 將生出來之新題清單整個打破，併入到這批請求最大的總匯考題集合內
        
        if not list_all_questions:  # 假如剛才全部教材裡頭只是一堆無意義之空白，造成生題機徒勞無功端出空盤
            dict_err_no_q = {'error': 'No questions generated. Please provide valid materials.'}  # 字典變數，設計一個請使用者檢查文件內容之溫馨提示報錯
            return jsonify(dict_err_no_q), 400  # 即刻腰斬產出作業並以 HTTP 400 送出這殘酷的事實給前端
        
        # Step 4: XuLink Exporter
        str_time_fmt = datetime.now().strftime('%Y%m%d_%H%M%S')  # 字串變數，用我們地球人比較常見的讀法紀錄這歷史性出單的一刻
        str_output_filename = f"training_question_bank_{str_time_fmt}.xlsx"  # 字串變數，動態合成為這個成果檔賦予旭聯辨識之專屬唯一長檔名
        str_output_path = os.path.join(flask_app.config['OUTPUT_FOLDER'], str_output_filename)  # 字串變數，利用 OS 工具結合出即將用來儲存的實體絕對路徑
        
        export_to_excel(list_all_questions, str_output_path)  # 下令給將最後的匯出模塊，將這些內部的出題結構依照死硬旭聯條款烙印成 Excel 寫出之

        dict_success_response = {  # 字典變數，封裝了這趟偉大航程最後要頒發給客戶端的戰果說明
            'status': 'success',  # 清清楚楚標示為本請求最終已經完美過關成功
            'message': f'Successfully generated {len(list_all_questions)} questions',  # 附帶告知到底系統嘔心瀝血生出了幾道大題
            'questions_count': len(list_all_questions),  # 提供方便給前端面板製作 UI 動畫之純數字變數載體
            'output_file': str_output_filename,  # 回報那張剛燙印好的最新長檔名
            'download_url': f'/api/download/{str_output_filename}',  # 組裝成一個有規律好記好點的相對下載路由去取得它
            'timestamp': datetime.now().isoformat()  # 回報 API 任務終止的機器絕對標準時間
        }
        return jsonify(dict_success_response)  # 滿載而歸的將這包字典轉印成 JSON 交到在網路另一頭殷切期盼的使用者手上
    
    except Exception as err_global:  # 無論中途哪支掃把星導致 API 某行非預期卡死或是陣列爆掉
        dict_err_global = {'error': str(err_global)}  # 字典變數，將最原始未經修飾的報警文字框進變數內
        return jsonify(dict_err_global), 500  # 垂頭喪氣用 HTTP 500 通知前端這是一個開發者可能沒預料到的底層 Error
        
@flask_app.route('/api/download/<str_filename>', methods=['GET'])  # 以裝飾器開闢一個新的 GET 路由，開放給剛剛成功產出報表的人點擊下載
def download_file(str_filename):  # 負責這個神聖派送任務的函式，會負責接下路由末端的檔名變數
    """Download generated Excel file"""
    try:  # 還是老樣子，防止被當成肉雞輸入一堆亂七八糟亂帶路徑的要求崩壞
        str_file_path = os.path.join(flask_app.config['OUTPUT_FOLDER'], str_filename)  # 字串變數，嚴格依循我們的產出後台去推導該目標真正的系統位置
        if not os.path.exists(str_file_path):  # 若系統確認那邊真的根本不存在該名目之檔名
            dict_err_not_found = {'error': 'File not found'}  # 字典變數，撰寫這份東西不在我們守備範圍之聲明
            return jsonify(dict_err_not_found), 404  # 送交 HTTP 404 表明這網頁迷路或檔案丟失之意給外界
        return send_file(str_file_path, as_attachment=True, download_name=str_filename)  # 成功通過考驗，利用黑科技送出位元給對方瀏覽器當作夾檔直接跳出下載！
    except Exception as err_dl:  # 無論檔案太胖或是 I/O 突然拉閘中斷
        dict_err_dl = {'error': str(err_dl)}  # 字典變數，紀錄並收編這起事件原始文字為己助
        return jsonify(dict_err_dl), 500  # 送交開發者去分析原因的 HTTP 500 給前端交代

@flask_app.route('/api/config', methods=['GET'])  # 最後是這個為了解說全站能耐而開啟的心臟檢查指南路由
def get_config():  # 肩負說明全系統各種奇門遁甲支援度到底到了哪一個梯次任務的主函式
    """Get API configuration"""
    dict_sys_config = {  # 字典變數，一次性把本質與各個維度常數列成樹狀表
        'supported_formats': list(set_allowed_extensions),  # 從全域那兒將允許之檔案陣列取出攤在陽光下
        'supported_question_types': ['true_false', 'single_choice', 'multiple_choice', 'fill_in_blank', 'essay'],  # 當前最新五大天王出題類別一覽
        'supported_difficulties': ['easy', 'medium', 'hard'],  # 這三個難度的門檻就是給 UI 去做成按鈕介面使用的
        'supported_languages': ['zh-TW', 'en-US'],  # 支援系統所懂得撰寫的兩類大主流語系
        'version': '1.0.0'  # 這是這顆後台正在跑的核心主版號標誌
    }
    return jsonify(dict_sys_config)  # 打包成清爽的 JSON 型態拋出給對此系統好奇的前端套件

if __name__ == '__main__':  # 如果啟動的引線並非藉助正規伺服環境，而是我們自己在電腦測試運行
    flask_app.run(debug=True, host='0.0.0.0', port=8000)  # 將 Flask 切換至不眠不休的除錯型態隨時發送更新並廣播佔據 TCP 8000 埠道