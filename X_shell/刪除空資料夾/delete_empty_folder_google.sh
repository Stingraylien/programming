#!/bin/bash

# --- 設定 ---
LOG_FILE_NAME="process_status.log" # 日誌檔案名稱
COMPLETION_MARKER="##ALL_DIRECTORIES_PROCESSED_SUCCESSFULLY##" # 完成標記

# --- 函數：顯示訊息 ---
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# --- 步驟 1: 選擇根資料夾 ---
log_message "提示使用者選擇根資料夾..."
# 使用 AppleScript 取得資料夾路徑 (適用於 macOS)
START_DIR=$(osascript -e 'tell application "System Events" to activate' \
                      -e 'set folderPath to choose folder with prompt "請選擇要處理的根資料夾：" without invisibles' \
                      -e 'POSIX path of folderPath' 2>/dev/null)

# 檢查使用者是否取消選擇
if [ -z "$START_DIR" ]; then
    log_message "錯誤：未選擇資料夾，程式結束。"
    exit 1
fi

# 確保 START_DIR 路徑結尾沒有斜線，方便後續處理
START_DIR="${START_DIR%/}"
LOG_FILE="$START_DIR/$LOG_FILE_NAME" # 日誌檔案完整路徑

log_message "選擇的根資料夾: $START_DIR"
log_message "日誌檔案將位於: $LOG_FILE"
echo "-------------------------------------------"


# --- 步驟 2: 檢查並讀取日誌檔案 ---
processed_dirs=() # 用陣列儲存已處理的資料夾名稱

if [ -f "$LOG_FILE" ]; then
    log_message "找到日誌檔案: $LOG_FILE"
    # 檢查是否有完成標記
    if grep -qFx "$COMPLETION_MARKER" "$LOG_FILE"; then
        log_message "狀態：上次執行已成功完成。"
        read -p "是否要清除紀錄並重新開始檢查? (y/N): " choice
        case "$choice" in
          y|Y )
            log_message "動作：清除舊日誌並重新開始..."
            rm "$LOG_FILE"
            # 建立空的日誌檔
            touch "$LOG_FILE"
            ;;
          * )
            log_message "動作：不執行新的檢查。程式結束。"
            exit 0
            ;;
        esac
    else
        log_message "狀態：上次執行未完成或被中斷。將嘗試從上次紀錄繼續。"
        # 讀取已處理的資料夾名稱 (排除完成標記和空行)
        while IFS= read -r line; do
            if [[ -n "$line" && "$line" != "$COMPLETION_MARKER" ]]; then
                 processed_dirs+=("$line")
            fi
        done < "$LOG_FILE"
        log_message "已載入 ${#processed_dirs[@]} 個已處理的資料夾紀錄。"
    fi
else
    log_message "狀態：未找到日誌檔案，將開始全新檢查。"
    # 建立空的日誌檔
    touch "$LOG_FILE"
    if [ $? -ne 0 ]; then
        log_message "錯誤：無法在 $START_DIR 中建立日誌檔案 $LOG_FILE_NAME。請檢查權限。"
        exit 1
    fi
fi
echo "-------------------------------------------"


# --- 函數：檢查資料夾是否已處理 ---
is_processed() {
    local dir_to_check="$1"
    local dir_base_name=$(basename "$dir_to_check") # 只比較基本名稱
    for processed_dir in "${processed_dirs[@]}"; do
        if [[ "$processed_dir" == "$dir_base_name" ]]; then
            return 0 # 找到 (已處理)，返回 true (shell 0)
        fi
    done
    return 1 # 未找到 (未處理)，返回 false (shell 1)
}

# --- 步驟 3: 找出所有目標子資料夾 ---
# 使用 find 找出 START_DIR 下的第一層子資料夾
# -mindepth 1 避免 START_DIR 本身
# -maxdepth 1 只找第一層
# -type d 只找資料夾
target_dirs=()
while IFS= read -r dir; do
    target_dirs+=("$dir")
done < <(find "$START_DIR" -mindepth 1 -maxdepth 1 -type d)

total_target_dirs=${#target_dirs[@]}
log_message "在 '$START_DIR' 中找到 $total_target_dirs 個第一層子資料夾。"

if [ $total_target_dirs -eq 0 ]; then
    log_message "警告：在 '$START_DIR' 下未找到任何子資料夾可供處理。"
    # 如果沒有子資料夾，可以視為「完成」
    if ! grep -qFx "$COMPLETION_MARKER" "$LOG_FILE"; then
         echo "$COMPLETION_MARKER" >> "$LOG_FILE"
         sync # 嘗試將緩衝區寫入磁碟
         log_message "已將完成標記寫入空的日誌檔案。"
    fi
    log_message "程式結束。"
    exit 0
fi

# --- 步驟 4: 迭代處理每個子資料夾 ---
all_processed_this_run=1 # 標記此輪執行是否所有都成功處理或跳過

for dir_path in "${target_dirs[@]}"; do
    dir_name=$(basename "$dir_path")
    log_message "--- 開始處理資料夾: $dir_name ---"

    # 檢查是否已處理過
    if is_processed "$dir_path"; then
        log_message "跳過：'$dir_name' 已在日誌中標記為已處理。"
        echo "-------------------------------------------"
        continue # 處理下一個資料夾
    fi

    log_message "執行檢查/處理：'$dir_name' (路徑: $dir_path)"

    # ==============================================================
    # V V V V V V V V V V V V V V V V V V V V V V V V V V V V V V V
    #
    # 在這裡放入你對每個資料夾實際要執行的操作
    # 例如：複製檔案、轉換格式、分析內容、執行另一個腳本等
    #
    # 範例操作： (請替換成你的實際需求)
    # echo "  模擬：正在處理 $dir_name ..."
    # ls -l "$dir_path" > "$START_DIR/${dir_name}_filelist.txt" # 範例：列出檔案清單
    # sleep 1 # 模擬耗時操作

    # 模擬處理成功：(實際應用中，你需要檢查你的處理指令是否成功)
    process_success=0 # 假設成功 (0 代表成功)
    echo "  (模擬) 處理 '$dir_name' 完成。"

    # ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^
    # ==============================================================

    # 檢查處理結果
    if [ $process_success -eq 0 ]; then
        log_message "成功處理 '$dir_name'。"
        # 只有成功處理後，才將資料夾名稱寫入日誌檔案
        echo "$dir_name" >> "$LOG_FILE"
        sync # 嘗試將緩衝區寫入磁碟，減少中斷時的資料遺失風險
        log_message "已將 '$dir_name' 記錄到 $LOG_FILE。"
        # 將剛處理完的加入 processed_dirs 陣列，供後續最終檢查使用
        processed_dirs+=("$dir_name")
    else
        log_message "錯誤：處理 '$dir_name' 失敗。請檢查相關錯誤訊息。"
        log_message "注意：'$dir_name' 將不會被記錄到日誌檔案，下次執行會重試。"
        all_processed_this_run=0 # 標記此輪執行未完全成功
    fi
    echo "-------------------------------------------"

done

# --- 步驟 5: 最終檢查與寫入完成標記 ---
# 重新讀取日誌檔案，計算真正記錄了多少個資料夾 (避免重複計算記憶體中的)
final_processed_count=0
if [ -f "$LOG_FILE" ]; then
   # 只計算非空行且不是完成標記的行數
   final_processed_count=$(grep -cve '^\s*$' -e "$COMPLETION_MARKER" "$LOG_FILE" || echo 0)
fi

log_message "最終檢查：目標資料夾總數 = $total_target_dirs, 已記錄處理完成數 = $final_processed_count"

if [ "$final_processed_count" -ge "$total_target_dirs" ]; then
    log_message "狀態：所有目標資料夾均已處理並記錄。"
    # 檢查是否已存在完成標記，避免重複寫入
    if ! grep -qFx "$COMPLETION_MARKER" "$LOG_FILE"; then
        log_message "動作：寫入完成標記到 $LOG_FILE..."
        echo "$COMPLETION_MARKER" >> "$LOG_FILE"
        sync
        log_message "-------------------------------------------"
        log_message "      🎉 所有資料夾檢查完畢 🎉        "
        log_message "-------------------------------------------"
    else
        log_message "狀態：完成標記已存在於日誌檔案中。"
    fi
    exit 0 # 成功退出
else
    log_message "-------------------------------------------"
    log_message "警告：腳本執行完畢，但並非所有目標資料夾都已成功處理並記錄。"
    log_message "日誌檔案未標記為完成。下次執行將會繼續處理剩餘的資料夾。"
    log_message "-------------------------------------------"
    exit 1 # 異常退出 (未完成)
fi