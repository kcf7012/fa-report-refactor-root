# Handoff: 為 fa-report-improvement skill 補上「3 種執行方式」文件

> 建立日期:2026-01-15
> 交接給:下一個文件維護任務 / agent
> 工作目錄:`/home/elan/fa-report-refactor`

## 1. 任務目標

把 fa-report-improvement 技能包目前實際支援的 **3 種執行方式 + 1 種系統指令** 寫入:
- 根目錄 `docs/USER_GUIDE.md`(使用手冊)
- `.agents/skills/fa-report-improvement/README.md`(技能包 README)

讓使用者有清楚的對照表與詳細指令可參考。

## 2. 已完成內容

- ✅ `docs/USER_GUIDE.md` § 1.2 新增「執行方式選擇」對照表(4 種方式表格)
- ✅ `docs/USER_GUIDE.md` § 2.4 新增「執行方式詳細指令」完整內容(4 種方式 + 選擇指南)
- ✅ 修正 § 1.x 章節編號錯誤:原本有兩個 `### 1.1`,已重新編號為 `1.1 → 1.4`
- ✅ `.agents/skills/fa-report-improvement/README.md` 新增「4. 執行方式選擇」章節,內容與 USER_GUIDE 同步
- ✅ 兩份文件內容已對齊(對照表 + 4 種方式 + 選擇指南三處一致)

## 3. 關鍵檔案和位置

| 檔案 | 用途 |
|------|------|
| `/home/elan/fa-report-refactor/docs/USER_GUIDE.md` | 專案主要使用手冊,690+ 行,9 大章節 + 附錄 |
| `/home/elan/fa-report-refactor/.agents/skills/fa-report-improvement/README.md` | 技能包入口 README,v3.0 簡介 |
| `/home/elan/fa-report-refactor/.agents/skills/fa-report-improvement/SKILL.md` | 技能觸發與詳細說明,給 agent 讀 |
| `/home/elan/fa-report-refactor/.agents/skills/fa-report-improvement/pyproject.toml` | 定義 `fa-improve` console script(`fa_improver.cli:main`) |
| `/home/elan/fa-report-refactor/.agents/skills/fa-report-improvement/scripts/improve_fa_report.py` | 傳統 CLI(向後相容) |
| `/home/elan/fa-report-refactor/.agents/skills/fa-report-improvement/test_llm_end_to_end.py` | 端對端測試(評估+改善+成本報告) |
| `/home/elan/fa-report-refactor/docs/handoff/` | 本次新增的 handoff 歸檔目錄 |

## 4. 重要規則和限制

- ⚠️ **pi 環境下必須** `cd .agents/skills/fa-report-improvement` + `PYTHONPATH=src` 才能直接用 `python -m fa_improver`(因為這是 skill 目錄,非 Python 套件根)
- ⚠️ 文件章節編號要連續,不能跳號或重號(本次修正了兩個 `### 1.1` 的問題)
- ⚠️ 兩個文件的「執行方式」內容必須**同步**,因為 USER_GUIDE 給人類讀、skill README 給 skill 系統讀
- ⚠️ USER_GUIDE.md 與 skill README.md 是**兩份獨立維護**的文件,改一份要記得同步另一份

## 5. 已確認結論

- ✓ 技能包目前實際支援 **3 種執行方式 + 1 種系統指令**:
  1. 新 CLI:`python -m fa_improver`(推薦,完整 argparse)
  2. 傳統腳本:`python scripts/improve_fa_report.py`(向後相容,位置參數)
  3. 端對端測試:`python test_llm_end_to_end.py`(開發/展示)
  4. 系統指令:`fa-improve`(需先 `pip install -e .`)
- ✓ 對應到 3 種評估模式:預先生成 JSON / LLM 直接評估 / 離線測試(mock)
- ✓ 驗證結果:四種方式均已可用,端對端測試 12 個改善動作通過
- ✓ 兩個文件 § 1.2 與 § 4 內容一致,§ 2.4 為詳細展開

## 6. 待確認事項

- ❓ pyproject.toml 是否還需要新增其他 CLI alias — 待確認
- ❓ 上一個 session 出現的 `400 failed to read request body` 錯誤是否會在新 session 復發 — 待確認(推測為舊 session LLM API 問題,與本任務無關)
- ❓ USER_GUIDE.md 是否需要在「目錄」區塊補上 § 1.2 / § 2.4 子節連結 — 待確認(目前目錄只列主章節)

## 7. 不要重複做的事情

- 🚫 不要重新加 § 1.2「執行方式選擇」(已存在於 USER_GUIDE.md:55)
- 🚫 不要重新加 § 2.4「執行方式詳細指令」(已存在於 USER_GUIDE.md:157)
- 🚫 不要重新加 skill README.md 的「4. 執行方式選擇」(已存在於第 54 行)
- 🚫 不要改變「1.1 → 1.4」的編號順序(已驗證為正確)
- 🚫 不要把 4 種方式合併成單一說明,要維持對照表 + 詳細指令的分層結構
- 🚫 不要在對話中重新展示已寫入文件的完整內容(用 `read` 確認即可)

## 8. 建議下一步

1. **(優先)** 把這份 handoff 本身歸檔(已完成),並把 `handoff-doc-generator` 技能註冊到 pi 的 skills 清單
2. 檢查 `pyproject.toml` 是否需要補充 CLI alias(待確認事項)
3. 若有 CI/CD 文件或 README badge,補上「3 種執行方式」對照
4. 考慮把「3 種評估模式」(A/B/C)的對照表也獨立成一張總表(目前分散在 USER_GUIDE.md § 2 各小節)
5. 對 USER_GUIDE.md 跑 markdown linter,確認長度 690+ 行無 TOC 錨點損壞

---

✅ Handoff 文檔已寫入:`/home/elan/fa-report-refactor/docs/handoff/docs-3-exec-modes-handoff-20260115.md`
   包含:8 個區塊,5 個已確認結論,3 個待確認事項