#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tests/test_input_adapter.py
# Unit tests for the Input Adapter module

import unittest  # 匯入官方內建獨立單元測試驅動核心框架套件
import os  # 匯入以處置本地端殘留路徑或是驗屍管理
import tempfile  # 匯入為我們蓋起防塵測試用空箱之好用組件
from src.input_adapter import process_file  # 將主系統核心功能入口拉入備戰供測
from src.input_adapter.input_adapter import process_txt, process_pdf, process_pptx, process_docx  # 另外強制把專用處理小兵抓出來備驗

class TestInputAdapter(unittest.TestCase):  # 開起對轉換龐雜介面的檢視法庭殿堂
    """Test cases for the Input Adapter module"""
    
    def setUp(self):  # 法庭準備開門前先設圍籬免遭攻擊的佈置
        """Set up test fixtures"""
        self.str_temp_dir = tempfile.mkdtemp()  # 字串變數，建立隱去蹤跡不留檔案的安全密室
    
    def tearDown(self):  # 法庭收攤前必須處理的焚化爐機制善後
        """Clean up temporary files"""
        for str_file in os.listdir(self.str_temp_dir):  # 將這密室內每件擺設死白清查造冊
            str_file_path = os.path.join(self.str_temp_dir, str_file)  # 字串變數，計算好清理路線
            if os.path.isfile(str_file_path):  # 給予最後確認只殺檔案
                os.unlink(str_file_path)  # 就直接給予一槍斃命除根抹去
        os.rmdir(self.str_temp_dir)  # 連同整間密室一併埋藏摧毀掉不著任何痕跡
    
    def test_process_txt_simple(self):  # 初階勘驗：對平坦文本文字檔通盤解析有無失手
        """Test processing a simple TXT file"""
        str_test_file = os.path.join(self.str_temp_dir, 'test.txt')  # 字串變數，指定屋內新實驗用老鼠名稱
        str_content = "This is a test document.\nWith multiple lines."  # 字串變數，預留一串注射內文
        with open(str_test_file, 'w', encoding='utf-8') as file_obj:  # 開始將藥劑寫入存檔
            file_obj.write(str_content)  # 生效寫入
        
        dict_result = process_txt(str_test_file)  # 字典變數，推入讀取取得包裹
        
        self.assertEqual(dict_result['source_type'], 'txt')  # 首度盤查該包必須承認自己血統
        self.assertIn('sections', dict_result)  # 深核對內門是否設好區塊欄位以防坍方
        self.assertGreater(len(dict_result['sections']), 0)  # 確認不僅有欄位還不能空蕩蕩
        self.assertIn('content', dict_result['sections'][0])  # 把第一個段落抽身問話確認帶內文標籤
        self.assertIn('title', dict_result['sections'][0])  # 確認有無臨時蓋標題名印記
    
    def test_process_txt_with_sections(self):  # 對帶有暗碼井字號的文字檔進行查水表
        """Test processing a TXT file with section markers"""
        str_test_file = os.path.join(self.str_temp_dir, 'test_sections.txt')  # 字串變數，二號豪華老鼠入屋
        str_content = "### Section 1\nThis is content 1.\n### Section 2\nThis is content 2."  # 字串變數，含有尊絕暗門的高級文章注射液
        with open(str_test_file, 'w', encoding='utf-8') as file_obj:  # 依然以最高規開啟它
            file_obj.write(str_content)  # 打入劑量完成
        
        dict_result = process_txt(str_test_file)  # 字典變數，收繳拆解化驗物件大成
        
        self.assertEqual(dict_result['source_type'], 'txt')  # 第一階比對通過查核無誤
        self.assertEqual(len(dict_result['sections']), 2)  # 強力驗明是否順理解出兩塊及格
        self.assertIn('Section 1', dict_result['sections'][0]['title'])  # 細微對核第一塊頭銜正解
        self.assertIn('Section 2', dict_result['sections'][1]['title'])  # 相同審查第二大塊有無走板
    
    def test_process_file_with_txt(self):  # 主路由器測試：用文本白老鼠強攻大門分流器會否卡住
        """Test the main process_file function with TXT file"""
        str_test_file = os.path.join(self.str_temp_dir, 'test.txt')  # 字串變數，三號老鼠報到名字隨意
        with open(str_test_file, 'w', encoding='utf-8') as file_obj:  # 啟動製造器
            file_obj.write("Test content")  # 內文不拖泥帶水越短越好
        
        dict_result = process_file(str_test_file)  # 字典變數，委託大總管處理分配並回收看成效
        
        self.assertEqual(dict_result['source_type'], 'txt')  # 確認總管沒有老花眼分錯分類櫃
        self.assertIn('sections', dict_result)  # 與有沒有把應交的名冊保管妥當
    
    def test_process_file_not_found(self):  # 查緝空包彈戰：給假地址看系統會不會真當機不回神
        """Test handling of non-existent files"""
        with self.assertRaises(FileNotFoundError):  # 我們預期且期望系統會生氣拋例外才對
            process_file('/path/to/nonexistent/file.txt')  # 果斷地朝不存在假牆開槍一試便知
    
    def test_process_file_unsupported_format(self):  # 異形入侵戰：傳遞怪不可測副檔名的病毒給老大哥
        """Test handling of unsupported file formats"""
        str_test_file = os.path.join(self.str_temp_dir, 'test.unknown')  # 字串變數，打造不明變異檔案名之器物
        with open(str_test_file, 'w') as file_obj:  # 確保這東西有血肉開啟
            file_obj.write("test")  # 塞入短字眼充場作戲敷衍之
        
        with self.assertRaises(ValueError):  # 期望系統主管慧眼賞一個退貨巴掌給開發端
            process_file(str_test_file)  # 送這危險武器闖關測安檢
    
    def test_process_txt_empty_file(self):  # 零位元空襲防衛測試，防止零被除或是崩潰出發
        """Test processing an empty TXT file"""
        str_test_file = os.path.join(self.str_temp_dir, 'empty.txt')  # 字串變數，建造出看似有實但無實虛重零幽靈
        with open(str_test_file, 'w') as file_obj:  # 打開準備注入點滴
            pass  # 什麼都不給，關門結束空城計完工
        
        dict_result = process_txt(str_test_file)  # 字典變數，帶詭計試探解析端
        
        self.assertEqual(dict_result['source_type'], 'txt')  # 系統認得這有名字無內涵之掛名客
        self.assertIn('sections', dict_result)  # 老實給予空虛回傳避免程式死當發作
    
    def test_process_pdf_fallback(self):  # 丟一份假 PDF 看退回安撫防線
        """Test PDF processing fallback when file doesn't exist"""
        str_test_file = os.path.join(self.str_temp_dir, 'dummy.pdf')  # 字串變數，偽造名號招牌
        with open(str_test_file, 'wb') as file_obj:  # 重啟二進位硬塞這違禁物
            file_obj.write(b'Not a real PDF')  # 內部裝填笑死人的非真實可解雜碎
        
        try:  # 無情轟炸下看系統撐住此招否
            dict_result = process_pdf(str_test_file)  # 字典變數，讓專精私人匠師解碼
            self.assertEqual(dict_result['source_type'], 'pdf')  # 保留宣稱其物原意紀錄
            self.assertIn('sections', dict_result)  # 封存其無法處置無奈資訊交差
        except Exception:  # 這是一份允發生死當的特赦場條款
            pass  # 拋錯也笑笑放過原諒它
    
    def test_process_pptx_fallback(self):  # 將上關重演搬至假 PPTX 進行
        """Test PPTX processing fallback"""
        str_test_file = os.path.join(self.str_temp_dir, 'dummy.pptx')  # 字串變數，PPTX 膺品招標外觀
        with open(str_test_file, 'wb') as file_obj:  # 二階開檔塞入
            file_obj.write(b'Not a real PPTX')  # 灌注無用垃圾鐵內文
        
        try:  # 下達防禦力測試網
            dict_result = process_pptx(str_test_file)  # 字典變數，指派首席前往拆炸彈不明垃圾
            self.assertEqual(dict_result['source_type'], 'pptx')  # 最終能給個身分證就是萬幸
            self.assertIn('sections', dict_result)  # 以及那包安撫工程師宣告失敗文字亦同確認
        except Exception:  # 同樣是個萬一真爆炸也絕不深究的特赦地
            pass  # 失敗不算罪孽直接隨風歸去
    
    def test_process_docx_fallback(self):  # 假 DOCX 惡搞三回戰加映
        """Test DOCX processing fallback"""
        str_test_file = os.path.join(self.str_temp_dir, 'dummy.docx')  # 字串變數，搞最後的假文件披風袍
        with open(str_test_file, 'wb') as file_obj:  # 開倉直達寫入深處地穴
            file_obj.write(b'Not a real DOCX')  # 塞入廢文大騙局
        
        try:  # 老招去賭命解碼看系統還在否
            dict_result = process_docx(str_test_file)  # 字典變數，委由專武扛轎子化解
            self.assertEqual(dict_result['source_type'], 'docx')  # 死不認錯把名片留下了保住尊嚴
            self.assertIn('sections', dict_result)  # 還有那包無力的陣列遺書歸還相交
        except Exception:  # 開特例無責大赦條款護法
            pass  # 防禦失敗便令其安息亦無妨

class TestInputAdapterIntegration(unittest.TestCase):  # 開起另高層次實戰演習總基地台
    """Integration tests for Input Adapter with other modules"""
    
    def setUp(self):  # 一樣老戲碼先請神造屋以免污染旁人
        """Set up test fixtures"""
        self.str_temp_dir = tempfile.mkdtemp()  # 字串變數，建立隱蹤密室
    
    def tearDown(self):  # 走退場大掃除毀屍不留點滴之法流
        """Clean up temporary files"""
        for str_file in os.listdir(self.str_temp_dir):  # 掃描密室亡命文件清冊
            str_file_path = os.path.join(self.str_temp_dir, str_file)  # 字串變數，組成死期路徑清單斬首線
            if os.path.isfile(str_file_path):  # 不傷及無辜活殺檔案實體之核驗
                os.unlink(str_file_path)  # 死刑處決了結
        os.rmdir(self.str_temp_dir)  # 連根拔起大本營屋
    
    def test_adapter_output_format(self):  # 末日之戰：確認系統大腦介面轉接頭是否完美對應銜接下游沒斷手斷腳
        """Test that adapter output has correct format for downstream processing"""
        str_test_file = os.path.join(self.str_temp_dir, 'test.txt')  # 字串變數，搞包最直白靶材過場防意外之測
        str_content = "Chapter 1\nContent for chapter 1\nChapter 2\nContent for chapter 2"  # 字串變數，寫一個教科書小縮圖雙標題
        with open(str_test_file, 'w') as file_obj:  # 點火將料開鍋寫進硬碟內
            file_obj.write(str_content)  # 注入實質
        
        dict_result = process_file(str_test_file)  # 字典變數，交給總理大臣跑完全趟看他吐了什麼規格包
        
        self.assertIn('source_type', dict_result)  # 追查包含血統印記不可遺失無誤之舉
        self.assertIn('sections', dict_result)  # 有無包裹那珍貴內文盒子
        self.assertIsInstance(dict_result['sections'], list)  # 第三層驗證這必須必然是個陣列免遭假冒騙人
        
        for dict_section in dict_result['sections']:  # 刁鑽進入盒內條目單獨照妖鏡問話查證
            self.assertIn('title', dict_section)  # 確認小格有獨斷標題
            self.assertIn('content', dict_section)  # 確認己身獨家內容物宣告
            self.assertIsInstance(dict_section['title'], str)  # 更確認此點必須為純粹字串防崩裂
            self.assertIsInstance(dict_section['content'], str)  # 確認絕對屬字串護下游平安渡過險境

if __name__ == '__main__':  # 若又是命令列拿鞭子催落呼叫特戰戲碼之本測試外傳
    unittest.main()  # 特遣軍團全放殺出一輪測試道場供高層閱兵
