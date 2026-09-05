# AGENTS.md — FA Report Refactor 專案指南

> **給 AI coding agent(pi、Claude Code、GPT 等)在這個專案工作的規則**
>
> 本檔規範 agent 在本專案的行為、慣例、與可用工具。專案根目錄以 `<PROJECT_ROOT>` 表示,實際位置依機器而定,不要寫死。
>
> ⚠️ **寫日期前先跑 `date "+%Y-%m-%d"` 確認今天**——不要沿用本檔或任何文件裡出現過的日期。
> 舊版本曾在此硬編某一天的日期,導致後續 handoff 與 CHANGELOG 全部寫錯,已移除。
>
> 📌 **Claude Code 使用者請先讀 `<PROJECT_ROOT>/CLAUDE.md`**——該檔記錄目前這台機器的實際狀態(含遷移未完成造成的故障)與正確指令。

---

## 一、專案速覽

| 項目 | 值 |
|------|-----|
| **名稱** | fa-report-refactor |
| **用途** | 半導體 FA(Failure Analysis)報告智慧化改善工具 |
| **當前版本** | v3.1.4 tag,但 `main` HEAD 已超前 5 個 commit(回歸修正未進 tag);下一版規劃 v3.1.5 |
| **Git 倉庫** | 雙倉庫架構(根倉庫 + 技能包子倉庫) |
| **主語言** | Python ≥ 3.10 |
| **套件管理** | uv(取代 pip + venv)。版本以 `.github/workflows/test.yml` 的 `UV_VERSION` 為準,本機用 `uv --version` 確認 |
| **測試框架** | pytest + pytest-cov |
| **測試結果** | **233 passed + 3 skipped,覆蓋率 85%**(多處舊文件誤植 90%,以實跑為準) |
| **Lint** | ruff(check + format)。black 已停用,見 `.pre-commit-config.yaml` 註解 |
| **主入口** | `.agents/skills/fa-report-improvement/src/fa_improver/cli.py` |

---

## 二、雙倉庫架構(極重要!)

本專案使用**雙 git 倉庫**:

```
<PROJECT_ROOT>/                                       ← 根倉庫
├── .agents/skills/fa-report-improvement/.git/        ← 技能包子倉庫
├── docs/                                              ← 根倉庫追蹤
├── AGENTS.md (本檔)                                   ← 根倉庫追蹤
├── README.md                                          ← 根倉庫追蹤
└── report/                                            ← 根倉庫追蹤
```

| 倉庫 | 追蹤範圍 | 用途 |
|------|---------|------|
| **根倉庫**(`<PROJECT_ROOT>/`) | `docs/` + `report/` + `AGENTS.md` + 根 `README.md` | 文件、評估、設計 |
| **技能包倉庫**(`.agents/skills/fa-report-improvement/`) | `SKILL.md` + `src/` + `tests/` + `references/` | 程式碼、測試、樣板 |

### ⚠️ commit 時要小心

```bash
# 在根倉庫工作(預設)
cd <PROJECT_ROOT>

# 在技能包倉庫工作
cd <PROJECT_ROOT>/.agents/skills/fa-report-improvement

# 兩個 git 各自獨立!commit 互不影響
```

---

## 三、檔案結構(速覽)

```
fa-report-refactor/
├── AGENTS.md                           ← 本檔(agent 規範)
├── README.md                           ← 專案入口
│
├── docs/                               ← 根倉庫追蹤
│   ├── 00_executive_summary.md         ← 給「只想知道重點」的人
│   ├── 01_assessment.md                ← 完整評估(20 個問題分級)
│   ├── 02_refactor_plan.md             ← 5 階段重構計畫
│   ├── 03_design_comparison.md         ← v2.3 vs v3.0 視覺對比
│   ├── 04_summary_design.md            ← Summary 拆解設計
│   ├── 05_prevention_design.md         ← 改善對策拆解設計
│   ├── 06_expansion_patterns.md        ← 通用展開模式
│   ├── 07_llm_agent.md                 ← LLM 整合詳細設計 ⭐
│   ├── 08_uv_integration.md            ← uv 套件管理
│   ├── 09_improvement_coverage.md      ← 6 維度 100% 覆蓋證明
│   ├── 10_api_reference.md             ← v3.0.1 公開 API 參考手冊 ⭐
│   ├── USER_GUIDE.md                   ← 終端使用者手冊 ⭐
│   ├── TESTING.md                      ← 測試規範
│   ├── VISION.md                       ← v3.0 智慧化願景
│   ├── README.md                       ← docs/ 索引
│   ├── PHASE2-5_TODO.md                ← 歷史任務清單(全部 ✅ 完成)
│   └── handoff/                        ← 任務交接文檔
│       └── YYYY-MM-DD-*-handoff.md    ← 命名:<日期>-<task-slug>-handoff.md
│
├── .agents/skills/                     ← ★ 技能包總目錄
│   ├── fa-report-improvement/          ← 主技能包(獨立 git 倉庫)
│   │   ├── SKILL.md                    ← 技能包入口(給 agent 讀)
│   │   ├── README.md                   ← 給人類讀的簡介
│   │   ├── CHANGELOG.md                ← 版本紀錄(v3.0.0 + v3.0.1)
│   │   ├── pyproject.toml              ← 套件設定(含 [tool.pytest.ini_options])
│   │   ├── uv.lock                     ← 依賴鎖定(51 套件)
│   │   ├── .pre-commit-config.yaml     ← Git hooks(ruff / ruff-format / 基本檢查 / pytest)
│   │   ├── requirements.txt            ← pip fallback(向後相容)
│   │   ├── src/fa_improver/            ← 主程式碼(39 個 .py)
│   │   ├── tests/                      ← 233 passed + 3 skipped
│   │   ├── references/                 ← 領域知識(5 份)
│   │   └── scripts/                    ← 向後相容 CLI 入口
│   │
│   ├── handoff-doc-generator/          ← 任務交接文檔產生器技能
│   ├── commit-helper/                  ← Conventional commit 訊息產生器
│   └── code-reviewer/                  ← 自動化程式碼審查(只給建議不修改)
│
└── report/                             ← FA 報告與評估 JSON
```

---

## 四、必讀文件(agent 接手時的優先順序)

### 4.1 第一次進入專案(30 秒)
1. **本檔**(`AGENTS.md`)— 你正在讀的
2. `docs/00_executive_summary.md` — 重點摘要
3. `docs/README.md` — docs/ 索引

### 4.2 理解架構(5 分鐘)
4. `docs/VISION.md` — 智慧化願景
5. `docs/02_refactor_plan.md` — 5 階段重構計畫
6. `docs/10_api_reference.md` — 35 模組 API 參考 ⭐

### 4.3 開始工作
7. `docs/USER_GUIDE.md` — 使用手冊(若有實際使用需求)
8. `.agents/skills/fa-report-improvement/SKILL.md` — 技能包入口

### 4.4 ⭐ 目前進行中(最優先,先讀這兩份)
9. `docs/handoff/2026-09-05-cross-platform-migration-plan-handoff.md` — **跨平台遷移 + 稽核修正執行計劃(P0-P7)**。專案剛從 WSL 搬到新環境,有數項現行故障未修,動手前必讀。
10. `docs/handoff/2026-09-04-fa-report-refactor-audit-round3-handoff.md` — 第三輪獨立稽核。含 `get_title_placeholder()` 的結構性缺口(連續三輪未解)。

### 4.5 理解歷史決策
11. `docs/handoff/2026-09-02-fa-report-refactor-audit-handoff.md` — 第一輪獨立稽核(v3.1.2/v3.1.3),含降級為 backlog 的 3 項
12. `docs/handoff/2026-09-03-audit-remediation-plan-handoff.md` — 第一輪的改善計畫(Kenny 拍板)
13. `docs/handoff/2026-09-03-next-audit-cycle-planning.md` — 稽核週期 SOP(⚠️ 第 77 行仍指向舊 tag,計劃書 P5 會修)
14. `docs/handoff/2026-09-04-v3.1.4-regression-fix-handoff.md` — 標題偏左回歸修正紀錄
15. `docs/handoff/2026-09-01-v313-user-feedback-fixes-handoff.md` — v3.1.3 三個版面問題修正
16. `docs/handoff/2026-09-01-v312-final-fixes-handoff.md` — v3.1.2 修 v3.1.1 殘留 4 大渲染問題
17. `docs/handoff/2026-09-01-v311-incomplete-rendering-handoff.md` — v3.1.1 未完成項揭露
18. `docs/handoff/2026-09-03-pr-merge-flow-playwright-guide.md` — PR + Merge 流程教學
19. ~~`docs/handoff/2026-08-31-honest-phase-completion-check-handoff.md`~~(已全部完成,參考 § 十一)
20. `docs/PHASE2-5_TODO.md` — 歷史任務清單(已完成,有誠實標記的差距)

> ⚠️ `docs/handoff/` 底下多數是 WSL 時期的紀錄,內文的絕對路徑是**當時的事實**,刻意不改寫。讀它們是為了理解決策脈絡,**不要照著裡面的路徑或指令執行**。

---

## 五、可用技能包(4 個)

本專案有 4 個 `.agents/skills/`,agent **應主動運用**:

### 5.1 ⭐ fa-report-improvement(主技能包)

**觸發**:使用者給定 .pptx / .ppt + 評估檔,要求改善 FA 報告

**位置**:`.agents/skills/fa-report-improvement/`

**入口**:`src/fa_improver/cli.py`

**典型用法**:
```bash
cd .agents/skills/fa-report-improvement
uv run python -m fa_improver input.pptx --eval eval.json --output improved.pptx
```

**詳見**:該技能包內 `SKILL.md`

### 5.2 handoff-doc-generator(自動交接文檔)

**觸發**:使用者說「寫交接文檔」「handoff」「幫我交接給下一個任務」

**產出**:`docs/handoff/<YYYY-MM-DD>-<task-slug>-handoff.md`

**8 大區塊**:目標 / 完成內容 / 關鍵檔案 / 規則 / 結論 / 待確認 / 避免重做 / 下一步

**詳見**:`.agents/skills/handoff-doc-generator/SKILL.md`

### 5.3 commit-helper(自動 commit)

**觸發**:使用者說「幫我 commit」「寫個 commit」「git commit」

**自動產生**:Conventional commit prefix(`feat:` / `fix:` / `docs:` / `chore:` 等)+ 中文訊息

**安全機制**:
- 🚫 不 commit `.env` / `__pycache__` / `venv/` / `.venv/`
- 🚫 不自動 push

**詳見**:`.agents/skills/commit-helper/SKILL.md`

### 5.4 code-reviewer(只給建議不修改)⭐

**觸發**:使用者說「code review」「幫我看程式碼」「review 一下」

**🚨 絕對原則**:只給建議,**不修改**使用者程式碼
- 即使發現 P0 bug、安全漏洞、lint 錯誤
- 即使使用者說「順手修一下」
- 例外:`docs/`、`*.md`、`handoff/` 等非程式碼檔可以產生報告

**7 大維度**:正確性 / 可讀性 / 可維護性 / 測試 / 安全 / 效能 / 規範

**3 級嚴重度**:P0(必須修)/ P1(應修)/ P2(可延後)

**詳見**:`.agents/skills/code-reviewer/SKILL.md`

---

## 六、核心工作規則

### 6.0 語言

- **一律使用台灣繁體中文**撰寫回覆、commit message、handoff 文檔與程式碼註解。
- **技術術語保留英文原文,不要硬翻**。例如 placeholder、layout、fixture、commit、branch protection、coverage、lint、hook、stash、upstream、pipeline、fallback 等,直接用英文,不要譯成「佔位符」「版面配置」「基準線」之類。
- 用台灣慣用詞,不要用中國大陸用語。常見對照:**程式碼**(非「代碼」)、**檔案**(指 file 時,非「文件」)、資料夾、記憶體、預設值、函式、變數、迴圈、字串、介面。
- 混排時中英文之間不加空格與否維持全檔一致即可,不強制。


### 6.1 修改程式碼前的必做事項

1. **讀檔案** — 不要憑印象評價(用 `read` 工具讀完整檔案)
2. **確認日期** — 寫日期前用 `date` 指令確認今天
3. **理解上下文** — 看相關測試與文件
4. **檢查 git 狀態** — `git status` 確認沒有意外的變更(注意是**哪一個** repo,見 § 二)

### 6.2 修改程式碼後的必做事項

1. **跑測試**:`cd .agents/skills/fa-report-improvement && uv run pytest tests/ -q`
2. **檢查 ruff**:`uv run ruff check src/ scripts/ tests/`
3. **不要用 `--no-verify`** 跳過 pre-commit(除非 pre-commit 本身卡住)
4. **寫 commit** — 使用 `commit-helper` 技能
5. **確認 git 乾淨** — `git status` 應為空

### 6.3 不要做的事

- 🚫 不要在根倉庫 commit 技能包內的檔案(那是子仓库)
- 🚫 不要 commit `.env`、`.venv/`、`venv/`、`__pycache__/`(已寫進 .gitignore)
- 🚫 不要「順手修」code-reviewer 提出的問題(絕對原則)
- 🚫 不要使用過時日期(如 2026-01-15)寫入新文件
- 🚫 不要修改母片相關程式碼而不跑 `tests/unit/test_master_protection.py`
- 🚫 不要跳過測試(就算時間壓力大)
- 🚫 不要 commit `uv.lock` 以外的多餘 lock 檔(如 `poetry.lock`、`Pipfile.lock`)

---

## 七、Python 編碼風格

### 7.1 ruff 規則(`pyproject.toml`)

```toml
[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "SIM"]
ignore = ["E501"]  # line-too-long(交給 black)
```

**常見禁用**:
- `bare except:`(用 `except Exception:` 或更具體)
- 單字母變數 `l`(用 `lo` / `line` 等)
- 未使用的變數 / 函式
- 巢狀 `with`(用單一 `with` 多 context)
- 函式命名 PascalCase(用 snake_case)

### 7.2 型別提示

- 必須用 Python 3.10+ 語法:`list[X]`、`X | None`(非 `Optional[X]` / `Union[X, Y]`)
- 公開函式必須有完整 type hints
- 內部函式鼓勵但非必要

### 7.3 測試規範(`docs/TESTING.md`)

- 測試檔案:`tests/unit/test_<module>.py` 或 `tests/integration/test_<flow>.py`
- 類別:`Test<Feature>`(PascalCase)
- 方法:`test_<scenario>_<expected>`(snake_case)
- AAA 模式:Arrange / Act / Assert
- 母片保護測試必寫
- 覆蓋率目標:**≥ 80%**(目前 85%)

---

## 八、Git 工作流

### 8.1 雙倉庫的 commit 流程

```bash
# 1. 在根倉庫工作(預設)
cd <PROJECT_ROOT>
git status
git add docs/AGENTS.md
git commit -m "docs: 加入 AGENTS.md"

# 2. 切到技能包倉庫
cd .agents/skills/fa-report-improvement
git status
git add src/ tests/
git commit -m "feat: 新增 X 功能"

# 3. 兩個倉庫各自獨立 push(若需要)
cd <PROJECT_ROOT>
git push origin main
cd .agents/skills/fa-report-improvement
git push origin main
```

### 8.2 Conventional Commit 格式

由 `commit-helper` 技能自動產生,或手動:

```bash
git commit -m "<prefix>: <中文簡述 50 字內>" -m "<詳細說明條列>"
```

| prefix | 用途 |
|--------|------|
| `feat:` | 新功能 |
| `fix:` | Bug 修正 |
| `docs:` | 純文件 |
| `chore:` | 雜項(配置、依賴) |
| `refactor:` | 重構(不修行為) |
| `test:` | 測試新增 |
| `style:` | 純格式化 |
| `perf:` | 效能優化 |
| `ci:` | CI 設定 |

---

## 九、母片保護(最高優先原則)

半導體 FA 報告含公司機密資訊,**母片絕對不能被破壞**:

- 🛡️ ELAN 公司 Logo、標語、雲霄建築底圖
- 🛡️ 機密等級標示(Confidential Information)
- 🛡️ 各部門色系與字型

### 9.1 每次投影片操作後必須驗證

- 母片 XML 完全不變
- Layout 數量不變(不可新增 layout)
- 不可刪除任何原始投影片
- 不可修改母片背景、shape、image

### 9.2 跑專門測試

```bash
uv run pytest tests/unit/test_master_protection.py -v
```

**不可繞過** — 若失敗,絕對不能合併。

---

## 十、LLM 整合

技能包支援 OpenAI API 整合(`src/fa_improver/llm/openai_client.py`)。

### 10.1 設定 API Key

```bash
cp .env.example .env
# 編輯 .env 填入 OPENAI_API_KEY
```

### 10.2 ✅ 安全強化(個資遮罩)

v3.1.0 起,LLM 送出前可自動遮罩個資:

- ✅ `src/fa_improver/llm/redact.py` **已實作**
- **遮罩類型**:電話、Email、中文姓名、IP、工號、身分證、信用卡
- **啟用方式**:
  - CLI:`fa-improve input.pptx --llm-provider openai --redact-pii ...`
  - Python:`OpenAIClient(redact_pii_before_send=True)`
- **詳細用法**:參見 CHANGELOG v3.1.0 章節

預設關閉(向後相容)。建議對真實報告**啟用遮罩**。

### 10.3 重試機制(tenacity)

v3.1.0 起,OpenAI client 自動處理瞬時錯誤:

- **重試策略**:tenacity exponential backoff(1s → 2s → 4s,最多 `max_retries` 次)
- **不重試**:認證錯誤(401 / Invalid api_key)— 立即拋出 `LLMAuthError`

---

## 十一、v3.1.0 優化項(✅ 全部完成於 2026-08-31)

8 項 v3.1+ 優化項已全部完成並在 v3.1.0 tag 發布。詳見各項目的 commit:

| 優先 |項目 | Commit | 狀態 |
|------|------|--------|------|
| 🔴 P0 | 個資遮罩(`llm/redact.py`) | `92c9a68` | ✅ 完成 |
| 🟡 P1 | 重試機制(tenacity) | `559c9e4` | ✅ 完成 |
| 🟡 P1 | 7 個 improver 用 TemplateLoader | `02cd238` | ✅ 完成 |
| 🟢 P2 | 3 個 improver 用視覺元素 | `bbb28ba` | ✅ 完成 |
| 🟢 P2 | `--api-key` CLI 參數 | `b5fbfba` | ✅ 完成 |
| 🟢 P2 | `test_template_validation.py` | `9a39076` | ✅ 完成 |

**成果**:測試 102 → 203(+101),tag `v3.1.0` 已建立。(當時 handoff 宣稱覆蓋率達 90%,但獨立稽核與 CI log 實測都是 85%,此處不再沿用該數字。)

下一輪任務參考 `docs/handoff/` 最新交接文檔。

---

## 十二、疑難排解速查

| 問題 | 解決 |
|------|------|
| `ModuleNotFoundError: fa_improver` | 用 `uv run`(不要用 `.venv/bin/...`,那是 POSIX-only 路徑) |
| pre-commit 卡住 | 用 `git commit --no-verify` 跳過(但要先理解為何失敗) |
| ruff 報錯 | `uv run ruff check --fix`(自動修大部分) |
| 母片保護測試失敗 | **絕對不能合併**,先修程式碼 |
| LLM API 失敗 | 檢查 `.env` 的 `OPENAI_API_KEY` |
| 想查 git log | `git log --oneline -20`(看近期 commit) |
| 確認今天日期 | `date "+%Y-%m-%d"` |

---

## 十三、相關連結

- **pi coding agent**:https://github.com/earendil-works/pi
- **uv 套件管理**:https://docs.astral.sh/uv/
- **ruff linter**:https://docs.astral.sh/ruff/
- **python-pptx**:https://python-pptx.readthedocs.io/
- **pytest**:https://docs.pytest.org/

---

**最後更新**:2026-09-05(修正 WSL 時期遺留的寫死路徑與過時數字)
**維護者**:Kenny Kang (ELAN FA Report 專案)
**授權**:MIT