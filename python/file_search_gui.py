#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案搜尋程式 - 搜尋檔名中包含特定字串的檔案
修復 macOS 兼容性問題的 GUI 版本
"""

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    GUI_AVAILABLE = True
except ImportError:
    print("❌ tkinter 不可用，改用命令列模式")
    GUI_AVAILABLE = False

import os
import threading
import subprocess
import sys
from pathlib import Path
import time
import datetime
import math


class FileSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("檔案搜尋工具")
        self.root.geometry("900x700")
        
        # 設定 macOS 特定樣式
        if sys.platform == "darwin":
            try:
                # 使用 macOS 原生外觀
                self.root.tk.call('tk', 'scaling', 1.0)
            except:
                pass
        
        # 設定變數
        self.search_path = tk.StringVar(value=os.path.expanduser("~"))
        self.search_text = tk.StringVar()
        self.case_sensitive = tk.BooleanVar()
        self.include_subfolders = tk.BooleanVar(value=True)
        self.search_running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """建立使用者介面"""
        # 主容器
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 搜尋區域
        search_frame = ttk.LabelFrame(main_frame, text="搜尋設定", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 路徑選擇
        ttk.Label(search_frame, text="搜尋路徑:").grid(row=0, column=0, sticky=tk.W, pady=2)
        path_frame = ttk.Frame(search_frame)
        path_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        search_frame.columnconfigure(1, weight=1)
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.search_path)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="瀏覽", command=self.browse_folder).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 搜尋文字
        ttk.Label(search_frame, text="搜尋字串:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.text_entry = ttk.Entry(search_frame, textvariable=self.search_text)
        self.text_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self.text_entry.bind('<Return>', lambda e: self.start_search())
        
        # 選項
        options_frame = ttk.Frame(search_frame)
        options_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        ttk.Checkbutton(options_frame, text="區分大小寫", variable=self.case_sensitive).pack(side=tk.LEFT)
        ttk.Checkbutton(options_frame, text="包含子資料夾", variable=self.include_subfolders).pack(side=tk.LEFT, padx=(20, 0))
        
        # 按鈕區域
        button_frame = ttk.Frame(search_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        self.search_btn = ttk.Button(button_frame, text="🔍 開始搜尋", command=self.start_search)
        self.search_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ 停止", command=self.stop_search, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="🗑️ 清除", command=self.clear_results).pack(side=tk.LEFT)
        
        # 結果區域
        result_frame = ttk.LabelFrame(main_frame, text="搜尋結果", padding=5)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 結果列表
        list_frame = ttk.Frame(result_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 使用 Listbox 替代 Treeview 以提高兼容性
        self.result_listbox = tk.Listbox(list_frame, font=("Monaco", 11))
        scrollbar_v = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.result_listbox.yview)
        scrollbar_h = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.result_listbox.xview)
        
        self.result_listbox.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.result_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 綁定雙擊事件
        self.result_listbox.bind('<Double-Button-1>', self.open_selected_file)
        self.result_listbox.bind('<Button-2>', self.show_context_menu)  # 右鍵 (macOS)
        self.result_listbox.bind('<Control-Button-1>', self.show_context_menu)  # Ctrl+點擊 (macOS)
        
        # 操作按鈕
        action_frame = ttk.Frame(result_frame)
        action_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(action_frame, text="📂 開啟檔案", command=self.open_selected_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="📁 開啟資料夾", command=self.open_file_location).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="📋 複製路徑", command=self.copy_path).pack(side=tk.LEFT)
        
        # 狀態列
        self.status_var = tk.StringVar(value="就緒")
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X)
        
        # 儲存結果數據
        self.results = []
    
    def show_context_menu(self, event):
        """顯示右鍵選單"""
        try:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="開啟檔案", command=self.open_selected_file)
            menu.add_command(label="開啟資料夾", command=self.open_file_location)
            menu.add_separator()
            menu.add_command(label="複製路徑", command=self.copy_path)
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def browse_folder(self):
        """瀏覽資料夾"""
        folder = filedialog.askdirectory(title="選擇搜尋資料夾", initialdir=self.search_path.get())
        if folder:
            self.search_path.set(folder)
    
    def start_search(self):
        """開始搜尋"""
        if not self.search_path.get().strip():
            messagebox.showwarning("警告", "請選擇搜尋路徑！")
            return
            
        if not self.search_text.get().strip():
            messagebox.showwarning("警告", "請輸入搜尋字串！")
            return
            
        if not os.path.exists(self.search_path.get()):
            messagebox.showerror("錯誤", "搜尋路徑不存在！")
            return
        
        self.clear_results()
        self.search_running = True
        self.search_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set("搜尋中...")
        
        # 在新線程中搜尋
        threading.Thread(target=self.search_files, daemon=True).start()
    
    def stop_search(self):
        """停止搜尋"""
        self.search_running = False
        self.search_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("搜尋已停止")
    
    def search_files(self):
        """搜尋檔案"""
        search_path = Path(self.search_path.get())
        search_text = self.search_text.get()
        case_sensitive = self.case_sensitive.get()
        include_subfolders = self.include_subfolders.get()
        
        if not case_sensitive:
            search_text = search_text.lower()
        
        found_count = 0
        
        try:
            pattern = "**/*" if include_subfolders else "*"
            
            for file_path in search_path.glob(pattern):
                if not self.search_running:
                    break
                    
                if file_path.is_file():
                    filename = file_path.name
                    check_name = filename.lower() if not case_sensitive else filename
                    
                    if search_text in check_name:
                        try:
                            stat_info = file_path.stat()
                            size = self.format_file_size(stat_info.st_size)
                            modified = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M")
                            
                            result = {
                                'filename': filename,
                                'path': str(file_path.parent),
                                'full_path': str(file_path),
                                'size': size,
                                'modified': modified
                            }
                            
                            # 更新 GUI
                            self.root.after(0, self.add_result, result)
                            found_count += 1
                            
                            self.root.after(0, self.status_var.set, f"搜尋中... 找到 {found_count} 個檔案")
                            
                        except (OSError, PermissionError):
                            continue
                            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "錯誤", f"搜尋錯誤：{str(e)}")
        
        if self.search_running:
            self.root.after(0, self.search_completed, found_count)
    
    def search_completed(self, found_count):
        """搜尋完成"""
        self.search_running = False
        self.search_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set(f"搜尋完成，共找到 {found_count} 個檔案")
    
    def add_result(self, result):
        """添加搜尋結果"""
        self.results.append(result)
        # 格式化顯示文字
        display_text = f"{result['filename']:<30} | {result['size']:<10} | {result['modified']:<16} | {result['path']}"
        self.result_listbox.insert(tk.END, display_text)
    
    def clear_results(self):
        """清除結果"""
        self.results = []
        self.result_listbox.delete(0, tk.END)
        self.status_var.set("就緒")
    
    def get_selected_result(self):
        """取得選中的結果"""
        selection = self.result_listbox.curselection()
        if selection:
            return self.results[selection[0]]
        return None
    
    def open_selected_file(self, event=None):
        """開啟選中的檔案"""
        result = self.get_selected_result()
        if not result:
            messagebox.showwarning("警告", "請選擇一個檔案！")
            return
        
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(['open', result['full_path']])
            elif sys.platform == "win32":  # Windows
                os.startfile(result['full_path'])
            else:  # Linux
                subprocess.run(['xdg-open', result['full_path']])
        except Exception as e:
            messagebox.showerror("錯誤", f"無法開啟檔案：{str(e)}")
    
    def open_file_location(self):
        """開啟檔案所在資料夾"""
        result = self.get_selected_result()
        if not result:
            messagebox.showwarning("警告", "請選擇一個檔案！")
            return
        
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(['open', result['path']])
            elif sys.platform == "win32":  # Windows
                os.startfile(result['path'])
            else:  # Linux
                subprocess.run(['xdg-open', result['path']])
        except Exception as e:
            messagebox.showerror("錯誤", f"無法開啟資料夾：{str(e)}")
    
    def copy_path(self):
        """複製路徑到剪貼簿"""
        result = self.get_selected_result()
        if not result:
            messagebox.showwarning("警告", "請選擇一個檔案！")
            return
        
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(['pbcopy'], input=result['full_path'], text=True)
            elif sys.platform == "win32":  # Windows
                os.system(f'echo {result["full_path"]} | clip')
            else:  # Linux
                subprocess.run(['xclip', '-selection', 'clipboard'], input=result['full_path'], text=True)
            
            messagebox.showinfo("成功", "路徑已複製到剪貼簿！")
        except Exception as e:
            messagebox.showerror("錯誤", f"複製失敗：{str(e)}")
    
    @staticmethod
    def format_file_size(size_bytes):
        """格式化檔案大小"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"


def main():
    """主程式"""
    if not GUI_AVAILABLE:
        print("GUI 不可用，請檢查 tkinter 安裝")
        return
    
    root = tk.Tk()
    
    # macOS 特定設定
    if sys.platform == "darwin":
        try:
            # 設定應用程式名稱
            root.createcommand('tk::mac::ReopenApplication', lambda: root.deiconify())
        except:
            pass
    
    app = FileSearchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()