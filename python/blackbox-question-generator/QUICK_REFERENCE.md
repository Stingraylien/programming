# 快速啟動指南 - 常用命令速查表

## 🔧 本地開發

### 啟動 API 伺服器（開發模式）
```bash
cd /Users/wei-xianglien/Library/CloudStorage/OneDrive-InventecCorp/programming/python/blackbox-question-generator

# 啟動虛擬環境
source venv/bin/activate

# 啟動 Flask 開發伺服器
FLASK_PORT=8000 python scripts/start_server.py
```

### 測試 API 端點
```bash
# 健康檢查
curl http://localhost:8000/api/health

# 獲取配置
curl http://localhost:8000/api/config | python -m json.tool

# 運行所有測試
cd /那個設置的位置
pytest tests/ -v

# 運行特定測試
pytest tests/test_question_generator.py -v

# 查看測試覆蓋率
pytest tests/ --cov=src --cov-report=html
```

---

## ☁️ Azure 部署

### 快速部署（自動化）
```bash
# 確保在專案根目錄
cd /Users/wei-xianglien/Library/CloudStorage/OneDrive-InventecCorp/programming/python/blackbox-question-generator

# 執行自動部署腳本
./deploy-to-azure.sh my-question-generator question-gen-rg eastasia

# 參數說明:
# - my-question-generator  = 應用名稱（全球唯一）
# - question-gen-rg        = 資源群組名稱
# - eastasia               = Azure 區域
```

### 手動部署步驟

#### 1. 登入 Azure
```bash
az login
az account show
```

#### 2. 建立資源
```bash
# 建立資源群組
az group create --name question-gen-rg --location eastasia

# 建立 App Service Plan
az appservice plan create \
  --name question-gen-plan \
  --resource-group question-gen-rg \
  --is-linux \
  --sku B1

# 建立 Web App
az webapp create \
  --resource-group question-gen-rg \
  --plan question-gen-plan \
  --name my-question-generator \
  --runtime "PYTHON:3.10"
```

#### 3. 設定應用
```bash
az webapp config appsettings set \
  --resource-group question-gen-rg \
  --name my-question-generator \
  --settings \
    FLASK_ENV=production \
    FLASK_DEBUG=0 \
    API_KEY="your-secret-key-here"
```

#### 4. 部署程式碼
```bash
# 建立 ZIP 檔案
zip -r deployment.zip . -x "venv/*" ".git/*" "__pycache__/*"

# 部署
az webapp deployment source config-zip \
  --resource-group question-gen-rg \
  --name my-question-generator \
  --src deployment.zip
```

#### 5. 驗證部署
```bash
curl https://my-question-generator.azurewebsites.net/api/health
```

---

## 🤖 Copilot Studio 配置

### 登入 Copilot Studio
```
進入: https://copilotstudio.microsoft.com
使用公司 Microsoft 365 帳號登入
```

### 快速配置檢查清單
- [ ] 新 Copilot 已建立
- [ ] REST API 連接已配置
- [ ] API URL 正確
- [ ] API 金鑰已設定
- [ ] 4 個 API 操作已定義
- [ ] 對話流程已設定
- [ ] Teams 觸發器已啟用
- [ ] 測試成功
- [ ] 發佈至組織

### API 連接字符串範本
```
基本 URL: https://my-question-generator.azurewebsites.net
認証類型: API 金鑰
位置: Header
參數名: Authorization
參數值: Bearer YOUR_API_KEY_HERE
```

---

## 📁 重要檔案位置

```
項目根目錄/
├── 📄 README.md                          - 項目概述
├── 📄 ARCHITECTURE.md                    - 架構說明
├── 📄 AZURE_DEPLOYMENT_QUICK_START.md    - Azure 部署快速開始
├── 📄 COPILOT_INTEGRATION_GUIDE.md       - 完整集成指南
├── 📄 COPILOT_STUDIO_SETUP.md           - Copilot Studio 詳細設定
├── 📄 DEPLOYMENT_CHECKLIST.md           - 部署檢查清單
├── 📄 config.py                         - 應用配置
├── 📄 wsgi.py                         - 生產 WSGI 入口
├── 📄 requirements.txt                  - 開發依賴
├── 📄 requirements-production.txt       - 生產依賴
├── 🔧 deploy-to-azure.sh               - 自動化部署腳本
├── 📁 src/                             - 核心模組
├── 📁 api/                             - Flask API
├── 📁 tests/                           - 測試檔案
└── 📁 venv/                            - 虛擬環境
```

---

## 🐛 常見問題快速解決

### 問題 1：Port 8000 被占用
**解決方案**：
```bash
# 使用環境變數指定其他端口
FLASK_PORT=9000 python scripts/start_server.py

# 或殺死占用該端口的進程
lsof -i :8000
kill -9 <PID>
```

### 問題 2：模組導入錯誤
**解決方案**：
```bash
# 確保虛擬環境已激活
source venv/bin/activate

# 確保主目錄在 Python 路徑中
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 問題 3：依賴安裝失敗
**解決方案**：
```bash
# 清除 pip 快取
pip cache purge

# 重新安裝
pip install -r requirements.txt --no-cache-dir

# 強制重新安裝特定包
pip install --force-reinstall pandas
```

### 問題 4：Azure 部署失敗
**解決方案**：
```bash
# 檢查 Azure 日誌
az webapp log tail --resource-group question-gen-rg --name my-question-generator

# 檢查部署狀態
az webapp deployment list-publishing-credentials \
  --resource-group question-gen-rg \
  --name my-question-generator
```

---

## 📊 監控和調試

### 查看 API 日誌（本地）
```bash
# 直接查看應用輸出（需要啟動伺服器時的終端視圖）
# Flask debug 模式會自動輸出每個請求的日誌
```

### 查看 Azure 日誌
```bash
# 即時日誌
az webapp log tail \
  --resource-group question-gen-rg \
  --name my-question-generator \
  --provider all

# 下載完整日誌
az webapp log download \
  --resource-group question-gen-rg \
  --name my-question-generator
```

### 查看 Copilot 分析
1. 進入 Copilot Studio
2. 進入**分析** → **對話洞察**
3. 查看以下指標：
   - 總對話數
   - 平均對話時長
   - 常見問題
   - 成功率

---

## 🔄 更新和維護

### 更新依賴
```bash
# 檢查過期的包
pip list --outdated

# 更新特定包
pip install --upgrade pandas

# 更新所有包（謹慎操作）
pip install --upgrade -r requirements.txt
```

### 更新 API 程式碼
```bash
# 本地測試後
# 1. 提交程式碼變更
git add .
git commit -m "Updated API logic"

# 2. 重新部署
rm deployment.zip
zip -r deployment.zip . -x "venv/*" ".git/*"

az webapp deployment source config-zip \
  --resource-group question-gen-rg \
  --name my-question-generator \
  --src deployment.zip
```

---

## 🛑 緊急操作

### 暫停 API 服務（停止 Web App）
```bash
az webapp stop \
  --resource-group question-gen-rg \
  --name my-question-generator
```

### 恢復 API 服務
```bash
az webapp start \
  --resource-group question-gen-rg \
  --name my-question-generator
```

### 重啟 API 服務
```bash
az webapp restart \
  --resource-group question-gen-rg \
  --name my-question-generator
```

### 刪除 Copilot（測試環境）
```bash
# 在 Copilot Studio 中
進入 Copilot 設定 → 進階選項 → 刪除此 Copilot
```

---

## 📞 聯絡方式

| 項目 | 聯絡方式 |
|------|---------|
| 技術支持 | dev-team@example.com |
| Azure 問題 | https://portal.azure.com/support |
| Copilot 問題 | copilot-support@example.com |
| 緊急情況 | +886-XXXX-XXXX |

---

## 💡 有用的連結

- [Azure Portal](https://portal.azure.com)
- [Copilot Studio](https://copilotstudio.microsoft.com)
- [Azure CLI 文檔](https://docs.microsoft.com/cli/azure)
- [Microsoft Learn - Copilot](https://learn.microsoft.com/copilot)
- [Flask 官方文檔](https://flask.palletsprojects.com)
- [Python 官方文檔](https://docs.python.org/3)

---

**最後更新**：2026年3月24日  
**下一次更新**：2026年4月24日
