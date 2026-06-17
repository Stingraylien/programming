ARCHITECTURE.md — 黑盒子架構（Black Box Architecture）

目的：將「教材 → 出題 → 旭聯題庫 Excel」流程，封裝為可由 Microsoft 365 Copilot Agent 呼叫的後端能力，並以 VS Code + Microsoft 365 Agents Toolkit 進行開發與維護。


使用方式（方案 A）：

本檔案請直接存放於 VS Code 專案根目錄
檔名建議為：ARCHITECTURE.md作為工程設計說明與對內溝通文件


1. 架構總覽
┌─────────────────────────────────────────────┐
│        Microsoft 365 Copilot / Teams        │
│  (使用者上傳教材、下指令、下載結果)        │
└───────────────┬─────────────────────────────┘
                │  (Agent 呼叫)
┌───────────────▼─────────────────────────────┐
│        Copilot Agent（VS Code）              │
│  - Prompt Contract                           │
│  - 檔案接收與參數驗證                         │
│  - 後端 API Orchestration                    │
└───────────────┬─────────────────────────────┘
                │  (HTTP / REST)
┌───────────────▼─────────────────────────────┐
│        黑盒子核心服務（Black Box API）      │
│  1) Input Adapter                            │
│  2) Canonical Content                        │
│  3) Question Generator                       │
│  4) XuLink Exporter                          │
└───────────────┬─────────────────────────────┘
                │
┌───────────────▼─────────────────────────────┐
│        輸出：旭聯題庫 Excel (.xlsx)         │
└─────────────────────────────────────────────┘




2. 黑盒子模組說明
2.1 Input Adapter（輸入轉換）
職責：

接收多種教材格式並轉為可處理的中介資料
支援格式（可逐步擴充）：

pdfpptxdocxmp4（字幕 / 語音轉文字後處理）
輸出資料結構（範例）：
{
  "source_type": "pptx",
  "sections": [
    {
      "title": "Chapter 1",
      "content": "..."
    }
  ]
}




2.2 Canonical Content（標準化內容層）
職責：

將不同來源的文字內容統一為「章節 / 學習目標 / 段落」結構
去除重複內容、標準化術語
資料結構（範例）：
{
  "chapter": "Network Basics",
  "learning_objectives": [
    "Understand TCP/IP",
    "Know OSI layers"
  ],
  "paragraphs": ["...", "..."]
}




2.3 Question Generator（出題引擎）
職責：

根據 Canonical Content 產生題目資料（尚未是 Excel）
嚴格對齊旭聯題庫規格（題型、難度、權重）
策略模式（Strategy Pattern）：

rule_based：規則式出題（不依賴 AI）
ai_assisted：AI 輔助出題（可選 Azure OpenAI / Copilot 能力）
支援題型：

是非題（True / False）
單選題（Single Choice）
複選題（Multiple Choice）
填充題（Fill in the Blank）
問答題（Essay）


2.4 XuLink Exporter（旭聯題庫匯出器）
職責：

將題目資料轉為 旭聯 LMS 可匯入的 Excel 格式
確保欄位順序、題型代碼、答案標記完全正確
輸出結果：

training_question_bank.xlsx3. Copilot Agent 與黑盒子之間的契約（API Contract）
3.1 API Endpoint（範例）
POST /api/generate-question-bank
Content-Type: multipart/form-data


3.2 Request

教材檔案：pdf / pptx / docx / mp4參數（JSON）：
{
  "question_types": ["single", "true_false"],
  "difficulty": "medium",
  "language": "zh-TW",
  "output_format": "xulink_excel"
}


3.3 Response
{
  "status": "success",
  "download_url": "https://.../training_question_bank.xlsx"
}




4. VS Code 專案建議結構
blackbox-question-generator/
├─ agent/                      # Copilot Agent 定義
│  ├─ prompt.md                # Prompt Contract
│  └─ actions.yaml             # Agent Actions
├─ src/
│  ├─ input_adapter/
│  ├─ canonical_content/
│  ├─ question_generator/
│  └─ xulink_exporter/
├─ api/
│  └─ main.py / index.ts        # HTTP API Entry
├─ tests/
├─ README.md
└─ ARCHITECTURE.md              # ← 本文件（方案 A）




5. 設計原則（Design Principles）

Agent ≠ 商業邏輯：Copilot Agent 僅負責入口、權限與流程編排
黑盒子為唯一核心：所有出題邏輯集中於後端服務
可重用性：可被 Copilot、Power Automate、API 呼叫
可治理性：符合 Microsoft 365 企業資料保護與審計需求
可演進性：輸入格式、出題策略可獨立擴充


6. 使用情境（Example）
@旭聯題庫產生器
請根據我上傳的 PPT 與 PDF，
產生可匯入旭聯的考題 Excel，
題型包含是非與單選題。


→ Copilot Agent 呼叫黑盒子 API → 回傳 .xlsx✅ 本文件為 方案 A（ARCHITECTURE.md）正式版，
適合直接納入 VS Code 專案並進行版本控管。