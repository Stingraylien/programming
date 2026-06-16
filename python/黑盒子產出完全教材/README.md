# 黑盒子題庫產生器 (Black Box Question Generator)

## 簡介
黑盒子題庫產生器是一個後端 API 服務與工具，能夠自動處理各種教材格式（如 PDF、PPTX、DOCX、MP4、TXT），並透過智能內容提取與規則式出題，自動生成符合「旭聯 LMS 系統」規格的題庫 Excel 檔案。除題庫外，亦可一併產出教材摘要、簡報、封面圖與教學影片等多種衍生產物。

## 檔案結構與模組
- `api/main.py`: Flask RESTful API 進入點（含 GUI 前端頁面 `api/templates/index.html`）。
- `src/input_adapter/`: 負責解析多種輸入格式的配接器。
- `src/canonical_content/`: 負責將文本標準化（章節、學習目標、段落）。
- `src/question_generator/`: 出題引擎（支援是非、單選、複選、填充、問答）。
- `src/xulink_exporter/`: 將題目輸出為旭聯 Excel 格式的模組。
- `src/translation/`: 多語系文字翻譯（`translate_text`）。
- `src/summary_exporter/`: 教材文字摘要輸出（`export_text_summary`）。
- `src/ppt_generator/`: 教材摘要簡報產生（`build_summary_ppt`）。
- `src/image_generator/`: 封面圖產生（`generate_cover_image`，含漸層背景與中文字型）。
- `src/video_generator/`: 教學影片產生（`generate_video`，含 TTS 語音與投影片渲染）。
- `使用者操作手冊.md`: 針對 API 呼叫者與端點測試的使用教學。
- `開發環境建置指南.md`: 針對開發人員的環境設定與本機運行教學。

## 功能特色
- **多格式輸入支持**: 支援 PDF、PPTX、DOCX、MP4（含字幕）、TXT 等主流教材格式。
- **五種題型生成**: 是非題、單選題、複選題、填充題、問答題。
- **多元產物輸出**: 題庫 Excel、文字摘要、簡報（PPTX）、封面圖、教學影片。
- **多語系支援**: 內建翻譯模組，可將教材內容轉換為多種語言。
- **智能內容標準化**: 自動提取章節、學習目標、段落。
- **規則式防呆出題**: 確保生成的題目完全符合旭聯規格。
- **RESTful API + GUI**: 提供 API 端點與網頁前端，易於與 Microsoft 365 Copilot Agent 等系統整合串接。

*(註：原英文版詳細架構文件與快速啟動指南，已統整分散至其餘說明文件中)*