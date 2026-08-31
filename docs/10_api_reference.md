# FA Report Improvement v3.0 — API 參考手冊

> **對象版本**:v3.0.1
> **範圍**:`src/fa_improver/` 內 35 個模組的公開 API
> **目的**:給進階使用者 / 整合者 / 二次開發者使用

---

## 目錄

- [1. CLI 入口](#1-cli-入口)
- [2. Domain — 領域模型](#2-domain--領域模型)
- [3. Parsers — 輸入解析](#3-parsers--輸入解析)
- [4. Layout — 版面處理](#4-layout--版面處理)
- [5. Improvers — 改善動作](#5-improvers--改善動作)
- [6. Templates — 樣板系統](#6-templates--樣板系統)
- [7. Visuals — 視覺元素](#7-visuals--視覺元素)
- [8. LLM — LLM 整合](#8-llm--llm-整合)
- [9. Utils — 公用工具](#9-utils--公用工具)

---

## 1. CLI 入口

### `fa_improver.cli:main()`

CLI 主入口,由 `fa-improve` console script 呼叫。

**位置**:`src/fa_improver/cli.py`

**呼叫方式**:
```bash
# 從技能包目錄
PYTHONPATH=src python -m fa_improver <input> [options]

# 安裝後
fa-improve <input> [options]
```

**參數**:

| 參數 | 型別 | 預設 | 說明 |
|------|------|------|------|
| `input` | str(必填) | — | 輸入 pptx/ppt 檔案路徑 |
| `-e`, `--eval` | str | None | 評估檔(JSON 或 TXT) |
| `--llm-provider` | str | None | `openai` / `mock` |
| `--model` | str | `gpt-4o-mini` | LLM 模型 |
| `-o`, `--output` | str(必填) | — | 輸出 pptx 路徑 |
| `--template-dir` | str | None | 自訂樣板目錄 |
| `-v`, `--verbose` | flag | False | 詳細輸出 |

**回傳**: `int` (exit code,0 = 成功)

**範例**:
```python
import sys
from fa_improver.cli import main

sys.argv = ['fa-improve', 'report.pptx', '--eval', 'eval.json', '--output', 'out.pptx']
sys.exit(main())
```

---

## 2. Domain — 領域模型

### 2.1 `Dimension` (Enum)

**位置**:`src/fa_improver/domain/evaluation.py`

6 個評估維度:

| 值 | 權重 | 觸發門檻 |
|----|------|---------|
| `BASIC_INFO` | 15% | < 80 |
| `PROBLEM_DEFINITION` | 15% | < 70 |
| `ANALYSIS_METHOD` | 20% | < 70 |
| `EVIDENCE` | 20% | < 70 |
| `ROOT_CAUSE` | 20% | < 80 |
| `PREVENTION` | 10% | < 85 |

### 2.2 `GapSeverity` (Enum)

| 值 | 數值 | 說明 |
|----|------|------|
| `OK` | 0 | 不需改善 |
| `MINOR` | 1 | 小幅改善 |
| `MODERATE` | 2 | 中度改善 |
| `SEVERE` | 3 | 大幅改善 |

### 2.3 `DimensionScore`

```python
@dataclass
class DimensionScore:
    dimension: Dimension
    score: float                    # 0-100
    weight: float                   # 0-1
    notes: str = ""
    
    @property
    def severity(self) -> GapSeverity: ...
    
    @property
    def gap(self) -> float: ...      # 100 - score
```

### 2.4 `EvaluationResult`

```python
@dataclass
class EvaluationResult:
    total_score: float                          # 0-100
    grade: str                                  # A/B/C/D/F
    dimensions: list[DimensionScore]
    summary: str = ""
    improvements: list[Improvement] = field(default_factory=list)
    
    def gap(self, dim: Dimension) -> float: ...
    def severity(self, dim: Dimension) -> GapSeverity: ...
    def needs_improvement(self, dim: Dimension) -> bool: ...
```

### 2.5 `Suggestion` / `ActionItem` / `Improvement`

```python
@dataclass
class Suggestion:
    dimension: Dimension
    text: str
    priority: Priority = Priority.MEDIUM

@dataclass
class ActionItem:
    description: str
    owner: str = ""
    deadline: str = ""

@dataclass
class Improvement:
    title: str
    rationale: str
    actions: list[ActionItem]
```

### 2.6 `SlideTemplate` / `TemplateSection`

```python
@dataclass
class TemplateSection:
    title: str
    bullets: list[str]
    visual: VisualElement | None = None
    notes: str = ""

@dataclass
class SlideTemplate:
    name: str
    title: str
    sections: list[TemplateSection]
    color_theme: ColorTheme = ColorTheme.PRIMARY
    max_bullets_per_section: int = 4
    
    def validate(self) -> None:
        """驗證樣板規範,違反則拋 TemplateValidationError"""
```

### 2.7 例外

- `TemplateValidationError(Exception)` — 樣板驗證失敗

---

## 3. Parsers — 輸入解析

### 3.1 `EvaluationParser`

**位置**:`src/fa_improver/parsers/evaluation_parser.py`

```python
class EvaluationParser:
    def parse(self, file_path: Path) -> EvaluationResult:
        """自動偵測 JSON / TXT 格式"""
```

支援格式:
- **JSON**:`fa_report_analyzer_v3` 評估結果
- **TXT**:文字版評估輸出

### 3.2 `FilenameParser`

**位置**:`src/fa_improver/parsers/filename_parser.py`

```python
class FilenameParser:
    def parse(self, filename: str) -> ReportContext:
        """從檔名提取 FA 編號、客戶、產品資訊"""
```

範例:`Kobo_ZHT_RA6080_SPcomFailI.pptx` → 
```
{
  "customer": "Kobo",
  "model": "ZHT_RA6080",
  "defect_type": "SPcomFail",
  "severity": "I"  (I/II/III)
}
```

---

## 4. Layout — 版面處理

### 4.1 `MasterProtector`(★ 關鍵)

**位置**:`src/fa_improver/layout/protector.py`

**職責**:確保改善過程不修改母片。

```python
class MasterProtector:
    def __init__(self, prs: Presentation): ...
    
    def snapshot(self) -> MasterSnapshot:
        """擷取改善前的母片狀態"""
    
    def assert_unchanged(self, original: MasterSnapshot) -> None:
        """改善後驗證母片未變(失敗則拋 MasterProtectionError)"""
    
    def assert_can_add_slide(self, layout_name: str) -> None:
        """確認 layout 已存在(不可新增 layout)"""
```

**例外**:
- `MasterProtectionError(Exception)` — 母片違規

### 4.2 `find_content_layout()`

**位置**:`src/fa_improver/layout/selector.py`

```python
def find_content_layout(prs: Presentation, prefer_title: bool = True) -> SlideLayout:
    """智慧選擇合適的 layout(避免 cover/封面)"""
```

---

## 5. Improvers — 改善動作

### 5.1 `BaseImprover`(抽象)

**位置**:`src/fa_improver/improvers/base.py`

```python
class BaseImprover(ABC):
    @abstractmethod
    def is_applicable(self, evaluation: EvaluationResult) -> bool: ...
    
    @abstractmethod
    def improve(self, prs: Presentation, evaluation: EvaluationResult) -> int:
        """回傳新增的投影片數量"""
```

### 5.2 8 種 Improver 實作

| 類別 | 觸發條件 | 用途 |
|------|---------|------|
| `BasicInfoImprover` | score < 80 | 新增 FA 基本資訊 |
| `ProblemDefinitionImprover` | score < 70 | 新增問題描述 |
| `AnalysisMethodImprover` | score < 70 | 新增 8D 流程 |
| `EvidenceChecklistImprover` | score < 70 | 新增證據清單 |
| `RootCauseImprover` | score < 80 | 5-Why + 統計驗證 |
| `PreventionImprover` | score < 85 | 改善對策總覽 |
| `SummaryImprover` | always | 強化 Summary |
| `Orchestrator` | — | 編排多個 improver |

### 5.3 `ImprovementOrchestrator`

**位置**:`src/fa_improver/improvers/orchestrator.py`

```python
class ImprovementOrchestrator:
    def __init__(self, improvers: list[BaseImprover] | None = None): ...
    
    def plan(self, evaluation: EvaluationResult) -> list[SlideAction]: ...
    def execute(self, prs: Presentation, evaluation: EvaluationResult) -> int: ...
```

---

## 6. Templates — 樣板系統

### 6.1 內建樣板

**位置**:`src/fa_improver/templates/builtin/`

8 個 JSON 樣板:

| 檔案 | 用途 |
|------|------|
| `basic_info.json` | FA 基本資訊 |
| `problem_definition.json` | 問題描述 |
| `analysis_method.json` | 8D 流程 |
| `evidence_checklist.json` | 證據清單 |
| `root_cause_5why.json` | 5-Why 推導 |
| `root_cause_statistical.json` | 統計驗證方法 |
| `prevention_overview.json` | 改善對策總覽 |
| `executive_summary.json` | Executive Summary 強化 |

### 6.2 `TemplateLoader`

**位置**:`src/fa_improver/templates/loader.py`

```python
class TemplateLoader:
    def __init__(self, template_dir: Path | None = None): ...
    
    def load(self, name: str) -> SlideTemplate: ...
    def list_available(self) -> list[str]: ...
    
    # 內建樣板捷徑
    def load_builtin(self, name: str) -> SlideTemplate: ...
```

**BUILTIN_TEMPLATES**:`dict[str, SlideTemplate]`,所有內建樣板

### 6.3 自訂樣板

使用者可在 CLI 指定 `--template-dir ./my-templates/`,覆寫或新增樣板。

範例:`my-templates/basic_info.json`
```json
{
  "name": "company_basic_info",
  "title": "公司專屬 FA 基本資訊",
  "sections": [
    {
      "title": "案件資訊",
      "bullets": ["FA 編號:...", "客戶:..."],
      "visual": "checklist"
    }
  ],
  "color_theme": "primary"
}
```

---

## 7. Visuals — 視覺元素

### 7.1 5 種視覺元素

**位置**:`src/fa_improver/visuals/base.py`

| 類別 | 視覺 | 用途 |
|------|------|------|
| `ChecklistGenerator` | ☐ ☑ checkbox | 待辦清單 |
| `FlowDiagramGenerator` | 矩形 + 箭頭 | 5-Why 流程 |
| `ComparisonTableGenerator` | Native PPT table | DVT vs PVT 對照 |
| `ProgressBarGenerator` | 矩形填充 | 6 維度評分視覺化 |
| `TimelineGenerator` | 箭頭 + 階段 | 立即/短期/中期/長期 |

### 7.2 統一 API

```python
class VisualGenerator(ABC):
    @abstractmethod
    def generate(
        self,
        slide: Slide,
        section: TemplateSection,
        content: dict[str, Any]
    ) -> None: ...
```

### 7.3 `ColorPalette`

**位置**:`src/fa_improver/visuals/colors.py`

ELAN 主色系:
- `ELAN_BLUE = RGBColor(0x1F, 0x4E, 0x79)` (深藍主色)
- `ELAN_LIGHT_BLUE = RGBColor(0x5B, 0x9B, 0xD5)` (輔助)
- `ELAN_RED = RGBColor(0xC0, 0x00, 0x00)` (強調)

---

## 8. LLM — LLM 整合

### 8.1 `LLMClient`(Protocol)

**位置**:`src/fa_improver/llm/base.py`

```python
class LLMClient(Protocol):
    def evaluate(
        self,
        pptx_content: bytes,
        rubric: str,
        model: str = "gpt-4o-mini"
    ) -> EvaluationResult: ...
```

### 8.2 實作

| 類別 | 位置 | 用途 |
|------|------|------|
| `OpenAIClient` | `llm/openai_client.py` | OpenAI API |
| `MockLLMClient` | `llm/mock_client.py` | 測試用,離線 |
| `LLMEvaluator` | `llm/evaluator.py` | 將 LLM 結果轉為 EvaluationResult |

### 8.3 使用範例

```python
from fa_improver.llm import OpenAIClient, LLMEvaluator

client = OpenAIClient(api_key="sk-...")
evaluator = LLMEvaluator(client)

with open("report.pptx", "rb") as f:
    pptx_content = f.read()

result = evaluator.evaluate(pptx_content)
print(f"總分: {result.total_score}, 等級: {result.grade}")
```

### 8.4 Prompts

**位置**:`src/fa_improver/llm/prompts.py`

- `SYSTEM_PROMPT` — 系統提示詞
- `USER_PROMPT_TEMPLATE` — 使用者提示詞樣板(含 rubric)

---

## 9. Utils — 公用工具

### 9.1 `PPTConverter`

**位置**:`src/fa_improver/utils/ppt_converter.py`

```python
class PPTConverter:
    def convert_if_needed(self, file_path: Path) -> Path | None:
        """若輸入是 .ppt,自動轉為 .pptx"""
    
    def cleanup(self) -> None:
        """清理轉換過程中的臨時檔"""
```

支援:LibreOffice(跨平台)、pywin32(Windows only)

### 9.2 環境變數

| 變數 | 預設 | 說明 |
|------|------|------|
| `OPENAI_API_KEY` | — | OpenAI API key |
| `FA_IMPROVER_MODEL` | `gpt-4o-mini` | 預設 LLM 模型 |
| `FA_IMPROVER_TEMPLATE_DIR` | — | 預設自訂樣板目錄 |
| `FA_IMPROVER_LOG_LEVEL` | `INFO` | 日誌等級 |

### 9.3 退出碼

| Code | 意義 |
|------|------|
| 0 | 成功 |
| 1 | 一般錯誤(檔案不存在、解析失敗) |
| 2 | 母片保護違規 |
| 3 | API 錯誤(LLM 評估失敗) |
| 4 | 樣板錯誤 |

---

## 附錄:完整模組清單

```
src/fa_improver/
├── __init__.py
├── __main__.py              # python -m fa_improver 入口
├── cli.py                   # argparse CLI
│
├── domain/                  # 純資料模型
│   ├── evaluation.py        # Dimension, EvaluationResult, DimensionScore
│   ├── suggestion.py        # Suggestion, ActionItem, Improvement
│   └── template.py          # SlideTemplate, TemplateSection
│
├── parsers/
│   ├── evaluation_parser.py # JSON / TXT 解析
│   └── filename_parser.py   # 從檔名提取 metadata
│
├── layout/
│   ├── selector.py          # find_content_layout()
│   └── protector.py         # MasterProtector(★ 母片保護)
│
├── improvers/               # 8 種改善動作 + 編排器
│   ├── base.py
│   ├── basic_info.py
│   ├── problem_definition.py
│   ├── analysis_method.py
│   ├── evidence_checklist.py
│   ├── root_cause.py
│   ├── prevention.py
│   ├── summary.py
│   └── orchestrator.py      # ImprovementOrchestrator
│
├── templates/
│   ├── loader.py            # TemplateLoader
│   └── builtin/             # 8 個 JSON 樣板
│
├── visuals/                 # 5 種視覺元素
│   ├── base.py              # VisualGenerator 基類 + 5 種實作
│   └── colors.py            # ColorPalette
│
├── llm/                     # LLM 整合
│   ├── base.py              # LLMClient Protocol
│   ├── openai_client.py
│   ├── mock_client.py
│   ├── evaluator.py
│   └── prompts.py
│
└── utils/
    └── ppt_converter.py     # .ppt → .pptx 自動轉換
```

---

## 變更紀律

| 版本 | 日期 | 主要變更 |
|------|------|---------|
| v3.0.1 | 2026-08-31 | 加入 ppt_converter / pre-commit / uv.lock, ruff 全綠 |
| v3.0.0 | 2026-08-31 | 模組化 + 6 維度完整覆蓋 + LLM 整合 |

## 相關文件

- [`02_refactor_plan.md`](02_refactor_plan.md) — 重構計劃與母片保護原則
- [`USER_GUIDE.md`](USER_GUIDE.md) — 終端使用者手冊
- [`TESTING.md`](TESTING.md) — 測試策略
- [`08_uv_integration.md`](08_uv_integration.md) — uv 安裝整合

---

**授權**:MIT
**維護**:Kenny Kang <kenny.kang@elan.com.tw>