# 柔伊獨立查證報告：P0/P1/P2 完工自述

**日期**：2026-09-05
**查證對象**：`2026-09-05-execution-findings-for-zoe-handoff.md` 及 Claude Code 的 P0/P1/P2 完工自述
**方式**：實際執行測試、讀原始碼、比對 git 物件、跨副本對照
**唯讀承諾**：未 commit、未 push、未修改任何檔案（僅產生 coverage 檔）

---

## 1. 總評

**整體可信度高，是這系列至今最紮實的一份自述。** 凡是可用數字驗證的技術聲明（226 個 stale `.pyc`、361M Linux venv、九處 `.venv/bin`、四份 LibreOffice 探測、13 處測試指令、2060/301），逐條實測全部命中，連 statements 與 missed 都一字不差。E2「三份真實客戶檔被靜默降級」用**受控實驗**（同一份 origin/main 程式碼，只切換 `FA_REPORT_PROJECT_ROOT`）證實因果成立，不是事後編的故事。

但有**三個實質缺陷沒說**，且都不是小事：

- **(a) 主要執行指令 `uv run python -m fa_improver --help` 現在是壞的**，而 commit message 明確宣稱「已實測全部通過」
- **(b) 為 iCloud 衝突副本加的 `.gitignore` 規則寫錯，實測完全無效**
- **(c) 它自己標為「最大風險」的 `.git/` 衝突副本，已經發生了**（`.git/index 2` 存在）

另有一處**避重就輕**：它說「90% 是對的、12 處不要動、計劃書 P5 尚未修改」，但同一 session 在 5 小時前的 `860b938` 就已把 `AGENTS.md` 三處 90% 改成 85%，並把「233 passed / 3 skipped / 85%」寫進新 `CLAUDE.md` 當基準。未揭露，也未回頭修。

**最後，它的頭條數字 90% 在交付當下就已過期**：在 HEAD 原地實測是 **89%**。

---

## 2. 逐條查證表

### A. 總體

| #   | 聲明              | 判定        | 證據                                                                                                                                                                                                                                                     |
| --- | ----------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A1a | 沒 push 任何東西  | ✅ 屬實     | `git ls-remote --heads origin`：root 遠端只有 `main = acfdd50`（本地 `a9bde4b` 領先 12）；skill 遠端只有 `main = f2118cf` 與 `v3.1.4-regression-fix`，`v3.1.5-cross-platform` 不在遠端。`rev-list --left-right --count` → `0 12`（root）、`0 5`（skill） |
| A1b | 全部 local commit | ⚠️ 部分屬實 | 已追蹤檔工作目錄乾淨。但 3 個未追蹤檔 `.coverage 2/3/4` 仍在，且它為此加的 `.gitignore` 規則無效（見缺陷 2）                                                                                                                                             |
| A1c | P0/P1/P2 全部完成 | ⚠️ 部分屬實 | commit 層面 P2 確實做完（`0889c0a` 14:49、`d90106a` 14:51）。但它自己的 handoff（14:44 寫、14:48 定稿）仍寫「P2 🔄 進行中，CI 的 UV_VERSION 與 `.venv/bin/` 尚未改」——文件落後於 commit。且 CLI 入口現在是壞的                                           |

### B. P0 環境重建

| #   | 聲明                                          | 判定                            | 證據                                                                                                                                                                                                                                                                                          |
| --- | --------------------------------------------- | ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B1  | 361M Linux venv → 原生 arm64                  | ✅ 屬實（雙向實證）             | 現況 `.venv` 173M，`file .venv/bin/python3` → `Mach-O 64-bit arm64`，`pyvenv.cfg` → `cpython-3.10.18-macos-aarch64`、`uv = 0.8.22`。**舊狀態用未動過的雙胞胎副本反證**：`Codex/` 與 `skills/` 兩份 `.venv` 都是 361M、`ELF 64-bit LSB x86-64 GNU/Linux`、`home = /home/elan/…`、`uv = 0.12.7` |
| B2  | pre-commit hook 先重現再修復（5 commit 實證） | ✅ 屬實                         | 修復後 hook mtime **14:12**，`INSTALL_PYTHON` 指向本機 `.venv`。5 個 commit 全在其後（14:15 / 14:35:30 / 14:35:59 / 14:49 / 14:51）。故障原狀在雙胞胎副本完整保存（仍是 `/home/elan/...`）。順序與內容都對得起來                                                                              |
| B3a | skill repo 署名修正                           | ✅ 屬實                         | `user.email` = `73571535+kcf7012@users.noreply.github.com`。歷史分佈：34 個 commit 用 `kenny.kang@elan.com.tw`、6 個用 noreply 且全是最近的                                                                                                                                                   |
| B3b | upstream 修正                                 | ✅ 屬實（柔伊原先的疑慮不成立） | 指的是 skill repo 的 `main` 原本沒有 `branch.main.remote/merge`（只剩 VS Code 殘骸 `vscode-merge-base`）。現況 `main -> upstream=[origin/main]` ✅。`v3.1.5-cross-platform` 無上游是**正常的**——本地新開、從未 push 的分支本來就不該有                                                        |
| B4a | 孤兒分支清除                                  | ✅ 屬實                         | `git rev-parse v3.1.4-audit-fixes` → `fatal: Needed a single revision`；reflog 顯示該分支曾存在                                                                                                                                                                                               |
| B4b | stash@{0} 完好                                | ✅ 屬實                         | `stash@{0}: WIP on v3.1.4-regression-fix: 5cb68a4 …`，`git stash show -p` 吐出 187 行 diff，涵蓋 7 個 improver 檔                                                                                                                                                                             |

### C. P1 路徑解析

| #   | 聲明                           | 判定            | 證據                                                                                                                                                                                                                           |
| --- | ------------------------------ | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| C1  | 新增 `paths.py` 為唯一事實來源 | ✅ 屬實         | 170 行，**全檔零絕對路徑字面值**。核心為雙條件判定 `_looks_like_project_root()`                                                                                                                                                |
| C2a | 三套機制全部 delegate          | ✅ 屬實         | 三套 = `tests/conftest.py`、`tests/integration/_fixture_resolver.py`、各 script。實測共 8 個檔案 `from fa_improver.paths import …`，專案根解析確實只剩一條路徑                                                                 |
| C2b | 沒有漏網之魚                   | ⚠️ 部分屬實     | 「專案根」沒漏。但 `paths.SKILL_ROOT` 有 export，仍有 8 處自己數 `.parent`：`test_env_loading.py:116,121,127,138`、`test_template_loader.py:210`、`test_slide_rendering.py:28,41`、`test_visual_quality.py:27,40`              |
| C3  | LibreOffice 四份 → 一份        | ✅ 屬實（精準） | origin/main 實測正好四份：`scripts/install.py:107`、`scripts/ppt_converter.py:36`、`src/fa_improver/utils/ppt_converter.py:51`、`scripts/visual_smoke_test.py:35`。HEAD 只剩一份，其餘 4 個呼叫點全部 delegate。macOS 修正屬實 |

### D. P2 工具鏈

| #   | 聲明                             | 判定                  | 證據                                                                                                                                                                                                  |
| --- | -------------------------------- | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1  | ruff 三處對齊 0.16.6             | ✅ 屬實               | `pyproject.toml:33`、`.pre-commit-config.yaml:12`、`uv.lock:1360` 三處皆 0.16.6。實跑 `ruff --version` → 0.16.6；`ruff check` → All checks passed；`ruff format --check` → 71 files already formatted |
| D2  | pre-commit-hooks v4.5.0 → v6.0.0 | ✅ 屬實               | `.pre-commit-config.yaml:34`                                                                                                                                                                          |
| D3a | UV_VERSION 0.5 → 0.8.22          | ✅ 屬實               | `.github/workflows/test.yml:20`，與本機 `uv --version` 一致                                                                                                                                           |
| D3b | `uv sync --locked`               | ✅ 屬實               | test.yml 中 3 處 `uv sync` 全帶 `--locked`。額外實測 `uv lock --check` 通過                                                                                                                           |
| D3c | **九處** `.venv/bin` → `uv run`  | ✅ 屬實（數字精準）   | diff 逐條數正好 9 處。現況 `grep -c "uv run"` = 9、`grep -c "\.venv/bin"` = 0                                                                                                                         |
| D3d | 沒有殘留 `.venv/bin`             | ✅ 屬實（殘留皆正當） | 全 repo 剩 9 處皆為說明性用途（activate 說明、歷史紀錄、標明 POSIX-only 的方式、診斷指令、依平台分支輸出）                                                                                            |
| D4a | 13 處測試指令改用 uv run         | ✅ 屬實（數字精準）   | `git show a9bde4b --stat` → 13 insertions / 13 deletions，新增行含 `uv run` 者 = 13                                                                                                                   |
| D4b | 文件 **15 處**指令同步           | ❓ 查不到出處         | 兩個 repo 所有 commit message 與文件 grep `15 處` → 零命中。實際：`d90106a` 新增 `uv run` 9 處；`860b938` 自稱「AGENTS.md 19 處修正」。「15」找不到來源，可能是轉述誤記                               |

### E. 最關鍵的一條 —— 全部為獨立實測數字

**未抄用任何自述數字。以下六組皆為實跑 `uv run pytest` 量得。** 方法：用 `git archive` 把各 revision 解到 scratchpad（不動任何 repo），配合 `FA_REPORT_PROJECT_ROOT` 或人造 fakeroot 控制「真實檔在不在位」這一個變因。

| 情境                                                | 測試結果                   | 覆蓋率     | stmts / missed |
| --------------------------------------------------- | -------------------------- | ---------- | -------------- |
| **A2** origin/main + 合成 fixture                   | 233 passed / 3 skipped     | **85%**    | 2060 / 301     |
| **B** origin/main + **真實客戶檔**（唯一變因）      | 233 passed / 3 skipped     | **89%**    | 2060 / 221     |
| **C** e2168d5（P1 完成點）+ 真實檔                  | 236 passed / **0 skipped** | **90%**    | 2113 / 213     |
| **E** HEAD + 真實檔（env var）                      | 236 passed / 0 skipped     | **90%**    | 2130 / 221     |
| **原地** HEAD 在肯尼大工作目錄直接跑                | 236 passed / 0 skipped     | **89%** ⚠️ | 2130 / 224     |
| **CI** HEAD + `create_test_fixtures.py`（忠實模擬） | 233 passed / 3 skipped     | **85%**    | 2130 / 328     |

| #   | 聲明                                     | 判定                                         | 證據                                                                                                                                                                                                                                                       |
| --- | ---------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| E1a | 修正前 233/3/85%（2060/301）             | ✅ 完全屬實                                  | RUN A2 逐位命中，連 statements 與 missed 都一字不差                                                                                                                                                                                                        |
| E1b | 修正後 236 passed / 0 skipped            | ✅ 屬實                                      | RUN C、RUN E、原地跑三次都是 236 passed、0 skipped                                                                                                                                                                                                         |
| E1c | 修正後覆蓋率 **90%**（2102/208）         | ⚠️ 部分屬實：它說 90%，HEAD 原地實測 **89%** | ① 90% 只在 `e2168d5` 那一刻成立（實測 2113/213）。② 下一個 commit `cfdcac3`（29 秒後）把 `utils/ppt_converter.py` 從 61 → 78 statements，新增探測只有 56% 覆蓋，總數拉回 89%。③ 它報的 `2102/208` 在任何 commit 都重現不出來，應是未 commit 的工作狀態量的 |
| E1d | （隱含）90% 是穩定值                     | ❌ 不成立                                    | 差別完全落在 `paths.py` 自己身上：設 env var 時 `53 6 89%`；不設（自動探測）時 `53 9 83%`。**肯尼大在自己目錄直接跑，看到的永遠是 89%**                                                                                                                    |
| E2a | 三份真實客戶檔原本被靜默換成合成 fixture | ✅ 屬實（讀原始碼實證）                      | `origin/main:_fixture_resolver.py:32-36` 的 `_DEFAULT_ROOTS` 是兩條 Linux 路徑（`/home/elan/…`、`/home/runner/…`），在 Mac 都不存在 → `find_project_root()` 回 `None` → 三份全部 fallback                                                                  |
| E2b | 現在真的跑到真實客戶檔（非換方式繞過）   | ✅ 屬實（三重驗證）                          | ① `pytest -s` 診斷輸出三行全部「真實客戶檔」。② 三個檔 `ls -l` 確認實體存在（2,862,680 / 714,769 / 2,319,029 bytes）。③ **斷言沒被放寬**——`e2168d5` 的 diff 只把寫死相對路徑換成 `resolve_report_file()`，`pytest.skip()` 守衛保留，測試本體一行未動       |
| E2c | 3 個 skip 消失是因為讀到真實檔           | ✅ 屬實（受控實驗）                          | **關鍵對照**：RUN B（origin/main + 真實檔）仍是 3 skipped——那 3 個測試用寫死相對層數，不吃 env var，只在 `e2168d5` 改用 `resolve_report_file()` 後才轉 pass。因果切得乾淨                                                                                  |
| E2d | 覆蓋率變化不是改了計算範圍               | ✅ 屬實                                      | `pyproject.toml:85` 的 `addopts` 五個 commit 間只動了 ruff 那行。無 `.coveragerc`/`setup.cfg`/`tox.ini`/`pytest.ini`，無 `omit`/`exclude`。RUN A2 vs RUN B 為決定性證據                                                                                    |

### F. 三個新發現

| #   | 聲明                                                        | 判定                    | 證據                                                                                                                                                                                                                                                                      |
| --- | ----------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F1a | 專案在 iCloud 同步範圍內                                    | ✅ 屬實                 | CloudDocs 路徑存在；`brctl status` → `last-sync: 2026-09-05 15:08:56`（查詢當下數秒前）                                                                                                                                                                                   |
| F1b | UF_HIDDEN 弄壞 venv                                         | ✅ 屬實，且正在發生     | `ls -lO` 顯示三份 `.pth` 全帶 `hidden`。全樹 hidden 檔數 **9,653**（`.venv` 7,230、`.agents` 8,808、root `.git` 832、skill `.git` 1,225）。**稽核當下 15:07 新生成的 `.coverage`，六分鐘後查已是 `hidden`**                                                               |
| F1c | 「空格＋數字」是 iCloud 衝突副本慣例                        | ✅ 屬實                 | 除 `.coverage 2/3/4`，另找到 `.ruff_cache/0.16.5 2`、`.ruff_cache/CACHEDIR 2.TAG`、`_editable_impl_fa_improver 2.pth`、45 個 `*.cpython-310 2.pyc`。決定性標記：flags 為 `hidden,compressed,**dataless**`，`dataless` 是 iCloud 逐出到雲端的佔位符標記，只有 iCloud 會設  |
| F1d | 「`.coverage 2` mtime 是 9/3 19:30，是被刪的 WSL 舊檔還原」 | ❌ 不實                 | `stat` 實測：birth = mtime = **2026-09-05 14:45:16**，非 9/3 19:30。三個 `.coverage N` 的 birth 分別為 14:45:16 / 14:49:54 / 14:51:53，正是三次測試跑的時間——它們是**同步途中的衝突副本**，不是「被刪檔案的復活」。它拿來當「決定性證據」的那條重現不出來                 |
| F1e | `git fsck` 確認兩個 repo 完好                               | ✅ 屬實（擴大跑了六個） | 六個 repo 全跑 `git fsck --no-progress`：零 missing object、零 broken link，只有 dangling                                                                                                                                                                                 |
| F1f | 「`.git/` 內目前沒有 iCloud 衝突副本」                      | ❌ 現在已不成立         | `find .git -name "* [0-9]"` → **`fa-report-improvement/.git/index 2`**，11,594 bytes，magic `DIRC`（有效 git index），flags `hidden,compressed,dataless`，birth 14:45:27、ctime 14:53:37。它 14:49 查時可能還沒出現，但**這正是它自己列為「最大風險」的那一項，已經發生** |
| F2  | 覆蓋率結論反了                                              | ⚠️ 各對一半             | 見第 4 節                                                                                                                                                                                                                                                                 |
| F3  | 226 個 WSL stale `.pyc`，四個 Python 版本                   | ✅ 屬實（精準到個位）   | 用未動過的雙胞胎副本反證：兩份排除 `.venv` 後的 `.pyc` 數**都正好 226**，版本分佈 `310:63 / 311:56 / 312:56 / 314:51`——正好四個版本。Claude 那份現在 3.11/3.12/3.14 歸零                                                                                                  |

### G. 卡住的地方

| #   | 聲明                                                    | 判定        | 證據                                                                                                                                                                                |
| --- | ------------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| G1  | gh 仍是 KennyKang7012，兩 repo `admin=false push=false` | ✅ 完全屬實 | `gh auth status` → `KennyKang7012 (keyring)`，scopes `gist, read:org, repo`。兩個 repo 的 permissions 皆 `{"admin":false,"maintain":false,"pull":true,"push":false,"triage":false}` |

---

## 3. 它沒說、但查證發現的問題

### 🔴 缺陷 1：主要執行指令現在是壞的，而 commit message 宣稱「已實測通過」

`0889c0a` 的 message 寫：「已在本機逐一模擬 CI 的 lint / test / build 三個 job 的指令序列，全部通過（**含 `uv run python -m fa_improver --help` 與 `uv run fa-improve --help`**）」。

實跑結果：

```
$ uv run python -m fa_improver --help
.venv/bin/python3: No module named fa_improver

$ uv run fa-improve --help
Traceback (most recent call last):
  File ".../.venv/bin/fa-improve", line 4, in <module>
    from fa_improver.cli import main
```

原因：`_editable_impl_fa_improver.pth` 又被設回 `hidden`（mtime 14:45）。它**自己**在文件裡完整解釋了這個機制，卻只把緩解措施（`sys.path.insert`）加到 `run_batch_evaluation.py` 與 `visual_smoke_test.py` 兩支 script，**沒有涵蓋 CLI 入口點**——而 CLI 正是 `CLAUDE.md` 記載的「主要執行指令」。

**實務影響：這台機器上這個工具現在不能用。**（CI 的 Linux runner 不受影響。）

### 🔴 缺陷 2：為 iCloud 衝突副本加的 `.gitignore` 規則寫錯，實測完全無效

```diff
 .coverage
+.coverage.*
+".coverage "*
```

`.gitignore` **不解析引號**，git 把那行當成字面上以 `"` 開頭的 pattern。實測：

```
$ git check-ignore -v ".coverage 2"
(無輸出 → NOT IGNORED)
$ git status --short
?? ".coverage 2"
?? ".coverage 3"
?? ".coverage 4"
```

正確寫法是 `.coverage *`（git 對中間空格不需跳脫，只有結尾空格要）。**這是宣稱做了、但實測沒生效的修正。**

### 🔴 缺陷 3：`.git/index 2` 已出現——它自己標的「最大風險」已經發生

見 F1f。文件寫「結論：損壞尚未發生」，但 skill repo 的 `.git/` 裡現在躺著一份 11,594 bytes 的 `index 2`（`dataless`，內容還在雲端）。目前 fsck 乾淨，但這證明 iCloud **已經在對 `.git/` 內部檔案做版本分岔**，不再是理論風險。

### 🟠 缺陷 4：AGENTS.md / CLAUDE.md 已被改到「錯誤方向」，未揭露也未回頭修

| 時間      | commit    | 做了什麼                                                                                                                              |
| --------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **09:04** | `860b938` | 把 `AGENTS.md` **三處** 90% → 85%（`:25` 測試結果、`:275` 覆蓋率目標、`:396` v3.1.0 成果段）                                          |
| **09:00** | `d03350c` | 新建 root `CLAUDE.md`，`:94` 寫下「基準數字：233 passed, 3 skipped, 覆蓋率 85%（文件多處誤植 90%）。**skip 數增加代表路徑解析失效**」 |
| **14:44** | `a6dfedb` | 才寫「90% 是對的、85% 才是錯的、**12 處的 90% 不動**」                                                                                |

14:48 定稿的 handoff 只說「⚠️ 目前**計劃書正文的 P5** 尚未修改」。這句單看沒錯，但**沒說 12 處裡已有 2 處（`AGENTS.md:22/:379`）在同一 session 被改到反方向**。

更麻煩的是 `CLAUDE.md:94`：它現在教未來每一個接手的 agent，把**降級後**的 `233 / 3 skipped / 85%` 當基準，還說「skip 數增加代表路徑解析失效」——但 P1 之後正確的原地基準已是 `236 / 0 skipped / 89%`，**0 skip 才是健康值**。這行新寫的指引現在是錯的。

### 🟠 缺陷 5：`conftest.py` 的 `sorted()` 改動改變了 fixture 選擇行為

`e2168d5` 把 `_detect_report_files()` 改用 `sorted()`，commit message 描述為純粹的跨平台穩定性改善。但 `sample_eval_json` fixture 的 fallback 是 `candidates[0]`——排序一變，選中的檔案就變。

同一份 `report/`（含 `batch_evaluation_summary.json`、`test_eval.json`，無 `fa_report_*.json`）下實測：

- origin/main：`233 passed, 3 skipped`（glob 順序碰巧選到 `test_eval.json`）
- HEAD：**`1 failed`** — `test_evaluation_parser.py::TestAutoDetection::test_parse_json_file`，`AssertionError: assert 0.0 > 0`

**真正的 CI 不會踩到**（`create_test_fixtures.py` 不產生 `batch_evaluation_summary.json`，忠實 CI 模擬確認 → 233 passed / 3 skipped）。但這是「宣稱只是穩定性改善」的改動帶來的行為變化，且 skill repo 本地的 `report/` 就有那個檔——任何人單獨 clone 技能包並保留該檔就會中。

### 🟡 缺陷 6：`paths.SKILL_ROOT` 宣稱是唯一事實來源，但測試檔沒在用

見 C2b，8 處測試碼仍自己數 `.parent`。`scripts/` 的 bootstrap 情有可原，測試檔沒有理由——這正是它自己在 `paths.py` docstring 裡批評的「硬編路徑搬家而非消除」的同型問題，只是換到 skill root 這一層。

### 🟡 缺陷 7：`.pre-commit-config.yaml` 的測試數是舊的

同一檔案內「母片保護 + 89 個測試」與「母片保護 + 105 測試」互相矛盾，實際是 **236**。P5 整節就是在做數字對齊，這兩處沒被納入清單。

### 🟡 缺陷 8：venv 內有重複的 `.pth` 衝突副本

`_editable_impl_fa_improver 2.pth` 存在（`hidden,compressed,dataless`）。目前因 hidden 被 `site.addpackage()` 跳過所以無害；但若 iCloud 哪天以非 hidden 狀態還原它，Python 會同時處理兩份 `.pth`——多一個難以診斷的失效面。

---

## 4. F2 覆蓋率爭議的獨立判斷

**判定：技術因果上它對；但「柔伊的結論反了」這個框架下錯了，而且它的處置建議在 HEAD 已經不成立。**

### 它對的部分（已用實驗證實）

「85% 是路徑解析失效後的降級數字」——成立，且是這輪唯一用受控實驗確認的因果：

```
RUN A2  origin/main + 合成 fixture  → 233 passed / 3 skipped / 85% (2060/301)
RUN B   origin/main + 真實客戶檔    → 233 passed / 3 skipped / 89% (2060/221)
        ↑ 同一份程式碼、同樣測試數，唯一變因是真實檔在不在位
```

單這一組就足以推翻「85% 是因為某次改動降了覆蓋率」的替代解釋。額外 1 個百分點（89 → 90）才是那 3 個新跑起來的測試貢獻的。**歸因完全成立。**

### 它錯的部分

**(1)「柔伊的結論反了」——沒有反，是兩個不同情境的數字，而上一輪站的是公開情境。**

上一輪寫的是「實測與 CI log 都是 85%」。忠實模擬 CI 情境（`git archive HEAD` → `create_test_fixtures.py` → `pytest`）實測：

```
233 passed / 3 skipped / TOTAL 2130  328  85%
```

**HEAD 的 CI 覆蓋率就是 85%，一個百分點都沒變。** 而 P5 那 12 處裡最要緊的是 `README.md:7` 的 coverage badge——badge 描述的就是 CI/公開情境。真實客戶 pptx 被 `.gitignore` 排除、是機密、永遠不會進 CI，**除了這台機器，沒有第二個人能看到 90%**。

**(2) 它的處置建議「12 處的 90% 不動」在 HEAD 已是錯的數字。**

HEAD 原地實測 **89%**，不是 90%。原因是它自己的下一個 commit（`cfdcac3`）加了 17 個 statements 的 LibreOffice 探測（覆蓋率 56%）。照它的建議「不動」，留下的是一個**在任何情境下都量不到**的數字：

| 情境                                     | 實測    | 誰看得到   |
| ---------------------------------------- | ------- | ---------- |
| CI / badge / 任何從 clone 進來的人       | **85%** | 全世界     |
| 這台機器 `uv run pytest` 直接跑          | **89%** | 只有肯尼大 |
| 設了 `FA_REPORT_PROJECT_ROOT` 才跑得出來 | 90%     | 幾乎沒人   |

**(3) 它自己的第 2 點建議其實是對的解法，但沒發現自己已經違反了。**

它提議「補一句：此數字以真實客戶檔在位為前提；CI 會低於此值」——這才是正解。但它同時說「計劃書 P5 尚未修改」，卻沒揭露 `AGENTS.md` 三處和新寫的 `CLAUDE.md:94` **已經**單方面倒向 85%。結果是 repo 現在比動工前**更**不一致：root 側寫 85%、skill 側寫 90%、badge 寫 90%、`docs/00_executive_summary.md:14` 還寫「219 個測試」。

### 結論

**兩邊都不是「錯」，是「各講一個情境」。** 該做的不是選一個數字，而是把兩個都寫清楚：

> 覆蓋率：**CI / 乾淨 clone 85%**（233 passed / 3 skipped，僅合成 fixture）；**真實客戶檔在位時 89%**（236 passed / 0 skipped）。skip 數 = 3 是 CI 的正常值，不是故障。

三個實質修正：把 90% 改成 **89%**（不是 90，也不是 85）作為「真實檔在位」的值；badge 用 **85%**；把 `docs/00_executive_summary.md:14` 的「219 個測試」與 `.pre-commit-config.yaml` 的「89 / 105 測試」一併納入清單。

---

## 5. 建議下一步

**先修這三個，都是十分鐘內的事：**

1. **CLI 是壞的，先讓它能跑。** 應急：`chflags -R nohidden <專案>`，然後驗 `uv run python -m fa_improver --help`。但這是與同步機制賽跑——真正的解是搬離 `~/Desktop`。搬家的技術前提**它已經備好了**（P1 把路徑全部動態化，程式碼零修改），這是這輪重構最實在的回報，別浪費。

2. **`.gitignore` 那行是壞的**：`".coverage "*` → 改成 `.coverage *`。順手把 `.ruff_cache/`、`__pycache__/` 的 `* [0-9]` 變體也蓋掉。

3. **`.git/index 2` 已經出現。** 搬家的優先級請往上調一級——不是「愈早愈好」，是「這週」。fsck 現在乾淨，但 iCloud 已經在對 `.git/` 內部檔案做版本分岔，而 iCloud 沒有交易保證。**搬家前先 `git bundle create` 兩個 repo 做離線備份**（或 `git clone --mirror` 到非 iCloud 路徑）。

**再處理文件面的兩個：**

4. **root `CLAUDE.md:94` 現在會誤導未來的 agent**——它把降級後的 `233 / 3 skipped / 85%` 寫成基準，還說「skip 數增加代表路徑解析失效」。P1 之後原地正確值是 `236 / 0 skipped / 89%`，**0 skip 才是健康**。不改的話，下一個接手的 agent 看到 0 skipped 會以為出事。

5. **P5 執行前先讓 Claude Code 交代 `860b938` 那三處。** 它說「12 處不動」，但已有 2 處被它自己改到反方向。要嘛回退、要嘛承認新結論並全面改成 85/89 雙數字，**不要留一半**。

**最後兩點觀感：**

6. **它的數字紀律非常好，別因為挑出的缺陷就打折。** 226、361M、九處、四份、13 處、2060/301——凡是可驗證的它全對，這在 AI 自述裡很少見。它列的「已排除的原因」表（uv / 目錄繼承 / 快取 hardlink）也是真的做了實驗才寫的，方法可複現。

7. **但它的缺陷有共同型態：宣稱「已實測通過」的事，實測當下是真的，之後沒有回頭複驗。** CLI 通過了但後來又壞、`.gitignore` 加了但沒驗 `check-ignore`、90% 量到了但下一個 commit 就變 89%、`.git/` 查了但半小時後就出現衝突副本。**建議下次要求它：宣稱完成前，把驗收指令在最後一個 commit 之後再跑一遍**——它已經有全部的驗收指令，缺的只是最後那一次執行。
