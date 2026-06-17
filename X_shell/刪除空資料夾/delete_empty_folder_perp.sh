#!/bin/bash

# 設定要搜尋的起始目錄
if [ -n "$1" ]; then
    START_DIR="$1"
else
    START_DIR="."
fi

# 設定日誌檔案
LOG_FILE="cleanup_log.txt"
COMPLETION_MARK="COMPLETED"

# ANSI 顏色代碼
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 計數器
REMOVED=0
TOTAL=0
SCANNED=0

# 檢查日誌檔案是否存在，如果不存在則創建
if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
fi

# 檢查日誌檔案是否已完成
is_completed() {
    if grep -q "$COMPLETION_MARK" "$LOG_FILE"; then
        return 0
    else
        return 1
    fi
}

# 檢查目錄是否已被掃描
is_dir_scanned() {
    if grep -q "^$1$" "$LOG_FILE"; then
        return 0
    else
        return 1
    fi
}

# 記錄已掃描的目錄
log_scanned_dir() {
    echo "$1" >> "$LOG_FILE"
}

# 找出並刪除空資料夾的函數
cleanup_empty_dirs() {
    local dir="$1"
    local found=0
    local current_dir_empty_count=0

    # 檢查目錄是否已被掃描
    if is_dir_scanned "$dir"; then
        echo -e "${YELLOW}跳過已掃描的目錄:${NC} ${BLUE}$dir${NC}"
        return 0
    fi

    echo -e "${CYAN}掃描目錄:${NC} ${YELLOW}$dir${NC}"
    log_scanned_dir "$dir"

    # 使用find命令找出空目錄
    while IFS= read -r empty_dir; do
        if [ -d "$empty_dir" ]; then
            TOTAL=$((TOTAL+1))
            current_dir_empty_count=$((current_dir_empty_count+1))
            echo -e " ${YELLOW}[發現]${NC} 空資料夾: ${BLUE}$empty_dir${NC}"
            
            # 刪除空資料夾
            echo -e " ${YELLOW}嘗試刪除...${NC}"
            rmdir "$empty_dir" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo -e " ${GREEN}✓ 成功刪除${NC}"
                REMOVED=$((REMOVED+1))
                found=1
            else
                echo -e " ${RED}✗ 無法刪除 (可能有隱藏檔案或權限問題)${NC}"
            fi
            echo -e " ${BLUE}----------------------------------------${NC}"
        fi
    done < <(find "$dir" -depth -type d -empty 2>/dev/null)

    if [ "$current_dir_empty_count" -eq 0 ]; then
        echo -e " ${GREEN}[結果]${NC} 此目錄下未發現空資料夾"
    else
        echo -e " ${GREEN}[結果]${NC} 此目錄下共發現 ${YELLOW}$current_dir_empty_count${NC} 個空資料夾"
    fi

    SCANNED=$((SCANNED+1))
    echo -e "${BLUE}--------------------------------------------------------${NC}"

    return $found
}

# 主程序
main() {
    echo -e "${BLUE}========================================================${NC}"
    echo -e "${CYAN}空資料夾清理工具 - 詳細執行過程${NC}"
    echo -e "${BLUE}========================================================${NC}"
    echo -e "${CYAN}開始搜尋並刪除空資料夾${NC}"
    echo -e "${CYAN}起始目錄:${NC} ${YELLOW}$START_DIR${NC}"
    echo -e "${BLUE}--------------------------------------------------------${NC}"

    if is_completed; then
        echo -e "${GREEN}上次掃描已完成，重新開始掃描。${NC}"
        > "$LOG_FILE"  # 清空日誌檔案
    else
        echo -e "${YELLOW}繼續上次未完成的掃描。${NC}"
    fi

    iterations=0
    while true; do
        iterations=$((iterations+1))
        echo -e "${CYAN}正在執行第 ${YELLOW}$iterations${NC} ${CYAN}次掃描...${NC}"
        cleanup_empty_dirs "$START_DIR"
        found=$?
        if [ $found -eq 0 ]; then
            echo -e "${GREEN}未發現更多空資料夾，停止掃描。${NC}"
            break
        else
            echo -e "${YELLOW}發現並刪除了空資料夾，需要再次掃描...${NC}"
        fi
    done

    echo -e "${BLUE}========================================================${NC}"
    echo -e "${CYAN}清理完成！${NC}"
    echo -e "${CYAN}統計信息:${NC}"
    echo -e " 目錄掃描次數: ${YELLOW}$SCANNED${NC}"
    echo -e " 發現空資料夾: ${YELLOW}$TOTAL${NC} 個"
    echo -e " 成功刪除資料夾: ${GREEN}$REMOVED${NC} 個"

    if [ $REMOVED -lt $TOTAL ]; then
        echo -e " ${RED}無法刪除的資料夾: ${YELLOW}$((TOTAL-REMOVED))${NC} 個${NC}"
        echo -e "${YELLOW}提示: 無法刪除的資料夾可能包含隱藏檔案或沒有刪除權限${NC}"
        echo -e "${YELLOW}您可以使用 'ls -la [資料夾路徑]' 檢查是否有隱藏檔案${NC}"
    fi

    echo -e "${BLUE}========================================================${NC}"

    # 標記完成
    echo "$COMPLETION_MARK" >> "$LOG_FILE"
}

# 捕獲中斷信號
trap 'echo -e "${RED}腳本被中止${NC}"; exit 1' INT TERM

# 執行主程序
main

exit 0
