# Handoff: v3.1.3 用戶回饋版面優化(2026-09-02)

> 建立日期:2026-09-02
> 對象:未來接手 Agent / 維護者
> 工作目錄:`/home/elan/fa-report-refactor/.agents/skills/fa-report-improvement/`
> **狀態**:🟢 **v3.1.3 已修正完成 Kenny 2026-09-02 反饋的 3 個版面問題**

---

## 1. 任務目標

延續 v3.1.2 修正後,Kenny 視覺驗證 3 份報告改善輸出截圖,發現 3 個剩餘版面問題:

1. 🟡 簡報標題偏左(3 份報告皆有)— 標題第一個字被母片左上裝飾擋住
2. 🟡 Page 10/13/14(MS)、Page 12/15/16(N160JCN)標題與內容重疊
3. 🟡 最後一頁「6 維度評分分析」slide 應移除(3 份報告)

詳見用戶原始反饋(2026-09-02 上午提供 36 張截圖)。

---

## 2. 已完成內容

### 2.1 修正「簡報標題偏左」

**位置**:
- `src/fa_improver/improvers/_safe_shape.py`(`TITLE_SAFE_LEFT_INCH = 1.2` 等常數)
- `src/fa_improver/improvers/basic_info.py`(`_get_or_create_title` 統一改用 helper)

**根本原因**:
- 母片左上角裝飾(深藍直條 `矩形 12/34` + 淺藍色塊 `矩形 13/35`)位於 x=0.54-0.97 in
- `get_or_create_title()` 的 fallback `safe_textbox` 從 `left=0.5 in` 開始 → title 第一個字被裝飾擋住
- `basic_info.py` 的 `_get_or_create_title` 自己 hard-code `margin=0.5`,繞過了 helper

**修正策略**:
- 新增常數 `TITLE_SAFE_LEFT_INCH = 1.2`(避開 x=0.54-0.97 的裝飾區)
- `get_or_create_title()` fallback safe_textbox 的 `left` 從 0.5 改為 1.2,height 從 1.0 改為 0.85(更緊湊)
- 動態檢查:若 `left >= sw - 2.0` (slide 太窄),自動 fallback 到 `max(0.5, sw - 9.5)`
- `basic_info.py` 的 `_get_or_create_title` / `_get_or_create_body` 統一改呼叫 `_safe_shape.get_or_create_title/body`

### 2.2 修正「標題與內容重疊」

**位置**:`src/fa_improver/improvers/_safe_shape.py`

**根本原因**:
- MS / N160JCN 的 layout `2L - Topic`、`Topic-Numbers` 的 body placeholder 高度只有 0.51 in
- 當我們用 `_get_or_create_body` 回傳該 placeholder 寫入「heading + 多個 bullets」時,內容溢出到 title 區
- N160JCN 的 layout `Topic-Numbers` 只有 1 個 placeholder (`文字版面配置區 7`),這個 placeholder 既當 title 又當 body — 我們用 `_get_or_create_body` 寫進這個 placeholder,但同時 `_get_or_create_title` 又建立一個 TextBox 蓋在 placeholder 上方,造成「title 文字」與「layout placeholder 的 heading 文字」互相覆蓋

**修正策略**:
- 新增常數 `BODY_MIN_HEIGHT_INCH = 1.0`
- `get_body_placeholder()` 當 layout placeholder `height < 1.0 in` 時,return None → fallback 用 `safe_textbox(top=1.5, height=sh-2.0)` 重新建立 body
- `get_title_placeholder()` 當 layout 沒有 idx=0 placeholder 且 `len(placeholders) <= 1` 時,return None → fallback 用 `safe_textbox(top=0.3, height=0.85)` 避免與該 placeholder 重疊

### 2.3 移除「6 維度評分分析」slide(預設關閉)

**位置**:
- `src/fa_improver/improvers/summary.py`(`enhance_summary_section` 加 `include_dimension_chart` 參數)
- `src/fa_improver/improvers/orchestrator.py`(加 `include_dimension_chart` 屬性)
- `src/fa_improver/cli.py`(加 `--include-dimension-chart` flag)

**修正策略**:
- `enhance_summary_section()` 新增 `include_dimension_chart: bool = False` 參數(keyword-only,向後相容)
- 預設 `False`:不產生「6 維度評分分析」slide
- 透過 `--include-dimension-chart` CLI flag 可 opt-in 開啟
- `_new_dimension_progress_slide()` 函式保留不刪除(向後相容,允許其他腳本直接呼叫)

### 2.4 新增視覺回歸測試

**位置**:`tests/integration/test_visual_quality.py`

新增 3 個測試類別 / 4 個測試方法:

| 測試類別 | 測試方法 | 驗證內容 |
|---------|---------|---------|
| `TestNoTitleDecorationOverlap` | `test_title_textbox_safe_left` | 新增 slide 的 title textbox 的 left >= 1.2 in |
| `TestBodyHasEnoughHeight` | `test_no_overlap_between_title_and_body` | body 不與 title 重疊 + body.height >= 1.0 in |
| `TestDimensionChartOptIn` | `test_dimension_chart_skipped_by_default` | 預設不出現「6 維度評分分析」slide |
| `TestDimensionChartOptIn` | `test_dimension_chart_enabled_with_flag` | `--include-dimension-chart` 正常運作 |

---

## 3. 關鍵檔案和位置

| 檔案 | 動作 |
|------|------|
| `src/fa_improver/improvers/_safe_shape.py` | 🔧 加 `TITLE_SAFE_LEFT_INCH` 等常數 + 改進 `get_title_placeholder` / `get_body_placeholder` / `get_or_create_title` / `get_or_create_body` |
| `src/fa_improver/improvers/summary.py` | 🔧 `enhance_summary_section` 加 `include_dimension_chart` keyword-only 參數 |
| `src/fa_improver/improvers/orchestrator.py` | 🔧 `ImprovementOrchestrator.__init__` 加 `include_dimension_chart` 屬性,傳給 `enhance_summary_section` |
| `src/fa_improver/improvers/basic_info.py` | 🔧 `_get_or_create_title` / `_get_or_create_body` 統一改用 `_safe_shape` helper(原本 hard-code) |
| `src/fa_improver/cli.py` | 🔧 加 `--include-dimension-chart` flag |
| `tests/integration/test_visual_quality.py` | 🆕 加 4 個 v3.1.3 視覺回歸測試 |
| `CHANGELOG.md` | 🔧 加 v3.1.3 條目 |
| `docs/handoff/2026-09-01-v313-user-feedback-fixes-handoff.md` | 🆕 本檔(交接文檔) |

---

## 4. 重要規則和限制

- ⚠️ 當前日期:2026-09-02(任何新文件都必須用這個日期)
- ⚠️ 雙倉庫架構:本檔在根倉庫,程式碼改動 commit 在技能包倉庫
- ⚠️ AGENTS.md § 9:母片保護 100% 通過 — 跑 `tests/unit/test_master_protection.py` 確認
- ⚠️ AGENTS.md § 7.2:Python 3.10+ 型別語法(`X | None` 而非 `Optional[X]`)

---

## 5. 已確認結論

- ✅ 3 個用戶回饋的版面問題全部修正
- ✅ 219 個測試通過(203 unit + 7 slide_rendering + 9 visual_quality)+ 3 skipped
- ✅ 90% 覆蓋率(從 v3.1.2 的 89% 提升)
- ✅ Ruff all checks passed
- ✅ 母片保護 100% 通過
- ✅ 3 份批次改善報告:title 完整顯示、不再重疊、最後一頁不再是「6 維度評分分析」
- ✅ 53 張視覺驗證圖片(15+18+20)已人工檢查過

---

## 6. 不要重複做的事情

- 🚫 **不要改母片 XML**(AGENTS.md § 9)— 此次純改 generator,不動 pptx 母片
- 🚫 **不要把 title 改回 left=0.5** — 母片裝飾區在 x=0.54-0.97,會擋住第一個字
- 🚫 **不要讓「6 維度評分分析」slide 預設開啟** — Kenny 明確要求移除
- 🚫 **不要直接 hard-code `margin=0.5` 在 improver** — 統一用 `_safe_shape` 的常數
- 🚫 **不要在「Topic」、「Topic-Numbers」單 placeholder layout 寫 body 進 placeholder** — 高度只有 0.51 in,會溢出

---

## 7. 給未來 session Agent 的建議

### 7.1 若發現新 bug

1. 用 `uv run python scripts/visual_smoke_test.py --pptx <pptx>` 產出視覺圖片
2. 人工檢查圖片,找到問題
3. 在 `tests/integration/test_visual_quality.py` 加視覺回歸測試
4. 修 bug,確認測試通過
5. 重跑批次確認問題消失

### 7.2 若要優化版面

- 所有 title 位置都用 `_safe_shape.TITLE_SAFE_LEFT_INCH` 常數(目前 1.2)
- 所有 body 高度門檻都用 `_safe_shape.BODY_MIN_HEIGHT_INCH` 常數(目前 1.0)
- 需要新增 layout 種類時,在 `_safe_shape.py` 加 layout 判斷邏輯,而非散落在各 improver

### 7.3 未來可能的改進(非緊急)

- **LLM 整合**:見 `docs/handoff/2026-08-31-llm-vs-bugfix-decision-handoff.md`
- **母片裝飾設計**:若 Kenny 想完全消除左上裝飾對新內容的影響,需修 pptx 母片(超出本專案範圍)
- **OCR 自動驗證**:`scripts/visual_smoke_test.py` 可加上 OCR 自動檢查 title 文字(本次未做)

---

## 8. 統計數據

| 指標 | v3.1.2 | v3.1.3 |
|------|--------|--------|
| Unit test | 203 passed | 203 passed ✅ |
| slide_rendering smoke test | 7 passed | 7 passed ✅ |
| visual_quality smoke test | 5 passed | **9 passed** ✅(+4 個 v3.1.3 測試) |
| **總計** | 215 + 3 skipped | **219 + 3 skipped** |
| 覆蓋率 | 89% | **90%** ✅ |
| Ruff | All checks passed | All checks passed ✅ |

### 真實批次執行

| 報告 | 原始 | v3.1.2 產出 | v3.1.3 產出 |
|------|------|-------------|-------------|
| 260811 (10×7.5) | 5 張 | 16 張 | **15 張** ✅(少 1 張 dim chart) |
| MS (13.33×7.5) | 5 張 | 19 張 | **18 張** ✅(少 1 張 dim chart) |
| N160JCN (13.33×7.5) | 9 張 | 21 張 | **20 張** ✅(少 1 張 dim chart) |

**視覺驗證圖片數**:53 張(260811: 15 + MS: 18 + N160JCN: 20)

---

## 9. Git 歷史

### 技能包倉庫(`fa-report-refactor/.agents/skills/fa-report-improvement/`)
- 預計 commit:`fix: 修正 Kenny 2026-09-02 回饋的 3 個版面問題 + 4 個視覺回歸測試`

### Tags
- 待建立:`v3.1.3`(本次)

---

## 10. CLI 用法對照表

| 情境 | v3.1.2 指令 | v3.1.3 指令 |
|------|-------------|-------------|
| 預設(無 6 維度) | (無對應) | `uv run python -m fa_improver input.pptx --eval eval.json --output out.pptx` |
| 包含 6 維度分析 | (自動產生) | `uv run python -m fa_improver input.pptx --eval eval.json --include-dimension-chart --output out.pptx` |

---

✅ Handoff 文檔已寫入:`/home/elan/fa-report-refactor/docs/handoff/2026-09-01-v313-user-feedback-fixes-handoff.md`
   包含:10 個區塊,3 大 Bug 修正記錄,關鍵檔案與位置,給未來 session 的建議,完整統計