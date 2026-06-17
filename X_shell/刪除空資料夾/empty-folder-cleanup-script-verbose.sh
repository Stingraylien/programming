#!/bin/bash

# 設定要搜尋的起始目錄
# 預設是當前目錄，可以修改為其他目錄路徑
if [ -n "$1" ]; then
    START_DIR="$1"
else
    START_DIR="."
fi

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

# 找出並刪除空資料夾的函數
cleanup_empty_dirs() {
    local dir="$1"
    local found=0
    local current_dir_empty_count=0
    
    echo -e "${CYAN}掃描目錄:${NC} ${YELLOW}$dir${NC}"
    
    # 使用find命令找出空目錄
    # -depth選項確保先處理子目錄再處理父目錄
    # -type d只查找目錄
    # -empty只查找空目錄
    
    while IFS= read -r empty_dir; do
        if [ -d "$empty_dir" ]; then
            TOTAL=$((TOTAL+1))
            current_dir_empty_count=$((current_dir_empty_count+1))
            echo -e "  ${YELLOW}[發現]${NC} 空資料夾: ${BLUE}$empty_dir${NC}"
            
            # 顯示目錄內容 (應該為空)
            echo -e "    ${CYAN}檢查目錄內容:${NC}"
            ls -la "$empty_dir" | while read line; do
                # 忽略 . 和 .. 目錄
                if [[ ! "$line" =~ " \.$" && ! "$line" =~ " \.\.$" ]]; then
                    echo -e "    ${RED}意外找到項目:${NC} $line"
                else
                    echo -e "    ${GREEN}$line${NC}"
                fi
            done
            
            # 刪除空資料夾
            echo -e "    ${YELLOW}嘗試刪除...${NC}"
            rmdir "$empty_dir" 2>/dev/null
            
            if [ $? -eq 0 ]; then
                echo -e "    ${GREEN}✓ 成功刪除${NC}"
                REMOVED=$((REMOVED+1))
                found=1
            else
                echo -e "    ${RED}✗ 無法刪除 (可能有隱藏檔案或權限問題)${NC}"
                echo -e "    ${YELLOW}嘗試檢查隱藏檔案:${NC}"
                ls -la "$empty_dir"
            fi
            echo -e "  ${BLUE}----------------------------------------${NC}"
        fi
    done < <(find "$dir" -depth -type d -empty 2>/dev/null)
    
    if [ "$current_dir_empty_count" -eq 0 ]; then
        echo -e "  ${GREEN}[結果]${NC} 此目錄下未發現空資料夾"
    else
        echo -e "  ${GREEN}[結果]${NC} 此目錄下共發現 ${YELLOW}$current_dir_empty_count${NC} 個空資料夾"
    fi
    
    SCANNED=$((SCANNED+1))
    echo -e "${BLUE}--------------------------------------------------------${NC}"
    
    return $found
}

# 循環執行，直到找不到更多空資料夾
# 這是必要的，因為刪除子目錄後，父目錄可能變成空的
iterations=0
while true; do
    iterations=$((iterations+1))
    echo -e "${CYAN}正在執行第 ${YELLOW}$iterations${NC} ${CYAN}次掃描...${NC}"
    
    cleanup_empty_dirs "$START_DIR"
    found=$?
    
    if [ $found -eq 0 ]; then
        # 沒有找到更多空資料夾，退出循環
        echo -e "${GREEN}未發現更多空資料夾，停止掃描。${NC}"
        break
    else
        echo -e "${YELLOW}發現並刪除了空資料夾，需要再次掃描...${NC}"
    fi
done

echo -e "${BLUE}========================================================${NC}"
echo -e "${CYAN}清理完成！${NC}"
echo -e "${CYAN}統計信息:${NC}"
echo -e "  目錄掃描次數: ${YELLOW}$SCANNED${NC}"
echo -e "  發現空資料夾: ${YELLOW}$TOTAL${NC} 個"
echo -e "  成功刪除資料夾: ${GREEN}$REMOVED${NC} 個"

# 如果有無法刪除的資料夾
if [ $REMOVED -lt $TOTAL ]; then
    echo -e "  ${RED}無法刪除的資料夾: ${YELLOW}$((TOTAL-REMOVED))${NC} 個${NC}"
    echo -e "${YELLOW}提示: 無法刪除的資料夾可能包含隱藏檔案或沒有刪除權限${NC}"
    echo -e "${YELLOW}您可以使用 'ls -la [資料夾路徑]' 檢查是否有隱藏檔案${NC}"
fi
echo -e "${BLUE}========================================================${NC}"
