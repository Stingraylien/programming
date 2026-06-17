# 黑盒子題庫產生器 (Black Box Question Generator)

## 簡介
黑盒子題庫產生器是一個強大的後端 API 服務與工具，能夠自動處理各種教材格式（如 PDF、PPTX、DOCX、MP4），並透過智能內容提取與規則式出題，自動生成符合「旭聯 LMS 系統」規格的題庫 Excel 檔案。

## 檔案結構與模組
- `api/main.py`: Flask RESTful API 進入點。
- `src/input_adapter/`: 負責解析多種輸入格式的配接器。
- `src/canonical_content/`: 負責將文本標準化。
- `src/question_generator/`: 出題引擎（支援是非、單選、複選、填充、問答）。
- `src/xulink_exporter/`: 將題目輸出為旭聯 Excel 格式的模組。
- `使用者操作手冊.md`: 針對 API 呼叫者與端點測試的使用教學。
- `開發環境建置指南.md`: 針對開發人員的環境設定與本機運行教學。

## 功能特色
- **多格式輸入支持**: 支援 PDF、PPTX、DOCX、MP4（含字幕）等主流教材格式。
- **五種題型生成**: 是非題、單選題、複選題、填充題、問答題。
- **智能內容標準化**: 自動提取章節、學習目標、段落。
- **規則式防呆出題**: 確保生成的題目完全符合旭聯規格。
- **RESTful API 架構**: 易於與其他前端系統或 Microsoft 365 Copilot Agent 進行整合串接。

*(註：原英文版詳細架構文件與快速啟動指南，已統整分散至其餘說明文件中)*