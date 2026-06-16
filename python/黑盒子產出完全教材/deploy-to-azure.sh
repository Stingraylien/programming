#!/bin/bash
# Azure 自動化部署指令碼
# 使用方式: ./deploy-to-azure.sh <app-name> <resource-group> <region>

set -e

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查參數
if [ $# -lt 3 ]; then
    echo "使用方式: $0 <app-name> <resource-group> <region>"
    echo "示例: $0 my-question-generator question-gen-rg eastasia"
    exit 1
fi

APP_NAME=$1
RESOURCE_GROUP=$2
REGION=$3
APP_SERVICE_PLAN="${RESOURCE_GROUP}-plan"
API_KEY=$(openssl rand -hex 32)

echo -e "${YELLOW}=== Black Box Question Generator - Azure 部署 ===${NC}"
echo ""

# 步驟 1：檢查 Azure CLI
echo -e "${YELLOW}步驟 1：檢查 Azure CLI...${NC}"
if ! command -v az &> /dev/null; then
    echo -e "${RED}✗ Azure CLI 未安裝${NC}"
    echo "請安裝: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi
echo -e "${GREEN}✓ Azure CLI 已安裝${NC}"

# 步驟 2：檢查登入
echo -e "${YELLOW}步驟 2：檢查 Azure 登入...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${RED}✗ 未登入 Azure${NC}"
    echo "執行: az login"
    exit 1
fi
ACCOUNT=$(az account show --query user.name -o tsv)
echo -e "${GREEN}✓ 已登入為: $ACCOUNT${NC}"

# 步驟 3：建立資源群組
echo -e "${YELLOW}步驟 3：建立資源群組: $RESOURCE_GROUP${NC}"
az group create --name "$RESOURCE_GROUP" --location "$REGION" 2>/dev/null || true
echo -e "${GREEN}✓ 資源群組已就緒${NC}"

# 步驟 4：建立 App Service Plan
echo -e "${YELLOW}步驟 4：建立 App Service Plan: $APP_SERVICE_PLAN${NC}"
az appservice plan create \
    --name "$APP_SERVICE_PLAN" \
    --resource-group "$RESOURCE_GROUP" \
    --is-linux \
    --sku B1 \
    2>/dev/null || true
echo -e "${GREEN}✓ App Service Plan 已建立${NC}"

# 步驟 5：建立 Web App
echo -e "${YELLOW}步驟 5：建立 Web App: $APP_NAME${NC}"
az webapp create \
    --resource-group "$RESOURCE_GROUP" \
    --plan "$APP_SERVICE_PLAN" \
    --name "$APP_NAME" \
    --runtime "PYTHON:3.10"
echo -e "${GREEN}✓ Web App 已建立${NC}"

# 步驟 6：設定應用設定
echo -e "${YELLOW}步驟 6：設定應用設定...${NC}"
az webapp config appsettings set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --settings \
        FLASK_ENV=production \
        FLASK_DEBUG=0 \
        PYTHONPATH=/home/site/wwwroot \
        API_KEY="$API_KEY"
echo -e "${GREEN}✓ 應用設定已配置${NC}"

# 步驟 7：啟用 CORS
echo -e "${YELLOW}步驟 7：配置 CORS...${NC}"
az webapp cors add \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --allowed-origins "https://*.microsoft.com" "https://*.office.com" "http://localhost:3000" \
    2>/dev/null || true
echo -e "${GREEN}✓ CORS 已配置${NC}"

# 步驟 8：建立部署 ZIP
echo -e "${YELLOW}步驟 8：準備部署檔案...${NC}"
zip -r deployment.zip . \
    -x "venv/*" ".git/*" "__pycache__/*" "*.pyc" "*.egg-info/*" "build/*" > /dev/null 2>&1
echo -e "${GREEN}✓ 部署檔案已準備 (deployment.zip)${NC}"

# 步驟 9：部署程式碼
echo -e "${YELLOW}步驟 9：部署程式碼到 Azure...${NC}"
az webapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --src deployment.zip
echo -e "${GREEN}✓ 程式碼已部署${NC}"

# 步驟 10：等待部署完成
echo -e "${YELLOW}步驟 10：等待部署完成（30 秒）...${NC}"
sleep 30

# 步驟 11：驗證部署
echo -e "${YELLOW}步驟 11：驗證部署...${NC}"
APP_URL="https://${APP_NAME}.azurewebsites.net"
HEALTH_CHECK=$(curl -s "$APP_URL/api/health" 2>/dev/null || echo "")

if [[ $HEALTH_CHECK == *"healthy"* ]]; then
    echo -e "${GREEN}✓ API 健康檢查成功${NC}"
else
    echo -e "${YELLOW}⚠ 健康檢查進行中，請稍候...${NC}"
fi

# 步驟 12：顯示摘要
echo ""
echo -e "${GREEN}=== 部署完成 ===${NC}"
echo ""
echo "📊 部署信息:"
echo "  應用名稱: $APP_NAME"
echo "  資源群組: $RESOURCE_GROUP"
echo "  區域: $REGION"
echo "  API URL: $APP_URL/api"
echo "  API 金鑰: $API_KEY"
echo ""
echo "🔗 後續步驟:"
echo "  1. 測試 API: curl $APP_URL/api/health"
echo "  2. 進入 Copilot Studio: https://copilotstudio.microsoft.com"
echo "  3. 建立新 Copilot 並連接此 API"
echo "  4. 配置 API 端點和認证"
echo ""
echo "📝 注意:"
echo "  - API 金鑰已設定為環境變數 API_KEY"
echo "  - 部署檔案保存於: deployment.zip"
echo "  - 可安全刪除: rm deployment.zip"
echo ""
echo -e "${YELLOW}需要幫助? 查看 AZURE_DEPLOYMENT_QUICK_START.md${NC}"
