# Copilot Studio 配置指南

本文檔說明如何在 Microsoft Copilot Studio 中配置與集成 Black Box Question Generator API。

---

## 前置條件

✅ Flask API 已部署到 Azure  
✅ API URL 已獲得（例如：`https://my-app.azurewebsites.net`）  
✅ API 金鑰已獲得  
✅ 擁有公司 Microsoft 365 組織的存取權  
✅ Copilot Studio 存取權限

---

## 第 1 步：登入 Copilot Studio

1. 進入 [Copilot Studio](https://copilotstudio.microsoft.com)
2. 使用公司 Microsoft 365 帳號登入
3. 選擇公司組織

---

## 第 2 步：建立新 Copilot

1. 點擊 **+ 新建** → **Copilot**
2. 填寫基本信息：
   - **名稱**: 題目生成助手
   - **說明**: 協助教師快速生成考試題目（支持 PDF、PPT、Word）
   - **語言**: 繁體中文
3. 點擊 **建立**

---

## 第 3 步：配置 API 連接

### 3.1 添加 REST API 連接

1. 在左側菜單找到 **插件**
2. 點擊 **+ 添加操作** → **REST API**
3. 填寫連接詳細資訊：

```
連接名稱: Question Generator API
基本 URL: https://my-app.azurewebsites.net    ← 替換為您的 API URL
認證類型: API 金鑰
位置: Header
參數名稱: Authorization
參數值: Bearer <您的 API 金鑰>              ← 替換為您的 API 金鑰
```

4. 點擊 **連接** 後 **測試連接**

---

## 第 4 步：定義 API 操作

在 REST API 連接中定義以下 4 個操作：

### 操作 1：健康檢查

```
Operation ID: HealthCheck
HTTP 方法: GET
相對路徑: /api/health
說明: 檢查 API 服務狀態

回應示例:
{
  "status": "healthy",
  "timestamp": "2026-03-24T13:12:29.757985"
}
```

### 操作 2：獲取配置

```
Operation ID: GetConfig
HTTP 方法: GET
相對路徑: /api/config
說明: 獲取支持的題型、難度和語言

回應示例:
{
  "supported_question_types": ["true_false", "single_choice", ...],
  "supported_difficulties": ["easy", "medium", "hard"],
  "supported_languages": ["zh-TW", "en-US"],
  "supported_formats": ["pdf", "pptx", "docx", "txt"],
  "version": "1.0.0"
}
```

### 操作 3：生成題目

```
Operation ID: GenerateQuestions
HTTP 方法: POST
相對路徑: /api/generate-question-bank
說明: 生成考試題目並輸出 Excel

請求體:
{
  "materials": [file],              // 上傳的檔案
  "question_count": 10,             // 題目數量
  "question_types": [               // 題型陣列
    "true_false",
    "single_choice"
  ],
  "difficulty": "medium",           // 難度: easy/medium/hard
  "language": "zh-TW"               // 語言: zh-TW/en-US
}

回應示例:
{
  "status": "success",
  "message": "Successfully generated 10 questions",
  "question_count": 10,
  "output_file": "training_question_bank_20260324_131200.xlsx",
  "download_url": "/api/download/training_question_bank_20260324_131200.xlsx"
}
```

### 操作 4：下載檔案

```
Operation ID: DownloadFile
HTTP 方法: GET
相對路徑: /api/download/{filename}
說明: 下載生成的 Excel 檔案

參數:
- filename: 要下載的檔案名稱

回應: Binary (Excel 檔案)
```

---

## 第 5 步：建立對話流程

### 5.1 開始對話流程

1. 進入 Copilot Studio 中的**主對話主題**
2. 編輯歡迎訊息：

```
歡迎訊息:
"👋 歡迎使用題目生成助手！

我可以幫助您快速生成考試題目。

📝 支持的檔案格式:
  • PDF 文件
  • PowerPoint 演示文稿
  • Word 文檔
  • 純文本檔案

請上傳您的教學材料，我會幫您生成相應的題目。"
```

### 5.2 設定使用者輸入節點

在對話流程中按順序添加以下節點：

#### 節點 1：檔案上傳
```
提示: "請上傳您的教學材料（PDF、PPT、Word 或 TXT）"
動作: 等待檔案輸入
變數: materials (File)
```

#### 節點 2：題目數量
```
提示: "需要生成多少道題目？（建議 5-20 道）"
動作: 等待用戶輸入
變數: question_count (Number)
預設值: 10
驗證: 5-50 之間
```

#### 節點 3：選擇題型
```
提示: "選擇要生成的題型:"
動作: 提供多選選項
選項:
  ☐ 是非題 (true_false)
  ☐ 單選題 (single_choice)
  ☐ 複選題 (multiple_choice)
  ☐ 填空題 (fill_in_blank)
  ☐ 申論題 (essay)
預設: [ 是非題, 單選題 ]
變數: question_types (Array)
```

#### 節點 4：選擇難度
```
提示: "選擇試題難度:"
動作: 提供單選選項
選項:
  ○ 簡單 (easy)
  ○ 中等 (medium)      ← 推薦
  ○ 困難 (hard)
預設: medium
變數: difficulty (Choice)
```

#### 節點 5：確認語言
```
提示: "選擇輸出語言:"
動作: 提供單選選項
選項:
  ○ 繁體中文 (zh-TW)   ← 推薦
  ○ English (en-US)
預設: zh-TW
變數: language (Choice)
```

#### 節點 6：確認摘要
```
訊息: "準備生成題目，請確認信息:

📁 檔案已上傳
📊 數量: {question_count} 道
🎯 題型: {question_types}
💪 難度: {difficulty}
🌐 語言: {language}

確認無誤，即將生成..."

動作: 無需用戶確認，直接進行
```

#### 節點 7：調用 API
```
動作: 調用 GenerateQuestions
參數映射:
  - materials → {materials}
  - question_count → {question_count}
  - question_types → {question_types}
  - difficulty → {difficulty}
  - language → {language}

儲存回應到變數: generateResponse
```

#### 節點 8：顯示結果
```
條件: 如果 generateResponse.status == "success"

訊息: "✅ 題目生成成功！

📊 生成統計:
  • 題目數: {generateResponse.question_count}
  • 檔案名: {generateResponse.output_file}
  • 檔案大小: ~{問題計數} KB

🔗 下載連結:
{generateResponse.download_url}"

動作: 提供下載按鈕
```

#### 節點 9：錯誤處理
```
條件: 如果 generateResponse.status != "success"

訊息: "❌ 生成失敗

錯誤信息: {generateResponse.message}

可能原因:
  • 檔案格式不支持
  • 檔案損毀或無法讀取
  • 參數設定不正確

💡 建議:
  1. 檢查檔案格式
  2. 嘗試更新材料
  3. 聯絡支持團隊"

動作: 提供重新開始選項
```

---

## 第 6 步：添加高級功能

### 6.1 情報卡片（Rich Cards）

在結果節點中添加格式化卡片：

```
卡片類型: Adaptive Card
內容以下（JSON 附加格式):
{
  "type": "AdaptiveCard",
  "body": [
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "✅ 題目生成成功！",
          "weight": "bolder",
          "size": "large"
        },
        {
          "type": "ColumnSet",
          "columns": [
            {
              "width": "stretch",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "題目數",
                  "weight": "bolder"
                },
                {
                  "type": "TextBlock",
                  "text": "${question_count}"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### 6.2 快速按鈕

添加快速操作按鈕：

```
按鈕 1: 下載 Excel
  動作: 開啟連結 → {download_url}

按鈕 2: 新建題庫
  動作: 重新開始對話

按鈕 3: 查看幫助
  動作: 顯示幫助主題
```

---

## 第 7 步：配置觸發器

### 7.1 Teams 觸發器

1. 進入**發佈** → **整合到 Teams**
2. 配置以下設定：
   - 允許用戶在 Teams 中搜索 Copilot
   - 啟用私人聊天
   - 啟用群組聊天

### 7.2 Power Automate 觸發器

啟用流程觸發器以支持自動化工作流程。

---

## 第 8 步：測試 Copilot

### 8.1 在 Copilot Studio 中測試

1. 點擊右上角的**測試**
2. 執行完整對話流程：
   - 上傳測試檔案
   - 設置參數
   - 驗證輸出

### 8.2 在 Teams 中測試

1. 進入 Teams
2. 在應用商店搜索您的 Copilot
3. 啟動對話並執行完整流程
4. 驗證以下結果：
   - ✓ 檔案上傳成功
   - ✓ 參數驗證正確
   - ✓ API 調用成功
   - ✓ Excel 檔案可下載
   - ✓ 格式正確

---

## 第 9 步：發佈 Copilot

### 9.1 發佈到公司內部

1. 進入**發佈** → **可用性**
2. 選擇 **組織內部**
3. 設定存取權限：
   - 所有人
   - 特定部門
   - 特定使用者

### 9.2 發佈到頻道

1. 進入**整合到 Teams**
2. 選擇要發佈的頻道
3. 點擊**發佈**

---

## 常見問題

### Q1：API 連接失敗

```
A: 檢查以下項目:
  1. API URL 是否正確
  2. Azure 中的 CORS 設定
  3. API 金鑰是否有效
  4. 防火牆設定
```

### Q2：檔案上傳失敗

```
A: 檢查以下項目:
  1. 檔案大小（< 100 MB）
  2. 檔案格式（PDF/PPTX/DOCX/TXT）
  3. 檔案完整性
```

### Q3：生成的題目格式不對

```
A: 檢查以下項目:
  1. 語言設定
  2. 難度映射
  3. 題型配置
```

---

## 監控和分析

### 查看使用統計

1. 進入**分析** → **對話洞察**
2. 查看以下指標：
   - 對話次數
   - 平均對話時長
   - 成功率
   - 常見錯誤

### 設定告警

配置以下告警：
- API 錯誤率 > 5%
- 平均回應時間 > 3 秒
- 每天對話次數 < 10

---

## 維護和更新

### 定期檢查

- 每週：檢查 API 狀態和錯誤日誌
- 每月：更新文檔和提示詞
- 每季：收集使用者反饋，優化流程

### 備份和災難恢復

定期備份 Copilot 配置：
1. 進入**設定** → **備份**
2. 下載配置檔案
3. 存儲到安全位置

---

## 後續步驟

✅ 已完成基礎配置  
📈 監控 API 使用情況  
🚀 收集用戶反饋進行優化  
🔄 定期更新題目生成策略  
📱 擴展到其他 Microsoft 365 應用（Outlook、Teams）

---

## 支持聯絡

- 技術支持：dev-team@example.com
- Copilot Studio 文檔：https://learn.microsoft.com/copilot
- Azure 支持：https://portal.azure.com/support
