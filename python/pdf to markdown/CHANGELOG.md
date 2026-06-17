# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to Semantic Versioning.

## [Unreleased]

## [1.2.0] - 2026-04-25
### Changed
- **Refactoring:** 根據 `my_coding_style.md` 規範，全面重構 `pdf_to_md_converter.py` 的程式碼。
- **Variable Naming:** 替換所有變數名稱，強制加入嚴格的資料型態前綴（如 `int_`, `str_`, `ui_`, `list_`）。
- **Documentation:** 為每一行程式碼加入詳細、口語化且對齊的中文註解，大幅提升未來可維護性與可讀性。
- **Documentation:** 新增四大標準說明文件（README、使用者操作手冊、開發環境建置指南、CHANGELOG），滿足專案規範。

## [1.1.0] - 2026-04-25
### Added
- **UI Enhancement:** 新增即時進度條 (`QProgressBar`)。
- **UI Enhancement:** 新增即時統計數據 (`QLabel`)，可顯示 `Total`、`Completed` 與 `Remaining` 的檔案數量。
### Changed
- **Threading Logic:** 實作跨執行緒的安全信號傳遞 (`WorkerSignals`) 以即時更新 UI 畫面而不發生凍結。

## [1.0.0] - 2026-04-25
### Added
- 初始版本釋出。
- 實作基於 PySide6 的圖形化介面。
- 實作基於 `pymupdf4llm` 的 PDF 轉 Markdown 核心轉換邏輯。
- 實作選擇資料夾後，自動遞迴尋找 `.pdf` 檔案的功能。
