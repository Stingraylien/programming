# test_question_generator.py
# Basic tests for question generator

import unittest  # 匯入官方內建的獨立單元測試驅動程式核心強效框架
from src.question_generator.question_generator import QuestionGenerator  # 將我們精心設計打造出來的造題機器引擎實例給請過來這塊無人的演武場

class TestQuestionGenerator(unittest.TestCase):  # 宣告名為檢測這龐大出題機器的戰鬥專場空間，直系繼承自測試官方父類別
    def setUp(self):  # 我們每場微型小戰役鳴槍開打前，必須確保就位的鋪草皮儀式暖身動作
        self.obj_generator = QuestionGenerator()  # 物件變數，穩固安放一台我們自己的出廠全新未遭破壞出題機器好讓接下來可以狂操猛測試火
        self.dict_sample_content = {  # 字典變數，捏一包用來餵飽這台機器專用且絕對沒有問題純淨的極營養原物料模組供其無虞消耗
            "chapter": "Test Chapter",  # 我們餵出了這篇小文的第一個虛擬章節名稱
            "learning_objectives": ["Learn basics"],  # 設計了一句單薄卻足以塞牙縫用充場面的教條標語
            "paragraphs": ["This is a test paragraph."]  # 切下一塊雖然單薄卻為有效的一句測試精煉文字當熬湯底料去煮
        }

    def test_generate_true_false(self):  # 第一場測試對抗戰役主軸：考驗它是否能夠不當機的平滑順利吐出成形的是非題成果
        list_questions = self.obj_generator._generate_true_false(self.dict_sample_content, 3)  # 陣列變數，野蠻粗魯的硬去呼叫受保護的私房出題函式測試以端詳看他的反應與成品出水是否純粹
        self.assertEqual(len(list_questions), 1)  # 裁判無情面宣判，剛才我們所丟擲進去之草根底料，即便微不足道也非得給我擠壓出保底一題以證此機器並無死機壞軌才算通關
        self.assertEqual(list_questions[0]["type"], "[TrueFalse]")  # 身分二次驗明正身：鐵腕抽驗這該機器出品之唯一成品上，是否有如期蓋上代表著這是非題專屬血統的浮水印記合格審驗章

    def test_generate_single_choice(self):  # 開啟這場毫無留情的第二場突襲對決：直接考驗能否平安挺過單選題出題任務順利無傷下莊
        list_questions = self.obj_generator._generate_single_choice(self.dict_sample_content, 3)  # 陣列變數，下達上級司令命令強迫該破銅爛鐵機器動用私章強制逼出生出帶有單選手腳選項附庸的正規試卷檔案
        self.assertEqual(len(list_questions), 1)  # 同第一役般慘絕寰宇地檢查它是否真連一題這種保底產能基本盤產量都做不到而無端中箭卡線報錯墜落崩壞否
        self.assertEqual(list_questions[0]["type"], "[SingleChoice]")  # 還須親自確認它並沒有用其他黑魔法來魚目混珠把理應是單選題的身份符碼偷偷狸貓換太子蓋成其他光怪陸離阿哩不達的記號偽裝過盤

if __name__ == '__main__':  # 身為系統終點，當如果有位沒耐心的工程師嫌麻煩直接從無情命令列視窗直接下達命令拿鞭子抽打呼叫我們這部劇碼程式時
    unittest.main()  # 那就不再溫良恭儉讓地，全額通吃直接把上述所條列好的那堆機關槍項目一股腦兒全數釋放點燃瘋狂大清倉跑過一遍展示給觀眾看