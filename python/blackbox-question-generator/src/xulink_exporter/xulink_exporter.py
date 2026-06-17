# xulink_exporter.py
# XuLink Exporter: Export questions to XuLink Excel format

import pandas as pd  # 匯入超強力資料表與 Excel 處置霸主模組
from typing import List, Dict  # 匯入靜態型別標籤符號功能以便我們開發編修更有紀律

def export_to_excel(list_questions: List[Dict], str_filename: str = "training_question_bank.xlsx"):  # 設計一個轉大表的巨型引擎函式
    """
    Export questions to XuLink compatible Excel format.
    Follows the format specified in test_rule.md
    """
    list_rows = []  # 陣列變數，開闢一個非常廣袤空地準備存放一行行要準備被燒入 Excel 內的資料列紀錄

    for dict_question in list_questions:  # 如同軍隊般開始逐一審問剛剛從產線產出的字典考題每一道
        # Add question header row
        dict_question_row = {  # 字典變數，為了遵照旭聯老舊格式必須首位建置獨享的一行霸權所謂題目標題列
            "#Qtype": dict_question.get("type", ""),  # 填入血統身份證明書 (例如單選或是非標籤)
            "Subject": dict_question.get("subject", ""),  # 正式把問題考幹文宣謄寫而上
            "Option": "",  # 首行題干本身絕不能夾雜沾染選項的文字故清白空格處理
            "Weight": dict_question.get("weight", 1),  # 本題的原始價值賦予與加權分數配置
            "Difficulty": dict_question.get("difficulty", 3),  # 將難關障礙等第評分轉交給這行紀錄
            "Answer": "",  # 第一列不能有解答洩露的嫌疑一樣保持封印空字串
            "Option Limit Type": dict_question.get("option_limit_type", 0),  # 設定對於該考題後續所施加之上限或下限神力模式編碼
            "Option Limit Count": dict_question.get("option_limit_count", 0),  # 定義受限總量是幾頭文字等之真真實數字
            "Analyze(for QBank)": dict_question.get("analyze", ""),  # 留下所謂背後真諦答案解析雖然我們多半無能給出白券
            "NoRandom(for QBank)": dict_question.get("no_random", 0)  # 填入指示平台是否不准亂序洗牌亂攪局防駭模式鎖
        }
        list_rows.append(dict_question_row)  # 將這華麗的第一列重磅加入大集合成為主將當急先鋒排場

        # Add option rows
        if "options" in dict_question:  # 要是這題真不是裝死申論題而是正派具有複數選項分支路口的迷宮時
            for int_i, str_option in enumerate(dict_question["options"]):  # 將迷宮分支一個個拔下來檢視並附上自動累進之排序數值
                bool_is_correct = False  # 布林變數，出門在外總先假設所有人都是錯的清白假定原理開場為否
                
                # Handle different answer formats
                if isinstance(dict_question.get("answer"), str):  # （如果給標準答案的人就用一個超直白單一無二純字串）
                    bool_is_correct = str_option == dict_question.get("answer")  # 把兩者貼鼻頭一對比，一樣就立刻冊封為對錯為否決無情面
                elif isinstance(dict_question.get("answer"), list):  # （如果給標準答案是採用更為機智的高規格包裝大陣列表態）
                    bool_is_correct = str_option in dict_question.get("answer", [])  # 啟動雷達掃瞄該選項名字名字是否有在這答案陣列裡投石問路有就有沒有就再見
                
                str_answer_mark = "y" if bool_is_correct else ""  # 字串變數，配合高冷舊系統僅認小寫 y 作為解答之識別印記，不對即刻一無所有空白處刑
                
                dict_option_row = {  # 字典變數，為這苦命小弟建置伴隨主將的一系列專屬隨從跟班列數資料
                    "#Qtype": "",  # 隨從小弟無權決定身分
                    "Subject": "",  # 已經講過的問題不可復刻重複
                    "Option": str_option,  # 只有在這個領域它能大聲宣告展示它的魅力價值內文存在
                    "Weight": "",  # 評比總權在首無關細微小卒
                    "Difficulty": "",  # 同上無權過問
                    "Answer": str_answer_mark,  # 小寫解答印記決定了你生死成敗標籤在此
                    "Option Limit Type": "",  # 無管轄權
                    "Option Limit Count": "",  # 無實權
                    "Analyze(for QBank)": "",  # 再也沒有解釋的可能通通歸於平靜空白
                    "NoRandom(for QBank)": ""  # 不得造訪此地
                }
                list_rows.append(dict_option_row)  # 將這群配角們也都全數收編進大行列內與主將匯流

    # Create DataFrame with correct column order
    df_excel = pd.DataFrame(list_rows, columns=[  # DataFrame變數，強勢呼叫熊貓神獸幫這龐大烏合之眾陣列鑄入表格中兼顧順序嚴格監工排列之
        "#Qtype", "Subject", "Option", "Weight", "Difficulty", "Answer",  # 上半段黃金比例名錄
        "Option Limit Type", "Option Limit Count", "Analyze(for QBank)", "NoRandom(for QBank)"  # 下半場萬年不變規矩必帶附表標頭名稱
    ])

    # Save to Excel
    df_excel.to_excel(str_filename, index=False, sheet_name='Questions')  # 命令這隻帶好隊伍的熊貓直接將資料生燙刻入到指定的那個巨大長名之檔案中不用帶多餘序號而且貼心附上 Questions 分頁名牌
    
    return str_filename  # 大功告成光榮將刻好的結果檔名牌送出外頭給予世界