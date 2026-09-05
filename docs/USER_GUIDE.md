# FA Report Improvement — 使用手冊

> **完整使用指南**:從安裝到進階應用,涵蓋所有使用情境
> **當前版本**:v3.1.4(2026-09-03)+ v3.1.4-regression-fix(2026-09-04)
> **適用對象**:FA 工程師、品管主管、研發團隊

---

## 目錄

1. [快速開始(5 分鐘上手)](#1-快速開始)
2. [三種使用模式](#2-三種使用模式)
3. [輸入檔案格式](#3-輸入檔案格式)
4. [6 維度評估 + 改善機制](#4-6-維度評估--改善機制)
5. [進階:自訂樣板](#5-進階自訂樣板)
6. [進階:視覺元素](#6-進階視覺元素)
7. [進階:LLM 整合](#7-進階llm-整合)
8. [常見問題](#8-常見問題)
9. [故障排除](#9-故障排除)

---

## 1. 快速開始

### 1.1 安裝

#### 方式 A:使用 `uv`(推薦)

```bash
# 安裝 uv(若尚未安裝)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 進入技能包目錄
cd .agents/skills/fa-report-improvement

# 同步依賴(自動建立 .venv)
uv sync

# 驗證安裝
uv run python -c "import fa_improver; print('✓ 安裝成功')"
```

#### 方式 B:使用 pip

```bash
# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate (Windows)

# 安裝套件
pip install -e ".[dev,llm]"
```

### 1.2 執行方式選擇

技能包提供 3 種執行方式(+ 1 種安裝後的系統指令):

| # | 方式 | 指令 | 適用 |
|---|------|------|------|
| **1** | **新 CLI**(推薦) | `python -m fa_improver ...` | 日常使用、CI/CD |
| **2** | **傳統腳本** | `python scripts/improve_fa_report.py ...` | 向後相容舊版指令 |
| **3** | **端對端測試** | `python test_llm_end_to_end.py` | 開發測試、展示 |
| 4 | **系統指令** (需 `pip install -e .`) | `fa-improve ...` | 任何目錄、全域使用 |

詳細使用見 [§ 2 三種使用模式](#2-三種使用模式)與 [§ 2.4 執行方式詳細指令](#24-執行方式詳細指令)。

### 1.3 設定 API Key(選填)

```bash
# 複製範例檔
cp .env.example .env

# 編輯 .env,填入你的 OpenAI API Key
# OPENAI_API_KEY=sk-...
```

> **注意**:只有在「用 LLM 直接評估」時才需要 API Key。若已有評估 JSON 可跳過此步。

### 1.4 第一次執行

```bash
# 最簡單的方式:使用預先生成的評估 JSON
uv run python -m fa_improver report.pptx \
    --eval report_eval.json \
    --output improved.pptx

# 輸出:
# 📖 解析評估檔:report_eval.json
#    總分:55.5 (F)
# 📊 載入簡報:report.pptx
#    投影片數:9
# 🔧 執行改善...
# ✓ 完成!
#    輸出:improved.pptx
#    投影片:9 → 12 張
#    母片保護:✓
#    耗時:0.3s
```

---

## 2. 三種使用模式

### 模式 A:預先準備評估 JSON(推薦)

**適用情境**:已有評估工具(如 fa_report_analyzer_v3)產生評估結果

```bash
python -m fa_improver report.pptx \
    --eval eval.json \
    --output improved.pptx
```

**優點**:
- 快速(無 LLM 呼叫)
- 可重現(評估結果已固定)
- 離線可用
- 成本低(僅 PPTX 處理)

### 模式 B:用 LLM 直接評估

**適用情境**:沒有評估工具,希望 AI 自動評估

```bash
# 設定 API Key
export OPENAI_API_KEY=sk-...

# 或使用 .env 檔案
python -m fa_improver report.pptx \
    --llm-provider openai \
    --output improved.pptx
```

**優點**:
- 零設定(只要有 API Key)
- 自動評估 6 維度
- 支援自訂模型(`--model gpt-4o`)

**成本**:每份報告約 $0.001-0.005 USD(GPT-4o-mini)

### 模式 C:離線測試

**適用情境**:開發、測試、CI/CD

```bash
python -m fa_improver report.pptx \
    --llm-provider mock \
    --output improved.pptx
```

**優點**:
- 完全離線
- 無 API 成本
- 可預測結果(預設回傳)

### 2.4 執行方式詳細指令

#### 方式 1: `python -m fa_improver` (新 CLI · 推薦)

**特點**:完整 argparse 介面、所有選項

**基本用法**:
```bash
# 從技能包目錄執行
cd .agents/skills/fa-report-improvement
PYTHONPATH=src python -m fa_improver input.pptx \
    --eval eval.json \
    --output improved.pptx

# 或安裝後(不需 PYTHONPATH)
pip install -e .
fa-improve input.pptx --eval eval.json --output improved.pptx
```

**所有選項**:
```bash
python -m fa_improver --help
```

```
positional arguments:
  input                 輸入 pptx 檔案路徑

options:
  -h, --help            顯示說明
  -e, --eval EVAL       評估檔(JSON 或 TXT)
  --llm-provider        LLM provider(openai / mock)
  --model               LLM 模型(預設 gpt-4o-mini)
  -o, --output          輸出 pptx 檔案路徑
  --template-dir        自訂樣板目錄
  -v, --verbose         詳細輸出
```

#### 方式 2: `scripts/improve_fa_report.py` (傳統 CLI · 向後相容)

**特點**:簡單位置參數、舊版用戶無需改指令

**基本用法**:
```bash
cd .agents/skills/fa-report-improvement
python scripts/improve_fa_report.py input.pptx eval.json output.pptx
```

**自動委派**:內部會轉換為新 CLI 的命名參數(`--eval` / `--output`)。

#### 方式 3: 端對端測試程式

**特點**:自動評估+改善+成本報告,適合開發測試與展示

**test_llm_end_to_end.py** — 完整 LLM 評估 + 改善流程:
```bash
cd .agents/skills/fa-report-improvement
python test_llm_end_to_end.py

# 指定報告
python test_llm_end_to_end.py /path/to/report.pptx
```

**輸出範例**:
```
評估分數: D (65.0/100)
改善動作: 12 個
投影片增加: 7 張
母片保護: 通過 ✓
預估成本: $0.0006 USD
```

**test_api_key.py** — 只驗證 API key:
```bash
python test_api_key.py
```

#### 方式 4: 系統層級指令 `fa-improve` (安裝後)

**特點**:安裝套件後,任何目錄都可以呼叫

**安裝**:
```bash
cd .agents/skills/fa-report-improvement
pip install -e .
```

**使用**:
```bash
# 任何目錄
fa-improve /path/to/report.pptx --eval /path/to/eval.json --output /path/to/output.pptx
```

**解除安裝**:
```bash
pip uninstall fa-improver
```

#### 執行方式選擇指南

| 情境 | 推薦方式 |
|------|---------|
| 日常使用 | 方式 1 (`python -m fa_improver`) |
| 舊版指令相容 | 方式 2 (傳統腳本) |
| 開發/展示 | 方式 3 (端對端測試) |
| 系統整合 | 方式 4 (`fa-improve`) |

---

## 3. 輸入檔案格式

### 3.1 報告檔案(`.pptx` / `.ppt`)

| 格式 | 支援 | 說明 |
|------|------|------|
| `.pptx` | ✅ 直接處理 | PowerPoint 2007+ |
| `.ppt` | ✅ 自動轉換 | PowerPoint 97-2003,需 LibreOffice 或 PowerPoint |

**自動轉換原理**:
- Linux:使用 `libreoffice` 指令
- macOS:使用 `/Applications/LibreOffice.app/Contents/MacOS/soffice`
- Windows:使用 `pywin32` + PowerPoint

### 3.2 評估 JSON 格式

```json
{
  "total_score": 55.5,
  "grade": "F",
  "dimension_scores": {
    "基本資訊完整性": {
      "score": 40,
      "weight": 15,
      "comment": "缺批號"
    },
    "問題描述與定義": {
      "score": 45,
      "weight": 15,
      "comment": "未量化"
    },
    "分析方法與流程": {
      "score": 50,
      "weight": 20,
      "comment": "缺深度分析"
    },
    "數據與證據支持": {
      "score": 45,
      "weight": 20,
      "comment": "缺對照組"
    },
    "根因分析": {
      "score": 40,
      "weight": 20,
      "comment": "推測非分析"
    },
    "改善對策": {
      "score": 40,
      "weight": 10,
      "comment": "缺失"
    }
  },
  "summary": "報告需要大幅改善",
  "strengths": ["優點1", "優點2"],
  "improvements": [
    {
      "priority": "高",
      "item": "根因分析",
      "suggestion": "需使用 5-Why 分析法"
    }
  ]
}
```

**相容格式**:
- `dimensions`(扁平)與 `dimension_scores`(巢狀)都支援
- `improvements` 支援字串陣列與物件陣列

### 3.3 評估 TXT 格式

來自 fa_report_analyzer_v3 的文字輸出,範例:

```
================================================================================
FA 報告評分結果
================================================================================

來源文件:xxx.pptx
總分: 55.50 / 100
等級: F

--------------------------------------------------------------------------------
各維度評分詳情
--------------------------------------------------------------------------------

【基本資訊完整性】
  得分: 40.0 / 100  (40.0%)
  權重: 15%
  加權分數: 6.00
  評語: ...
```

工具會自動解析這種格式。

---

## 4. 6 維度評估 + 改善機制

### 4.1 觸發門檻總表

| 維度 | 權重 | 觸發門檻 | 改善動作 |
|------|------|---------|---------|
| 基本資訊完整性 | 15% | < 80 | 新增「FA 基本資訊」 |
| 問題描述與定義 | 15% | < 70 | 新增「問題描述與失效定義」 |
| 分析方法與流程 | 20% | < 70 | 新增「8D 流程 + 方法對照」 |
| 數據與證據支持 | 20% | < 70 | 新增「對照組數據 + 證據清單」 |
| 根因分析 | 20% | < 80 | 新增「5-Why + 統計驗證」 |
| 改善對策 | 10% | < 85 | 新增「改善對策總覽」 |

### 4.2 改善觸發實例

**範例**:MS Meishan 報告(全部 6 維度低分)
- 原始:5 張投影片
- 觸發後:12 張投影片
- 觸發動作:12 個(全部)
- 母片保護:✓

**範例**:N160JCN-EEK 報告(基本資訊高分)
- 原始:9 張投影片
- 觸發後:12 張投影片
- 跳過:基本資訊完整性(85 ≥ 80)
- 母片保護:✓

### 4.3 嚴重度決定展開張數

| 根因分析分數 | 嚴重度 | 觸發動作 |
|-------------|--------|---------|
| ≥ 85 | NONE | 不觸發 |
| 70-84 | MINOR | 統計驗證(1 張) |
| 50-69 | MODERATE | 5-Why + 統計驗證(2 張) |
| < 50 | SEVERE | 5-Why + 對照組 + 證據 + 統計(4 張) |

---

## 5. 進階:自訂樣板

### 5.1 樣板系統概述

技能包提供 **8 個內建樣板**(`templates/builtin/`),使用者可在不改程式碼的情況下覆寫。

### 5.2 建立自訂樣板目錄

```bash
mkdir my-templates
```

### 5.3 範例:客製化「改善對策」樣板

建立 `my-templates/prevention_overview_company.json`:

```json
{
  "extends": "prevention_overview",
  "title": "ELAN 改善對策總覽",
  "description": "公司專屬版本",
  "sections": [
    {
      "heading": "ELAN 改善對策項目",
      "visual": "checklist",
      "max_bullets": 4,
      "max_words_per_bullet": 30,
      "placeholder_items": [
        "短期:補齊 FA 基本資訊(FAE 負責)",
        "中期:建立 IQC SOP(編號:ELAN-QA-IQC-2026)",
        "長期:導入 MES 系統自動監測失效比例",
        "持續:每月失效案例分享會"
      ]
    }
  ]
}
```

### 5.4 使用自訂樣板

```bash
python -m fa_improver report.pptx \
    --eval eval.json \
    --template-dir ./my-templates \
    --output improved.pptx
```

### 5.5 樣板語法

| 欄位 | 必填 | 說明 |
|------|------|------|
| `name` | ✅ | 樣板唯一名稱 |
| `title` | ✅ | 投影片標題 |
| `layout_name` | ❌ | 使用的 layout(預設「2L - Topic」) |
| `extends` | ❌ | 繼承哪個內建樣板 |
| `sections` | ✅ | 區塊列表 |
| `max_total_words` | ❌ | 總字數上限(預設 200) |

每個 section 包含:
- `heading`:區塊標題
- `visual`:視覺元素類型
- `max_bullets`:bullet 數量上限
- `max_words_per_bullet`:每個 bullet 字數上限
- `placeholder_items`:可被替換的範本項目

### 5.6 樣板驗證規則

- `max_bullets` ≤ 5(資料表除外)
- `max_words_per_bullet` ≤ 50
- `max_total_words` ≤ 300
- `sections` 數量 ≤ 5
- 違反任一規則會在載入時拋出 `TemplateValidationError`

---

## 6. 進階:視覺元素

### 6.1 5 種視覺元素

| 類型 | 用途 | 範例 |
|------|------|------|
| Checklist | 待辦事項、檢查清單 | 8D 步驟、品管檢查 |
| Flow Diagram | 流程、推導 | 5-Why 推導 |
| Comparison Table | 對照、A/B 比較 | DVT vs PVT |
| Progress Bar | 進度、分數視覺化 | 6 維度評分 |
| Timeline | 時間軸、階段 | 立即/短期/中期/長期 |

### 6.2 自動觸發

每張新投影片**至少 1 個視覺元素**:
- `FA 基本資訊` → Bullet list
- `問題描述` → Comparison table + Checklist
- `分析方法` → Checklist + Comparison table
- `數據證據` → Comparison table + Checklist
- `根因分析(5-Why)` → Flow diagram
- `根因分析(統計)` → Checklist
- `改善對策` → Checklist
- `Summary 強化` → Progress bar(6 維度視覺化)

### 6.3 自訂顏色

`visuals/colors.py` 提供 ELAN 品牌色:

```python
ELAN_BLUE = RGBColor(0x1F, 0x4E, 0x79)        # 主色
ELAN_LIGHT_BLUE = RGBColor(0x5B, 0x9B, 0xD5)  # 輔助色
ELAN_RED = RGBColor(0xC0, 0x00, 0x00)          # 警告
ELAN_GREEN = RGBColor(0x70, 0xAD, 0x47)        # 成功
ELAN_ORANGE = RGBColor(0xED, 0x7D, 0x31)       # 注意
ELAN_GRAY = RGBColor(0x80, 0x80, 0x80)         # 中性
```

---

## 7. 進階:LLM 整合

### 7.1 設定 API Key

#### 方法 1:環境變數

```bash
export OPENAI_API_KEY=sk-...
```

#### 方法 2:.env 檔案

```bash
cp .env.example .env
# 編輯 .env:OPENAI_API_KEY=sk-...
```

#### 方法 3:CLI 參數

```python
from fa_improver.llm.openai_client import OpenAIClient
client = OpenAIClient(api_key="sk-...")
```

### 7.2 支援的 LLM Provider

| Provider | 設定方式 |
|---------|---------|
| OpenAI | `OPENAI_API_KEY=sk-...` |
| Groq | `OPENAI_API_KEY=gsk-...`<br>`OPENAI_BASE_URL=https://api.groq.com/openai/v1` |
| Together | `OPENAI_BASE_URL=https://api.together.xyz/v1` |
| OpenRouter | `OPENAI_BASE_URL=https://openrouter.ai/api/v1` |
| Azure | `OPENAI_BASE_URL=https://YOUR-RESOURCE.openai.azure.com/...` |
| 本地 Ollama | `OPENAI_BASE_URL=http://localhost:11434/v1` |

### 7.3 選擇模型

```bash
# GPT-4o-mini(預設,最便宜)
python -m fa_improver report.pptx --llm-provider openai --model gpt-4o-mini

# GPT-4o(更強但更貴)
python -m fa_improver report.pptx --llm-provider openai --model gpt-4o

# o1-mini(推理能力強)
python -m fa_improver report.pptx --llm-provider openai --model o1-mini
```

### 7.4 成本估算

| 模型 | 輸入 (per 1M tokens) | 輸出 (per 1M tokens) |
|------|---------------------|---------------------|
| gpt-4o-mini | $0.15 | $0.60 |
| gpt-4o | $2.50 | $10.00 |
| o1-mini | $3.00 | $12.00 |

**一份 10 頁報告**:約 1,500 tokens(輸入) + 800 tokens(輸出)
- gpt-4o-mini: $0.0007
- gpt-4o: $0.012

### 7.5 監控用量

到 OpenAI Dashboard 查看實際用量:
- https://platform.openai.com/usage

---

## 8. 常見問題

### Q1:輸出檔案是空的?

確認 `output_path` 的目錄存在且有寫入權限:

```bash
mkdir -p /path/to/output
python -m fa_improver report.pptx --eval eval.json --output /path/to/output/improved.pptx
```

### Q2:出現「找不到 OPENAI_API_KEY」?

設定 API Key:

```bash
export OPENAI_API_KEY=sk-...
# 或
echo "OPENAI_API_KEY=sk-..." > .env
```

### Q3:PPT 轉換失敗?

確認 LibreOffice 已安裝:

```bash
# Linux
sudo apt install libreoffice

# macOS
brew install --cask libreoffice

# Windows
# 安裝 LibreOffice 或 Microsoft PowerPoint
```

### Q4:出現「pptx 檔案有母片保護違規」?

這代表你的功能意外修改了母片 XML。請:
1. 確認沒有自訂修改母片的程式碼
2. 執行 `pytest tests/unit/test_master_protection.py -v`
3. 若測試失敗,聯絡開發者

### Q5:如何自訂觸發門檻?

透過環境變數或修改 `src/fa_improver/improvers/orchestrator.py` 的 `TRIGGER_THRESHOLDS`:

```python
TRIGGER_THRESHOLDS = {
    Dimension.BASIC_INFO: 80,    # 預設
    Dimension.PROBLEM_DEF: 70,   # 可調
    # ...
}
```

### Q6:可以批次處理多份報告嗎?

可以!用 shell 迴圈:

```bash
for f in report/*.pptx; do
    python -m fa_improver "$f" \
        --eval fa_report_$(basename "$f" .pptx).json \
        --output "improved/$(basename "$f")"
done
```

---

## 9. 故障排除

### 9.1 完整診斷指令

```bash
# 1. 確認 Python 版本
python --version  # 應為 3.10+

# 2. 確認依賴安裝
pip list | grep -E "python-pptx|pydantic|openai"

# 3. 確認 .env 設定
cat .env

# 4. 跑測試診斷
pytest tests/ -v

# 5. 端對端測試(需要 API Key)
python test_api_key.py
python test_llm_end_to_end.py
```

### 9.2 常見錯誤訊息

| 錯誤 | 原因 | 解決 |
|------|------|------|
| `ModuleNotFoundError: fa_improver` | 沒切到技能包目錄 | `cd .agents/skills/fa-report-improvement` |
| `No such file or directory: .env` | 沒設定 .env | `cp .env.example .env` |
| `pptx 檔案格式錯誤` | 檔案損壞 | 用 PowerPoint 重新存檔 |
| `母片保護失敗` | 程式碼錯誤 | 回報 issue |
| `API rate limit exceeded` | OpenAI 速率限制 | 等待或升級方案 |

### 9.3 取得協助

- **文件**:`docs/` 目錄
- **測試**:89 個測試展示正確使用方式
- **範例**:`examples/` 目錄
- **變更記錄**:`CHANGELOG.md`

---

## 附錄:完整 CLI 選項

```bash
python -m fa_improver --help
```

```
usage: fa-improve [-h] -e EVAL [-o OUTPUT] [-v] input

positional arguments:
  input              輸入 pptx 檔案路徑

options:
  -h, --help         顯示說明
  -e, --eval EVAL    評估檔(JSON 或 TXT)
  --llm-provider     LLM provider(openai / mock)
  --model            LLM 模型(預設 gpt-4o-mini)
  -o, --output       輸出 pptx 檔案路徑
  --template-dir     自訂樣板目錄
  -v, --verbose      詳細輸出
```

### 環境變數

| 變數 | 預設 | 說明 |
|------|------|------|
| `OPENAI_API_KEY` | (無) | OpenAI API Key |
| `FA_IMPROVER_MODEL` | `gpt-4o-mini` | LLM 模型 |
| `FA_IMPROVER_LLM_PROVIDER` | `openai` | LLM provider |
| `OPENAI_BASE_URL` | (無) | 自訂 endpoint |
| `FA_IMPROVER_LLM_TIMEOUT` | `60` | HTTP 請求超時(秒) |
| `FA_IMPROVER_LLM_MAX_RETRIES` | `3` | 最大重試次數 |

---

## 📋 v3.1.0+ 新增 CLI 參數補充

> 本節為 v3.1.0、v3.1.2、v3.1.3 新增的 CLI 參數補充說明

| 參數 | 版本 | 說明 |
|------|------|------|
| `--api-key` | v3.1.0+ | OpenAI API key(優先於 `OPENAI_API_KEY` 環境變數與 `.env` 檔案) |
| `--redact-pii` | v3.1.0+ | 在送出 LLM 前遮罩個資(電話/Email/中文姓名/IP/工號/身分證/信用卡) |
| `--base-url` | v3.1.0+ | 自訂 API endpoint(用於 OpenAI 相容介面如 Groq、OpenRouter) |
| `--include-dimension-chart` | v3.1.3+ | opt-in 加入「6 維度評分分析」slide(預設關閉,符合 Kenny 2026-09-02 回饋) |

### 範例:v3.1.3 預設(不含6 維度圖)

```bash
uv run python -m fa_improver report.pptx \
  --eval eval.json \
  --output improved.pptx
```

### 範例:opt-in 加入6 維度圖

```bash
uv run python -m fa_improver report.pptx \
  --eval eval.json \
  --include-dimension-chart \
  --output improved.pptx
```

### 範例:v3.1.0 個資遮罩

```bash
uv run python -m fa_improver report.pptx \
  --llm-provider openai \
  --redact-pii \
  --api-key sk-xxx \
  --output improved.pptx
```

---

## 🛡️ v3.1.3 版面優化(Kenny 2026-09-02 回饋)

v3.1.3 解決了3 個用戶回饋的版面問題:

1. **簡報標題偏左**:title 從 left=0.5 in 改為 left=1.2 in,避免被母片左上裝飾(0.54-0.97 in)擋住
2. **標題與內容重疊**:當 layout 的 body placeholder 高度 < 1.0 in 時,fallback 用 safe_textbox(高度 = slide高 - 2.0)
3. **移除6 維度評分分析**:預設不再產生此 slide(用戶回饋對終端用戶無實質幫助)

詳見 `docs/handoff/2026-09-01-v313-user-feedback-fixes-handoff.md`。v3.1.4 — 稽核修正 + CI 從紅轉綠 + 視覺回歸測試誠實化

## 🚀 v3.1.4 版本說明

### 對比 v3.1.3

| 指標 | v3.1.3 | v3.1.4 |
|------|--------|--------|
| 測試通過 | 219 | **235**(CI)/ **238**(真實客戶檔在位) |
| 測試 skip | 3 | 3(CI)/ **0**(真實客戶檔在位) |
| 覆蓋率 | 90% | **85%**(CI)/ **89%**(真實客戶檔在位) |
| ruff check | ✅ | ✅ |
| ruff format | ❌(CI 自 08-31 起紅燈) | ✅ **稽核 #1 順手解決** |
| CI Build Distribution | 一直被 skip | ✅ **v3.1.4 起重跑** |
| CI 狀態 | ❌ 持續紅燈 | ✅ **5/5 jobs success** |
| 視覺回歸測試 CI | ❌ 永遠 skip | ✅ **真在跑**(用合成 fixture) |

### 4 大新功能/修正

#### 1. conftest fixture 陷阱修正(`tests/conftest.py`)

全新 clone 環境跑 `pytest tests/` 不再爆 `IsADirectoryError`。

`sample_pptx/sample_eval_json/sample_eval_txt` 找不到檔案時改回傳 `None`(`Path | None`),13 處呼叫端從 `if not X.exists()` 改為 `if X is None`。

#### 2. 5-Why fallback 重設計(`src/fa_improver/improvers/root_cause.py`)

新增 `_truncate_step_text()` helper,中英文句號「。」與「.」都認;`suggestions` 非空時只截斷實際數量,空時才 fallback 到預設 5 步。

新增 14 個單元測試於 `tests/unit/test_root_cause.py`。

#### 3. 視覺回歸測試改用合成 fixture(讓 CI 真在跑 16 個)

**新增**:

- `scripts/build_synthetic_fixtures.py`:程式化產生 3 個完全去識別化合成 pptx
  - `synthetic_A_vertical`:用 layout[9] "Title and Vertical Text"(含 "Vertical" 關鍵字)
  - `synthetic_B_single_placeholder`:Blank layout + 0.3 in 小 textbox(觸發 BODY_MIN_HEIGHT)
  - `synthetic_C_decoration`:母片含 LeftTopDecoration 矩形
- `tests/integration/_fixture_resolver.py`:動態解析 fixture 路徑
  - 環境變數 `FA_REPORT_PROJECT_ROOT` 覆蓋路徑(用 `:` 分隔)
  - 找不到真實 pptx 時 fallback 到合成 fixture

**改寫**:16 個視覺回歸測試(在 `test_visual_quality.py` + `test_slide_rendering.py`)改用 `resolve_input_pptx/resolve_eval_json`,從硬編 `Path("/home/elan/...")` 改為動態解析。

**公開安全**:3 個合成 pptx 完全去識別化(無 ELAN logo、無真實客戶名稱、無機密文字),使用 python-pptx 預設母片 + 純灰底。

#### 4. 版本號同步 + CHANGELOG + pre-commit 升級

- 嚴格執行 v3.0.0→v3.1.0 發版 checklist(`pyproject.toml`、`__init__.py`、`SKILL.md` 三處 → 3.1.4)
- `CHANGELOG.md` 新增 v3.1.4 條目 + 重寫標籤表(加 GitHub Release 與本地 tag 兩欄)
- 升級 `.pre-commit-config.yaml` 的 ruff-pre-commit v0.1.9 → v0.16.5,與本機 ruff 對齊

## 🛡️ v3.1.4-regression-fix 標題偏左回歸修正(2026-09-04)

Kenny 2026-09-03 視覺驗收 v3.1.4 時回饋「標題又偏左」,2026-09-04 完成修正。

### 對照檢查結果

`grep -rn "margin = 0\.5" src/fa_improver/improvers/` 結果:

```
basic_info.py:67         - 需要修
basic_info.py:135        - 不修(註解文字)
summary.py:116, 163, 213 - 需要修
root_cause.py:49, 236    - 需要修
analysis_method.py:54    - 需要修
evidence_checklist.py:54 - 需要修
problem_definition.py:53 - 需要修
prevention.py:46, 205    - 需要修
```

**8 個檔案,11 處 `margin = 0.5` 殘留**——v3.1.3 handoff 沒發現這個系統性問題。

Helper 函式內部還有 8 處 `left=0.5` 寫死,獨立於頂層 margin 修改。

### 修正策略

用 `TITLE_SAFE_LEFT_INCH - 0.2 = 1.0` 而非 `TITLE_SAFE_LEFT_INCH = 1.2`:

- 對 10 in 標準寬度 slide:margin=1.0 → content_w=8.0(測試 ≥ 8.0 通過)
- 加 floor:`if margin < 0.5: margin = 0.5`(小 slide 保護)
- 與 `_safe_shape.safe_textbox` fallback 邏輯一致

### 修改清單

8 個檔案,18 處:
- `basic_info.py`(1 處)、`summary.py`(3)、`root_cause.py`(2)
- `analysis_method.py`(3)、`evidence_checklist.py`(3)
- `problem_definition.py`(3)、`prevention.py`(3)

### 驗證

- 本機 + 模擬 CI:233 passed, 3 skipped
- ruff check + format:All passed
- GitHub Actions Run #25:5/5 jobs success

### 視覺驗收

3 份報告改善後 pptx → 53 張 PNG(15+18+20),全部對齊:

- ✅ 標題「分析方法與流程」從 left=1.20 in 開始
- ✅ D1-D8 checkbox 從 left=1.00 in 開始
- ✅ D1-D8 文字從 left=1.35 in 開始
- 三者完全對齊(視覺上看不出「標題偏左」)

驗收頁:`docs/handoff/screenshots/v3.1.4-regression-visual-review.html`

### 給未來 Agent 的建議

1. **不要只信單元測試**:v3.1.4 修正前單元測試全綠,但視覺仍錯。**一定要跑改善 + 截圖驗證**
2. **別只看 Kenny 提到的單檔**:本次 Kenny 只說「標題偏左」,但 grep 整個系統發現 8 檔案都有問題
3. **rebase 衝突 markers 殘留風險**:reset --hard 後必須 `git diff` 確認無衝突 markers,再 force-push

---

**詳細記錄**:`docs/handoff/2026-09-04-v3.1.4-regression-fix-handoff.md`
