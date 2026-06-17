#!/bin/bash

# MP4 重複檔案檢測和刪除腳本
# 使用方法: ./find_duplicate_mp4.sh [資料夾路徑]

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函數：顯示使用說明
show_usage() {
    echo "使用方法："
    echo "  $0 [資料夾路徑]"
    echo ""
    echo "範例："
    echo "  $0 /Users/username/Movies"
    echo "  $0 ."
    echo ""
    echo "如果不指定路徑，將使用當前目錄"
}

# 函數：確認用戶輸入
confirm() {
    while true; do
        read -p "$1 (y/n): " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "請輸入 y 或 n";;
        esac
    done
}

# 設定目標資料夾
if [ $# -eq 0 ]; then
    TARGET_DIR="."
elif [ $# -eq 1 ]; then
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi
    TARGET_DIR="$1"
else
    echo -e "${RED}錯誤：參數過多${NC}"
    show_usage
    exit 1
fi

# 檢查目錄是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}錯誤：目錄 '$TARGET_DIR' 不存在${NC}"
    exit 1
fi

# 轉換為絕對路徑
TARGET_DIR=$(cd "$TARGET_DIR" && pwd)
echo -e "${BLUE}檢查目錄：${NC}$TARGET_DIR"

# 創建臨時檔案
TEMP_DIR=$(mktemp -d)
SIZE_FILE="$TEMP_DIR/sizes.txt"
HASH_FILE="$TEMP_DIR/hashes.txt"
DUPLICATE_FILE="$TEMP_DIR/duplicates.txt"

# 清理函數
cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# 步驟1：找到所有 mp4 檔案
echo -e "${YELLOW}步驟1：搜尋 MP4 檔案...${NC}"
find "$TARGET_DIR" -maxdepth 1 -name "*.mp4" -type f > "$TEMP_DIR/mp4_files.txt"

if [ ! -s "$TEMP_DIR/mp4_files.txt" ]; then
    echo -e "${RED}在目錄中沒有找到 MP4 檔案${NC}"
    exit 0
fi

TOTAL_FILES=$(wc -l < "$TEMP_DIR/mp4_files.txt")
echo -e "${GREEN}找到 $TOTAL_FILES 個 MP4 檔案${NC}"

# 步驟2：獲取檔案大小
echo -e "${YELLOW}步驟2：分析檔案大小...${NC}"
while IFS= read -r file; do
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        basename=$(basename "$file")
        echo "$size|$file|$basename" >> "$SIZE_FILE"
    fi
done < "$TEMP_DIR/mp4_files.txt"

# 步驟3：找出相同大小的檔案
echo -e "${YELLOW}步驟3：尋找相同大小的檔案...${NC}"
awk -F'|' '{sizes[$1] = sizes[$1] $0 "\n"} END {for(size in sizes) if(gsub(/\n/, "&", sizes[size]) > 1) printf "%s", sizes[size]}' "$SIZE_FILE" > "$TEMP_DIR/same_size.txt"

if [ ! -s "$TEMP_DIR/same_size.txt" ]; then
    echo -e "${GREEN}沒有找到相同大小的檔案，因此沒有重複檔案${NC}"
    exit 0
fi

GROUPS_TO_CHECK=$(awk -F'|' '{print $1}' "$TEMP_DIR/same_size.txt" | sort -u | wc -l)
echo -e "${BLUE}找到 $GROUPS_TO_CHECK 組相同大小的檔案${NC}"

# 步驟4：計算 MD5 雜湊值
echo -e "${YELLOW}步驟4：計算檔案內容雜湊值...${NC}"
current_group=0
while IFS= read -r size; do
    current_group=$((current_group + 1))
    echo -e "${BLUE}處理第 $current_group / $GROUPS_TO_CHECK 組...${NC}"
    
    # 獲取相同大小的檔案
    awk -F'|' -v target_size="$size" '$1 == target_size {print $2}' "$TEMP_DIR/same_size.txt" > "$TEMP_DIR/current_group.txt"
    
    # 計算這組檔案的 MD5
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            hash=$(md5 -q "$file" 2>/dev/null || md5sum "$file" 2>/dev/null | cut -d' ' -f1)
            basename=$(basename "$file")
            echo "$hash|$file|$basename" >> "$HASH_FILE"
        fi
    done < "$TEMP_DIR/current_group.txt"
    
done < <(awk -F'|' '{print $1}' "$TEMP_DIR/same_size.txt" | sort -u)

# 步驟5：找出重複檔案
echo -e "${YELLOW}步驟5：識別重複檔案...${NC}"
awk -F'|' '{hashes[$1] = hashes[$1] $0 "\n"} END {for(hash in hashes) if(gsub(/\n/, "&", hashes[hash]) > 1) printf "%s", hashes[hash]}' "$HASH_FILE" > "$DUPLICATE_FILE"

if [ ! -s "$DUPLICATE_FILE" ]; then
    echo -e "${GREEN}沒有找到重複的 MP4 檔案${NC}"
    exit 0
fi

# 顯示結果
echo -e "\n${GREEN}=== 找到重複檔案 ===${NC}"
duplicate_groups=0
total_duplicates=0

while IFS= read -r hash; do
    duplicate_groups=$((duplicate_groups + 1))
    echo -e "\n${YELLOW}重複組 $duplicate_groups：${NC}"
    
    group_files=$(awk -F'|' -v target_hash="$hash" '$1 == target_hash {print $3}' "$DUPLICATE_FILE")
    group_count=$(echo "$group_files" | wc -l)
    total_duplicates=$((total_duplicates + group_count - 1))
    
    echo "$group_files" | while IFS= read -r filename; do
        echo "  • $filename"
    done
    
done < <(awk -F'|' '{print $1}' "$DUPLICATE_FILE" | sort -u)

echo -e "\n${BLUE}總共可刪除 $total_duplicates 個重複檔案（每組保留第一個檔案）${NC}"

# 詢問是否刪除
echo ""
if confirm "是否要刪除重複檔案？"; then
    echo -e "\n${RED}⚠️  警告：即將刪除 $total_duplicates 個重複檔案！${NC}"
    echo "每組重複檔案將保留第一個，其餘移至垃圾桶。"
    echo ""
    
    if confirm "確定要繼續嗎？"; then
        deleted_count=0
        error_count=0
        
        echo -e "\n${YELLOW}正在刪除重複檔案...${NC}"
        
        while IFS= read -r hash; do
            # 獲取這組重複檔案的路徑
            awk -F'|' -v target_hash="$hash" '$1 == target_hash {print $2}' "$DUPLICATE_FILE" > "$TEMP_DIR/to_delete.txt"
            
            # 跳過第一個檔案，刪除其餘檔案
            tail -n +2 "$TEMP_DIR/to_delete.txt" | while IFS= read -r file_to_delete; do
                if [ -f "$file_to_delete" ]; then
                    filename=$(basename "$file_to_delete")
                    if mv "$file_to_delete" ~/.Trash/ 2>/dev/null; then
                        echo -e "${GREEN}✓ 已刪除：$filename${NC}"
                        deleted_count=$((deleted_count + 1))
                    else
                        echo -e "${RED}✗ 刪除失敗：$filename${NC}"
                        error_count=$((error_count + 1))
                    fi
                fi
            done
            
        done < <(awk -F'|' '{print $1}' "$DUPLICATE_FILE" | sort -u)
        
        echo -e "\n${GREEN}=== 刪除操作完成 ===${NC}"
        echo -e "${GREEN}成功刪除：$deleted_count 個檔案${NC}"
        if [ $error_count -gt 0 ]; then
            echo -e "${RED}刪除失敗：$error_count 個檔案${NC}"
        fi
        
        if confirm "是否要在 Finder 中顯示資料夾？"; then
            open "$TARGET_DIR"
        fi
    else
        echo "操作已取消"
    fi
else
    echo "操作已取消"
    
    if confirm "是否要儲存報告到桌面？"; then
        report_file="$HOME/Desktop/MP4重複檔案報告.txt"
        {
            echo "MP4 重複檔案檢測報告"
            echo "檢查目錄：$TARGET_DIR"
            echo "檢查時間：$(date)"
            echo ""
            echo "找到 $duplicate_groups 組重複檔案："
            echo ""
            
            group_num=0
            while IFS= read -r hash; do
                group_num=$((group_num + 1))
                echo "重複組 $group_num："
                awk -F'|' -v target_hash="$hash" '$1 == target_hash {print "  • " $3}' "$DUPLICATE_FILE"
                echo ""
            done < <(awk -F'|' '{print $1}' "$DUPLICATE_FILE" | sort -u)
            
            echo "總共可刪除 $total_duplicates 個重複檔案"
            
        } > "$report_file"
        
        echo -e "${GREEN}報告已儲存到：$report_file${NC}"
    fi
fi