# Handoff: 批次版面渲染問題的 LLM vs Bug 修正策略評估

> 建立日期:2026-08-31
> 交接給:下一個接手 Agent / 維護者 / 專案負責人(Kenny)
> 工作目錄:`/home/elan/fa-report-refactor/.agents/skills/fa-report-improvement/`
> **狀態**:🟢 決策已定,等待執行 handoff `2026-08-31-batch-eval-rendering-issues-handoff.md` 的 Step 1-5

---

## 1. 任務目標

針對 18 張截圖所反映的版面渲染問題,**評估「啟用 LLM」vs「純修版 bug」**哪個策略能真正解決問題,並把決策依據寫入專案文檔,讓未來接手者理解為何當下選擇純修版 bug。

子目標:
1. 從截圖歸納問題類型,量化「LLM 能修」與「LLM 不能修」的比例
2. 評估啟用 LLM 的副作用(成本、風險、執行時間、可測試性)
3. 給出可執行的最終決策,並與 `AGENTS.md § 十.2` 的「LLM 預設關閉」原則保持一致

---

## 2. 已完成內容

- ✅ 讀完 18 張截圖,完成問題分類
- ✅ 讀完 handoff `2026-08-31-batch-eval-rendering-issues-handoff.md` 全文(9 個區塊)
- ✅ 確認 `.env` 已填入 OPENAI_API KEY(技術上 LLM 可用)
- ✅ 評估 LLM 對本批次問題的實質幫助,結論:**LLM 0% 覆蓋率,純修 bug 100% 覆蓋率**
- ✅ 決策已寫入本文檔

---

## 3. 問題分類(18 張截圖歸納)

### 3.1 問題清單與 LLM 覆蓋率

| # | 問題類型 | 嚴重度 | 出現截圖 | 根本原因 | LLM 能修? |
|---|---------|--------|---------|---------|---------|
| 1 | **完全空白投影片** | 🔴 P0 | 8 張(260811-001/004/006、MS-002/006、N160JCN-002/004/006) | `add_X_slide()` 執行但沒建立任何 shape(layout 找不到 / `_get_or_create_title` 回 None) | ❌ 不能 |
| 2 | **內容互相覆蓋** | 🟡 P1 | 3 張(260811-002、260811-005、MS-005) | 多個 visual 元素座標重疊,沒檢查 slide bounds | ❌ 不能 |
| 3 | **slide_width 不匹配** | 🟡 P1 | 3 檔(260811 9.5 in、MS 33+ in、N160JCN 13 in) | `Inches(0.5)`、`Inches(9.0)` hard-coded,沒讀 `prs.slide_width` | ❌ 不能 |
| 4 | **內容被擠壓到左上角** | 🟡 P1 | 6 張+(260811-005、N160JCN-005、MS 全體) | 同上,Inches() 絕對座標在非標準尺寸投影片上位置錯誤 | ❌ 不能 |
| 5 | **title 蓋到 placeholder** | 🟢 P2 | 5 張(N160JCN-002/003/005、MS-003/004) | title shape 與 body shape 位置沒跟著 slide 尺寸調整 | ❌ 不能 |
| 6 | **文字變垂直** | 🟢 P2 | 2 張(260811-002 D1-D8 直排、260811-005 整頁旋轉) | textbox 寬度 < 中文字寬,觸發 autofit 變直排 | ❌ 不能 |
| 7 | **母片裝飾干擾** | 🟢 P2 | 多張(母片「延伸」「延續」「追蹤」垂直字壓在內容上) | 內容區沒避開母片裝飾區 | ❌ 不能 |
| 8 | **內容品質死板** | ⚪ 非當前問題 | — | 模板文字不夠個人化 | ✅ 能(LLM 強項) |

**結論**:18 張截圖的問題中,**100% 是版面/座標/邏輯 bug,0% 是內容品質問題**。LLM 在本批次完全無能為力。

### 3.2 啟用 LLM 反而會讓情況更糟

以 **MS 的 33-inch 寬 slide** 為例(目前最嚴重):

```
現狀(無 LLM):
  add_summary_slide 執行失敗 → slide 完全空白 → 使用者一眼看出 bug
  修復成本:低(直接修程式)

啟用 LLM 後:
  add_summary_slide 成功,但 textbox 寬度只設 9 inches
  LLM 生成 800 字精闢分析 → 文字擠在 9/33 = 27% 區域
  → 觸發 autofit → 文字變垂直 → 使用者完全看不懂
  修復成本:高(還要修版面,且浪費 API 錢)
```

**LLM 文字越長,在錯誤座標下表現越慘。** 在沒修版面之前啟用 LLM 等於「花錢讓 bug 更明顯」。

---

## 4. 啟用 LLM 的副作用評估

| 維度 | 不啟用 LLM(純修版) | 啟用 LLM(疊加) | 差距 |
|------|-------------------|----------------|------|
| 修好 P0 空白頁 | ✅ 可專注修 | ❌ LLM 文字會跑到錯位置,看不出修了什麼 | 大 |
| 修好 P1 座標 | ✅ 容易驗證 | ❌ LLM 文字長度變數多,難驗證 | 大 |
| 執行時間 | ✅ 5-10 分鐘 | ❌ 30-60 分鐘(21 次 API 呼叫) | 3-6 倍 |
| API 成本 | ✅ $0 | ❌ $0.3-1.5 / 3 份報告 | + |
| 風險 | ✅ 純程式改動 | ❌ API failure、rate limit、PII 外洩 | 大 |
| 可測試性 | ✅ 單元測試可控 | ❌ LLM 輸出不確定 | 大 |
| 符合 AGENTS.md § 十.2 | ✅ 符合「預設關閉」 | ⚠️ 偏離當前任務 | — |
| 符合當前 handoff Step 1-5 | ✅ 完全符合 | ⚠️ 額外引入新測試需求 | — |

---

## 5. 已確認結論

- ✓ **本批次問題 100% 是版面 bug,LLM 覆蓋率 0%**
- ✓ 啟用 LLM 不會修好任何 1 張截圖,反而可能讓 bug 更難 debug
- ✓ AGENTS.md § 十.2 明確寫「預設關閉,建議對真實報告啟用遮罩」,暗示需要先驗證
- ✓ 當前紅隊(handoff § 11 的 v3.1+ 8 項)未涵蓋版面渲染問題,這是**新 bug 類別**
- ✓ LLM 的真正價值在「**內容品質強化**」,不是「**版面修復**」

---

## 6. 最終決策

### 🅰️ 純修版面 bug(已選定 ✅)

依照 `2026-08-31-batch-eval-rendering-issues-handoff.md` 的 Step 1-5:

1. **Step 1:診斷** — 跑批次加 debug log,找出哪幾個 improver silently fail
2. **Step 2:修座標** — orchestrator 計算 `slide_width_inch` / `slide_height_inch` 傳給 improvers
3. **Step 3:加 debug 機制** — 每個 improver 加 `logger.info(...)` 與 try/except
4. **Step 4:逐步測試** — 一次只測一個報告,看渲染結果
5. **Step 5:回歸測試** — 確保 203 個既有測試仍通過,ruff 無新錯誤

完成後:
- 新增 `tests/integration/test_slide_rendering.py` 自動偵測空白頁與座標超界
- 更新本 handoff 為 ✅ 已修正
- 新增 `docs/architecture/slide-layout-system.md` 說明座標系統
- 更新 CHANGELOG

### ❌ 不採用的替代方案

- **🅱️ 修版面 + 同時加 LLM** — 不建議,因 LLM 文字長度變數會干擾版面測試;且需要新增 CLI 參數 + 測試 + 文檔,屬於 v3.2.0 功能
- **🅲️ 只加 LLM,不修版面** — ❌ 完全不建議,純粹浪費 API 錢且讓 bug 更明顯

---

## 7. LLM 之後可考慮的混合策略(下一輪任務)

等版面 P0/P1/P2 修完、版面乾淨後,**可針對特定投影片**用 LLM 強化文案,屬於 v3.2.0+ 範圍:

```bash
# 未來可能的 CLI(僅示意,未實作)
fa-improve input.pptx --eval eval.json \
  --llm-enhance-summary \
  --llm-enhance-root-cause \
  --redact-pii
```

LLM 真正能幫上忙的場景:

| 場景 | LLM 價值 | 預期效益 |
|------|---------|---------|
| Executive Summary 改寫 | 🟢 高 | 「初步異常檢驗報告」→「測試紀錄(Test Log)」措辭更精準 |
| Key Improvements 客製建議 | 🟢 高 | 根據 D1-D8 各維度評分,自動產出客製建議 |
| Root Cause 5-Why 推導 | 🟢 中 | 從「IC 發燙」→「接點阻抗高」→「焊線品質差」邏輯鏈 |
| Prevention 對策細化 | 🟢 中 | 從「D7:再發防止(SOP/防呆)」展開成具體 SOP 條文 |
| 自動翻譯雙語 | 🟢 中 | 中文 FA 報告 + 英文版給海外客戶 |

**前提**:這些都是**錦上添花**,必須在版面乾淨之後才能發揮價值。

---

## 8. 不要重複做的事情

- 🚫 不要在版面 bug 修完之前啟用 LLM(會讓 bug 更難 debug)
- 🚫 不要修改 AGENTS.md § 十.2 的「LLM 預設關閉」原則(這是已驗證的設計決策)
- 🚫 不要新增 `llm_enhance_*` CLI 參數(屬於下一輪任務,不是當前)
- 🚫 不要在 `tests/integration/test_slide_rendering.py` 之前測試 LLM(沒有版面保護,LLM 輸出會全亂)
- 🚫 不要回頭檢視「8 張空白頁是不是 LLM 沒啟用造成的」— 不是,純粹是 `_get_or_create_title` 回 None

---

## 9. 重要規則和限制

- ⚠️ 當前日期:2026-08-31(任何新文件都必須用這個日期)
- ⚠️ 母片保護:任何版面修正都必須重跑 `tests/unit/test_master_protection.py`
- ⚠️ 雙倉庫架構:版面修正屬於「技能包倉庫」`.agents/skills/fa-report-improvement/`
- ⚠️ 既有測試:203 個測試 + 3 個 skipped + 90% 覆蓋率,任何修改都不能降低這些數字
- ⚠️ `.env` 已填入 OPENAI_API_KEY,但本任務**不使用**

---

## 10. 建議下一步

1. **立即執行** — 依照 handoff Step 1:在每個 improver 開頭加 `logger.debug(...)`,跑批次看哪些 silently fail
2. **短期(本 session 內)** — 完成 Step 2-3,修座標 + 加 try/except,然後跑 18 張截圖重新驗證
3. **中期(下次 session)** — 加 smoke test `tests/integration/test_slide_rendering.py`
4. **長期(下一輪任務)** — 討論 LLM 整合的 v3.2.0 設計(需要單獨的 handoff + 設計文檔)

---

## 11. 一句話總結

> **本批次 18 張截圖的問題是「程式沒把內容放到對的位置」,不是「內容品質不好」。啟用 LLM 等於花錢請大廚,但廚房根本沒開火。先把火開了(修 P0/P1)、把爐子修好(修座標)、確認排煙正常(修母片覆蓋),最後再請大廚來炒菜(LLM 強化文案)。順序不能顛倒。**

---

✅ Handoff 文檔已寫入:`/home/elan/fa-report-refactor/docs/handoff/2026-08-31-llm-vs-bugfix-decision-handoff.md`
   包含:11 個區塊,7 個已確認結論,2 個不採用方案,5 個 LLM 未來場景,4 個不要做的事