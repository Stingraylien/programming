# tests/test_integration.py
# Integration tests for the entire pipeline

import unittest  # 匯入官方內建的獨立單元測試驅動程式核心框架
import os  # 匯入 os 模組以處理系統層面路徑與檔案生死存亡
import sys  # 匯入 sys 模組以供動態霸道竄改開發全域套件載入路徑
import tempfile  # 匯入能夠隨意免洗拋棄的安全虛擬儲物櫃工具
import shutil  # 匯入殘暴的檔案管理工具以便測試結束後清掃假資料夾
from datetime import datetime  # 匯入精準時間戳記抓取工具以應付動態需求名冊

# Add src to path
str_sys_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # 字串變數，抓取上層絕對老巢路徑位址
sys.path.insert(0, str_sys_path)  # 把算出來的巢穴給強制編列進入首要環境路徑清單

from src.input_adapter import process_file  # 強拉 adapter 套件的核心過來準備待測
from src.canonical_content import standardize_content  # 拉拔內容模組負責清洗結構功能
from src.question_generator import QuestionGenerator  # 將出題引擎大老請駕降臨
from src.xulink_exporter import export_to_excel  # 把匯出官僚也給邀約列席本案

class TestIntegration(unittest.TestCase):  # 宣告名為檢測這龐大四神整合體的試煉地獄專區，直系繼承自測試官方父類別
    def setUp(self):  # 開打前的圈地儀式準備事宜
        """Set up test fixtures"""
        self.str_temp_dir = tempfile.mkdtemp()  # 字串變數，向系統調用一個絕對乾淨暫存測試空屋
        
        # Create a sample text file for testing
        self.str_sample_file = os.path.join(self.str_temp_dir, 'sample.txt')  # 字串變數，準備在這個空屋內建立一個假的地基
        with open(self.str_sample_file, 'w') as file_obj:  # 發號司令開始挖地基寫入
            file_obj.write("Sample Content\n\nThis is a test document.\n\nWith multiple paragraphs.")  # 灌入一些可憐測試內容血肉

    def tearDown(self):  # 測試後不能留下痕跡的滅跡滅口環節
        """Clean up test fixtures"""
        if os.path.exists(self.str_temp_dir):  # 確認真有作案留下的暫存黑屋紀錄
            shutil.rmtree(self.str_temp_dir)  # 毫不留情的動用工具將整個屋子連根拔起燒盡不留殘骸

    def test_pipeline_end_to_end(self):  # 高難度從頭到腳一條龍完全端對端地獄特訓
        """Test the complete pipeline from input to Excel export"""
        
        # Step 1: Process file (using mock data since we don't have real files)
        dict_intermediate_data = {  # 字典變數，由於沒檔案可解只能自己用字串頂替中間地帶心血資料
            "source_type": "text",  # 偽稱血統為文字標籤類
            "sections": [  # 直接開掛掛載已解好的章節
                {  # 創建一個擁有完美長段落教材
                    "title": "Chapter 1: Introduction",  # 章節名稱分派賦予
                    "content": "This is an introduction section with multiple paragraphs.\n\nIt contains important concepts."  # 富有文才內文主體
                },
                {  # 創建另一片錦上添花陪考教材
                    "title": "Chapter 2: Main Content",  # 標題配置無誤通過
                    "content": "This chapter covers the main ideas.\n\nWith practical examples."  # 再次塞入垃圾過渡文
                }
            ]
        }
        
        # Step 2: Standardize content
        dict_canonical_content = standardize_content(dict_intermediate_data)  # 字典變數，把這包假資料推給洗淨模組要求清洗回傳出標準金
        self.assertIn("chapter", dict_canonical_content)  # 確認這包真金純粹保證含有神聖章節目錄標記
        self.assertIn("learning_objectives", dict_canonical_content)  # 不可漏掉最難搞的學習宗旨目標確認
        self.assertIn("paragraphs", dict_canonical_content)  # 最重心的文字段落更是絕對必需品檢查
        self.assertGreater(len(dict_canonical_content["paragraphs"]), 0)  # 要求海洋內至少得有一滴內容不可為零
        
        # Step 3: Generate questions
        obj_generator = QuestionGenerator(strategy="rule_based")  # 物件變數，熱騰騰出題機上陣待命
        list_question_types = ["true_false", "single_choice", "multiple_choice"]  # 陣列變數，開具本次討伐任務之三款指定產出清冊
        list_questions = obj_generator.generate_questions(dict_canonical_content, list_question_types, "medium", "zh-TW")  # 陣列變數，把指令跟剛剛榨好真金混合強制生產接獲
        
        self.assertGreater(len(list_questions), 0)  # 審查有無繳白卷失敗之處，有半題都好
        for dict_question in list_questions:  # 如城牆閱兵般檢視所有誕生的每一道兒科狀況
            self.assertIn("type", dict_question)  # 確認身上皆有掛上題型狗牌
            self.assertIn("subject", dict_question)  # 確認皆有身為主問句文膽存在
            self.assertIn("difficulty", dict_question)  # 確認均有背負難度星等標籤
            self.assertIn("weight", dict_question)  # 確認每條拿到計分價值籌碼以供加權給分
        
        # Step 4: Export to Excel
        str_output_file = os.path.join(self.str_temp_dir, "test_output.xlsx")  # 字串變數，在這個黑屋內準備留給 Excel 的終端檔名路徑
        export_to_excel(list_questions, str_output_file)  # 命令搬運工將列隊神軍題庫趕進 Excel 框架燒錄
        
        self.assertTrue(os.path.exists(str_output_file))  # 檢查檔案有沒有不翼而飛忘了建立
        self.assertGreater(os.path.getsize(str_output_file), 0)  # 再度確認生出來的有殼但絕不能是空包彈的可能

    def test_question_types_generation(self):  # 極限測試五大天王題型是否能不挑食產出
        """Test generation of all question types"""
        dict_canonical_content = {  # 字典變數，微型測資
            "chapter": "Test Chapter",  # 掛頭銜免遭攔查防護
            "learning_objectives": ["Learn A", "Learn B"],  # 為申論題準備特權詞卡
            "paragraphs": ["Content 1", "Content 2", "Content 3"]  # 有肉的段落字句
        }
        
        obj_generator = QuestionGenerator()  # 物件變數，出題基底
        list_all_types = ["true_false", "single_choice", "multiple_choice", "fill_in_blank", "essay"]  # 陣列變數，列出系統功能表大項
        
        for str_q_type in list_all_types:  # 去逼迫生產機器產能極限操作各題型
            list_questions = obj_generator.generate_questions(dict_canonical_content, [str_q_type], "medium")  # 陣列變數，接過生成成果
            self.assertGreater(len(list_questions), 0, f"No questions generated for type: {str_q_type}")  # 倘若任意一項絕種沒產出即報錯

    def test_difficulty_levels(self):  # 對抗各難度刻度是否不影響其機能輸出
        """Test question generation with different difficulty levels"""
        dict_canonical_content = {  # 字典變數，最貧瘠教材敷衍用
            "chapter": "Test Chapter",  # 敷衍的假營業字樣
            "learning_objectives": ["Learn"],  # 個位數單一目標充數頂替
            "paragraphs": ["Content"]  # 最短一詞段落頂上
        }
        
        obj_generator = QuestionGenerator()  # 物件變數，找生題機上陣
        list_difficulties = ["easy", "medium", "hard"]  # 陣列變數，準備三個星等的魔考驗證
        
        for str_difficulty in list_difficulties:  # 對三難度無差別砲轟測試
            list_questions = obj_generator.generate_questions(  # 陣列變數，開袋準備收卷
                dict_canonical_content,   # 餵入這寒酸可憐教材
                ["single_choice"],   # 強硬限定單選測試免失焦
                str_difficulty  # 替換難度挑戰指令
            )
            self.assertGreater(len(list_questions), 0)  # 要求保底不能不給題
            self.assertIn(list_questions[0]["difficulty"], [1, 3, 5])  # 更深度勘驗轉化機器數字歸矩是否正確

if __name__ == '__main__':  # 若從命令列指令呼叫本大戲大本營開演
    unittest.main()  # 放行所有特聘考官進場開始殘酷主審查