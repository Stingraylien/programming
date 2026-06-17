#!/bin/bash

# 設定要搜尋的起始目錄
# 預設是當前目錄，可以通過命令列參數指定其他路徑
if [ -n "$1" ]; then
    START_DIR="$1"
else
    START_DIR="."
fi

# 設定 log 檔案路徑
LOG_FILE="$START_DIR/cleanup_log.txt"

# ANSI 顏色代碼，用於輸出著色
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 顯示標題和說明
echo -e "${BLUE}========================================================${NC}"
echo -e "${CYAN}空資料夾清理工具 - 詳細執行過程${NC}"
echo -e "${BLUE}========================================================${NC}"
echo -e "${CYAN}開始搜尋並刪除空資料夾${NC}"
echo -e "${CYAN}起始目錄:${NC} ${YELLOW}$START_DIR${NC}"
echo -e "${BLUE}--------------------------------------------------------${NC}"

# 計數器
REMOVED=0
TOTAL=0
SCANNED=0

# 檢查 log 檔案狀態
if [ -f "$LOG_FILE" ] && [ "$(tail -n 1 "$LOG_FILE")" = "COMPLETED" ]; then
    echo -e "${GREEN}上次的檢查已經完成，重新開始。${NC}"
    > "$LOG_FILE"  # 清空 log 檔案
else
    echo -e "${YELLOW}繼續上次的檢查。${NC}"
fi

# 定義檢查資料夾的函數
check_dir() {
    local dir="$1"
    
    # 檢查是否已經記錄在 log 檔案中，若是則跳過
    if grep -Fxq "$dir" "$LOG_FILE" 2>/dev/null; then
        echo -e "  ${CYAN}[跳過]${NC} 已經檢查過的資料夾: ${YELLOW}$dir${NC}"
        return
    fi
    
    echo -e "${CYAN}掃描目錄:${NC} ${YELLOW}$dir${NC}"
    
    # 遞迴檢查子目錄
    for subdir in "$dir"/*; do
        if [ -d "$subdir" ]; then
            check_dir "$subdir"
        fi
    done
    
    # 檢查當前目錄是否為空
    if [ -z "$(ls -A "$dir")" ]; then
        echo -e "  ${YELLOW}[發現]${NC} 空資料夾: ${BLUE}$dir${NC}"
        echo -e "    ${CYAN}檢查目錄內容:${NC}"
        ls -la "$dir" | while read line; do
            if [[ ! "$line" =~ " \.$" && ! "$line" =~ " \.\.$" ]]; then
                echo -e "    ${RED}意外找到項目:${NC} $line"
            else
                echo -e "    ${GREEN}$line${NC}"
            fi
        done
        echo -e "    ${YELLOW}嘗試刪除...${NC}"
        rmdir "$dir" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "    ${GREEN}✓ 成功刪除${NC}"
            REMOVED=$((REMOVED+1))
        else
            echo -e "    ${RED}✗ 無法刪除 (可能有隱藏檔案或權限問題)${NC}"
            echo -e "    ${YELLOW}嘗試檢查隱藏檔案:${NC}"
            ls -la "$dir"
        fi
        TOTAL=$((TOTAL+1))
    else
        echo -e "  ${GREEN}[結果]${NC} 此目錄不為空"
    fi
    
    # 將檢查過的資料夾記錄到 log 檔案
    echo "$dir" >> "$LOG_FILE"
    SCANNED=$((SCANNED+1))
    echo -e "${BLUE}--------------------------------------------------------${NC}"
}

# 執行檢查
check_dir "$START_DIR"

# 顯示統計信息
echo -e "${BLUE}========================================================${NC}"
echo -e "${CYAN}清理完成！${NC}"
echo -e "${CYAN}統計信息:${NC}"
echo -e "  目錄掃描次數: ${YELLOW}$SCANNED${NC}"
echo -e "  發現空資料夾: ${YELLOW}$TOTAL${NC} 個"
echo -e "  成功刪除資料夾: ${GREEN}$REMOVED${NC} 個"
if [ $REMOVED -lt $TOTAL ]; then
    echo -e "  ${RED}無法刪除的資料夾: ${YELLOW}$((TOTAL-REMOVED))${NC} 個${NC}"
    echo -e "${YELLOW}提示: 無法刪除的資料夾可能包含隱藏檔案或沒有刪除權限${NC}"
    echo -e "${YELLOW}您可以使用 'ls -la [資料夾路徑]' 檢查是否有隱藏檔案${NC}"
fi
echo -e "${BLUE}========================================================${NC}"

# 標記完成
echo "COMPLETED" >> "$LOG_FILE"