# 實作計畫：產生 PPT、MP4 和純文字摘要

## 目標描述 (Goal Description)
擴充 `黑盒子產出完全教材`，使用者先輸入課程名稱，之後接收輸入檔案 (docx, pdf 等) 時，產出以下成果

1. **摘要 PPTX**：一份總結課程內容的投影片簡報。
2. **MP4 影片**： 以 項目 1 的投影片為基底，錄製一個使用 H.264 編碼的影片，結合重點摘要投影片及語音旁白，用旁白語音解說 **摘要 PPTX**內容
3.  **考題**（且符合 `旭聯平台考題範本.xlsx` 規範）。使用者可自由選擇是非題、單選題、多選題、填充題等題型，系統可以對題數提出建議，但題數最低要有 20 題 。 ‘黑盒子參考指南.md’ 提供了考題的範本以及格式
4. **TXT 摘要檔案**：包含「課程名稱」、「課程目標」和「課程大綱」的純文字檔。
5 依照課程名稱與課程內容，生成一張封面圖片

## 需要使用者確認的事項 (User Review Required)
> [!IMPORTANT]
> **依賴套件庫**：實作 MP4 與語音生成會需要外部套件，例如 `python-pptx` (簡報)、`edge-tts` (語音生成旁白) 以及 `moviepy` (將相依於 `ffmpeg` 進行影片合成)，請問是否同意將這些新增到 [requirements.txt](file:///Users/wei-xianglien/Library/CloudStorage/OneDrive-InventecCorp/programming/python/requirements.txt) 中？

## 提議的變更 (Proposed Changes)

---

### API 與輸入層 (API & Input Layer)
更新進入點，以接收並處理新的欄位。
#### [MODIFY] `api/main.py` (或其他相關的 API/CLI 進入點)
- 新增 `course_name` 為必填的輸入參數。
- 協調新的資料流程式：正規化內容提取 -> 產出考題 -> 產出純文字 (TXT) -> 產出簡報 (PPT) -> 產出簡報解說影片 (MP4) -> 產出旭聯格式 Excel。

---

### 純文字摘要生成模組 (TXT Summary Generator)
建立一個用來產生簡單文字檔的模組。
#### [NEW] `src/summary_exporter/text_exporter.py`
- 接收正規化內容 (Canonical Context) 與 `course_name`。
- 提取或推斷「課程目標」與「課程大綱」。
- 將內容寫入 [.txt](file:///Users/wei-xianglien/Library/CloudStorage/OneDrive-InventecCorp/programming/python/requirements.txt) 檔案。

---

### 考題產生器限制 (Question Generator Constraints)
確保精準產出最低 20  題考題以符合 MP4 語音及 Excel 規範。
#### [MODIFY] `src/question_generator/` (Engine)
- 若目標輸出包含影片格式，限制必須產生剛好 20 題。
- 確保考題格式嚴格符合 `旭聯平台考題範本.xlsx` 標準規則。

---

### PPT 生成模組 (PPT Generator)
#### [NEW] `src/ppt_generator/ppt_builder.py`
- 使用 `python-pptx` 從正規化內容生成重點摘要的投影片。
- 

---

### 影片與音訊生成模組 (Video & Audio Generator)
#### [NEW] `src/video_generator/video_builder.py`
- **TTS 語音層**：使用 Text-to-Speech 套件（例如 `edge-tts`）生成重點摘要與重點摘要的投影片，並且結合語音旁白解說
- **影片合成**：將 PPT 投影片轉換為圖片，接著利用 `moviepy`（使用 `h264` 編碼）將投影片影像與 TTS 音頻同步，輸出為 MP4 影片檔。

依照課程名稱與課程內容，生成一張封面圖片

## 驗證計畫 (Verification Plan)

### 自動化測試 (Automated Tests)
- 測試正規化內容提取邏輯，驗證「課程目標」與「課程大綱」正確擷取並格式化為 TXT。
- 更新 `make test-api`（專案中的現有測試），以覆蓋新的 `course_name` 參數。
- 對影片生成器進行 Mock 測試，確保以 `h.264` 選項呼叫 `ffmpeg`，避免單元測試耗費大量時間渲染影片。

### 人工驗證 (Manual Verification)
1. 透過 CLI 或 API 提供一個測試用 `.docx` 檔案，並傳入「範例課程 101」作為課程名稱。
2. 驗證產出物：
   - `summary.txt` 正確包含名稱、目標與大綱。
   - `presentation.pptx` 包含課程重點摘要
   - `video.mp4` 以課程重點摘要的投影片製作 h.264 格式的 mp4 檔案，並且能夠在標準播放器中順利播放（H.264 編碼），並且能聽見正確語音旁白，語音旁白與投影片內容相關。
   - `training_question_bank.xlsx` 格式正確無誤。
   - '封面圖片.jpg' 包含課程名稱 並且根據課程名稱與課程內容產出一張有代表性的封面圖片
