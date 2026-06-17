#!/bin/bash

# 設定要搜尋的起始目錄
# 預設是當前目錄，可以修改為其他目錄路徑
START_DIR="."

# 顯示說明
echo "開始搜尋並刪除空資料夾，起始目錄: $START_DIR"
echo "-------------------------------------------"

# 計數器
REMOVED=0
TOTAL=0

# 找出並刪除空資料夾的函數
cleanup_empty_dirs() {
  local dir="$1"
  local found=0
  
  # 使用find命令找出空目錄
  # -depth選項確保先處理子目錄再處理父目錄
  # -type d只查找目錄
  # -empty只查找空目錄
  
  while IFS= read -r empty_dir; do
    if [ -d "$empty_dir" ]; then
      TOTAL=$((TOTAL+1))
      echo "發現空資料夾: $empty_dir"
      
      # 刪除空資料夾
      rmdir "$empty_dir" 2>/dev/null
      
      if [ $? -eq 0 ]; then
        echo "已刪除: $empty_dir"
        REMOVED=$((REMOVED+1))
        found=1
      else
        echo "無法刪除: $empty_dir (可能有隱藏檔案或權限問題)"
      fi
    fi
  done < <(find "$dir" -depth -type d -empty)
  
  return $found
}

# 循環執行，直到找不到更多空資料夾
# 這是必要的，因為刪除子目錄後，父目錄可能變成空的
iterations=0
while true; do
  iterations=$((iterations+1))
  echo "正在執行第 $iterations 次掃描..."
  
  cleanup_empty_dirs "$START_DIR"
  found=$?
  
  if [ $found -eq 0 ]; then
    # 沒有找到更多空資料夾，退出循環
    break
  fi
done

echo "-------------------------------------------"
echo "清理完成！"
echo "統計: 發現 $TOTAL 個空資料夾，成功刪除 $REMOVED 個"

# 如果有無法刪除的資料夾
if [ $REMOVED -lt $TOTAL ]; then
  echo "提示: 有 $((TOTAL-REMOVED)) 個資料夾無法刪除，可能包含隱藏檔案或沒有刪除權限"
  echo "您可以使用 'ls -la [資料夾路徑]' 檢查是否有隱藏檔案"
fi
