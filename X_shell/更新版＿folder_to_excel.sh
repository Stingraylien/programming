#!/bin/bash

# 讓使用者選擇資料夾
folder_path=$(osascript -e 'tell application "System Events"
    activate
    set folderPath to choose folder with prompt "請選擇要處理的資料夾："
    set posixPath to POSIX path of folderPath
end tell')

# 檢查是否已選擇資料夾
if [ -z "$folder_path" ]; then
    echo "未選擇資料夾，程式結束"
    exit 1
fi

# 設定輸出的 CSV 檔案路徑（與選擇的資料夾同層級）
output_file="${folder_path%/}/檔案清單.csv"

# 建立 CSV 檔案並寫入標題
echo "檔案名稱" > "$output_file"

# 列出資料夾中的檔案名稱並寫入 CSV
find "$folder_path" -type f -maxdepth 1 | while read file; do
    filename=$(basename "$file")
    echo "$filename" >> "$output_file"
done

# 轉換 CSV 為 Excel 格式並確保正確關閉
osascript <<EOD
tell application "Microsoft Excel"
    activate
    set newWorkbook to make new workbook
    set csvFile to POSIX file "$output_file"
    open text file csvFile
    tell active sheet
        set used range's column width to 50
    end tell
    save active workbook
    quit
end tell
EOD

# 刪除暫存的 CSV 檔案
rm "$output_file"

echo "完成！檔案清單已匯出。"
exit 0