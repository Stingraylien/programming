# 專案開發與寫作規範 (Coding Style & Documentation Guidelines)

本文件定義了我在 Python 開發專案中的核心編碼風格、架構原則以及必須產出的標準說明文件，以確保所有專案都具備極高的可讀性、一致性與可維護性。未來不論是個人開發、團隊接手協作或是請 AI 助手協助，都請務必遵循此規範。

---

## 1. 程式碼撰寫規範 (Coding Style)

- **嚴格的型態前綴 (Type Prefix)**：
  所有的變數命名必須加上明確的資料型態前綴（例如: `str_name` 代表字串, `list_data` 代表清單/陣列, `df_excel` 代表 Pandas DataFrame, `int_count` 代表整數, `root_` / `tk_` 代表 GUI 元件等）。
- **對齊的詳盡註解 (Detailed Aligned Comments)**：
  程式碼的「每一列」最右側，都盡可能必須有詳細且用詞白話的對齊 `# 註解`，以利完全不懂程式的非技術人員或未來的接手者能夠一行一行讀懂業務邏輯。
- **動態路徑處理 (Dynamic Path Handling)**：
  絕對避免將任何個人電腦的實體硬碟路徑寫死 (Hardcode)。應優先使用圖形化套件 (例如 `tkinter.filedialog.askopenfilename`) 讓使用者在執行時動態選取檔案，或是使用 `os.path` / `pathlib` 來處理相對路徑與目錄創建。

---

## 2. 專案標準文件要求 (Required Documentation)

任何一個完整的工具專案或是服務，在開發或重構完畢後，**必須**產出以下四份標準說明文件，並直接存放於專案根目錄中：

1. **`README.md` (入口文件)**
   - 專案簡介、解決了什麼痛點、核心功能總覽、快速啟動指令。
2. **`使用者操作手冊.md` (User Guide)**
   - 針對終端使用者 (如 HR 人員、出題老師、業務單位) 的操作手冊。必須使用極度白話的步驟式教學 (例如：第一步點擊這個、第二步選取檔案)，並且說明可能的錯誤警告及產出檔案的位置。
3. **`開發環境建置指南.md` (Developer Guide)**
   - 紀錄下此專案的 Python 開發環境建立流程、所需的 pip 相依套件 (或附上 `requirements.txt`)、以及如何使用打包工具 (如 PyInstaller) 將專案封裝為獨立執行檔的指令。
4. **`CHANGELOG.md` (版本更新紀錄)**
   - 紀錄各版本的開發歷程、新增功能、修改邏輯與修復事項 (遵從 Keep a Changelog 格式，例如註明 `Added`, `Changed`, `Fixed`)。

---

## 3. 架構與防呆設計原則 (Architecture & Foolproofing Rules)

- **使用者體驗 (GUI & UX)**：
  只要是給非技術人員使用的工具，盡量提供簡單直覺的使用者介面 (例如 Tkinter splash screen 開場畫面、按鈕選單)。
- **堅固的錯誤處理 (Error Handling & User Prompt)**：
  使用 `try...except` 捕捉各種預期的錯誤（例如：來源檔案格式不符、必填欄位空白、檔案正被其他軟體開啟佔用）。發生錯誤時，應善用友善的彈跳視窗 (`messagebox.showwarning`) 提示使用者問題發生在哪裡，而不應讓程式在背景無效崩潰。
- **產出隔離與日誌紀錄 (Output Management)**：
  將系統的產出結果進行妥善隔離分類。例如將轉換成功的檔案自動建立/搬移至 `output/` 資料夾，而將含有錯誤或邏輯不合規的資料，產生彙整報告並放置於 `failed/` 或 `logs/` 資料夾中。