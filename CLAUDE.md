# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

半導體 FA(Failure Analysis)報告智慧化改善工具。輸入一份 `.pptx` 報告 + 一份評估結果,依 6 個評估維度自動補上改善投影片,**且絕對不能破壞公司母片**。

---

## 語言

- **回覆、commit message、handoff 文檔、程式碼註解一律使用台灣繁體中文。**
- **技術術語保留英文原文,不要硬翻成中文**:placeholder、layout、fixture、commit、branch protection、coverage、lint、hook、stash、upstream、pipeline、fallback、resolver、mixin 等直接寫英文。
- 用台灣慣用詞,避免中國大陸用語:**程式碼**(非「代碼」)、**檔案**(指 file 時,非「文件」)、資料夾、記憶體、預設值、函式、變數、字串。
  > 既有文件(含 `AGENTS.md`)還有少數「代碼」等用詞未統一,新寫的內容請用台灣用法。

---

## ⚠️ 這個 repo 正在從 WSL 遷移到 macOS,尚未完成

專案原本在 Windows WSL(`/home/elan/fa-report-refactor/`)開發,整個目錄被**複製**(不是 clone)到目前的 macOS 路徑。因此有幾件事現在是壞的:

| 現況 | 影響 |
|---|---|
| `.agents/skills/fa-report-improvement/.venv/` 是 Linux x86-64 ELF | `.venv/bin/python` 執行會 `exec format error`,連 `uv sync` 都被擋住 |
| 技能包 `.git/hooks/pre-commit` 寫死 WSL 路徑 | **該 repo 任何 `git commit` 都會失敗**;需 `uv run pre-commit install` 重新產生 |
| `tests/integration/_fixture_resolver.py` 硬編 `/home/elan/...` | 真實客戶 pptx 存在卻找不到 → 16 個視覺回歸測試**靜默降級**跑合成 fixture(不報錯、不 skip) |
| 技能包 `.git/config` 的 `user.email` 是不存在的位址 | commit 署名錯誤 |
| 技能包 `main` 沒有 upstream 追蹤 | `git pull` 會 fatal |

**完整的遷移與修正計劃在 `docs/handoff/2026-09-05-cross-platform-migration-plan-handoff.md`(P0-P7)。動手前先讀它**,不要自己重新發明修法。

### 目前進度(2026-09-05)

| 項目 | 狀態 |
|---|---|
| 計劃書 | 已完成並經獨立複查,**Kenny 審閱中,尚未授權執行** |
| P0-P7 | **全部尚未開始**,程式碼一行未改 |
| 根倉庫 | 有數個 commit 在本地 `main`,**未 push** |
| 技能包倉庫 | 完全未動,HEAD 與 `origin/main` 同步 |

> 接手時先跑 `git log --oneline origin/main..HEAD` 與 `git status` 確認實際狀態,不要以本表為準——這行字會過時。
> **未經 Kenny 明確指示不要開始執行 P0,也不要 push。**

### AGENTS.md 有已知錯誤,不要照抄

`AGENTS.md` 是 WSL 時期寫的,以下內容**目前是錯的**(計劃書 P5 會修):

- 所有 `cd /home/elan/fa-report-refactor` 指令(`:50,53,268,280`)
- `:20` 宣稱 uv 0.12.7+(v3.1.5 起本機與 CI 都是 0.8.22)
- `:23,95` 宣稱有 black(`.pre-commit-config.yaml` 已停用)
- `:326` 的 `.venv/bin/python`(改用 `uv run`)

其餘規則(母片保護、雙倉庫 commit 流程、Conventional Commit 格式)仍然有效。

---

## 雙倉庫架構(最重要的結構事實)

```
fa-report-refactor/                              ← 根倉庫 (kcf7012/fa-report-refactor-root)
├── docs/ AGENTS.md README.md report/            ← 根倉庫追蹤
└── .agents/skills/fa-report-improvement/        ← 獨立 git repo (kcf7012/fa-report-refactor)
    └── src/ tests/ SKILL.md CHANGELOG.md ...
```

- 根 `.gitignore` 有 `.agents/`,所以**根倉庫看不到技能包的任何檔案**。兩個 git 完全獨立,各自 commit、各自 push。
- **程式碼改動一律在技能包倉庫**;`docs/`、`report/` 在根倉庫。
- 兩邊都有 `report/` 目錄:根倉庫的放**真實客戶檔**,技能包的放 CI 動態產生的測試 fixture。路徑解析要能區分兩者。

---

## 常用指令

全部在技能包目錄下執行,一律用 `uv run`(不要用 `.venv/bin/...`,那是 POSIX-only 且目前是壞的):

```bash
cd .agents/skills/fa-report-improvement

uv sync --extra dev --extra llm         # 建立環境(Python 3.10,見 .python-version)
uv run pytest tests/ -q                 # 全部測試
uv run pytest tests/unit/test_master_protection.py -v   # 母片保護(改母片相關程式碼必跑)
uv run pytest tests/integration/test_visual_quality.py::TestNoTitleDecorationOverlap -v   # 單一類別
uv run pytest tests/ -q -k "title"      # 依名稱篩選
uv run ruff check src/ tests/ scripts/
uv run ruff format --check src/ tests/ scripts/
uv run pre-commit run --all-files

# 實際跑一次改善
uv run python -m fa_improver <input.pptx> --eval <eval.json> --output <out.pptx>
```

`pyproject.toml` 的 `addopts` 已內建 `--cov=fa_improver --cov-report=term-missing`,所以任何 pytest 呼叫都會跑覆蓋率;沒裝 dev extra 時 `pytest` 會因無法識別參數而直接失敗。

基準數字**取決於真實客戶 pptx 在不在位**,只寫一個數字必定在另一個情境變成錯的:

| 情境 | 測試 | 覆蓋率 |
|---|---|---|
| CI / 乾淨 clone(只有合成 fixture) | 235 passed + **3 skipped** | **85%** |
| 真實客戶檔在位(根倉庫 `report/`) | 238 passed + **0 skipped** | **89%** |

**這台機器上正常值是 0 skipped**;出現 3 skipped 代表路徑解析失效、真實客戶檔沒被讀到
(v3.1.5 前的舊值 233/3/85% 就是這種降級狀態)。CI 上 3 skipped 才是正常的。

---

## 改善流程的架構

```
eval JSON/TXT ─→ parsers/evaluation_parser ─→ domain/evaluation (6 個 Dimension + GapSeverity)
                                                      │
                          improvers/orchestrator.build_plan()  依維度落差決定要加哪些投影片
                                                      │
                          improvers/orchestrator.execute()  逐一呼叫對應 improver
                                                      │
    basic_info / problem_definition / analysis_method / evidence_checklist /
    root_cause (5-Why + 統計) / prevention (對策 + IQC + 監控) / summary
                                                      │
                          全部經由 improvers/_safe_shape.py 建立 shape
                                                      │
                          layout/protector.MasterProtector 驗證母片未被改動
```

**`improvers/_safe_shape.py` 是所有版面邏輯的單一出口**,不要在 improver 裡直接呼叫 `slide.shapes.add_textbox()`:

- `safe_textbox()` — 強制 `rotation=0`、`auto_size=None`,避開母片繼承來的旋轉/直排屬性
- `get_or_create_title()` / `get_or_create_body()` — 找不到合適 placeholder 時 fallback 建立新 textbox
- `TITLE_SAFE_LEFT_INCH = 1.2` — 避開母片左上裝飾區的安全左界;各 improver 用 `TITLE_SAFE_LEFT_INCH - 0.2` 當內容 margin
- ⚠️ **已知結構缺口**:`get_title_placeholder()` 在原生 placeholder 分支直接 `return ph`,完全不檢查 `left` 座標,所以安全常數在最常見的路徑上不生效。修法見計劃書 P4,不要自行改動數值。

版面尺寸全部是寫死英吋且從不量測文字寬度;程式碼**從不設定 `font.name`**(刻意繼承母片主題字型)。

---

## 母片保護(最高優先原則)

FA 報告含公司機密(Logo、機密等級標示、部門色系)。`layout/protector.py` 的 `MasterProtector` 在改善前後各拍一次快照比對:母片 XML 不變、layout 數量不變、不刪除任何原始投影片。

**`tests/unit/test_master_protection.py` 失敗時絕對不能合併。** 任何動到 placeholder 幾何、layout 選擇、或 shape 增刪的改動,都要跑這支測試。

---

## 測試 fixture 的兩層解析

`tests/integration/_fixture_resolver.py` 先找真實客戶 pptx,找不到才 fallback 到 `tests/integration/_synthetic_fixtures/` 的去識別化合成檔。這個設計是為了讓 CI(沒有客戶檔)也能跑視覺回歸測試。

失效時**不會報錯**,只會安靜地改用較弱的 fixture —— 加測試時要確認你的測試在兩種來源下都有意義。`tests/conftest.py` 另有一套向上搜尋 `report/` 的機制,兩者目前不一致(計劃書 P1 要統一)。

`FA_REPORT_PROJECT_ROOT` 環境變數可覆寫搜尋根目錄。

---

## 路徑規則(這次遷移的核心教訓)

- **不要寫任何絕對路徑字面值**。用 `pathlib` + `__file__` 錨定,或環境變數。
- 分隔多個路徑用 `os.pathsep`,不要寫死 `":"`。
- 指令一律 `uv run <cmd>`,不要 `.venv/bin/<cmd>`。
- 文件裡用 `<PROJECT_ROOT>` 佔位,不要填某台機器的實際路徑。
- 歷史教訓:第一輪稽核抓到測試硬編路徑,修法只是把路徑**搬進** resolver 的預設值,沒有真正消除;失效方式從「看得見的 skip」變成「看不見的降級」,連續三輪稽核都沒發現。

---

## 慣例

- **Conventional Commit + 中文訊息**:`<prefix>: <50 字內簡述>`,prefix 用 `feat/fix/docs/chore/refactor/test/style/perf/ci`。
- **Handoff 文檔**:`docs/handoff/<YYYY-MM-DD>-<task-slug>-handoff.md`。寫日期前用 `date` 確認今天,不要沿用文件裡的舊日期。
- **版本號**:改版時 `pyproject.toml` + `src/fa_improver/__init__.py` + `SKILL.md` frontmatter 三處必須同步(四個 README 也常漏,見計劃書 P6)。
- 型別提示用 Python 3.10+ 語法(`list[X]`、`X | None`)。
- 這個 shell 的 `grep` 是包裝函式且預設 `--exclude-dir=.git`;要掃 `.git/` 內容必須用 `find .git -type f -exec command grep -l ... {} +`,否則會**靜默回傳空結果**。
