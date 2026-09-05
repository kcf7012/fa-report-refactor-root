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

## 跨平台遷移狀態(WSL → macOS + CI/CD 強化)

專案原本在 WSL 開發,2026-09-05 起分階段遷移到 macOS 並強化 CI/CD(計劃書 P0-P7)。
**P0-P3 已完成並在遠端 CI 驗證過**(venv 重建、路徑解析改為 `fa_improver.paths`
統一事實來源、工具鏈版本三處對齊、macOS runner + pre-commit job + branch protection)。

**不要在這裡找「目前進度」的快照 —— 上一版就是活生生的教訓:整段四句話全錯,
而那是新 session 開場第一個讀到的檔。** 這類表格必然過期,改用指令自己看:

```bash
# 兩個 repo 是否有未推的 commit
cd <PROJECT_ROOT>                                      && git log --oneline origin/main..HEAD
cd <PROJECT_ROOT>/.agents/skills/fa-report-improvement && git log --oneline origin/main..HEAD

# CI 現況
gh run list --repo kcf7012/fa-report-refactor --limit 5
gh run list --repo kcf7012/fa-report-refactor-root --limit 5
```

- 完整計劃與任務拆解:`docs/handoff/2026-09-05-cross-platform-migration-plan-handoff.md`(P0-P7)
- 每一輪的獨立查證:`docs/handoff/2026-09-05-zoe-verification-*.md`,依檔名日期由舊到新讀;
  每份的「給 Claude Code 的指示」一節通常就是下一步待辦

### branch protection(兩個 repo 規則不同,2026-09-05 拍板)

| repo | `enforce_admins` | 直推 main |
|---|---|---|
| 技能包(`fa-report-refactor`) | `true` | ❌ 必須走 PR |
| 根倉庫(`fa-report-refactor-root`) | `false` | ✅ 可以 |

理由:技能包是要交付給別的 agent 使用的產品,嚴一點是對的。根倉庫是單人維護、
高頻小改的文件倉庫,強制自己開 PR 自己核准是演戲,反而會養成「無腦點過」的習慣。
兩個 repo 都設了 `allow_force_pushes=false`、`allow_deletions=false`
——這兩項防呆與 `enforce_admins` 無關,根倉庫放寬 review 不影響它們。
數值可能再調整,用 `gh api repos/kcf7012/<repo>/branches/main/protection` 確認現況,
不要憑這張表的印象行動。

### AGENTS.md 可能有過時內容

`AGENTS.md` 是 WSL 時期寫的舊文件。**不要假設它記載的環境細節(版本號、路徑、
工具鏈選擇)是對的**——這幾輪已經修正過好幾次,但只要沒人盯著就會再飄,曾經同一批
「已知錯誤」清單本身就在後續某次修正後變成過期清單。有疑問時以程式碼、
`pyproject.toml`、`.github/workflows/` 為準,不要照抄看起來像規則的敘述文字而不驗證。
母片保護、雙倉庫 commit 流程、Conventional Commit 格式這些**規則性**內容不受此影響,
仍然有效。

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

## ⚠️ 這個專案在 iCloud Drive 同步範圍內,會定期弄壞 venv

`~/Desktop` 已被 macOS 的「桌面與文件」功能納入 iCloud(實體在
`~/Library/Mobile Documents/com~apple~CloudDocs/Desktop/`)。後果:

| 症狀 | 機制 |
|---|---|
| `uv run python -m fa_improver` 突然 `ModuleNotFoundError` | venv 的 `.pth` 被設上 `UF_HIDDEN`,Python 的 `site.addpackage()` 會**直接跳過** hidden 的 `.pth`,editable install 因此不在 `sys.path` 上 |
| **`git commit` 被自己的 pre-commit hook 擋下** | 上述狀態下 `tests/unit/test_package_import.py` 必紅,而 pytest hook 是 `always_run` |
| 刪掉的檔案帶著原始 mtime 自己回來(`.coverage 2`) | iCloud 的衝突副本 / 雲端還原 |

**實測復發速度:清乾淨後約 10 分鐘就會長回幾千個 hidden 檔。**

### commit 前撞到 pytest 紅在 `test_package_import` 時

```bash
chflags -R nohidden .        # 在專案根目錄執行,然後重試 commit
```

這是**正常的**,不是程式壞掉 —— 那支測試就是設計來讓這個故障可見的
(在此之前它是隱形的:測試全綠但 CLI 壞掉)。

### 根治方案(2026-09-05 拍板:直接搬離 iCloud)

`UV_PROJECT_ENVIRONMENT` 環境變數方案**已評估後否決**:它只能靠 `direnv` 之類
機制注入,而 `direnv` 掛在 shell 的提示符事件上,只有互動式終端機會觸發。
Claude Code 執行指令、pre-commit hook 跑測試用的都是非互動式 shell,根本不會
觸發 —— 環境變數沒設,`uv` 就退回在專案內重建 `.venv`,等於白搬而且是**靜默
失敗**,直到 CLI 又壞掉才會發現。`uv` 也沒有任何 `pyproject.toml`/`uv.toml`
層級的等價設定,只吃環境變數,所以不存在對所有呼叫路徑都可靠的專案級寫法。

**決定:把整個專案搬出 `~/Desktop`**(例如 `~/Projects/`)。技術前提已具備:
技能包 tracked 檔裡零個寫死目前絕對路徑(P1 的成果),根倉庫僅 2 個(皆為
handoff 文件的敘述文字,不影響功能)——**搬完程式碼不用改**,只需:

```bash
uv sync --locked --extra dev --extra llm   # 舊 .venv 的 pyvenv.cfg / bin/ shebang 都寫死絕對路徑,不能直接搬
uv run pre-commit install                   # hook 的 INSTALL_PYTHON 也寫死舊路徑
```

搬家由 Kenny/柔伊主導執行,Claude Code 不要自己動手 `mv`。

完整證據與排查過程:`docs/handoff/2026-09-05-execution-findings-for-zoe-handoff.md` 發現 2;
否決 `UV_PROJECT_ENVIRONMENT` 的完整技術理由:
`docs/handoff/2026-09-05-zoe-verification-round7-p3-ci.md` 第 6 節第 8 項。

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
- **宣稱完成前,把驗收指令在最後一個 commit 之後再跑一遍。** 中途通過不算數 ——
  環境類的驗收(能不能 import、指令跑不跑得動)會在幾分鐘內失效。報告數字時附上當時的 HEAD SHA。
- **驗收要包含「我聲稱修改的檔案,是否真的都在 diff 裡」。** 用 `git show --name-only`
  或 `git diff --name-only` 對照自己列的待辦清單。連續兩輪敗在同一個地方:**改了一部分
  就宣告「一律」**(AGENTS.md 那次、README badge 那次)。
- **對「時效性證據」(會被覆寫、刪除、重新產生的檔案狀態)下判定時,只能寫「無法驗證」,
  不能寫「不實」。** 要下「不實」必須有正面反證,不能只憑「我重現不出來」——證據消失
  不代表證據不存在過。反例:曾把一份 mtime 觀測記錄誤判為「不實」,後來被證明原始觀測
  沒錯,只是同名檔案已被另一批取代;過度延伸推論比不下判斷更糟。
  見 `docs/handoff/2026-09-05-zoe-verification-p0p2-execution.md` 與
  `docs/handoff/2026-09-05-zoe-verification-round6-redflag-fixes.md` 第 4 節。
- **Handoff 文檔**:`docs/handoff/<YYYY-MM-DD>-<task-slug>-handoff.md`。寫日期前用 `date` 確認今天,不要沿用文件裡的舊日期。
- **版本號**:改版時 `pyproject.toml` + `src/fa_improver/__init__.py` + `SKILL.md` frontmatter 三處必須同步(四個 README 也常漏,見計劃書 P6)。
- 型別提示用 Python 3.10+ 語法(`list[X]`、`X | None`)。
- 這個 shell 的 `grep` 是包裝函式且預設 `--exclude-dir=.git`;要掃 `.git/` 內容必須用 `find .git -type f -exec command grep -l ... {} +`,否則會**靜默回傳空結果**。
