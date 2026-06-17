import sys                                                                      # 引入系統模組，用於處理命令列參數
import threading                                                                # 引入多執行緒模組，避免介面卡頓
from pathlib import Path                                                        # 引入 Path 模組，用於物件導向式的路徑操作
import pymupdf4llm                                                              # 引入 PDF 轉 Markdown 的核心套件
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,          # 引入 PySide6 所需的視窗與元件模組
                               QTextEdit, QVBoxLayout, QHBoxLayout, QWidget,    # 引入排版與文字區域模組
                               QFileDialog, QMessageBox, QLabel, QProgressBar)  # 引入對話框與進度條模組
from PySide6.QtCore import Signal, QObject                                      # 引入信號與物件模組，用於跨執行緒通訊

class WorkerSignals(QObject):                                                   # 建立一個負責跨執行緒溝通的信號類別
    signal_str_log_msg = Signal(str)                                            # 定義一個發送字串的信號，用於傳遞日誌訊息
    signal_tuple_progress = Signal(int, int, int)                               # 定義一個發送三個整數的信號 (已完成, 剩餘, 總數)，用於更新進度
    signal_tuple_finished = Signal(int, int)                                    # 定義一個發送兩個整數的信號 (成功數, 錯誤數)，表示處理結束

class PDFToMarkdownApp(QMainWindow):                                            # 建立主視窗類別，繼承自 QMainWindow
    def __init__(self):                                                         # 初始化方法
        super().__init__()                                                      # 呼叫父類別的初始化方法
        self.setWindowTitle("PDF to Markdown Converter")                        # 設定視窗標題
        self.resize(650, 450)                                                   # 設定視窗初始大小為 650x450
        
        self.widget_central = QWidget()                                         # 建立一個中央基礎元件
        self.setCentralWidget(self.widget_central)                              # 將基礎元件設定為主視窗的中心
        self.layout_main = QVBoxLayout(self.widget_central)                     # 建立一個垂直排列的排版器，綁定到中央元件
        
        # UI Elements
        self.ui_btn_select_folder = QPushButton("Select Folder")                # 建立一個「選擇資料夾」的按鈕元件
        self.ui_btn_select_folder.setFixedHeight(40)                            # 設定按鈕的固定高度為 40
        
        # Apply some basic styling
        self.ui_btn_select_folder.setStyleSheet("""                             
            QPushButton {                                                       
                font-size: 16px;                                                
                background-color: #007ACC;                                      
                color: white;                                                   
                border-radius: 5px;                                             
            }                                                                   
            QPushButton:hover {                                                 
                background-color: #005999;                                      
            }                                                                   
            QPushButton:disabled {                                              
                background-color: #cccccc;                                      
                color: #666666;                                                 
            }                                                                   
        """)                                                                    # 為按鈕套用 CSS 樣式，設定字體、顏色、圓角及互動效果
        self.ui_btn_select_folder.clicked.connect(self.select_folder)           # 將按鈕的點擊事件綁定到 select_folder 方法
        self.layout_main.addWidget(self.ui_btn_select_folder)                   # 將按鈕加入主要的垂直排版中
        
        # Stats and Progress Bar Layout
        self.layout_stats = QHBoxLayout()                                       # 建立一個水平排列的排版器，用於放置統計資訊
        self.ui_lbl_stats = QLabel("Total: 0 | Completed: 0 | Remaining: 0")    # 建立一個文字標籤，預設顯示各項數值為 0
        self.ui_lbl_stats.setStyleSheet("font-weight: bold; font-size: 14px;")  # 為文字標籤設定粗體與 14px 字型大小
        self.layout_stats.addWidget(self.ui_lbl_stats)                          # 將文字標籤加入水平排版中
        self.layout_main.addLayout(self.layout_stats)                           # 將水平排版加入主要的垂直排版中
        
        self.ui_bar_progress = QProgressBar()                                   # 建立一個進度條元件
        self.ui_bar_progress.setValue(0)                                        # 將進度條初始值設為 0
        self.ui_bar_progress.setTextVisible(True)                               # 設定進度條上的百分比文字為可見
        self.layout_main.addWidget(self.ui_bar_progress)                        # 將進度條加入主要的垂直排版中
        
        self.ui_text_log_area = QTextEdit()                                     # 建立一個多行文字編輯區域，用於顯示日誌
        self.ui_text_log_area.setReadOnly(True)                                 # 將文字區域設定為唯讀，防止使用者修改內容
        self.ui_text_log_area.setStyleSheet("font-family: Courier; font-size: 13px; background-color: #f5f5f5;") # 設定文字區域的字體、大小與背景色
        self.layout_main.addWidget(self.ui_text_log_area)                       # 將文字區域加入主要的垂直排版中
        
        self.bool_is_processing = False                                         # 建立一個布林變數，用來標記目前是否正在處理檔案中
        
        # Setup signals for thread-safe UI updates
        self.obj_signals = WorkerSignals()                                      # 實例化 WorkerSignals 信號物件
        self.obj_signals.signal_str_log_msg.connect(self.append_log)            # 將發送日誌訊息的信號綁定到 append_log 方法
        self.obj_signals.signal_tuple_progress.connect(self.update_progress)    # 將發送進度的信號綁定到 update_progress 方法
        self.obj_signals.signal_tuple_finished.connect(self.on_processing_finished) # 將處理結束的信號綁定到 on_processing_finished 方法

    def append_log(self, str_message):                                          # 定義附加日誌的方法，接收字串型態的訊息
        self.ui_text_log_area.append(str_message)                               # 將傳入的訊息字串附加到日誌文字區域的最後面
        obj_scrollbar = self.ui_text_log_area.verticalScrollBar()               # 取得日誌文字區域的垂直捲軸物件
        obj_scrollbar.setValue(obj_scrollbar.maximum())                         # 將捲軸的位置設定為最底部，實現自動捲動效果

    def update_progress(self, int_completed, int_remaining, int_total):         # 定義更新進度的方法，接收三個整數參數
        self.ui_lbl_stats.setText(f"Total: {int_total} | Completed: {int_completed} | Remaining: {int_remaining}") # 更新畫面上的統計文字標籤內容
        if int_total > 0:                                                       # 檢查總檔案數是否大於 0
            self.ui_bar_progress.setMaximum(int_total)                          # 將進度條的最大值設定為總檔案數
            self.ui_bar_progress.setValue(int_completed)                        # 將進度條的當前值設定為已完成的數量

    def select_folder(self):                                                    # 定義點擊選擇資料夾按鈕時觸發的方法
        if self.bool_is_processing:                                             # 檢查布林變數，如果正在處理中
            QMessageBox.warning(self, "Warning", "Currently processing files. Please wait.") # 顯示警告訊息視窗，請使用者等待
            return                                                              # 結束此方法，不繼續執行
            
        str_folder_selected = QFileDialog.getExistingDirectory(self, "Select Folder to Scan for PDFs") # 開啟選擇資料夾的對話框，取得路徑字串
        if str_folder_selected:                                                 # 如果使用者有選擇資料夾（路徑字串不為空）
            self.ui_text_log_area.clear()                                       # 清空目前日誌文字區域的內容
            self.update_progress(0, 0, 0)                                       # 歸零畫面上的統計文字
            self.ui_bar_progress.setValue(0)                                    # 將進度條歸零
            
            self.append_log(f"Selected folder: {str_folder_selected}")          # 將選取的資料夾路徑寫入日誌
            self.append_log("Starting search and conversion...")                # 寫入開始搜尋與轉換的提示訊息到日誌
            
            self.bool_is_processing = True                                      # 將處理中標記設為 True
            self.ui_btn_select_folder.setEnabled(False)                         # 停用「選擇資料夾」按鈕，避免重複點擊
            obj_thread = threading.Thread(target=self.process_folder, args=(str_folder_selected,), daemon=True) # 建立一個背景執行緒來執行 process_folder 方法
            obj_thread.start()                                                  # 啟動背景執行緒

    def process_folder(self, str_folder_path):                                  # 定義實際處理資料夾的方法，接收資料夾路徑字串
        int_success_count = 0                                                   # 初始化成功轉換的計數器整數變數
        int_error_count = 0                                                     # 初始化轉換失敗的計數器整數變數
        try:                                                                    # 開始使用 try...except 捕捉可能發生的錯誤
            list_pdf_files = list(Path(str_folder_path).rglob("*.pdf"))         # 使用 Path 模組遞迴搜尋資料夾下所有 .pdf 檔案，並轉為清單
            int_total_files = len(list_pdf_files)                               # 取得找到的 PDF 檔案總數，存為整數變數
            
            if int_total_files == 0:                                            # 如果總檔案數為 0
                self.obj_signals.signal_str_log_msg.emit("No PDF files found in the selected folder and its subfolders.") # 發送信號更新日誌，提示找不到檔案
                return                                                          # 結束方法

            self.obj_signals.signal_str_log_msg.emit(f"Found {int_total_files} PDF file(s).") # 發送信號更新日誌，顯示找到的檔案數量
            self.obj_signals.signal_tuple_progress.emit(0, int_total_files, int_total_files) # 初始化發送進度信號，讓畫面知道有幾個檔案要處理
            
            for int_index, path_pdf_file in enumerate(list_pdf_files, start=1): # 使用迴圈逐一處理清單中的每個 PDF 檔案路徑物件，並加上索引值
                path_md_file = path_pdf_file.with_suffix('.md')                 # 將原本的 .pdf 副檔名替換為 .md，建立新的目標路徑物件
                self.obj_signals.signal_str_log_msg.emit(f"[{int_index}/{int_total_files}] Processing: {path_pdf_file.name}") # 發送信號更新日誌，顯示目前正在處理哪一個檔案
                
                try:                                                            # 針對單一檔案的轉換過程使用 try...except 捕捉錯誤
                    str_md_text = pymupdf4llm.to_markdown(str(path_pdf_file))   # 呼叫 pymupdf4llm 將 PDF 轉換為 Markdown 格式的字串變數
                    
                    with open(path_md_file, 'w', encoding='utf-8') as obj_file: # 以寫入模式開啟新的 .md 檔案物件
                        obj_file.write(str_md_text)                             # 將轉換後的 Markdown 字串寫入檔案中
                        
                    self.obj_signals.signal_str_log_msg.emit(f"    -> Saved: {path_md_file.name}") # 發送信號更新日誌，顯示儲存成功
                    int_success_count += 1                                      # 將成功計數器加 1
                except Exception as obj_exception:                              # 若在轉換或儲存過程中發生例外錯誤
                    self.obj_signals.signal_str_log_msg.emit(f"    -> Error processing {path_pdf_file.name}: {str(obj_exception)}") # 發送信號更新日誌，顯示錯誤細節
                    int_error_count += 1                                        # 將失敗計數器加 1
                
                int_remaining = int_total_files - int_index                     # 計算剩餘的檔案數
                self.obj_signals.signal_tuple_progress.emit(int_index, int_remaining, int_total_files) # 發送信號，更新畫面的進度條與統計數字

            self.obj_signals.signal_str_log_msg.emit("=" * 40)                  # 發送信號寫入分隔線到日誌
            self.obj_signals.signal_str_log_msg.emit(f"Finished processing! Successfully converted: {int_success_count}, Errors: {int_error_count}") # 發送信號顯示總結訊息
        except Exception as obj_exception:                                      # 捕捉最外層可能發生的預期外例外錯誤
            self.obj_signals.signal_str_log_msg.emit(f"An unexpected error occurred: {str(obj_exception)}") # 發送信號將未預期的錯誤顯示在日誌中
        finally:                                                                # 不論是否發生錯誤，最後都會執行此區塊
            self.obj_signals.signal_tuple_finished.emit(int_success_count, int_error_count) # 發送信號通知主執行緒處理已經全部結束，並帶上統計數字

    def on_processing_finished(self, int_success_count, int_error_count):       # 定義當收到處理結束信號時觸發的方法
        self.bool_is_processing = False                                         # 將處理中標記重新設為 False
        self.ui_btn_select_folder.setEnabled(True)                              # 重新啟用「選擇資料夾」按鈕
        QMessageBox.information(self, "Completed", f"Conversion completed!\nSuccess: {int_success_count}\nErrors: {int_error_count}") # 彈出對話框告知使用者轉換完成及結果統計

if __name__ == "__main__":                                                      # 判斷是否為直接執行此腳本
    pyside_app = QApplication(sys.argv)                                         # 初始化 PySide6 的 QApplication 物件，並傳入系統參數
    pyside_window = PDFToMarkdownApp()                                          # 實例化我們設計的 PDFToMarkdownApp 主視窗物件
    pyside_window.show()                                                        # 顯示主視窗
    sys.exit(pyside_app.exec())                                                 # 進入應用程式的主迴圈，並在結束時回傳狀態碼給系統
