# Handoff: v3.1.0 Git 推送總結與雙倉庫架構

> 建立日期:2026-08-31
> 對象:專案成員、維護者、未來接手 Agent
> 工作目錄:`/home/elan/fa-report-refactor/`

## 1. 推送結論

### ✅ v3.1.0 完整釋出並推送至 GitHub

本專案採用**雙 git 倉庫**架構,2026-08-31 完成 v3.1.0 釋出,**兩個倉庫已獨立推送至 GitHub**:

| 倉庫 | URL | 內容 | Tag |
|------|-----|------|-----|
| 🔧 **主倉庫**(技能包) | https://github.com/kcf7012/fa-report-refactor | 原始碼、測試、CHANGELOG、SKILL.md | **`v3.1.0`** |
| 📚 **根倉庫**(文件) | https://github.com/kcf7012/fa-report-refactor-root | AGENTS.md、docs/、report/ | (無 tag) |

### 對外可達連結

- **主倉庫首頁**:https://github.com/kcf7012/fa-report-refactor
- **根倉庫首頁**:https://github.com/kcf7012/fa-report-refactor-root
- **v3.1.0 Release**:https://github.com/kcf7012/fa-report-refactor/releases/tag/v3.1.0

---

## 2. 推送過程紀錄(給未來參考)

### 2.1 背景

本專案從 v3.0.0 起使用**雙 git 倉庫架構**:

```
/home/elan/fa-report-refactor/                        ← 根倉庫(獨立 .git)
├── .agents/skills/fa-report-improvement/.git/        ← 技能包子倉庫(獨立 .git)
├── docs/                                              ← 根倉庫追蹤
├── AGENTS.md / README.md                              ← 根倉庫追蹤
└── report/                                            ← 根倉庫追蹤
```

兩個倉庫**各自獨立 commit**,不能合併到同一個分支。

### 2.2 第一次推送(失敗 — Permission denied)

```bash
# 嘗試推到 https://github.com/KennyKang7012/fa-report-refactor
git push -u origin main
# ❌ remote: Permission to KennyKang7012/fa-report-refactor.git denied to kcf7012.
# ❌ fatal: unable to access ... 403
```

**原因**:Git 認證帳號 `kcf7012` 與倉庫擁有者 `KennyKang7012` 不一致。

### 2.3 第二次推送(部分成功 — 倉庫衝突)

```bash
# 改推到 https://github.com/kcf7012/fa-report-refactor
# 根倉庫 main 推送成功
# ❌ 技能包倉庫推送被拒(同一個 URL 已有根倉庫內容)
# Updates were rejected because the remote contains work that you do not have locally.
```

**問題**:兩個倉庫的 commit 歷史完全不同,但用同一個 URL 不能共存。

### 2.4 最終解決 — 兩個獨立倉庫(推薦架構)

使用者建立第二個 GitHub 倉庫 `https://github.com/kcf7012/fa-report-refactor-root`,兩個倉庫各指各的 URL:

```bash
# 根倉庫 → fa-report-refactor-root.git
cd /home/elan/fa-report-refactor
git remote add origin https://github.com/kcf7012/fa-report-refactor-root.git
git push -u origin main  # ✅ 成功

# 技能包倉庫 → fa-report-refactor.git(覆蓋先前的根倉庫內容)
cd .agents/skills/fa-report-improvement
git remote add origin https://github.com/kcf7012/fa-report-refactor.git
git push --force-with-lease origin main  # ✅ 成功
git push origin v3.1.0  # ✅ tag 推送成功
```

**注意**:`--force-with-lease` 是因為遠端已有先前的根倉庫 main,需要覆蓋。`--force-with-lease` 比 `--force` 安全(若遠端有其他人的 commit 不會覆蓋)。

---

## 3. Git Remote 設定(未來操作參考)

### 3.1 根倉庫

```bash
cd /home/elan/fa-report-refactor
git remote -v
# origin  https://github.com/kcf7012/fa-report-refactor-root.git (fetch)
# origin  https://github.com/kcf7012/fa-report-refactor-root.git (push)
```

### 3.2 技能包倉庫

```bash
cd /home/elan/fa-report-refactor/.agents/skills/fa-report-improvement
git remote -v
# origin  https://github.com/kcf7012/fa-report-refactor.git (fetch)
# origin  https://github.com/kcf7012/fa-report-refactor.git (push)
```

### 3.3 推送指令速查

```bash
# === 根倉庫(文件) ===
cd /home/elan/fa-report-refactor
git add docs/ AGENTS.md report/
git commit -m "docs: ..."
git push origin main

# === 技能包倉庫(原始碼) ===
cd /home/elan/fa-report-refactor/.agents/skills/fa-report-improvement
git add src/ tests/ pyproject.toml CHANGELOG.md
git commit -m "feat: ..."
git push origin main
git push origin vX.Y.Z  # 推送新 tag
```

---

## 4. v3.1.0 釋出內容摘要

### 4.1 8 項 v3.1+ 優化項(全部完成)

| # | Commit | 項目 | 優先 |
|---|--------|------|------|
| 1 | `92c9a68` | feat(llm): 加入個資遮罩模組 redact.py | 🔴 P0 |
| 2 | `559c9e4` | feat(llm): 加入 tenacity 重試機制 | 🟡 P1 |
| 3 | `02cd238` | feat(improvers): 7 個 improver 整合 TemplateLoader | 🟡 P1 |
| 4 | `bbb28ba` | feat(improvers): 3 個 improver 整合視覺元素 | 🟢 P2 |
| 5 | `b5fbfba` | feat(cli): 加入 --api-key、--redact-pii、--base-url CLI 參數 | 🟢 P2 |
| 6 | `9a39076` | test: 加入 test_template_validation.py | 🟢 P2 |
| 7 | `5addfd2` | docs: 版本號 v3.0.1 → v3.1.0 + CHANGELOG 新增章節 | — |

### 4.2 測試數據對比

| 指標 | v3.0.1 | v3.1.0 | 進步 |
|------|--------|--------|------|
| 測試通過 | 102 + 3 skipped | **203 + 3 skipped** | **+101 (+99%)** |
| 覆蓋率 | 85% | **90%** | **+5%** |
| 模組數量 | 35 | **37** | +2 |

### 4.3 倉庫內容總覽

#### fa-report-refactor(技能包倉庫)

```
src/fa_improver/              ← 37 個 Python 模組
├── domain/                    ← 純資料模型
├── parsers/                   ← 輸入解析
├── layout/                    ← 母片保護
├── improvers/                 ← 8 種改善動作
├── templates/                 ← JSON 樣板
├── visuals/                   ← 5 種視覺元素
├── llm/                       ← LLM + redact.py(新增)
└── utils/                     ← 工具

tests/unit/                    ← 203 個測試
├── test_redact.py             ← 35 個(新增)
├── test_openai_client.py      ← 21 個(11 + 10 新增)
├── test_template_integration.py ← 21 個(新增)
├── test_cli.py                ← 8 個(新增)
├── test_template_validation.py ← 27 個(新增)
└── ...                        ← 既有測試

CHANGELOG.md / SKILL.md / README.md
references/                   ← PPT 轉換、虛擬環境、樣板指南
pyproject.toml (v3.1.0) / uv.lock
.pre-commit-config.yaml
```

#### fa-report-refactor-root(根倉庫)

```
AGENTS.md                     ← Agent 規範
docs/
├── README.md                 ← 文件索引
├── 00_executive_summary.md
├── 01_assessment.md
├── 02_refactor_plan.md
├── ...
├── PHASE2-5_TODO.md
├── TESTING.md
├── USER_GUIDE.md
└── handoff/
    ├── 2026-08-31-honest-phase-completion-check-handoff.md
    ├── 2026-08-31-v310-release-handoff.md       ← 本次完成總結
    └── 2026-08-31-v310-git-push-summary.md      ← 本檔

report/                       ← FA 報告與評估 JSON
.gitignore
```

---

## 5. 給未來成員的操作指南

### 5.1 Clone 完整專案(雙倉庫)

```bash
# Step 1: Clone 根倉庫
git clone https://github.com/kcf7012/fa-report-refactor-root.git
cd fa-report-refactor-root  # 注意:clone 後資料夾名稱

# Step 2: Clone 技能包倉庫到正確位置
git clone https://github.com/kcf7012/fa-report-refactor.git .agents/skills/fa-report-improvement
```

⚠️ **注意**:clone 後的根倉庫資料夾預設名稱是 `fa-report-refactor-root`,但 AGENTS.md 內部路徑假設是 `fa-report-refactor/`。建議改名:

```bash
mv fa-report-refactor-root fa-report-refactor
cd fa-report-refactor
ls .agents/skills/fa-report-improvement/  # 確認技能包已在
```

### 5.2 Pull 雙倉庫更新

```bash
# 更新根倉庫文件
cd /home/elan/fa-report-refactor
git pull

# 更新技能包(原始碼、測試)
cd .agents/skills/fa-report-improvement
git pull
```

### 5.3 推送新版本(假設 v3.2.0)

```bash
# === 在技能包倉庫工作 ===
cd .agents/skills/fa-report-improvement
# 1. 修改程式碼、寫測試
# 2. 跑測試確認
uv run pytest tests/
# 3. Commit(用 commit-helper 技能)
git add .
git commit -m "feat: 新功能"
# 4. 更新版本號
#    - pyproject.toml: version = "3.2.0"
#    - CHANGELOG.md: 新增 [3.2.0] 章節
#    - SKILL.md / README.md / references/*.md: 更新版本
git add pyproject.toml CHANGELOG.md SKILL.md README.md references/
git commit -m "docs: 版本號 v3.1.0 → v3.2.0"
# 5. Push + 打 tag
git push origin main
git tag -a v3.2.0 -m "v3.2.0 - ..."
git push origin v3.2.0

# === 在根倉庫工作(若 docs/ 有更新) ===
cd /home/elan/fa-report-refactor
# 1. 更新 AGENTS.md、docs/handoff/
# 2. Commit 與 push
git add AGENTS.md docs/
git commit -m "docs: ..."
git push origin main
```

---

## 6. 重要注意事項

### 6.1 雙倉庫不可合併

- ❌ **絕對不要**把技能包內容推到根倉庫 URL
- ❌ **絕對不要**把根倉庫內容推到技能包 URL
- ✅ 兩個倉庫各自的 URL 是**唯一**的正確位置

### 6.2 技能包 tag 只能打在技能包倉庫

- ✅ `v3.0.0` / `v3.0.1` / `v3.1.0` 在技能包倉庫
- ❌ 根倉庫沒有 tag(因為根倉庫主要是文件)

### 6.3 認證帳號

- 目前使用 `kcf7012`(GitHub 認證帳號)
- 倉庫擁有者也是 `kcf7012`(已驗證)
- 如更換 GitHub 帳號,需更新 remote URL 中的 username

### 6.4 Force Push 注意事項

- 兩個倉庫 URL 不同,**不需要** force push
- 只有當遠端有「不需要的舊內容」時才需 `--force-with-lease`(本次推送時遇到)
- 絕對不要用 `--force`(會覆蓋其他人的 commit)

### 6.5 母片保護(最高優先)

不論在哪個倉庫工作,**母片保護測試必須通過**:

```bash
cd /home/elan/fa-report-refactor/.agents/skills/fa-report-improvement
uv run pytest tests/unit/test_master_protection.py -v
```

❌ 不可繞過、不可跳過、不可合併失敗的 PR。

---

## 7. 統計數據

| 項目 | 數值 |
|------|------|
| v3.1.0 總 commit(技能包) | 8(含 docs commit) |
| v3.1.0 總 commit(根倉庫) | 2 |
| 新測試 | 101 個(+99%) |
| 覆蓋率提升 | +5%(85% → 90%) |
| 程式碼增量 | +~1500 行 |
| 文件增量 | +~400 行 |
| 推送 GitHub 倉庫 | 2 個獨立倉庫 |
| Tag 推送 | 1 個(v3.1.0) |

---

## 8. 參考文件

- **本機 handoff**:`docs/handoff/2026-08-31-v310-release-handoff.md`(完成內容總結)
- **誠實完成度**:`docs/handoff/2026-08-31-honest-phase-completion-check-handoff.md`(8 項優化項來源)
- **AGENTS.md**:根倉庫專案指南
- **CHANGELOG.md**:技能包版本變更記錄(在技能包倉庫)

---

✅ 本檔已寫入:`/home/elan/fa-report-refactor/docs/handoff/2026-08-31-v310-git-push-summary.md`
   包含:8 個區塊,推送過程紀錄,雙倉庫設定,未來操作指南,注意事項
