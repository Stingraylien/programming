# 版本更新紀錄 (Changelog)

所有關於「派遣人員匯入 elearning 系統轉換程式」的顯著變更紀錄都將記錄於此檔案中。

## [Unreleased] / [Initial Release]

### Added (新增功能)
- 實作 Tkinter GUI 操作介面，提供「到職匯入」、「離職匯入」與「離開」按鈕整合操作。
- 支援讀取常見試算表格式：`.xlsx`, `.xls`, `.csv`。
- 實作到職人員轉換邏輯：從特定列數讀取欄位，映射為 e-learning 格式。
- 實作離職人員轉換邏輯：自動將產出規格中 `IsDisabled` 欄位註記為 1。
- 產出檔案自動加上當前日期與時間之前綴（例：`YYYYMMDD_HHMMSS_到職人員.csv`），避免檔案覆蓋。
- 建立專案相關說明文件（README, 使用者手冊, 開發指南）。
