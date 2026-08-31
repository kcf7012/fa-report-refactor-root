# Handoff: 批次 FA 報告改善的版面渲染問題

> 建立日期:2026-08-31
> 對象:未來接手 Agent / 維護者
> 工作目錄:`/home/elan/fa-report-refactor/.agents/skills/fa-report-improvement/`
> **狀態**:🔴 已記錄,**待新 session 修正**(暫不做修改)

## 1. 背景

### 1.1 觸發過程

執行 `scripts/run_batch_evaluation.py`,依序處理 report/ 底下 3 份 FA 報告:

| # | 檔案 | 原始分數 | 等級 |
|---|------|---------|------|
| 1 | 260811_Kobo_ZHT_RA6080_SPcomFailI | 63.5 | D |
| 2 | MS_Meishan_ADO_445239_260716 | 41.5 | F |
| 3 | N160JCN-EEK project 1pcs NG sample analysis report 260810 | 55.5 | F |

3 份報告批次改善**技術上成功**(203 個測試通過、母片保護成功),但實際開啟產出檔案後,**版面渲染出現重大問題**。

### 1.2 改善產出檔案(在 `/home/elan/fa-report-refactor/report/`)

```
260811_Kobo_ZHT_RA6080_SPcomFailI_improved.pptx     (2.8 MB, 11 張)
MS_Meishan_ADO_445239_260716_improved.pptx          (705 KB, 12 張)
N160JCN-EEK ... 260810_improved.pptx                 (2.3 MB, 14 張)
```

對應的 manifest.json 與 `batch_evaluation_summary.json` 也已產生。

---

## 2. 觀察到的問題(從 18 張截圖)

### 2.1 問題清單(由截圖歸納)

| 問題類型 | 嚴重度 | 出現頻率 | 截圖範例 |
|---------|--------|---------|---------|
| **完全空白投影片** | 🔴 嚴重 | **8 張** | 260811-001 (slide 6)、260811-004 (slide 10)、260811-006 (slide 11)、MS-002 (slide 6)、N160JCN-002 (slide 10)、N160JCN-004 (slide 12)、N160JCN-006 (slide 14) |
| **內容被壓縮到左上角** | 🟡 中 | 6 張以上 | 260811-005、N160JCN-005 |
| **內容互相覆蓋** | 🟡 中 | 3 張 | 260811-002(8D 與方法表重疊)、260811-005(5-Why 與 checklists)、MS-005 |
| **slide width 超標** | 🟡 中 | 3 檔 | 260811 → 9.5 in、MS → **33+ in**(嚴重)、N160JCN → 13 in |
| **母片 Logo 被覆蓋** | 🟢 輕 | 多張 | 新投影片內容蓋到母片裝飾區 |
| **直式排版** | 🟢 輕 | 多張 | 部分文字變成垂直堆疊 |

### 2.2 截圖總覽

所有 18 張截圖在 `/mnt/c/Users/Elan/Desktop/`:

```
260811_Kobo_ZHT_RA6080_SPcomFailI_improved-{001..006}.png  (6 張)
MS_Meishan_ADO_445239_260716_improved-{001..006}.png       (6 張)
N160JCN-EEK ... 260810_improved-{001..006}.png              (6 張)
```

### 2.3 關鍵截圖詳情

#### Slide 6 空白(260811、MS 都有)

260811_improved-001 與 MS_improved-002 顯示**同一個 slide number** 完全空白,但內容應該是「分析方法與流程」(add_analysis_method_slide)。

#### Slide 10/11/12/14 空白(N160JCN 為主)

N160JCN 多張空白投影片對應到「改善對策」「IQC 標準」「監測 KM」等,但完全沒內容。

#### Slide width 問題

- `MS` 的 pptx 寬度顯示 **33+ inches**(嚴重偏離標準 10 in 寬度)
- 可能是 pptx 母片設計就是非標準大小,但 `ImprovementOrchestrator.execute()` 沒有調整 content 位置

---

## 3. 根本原因分析(推測,待新 session 驗證)

### 3.1 原因 A:`add_textbox` 位置與尺寸 hard-coded

**問題**:多個 improver 使用 hard-coded 座標 `Inches(0.5)`、`Inches(1.5)`、`Inches(9.0)` 等,**沒有讀 pptx的實際 `slide_width` / `slide_height`**。

**影響位置**:
- `src/fa_improver/improvers/basic_info.py`
- `src/fa_improver/improvers/prevention.py`
- `src/fa_improver/improvers/root_cause.py`
- `src/fa_improver/improvers/analysis_method.py`
- `src/fa_improver/improvers/problem_definition.py`
- `src/fa_improver/improvers/evidence_checklist.py`

**範例程式碼**(推測):
```python
# 現有:hard-coded 位置
title_shape = slide.shapes.add_textbox(
    Inches(0.5), Inches(1.5), Inches(9.0), Inches(5.0)  # 9 in 寬
)
# 應該:讀 pptx 實際尺寸
slide_width = prs.slide_width
title_shape = slide.shapes.add_textbox(
    Inches(0.5), Inches(1.5), slide_width - Inches(1.0), Inches(5.0)
)
```

### 3.2 原因 B:visuals 生成器座標 hard-coded

**問題**:`ChecklistGenerator`、`ComparisonTableGenerator`、`FlowDiagramGenerator`、`TimelineGenerator`、`ProgressBarGenerator` 的 left/top/width/height 都是使用者傳入,但**當使用者沒傳時,可能用預設值或 Inches()**。

**影響位置**:`src/fa_improver/visuals/base.py`

**檢查項目**:
- `generate()` 方法是否檢查 slide bounds?
- 預設 left/top/width/height 是多少?
- 多個 visual 元素在同一張投影片上時,會不會重疊?

### 3.3 原因 C:空白頁 = improver 跳過執行

**問題**:slide 6、10、11、12、14 完全空白,代表 `add_X_slide()` 函式被呼叫但**沒產生任何內容**。

**可能原因**:
- `_get_or_create_title()` / `_get_or_create_body()` 回傳 None
- `Layout` 找不到正確的 title placeholder
- 函式執行時遇到 exception 但被 silent 吞掉

**檢查位置**:每個 improver 的 `_get_or_create_body` 函式

### 3.4 原因 D:Orchestrator 排程問題

**問題**:Enhance Summary 呼叫時,可能找不到現有 Summary slide(因為某些 pptx 的 Summary 在第一頁或最後一頁),導致 enhance 失敗。

**影響位置**:`src/fa_improver/improvers/orchestrator.py` 的 `_execute_action()`

### 3.5 原因 E:slide_width 不匹配導致位置錯位

**問題**:MS 的 pptx slide_width 顯示 33+ inches,代表原本 pptx 設計就不是 10×7.5 標準大小。但 improvers 用 Inches(0.5) 等絕對座標,會把內容放到錯誤位置。

**檢查**:pptx 的 `prs.slide_width` 是否被讀取並傳遞給 improvers

---

## 4. 待修正項目(優先順序)

### 🔴 P0 - 完全空白頁(必修)

**修正位置**:每個 improver 的 `_get_or_create_title` / `_get_or_create_body` 函式

**檢查方式**:
1. 在每個 improver 函式開頭加入 `print(f"[DEBUG] add_X_slide called")`
2. 跑批次測試
3. 看哪些 improver 沒執行或執行失敗
4. 加上 try-except 捕捉 silent error

**實作建議**:
```python
def add_basic_info_slide(prs, evaluation, filename_info, ...):
    layout = find_content_layout(prs)
    if layout is None:
        print(f"⚠️  No content layout found, skipping")
        return None
    slide = prs.slides.add_slide(layout)
    # ... 確保 title 與 body 都有建立
    if not slide.shapes.title:
        # 手動建立 title textbox
        title_box = slide.shapes.add_textbox(...)
        title_box.text_frame.text = template.title
    return slide
```

### 🟡 P1 - 內容位置錯誤(座標問題)

**修正位置**:所有 improvers + visuals/base.py

**實作建議**:
```python
# 在 orchestrator.execute() 中:
def _get_slide_bounds(self, prs):
    return {
        "width": prs.slide_width,
        "height": prs.slide_height,
        "width_inch": prs.slide_width / 914400,  # EMU to inch
        "height_inch": prs.slide_height / 914400,
    }

# 傳給 improvers
self.slide_bounds = self._get_slide_bounds(prs)
add_basic_info_slide(prs, ..., slide_bounds=self.slide_bounds)

# improver 內部:
def add_basic_info_slide(prs, ..., slide_bounds=None):
    width = slide_bounds["width_inch"] if slide_bounds else 10
    left = (width - 9) / 2  # 置中
    # ...
```

### 🟡 P1 - MS 的 33 in 寬度

**原因**:MS 的 pptx 原本就是寬螢幕設計,可能不是 4:3 而是特殊比例。

**修正**:讓 Improver 動態適應 slide_width,不假設固定尺寸。

### 🟢 P2 - 母片覆蓋

**修正**:把內容區域縮小到母片 Logo 區之外(假設 Logo 在右上角,內容 left=0.5、right=2.5 內不要放)。

### 🟢 P2 - 文字直式排版

**原因**:可能是 textbox 寬度太窄(<中文字寬度),中文自動轉直式。

**修正**:確保 textbox 寬度 ≥ 4 inches。

---

## 5. 修正執行步驟(新 session)

### Step 1:診斷

```bash
cd /home/elan/fa-report-refactor/.agents/skills/fa-report-improvement

# 1. 跑批次並加 debug log
DEBUG=1 uv run python scripts/run_batch_evaluation.py 2>&1 | tee debug.log

# 2. 看 pptx 尺寸
uv run python -c "
from pptx import Presentation
prs = Presentation('report/MS_Meishan_ADO_445239_260716.pptx')
print('slide_width:', prs.slide_width, '=', prs.slide_width / 914400, 'inch')
print('slide_height:', prs.slide_height, '=', prs.slide_height / 914400, 'inch')
"

# 3. 找空白頁是哪張
uv run python -c "
from pptx import Presentation
prs = Presentation('report/260811_..._improved.pptx')
for i, slide in enumerate(prs.slides, 1):
    if len(slide.shapes) == 0 or all(s.text_frame.text == '' for s in slide.shapes if s.has_text_frame):
        print(f'Slide {i}: EMPTY')
"
```

### Step 2:修正座標(最常見問題)

修改 `src/fa_improver/improvers/orchestrator.py`,在 `execute()` 中計算 slide bounds 並傳給每個 improver:

```python
def execute(self, prs, output_path):
    # 取得 slide 尺寸
    self.slide_width_inch = prs.slide_width / 914400
    self.slide_height_inch = prs.slide_height / 914400

    # ... 傳給每個 improver
    add_basic_info_slide(prs, ..., slide_width=self.slide_width_inch)
```

然後修改每個 improver 的 `_get_or_create_title/body`:

```python
def _get_or_create_body(slide, slide_width=10, body_height=5):
    for shape in slide.placeholders:
        if shape.placeholder_format.idx != 0:
            # 縮放 placeholder 寬度到 slide 寬度
            return shape
    # Fallback:用 slide 全寬
    return slide.shapes.add_textbox(
        Inches(0.5), Inches(1.5),
        Inches(slide_width - 1.0),
        Inches(body_height),
    )
```

### Step 3:加入 debug 機制

在 orchestrator 加入 logging:

```python
import logging
logger = logging.getLogger(__name__)

def _execute_action(self, prs, action, suggestions):
    logger.info(f"[ORCH] Executing action: {action.value}")
    try:
        # 執行
        ...
        logger.info(f"[ORCH] {action.value} done, slides count: {len(prs.slides)}")
    except Exception as e:
        logger.error(f"[ORCH] {action.value} FAILED: {e}")
        raise
```

### Step 4:逐步測試

```bash
# 一次只測一個報告
uv run python scripts/run_batch_evaluation.py 2>&1 | grep -E "slide|EMPTY|FAIL"

# 看 pptx 渲染
# 開啟 LibreOffice 或上傳到 Google Slides 檢視
```

### Step 5:回歸測試

```bash
# 確保既有 203 個測試仍通過
uv run python -m pytest tests/ -q

# 確保 ruff 無新錯誤
.venv/bin/ruff check src/ tests/ scripts/
```

---

## 6. 暫時不做修改的原因

1. **範圍過大**:座標修正會影響所有 7 個 improvers + 5 個視覺元素生成器
2. **需要實機驗證**:每張截圖都需要人工判讀,無法靠單元測試發現
3. **可能影響母片保護**:如果改座標邏輯,需要重新驗證母片保護 100% 通過
4. **需要設計決策**:動態適應 slide_width 涉及 API 改變,需要設計 review

---

## 7. 給新 session Agent 的建議

### 7.1 優先順序

1. **先修空白頁問題(P0)** — 最嚴重的 bug
2. **再修座標問題(P1)** — 影響所有報告
3. **最後優化母片覆蓋(P2)** — 美觀問題

### 7.2 推薦實作策略

1. **加 debug logging** 在每個 improver,看哪些被跳過
2. **加 slide_bounds 參數** 從 orchestrator 傳給 improvers
3. **修 _get_or_create_body** 使用動態寬度
4. **加 pptx_smoke_test** 在 tests/ 內,自動檢測空白頁與座標問題

### 7.3 自動化測試建議

新增 `tests/integration/test_slide_rendering.py`:

```python
def test_no_empty_slides(sample_pptx, sample_eval_json, tmp_path):
    """改善後不應有空白投影片"""
    output = tmp_path / "out.pptx"
    orchestrator = ImprovementOrchestrator(evaluation, sample_pptx)
    orchestrator.execute(prs, output)

    for i, slide in enumerate(prs.slides, 1):
        assert len(slide.shapes) > 0, f"Slide {i} is empty"
        # 至少要有一個 shape 含有文字
        assert any(
            s.has_text_frame and s.text_frame.text.strip()
            for s in slide.shapes
        ), f"Slide {i} has no text content"
```

### 7.4 文檔更新

修正完成後:
1. 更新本 handoff 的狀態為 ✅ 已修正
2. 新增 `docs/architecture/slide-layout-system.md` 說明座標系統
3. 更新 CHANGELOG

---

## 8. 相關檔案位置

| 檔案 | 用途 |
|------|------|
| `scripts/run_batch_evaluation.py` | 批次執行腳本 |
| `src/fa_improver/improvers/orchestrator.py` | 協調器(座標計算入口) |
| `src/fa_improver/improvers/*.py` | 7 個 improver |
| `src/fa_improver/visuals/base.py` | 5 個視覺生成器 |
| `report/*.improved.pptx` | 產出檔案(有版面問題) |
| `report/batch_evaluation_summary.json` | 批次執行記錄 |
| `/mnt/c/Users/Elan/Desktop/*.png` | 18 張問題截圖 |

---

## 9. 統計數據

- **處理報告數**:3
- **總新增投影片數**:37(11+12+14)
- **空白頁數**:8(22%)
- **座標問題頁數**:15+(40%+)
- **母片保護成功率**:100%(技術層面)

---

✅ 本檔已寫入:`/home/elan/fa-report-refactor/docs/handoff/2026-08-31-batch-eval-rendering-issues-handoff.md`
   包含:9 個區塊,5 大根本原因分析,5 大修正優先順序,7 個新 session 建議,完整截圖索引

---

**⚠️ 重要**:本檔記錄的是**問題清單與分析**,**未做修改**。新 session 接手時請先讀本檔,再決定修正策略。
