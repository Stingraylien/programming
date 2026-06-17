-- MP4 重複檔案檢測和刪除腳本（Shell 優化版）
-- 使用 shell script 避免 Finder 逾時問題

-- 選擇要檢查的資料夾
set targetFolder to choose folder with prompt "請選擇要檢查重複 mp4 檔案的資料夾："
set folderPath to POSIX path of targetFolder

-- 使用 shell script 獲取所有 mp4 檔案
try
	set mp4FilesList to do shell script "find " & quoted form of folderPath & " -maxdepth 1 -name '*.mp4' -type f"
	
	if mp4FilesList is "" then
		display dialog "在選擇的資料夾中沒有找到 mp4 檔案。" buttons {"確定"} default button 1
		return
	end if
	
	-- 將檔案清單轉換為列表
	set mp4Files to paragraphs of mp4FilesList
	set totalFiles to count of mp4Files
	
on error
	display dialog "無法讀取資料夾內容，請確認資料夾權限。" buttons {"確定"} default button 1
	return
end try

display dialog "找到 " & totalFiles & " 個 mp4 檔案，開始分析..." buttons {"開始"} default button 1

-- 步驟1：使用 shell script 獲取檔案大小和建立檔案資訊
set fileInfoScript to "
for file in " & quoted form of folderPath & "*.mp4; do
    if [ -f \"$file\" ]; then
        size=$(stat -f%z \"$file\" 2>/dev/null || stat -c%s \"$file\" 2>/dev/null)
        basename=$(basename \"$file\")
        echo \"$file|$size|$basename\"
    fi
done
"

try
	set fileInfoOutput to do shell script fileInfoScript
	if fileInfoOutput is "" then
		display dialog "無法獲取檔案資訊。" buttons {"確定"} default button 1
		return
	end if
	
	set fileInfoLines to paragraphs of fileInfoOutput
on error
	display dialog "分析檔案時發生錯誤，請檢查檔案權限。" buttons {"確定"} default button 1
	return
end try

-- 步驟2：按檔案大小分組
set sizeGroups to {}
repeat with fileInfoLine in fileInfoLines
	if fileInfoLine is not "" then
		set AppleScript's text item delimiters to "|"
		set fileInfoParts to text items of fileInfoLine
		set AppleScript's text item delimiters to ""
		
		if (count of fileInfoParts) ≥ 3 then
			set filePath to item 1 of fileInfoParts
			set fileSize to item 2 of fileInfoParts
			set fileName to item 3 of fileInfoParts
			
			-- 尋找相同大小的分組
			set foundGroup to false
			repeat with j from 1 to count of sizeGroups
				set currentGroup to item j of sizeGroups
				set groupSize to item 1 of currentGroup
				if groupSize = fileSize then
					set groupFiles to item 2 of currentGroup
					set end of groupFiles to {filePath, fileName}
					set item j of sizeGroups to {groupSize, groupFiles}
					set foundGroup to true
					exit repeat
				end if
			end repeat
			
			if not foundGroup then
				set end of sizeGroups to {fileSize, {{filePath, fileName}}}
			end if
		end if
	end if
end repeat

-- 步驟3：只對有多個檔案的分組計算 MD5
set duplicateGroups to {}
set groupsToCheck to 0

-- 計算需要檢查的分組數量
repeat with sizeGroup in sizeGroups
	set groupFiles to item 2 of sizeGroup
	if (count of groupFiles) > 1 then
		set groupsToCheck to groupsToCheck + 1
	end if
end repeat

if groupsToCheck = 0 then
	display dialog "沒有找到相同大小的檔案，因此沒有重複檔案。" buttons {"確定"} default button 1
	return
end if

display dialog "找到 " & groupsToCheck & " 組相同大小的檔案，開始檢查內容..." buttons {"繼續"} default button 1

set currentGroupNum to 0

repeat with sizeGroup in sizeGroups
	set groupSize to item 1 of sizeGroup
	set groupFiles to item 2 of sizeGroup
	
	-- 只處理有多個檔案的分組
	if (count of groupFiles) > 1 then
		set currentGroupNum to currentGroupNum + 1
		
		-- 建立 MD5 計算腳本
		set md5Script to ""
		repeat with fileInfo in groupFiles
			set filePath to item 1 of fileInfo
			set md5Script to md5Script & "echo \"" & filePath & "|$(md5 -q " & quoted form of filePath & " 2>/dev/null || echo ERROR)\"" & return
		end repeat
		
		try
			set md5Output to do shell script md5Script
			set md5Lines to paragraphs of md5Output
			
			-- 解析 MD5 結果
			set fileHashes to {}
			repeat with md5Line in md5Lines
				if md5Line is not "" then
					set AppleScript's text item delimiters to "|"
					set md5Parts to text items of md5Line
					set AppleScript's text item delimiters to ""
					
					if (count of md5Parts) = 2 then
						set filePath to item 1 of md5Parts
						set md5Hash to item 2 of md5Parts
						
						-- 找到對應的檔案名稱
						repeat with fileInfo in groupFiles
							if (item 1 of fileInfo) = filePath then
								set fileName to item 2 of fileInfo
								set end of fileHashes to {filePath, fileName, md5Hash}
								exit repeat
							end if
						end repeat
					end if
				end if
			end repeat
			
			-- 在這組中尋找重複的 MD5
			set processedHashes to {}
			repeat with i from 1 to count of fileHashes
				set currentHashInfo to item i of fileHashes
				set currentHash to item 3 of currentHashInfo
				
				if currentHash is not in processedHashes and currentHash is not "ERROR" then
					set matchingFiles to {}
					
					repeat with j from 1 to count of fileHashes
						set compareHashInfo to item j of fileHashes
						set compareHash to item 3 of compareHashInfo
						if currentHash = compareHash then
							set compareFileName to item 2 of compareHashInfo
							set end of matchingFiles to compareFileName
						end if
					end repeat
					
					if (count of matchingFiles) > 1 then
						set end of duplicateGroups to matchingFiles
					end if
					
					set end of processedHashes to currentHash
				end if
			end repeat
			
		on error
			-- MD5 計算失敗，跳過這組
		end try
	end if
end repeat

-- 顯示結果和處理重複檔案
if (count of duplicateGroups) = 0 then
	display dialog "沒有找到重複的 mp4 檔案。" buttons {"確定"} default button 1
else
	set resultText to "找到 " & (count of duplicateGroups) & " 組重複檔案：" & return & return
	set totalDuplicates to 0
	
	repeat with i from 1 to count of duplicateGroups
		set duplicateGroup to item i of duplicateGroups
		set resultText to resultText & "重複組 " & i & "：" & return
		
		repeat with j from 1 to count of duplicateGroup
			set fileName to item j of duplicateGroup
			set resultText to resultText & "  • " & fileName & return
		end repeat
		set resultText to resultText & return
		set totalDuplicates to totalDuplicates + (count of duplicateGroup) - 1
	end repeat
	
	set resultText to resultText & "總共可刪除 " & totalDuplicates & " 個重複檔案（每組保留第一個檔案）"
	
	-- 顯示結果對話框
	set buttonChoice to display dialog resultText buttons {"刪除重複檔案", "僅檢視", "取消"} default button 2 with icon caution
	
	if button returned of buttonChoice is "刪除重複檔案" then
		-- 再次確認刪除操作
		set confirmText to "⚠️ 警告：即將刪除 " & totalDuplicates & " 個重複檔案！" & return & return & "每組重複檔案將保留第一個，其餘移至垃圾桶。" & return & return & "此操作無法復原，確定要繼續嗎？"
		set confirmChoice to display dialog confirmText buttons {"確定刪除", "取消"} default button 2 with icon stop
		
		if button returned of confirmChoice is "確定刪除" then
			set deletedCount to 0
			set errorCount to 0
			set errorMessages to ""
			
			-- 建立刪除腳本
			set deleteScript to ""
			repeat with i from 1 to count of duplicateGroups
				set duplicateGroup to item i of duplicateGroups
				
				-- 從第二個檔案開始刪除，保留第一個
				repeat with j from 2 to count of duplicateGroup
					set fileNameToDelete to item j of duplicateGroup
					set fullPath to folderPath & fileNameToDelete
					set deleteScript to deleteScript & "if [ -f " & quoted form of fullPath & " ]; then mv " & quoted form of fullPath & " ~/.Trash/ && echo 'SUCCESS:" & fileNameToDelete & "' || echo 'ERROR:" & fileNameToDelete & "'; fi" & return
				end repeat
			end repeat
			
			-- 執行刪除操作
			try
				set deleteResult to do shell script deleteScript
				set resultLines to paragraphs of deleteResult
				
				repeat with resultLine in resultLines
					if resultLine starts with "SUCCESS:" then
						set deletedCount to deletedCount + 1
					else if resultLine starts with "ERROR:" then
						set errorCount to errorCount + 1
						set errorMessages to errorMessages & "• " & (text 7 thru -1 of resultLine) & return
					end if
				end repeat
				
			on error errorMsg
				set errorCount to errorCount + 1
				set errorMessages to errorMessages & "• 刪除操作失敗：" & errorMsg & return
			end try
			
			-- 顯示刪除結果
			set resultMessage to "刪除操作完成！" & return & return
			set resultMessage to resultMessage & "成功刪除：" & deletedCount & " 個檔案" & return
			if errorCount > 0 then
				set resultMessage to resultMessage & "刪除失敗：" & errorCount & " 個檔案" & return & return & "錯誤詳情：" & return & errorMessages
			end if
			
			display dialog resultMessage buttons {"在 Finder 中顯示", "確定"} default button 2
			
			if button returned of result is "在 Finder 中顯示" then
				tell application "Finder"
					open targetFolder
					activate
				end tell
			end if
		end if
		
	else if button returned of buttonChoice is "僅檢視" then
		-- 提供檢視選項
		set viewChoice to display dialog resultText buttons {"在 Finder 中顯示資料夾", "儲存報告", "確定"} default button 3
		
		if button returned of viewChoice is "在 Finder 中顯示資料夾" then
			tell application "Finder"
				open targetFolder
				activate
			end tell
		else if button returned of viewChoice is "儲存報告" then
			-- 儲存報告到桌面
			set desktopPath to POSIX path of (path to desktop)
			set reportPath to desktopPath & "MP4重複檔案報告.txt"
			try
				do shell script "echo " & quoted form of resultText & " > " & quoted form of reportPath
				display dialog "報告已儲存到桌面：MP4重複檔案報告.txt" buttons {"確定"} default button 1
			on error
				display dialog "儲存報告時發生錯誤。" buttons {"確定"} default button 1
			end try
		end if
	end if
end if