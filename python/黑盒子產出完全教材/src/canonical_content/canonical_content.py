from typing import Dict, List  # 匯入類別標記，在靜態分析與開發階段提供自動補全與型式檢查支援

def standardize_content(dict_intermediate_data: Dict) -> Dict:  # 定義標準化教材內容的主函式，將原始結構轉換為系統預期的精準結構
    """Convert intermediate data to canonical content structure."""  # 函式說明文件字串，描述此功能為將中間格式資料標準化
    list_sections = dict_intermediate_data.get('sections', [])  # 陣列型字典變數，從來源資料中提取各個被初步切割的小節集合
    str_source_type = dict_intermediate_data.get('source_type', 'unknown')  # 字串變數，保留該份資料的原始檔案來源格式標記（如 pdf, docx 等）

    dict_canonical = {  # 字典型變數，宣告最終要產出給後續生成器使用的核心標準教材內容物件
        "source_type": str_source_type,  # 將原始來源標記繼承至標準化結構中以利追溯
        "chapter": extract_chapter(list_sections),  # 調用子函式萃取出該堂課的主題章節標題名稱
        "learning_objectives": extract_learning_objectives(list_sections),  # 調用子函式分析所有小節標題並歸納出五項核心學習目標
        "paragraphs": extract_paragraphs(list_sections)  # 調用子函式清洗所有內文並過濾掉重複或過短的無效段落
    }  # 結束標準化內容物件的字典定義

    return dict_canonical  # 將這份整理得井然有序的標準化內容字典物件回傳給呼叫端

def extract_chapter(list_sections: List[Dict]) -> str:  # 定義專門從亂序小節中擷取主標題名稱的工具函式
    """Extract main chapter title from sections"""  # 函式說明，註明此功能為提取課程對應的章節主標題
    if list_sections and 'title' in list_sections[0]:  # 邏輯判斷，確認小節清單不為空且首個小節具備標題屬性
        return list_sections[0].get('title', 'Default Chapter').strip()  # 取出首個標題作為主章節名並清除前後贅餘空格後回傳
    return 'Default Chapter'  # 萬一連首個標題都沒有則給予一個固定的預設章節替代文字

def extract_learning_objectives(list_sections: List[Dict]) -> List[str]:  # 定義負責歸納分析所有小節標題並生成學習目標的函式
    """Extract learning objectives from content."""  # 函式說明，指出此處負責從內容中歸類提取學習任務目標
    list_objectives = []  # 陣列字串變數，初始化一個空清單好來存放接下來生成的各項教學重點目標
    
    # Try to extract from section titles...
    for dict_section in list_sections:  # 字典變數迴圈，逐一檢視教材中的每一個切割小節區塊
        str_title = dict_section.get('title', '').strip()  # 字串變數，提取該小節的標題並對其進行去空格處理
        if str_title and str_title not in ['Introduction', 'Overview', 'Summary']:  # 若標題非空且不是通用的導論或總結等無意義字詞
            str_objective = f"Understand {str_title.lower()}"  # 字串型語句變數，利用套版公式「了解 XXX」將標題轉譯為學習目標
            if str_objective not in list_objectives:  # 為確保產出不重複之目標清單進行內容檢查
                list_objectives.append(str_objective)  # 將這條新穎的學習目標語句正式加入目標成果清單中
    
    # Default objectives if none found...
    if not list_objectives:  # 布林檢查，萬一整份教材都提取不出可用標題來產製目標
        list_objectives = [  # 重新賦予清單初值，手動加入兩個放諸四海皆準的通用型學習目標作為備案
            "Understand the main concepts",  # 第一項通用目標：理解核心基本概念
            "Apply knowledge in practice"  # 第二項通用目標：將所學知識應用於實際場域
        ]  # 結束清單重新定義
    
    # Limit to 5 objectives...
    return list_objectives[:5]  # 取出前五項最重要的學習目標回傳，避免數量過多導致後續簡報排版炸裂

def extract_paragraphs(list_sections: List[Dict]) -> List[str]:  # 定義負責統合所有小節內文並將其清洗成乾淨段落清單的函式
    """Extract and normalize paragraphs from all sections."""  # 函式說明，註記此處在執行段落的提取與正規化清洗作業
    list_paragraphs = []  # 陣列字串變數，宣告一個容器用來盛裝最終篩選出的純淨自然段落
    
    for dict_section in list_sections:  # 又是一次地毯式的搜索，遍歷所有小節原始資料
        str_content = dict_section.get('content', '').strip()  # 字串變數，從字典中挖掘內文並移除前後無意義的空白字元
        if str_content:  # 邏輯判斷，只有當該節內含真實文字內容時才值得進一步處理
            list_parts = str_content.split('\n\n')  # 陣列字串變數，透過雙換行符號切割出原作者的原始自然段落結構
            for str_part in list_parts:  # 字串變數迴圈，深入檢視每一個切割下來的段落碎塊
                str_part = str_part.strip()  # 再次精細去污，確保段落內部沒有多餘的邊緣空白
                if str_part and len(str_part) > 10:  # 嚴格審查機制：內容非空且長度需大於 10 字才被標識為有價值的資訊段
                    if str_part not in list_paragraphs:  # 排除重複檢查，避免在最後的教材中出現一模一樣的冗餘資訊
                        list_paragraphs.append(str_part)  # 通過重重關卡考驗，正式將高品質段落加入最終資料庫
    
    # If no substantial paragraphs found, create default ones...
    if not list_paragraphs:  # 布林檢查，萬一教材內容真的空空如也连一段話都湊不齊
        list_paragraphs = ['Default paragraph content']  # 給予一條預設內容佔位，防止後續模組因讀取到空陣列而崩潰
    
    return list_paragraphs  # 最後將這份血淚精華的純文字陣列奉還給系統主邏輯