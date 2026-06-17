#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圖片檔案檢查與清理腳本
檢查指定資料夾中的JPG/JPEG檔案，刪除無法開啟的損壞檔案
"""

import os
import sys
from PIL import Image
from pathlib import Path

def check_and_clean_images(folder_path):
    """
    檢查資料夾中的圖片檔案，刪除損壞的檔案
    
    Args:
        folder_path (str): 要檢查的資料夾路徑
    """
    # 支援的圖片副檔名
    image_extensions = {'.jpg', '.jpeg', '.JPG', '.JPEG'}
    
    # 轉換為Path對象
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"錯誤: 資料夾 '{folder_path}' 不存在！")
        return
    
    if not folder.is_dir():
        print(f"錯誤: '{folder_path}' 不是一個資料夾！")
        return
    
    print(f"正在檢查資料夾: {folder_path}")
    print("-" * 50)
    
    # 統計變數
    total_files = 0
    corrupted_files = 0
    deleted_files = 0
    
    # 遍歷資料夾中的所有檔案
    for file_path in folder.rglob("*"):
        # 檢查是否為圖片檔案
        if file_path.is_file() and file_path.suffix in image_extensions:
            total_files += 1
            print(f"檢查檔案: {file_path.name}", end=" ... ")
            
            try:
                # 嘗試開啟圖片
                with Image.open(file_path) as img:
                    # 載入圖片資料以確保檔案完整
                    img.load()
                    # 驗證圖片
                    img.verify()
                print("✓ 正常")
                
            except Exception as e:
                print(f"✗ 損壞 ({type(e).__name__})")
                corrupted_files += 1
                
                # 詢問是否刪除損壞的檔案
                try:
                    response = input(f"是否刪除損壞的檔案 '{file_path.name}'? (y/n/a=全部刪除): ").lower()
                    
                    if response == 'a':
                        # 設定自動刪除模式
                        auto_delete = True
                        os.remove(file_path)
                        print(f"已刪除: {file_path.name}")
                        deleted_files += 1
                    elif response == 'y':
                        os.remove(file_path)
                        print(f"已刪除: {file_path.name}")
                        deleted_files += 1
                    else:
                        print(f"保留檔案: {file_path.name}")
                        
                except KeyboardInterrupt:
                    print("\n操作被用戶中斷")
                    break
                except OSError as delete_error:
                    print(f"刪除失敗: {delete_error}")
    
    # 顯示統計結果
    print("\n" + "=" * 50)
    print("檢查完成！")
    print(f"總共檢查檔案: {total_files}")
    print(f"發現損壞檔案: {corrupted_files}")
    print(f"已刪除檔案: {deleted_files}")
    print(f"保留檔案: {total_files - deleted_files}")

def check_and_clean_images_auto(folder_path):
    """
    自動模式：檢查並自動刪除所有損壞的圖片檔案（不詢問）
    
    Args:
        folder_path (str): 要檢查的資料夾路徑
    """
    image_extensions = {'.jpg', '.jpeg', '.JPG', '.JPEG'}
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"錯誤: 資料夾 '{folder_path}' 不存在！")
        return
    
    print(f"自動模式：正在檢查資料夾 {folder_path}")
    print("-" * 50)
    
    total_files = 0
    corrupted_files = 0
    deleted_files = 0
    
    for file_path in folder.rglob("*"):
        if file_path.is_file() and file_path.suffix in image_extensions:
            total_files += 1
            print(f"檢查: {file_path.name}", end=" ... ")
            
            try:
                with Image.open(file_path) as img:
                    img.load()
                    img.verify()
                print("✓")
                
            except Exception:
                print("✗ (自動刪除)")
                corrupted_files += 1
                try:
                    os.remove(file_path)
                    deleted_files += 1
                except OSError as e:
                    print(f"刪除失敗: {e}")
    
    print(f"\n檢查完成！總計: {total_files}, 損壞: {corrupted_files}, 已刪除: {deleted_files}")

def main():
    """主函數"""
    print("圖片檔案檢查與清理工具")
    print("=" * 50)
    
    if len(sys.argv) == 1:
        # 互動式模式
        folder_path = input("請輸入要檢查的資料夾路徑: ").strip()
        mode = input("選擇模式 (1=互動式, 2=自動刪除): ").strip()
        
        if mode == "2":
            confirm = input("自動模式將直接刪除所有損壞檔案，確定嗎？(yes/no): ")
            if confirm.lower() == "yes":
                check_and_clean_images_auto(folder_path)
            else:
                print("操作取消")
        else:
            check_and_clean_images(folder_path)
    
    elif len(sys.argv) == 2:
        # 命令列模式 - 互動式
        check_and_clean_images(sys.argv[1])
    
    elif len(sys.argv) == 3 and sys.argv[2] == "--auto":
        # 命令列模式 - 自動刪除
        check_and_clean_images_auto(sys.argv[1])
    
    else:
        print("使用方法:")
        print("1. 互動式: python script.py [資料夾路徑]")
        print("2. 自動刪除: python script.py [資料夾路徑] --auto")
        print("3. 無參數: python script.py (互動式輸入)")

if __name__ == "__main__":
    main()