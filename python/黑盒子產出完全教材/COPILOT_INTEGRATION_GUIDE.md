# Microsoft 365 Copilot 集成指南

## 概述

本指南說明如何將 Black Box Question Generator 部署並集成到 Microsoft 365 Copilot 中。

---

## 第 1 部分：部署 Flask API

### 選項 A：部署到 Azure App Service（推薦）

#### 1. 準備部署
```bash
# 建立部署資料夾
mkdir -p deploy
cd deploy

# 複製必要的檔案
cp -r ../src .
cp -r ../tests .
cp ../config.py .
cp ../requirements.txt .
cp ../api/main.py .
cp -r ../scripts .
```

#### 2. 建立 Azure App Service

1. 登入 [Azure Portal](https://portal.azure.com)
2. 建立新的**應用程式服務**
   - **發行者**：Python 3.10
   - **作業系統**：Linux
   - **SKU**：B1（開發）或 B2（生產）
3. 複製應用程式名稱（例如：`myorg-question-generator.azurewebsites.net`）

#### 3. 設定部署

```bash
# 初始化 Git 倉庫
git init
git add .
git commit -m "Initial deployment"

# 新增 Azure 遠端
az webapp deployment source config-zip --resource-group <resource-group> \
  --name <app-name> --src <zip-file>
```

#### 4. 設定環境變數

在 Azure Portal 中：
1. 進入應用程式設定
2. 新增應用程式設定：
   - `FLASK_ENV`: `production`
   - `FLASK_DEBUG`: `0`
   - `PYTHONPATH`: `/home/site/wwwroot`

#### 5. 啟用 CORS

修改 `api/main.py`：

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "https://*.microsoft.com",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### 選項 B：部署到其他雲平台

- **Heroku** - 使用 `Procfile` 和 `runtime.txt`
- **AWS Lambda** - 使用 API Gateway + Zappa
- **Google Cloud Run** - 使用 Docker 容器

---

## 第 2 部分：配置 Copilot Agent

### 步驟 1：登入 Microsoft Copilot Studio

1. 進入 [Copilot Studio](https://copilotstudio.microsoft.com)
2. 使用公司 Microsoft 365 帳號登入
3. 建立新的 Copilot

### 步驟 2：建立 Copilot 基礎設定

```
名稱: 題目生成助手
說明: 協助教師和培訓人員快速生成考試題目
圖示: [選擇一個圖示代表 Copilot]
```

### 步驟 3：建立 API 連接

#### 在 Copilot Studio 中：

1. 進入**插件** → **建立新連接器**
2. 選擇 **REST API**
3. 設定連接詳細資訊：

```yaml
連接名稱: Question Generator API
基本 URL: https://myorg-question-generator.azurewebsites.net
認證方式: API 金鑰
API 金鑰位置: Header
金鑰名稱: Authorization
```

#### 定義 API 操作

**操作 1：健康檢查**
```
名稱: HealthCheck
方法: GET
端點: /api/health
說明: 檢查服務狀態
```

**操作 2：獲取配置信息**
```
名稱: GetConfig
方法: GET
端點: /api/config
說明: 獲取支持的題型和難度
```

**操作 3：生成題目**
```
名稱: GenerateQuestions
方法: POST
端點: /api/generate-question-bank
說明: 生成考試題目並輸出 Excel

請求體：
{
  "materials": [file],
  "question_count": 10,
  "question_types": ["true_false", "single_choice"],
  "difficulty": "medium",
  "language": "zh-TW"
}

回應：
{
  "status": "success",
  "message": "Successfully generated X questions",
  "question_count": 10,
  "output_file": "filename.xlsx"
}
```

**操作 4：下載檔案**
```
名稱: DownloadFile
方法: GET
端點: /api/download/{filename}
說明: 下載生成的 Excel 檔案
```

---

## 第 3 部分：建立 Agent 流程

### 步驟 1：主對話流程

在 Copilot Studio 中建立以下對話流程：

```
1. 歡迎訊息
   "歡迎使用題目生成助手！我可以幫助您快速生成考試題目。
    請上傳教學材料（支持 PDF、PowerPoint、Word 或 TXT）"

2. 接收檔案
   變數: materials (File)
   "感謝上傳！請告訴我需要生成多少개題目？"

3. 獲取題目數量
   變數: question_count (Number)
   預設值: 10

4. 選擇題型
   變數: question_types (Multiple Choice)
   選項: 
   - 是非題
   - 單選題
   - 複選題
   - 填空題
   - 申論題

5. 選擇難度
   變數: difficulty (Choice)
   選項:
   - 簡單 (easy)
   - 中等 (medium)
   - 困難 (hard)

6. 確認語言
   變數: language (Choice)
   選項:
   - 繁體中文 (zh-TW)
   - 英文 (en-US)

7. 處理請求
   Action: GenerateQuestions
   參數傳遞: materials, question_count, question_types, difficulty, language

8. 完成並提供下載
   "✅ 已生成 {question_count} 道題目！
    Excel 檔案已準備好下載：{output_file}"
   Action: DownloadFile
```

### 步驟 2：建立觸發器

在 Copilot Studio 中新增觸發器：

```
1. PowerAutomate 觸發器
   功能: 支持在 Power Automate 流程中使用此 Copilot

2. Teams 觸發器
   功能: 在 Teams 頻道和私人訊息中使用

3. SharePoint 整合
   功能: 直接從 SharePoint 文件庫上傳材料

4. Outlook 整合
   功能: 從 Outlook 附件生成試卷
```

---

## 第 4 部分：安全性配置

### 1. API 認証

修改 `api/main.py` 添加 API 金鑰驗證：

```python
from functools import wraps
import os

API_KEY = os.environ.get('API_KEY', 'your-secret-key-here')

def verify_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return {'error': 'Missing API key'}, 401
        
        token = auth_header.replace('Bearer ', '')
        if token != API_KEY:
            return {'error': 'Invalid API key'}, 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/generate-question-bank', methods=['POST'])
@verify_api_key
def generate():
    # 現有邏輯
```

### 2. 限流保護

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/generate-question-bank', methods=['POST'])
@limiter.limit("10 per minute")
@verify_api_key
def generate():
    # 限制每分鐘 10 個請求
```

### 3. HTTPS 強制

在 Azure App Service 中自動啟用 HTTPS。

---

## 第 5 部分：部署清單

### 部署前檢查表

- [ ] Flask API 已部署到 Azure/雲端
- [ ] API 金鑰已配置
- [ ] CORS 已啟用
- [ ] HTTPS 已強制執行
- [ ] 限流保護已設定
- [ ] 日誌記錄已啟用
- [ ] 備份策略已設定
- [ ] 監控告警已配置

### Copilot Studio 檢查表

- [ ] API 連接已測試
- [ ] 對話流程已完成
- [ ] 所有觸發器已配置
- [ ] 回應訊息已本地化
- [ ] 測試流程已執行
- [ ] 使用者文檔已準備

### 發佈檢查表

- [ ] 在組織內測試 (Beta)
- [ ] 收集使用者反饋
- [ ] 修復已知問題
- [ ] 發佈到公司 Copilot
- [ ] 發佈公告已發送
- [ ] 支持文檔已提供

---

## 第 6 部分：測試 Copilot Agent

### 1. 在 Copilot Studio 中測試

```
步驟 1: 按右上角的「測試」按鈕
步驟 2: 輸入測試訊息：
  "我想生成 5 道中等難度的單選題"
步驟 3: 上傳測試檔案
步驟 4: 驗證對話流程
步驟 5: 驗證 Excel 輸出正確
```

### 2. 在 Teams 中測試

```
步驟 1: 新增 Copilot 到 Teams 頻道
步驟 2: @提及 Copilot
步驟 3: 發送"生成題目"命令
步驟 4: 上傳材料並按照提示進行
步驟 5: 驗證生成的檔案
步驟 6: 下載並檢查 Excel 格式
```

### 3. 性能測試

```bash
# 使用 Apache Bench 進行負載測試
ab -n 100 -c 10 -H "Authorization: Bearer $API_KEY" \
   -p test_payload.json \
   https://myorg-question-generator.azurewebsites.net/api/health
```

---

## 第 7 部分：監控和維護

### Azure Portal 監控

1. 進入 Azure Portal
2. 選擇您的 App Service
3. 設定監控指標：
   - CPU 使用率
   - 記憶體使用率
   - HTTP 錯誤率（5xx）
   - 平均回應時間

### 配置告警

```yaml
告警規則:
  1. CPU > 80% ⇒ 發送電子郵件警告
  2. 5xx 錯誤率 > 1% ⇒ 立即通知
  3. 回應時間 > 5 秒 ⇒ 記錄日誌
```

### 日誌分析

在 Azure 中使用 Application Insights：

```
查詢示例:
1. 失敗請求: requests | where resultCode >= 400
2. 大檔案上傳: requests | where size > 10000000
3. 效能低下: requests | where duration > 5000
```

---

## 第 8 部分：故障排除

### 常見問題

**Q1: API 超時**
```
A: 增加 Azure App Service 的超時設定
   或優化檔案處理程式碼以提高速度
```

**Q2: 檔案上傳失敗**
```
A: 檢查:
   1. 檔案大小限制 (預設 100MB)
   2. 支持的副檔名列表
   3. CORS 設定是否正確
```

**Q3: Copilot 無法連接 API**
```
A: 驗證:
   1. API 金鑰是否正確
   2. Azure App Service 是否在線
   3. 防火牆是否允許連接
   4. HTTPS 憑證是否有效
```

**Q4: 生成的 Excel 格式錯誤**
```
A: 檢查:
   1. XuLink 格式規範是否符合
   2. 難度值是否正確映射 (1-5)
   3. 選項限制計數是否正確
```

---

## 第 9 部分：維護計劃

### 每日
- [ ] 檢查 API 可用性
- [ ] 監控錯誤日誌
- [ ] 驗證備份完成

### 每週
- [ ] 性能分析
- [ ] 更新日誌檢查
- [ ] 安全掃描

### 每月
- [ ] 依賴更新檢查
- [ ] 安全修補程式應用
- [ ] 容量規劃檢查
- [ ] 使用者反饋審查

### 每季
- [ ] 災害恢復測試
- [ ] 性能優化審查
- [ ] 新功能規劃

---

## 第 10 部分：後續步驟和改進

### 短期（1-2 個月）
- [ ] 完成 Azure 部署
- [ ] 發佈到公司內部 Copilot
- [ ] 收集初期使用者回饋

### 中期（3-6 個月）
- [ ] 集成 Azure OpenAI 進行 AI 輔助出題
- [ ] 新增 SharePoint 深度整合
- [ ] 實現批量生成功能

### 長期（6 個月以上）
- [ ] 企業級功能（審計日誌、版本控制）
- [ ] 多語言支持擴展
- [ ] 高級分析和報告

---

## 聯繫支持

對於技術問題，請聯繫：
- **開發團隊**: dev-team@example.com
- **Azure 支持**: https://portal.azure.com/support
- **Copilot Studio 文檔**: https://learn.microsoft.com/copilot
