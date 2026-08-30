# Phase 2: 樣板系統 TODO

## 目標
把 hard-coded 的版型內容轉為 JSON 樣板,讓使用者可在不改程式碼的情況下調整版型。

## 子任務

### 2.1 設計 SlideTemplate dataclass
- [ ] `src/fa_improver/domain/template.py`
  - 欄位:name, title, layout_name, sections, max_bullets, max_words, visual_element, color_theme
  - 驗證:不允許 max_bullets > 5

### 2.2 設計 TemplateConfig(整套改善的設定)
- [ ] 包含評估閾值、母片保護開關、命名規範等

### 2.3 實作 TemplateLoader(載入 JSON 樣板)
- [ ] 內建樣板目錄: `src/fa_improver/templates/builtin/*.json`
- [ ] 自訂樣板目錄: 使用者可從 CLI 指定 `--template-dir`
- [ ] 樣板繼承:可基於內建樣板覆寫部分欄位

### 2.4 建立 5 個核心 JSON 樣板
- [ ] `basic_info.json` — FA 基本資訊
- [ ] `root_cause_5why.json` — 5-Why 推導
- [ ] `root_cause_statistical.json` — 統計驗證方法
- [ ] `prevention_overview.json` — 改善對策總覽
- [ ] `executive_summary.json` — Executive Summary 強化

### 2.5 改寫 improvers 使用樣板
- [ ] `basic_info.py` 改為讀取 `basic_info.json`
- [ ] `root_cause.py` 改為讀取樣板
- [ ] `prevention.py` 改為讀取樣板
- [ ] `summary.py` 改為讀取樣板

### 2.6 樣板驗證測試
- [ ] `tests/unit/test_template_loader.py`
- [ ] `tests/unit/test_template_validation.py`

### 2.7 CLI 支援自訂樣板
- [ ] `fa-improve --template-dir ./my-templates ...`
- [ ] `fa-improve --template basic_info:custom_name ...`

## 預估工時
6 小時

## 成功標準
- 所有現有 3 份報告改善結果不變(向後相容)
- 至少 10 個新單元測試通過
- 使用者可用 JSON 覆寫任一樣板內容
- 樣板驗證:不能違反品質約束(max_bullets, max_words 等)