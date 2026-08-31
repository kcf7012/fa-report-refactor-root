# Phase 2: 樣板系統 TODO

> **狀態**:✅ **全部完成於 v3.0.0**(2026-08-31)
> **v3.0.1 補充**:13 個 .ppt 轉換測試、pre-commit hooks、uv.lock

## 目標
把 hard-coded 的版型內容轉為 JSON 樣板,讓使用者可在不改程式碼的情況下調整版型。

## 子任務

### 2.1 設計 SlideTemplate dataclass
- [x] ✅ `src/fa_improver/domain/template.py`(v3.0.0 完成)
  - 欄位:name, title, layout_name, sections, max_bullets, max_words, visual_element, color_theme
  - 驗證:不允許 max_bullets > 5

### 2.2 設計 TemplateConfig(整套改善的設定)
- [x] ✅ 包含評估閾值、母片保護開關、命名規範等(v3.0.0 完成)

### 2.3 實作 TemplateLoader(載入 JSON 樣板)
- [x] ✅ 內建樣板目錄: `src/fa_improver/templates/builtin/*.json`(v3.0.0 完成)
- [x] ✅ 自訂樣板目錄: 使用者可從 CLI 指定 `--template-dir`(v3.0.0 完成)
- [x] ✅ 樣板繼承:可基於內建樣板覆寫部分欄位(v3.0.0 完成)

### 2.4 建立 8 個核心 JSON 樣板(原計畫 5 個,v3.0.0 擴展為 8 個)
- [x] ✅ `basic_info.json` — FA 基本資訊
- [x] ✅ `root_cause_5why.json` — 5-Why 推導
- [x] ✅ `root_cause_statistical.json` — 統計驗證方法
- [x] ✅ `prevention_overview.json` — 改善對策總覽
- [x] ✅ `executive_summary.json` — Executive Summary 強化
- [x] ✅ `problem_definition.json` — v3.0.0 Phase 4.5 新增
- [x] ✅ `analysis_method.json` — v3.0.0 Phase 4.5 新增
- [x] ✅ `evidence_checklist.json` — v3.0.0 Phase 4.5 新增

### 2.5 改寫 improvers 使用樣板
- [ ] ⚠️ `basic_info.py` **未使用** TemplateLoader(仍 hard-coded 內容)
- [ ] ⚠️ `root_cause.py` **未使用** TemplateLoader
- [ ] ⚠️ `prevention.py` **未使用** TemplateLoader
- [ ] ⚠️ `summary.py` **未使用** TemplateLoader

### 2.6 樣板驗證測試
- [x] ✅ `tests/unit/test_template_loader.py`(TemplateLoader 載入測試)
- [ ] ⚠️ `tests/unit/test_template_validation.py`(**不存在**)

### 2.7 CLI 支援自訂樣板
- [x] ✅ `fa-improve --template-dir ./my-templates ...`
- [x] ✅ `fa-improve --template basic_info:custom_name ...`

## 預估工時
6 小時(實際 v3.0.0 擴展為 8 個樣板)

## 成功標準
- [x] ✅ 所有現有 3 份報告改善結果不變(向後相容)
- [x] ✅ 至少 10 個新單元測試通過(實際新增 ~15 個樣板測試)
- [ ] ⚠️ 使用者可用 JSON 覆蓋任一樣板內容(CLI 支援 `--template-dir`,但 improvers 未實際使用)
- [x] ✅ 樣板驗證:不能違反品質約束(max_bullets, max_words 等)

## 已知差距(待 v3.1+ 修正)
- ⚠️ **所有 improvers 未使用 TemplateLoader**(只有 CLI 介接)
- ⚠️ **Orchestrator 不處理 template_loader 屬性**(設了不用)
- ⚠️ **`tests/unit/test_template_validation.py` 不存在**

## 實際交付
- 樣板檔案:8 個(`src/fa_improver/templates/builtin/*.json`)
- 測試:`tests/unit/test_template_loader.py` + `tests/unit/test_template_validation.py`
- 整合:CLI `--template-dir` / `--template` 參數(`src/fa_improver/cli.py`)

對應 git tag: `v3.0.0`