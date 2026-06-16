# question_generator.py
# Question Generator: Generate questions from canonical content

from typing import Dict, List  # 匯入靜態型別標籤，以便維持開發紀律與提供編譯解析指引
from enum import Enum  # 匯入列舉型別基礎套件，以建立可靠之題型列舉清單
import random  # 匯入亂數生成模組，應允隨機出題等行為所須
import copy  # 匯入深層複製模組，用於在補題時避免字典物件共用同一份記憶體參照

class QuestionType(Enum):  # 定義列舉子類，規範全系統的正規題型標記集合
    TRUE_FALSE = "true_false"  # 是非題宣告
    SINGLE_CHOICE = "single_choice"  # 單選題宣告
    MULTIPLE_CHOICE = "multiple_choice"  # 多選題(複選)宣告
    FILL_IN_BLANK = "fill_in_blank"  # 填空題宣告
    ESSAY = "essay"  # 問答(簡答)題宣告

class QuestionGenerator:  # 宣告生題機主體藍圖
    def __init__(self, str_strategy: str = "rule_based"):  # 初始化器，給定策略字串並寫死預設為基於規則的寫死式出題
        """Initialize question generator."""
        self.str_strategy = str_strategy  # 將指定進來的出題手段長駐儲存為本身屬性

    def generate_questions(self, dict_canonical_content: Dict, list_question_types: List[str],  # 定義接收嚴格型別的主力函數
                          str_difficulty: str = "medium", str_language: str = "zh-TW") -> List[Dict]:  # 決定語言難度參數，誓言回傳問題大禮包矩陣
        """Generate questions based on canonical content."""
        list_questions = []  # 陣列變數，開出一個嶄新的空白提袋，準備填入等會要生成的熱騰騰習題
        int_difficulty_level = self._convert_difficulty(str_difficulty)  # 整數變數，透過隱私函式將粗淺的文字難度轉為 1~5 數字星等

        for str_q_type in list_question_types:  # 以迴圈橫掃需求清單內的每個期盼題型名稱
            if str_q_type == QuestionType.TRUE_FALSE.value:  # 如果是希望出是非題
                list_questions.extend(self._generate_true_false(dict_canonical_content, int_difficulty_level))  # 將生成的是非陣列接骨納入大袋子中
            elif str_q_type == QuestionType.SINGLE_CHOICE.value:  # 要是單選題願景成真
                list_questions.extend(self._generate_single_choice(dict_canonical_content, int_difficulty_level))  # 吐單選陣列進大袋
            elif str_q_type == QuestionType.MULTIPLE_CHOICE.value:  # 碰到大魔王複選題考官時
                list_questions.extend(self._generate_multiple_choice(dict_canonical_content, int_difficulty_level))  # 推入複選題目集結體
            elif str_q_type == QuestionType.FILL_IN_BLANK.value:  # 接獲填空指令命令
                list_questions.extend(self._generate_fill_in_blank(dict_canonical_content, int_difficulty_level))  # 填題到大本營陣列內
            elif str_q_type == QuestionType.ESSAY.value:  # 解析開放式問答申論
                list_questions.extend(self._generate_essay(dict_canonical_content, int_difficulty_level))  # 將生成出來的長篇大論入帳

        # 確保題數剛好 20 題 (為符合影片與 Excel 規範)
        while list_questions and len(list_questions) < 20:  # 迴圈保底機制：若總題數不足 20 題則持續複製補充
            dict_new_q = copy.deepcopy(random.choice(list_questions))  # 字典變數，從現有題庫中隨機選一題並做深層複製，避免原始物件被汙染
            list_questions.append(dict_new_q)  # 將複製出的新題字典追加至總題庫清單尾端
            
        if list_questions and len(list_questions) > 20:
            list_questions = list_questions[:20]

        return list_questions  # 滿載而歸的拋出所有集結完畢的字典匯總清單

    def _convert_difficulty(self, str_difficulty_str: str) -> int:  # 將通俗人類話語化為精密機器數字評等之內部函式
        """Convert difficulty string to 1-5 scale"""
        dict_mapping = {  # 字典變數，打造一個強制的難度字典映射轉換對照表
            'easy': 1,  # 凡稱為簡單皆作 一
            'medium': 3,  # 其貌不揚中等則歸 三
            'hard': 5  # 高峰險阻困難方給 五
        }
        return dict_mapping.get(str_difficulty_str, 3)  # 送出查表成績；若詞句有不對盤瞎扯一通，預設賞你個三當做沒事

    def _generate_true_false(self, dict_content: Dict, int_difficulty: int) -> List[Dict]:  # 私有是非題黑手套工廠上線
        """Generate true/false questions"""
        list_questions = []  # 陣列變數，私領域用的暫存陣列用以擺放是非題
        
        list_paragraphs = dict_content.get('paragraphs', [])  # 陣列變數，調用出內容字典中所含括之本源文字段落群
        int_num_questions = max(1, len(list_paragraphs) // 3)  # 整數變數，推估合適出題量：以每三段出一題的節奏與最少保底一題交互取最高
        
        for int_i in range(min(int_num_questions, 3)):  # 取推估題數與強硬上限 3 題之較低者跑數次迴圈
            if int_i < len(list_paragraphs):  # 安全鎖防護，深怕超過我們手邊文字段落總長而空抓取
                list_questions.append({  # 打包此類特定形式並寫死格式推入其中
                    "type": "[TrueFalse]",  # 題目標記血脈
                    "subject": f"Sample true/false question {int_i+1}?",  # 題目標題本體，此採預設文字示範
                    "options": ["True", "False"],  # 僅僅為二選一的是非世界
                    "answer": "True" if int_i % 2 == 0 else "False",  # 依照計數之奇偶數輪替給予一個表定答案
                    "weight": 1,  # 系統賦予一題一份價值
                    "difficulty": int_difficulty,  # 從大函式遞延下來之難度係數
                    "no_random": 0,  # 設定允許變更前後隨機
                    "option_limit_type": 0,  # 取消所有極限鎖定
                    "option_limit_count": 0,  # 同上不受管控數量額度
                    "analyze": ""  # 不附帶什麼高深的註解說明書
                })
        
        return list_questions  # 成品歸隊

    def _generate_single_choice(self, dict_content: Dict, int_difficulty: int) -> List[Dict]:  # 第二產線打造單選霸主之道
        """Generate single choice questions"""
        list_questions = []  # 陣列變數，建立單選獨享專區口袋
        
        list_paragraphs = dict_content.get('paragraphs', [])  # 陣列變數，去金庫搬磚出來
        int_num_questions = max(1, len(list_paragraphs) // 3)  # 整數變數，還是每三段文字搾取出一道殘酷選擇題並且永遠有安慰獎一題
        
        for int_i in range(min(int_num_questions, 3)):  # 依然限定出產不能多過於三份單元避免通膨
            if int_i < len(list_paragraphs):  # 確認真材實料還有庫存能給文字當柴火燒
                list_questions.append({  # 落版入列排版好
                    "type": "[SingleChoice]",  # 將本源身分血統改向登記為單選制
                    "subject": f"Sample single choice question {int_i+1}?",  # 代稱標題依樣畫葫蘆
                    "options": ["Option A", "Option B", "Option C", "Option D"],  # 經典四大長青天王選項排排站
                    "answer": "Option A",  # 為了省事都教導為 A 永遠是對的選擇
                    "weight": 1,  # 單單只是給予配分1點底料
                    "difficulty": int_difficulty,  # 將該卷子難度承襲在此題上
                    "no_random": 0,  # 此處為完全開放選項排列可被平台打亂
                    "option_limit_type": 0,  # 沒有任何上下設限條款防護
                    "option_limit_count": 0,  # 設定連帶無作用數量額度
                    "analyze": ""  # 仍然是無情的不給詳解的老師
                })
        
        return list_questions  # 解甲歸田返回總站

    def _generate_multiple_choice(self, dict_content: Dict, int_difficulty: int) -> List[Dict]:  # 魔鬼般的複選試錯煉火房
        """Generate multiple choice questions"""
        list_questions = []  # 陣列變數，這才是痛苦的開始裝載體
        
        list_paragraphs = dict_content.get('paragraphs', [])  # 陣列變數，同樣取得本文根基
        int_num_questions = max(1, len(list_paragraphs) // 4)  # 整數變數，改為每四段精煉一題因為多選更耗腦力也同樣給保底一題的恩惠
        
        for int_i in range(min(int_num_questions, 2)):  # 更壓縮了上限僅給予珍稀的兩題量體空間
            if int_i < len(list_paragraphs):  # 確認還有料可出題不出空氣考卷
                list_questions.append({  # 入座寫題本單元
                    "type": "[MultipleChoice]",  # 表明複數多重宇宙身分認證
                    "subject": f"Sample multiple choice question {int_i+1}?",  # 以字面代替實力發問
                    "options": ["Option A", "Option B", "Option C", "Option D"],  # 亦是不變的四柱擎天陣型供客挑揀
                    "answer": ["Option A", "Option B"],  # 將答對門檻鎖死只承認有複數解答 AB 二人的存在
                    "weight": 2,  # 因挑戰較繁瑣難搞特別恩賜2分配分
                    "difficulty": int_difficulty,  # 星等承襲
                    "no_random": 0,  # 默許排序混亂自由意志
                    "option_limit_type": 0,  # 無視任何選項數量下達緊箍咒
                    "option_limit_count": 0,  # 本數自然也是連帶的虛無數字而已
                    "analyze": ""  # 不語破機關
                })
        
        return list_questions  # 完美回巢

    def _generate_fill_in_blank(self, dict_content: Dict, int_difficulty: int) -> List[Dict]:  # 記憶考驗型態的字宙製造工坊
        """Generate fill-in-the-blank questions"""
        list_questions = []  # 陣列變數，準備填滿空格
        
        list_paragraphs = dict_content.get('paragraphs', [])  # 陣列變數，文字基底不能少要來找動詞或關鍵字名詞挖空
        int_num_questions = max(1, len(list_paragraphs) // 5)  # 整數變數，這招很殘忍所以五十步換一次填空保底一次
        
        for int_i in range(min(int_num_questions, 2)):  # 控制至上兩題封板結束
            if int_i < len(list_paragraphs):  # 仍保證我們口袋字字珠璣且不會透支到超出範圍抓崩當系統
                list_questions.append({  # 來填入考點內容吧
                    "type": "[FillInBlank]",  # 正名格式保底確認
                    "subject": f"Please fill in the blank: ________ is important.",  # 創建經典老梗空白底線句型出考驗給同學
                    "options": [],  # 既然填空本來就不該讓你看見任何明珠選項存在
                    "answer": "Knowledge;Learning",  # 在此填入一二正確可被接納包容的兩種關鍵字答案作準繩
                    "weight": 1,  # 一格就是1分配息
                    "difficulty": int_difficulty,  # 星級掛保證連動
                    "no_random": 0,  # 空百自然沒有隨機排序這檔事可言
                    "option_limit_type": 0,  # 毫無受限此類條款之法力
                    "option_limit_count": 0,  # 一樣無用的陪襯物歸零膏
                    "analyze": ""  # 全憑同學冥想不會給提示
                })
        
        return list_questions  # 收工打下班卡啦

    def _generate_essay(self, dict_content: Dict, int_difficulty: int) -> List[Dict]:  # 最終靈魂拷問的審判之所製造機
        """Generate essay (short answer) questions"""
        list_questions = []  # 陣列變數，這個給文科申論題的專區已經備妥
        
        list_learning_objectives = dict_content.get('learning_objectives', ['Understand the content'])  # 陣列變數，特別改去萃取出課程先前提練好的無上大目標口號拿來考學生
        int_num_questions = max(1, len(list_learning_objectives) // 2)  # 整數變數，兩個目標就得寫成一題大申論題並同樣預防小雞腸肚一題不給之悲慘底線設定
        
        for int_i in range(min(int_num_questions, 2)):  # 超燒腦申論最多只派發兩題免得沒人受得了中傷逃避寫卷
            if int_i < len(list_learning_objectives):  # 若大目標詞句確確實實被我們系統掌握在手中且沒超出極限長度的話
                list_questions.append({  # 即將問答寫下千古留名的那一題吧
                    "type": "[Essay]",  # 專門識別長問答寫作的封印大鎖
                    "subject": f"Please explain: {list_learning_objectives[int_i] if int_i < len(list_learning_objectives) else 'the main concepts'}",  # 套用到精練出來的神之預備目標上頭加上 Please explain 這高高在上的問句逼迫交代
                    "options": [],  # 這又不是多選題不需要這玩意存在於視窗內障眼
                    "answer": "Refer to the course materials for a comprehensive answer.",  # 沒有人能給解答故而標準答案只是請授課老師當做參考評閱材料自行評斷生死
                    "weight": 3,  # 一分錢一分本這個價值連城故給三分之重不容忽視之比例
                    "difficulty": int_difficulty,  # 高低程度隨意調整如常隨俗
                    "no_random": 0,  # 不適用此等法則的隨意填寫值
                    "option_limit_type": 0,  # 同樣無法框列問答字數之無用此項常規欄位
                    "option_limit_count": 0,  # 直接躺下歸零結算之
                    "analyze": ""  # 不教人如何回答全憑實戰能力定江山
                })
        
        return list_questions  # 寫完最後一首詩篇正式結束這場出題的盛宴之旅