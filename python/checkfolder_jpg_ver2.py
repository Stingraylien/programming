#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圖片檔案檢查與清理腳本
檢查指定資料夾中的JPG/JPEG檔案，刪除無法開啟的損壞檔案
"""

import os
import sys
from PIL import Image
from PIL.Image import UnidentifiedImageError
from pathlib import Path

def is_image_corrupted(file_path):
    """
    檢查圖片是否真正損壞
    使用多層檢測，避免誤判
    
    Args:
        file_path: 圖片檔案路徑
    
    Returns:
        tuple: (is_corrupted, error_type, can_basic_open)
    """
    can_basic_open = False
    error_type = None
    
    try:
        # 第一層：基本開啟測試
        with Image.open(file_path) as img:
            can_basic_open = True
            # 取得基本資訊
            width, height = img.size
            mode = img.mode
            
            # 第二層：嘗試載入像素資料
            try:
                img.load()
            except Exception as load_error:
                error_type = f"LoadError({type(load_error).__name__})"
                # 如果只是載入失敗但能開啟，可能只是格式問題
                return False, error_type, True
            
            # 第三層：嘗試驗證（最嚴格）
            try:
                # 重新開啟進行驗證（因為verify會破壞圖片對象）
                with Image.open(file_path) as verify_img:
                    verify_img.verify()
            except (AttributeError, OSError, IOError) as verify_error:
                error_type = f"VerifyError({type(verify_error).__name__})"
                # AttributeError通常不代表檔案真正損壞
                if isinstance(verify_error, AttributeError):
                    return False, error_type, True
                # 其他驗證錯誤可能是格式問題，但檔案可能仍可用
                return False, error_type, True
            except Exception as verify_error:
                error_type = f"VerifyError({type(verify_error).__name__})"
                return True, error_type, True
                
    except (IOError, OSError, UnidentifiedImageError) as open_error:
        # 無法開啟的檔案才是真正損壞
        error_type = f"OpenError({type(open_error).__name__})"
        return True, error_type, False
    except Exception as unknown_error:
        error_type = f"UnknownError({type(unknown_error).__name__})"
        return True, error_type, False
    
    return False, None, True

def check_and_clean_images(folder_path, strict_mode=False):
    """
    檢查資料夾中的圖片檔案，刪除損壞的檔案
    
    Args:
        folder_path (str): 要檢查的資料夾路徑
        strict_mode (bool): 嚴格模式，連格式問題也視為損壞
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
    print(f"檢測模式: {'嚴格模式' if strict_mode else '寬鬆模式'}")
    print("-" * 50)
    
    # 統計變數
    total_files = 0
    corrupted_files = 0
    format_issues = 0
    deleted_files = 0
    
    # 遍歷資料夾中的所有檔案
    for file_path in folder.rglob("*"):
        # 檢查是否為圖片檔案
        if file_path.is_file() and file_path.suffix in image_extensions:
            total_files += 1
            print(f"檢查檔案: {file_path.name}", end=" ... ")
            
            is_corrupted, error_type, can_open = is_image_corrupted(file_path)
            
            if not is_corrupted and can_open:
                if error_type:
                    print(f"⚠ 格式問題但可開啟 ({error_type})")
                    format_issues += 1
                    if strict_mode:
                        print("  嚴格模式：視為需要處理")
                        is_corrupted = True
                else:
                    print("✓ 正常")
            elif can_open and not strict_mode:
                print(f"⚠ 可開啟但有問題 ({error_type})")
                format_issues += 1
            else:
                print(f"✗ 真正損壞 ({error_type})")
                is_corrupted = True
            
            if is_corrupted or (strict_mode and error_type):
                corrupted_files += 1
                
                # 詢問是否刪除檔案
                try:
                    if can_open and not strict_mode:
                        response = input(f"檔案可開啟但有格式問題，是否仍要刪除 '{file_path.name}'? (y/n/a=全部刪除): ").lower()
                    else:
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
    print(f"真正損壞檔案: {corrupted_files}")
    print(f"格式問題檔案: {format_issues}")
    print(f"已刪除檔案: {deleted_files}")
    print(f"保留檔案: {total_files - deleted_files}")

def check_and_clean_images_auto(folder_path, strict_mode=False):
    """
    自動模式：檢查並自動刪除所有損壞的圖片檔案（不詢問）
    
    Args:
        folder_path (str): 要檢查的資料夾路徑
        strict_mode (bool): 嚴格模式，連格式問題也自動刪除
    """
    image_extensions = {'.jpg', '.jpeg', '.JPG', '.JPEG'}
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"錯誤: 資料夾 '{folder_path}' 不存在！")
        return
    
    print(f"自動模式：正在檢查資料夾 {folder_path}")
    print(f"檢測模式: {'嚴格模式' if strict_mode else '寬鬆模式'}")
    print("-" * 50)
    
    total_files = 0
    corrupted_files = 0
    format_issues = 0
    deleted_files = 0
    
    for file_path in folder.rglob("*"):
        if file_path.is_file() and file_path.suffix in image_extensions:
            total_files += 1
            print(f"檢查: {file_path.name}", end=" ... ")
            
            is_corrupted, error_type, can_open = is_image_corrupted(file_path)
            
            should_delete = False
            
            if not is_corrupted and can_open:
                if error_type:
                    print(f"⚠ 格式問題 ({error_type})")
                    format_issues += 1
                    if strict_mode:
                        should_delete = True
                else:
                    print("✓")
            elif can_open and not strict_mode:
                print(f"⚠ 保留 ({error_type})")
                format_issues += 1
            else:
                print(f"✗ 刪除 ({error_type})")
                should_delete = True
                corrupted_files += 1
            
            if should_delete:
                try:
                    os.remove(file_path)
                    deleted_files += 1
                except OSError as e:
                    print(f"  刪除失敗: {e}")
    
    print(f"\n檢查完成！")
    print(f"總計: {total_files}, 損壞: {corrupted_files}, 格式問題: {format_issues}, 已刪除: {deleted_files}")

def main():
    """主函數"""
    print("圖片檔案檢查與清理工具 v2.0")
    print("=" * 50)
    
    if len(sys.argv) == 1:
        # 互動式模式
        folder_path = input("請輸入要檢查的資料夾路徑: ").strip()
        print("\n檢測模式選擇：")
        print("1. 寬鬆模式 - 只刪除真正無法開啟的檔案")
        print("2. 嚴格模式 - 刪除所有有問題的檔案（包括格式問題）")
        mode_choice = input("選擇檢測模式 (1/2): ").strip()
        strict_mode = (mode_choice == "2")
        
        print("\n執行模式選擇：")
        print("1. 互動式 - 逐個確認刪除")
        print("2. 自動刪除 - 直接刪除所有問題檔案")
        exec_mode = input("選擇執行模式 (1/2): ").strip()
        
        if exec_mode == "2":
            confirm_msg = "自動刪除所有問題檔案" if strict_mode else "自動刪除真正損壞的檔案"
            confirm = input(f"{confirm_msg}，確定嗎？(yes/no): ")
            if confirm.lower() == "yes":
                check_and_clean_images_auto(folder_path, strict_mode)
            else:
                print("操作取消")
        else:
            check_and_clean_images(folder_path, strict_mode)
    
    elif len(sys.argv) >= 2:
        folder_path = sys.argv[1]
        strict_mode = "--strict" in sys.argv
        auto_mode = "--auto" in sys.argv
        
        if auto_mode:
            check_and_clean_images_auto(folder_path, strict_mode)
        else:
            check_and_clean_images(folder_path, strict_mode)
    
    else:
        print("使用方法:")
        print("1. 互動式: python script.py")
        print("2. 寬鬆模式: python script.py [資料夾路徑]")
        print("3. 嚴格模式: python script.py [資料夾路徑] --strict")
        print("4. 自動刪除: python script.py [資料夾路徑] --auto")
        print("5. 嚴格+自動: python script.py [資料夾路徑] --strict --auto")
        print("\n模式說明:")
        print("- 寬鬆模式: 只刪除真正無法開啟的檔案")
        print("- 嚴格模式: 連格式有問題但可開啟的檔案也處理")
        print("- 自動模式: 不詢問直接刪除問題檔案")