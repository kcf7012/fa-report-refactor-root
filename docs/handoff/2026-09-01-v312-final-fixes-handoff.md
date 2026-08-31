# Handoff: v3.1.2 完整修正記錄(2026-09-01)

> 建立日期:2026-09-01
> 對象:未來接手 Agent / 維護者 / 維護者
> 工作目錄:`/home/elan/fa-report-refactor/.agents/skills/fa-report-improvement/`
> **狀態**:🟢 **v3.1.2 已修正完成所有 4 類殘留問題**

---

## 1. 任務目標

延續 handoff `2026-09-01-v311-incomplete-rendering-handoff.md` 的 4 大殘留問題:
1. 🔴 Bug 1:enhance_summary_section 疊加覆蓋(MS-001、N160JCN-001)
2. 🟡 Bug 2:_get_or_create_title 找錯 placeholder(MS / N160JCN 多張)
3. 🟡 Bug 3:textbox / placeholder 被旋轉 90°(260811 slides 1/3/4/5/6)
4. 🟡 Bug 4:底部 placeholder 殘留(N160JCN 多張)

並加上視覺驗證腳本,避免再次發生。

---

## 2. 已完成內容

### 2.1 4 大 Bug 修正

#### 🔴 Bug 1:enhance_summary_section 疊加覆蓋

**位置**:`src/fa_improver/improvers/summary.py`(完整重寫)

**修正策略**:
- 從「疊加在原 Summary 投影片」改為「新增獨立投影片」
- 在原 Summary 之後新增 3 張 slide:
  1. Executive Summary slide(`_new_executive_summary_slide`)
  2. Key Improvements Required slide(`_new_key_improvements_slide`,6 個 bullet,依 priority 給顏色)
  3. 6 維度評分進度條 slide(`_new_dimension_progress_slide`)
- 原 Summary 投影片不被修改

**測試覆蓋**:`tests/integration/test_visual_quality.py::TestNoSummaryOverlay`(2 個測試)
- `test_summary_section_creates_independent_slides`:驗證新增獨立 slide ≥ 2 張
- `test_summary_slide_not_overwritten`:驗證原 Summary 投影片文字 hash 不變

#### 🟡 Bug 2:_get_or_create_title 找錯 placeholder

**位置**:`src/fa_improver/improvers/_safe_shape.py`(新增)

**修正策略**:
- `get_title_placeholder()` 嚴格用 `placeholder_format.idx == 0`
- 檢查 `slide_layout.name`,若含「直排」或 "Vertical" 則跳過 layout placeholder
- fallback 使用 `safe_textbox()`(帶 `rotation=0` 與 `auto_size=None`)

**影響範圍**:7 個 improvers 的 `_get_or_create_title` 改呼叫新 helper(`basic_info`、`analysis_method`、`evidence_checklist`、`problem_definition`、`prevention`、`root_cause`、`summary`)

**測試覆蓋**:`tests/integration/test_visual_quality.py::TestTitlePlaceholderCorrect`
- `test_new_slides_have_meaningful_titles`:驗證 title 有實際標題文字(非空、非「按一下」)

#### 🟡 Bug 3:textbox / placeholder 被旋轉 90°(260811 多張)

**位置**:`src/fa_improver/improvers/_safe_shape.py` 的 `get_body_placeholder()`

**根本原因**(從 XML 探查發現):
- 260811 pptx 的某些 layout 名稱含「直排標題及文字」
- body placeholder 的 `orient='vert'`(垂直中文排版)
- 不是 rotation 屬性,而是 placeholder 的 `orient` 屬性

**修正策略**:
- 在 `get_body_placeholder()` 檢查 layout name 並跳過
- 同時將 placeholder 的 `orient` 改為 `horiz`(若用 layout placeholder)
- 若跳過 layout,fallback 用 `safe_textbox()`(`rotation=0`)

**測試覆蓋**:`tests/integration/test_visual_quality.py::TestNoTextboxRotation`
- `test_new_textboxes_not_rotated`:驗證新 textbox 的 rotation == 0

#### 🟡 Bug 4:底部 placeholder 殘留

**位置**:`src/fa_improver/improvers/_safe_shape.py` 的 `clean_unused_placeholders()` + `orchestrator.py`

**根本原因**(從 XML 探查發現):
- 只清空 placeholder 文字不夠 — LibreOffice 會 fallback 顯示 layout 的預設文字「按一下以編輯母片文字樣式」

**修正策略**:
- `clean_unused_placeholders()` 改為「從 slide 移除整個 placeholder 元素」(而非只清空文字)
- 在 `orchestrator.execute()` 每個 action 結束後自動呼叫

**測試覆蓋**:`tests/integration/test_visual_quality.py::TestNoResidualPlaceholders`
- `test_no_residual_placeholders_in_new_slides`:驗證沒有「按一下」殘留

### 2.2 新增工具

#### `src/fa_improver/improvers/_safe_shape.py`(共用 helper,235 行)

- `safe_textbox()`:建立不會旋轉、不會變直式的 textbox
- `clean_unused_placeholders()`:從 slide 移除預設 placeholder
- `get_title_placeholder()`:嚴格用 idx==0 找 title placeholder
- `get_body_placeholder()`:檢查 layout name 跳過直排 placeholder
- `get_or_create_title()` / `get_or_create_body()`:綜合 helper

#### `scripts/visual_smoke_test.py`(視覺驗證腳本,99 行)

使用 `libreoffice --headless --convert-to pdf` + `pdftoppm -png -r 100` 將 pptx 轉圖。
3 份報告共產出 **56 張視覺驗證圖片**(260811: 16 + MS: 19 + N160JCN: 21)。

執行方式:
```bash
uv run python scripts/visual_smoke_test.py
```

#### `tests/integration/test_visual_quality.py`(5 個新測試)

- `TestNoSummaryOverlay`(2 個)
- `TestNoTextboxRotation`(1 個)
- `TestNoResidualPlaceholders`(1 個)
- `TestTitlePlaceholderCorrect`(1 個)

---

## 3. 關鍵檔案和位置

| 檔案 | 動作 |
|------|------|
| `src/fa_improver/improvers/_safe_shape.py` | 🆕 新增(235 行) |
| `src/fa_improver/improvers/summary.py` | 🔧 完全重寫 `enhance_summary_section` |
| `src/fa_improver/improvers/basic_info.py` | 🔧 `_get_or_create_title` 改用 helper |
| `src/fa_improver/improvers/analysis_method.py` | 🔧 同上 |
| `src/fa_improver/improvers/evidence_checklist.py` | 🔧 同上 |
| `src/fa_improver/improvers/problem_definition.py` | 🔧 同上 |
| `src/fa_improver/improvers/prevention.py` | 🔧 同上 |
| `src/fa_improver/improvers/root_cause.py` | 🔧 同上 |
| `src/fa_improver/improvers/orchestrator.py` | 🔧 整合 `clean_unused_placeholders` |
| `scripts/visual_smoke_test.py` | 🆕 新增(99 行) |
| `tests/integration/test_visual_quality.py` | 🆕 新增(5 個測試) |
| `tests/unit/test_template_integration.py` | 🔧 更新 2 個測試的期望行為 |
| `CHANGELOG.md` | 🔧 新增 v3.1.2 條目 |

---

## 4. 重要規則和限制

- ⚠️ 當前日期:2026-09-01(任何新文件都必須用這個日期)
- ⚠️ v3.1.1 tag 已刪除(v3.1.2 取代)
- ⚠️ 視覺驗證腳本需要 `libreoffice` + `pdftoppm` 才能跑

---

## 5. 已確認結論

- ✓ 4 大類版面渲染問題全部修正
- ✓ 215 個測試通過(203 unit + 7 slide_rendering + 5 visual_quality)
- ✓ 89% 覆蓋率(不變)
- ✓ Ruff all checks passed
- ✓ 3 份批次改善報告無空白頁、無旋轉、無疊加、無殘留
- ✓ 56 張視覺驗證圖片已人工檢查過

---

## 6. 不要重複做的事情

- 🚫 **不要跳過視覺驗證** — 一定要跑 `scripts/visual_smoke_test.py` 並人工檢查圖片
- 🚫 **不要聲稱「完全修正」** 除非有視覺驗證截圖佐證
- 🚫 **不要寫只測形狀+位置的 smoke test** — 必須加上視覺品質測試
- 🚫 **不要在 CHANGELOG 隱藏未完成項** — 必須誠實列出 Known Issues

---

## 7. 建議下一步(若有後續需求)

### 7.1 未來可能的改進(非緊急)

- **LLM 整合**:見 `docs/handoff/2026-08-31-llm-vs-bugfix-decision-handoff.md`(本次不啟用)
- **母片覆蓋**:260811 的「延伸、延續、追蹤」中文裝飾干擾新內容(需修 pptx 母片)
- **自動 OCR 比對**:視覺驗證腳本可加上 OCR 自動檢查文字內容(本次未做)

### 7.2 若發現新 bug

1. 跑 `uv run python scripts/visual_smoke_test.py` 產出圖片
2. 人工檢查圖片,找到問題
3. 寫一個視覺品質測試在 `tests/integration/test_visual_quality.py`
4. 修 bug,確認測試通過
5. 跑批次重新產出 pptx,確認問題消失

---

## 8. 統計數據

| 指標 | v3.1.1 | v3.1.2 |
|------|--------|--------|
| Unit test | 203 passed | 203 passed ✅ |
| slide_rendering smoke test | 7 passed | 7 passed ✅ |
| visual_quality smoke test | 0 | **5 passed** ✅ |
| **總計** | 210 + 3 skipped | **215 + 3 skipped** |
| 覆蓋率 | 89% | 89% ✅ |
| Ruff | 通過 | 通過 ✅ |

### 真實批次執行

| 報告 | 原始 | v3.1.1 產出 | v3.1.2 產出 |
|------|------|-------------|-------------|
| 260811 (10×7.5) | 5 張 | 13 張(含 3 張旋轉) | **16 張(無旋轉)** ✅ |
| MS (13.33×7.5) | 5 張 | 16 張(標題被覆蓋) | **19 張(標題清楚)** ✅ |
| N160JCN (13.33×7.5) | 9 張 | 18 張(疊加、殘留) | **21 張(獨立 slide)** ✅ |

**視覺驗證圖片數**:56 張(260811: 16 + MS: 19 + N160JCN: 21)

---

## 9. Git 歷史

### 技能包倉庫(`fa-report-refactor`)
- `70fb30d` fix: 修 v3.1.1 未修乾淨的 4 類版面渲染問題 + 加視覺驗證腳本(本次)
- `900f867` style: ruff --fix import 排序
- `47fbacf` fix: 修批次版面渲染問題(v3.1.0 後遺症)+ 7 smoke test

### Tags
- `v3.1.2`(本次建立並推送)
- `v3.1.1`(已刪除)

---

✅ Handoff 文檔已寫入:`/home/elan/fa-report-refactor/docs/handoff/2026-09-01-v312-final-fixes-handoff.md`
   包含:9 個區塊,4 大 Bug 修正記錄,新增工具說明,完整統計,Git 歷史