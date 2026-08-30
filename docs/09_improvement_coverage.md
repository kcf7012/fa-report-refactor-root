# 技能包改善覆蓋矩陣 — 對照 fa_report_analyzer_v3 評分標準

> **來源**:https://github.com/KennyKang7012/fa_report_analyzer_v3
> **參考檔案**:`backend/app/core/fa_analyzer_core.py` (lines 920-1010)
> **目的**:確認技能包是否針對每個評分指標都有對應的改善動作

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
- **問題範圍與影響評估** ⚠️
- **失效率數據** ⚠️

**技能包現況**: ❌ **未觸發**(完全沒處理)
- 沒有針對此維度的改善動作
- 若分數低於閾值,應新增:

**建議改善動作**:
- `add_problem_definition_slide`
  - 失效現象 vs 失效模式 對照表
  - 問題範圍量化(失效率、影響產品數量、市場規模)
  - 客戶影響評估

---

### 3. 分析方法與流程 (20%)
**評估內容**:
- 分析方法的適當性(SEM、FIB、X-ray、光學檢查)
- 分析步驟的邏輯性與完整性
- 實驗設計的合理性
- 分析設備使用的正確性

**技能包現況**: ❌ **未觸發**(完全沒處理)
- 沒有針對此維度的改善動作

**建議改善動作**:
- `add_analysis_method_slide`
  - 8D 流程檢查清單(D1-D8)
  - 分析方法對照表(SEM/FIB/X-ray 適用場景)
  - 實驗設計 SOP 範本

---

### 4. 數據與證據支持 (20%)
**評估內容**:
- 分析數據的充分性
- 圖片/圖表的清晰度與標註
- 量化數據的準確性
- 對照組/比較樣本的使用

**技能包現況**: ❌ **未觸發**(完全沒處理)

**建議改善動作**:
- `add_evidence_checklist_slide`
  - 對照組 vs 異常品 數據對照表(已在樣板預備)
  - 圖片品質檢查清單(解析度、對焦、比例尺)
  - 數據追溯性指引(每個數據的來源)

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
| 問題描述與定義 | 15% | ❌ | — | ❌ | **缺失** |
| 分析方法與流程 | 20% | ❌ | — | ❌ | **缺失** |
| 數據與證據支持 | 20% | ❌ | — | ❌ (預備) | **缺失** |
| 根因分析 | 20% | ✅ | < 80 | ✅ 兩種 | **已覆蓋** |
| 改善對策 | 10% | ❌ (預備) | < 85 | ❌ (預備) | **部分覆蓋** |

**改善覆蓋率**: 3/6 = 50%(維度)/ 45%(權重)

**合計**:45% 的權重有改善動作,但 **55% 的權重沒有處理**

---

## 三、改善計畫(Phase 4.5 / Phase 5 新增)

### 3.1 新增 3 個 Improver

#### `add_problem_definition_slide`(問題描述與定義)

```python
class ProblemDefinitionImprover:
    """針對問題描述與定義維度
    
    觸發條件: gap_severity >= MODERATE (分數 < 70)
    
    內容:
    - 失效現象 vs 失效模式 對照表
    - 問題範圍量化(失效率、影響數量)
    - 客戶影響評估
    """
    TRIGGER_THRESHOLD = 70  # < 70 觸發
    
    def add_slide(self, prs, evaluation):
        layout = find_content_layout(prs)
        slide = prs.slides.add_slide(layout)
        
        # 標題
        set_title(slide, "問題描述與失效定義")
        
        # 視覺化對照表
        ComparisonTableGenerator(
            slide, left=0.5, top=1.5, width=6, height=2.5
        ).generate({
                "headers": ["項目", "目前報告", "建議補充"],
                "rows": [
                    ["失效現象", "...", "更精確描述"],
                    ["失效模式", "...", "對應失效機制"],
                    ["問題範圍", "未量化", "失效率 % / 影響數量"],
                    ["客戶影響", "未評估", "出貨延遲 / 退貨成本"],
                ],
            })
        
        # 失效率資料表
        add_failure_rate_table(slide)
```

#### `add_analysis_method_slide`(分析方法與流程)

```python
class AnalysisMethodImprover:
    """針對分析方法與流程維度
    
    觸發條件: gap_severity >= MODERATE
    
    內容:
    - 8D 流程檢查清單
    - 適用方法建議(SEM/FIB/X-ray)
    - 實驗設計 SOP 連結
    """
    TRIGGER_THRESHOLD = 70
    
    def add_slide(self, prs, evaluation):
        # 8D 流程 checklist
        ChecklistGenerator(...).generate([
            {"text": "D1: 建立團隊", "checked": False},
            {"text": "D2: 描述問題", "checked": False},
            {"text": "D3: 圍堵行動", "checked": False},
            {"text": "D4: 根因分析", "checked": False},
            {"text": "D5: 永久對策", "checked": False},
            {"text": "D6: 實施與驗證", "checked": False},
            {"text": "D7: 再發防止", "checked": False},
            {"text": "D8: 團隊表揚", "checked": False},
        ])
        
        # 分析方法對照表
        ComparisonTableGenerator(...).generate({
            "headers": ["方法", "適用場景", "本案例應用"],
            "rows": [
                ["光學檢查", "外部損傷、燒毀痕跡", "✓"],
                ["SEM", "晶片內部結構", "?"],
                ["FIB", "橫截面分析", "?"],
                ["X-ray", "封裝裂縫、空洞", "?"],
            ],
        })
```

#### `add_evidence_checklist_slide`(數據與證據支持)

```python
class EvidenceChecklistImprover:
    """針對數據與證據支持維度
    
    觸發條件: gap_severity >= MODERATE
    
    內容:
    - 對照組 vs 異常品 數據
    - 圖片品質檢查清單
    - 數據追溯性指引
    """
    TRIGGER_THRESHOLD = 70
    
    def add_slide(self, prs, evaluation):
        # 對照組數據表
        ComparisonTableGenerator(...).generate({
            "headers": ["測試項目", "DVT 正常品", "PVT 異常品", "Spec"],
            "rows": [
                ["VH/VOUT", "正常", "異常", "0.4-0.6V"],
                ["ESD", "±2kV 通過", "?", "±2kV"],
            ],
        })
        
        # 圖片品質檢查清單
        ChecklistGenerator(...).generate([
            "圖片解析度 ≥ 1000x",
            "對焦清晰(可辨識 IC Marking)",
            "含比例尺(scale bar)",
            "異常點明確標註(箭頭/方框)",
        ])
```

### 3.2 Orchestrator 更新

```python
TRIGGER_THRESHOLDS = {
    Dimension.BASIC_INFO: 80,
    Dimension.PROBLEM_DEF: 70,      # ← 新增
    Dimension.METHOD: 70,            # ← 新增
    Dimension.EVIDENCE: 70,          # ← 新增
    Dimension.ROOT_CAUSE: 80,
    Dimension.PREVENTION: 85,
}
```

---

## 四、執行計畫

### Phase 4.5(立即)
- [ ] 新增 3 個 improvers(problem_definition、analysis_method、evidence_checklist)
- [ ] 新增對應 JSON 樣板
- [ ] Orchestrator 加入觸發條件
- [ ] 加入 15+ 個測試
- [ ] 端對端驗證

### 預估工時
4-6 小時

### 成功標準
- 所有 6 個維度都有對應改善動作
- 觸發門檻符合評分標準的「D 級」起點
- 投影片數增加 1-3 張(依嚴重度)
- 母片保護 100% 通過
- 測試覆蓋率 ≥ 80%

---

## 五、效益

| 項目 | 改善前 | 改善後 |
|------|--------|--------|
| 觸發改善的權重覆蓋 | 45% | 100% |
| 維度覆蓋率 | 50% (3/6) | 100% (6/6) |
| 報告品質預期提升 | +20 分 | +30-40 分 |
| 與 fa_report_analyzer 評分一致性 | 部分 | 完全 |