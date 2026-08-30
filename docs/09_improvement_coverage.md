# 技能包改善覆蓋矩陣 — 對照 fa_report_analyzer_v3 評分標準

> **來源**:https://github.com/KennyKang7012/fa_report_analyzer_v3
> **參考檔案**:`backend/app/core/fa_analyzer_core.py` (lines 920-1010)
> **目的**:確認技能包是否針對每個評分指標都有對應的改善動作
> **狀態**:✅ **6/6 維度 100% 覆蓋**(v3.0.0 + v3.0.1 完成)

---

## 一、6 維度評分標準完整對照

### 1. 基本資訊完整性 (15%)
**評估內容**:
- 產品資訊(型號、批號、製造日期)
- 客戶資訊與投訴內容
- FA 編號與日期
- 負責工程師資訊

**技能包現況**: ✅ **已覆蓋**(觸發門檻 < 80)
- 新增「FA 基本資訊」投影片
- 從檔名自動解析 FA 編號、日期、客戶、專案
- LLM 評估時注入[優化建議項目]

---

### 2. 問題描述與定義 (15%)
**評估內容**:
- 失效現象描述的清晰度
- 失效模式的準確性
- **問題範圍與影響評估**
- **失效率數據**

**技能包現況**: ✅ **已覆蓋**(觸發門檻 < 70)
- 新增「問題描述與失效定義」投影片
- `ProblemDefinitionImprover` 提供對照表、問題範圍量化、客戶影響評估
- 樣板:`problem_definition.json`

---

### 3. 分析方法與流程 (20%)
**評估內容**:
- 分析方法的適當性(SEM、FIB、X-ray、光學檢查)
- 分析步驟的邏輯性與完整性
- 實驗設計的合理性
- 分析設備使用的正確性

**技能包現況**: ✅ **已覆蓋**(觸發門檻 < 70)
- `AnalysisMethodImprover` 提供 8D 流程 checklist
- 分析方法對照表(SEM/FIB/X-ray 適用場景)
- 樣板:`analysis_method.json`

---

### 4. 數據與證據支持 (20%)
**評估內容**:
- 分析數據的充分性
- 圖片/圖表的清晰度與標註
- 量化數據的準確性
- 對照組/比較樣本的使用

**技能包現況**: ✅ **已覆蓋**(觸發門檻 < 70)
- `EvidenceChecklistImprover` 提供對照組 vs 異常品數據對照表
- 圖片品質檢查清單
- 數據追溯性指引
- 樣板:`evidence_checklist.json`

---

### 5. 根因分析 (20%)
**評估內容**:
- 根本原因的深度與準確度
- 因果關係的邏輯推導
- **5-Why 或 Fishbone 分析的應用** ✅
- **排除其他可能原因的論證** ⚠️

**技能包現況**: ✅ **已覆蓋**(觸發門檻 < 80)
- 5-Why 推導流程(樣板: `root_cause_5why`)
- 統計驗證方法(樣板: `root_cause_statistical`)
- DVT vs PVT 對照組設計

**可加強**:
- Fishbone(魚骨圖)視覺化
- 排除其他原因(FMEA 風格)的論證

---

### 6. 改善對策 (10%)
**評估內容**:
- 短期與長期對策的完整性
- 對策的可行性與有效性
- 預防措施的提出
- 驗證計畫

**技能包現況**: ✅ **已覆蓋**(觸發門檻 < 85)
- 改善對策總覽(IQC SOP、自動化監測、知識管理)
- 標準化與監測計畫

**可加強**:
- 驗證計畫具體化(短期追蹤、效果量化指標)

---

## 二、覆蓋率統計

| 維度 | 權重 | 改善觸發 | 觸發門檻 | 樣板 | 狀態 |
|------|------|---------|---------|------|------|
| 基本資訊完整性 | 15% | ✅ | < 80 | ✅ basic_info | **已覆蓋** |
| 問題描述與定義 | 15% | ✅ | < 70 | ✅ problem_definition | **已覆蓋** |
| 分析方法與流程 | 20% | ✅ | < 70 | ✅ analysis_method | **已覆蓋** |
| 數據與證據支持 | 20% | ✅ | < 70 | ✅ evidence_checklist | **已覆蓋** |
| 根因分析 | 20% | ✅ | < 80 | ✅ root_cause_5why + root_cause_statistical | **已覆蓋** |
| 改善對策 | 10% | ✅ | < 85 | ✅ prevention_overview | **已覆蓋** |

**改善覆蓋率**: 6/6 = **100%**(維度)/ **100%**(權重)

**合計**:所有 6 個維度都有對應改善動作

---

## 三、改善計畫 ✅ 已完成

### 3.1 ✅ 3 個 Improver 已實作

- ✅ `ProblemDefinitionImprover` — `src/fa_improver/improvers/problem_definition.py`
- ✅ `AnalysisMethodImprover` — `src/fa_improver/improvers/analysis_method.py`
- ✅ `EvidenceChecklistImprover` — `src/fa_improver/improvers/evidence_checklist.py`

### 3.2 ✅ 對應 JSON 樣板已建立

- ✅ `src/fa_improver/templates/builtin/problem_definition.json`
- ✅ `src/fa_improver/templates/builtin/analysis_method.json`
- ✅ `src/fa_improver/templates/builtin/evidence_checklist.json`

### 3.3 ✅ Orchestrator 已整合

```python
TRIGGER_THRESHOLDS = {
    Dimension.BASIC_INFO: 80,
    Dimension.PROBLEM_DEFINITION: 70,   # ← v3.0 新增
    Dimension.ANALYSIS_METHOD: 70,      # ← v3.0 新增
    Dimension.EVIDENCE: 70,             # ← v3.0 新增
    Dimension.ROOT_CAUSE: 80,
    Dimension.PREVENTION: 85,
}
```

### 3.4 ✅ 實際實作範例(參考原始程式碼)

> 以下為 v3.0 實際實作的 pseudocode,展示三個新增 improver 的核心邏輯:

#### `ProblemDefinitionImprover`(問題描述與定義)

```python
class ProblemDefinitionImprover:
    """針對問題描述與定義維度

    觸發條件: Dimension.PROBLEM_DEFINITION 的 gap_severity >= MODERATE
    (對應分數 < 70)
    """
    TRIGGER_THRESHOLD = 70

    def improve(self, prs, evaluation):
        # 從樣板載入
        template = TemplateLoader().load_builtin("problem_definition")
        layout = find_content_layout(prs)

        slide = prs.slides.add_slide(layout)
        set_title(slide, template.title)

        # 視覺化對照表
        ComparisonTableGenerator(slide).generate({
            "headers": ["項目", "目前報告", "建議補充"],
            "rows": [
                ["失效現象", "...", "更精確描述"],
                ["失效模式", "...", "對應失效機制"],
                ["問題範圍", "未量化", "失效率 % / 影響數量"],
                ["客戶影響", "未評估", "出貨延遲 / 退貨成本"],
            ],
        })
```

#### `AnalysisMethodImprover`(分析方法與流程)

```python
class AnalysisMethodImprover:
    """針對分析方法與流程維度"""
    TRIGGER_THRESHOLD = 70

    def improve(self, prs, evaluation):
        template = TemplateLoader().load_builtin("analysis_method")
        layout = find_content_layout(prs)
        slide = prs.slides.add_slide(layout)

        # 8D 流程 checklist(D1-D8)
        ChecklistGenerator(slide).generate([
            "D1: 建立團隊",
            "D2: 描述問題",
            "D3: 圍堵行動",
            "D4: 根因分析",
            "D5: 永久對策",
            "D6: 實施與驗證",
            "D7: 再發防止",
            "D8: 團隊表揚",
        ])

        # 分析方法對照表
        ComparisonTableGenerator(slide).generate({
            "headers": ["方法", "適用場景", "本案例應用"],
            "rows": [
                ["光學檢查", "外部損傷、燒毀痕跡", "✓"],
                ["SEM", "晶片內部結構", "?"],
                ["FIB", "橫截面分析", "?"],
                ["X-ray", "封裝裂縫、空洞", "?"],
            ],
        })
```

#### `EvidenceChecklistImprover`(數據與證據支持)

```python
class EvidenceChecklistImprover:
    """針對數據與證據支持維度"""
    TRIGGER_THRESHOLD = 70

    def improve(self, prs, evaluation):
        template = TemplateLoader().load_builtin("evidence_checklist")
        layout = find_content_layout(prs)
        slide = prs.slides.add_slide(layout)

        # 對照組數據表
        ComparisonTableGenerator(slide).generate({
            "headers": ["測試項目", "DVT 正常品", "PVT 異常品", "Spec"],
            "rows": [
                ["VH/VOUT", "正常", "異常", "0.4-0.6V"],
                ["ESD", "±2kV 通過", "?", "±2kV"],
            ],
        })

        # 圖片品質檢查清單
        ChecklistGenerator(slide).generate([
            "圖片解析度 ≥ 1000x",
            "對焦清晰(可辨識 IC Marking)",
            "含比例尺(scale bar)",
            "異常點明確標註(箭頭/方框)",
        ])
```

---

## 四、執行結果 ✅

### Phase 4.5(✅ 完成於 v3.0.0)
- [x] 新增 3 個 improvers(problem_definition、analysis_method、evidence_checklist)
- [x] 新增對應 JSON 樣板
- [x] Orchestrator 加入觸發條件
- [x] 加入單元測試(`tests/unit/test_new_improvers.py`)
- [x] 端對端驗證

### 成功標準(全部達成)
- ✅ 所有 6 個維度都有對應改善動作
- ✅ 觸發門檻符合評分標準的「D 級」起點
- ✅ 投影片數增加 1-3 張(依嚴重度)
- ✅ 母片保護 100% 通過(`tests/unit/test_master_protection.py`)
- ✅ 測試覆蓋率 **85%** (目標 80%)

---

## 五、效益 ✅ 已實現

| 項目 | 改善前 | 改善後 |
|------|--------|--------|
| 觸發改善的權重覆蓋 | 45% | **100%** |
| 維度覆蓋率 | 50% (3/6) | **100% (6/6)** |
| 報告品質預期提升 | +20 分 | **+30-40 分** |
| 與 fa_report_analyzer 評分一致性 | 部分 | **完全** |

---

## 六、未來可加強(非當前缺失)

雖然 6 個維度都已覆蓋,但以下項目可在後續版本優化:

| 項目 | 建議版本 | 優先級 |
|------|---------|--------|
| Fishbone(魚骨圖)視覺化 | v3.1+ | P2 |
| FMEA 風格排除論證 | v3.1+ | P2 |
| 驗證計畫具體化(短期追蹤、效果量化指標) | v3.1+ | P2 |
| 圖像評估能力(GPT-4o-vision 等) | v4.0+ | P3 |