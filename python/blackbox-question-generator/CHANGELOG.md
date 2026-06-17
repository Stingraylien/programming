# 版本更新紀錄 (Changelog)

所有關於「黑盒子題庫產生器 (Black Box Question Generator)」的顯著變更紀錄都將記錄於此檔案中。

## [1.0.0] - 2026-03-24 (MVP Release)

### Added (新增功能)
- 【解析核心】完成 Input Adapter，提供 PDF, PPTX, DOCX, MP4 檔案串接與基礎解析框架。
- 【解析核心】開發 Canonical Content 模組，統一將異質來源的文本結構標準化。
- 【出題引擎】實作 Question Generator，結合規則演算法，支援五種旭聯題型出題 (包含是非、單選、複選、填充、問答)。
- 【輸出引擎】開發 XuLink Exporter，將系統內部資料結構轉換匯出成符合旭聯 LMS 系統嚴格規範的 Excel 檔案。
- 【API 服務】建立基於 Flask 框架的 RESTful API，包含系統健康檢查 (`/api/health`)、設定讀取 (`/api/config`)、上傳轉檔與題庫供檔下載端點。
- 【佈署與自動化】配置單元及整合測試框架 (Pytest)、CI/CD 相關自動化腳本 (`Makefile`, `deploy-to-azure.sh`)。
- 【智慧代理】支持 Microsoft 365 Copilot Agent (M365) 集成，並提供 Prompt 範本與 Actions OpenAPI 定義。
