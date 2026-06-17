# canonical_content.py
# Canonical Content: Standardize content to chapter/learning objectives/paragraphs structure

from typing import Dict, List  # 匯入類別標記，寫程式時可增加 IDE 提示與閱讀性

def standardize_content(dict_intermediate_data: Dict) -> Dict:  # 接收來自各式轉譯器產生好的粗略字典，回傳精裝結構
    """Convert intermediate data to canonical content structure."""
    list_sections = dict_intermediate_data.get('sections', [])  # 陣列變數，取出粗略字典裡頭名為 sections 的清單資料
    str_source_type = dict_intermediate_data.get('source_type', 'unknown')  # 字串變數，保留該字典所聲稱傳遞過來的來源檔案類別

    dict_canonical = {  # 字典變數，我們系統最終極渴望看到的最美樹狀標準結構
        "source_type": str_source_type,  # 繼承記錄這份結構的血統
        "chapter": extract_chapter(list_sections),  # 呼叫萃取章節名之神功取出首要標題
        "learning_objectives": extract_learning_objectives(list_sections),  # 呼叫分析標題萃取學習目標之子函式
        "paragraphs": extract_paragraphs(list_sections)  # 呼叫大清洗邏輯濾網將純文字過濾洗出
    }

    return dict_canonical  # 將這顆過濾好的標準字典無私歸還

def extract_chapter(list_sections: List[Dict]) -> str:  # 定義專門從亂七八糟章節裡找出唯一主標題之工具函式
    """Extract main chapter title from sections"""
    if list_sections and 'title' in list_sections[0]:  # 若陣列內真有物件，且這首個小節具備稱之為 title 之屬性
        return list_sections[0].get('title', 'Default Chapter').strip()  # 拔得頭籌作為全場主標題，切去空白後回傳
    return 'Default Chapter'  # 否則給予老土的預設標題頂替

def extract_learning_objectives(list_sections: List[Dict]) -> List[str]:  # 根據通篇文章每階標題推導出「學習目標」的輔助函式
    """Extract learning objectives from content."""
    list_objectives = []  # 陣列變數，準備存放推敲出來之多條實用學習總結目標
    
    # Try to extract from section titles
    for dict_section in list_sections:  # 從粗解析出的文章分塊中一個個探索爬行
        str_title = dict_section.get('title', '').strip()  # 字串變數，提取這塊領地的當地標題名稱
        if str_title and str_title not in ['Introduction', 'Overview', 'Summary']:  # 如果標題存在且不是那類太寬泛的空泛贅字
            str_objective = f"Understand {str_title.lower()}"  # 字串變數，套用萬用公式「了解 XXXX」轉文法為目標
            if str_objective not in list_objectives:  # 若這句目標語法不曾被收錄防撞擊
                list_objectives.append(str_objective)  # 將其視同合理教學目標加進清單妥善保存
    
    # Default objectives if none found
    if not list_objectives:  # 若走過千山萬水全都是 Introduction 等詞墜
        list_objectives = [  # 陣列變數，強制生出兩個不論置於何處皆通的優雅目標充當牌面
            "Understand the main concepts",  # 了解中心主旨
            "Apply knowledge in practice"  # 實現理論於實務
        ]
    
    # Limit to 5 objectives
    return list_objectives[:5]  # 此生只取五瓢飲作為最高標上限以防系統爆版

def extract_paragraphs(list_sections: List[Dict]) -> List[str]:  # 負責把各處藏汙納垢的內文重新提取並平滑攤平之小幫手
    """Extract and normalize paragraphs from all sections."""
    list_paragraphs = []  # 陣列變數，準備蒐集那純粹又完美無缺的內文句集大成
    
    for dict_section in list_sections:  # 再次展開地毯式地網搜查
        str_content = dict_section.get('content', '').strip()  # 字串變數，把每小節的肉擠壓出來並除掉頭部空格毛刺
        if str_content:  # 只要確保這區塊真的擠得出文字血肉
            list_parts = str_content.split('\n\n')  # 陣列變數，利用兩次清脆空行折痕來辨識原作者的用心獨白段落
            for str_part in list_parts:  # 針對每一個被完美順切的獨立自然段來檢視
                str_part = str_part.strip()  # 字串變數，不忘幫這段子再洗刷掉邊緣殘存的虛空換行等孽障
                if str_part and len(str_part) > 10:  # （判別機制）唯有全字字數突破天靈蓋大於 10 才被承認為真經文
                    if str_part not in list_paragraphs:  # （查重機制）決絕避免兩段一模一樣如雙胞胎的刻意洗版
                        list_paragraphs.append(str_part)  # 加進我們至高無上的單一本源平直純淨句大典之中保留
    
    # If no substantial paragraphs found, create default ones
    if not list_paragraphs:  # 若是這堂教材通篇字數都連十個字都講不滿而導致這漁網空蕩蕩
        list_paragraphs = ['Default paragraph content']  # 給個假字詞避免接下來全盤演算死掉當交差
    
    return list_paragraphs  # 最後將這份血淚精華的純文字陣列奉還給系統主邏輯