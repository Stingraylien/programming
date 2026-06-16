# examples/api_usage_example.py
# Usage examples for the Black Box API

import requests  # 匯入以發起網路連線與操作請求封包的強勢函式庫
import json  # 匯入用以將辭典資料互相轉換為網頁通訊相容格式的幫手模組

str_base_url = "http://localhost:8000"  # 字串變數，固定寫入指向本地測試的根結點系統網址口

# Example 1: Check API Health
print("1. Health Check")  # 單純列印操作情境一之活動名稱作為大標誌
response_health = requests.get(f"{str_base_url}/api/health")  # 回應物件變數，測試主機存活脈動心跳是否正常
print(json.dumps(response_health.json(), indent=2))  # 以精美的雙空格縮排打印此心跳資料全貌
print()  # 美觀之用的空行跳躍

# Example 2: Get API Configuration
print("2. Get Configuration")  # 昭告讀者這即將是第二個測試場景演練介紹
response_config = requests.get(f"{str_base_url}/api/config")  # 回應物件變數，拿取目前伺服後台所宣稱的能力列表
dict_config = response_config.json()  # 字典變數，接住轉為 Python 本土物件結構後的資料陣列總匯包
print(f"Supported Question Types: {dict_config['supported_question_types']}")  # 秀出其能夠對付的所有題型版型支援清單
print(f"Supported Difficulties: {dict_config['supported_difficulties']}")  # 展示支援之三段門檻難度模式開關
print()  # 安插喘息留白區塊

# Example 3: Generate Question Bank (Basic)
print("3. Generate Question Bank")  # 強力主打的最強生成題庫全套功能公開檢測
with open('sample_material.txt', 'w') as file_obj:  # 本地端自己先捏造一個假客戶上傳目標文本檔案供稍後練兵防範未然
    file_obj.write("""
    # Chapter 1: Fundamentals
    
    Learning the basics of programming.
    
    Variables and data types are key concepts.
    Functions help organize code.
    
    # Chapter 2: Advanced Topics
    
    Exploring more complex programming patterns.
    
    Object-oriented programming provides structure.
    """)  # 寫入簡單卻實用具備含金量可供生題截取分析的測資訓練篇章

dict_files = {'materials': open('sample_material.txt', 'rb')}  # 字典變數，正式將這份測資以二進位綁架上車準備通關大挑戰
dict_data = {  # 字典變數，撰寫附表單用以夾帶的客製化命令指示規格要求
    'question_types': ['true_false', 'single_choice', 'multiple_choice'],  # 全面指定這卷宗必須涵蓋之三大量級題型要求指令
    'difficulty': 'medium',  # 一如既往的取中庸之道設定中等門檻
    'language': 'zh-TW',  # 語種之選擇此處情歸我國本土用語
    'output_format': 'xulink_excel'  # 霸氣指定大魔王旭聯專用的相容匯流排產出規格
}

response_post = requests.post(  # 回應物件變數，將所有陣列武裝送入 API 巨獸堡壘深處等候過關宣判
    f"{str_base_url}/api/generate-question-bank",  # 目標要地路由名稱
    files=dict_files,  # 第一隊為檔案敢死聯隊
    data=dict_data  # 第二隊為附加上膛的彈藥補給指令車
)

dict_result = response_post.json()  # 字典變數，解析回傳下來的戰車系統內部黑盒子精煉報告書
if response_post.status_code == 200:  # 倘若伺服器判讀說一切圓滿無病無災大收場之姿
    print(f"✓ Success!")  # 大字加印出這光榮回傳捷報告慰標語
    print(f"  - Questions Generated: {dict_result['questions_count']}")  # 向世界宣告成功製造提煉出的題數果實
    print(f"  - Output File: {dict_result['output_file']}")  # 印出那個被妥善命名存放的超長不重複產出檔案名稱
    print(f"  - Download URL: {dict_result['download_url']}")  # 回報其供我們能遠端點選奪取的提取檔案之超連結
else:  # 若是不幸陣亡報廢惹得系統異常崩盤勃然大怒時
    print(f"✗ Error: {dict_result.get('error', 'Unknown error')}")  # 將後端痛罵前台的原句血淋淋轉錄印出絕不再修飾圓場

print()  # 安插舒緩空行避免字距壓迫

# Example 4: Download Generated File
print("4. Download Generated Excel")  # 主題風格切換準備示範如何帶走下載戰利品檔案
if response_post.status_code == 200:  # 只有在前綴關卡已順利拿到實體提貨單號的鐵證大前提下
    str_download_url = dict_result['download_url']  # 字串變數，直接抽出該取貨單據上的存取專用目標密碼路由
    response_dl = requests.get(f"{str_base_url}{str_download_url}")  # 回應物件變數，向該門牌大舉進發想要討回熱騰騰的報告檔案
    
    if response_dl.status_code == 200:  # 伺服器果真守約定放出了未遭隱藏的寶物檔案通關綠燈
        with open(f"downloads/{dict_result['output_file']}", 'wb') as file_out:  # 開啟一個我方電腦安全屋內能寫入大量位元組的目的地金庫槽位
            file_out.write(response_dl.content)  # 將網路路上攔截到的無邊際本體資料大方傾瀉寫進木桶槽內並封印緊密
        print(f"✓ File downloaded: {dict_result['output_file']}")  # 印出安全順利下莊且進入倉庫入檔的字樣安人心
    else:  # 若伺服器因太勞累跳票毀約造成這條鏈結死亡檔案遺失
        print("✗ Download failed")  # 掛上白旗張貼下載大當機之訃聞悲報

print()  # 讓螢幕冷靜幾秒的區隔空行線

# Example 5: Generate with Multiple Files
print("5. Generate with Multiple Materials")  # 最高難度的合體多人大絕招即將示範盛大上線

# Create sample files
list_files_to_upload = []  # 陣列變數，開口張網以靜候迎接本回一起組隊前來送審的各路好漢英才匯集榜單
for int_i in range(2):  # 不囉縮先空手捏取兩位好兄弟來準備當犧牲品測試組
    str_fname = f'material_{int_i}.txt'  # 字串變數，為這些兄弟起好個別代表名字印記
    with open(str_fname, 'w') as file_part:  # 將兄弟檔憑空開鑿化作肉身出來
        file_part.write(f"Material {int_i+1}\n\nContent of material {int_i+1}.\n\nWith multiple paragraphs.")  # 朝兄弟肉身注入迷魂湯內容
    list_files_to_upload.append(str_fname)  # 將生面孔好兄弟招募收編進去成為預備敢死小隊隊列陣線

list_files = [('materials', open(str_f, 'rb')) for str_f in list_files_to_upload]  # 複雜陣列物件變數，大筆一揮用高階語法將清單全部兵變成讀取中之實體備戰狀態集結
dict_multi_data = {  # 字典變數，純粹為配合敢死部隊而生之血淋要求指令合約清冊
    'question_types': ['single_choice'],  # 限定唯一考這類最簡單粗暴之選擇款式
    'difficulty': 'hard',  # 下達指派那非人哉的最頂修羅道難度標準挑戰受試者極限
    'language': 'en-US'  # 而且特別不准說中文要求全面通盤轉換洋人英語輸出規格
}

response_multi = requests.post(  # 回應物件變數，號令全軍開始作戰直搗黃龍深入去挑戰無涯的伺服後台主城
    f"{str_base_url}/api/generate-question-bank",  # 目標依舊是屹立不搖的通關大門口正中央
    files=list_files,  # 第一波丟過去陣列包裝敢死隊所有二進位成員檔案身軀
    data=dict_multi_data  # 賦予修羅模式表單魔鬼難度指令同盟附帶前鋒開路去
)

dict_multi_result = response_multi.json()  # 字典變數，雙手捧著準備接起這包血汗歷劫打仗歸來後換來的終極戰報封包
print(json.dumps(dict_multi_result, indent=2))  # 以最端莊漂亮的姿勢大解讀張貼本張大規模戰役的報告成果大字報

# Clean up
import os  # 再度核對確保手頭緊握那大殺四方的刪檔案無敵權杖寶具可用
for str_f in list_files_to_upload:  # 當無情之人跑一趟敢死兄弟的報廢花名冊簿列
    os.remove(str_f)  # 一鍵清零地把他們遺腹留下的檔案全數抹煞掩埋歸為塵土絕不留下一丁點後患垃圾

print("\n✓ Examples completed!")  # 堂堂為演武腳本最終壓軸作收尾秀上圓滿順利的華麗宣告字眼