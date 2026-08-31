# Phase 4.5: 補齊 3 個缺失維度 TODO

> **狀態**:✅ **全部完成於 v3.0.0**(2026-08-31)
> **6/6 維度 100% 覆蓋**:從 v2.3.0 的 3/6(50%)進步到 v3.0 的 6/6(100%)

## 目標
把覆蓋率從 50% (3/6) 提升到 **100% (6/6)**,觸發改善的權重從 45% 提升到 **100%**

## 子任務

### 4.5.1 新增 ProblemDefinitionImprover
- [x] ✅ `src/fa_improver/improvers/problem_definition.py`(v3.0.0 完成)
- [x] ✅ 內容:失效現象 vs 失效模式對照表
- [x] ✅ 問題範圍量化(失效率、影響數量)
- [x] ✅ 客戶影響評估
- [x] ✅ 觸發條件:score < 70

### 4.5.2 新增 AnalysisMethodImprover
- [x] ✅ `src/fa_improver/improvers/analysis_method.py`(v3.0.0 完成)
- [x] ✅ 內容:8D 流程檢查清單(D1-D8)
- [x] ✅ 分析方法對照表(SEM/FIB/X-ray 適用場景)
- [x] ✅ 實驗設計建議
- [x] ✅ 觸發條件:score < 70

### 4.5.3 新增 EvidenceChecklistImprover
- [x] ✅ `src/fa_improver/improvers/evidence_checklist.py`(v3.0.0 完成)
- [x] ✅ 內容:對照組 vs 異常品 數據對照表
- [x] ✅ 圖片品質檢查清單
- [x] ✅ 數據追溯性指引
- [x] ✅ 觸發條件:score < 70

### 4.5.4 新增 3 個 JSON 樣板
- [x] ✅ `src/fa_improver/templates/builtin/problem_definition.json`
- [x] ✅ `src/fa_improver/templates/builtin/analysis_method.json`
- [x] ✅ `src/fa_improver/templates/builtin/evidence_checklist.json`

### 4.5.5 更新 Orchestrator
- [x] ✅ 加入新維度的觸發條件
- [x] ✅ 加入新 SlideAction
- [x] ✅ 加入新 Improver 執行邏輯

### 4.5.6 測試
- [x] ✅ 3 個新 improver 單元測試(`tests/unit/test_new_improvers.py`)
- [x] ✅ Orchestrator 整合測試
- [x] ✅ 端對端真實報告測試

## 預估工時
4-6 小時

## 成功標準
- [x] ✅ 6 個維度都有對應改善動作(從 3/6 → 6/6)
- [x] ✅ 觸發門檻涵蓋所有嚴重缺失(< 70)
- [x] ✅ 所有新測試通過
- [x] ✅ 母片保護 100% 通過
- [x] ✅ 不破壞現有功能(向後相容)

## 實際交付
- 3 個 improver 模組:`problem_definition.py` / `analysis_method.py` / `evidence_checklist.py`(提供 `add_*_slide` 函式)
- 3 個 JSON 樣板:`problem_definition.json` / `analysis_method.json` / `evidence_checklist.json`
- 測試:`tests/unit/test_new_improvers.py`
- Orchestrator 整合:`from .problem_definition import add_problem_definition_slide` 等 3 個 import
- 觸發覆蓋:從 45% 提升到 100% 權重

對應 git tag: `v3.0.0`