# Phase 4.5: 補齊 3 個缺失維度 TODO

## 目標
把覆蓋率從 50% (3/6) 提升到 **100% (6/6)**,觸發改善的權重從 45% 提升到 **100%**

## 子任務

### 4.5.1 新增 ProblemDefinitionImprover
- [ ] `src/fa_improver/improvers/problem_definition.py`
- [ ] 內容:失效現象 vs 失效模式對照表
- [ ] 問題範圍量化(失效率、影響數量)
- [ ] 客戶影響評估
- [ ] 觸發條件:score < 70

### 4.5.2 新增 AnalysisMethodImprover
- [ ] `src/fa_improver/improvers/analysis_method.py`
- [ ] 內容:8D 流程檢查清單(D1-D8)
- [ ] 分析方法對照表(SEM/FIB/X-ray 適用場景)
- [ ] 實驗設計建議
- [ ] 觸發條件:score < 70

### 4.5.3 新增 EvidenceChecklistImprover
- [ ] `src/fa_improver/improvers/evidence_checklist.py`
- [ ] 內容:對照組 vs 異常品 數據對照表
- [ ] 圖片品質檢查清單
- [ ] 數據追溯性指引
- [ ] 觸發條件:score < 70

### 4.5.4 新增 3 個 JSON 樣板
- [ ] `src/fa_improver/templates/builtin/problem_definition.json`
- [ ] `src/fa_improver/templates/builtin/analysis_method.json`
- [ ] `src/fa_improver/templates/builtin/evidence_checklist.json`

### 4.5.5 更新 Orchestrator
- [ ] 加入新維度的觸發條件
- [ ] 加入新 SlideAction
- [ ] 加入新 Improver 執行邏輯

### 4.5.6 測試
- [ ] 3 個新 improver 單元測試
- [ ] Orchestrator 整合測試
- [ ] 端對端真實報告測試

## 預估工時
4-6 小時

## 成功標準
- 6 個維度都有對應改善動作
- 觸發門檻涵蓋所有嚴重缺失(< 70)
- 所有新測試通過
- 母片保護 100% 通過
- 不破壞現有功能(向後相容)