# Handoff: v3.1.1 修正未完成 — 4 大殘留版面渲染問題

> 建立日期:2026-09-01
> 對象:未來接手 Agent / 維護者
> 工作目錄:`/home/elan/fa-report-refactor/.agents/skills/fa-report-improvement/`
> **狀態**:🔴 **v3.1.1 標記為「修正完成」是錯誤的** — 詳見 § 1 與 § 2

---

## 1. 真相揭露

### 1.1 為什麼這份 handoff 存在

`docs/handoff/2026-08-31-batch-eval-rendering-issues-handoff.md` 在 2026-08-31 被標記為 🟢 **已修正**(v3.1.1),並 commit 推送至 GitHub(tag `v3.1.1`)。

**但這是錯的標記**。

實際視覺驗證(28 張新截圖,2026-09-01 由 Kenny 提供)顯示 v3.1.1 仍有 **4 大類版面渲染問題**未修正,只是這次問題是「**有內容但內容錯位/重疊/旋轉**」而非「**完全空白**」(v3.1.0 是完全空白)。

### 1.2 v3.1.1 修正的真實覆蓋率

| 問題 | v3.1.0 狀態 | v3.1.1 是否修 | handoff § 10 宣稱 |
|------|-----------|------------|----------------|
| 🔴 P0 完全空白投影片 | 8 張空白 | ✅ 0 張空白 | ✅ 已修 |
| 🟡 P1 座標超出 slide 邊界 | 多張超界 | ✅ 動態計算 | ✅ 已修 |
| 🟡 P1 Inches 重複套用 bug | 多張錯位 | ✅ 傳 float | ✅ 已修 |
| 🔴 **enhance_summary 疊加覆蓋** | 2 張(MS-001、N160JCN-001) | ❌ **未修** | ❌ 未提及 |
| 🟡 **_get_or_create_title 找錯 placeholder** | 多張(MS / N160JCN 標題被覆蓋) | ❌ **未修** | ❌ 未提及 |
| 🟡 **textbox rotation bug** | 4 張(260811-001/003/004/005/006) | ❌ **未修** | ❌ 未提及 |
| 🟡 **底部 placeholder 殘留** | N160JCN 多張底部「按一下即可新增文字」 | ❌ **未修** | ❌ 未提及 |

**v3.1.1 的 smoke test `TestSlideRenderingBounds` 只檢查「shape 不超出 slide 邊界」,從未檢查「title placeholder 殘留」、「textbox 旋轉」、「enhance_summary 疊加」這三類。**

---

## 2. 4 大殘留問題詳情(2026-09-01 視覺驗證)

### 2.1 🔴 Bug 1:`enhance_summary_section` 疊加覆蓋(MS-001、N160JCN-001)

**截圖證據**:
- `/mnt/c/Users/Elan/Desktop/MS_Meishan_ADO_445239_260716_improved-001.png`
- `/mnt/c/Users/Elan/Desktop/N160JCN-EEK project 1pcs NG sample analysis report 260810_improved-001.png`

**症狀**:
- 原 Summary 投影片已有「Summary」標題 +「9mm WOT / Scenario_Name 表格」
- `enhance_summary_section()` 在同一頁注入 3 個新元素:
  - `ProgressBarGenerator`(6 維度進度條)
  - `Executive Summary` textbox
  - `Key Improvements Required` textbox
- 3 個新元素全部擠在原 Summary 同一頁,**嚴重重疊**:
  - 進度條蓋在原表格上
  - Executive Summary 蓋在表格右側
  - Key Improvements 蓋在進度條下方

**根本原因**(位置:`src/fa_improver/improvers/summary.py`):

```python
def enhance_summary_section(prs, ...):
    """策略:保留原 Summary 投影片不動,注入 Executive Summary 與 Key Improvements"""
    summary_idx = _find_summary_index(prs)
    if summary_idx == -1:
        summary_idx = len(prs.slides) - 1
    slide = prs.slides[summary_idx]  # ← 直接拿原 Summary slide
    
    _add_dimension_progress(slide, ...)  # 進度條蓋在原表格上
    _add_executive_summary(slide, ...)  # 蓋在右側
    _add_key_improvements(slide, ...)   # 蓋在下方
```

函式的設計假設是「強化」原 Summary,實際上是「**在已經有內容的投影片上疊加新內容**」,導致互相覆蓋。

**修正方向**(待新 session 執行):

```python
# 改寫成「新增獨立投影片」,而非「疊加原 Summary」
def enhance_summary_section(prs, evaluation, improvements, ...):
    """新增 3 張獨立投影片(不再疊加原 Summary)"""
    # 1. 找原 Summary 的位置,在其後新增 3 張
    summary_idx = _find_summary_index(prs)
    if summary_idx == -1:
        summary_idx = len(prs.slides) - 1
    insert_pos = summary_idx + 1
    
    # 2. 新增 Executive Summary slide
    if evaluation.summary:
        new_slide = _new_executive_summary_slide(prs, evaluation)
        _move_slide_after(new_slide, insert_pos)
    
    # 3. 新增 Key Improvements slide
    new_slide = _new_key_improvements_slide(prs, improvements)
    _move_slide_after(new_slide, insert_pos + 1)
    
    # 4. 新增 6 維度評分 slide
    if evaluation.dimensions:
        new_slide = _new_dimension_progress_slide(prs, evaluation)
        _move_slide_after(new_slide, insert_pos + 2)
```

### 2.2 🟡 Bug 2:`_get_or_create_title` 在 MS / N160JCN 回傳錯的 placeholder

**截圖證據**(7 張):
- MS-002 / 003 / 004 / 005 / 006 / 007 / 008 / 009 / 010 / 011 / 012(標題全部被「按一下即可新增文字」覆蓋)
- N160JCN-002 / 003 / 004 / 005 / 006 / 007 / 008 / 009 / 010(同上)

**症狀**:
- 新 slide 的標題 placeholder 顯示「按一下即可新增文字」(母片預設文字)
- 但實際內容(如「分析方法與流程」)被加在另一個 textbox 上
- 兩個文字並存,造成視覺混淆

**根本原因**(位置:7 個 improvers 的 `_get_or_create_title`):

```python
def _get_or_create_title(slide, slide_bounds=None):
    if slide.shapes.title:           # 1. 找 slide.shapes.title
        return slide.shapes.title
    for shape in slide.shapes:       # 2. 找 name 含 'title' 的
        if "title" in shape.name.lower():
            return shape
    return slide.shapes.add_textbox(...)  # 3. fallback
```

MS / N160JCN 的 pptx 母片設計**同時有多個 placeholder**:
- 主標題 placeholder(idx=0)— `slide.shapes.title` 通常會找到這個
- 但母片 layout 的某些版本中,還有「按一下即可新增文字」副 placeholder(name="PlaceHolder 2" 或類似)
- 我們的 textbox 寫進去但**原本的 placeholder 預設文字仍保留**

**修正方向**(待新 session 執行):

```python
def _get_or_create_title(slide, slide_bounds=None):
    # 策略 1:用 placeholder idx 嚴格匹配 title (idx=0)
    for ph in slide.placeholders:
        if ph.placeholder_format.idx == 0:
            return ph
    # 策略 2:找名稱含 Title 的 placeholder
    for ph in slide.placeholders:
        if "title" in ph.name.lower():
            return ph
    # 策略 3:fallback — 清掉「按一下」placeholder,建立新 textbox
    for shape in slide.shapes:
        if shape.has_text_frame and (
            "按一下" in shape.text_frame.text
            or "Click to add" in shape.text_frame.text
        ):
            shape.text_frame.text = ""
    return slide.shapes.add_textbox(...)
```

### 2.3 🟡 Bug 3:textbox 被旋轉 90°(260811 多張)

**截圖證據**(6 張):
- 260811_improved-001(基本資訊)— 「基本資訊完整性」標題旋轉 90°
- 260811_improved-003(數據證據)— 「數據與證據支持」標題旋轉 90°
- 260811_improved-004(5-Why)— **整頁文字旋轉 90°**,流程圖正常
- 260811_improved-005(原因型態)— **整頁文字旋轉 90°**
- 260811_improved-006(改善對策)— **整頁文字旋轉 90°**,timeline 正常

**症狀**:
- textbox 文字(包括正文、標題、bullet list)**全部變直式垂直排列**
- 但同一頁的形狀(shape)、表格(table)、流程圖(shape)正常顯示

**根本原因**:
260811 的 pptx 母片設計中,**某些 layout 的 body placeholder 被預設為旋轉 90°**(可能是垂直中文排版的設計)。
當我用 `slide.shapes.add_textbox()` 建立新 textbox 時,**新 textbox 不會繼承這個旋轉**,但...
當我用 `_get_or_create_body()` 回傳現有 placeholder(若有的話)時,**那個 placeholder 帶有旋轉屬性**,所以內容被旋轉。

**修正方向**(待新 session 執行):

```python
def _get_or_create_body(slide, slide_bounds=None):
    # 策略 1:找非旋轉的 placeholder
    for ph in slide.placeholders:
        if ph.placeholder_format.idx != 0:
            if ph.rotation == 0:  # ← 關鍵:過濾旋轉的 placeholder
                return ph
    # 策略 2:fallback 建立新 textbox,明確設 rotation = 0
    tb = slide.shapes.add_textbox(...)
    tb.rotation = 0
    return tb
```

同時,所有 improver 中**直接建立的 textbox**也需要確保 `rotation = 0`:

```python
def _safe_textbox(slide, left, top, width, height, text, ...):
    """建立不會旋轉的 textbox"""
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tb.rotation = 0  # ← 防止繼承母片旋轉屬性
    ...
```

### 2.4 🟡 Bug 4:底部 placeholder 殘留(N160JCN 多張)

**截圖證據**(多張):
- N160JCN-002 / 003 / 004 / 005 / 006 / 007 / 008 / 009 / 010 — 底部都有「按一下即可新增文字」placeholder

**症狀**:
- 每張新 slide 的底部出現「按一下即可新增文字」placeholder —這是母片 layout 設計本來就有的 footer placeholder
- 我們**沒主動寫文字也沒隱藏**,所以預設文字顯示出來

**根本原因**:
N160JCN pptx 的母片 layout 含 footer placeholder,`add_slide()` 後沒清掉預設文字。

**修正方向**(待新 session 執行):

```python
def _clean_unused_placeholders(slide):
    """清除未使用的 placeholder(預設文字或空)"""
    for shape in list(slide.placeholders):
        if shape.has_text_frame:
            text = shape.text_frame.text.strip()
            if not text or "按一下" in text or "Click to" in text:
                # 不刪除(可能影響母片),改為透明
                shape.fill.background()
```

或更激進的方案:在 orchestrator `add_slide` 後立即呼叫 `_clean_unused_placeholders(slide)`。

---

## 3. 為什麼 v3.1.1 的 smoke test 沒抓到這些問題

### 3.1 smoke test 的盲點

`tests/integration/test_slide_rendering.py` 的 7 個測試:

| 測試 | 檢查內容 | 對 Bug 1-4 的覆蓋 |
|------|---------|------------------|
| TestSlideRenderingNoEmptySlides (3) | slide 有文字 | ❌ **不覆蓋**(Bug 1-4 的 slide 都有文字) |
| TestSlideRenderingBounds | shape 不超出 slide 邊界 | ❌ **不覆蓋** |
| TestSlideRenderingSlideWidths | orchestrator 讀取真實寬度 | ❌ **不覆蓋** |
| TestSlideRenderingDynamicCoordinates | content 寬度跟著 slide 調整 | ❌ **不覆蓋** |
| TestMasterProtectionStillPasses | 母片保護通過 | ❌ **不覆蓋** |

**所有 smoke test 都用「形狀 + 位置」判斷,沒用「視覺」判斷**。要抓到 Bug 1-4 需要:
- 把 pptx 轉成圖片(用 `libreoffice --headless --convert-to png`)
- 人工目測或用 OCR 檢查

### 3.2 為什麼我之前沒做視覺驗證

`scripts/run_batch_evaluation.py` 只輸出 pptx 檔案,**沒有轉成圖片或截圖驗證**。Kenny 自己手動上傳到 Google Slides 才看到問題。

**這是流程缺陷**:修 bug 之後應該把 pptx 轉圖,確認視覺正確,才算「修正完成」。我跳過這步,直接標記 ✅。

---

## 4. v3.1.1 標記錯誤的責任歸屬

### 4.1 我(pi agent)做錯的事

1. ❌ **沒做視覺驗證** — 只跑單元測試,沒把 pptx 轉圖確認視覺
2. ❌ **過早聲稱「修正完成」** — 寫進 handoff § 10 + CHANGELOG v3.1.1 + 推送 v3.1.1 tag
3. ❌ **smoke test 設計不完整** — 只測「有沒有文字」、「有沒有超界」,沒測「標題是否正確」、「是否被旋轉」、「是否覆蓋」
4. ❌ **沒在 CHANGELOG 列「Known Issues」** — 只寫修好的,沒寫沒修的

### 4.2 後續應該做的事(待新 session 執行)

1. **刪除 v3.1.1 tag 或改成 pre-release**:
   ```bash
   git tag -d v3.1.1
   git push origin :refs/tags/v3.1.1
   git tag -a v3.1.1-rc1 -m "v3.1.1 release candidate 1(尚未修正 enhance_summary 疊加覆蓋與 textbox 旋轉問題)"
   ```

2. **修正 handoff `2026-08-31-batch-eval-rendering-issues-handoff.md`**:
   - 狀態從 🟢 已修正 改回 🟡 部分完成(v3.1.1-rc1)
   - § 10 改為「v3.1.1-rc1 修正紀錄(部分)」+ 新增 § 11 「未完成項目」

3. **新增視覺驗證腳本** `scripts/visual_smoke_test.py`:
   ```python
   """把 pptx 轉圖,目測或自動檢查版面渲染"""
   import subprocess
   from pathlib import Path
   
   def convert_pptx_to_images(pptx_path: Path) -> list[Path]:
       """用 libreoffice 把 pptx 轉成一組 png"""
       subprocess.run([
           "libreoffice", "--headless", "--convert-to", "png",
           "--outdir", str(pptx_path.parent / "_visual"),
           str(pptx_path)
       ])
       ...
   ```

4. **加強 smoke test**:
   ```python
   # tests/integration/test_slide_visual_quality.py
   def test_title_placeholders_not_residual(sample_pptx):
       """沒有殘留「按一下即可新增文字」placeholder"""
       ...
   
   def test_no_textbox_rotation(sample_pptx):
       """沒有 textbox 被旋轉"""
       ...
   
   def test_no_shape_overlap_on_summary(sample_pptx):
       """Summary 頁沒有 3 區塊互相覆蓋"""
       ...
   ```

5. **修正 4 個 Bug**(見 § 2 修正方向):
   - Bug 1: `enhance_summary_section` 改成新增獨立投影片
   - Bug 2: `_get_or_create_title` 用 `placeholder_format.idx == 0` 嚴格匹配
   - Bug 3: textbox 建立後 `rotation = 0`
   - Bug 4: `_clean_unused_placeholders` 處理底部 placeholder

---

## 5. 不要重複做的事情

- 🚫 **不要再聲稱「修正完成」**,除非有視覺驗證截圖佐證
- 🚫 **不要再推送 v3.1.x tag**,直到 4 個 Bug 全部修完
- 🚫 **不要再用同樣的 smoke test** — 必須加視覺驗證腳本
- 🚫 **不要再寫 handoff § 10「完全修正」**,要用「部分修正 + 明確列出未完成項」

---

## 6. 重要規則和限制

- ⚠️ 當前日期:**2026-09-01**(任何新文件都必須用這個日期)
- ⚠️ 雙倉庫架構:本檔在根倉庫,後續修正 commit 在技能包倉庫
- ⚠️ v3.1.1 tag 已推送,需先決定是否要 revert
- ⚠️ handoff `2026-08-31-batch-eval-rendering-issues-handoff.md` 仍標記 🟢 已修正,需修正

---

## 7. 關鍵檔案和位置

| 檔案 | 用途 | 需要做的動作 |
|------|------|------------|
| `docs/handoff/2026-08-31-batch-eval-rendering-issues-handoff.md` | 原始問題 handoff | 修正狀態標記 |
| `docs/handoff/2026-09-01-v311-incomplete-rendering-handoff.md`(本檔) | 新揭露 handoff | 已建立 |
| `src/fa_improver/improvers/summary.py` | `enhance_summary_section` 實作 | Bug 1: 改成新增獨立投影片 |
| 7 個 improvers 的 `_get_or_create_title` | 找 title placeholder | Bug 2: 用 idx 嚴格匹配 |
| 7 個 improvers 的 textbox 建立處 | `add_textbox` 呼叫 | Bug 3: 設 `rotation = 0` |
| `orchestrator.add_slide` 後的 cleanup | 底部 placeholder 殘留 | Bug 4: 加 `_clean_unused_placeholders` |
| `tests/integration/test_slide_rendering.py` | 既有 smoke test | 強化:加視覺驗證 |
| `scripts/visual_smoke_test.py`(待新增) | 視覺驗證腳本 | 新增 |
| `.agents/skills/fa-report-improvement/CHANGELOG.md` | v3.1.1 條目 | 加 Known Issues 段落 |

---

## 8. 建議下一步(請 Kenny 指示)

請明確選擇:

- **🅰️**:開始執行 § 4.2 全部動作(估計 2-3 小時)
- **🅱️**:只先做 § 4.2 第 1-2 項(revert tag + 修 handoff 狀態),留下 Bug 修正給下次 session
- **🅲️**:什麼都不做,只保留本 handoff 揭露真相,等 Kenny 確認後再決定

**作者強烈建議**:至少做 🅱️,因為 v3.1.1 tag 已推送但內含未修正問題,可能誤導其他使用者。

---

✅ Handoff 文檔已寫入:`/home/elan/fa-report-refactor/docs/handoff/2026-09-01-v311-incomplete-rendering-handoff.md`
   包含:8 個區塊,4 大殘留問題詳情,5 項 v3.1.1 的真實覆蓋率,7 個未完成建議動作,3 個選項等指示

---

**⚠️ 重要**:本檔的目的是**揭露 v3.1.1 標記錯誤**,**不做任何程式碼修改**。新 session 接手時請先讀本檔 + 上一份 handoff,再決定修正策略。