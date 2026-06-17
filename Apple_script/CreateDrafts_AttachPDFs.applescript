-- 將此路徑改成您在 Mac 上的 PDF 資料夾 (已下載/同步的 SharePoint 資料夾)
set pdfFolderPOSIX to "/Users/USERNAME/Downloads/GolfPDFs"
set attachOnlyFirst to false -- 若只想附第一個符合的檔案，改成 true

set recipients to {
    {name:"鄒莉君", email:"tsou.kelly@inventec.com"},
    {name:"蔡岳航", email:"tsai.john@inventec.com"},
    {name:"劉銘宗", email:"liu.martin@inventec.com"},
    {name:"陳曦", email:"chen.sybil@inventec.com"},
    {name:"孟欣薇", email:"meng.doreen@inventec.com"},
    {name:"陳孟甫", email:"chen.taylor@inventec.com"},
    {name:"徐沛文", email:"hsu.kevinpw@inventec.com"},
    {name:"李泰熾", email:"li.ted@inventec.com"},
    {name:"黎思函", email:"li.pear@inventec.com"},
    {name:"張以謙", email:"chang.johnnyic@inventec.com"},
    {name:"汪廣魁", email:"wang.ken@inventec.com"},
    {name:"李書芬", email:"lee.vickysf@inventec.com"},
    {name:"吳榮笙", email:"wu.jasonjs@inventec.com"},
    {name:"劉亭均", email:"liu.astrid@inventec.com"},
    {name:"黃仲瑋", email:"huang.ivancw@inventec.com"},
    {name:"林淑琦", email:"lin.suzanne@inventec.com"},
    {name:"黃冠銓", email:"huang.aaronkc@inventec.com"},
    {name:"陳俊樺", email:"chen.chunhua@inventec.com"},
    {name:"方嘉隆", email:"fang.felix@inventec.com"},
    {name:"殷嘉聰", email:"yin.mark@inventec.com"},
    {name:"鍾秀芸", email:"chung.claire@inventec.com"},
    {name:"孔祥新", email:"kong.jerry@inventec.com"},
    {name:"陳建文", email:"chen.tonycw@inventec.com"},
    {name:"陳俊彥", email:"chen.webb@inventec.com"},
    {name:"黃瑞君", email:"huang.rachel@inventec.com"},
    {name:"高政暐", email:"kao.leocw@inventec.com"},
    {name:"曹祥錞", email:"cao.joe@inventec.com"},
    {name:"蔡秉修", email:"tsai.david@inventec.com"},
    {name:"王自強", email:"wang.johnsontc@inventec.com"},
    {name:"邱宜姿", email:"chiu.lillian@inventec.com"}
}

on replaceText(s, f, r)
    set AppleScript's text item delimiters to f
    set parts to text items of s
    set AppleScript's text item delimiters to r
    set s2 to parts as text
    set AppleScript's text item delimiters to ""
    return s2
end replaceText

on escapeForShell(t)
    set t to my replaceText(t, "'", "'\''")
    return "'" & t & "'"
end escapeForShell

on findMatchingPDFs(nameText, folderPOSIX)
    set escapedName to my escapeForShell(nameText)
    set escapedFolder to my escapeForShell(folderPOSIX)
    set cmd to "find " & escapedFolder & " -type f -iname '*" & nameText & "*.pdf'"
    try
        set resultText to do shell script cmd
        set lines to paragraphs of resultText
        return lines
    on error
        return {}
    end try
end findMatchingPDFs

-- 建立草稿並附檔
tell application "Microsoft Outlook"
    repeat with rec in recipients
        set nameText to name of rec
        set emailText to email of rec
        set matchedPaths to my findMatchingPDFs(nameText, pdfFolderPOSIX)
        set msg to make new outgoing message with properties {subject:"【完訓證書通知】橫向管理高爾夫", content:"親愛的同仁，您好：

恭喜您完成『橫向管理高爾夫實戰訓練』，附件為您的完訓證書 PDF。
如需更正姓名或內容，請於3日內回覆本信。

訓練暨員工關係部 敬上"}
        make new recipient at msg with properties {email address:{address:emailText}}
        if matchedPaths is not {} then
            if attachOnlyFirst then
                set p to item 1 of matchedPaths
                set f to POSIX file p
                try
                    make new attachment at msg with properties {file:f}
                end try
            else
                repeat with p in matchedPaths
                    try
                        set f to POSIX file p
                        make new attachment at msg with properties {file:f}
                    end try
                end repeat
            end if
        end if
        save msg
    end repeat
end tell
