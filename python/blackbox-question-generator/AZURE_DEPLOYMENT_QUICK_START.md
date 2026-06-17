# 快速部署指南 - Microsoft 365 Copilot 集成

## 環境準備

本指南假設您已完成以下準備：
- ✅ Azure 帳號已創建並激活
- ✅ Microsoft 365 組織管理員權限
- ✅ 本地 Flask API 已驗證正常運作

---

## 步驟 1：登入 Azure Portal

```bash
# 如果尚未登入，執行以下命令
az login

# 驗證登入
az account show
```

---

## 步驟 2：建立 Azure 資源群組

```bash
# 設定變數
RESOURCE_GROUP="question-generator-rg"
REGION="eastasia"  # 或選擇其他區域

# 建立資源群組
az group create \
  --name $RESOURCE_GROUP \
  --location $REGION
```

---

## 步驟 3：建立 App Service Plan

```bash
# 設定變數
APP_SERVICE_PLAN="question-generator-plan"

# 建立 App Service Plan（B1 SKU 適合開發/測試）
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --is-linux \
  --sku B1
```

---

## 步驟 4：建立 Web App

```bash
# 設定變數
APP_NAME="question-generator-$(date +%s)"  # 全球唯一名稱

# 建立 Python Web App
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --name $APP_NAME \
  --runtime "PYTHON:3.10"

# 輸出應用 URL
echo "應用 URL: https://$APP_NAME.azurewebsites.net"
```

---

## 步驟 5：設定環境變數

```bash
# 設定 Flask 環境變數
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
    FLASK_ENV=production \
    FLASK_DEBUG=0 \
    PYTHONPATH=/home/site/wwwroot \
    API_KEY="your-secret-api-key-here"
```

---

## 步驟 6：部署程式碼

### 選項 A：使用 Git 部署

```bash
# 初始化 Git 倉庫（如果還未初始化）
git init
git add .
git commit -m "Prepare for Azure deployment"

# 配置 Azure 遠端
az webapp deployment source config-local-git \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME

# 取得部署認證
az webapp deployment list-publishing-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME

# 添加遠端並推送（將 URL 替換為上面取得的值）
git remote add azure <部署 URL>
git push azure main
```

### 選項 B：使用 ZIP 部署

```bash
# 建立部署 ZIP 包
zip -r deployment.zip . \
  -x "venv/*" ".git/*" "__pycache__/*" "*.pyc"

# 部署 ZIP
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --src deployment.zip
```

---

## 步驟 7：驗證部署

```bash
# 檢查應用狀態
az webapp show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --query state

# 檢查 API 可用性
curl https://$APP_NAME.azurewebsites.net/api/health
```

---

## 步驟 8：啟用 CORS

編輯 `api/main.py` 並新增 CORS 支持：

```python
from flask_cors import CORS

app = Flask(__name__)

# 允許來自 Microsoft 365 的請求
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://*.microsoft.com", "https://*.office.com"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

---

## 步驟 9：在 Copilot Studio 中測試

1. 進入 [Copilot Studio](https://copilotstudio.microsoft.com)
2. 建立新 Copilot
3. 進入**插件** → **建立新連接**
4. 選擇 **REST API** 連接器
5. 配置 API：
   - 基本 URL: `https://$APP_NAME.azurewebsites.net`
   - 認証: API 金鑰 (Authorization header)
   - 金鑰值: 您在步驟 5 中設定的 API_KEY

---

## 故障排除

### 常見問題

#### 1. 部署後出現 502 Bad Gateway

```bash
# 檢查 App Service 日誌
az webapp log tail \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME

# 常見原因：
# - Python 版本不符（確保是 3.10）
# - 依賴包未安裝（檢查 requirements-production.txt）
# - WSGI 配置錯誤
```

#### 2. API 金鑰驗証失敗

```bash
# 重新設定 API_KEY
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings API_KEY="new-key-here"
```

#### 3. CORS 錯誤

確保 `api/main.py` 中的 CORS 設定正確，並已重新部署。

---

## 監控和維護

### 檢查應用洞察

```bash
# 啟用 Application Insights
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --use-32bit-worker-process false

# 查看實時日誌
az webapp log tail \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --provider all
```

### 自動擴展配置

```bash
# 建立自動擴展規則
az monitor autoscale create \
  --resource-group $RESOURCE_GROUP \
  --resource-name-prefix $APP_NAME \
  --resource-type "Microsoft.Web/serverFarms" \
  --min-count 1 \
  --max-count 3 \
  --count 1
```

---

## 成本估計

| 資源 | SKU | 成本 | 說明 |
|------|-----|------|------|
| App Service Plan | B1 | $10/月 | 開發/測試 |
| 儲存體 | 50 GB | ~$1/月 | 備份和日誌 |
| 頻寬 | 出站 | 前 1GB 免費 | 超出後 $0.12/GB |
| **總計** | | **~$11/月** | 基本配置 |

**生產建議**：使用 B2 或更高 SKU，成本約 $40-100/月。

---

## 後續步驟

1. ✅ 完成 Azure 部署
2. ✅ 在 Copilot Studio 中配置 API
3. ✅ 建立 Copilot Agent 對話流程
4. ✅ 進行端到端測試
5. ✅ 發佈到公司內部 Copilot

詳細步驟請參考 [COPILOT_INTEGRATION_GUIDE.md](COPILOT_INTEGRATION_GUIDE.md)

---

## 需要幫助？

- **Azure 支持**: https://azure.microsoft.com/support/
- **Copilot Studio 文檔**: https://learn.microsoft.com/copilot
- **開發文檔**: 請參考項目中的其他 .md 檔案
