# 開發指南 (Development Guide)

## 快速開始 (Getting Started)

### 環境設置

1. **克隆專案** (Clone the project)
```bash
git clone <repository-url>
cd blackbox-question-generator
```

2. **建立虛擬環境** (Create virtual environment)
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

3. **安裝依賴** (Install dependencies)
```bash
make install
# or
pip install -r requirements.txt
```

### 啟動服務

```bash
make run
# or
python scripts/start_server.py
```

服務將在 `http://localhost:8000` 啟動

## 專案結構

```
blackbox-question-generator/
├── src/                          # 核心邏輯
│   ├── input_adapter/            # 輸入適配器
│   ├── canonical_content/        # 內容標準化
│   ├── question_generator/       # 出題引擎
│   └── xulink_exporter/          # Excel 匯出
├── api/                          # Flask API
│   └── main.py                   # API 主程式
├── tests/                        # 測試
├── scripts/                      # 工具腳本
├── config.py                     # 配置文件
└── requirements.txt              # 依賴管理
```

## API 端點

### 健康檢查
```
GET /api/health
```

### 配置信息
```
GET /api/config
```

### 生成題庫
```
POST /api/generate-question-bank

Request:
- Form data:
  - materials: 上傳的教材文件 (PDF, PPTX, DOCX, MP4)
  - question_types: 題型列表 (true_false, single_choice, multiple_choice, fill_in_blank, essay)
  - difficulty: 難度等級 (easy, medium, hard)
  - language: 語言 (zh-TW, en-US)

Response:
{
  "status": "success",
  "questions_count": 10,
  "output_file": "training_question_bank_20260324_120000.xlsx",
  "download_url": "/api/download/training_question_bank_20260324_120000.xlsx"
}
```

### 下載文件
```
GET /api/download/<filename>
```

## 測試

### 運行所有測試
```bash
make test
```

### 測試 API
```bash
make test-api
```

### 運行特定測試
```bash
python -m pytest tests/test_integration.py -v
python -m pytest tests/test_question_generator.py::TestQuestionGenerator::test_generate_true_false -v
```

## 擴展功能

### 添加新的輸入格式

在 `src/input_adapter/input_adapter.py` 中：

```python
def process_new_format(file_path: str) -> Dict:
    """Process new format"""
    return {
        "source_type": "new_format",
        "sections": [
            {"title": "Section Title", "content": "..."}
        ]
    }
```

### 添加新的題型

在 `src/question_generator/question_generator.py` 中：

```python
def _generate_new_type(self, content: Dict, difficulty: int) -> List[Dict]:
    """Generate new question type"""
    # Implementation here
    return [...]
```

### 自定義出題策略

修改 `QuestionGenerator` 初始化：

```python
generator = QuestionGenerator(strategy="ai_assisted")
```

## 常用命令

| 命令 | 說明 |
|------|------|
| `make install` | 安裝依賴 |
| `make test` | 運行測試 |
| `make run` | 啟動服務器 |
| `make test-api` | 測試 API |
| `make clean` | 清理生成的文件 |
| `make format` | 格式化代碼 |
| `make lint` | 代碼檢查 |

## 故障排除

### 缺少依賴庫
如遇到 `ImportError`，請確保已安裝相應的依賴：
```bash
pip install PyPDF2 python-pptx python-docx
```

### 文件上傳失敗
確保 `uploads/` 目錄存在且有寫入權限。

### 端口被佔用
如果 8000 端口被佔用，可以修改 `scripts/start_server.py` 中的端口號或設置 `FLASK_PORT` 環境變數。

## 貢獻指南

1. 創建功能分支: `git checkout -b feature/new-feature`
2. 提交更改: `git commit -am 'Add new feature'`
3. 推送分支: `git push origin feature/new-feature`
4. 提交 Pull Request

## 許可證

[Specify License]