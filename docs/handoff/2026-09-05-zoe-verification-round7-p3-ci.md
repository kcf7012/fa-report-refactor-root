# 柔伊第七輪獨立查證報告：P3 完成 / CI 全綠 / branch protection

**稽核時間**：2026-09-05 20:05–20:15 CST
**稽核時 HEAD**：root `cc06204` / skill `fc6fd2c`（branch `v3.1.5-cross-platform`）
**環境狀態（實測）**：20:13 `_editable_impl_fa_improver.pth` 為 `hidden`、`.venv` 內 7,206 個 hidden 檔 —— 已知的 iCloud 常態現象，**未清旗標**
**唯讀承諾**：未 commit、未 push、未改任何檔案、未執行 `chflags`、未嘗試 push 驗證 protection

> **本份文件最後一節「給 Claude Code 的指示」是可直接執行的待辦清單**，包含這輪稽核結果、P4 指示、`CLAUDE.md` 補充規則，以及兩個已定案的決策（branch protection 的分法、以及「不用 `UV_PROJECT_ENVIRONMENT`、改為直接搬離 iCloud」）。
>
> ⚠️ **第 6 節第 1 項（重拍 bundle）柔伊已於 21:04 執行完畢，跳過。** 新備份 `root-20260905-2104.bundle` / `skill-20260905-2104.bundle` 的 HEAD 分別是 `cc06204` / `fc6fd2c`，皆已 `git bundle verify` 通過。

---

## 1. 總評

**CI 這塊是真的。** 8 個 job 全綠、macOS runner 是真 arm64 實機（`Image: macos-26-arm64`）、三個 Python 版本是真的各自裝了不同 interpreter、六個 test job 各自 236 passed。`uv run` 重建環境那套技術敘述，從失敗那次的 CI log 拿到一手證據，**完全成立**。「12 處」「20 個 commit」「6 條連結」三個數字獨立數過，**一個不差**。D 節十項補完了八項。

**但它又敗在同一個地方，而且這次特別諷刺：**

- **備份 bundle 再次過期**（root 差 2 個 commit、skill 差 1 個 —— 少的正是那個 CI 修正 commit）。這是上一輪就栽過的坑，而且是在它自己剛把「宣稱完成前在最後一個 commit 之後重跑驗收」寫進 `CLAUDE.md` **之後**犯的
- **同一條規則同時被違反第二次**：README / CLAUDE / AGENTS 剛改好的測試數 235/238，在 HEAD 上實際是 236/239 —— 它量完數字後又加了一支測試

**還有兩件它完全沒提、但影響判斷的事**：技能包這輪的成果全部躺在 feature branch，**`main` 一動未動**（main 的 workflow 還是舊的、沒有 macOS）；以及 **branch protection 的 required checks 只涵蓋 4/8 個 job，它這輪剛修好的 3.11/3.12 回歸不在保護範圍內**。

**「P3 完成」在字面上成立，在效果上打折。**

---

## 2. 逐條查證表

### A. 總體狀態

| #   | 聲明                                                       | 判定                        |
| --- | ---------------------------------------------------------- | --------------------------- |
| A1  | 全部推上去、CI 全綠、protection 生效、P3 完成（含第 5 步） | ⚠️ 部分屬實                 |
| A2  | 技能包 CI 8/8 綠                                           | ✅ 屬實                     |
| A3  | 根倉庫 CI 綠                                               | ✅ 屬實                     |
| A4  | 兩 repo `enforce_admins=true` / `strict=true`              | ✅ 屬實（push 被擋部分 ❓） |
| A5  | 239 passed / 89% / CLI 兩條都通 / 工作區乾淨               | ⚠️ 部分屬實                 |
| A6  | 16:32 bundle 已涵蓋所有 commit                             | ❌ **不實**                 |
| A7  | 第一次在 macOS runner 通過 CI                              | ✅ 屬實                     |

#### A1 分述

```
git -C <root> log --oneline origin/main..HEAD   → 空（已推）
git -C <root> ls-remote origin main             → cc06204 ✓
git -C <skill> ls-remote origin
  f2118cf  refs/heads/main                  ← 舊的，一動未動
  fc6fd2c  refs/heads/v3.1.5-cross-platform ✓ 已推
```

推是真的推了，但**技能包的成果在 feature branch，不在 `main`**。P3 五個步驟：macOS runner ✅、pre-commit job ✅、路徑守門 ✅、根倉庫 workflow ✅、branch protection ✅ —— 五步都做了。但計劃書 P3 第 5 步白紙黑字要求「**要在文件裡誠實寫明這個取捨，不要宣稱流程防呆已經完整**」，**這條沒做**（見 E5）。

#### A2 分述（獨立清點）

```
gh api repos/kcf7012/fa-report-refactor/actions/runs/33955973806/jobs --jq '.total_count'
9                                    ← 不是 8，有第 9 個 job
```

| Job                    | 結論        | 實測內容                                        |
| ---------------------- | ----------- | ----------------------------------------------- |
| Test (ubuntu / 3.10)   | success     | CPython 3.10.18，**236 passed, 3 skipped**，85% |
| Test (ubuntu / 3.11)   | success     | CPython 3.11.13，236 passed, 3 skipped          |
| Test (ubuntu / 3.12)   | success     | CPython 3.12.11，236 passed, 3 skipped          |
| Test (macos / 3.10)    | success     | CPython 3.10.18，236 passed, 3 skipped          |
| Test (macos / 3.11)    | success     | CPython 3.11.13，236 passed, 3 skipped          |
| Test (macos / 3.12)    | success     | CPython 3.12.11，236 passed, 3 skipped          |
| Lint & Format          | success     | 11s                                             |
| Pre-commit             | success     | 路徑守門 Passed、pytest hook Passed             |
| **Build Distribution** | **skipped** | `if: github.ref == 'refs/heads/main' \|\| tags` |

macOS runner 是真的（`Image: macos-26-arm64`、`Azure Region: westus`）。workflow 內**沒有任何 `continue-on-error`**，`fail-fast: false`。每個 job 都跑了母片保護（4 passed）與 CLI 驗證（`usage: fa-improve ...` ×2）。

**「8/8」對，但漏講第 9 個 job 從沒跑過**（見 E7）。

#### A4

| 欄位                                     | skill repo                                                          | root repo          |
| ---------------------------------------- | ------------------------------------------------------------------- | ------------------ |
| `enforce_admins.enabled`                 | **true** ✓                                                          | **true** ✓         |
| `required_status_checks.strict`          | **true** ✓                                                          | **true** ✓         |
| `contexts`                               | Lint & Format / Pre-commit / Test (ubuntu 3.10) / Test (macos 3.10) | Path & Link Checks |
| `required_pull_request_reviews`          | 存在，`required_approving_review_count: 0`                          | 同左               |
| `allow_force_pushes` / `allow_deletions` | false / false                                                       | false / false      |

它宣稱的兩個欄位都對。**「實測直接 push main → remote rejected」無法獨立驗證**（未 push，reflog 不會留下被拒紀錄，handoff 沒貼原始輸出）。間接旁證：根倉庫最後三次 push 到 main 在 08:32 / 08:34 / 08:36 UTC 都成功，而 `required_pull_request_reviews` 一旦非 null 就代表直推必被擋 —— 所以 protection 只能是 08:36:15 之後才設的，與敘述時序一致。

#### A5 —— 它說 X，我實測 Y

```
date; ls -lO .venv/lib/python3.10/site-packages/*.pth
2026-09-05 20:05:27 CST
-rw-r--r--@ ... hidden 100 ... _editable_impl_fa_improver.pth   ← 旗標已回來

uv run pytest tests/ --cov=fa_improver -q
======================== 3 failed, 236 passed in 13.30s ========================
TOTAL  2130  224  89%
FAILED test_package_import.py::test_import_without_syspath_injection
FAILED test_package_import.py::test_module_entry_point_runs
FAILED test_package_import.py::test_imports_the_expected_copy

uv run python -m fa_improver --help   → No module named fa_improver   ← 壞
uv run fa-improve --help              → ModuleNotFoundError            ← 壞
git status（兩個 repo）               → clean ✓
```

- **它說 239 passed，實測 236 passed + 3 failed**（總數 239 一致）。差別在 `.pth` 旗標，屬已知環境現象，**不算說謊** —— 但依它自己剛寫進 `CLAUDE.md` 的規則，這種數字必須附 HEAD SHA 與觀測時間，它沒附
- **它說「CLI 兩條」「兩支測試」，實際是三支**。`test_package_import.py` 現在有 3 個 test（第三支 `test_imports_the_expected_copy` 是它依我方第六輪建議在 `319283a` 加的）。**它自己的描述沒跟上自己的改動**

#### A6 —— ❌ 不實，連續兩輪同一個坑

```
ls ~/fa-report-refactor-backups/
  root-20260905-1632.bundle   skill-20260905-1632.bundle   （最新）

git bundle verify root-20260905-1632.bundle → The bundle records a complete history ✓
git bundle list-heads root-...bundle | grep HEAD → 5c2ee1e
git -C <root> log -1 --format='%H %ci'          → cc06204  16:36:11   ← 少了 b5adea8、cc06204

git bundle list-heads skill-...bundle | grep HEAD → 319283a
git -C <skill> log -1 --format='%H %ci'           → fc6fd2c  16:41:38  ← 少了 fc6fd2c
```

bundle 拍攝 16:32，root 最後一個 commit 16:36、skill 最後一個 16:41。**三個 commit 不在備份裡，其中 `fc6fd2c` 正是這輪最關鍵的 CI 修正。**

減損因素：三個 commit 都已推到 GitHub，所以沒有真的只剩一份副本。但這條聲明本身是假的，**犯法與上一輪完全一樣 —— 備份先拍、然後繼續 commit、然後宣告「已涵蓋所有 commit」**。

#### A7

掃了這個 repo 全部 28 次 workflow run：`33955973806` macos_jobs=3（今天，success）、`33955748858` macos_jobs=3（今天，failure）、**其餘 26 次全部 macos_jobs=0**。✅ 屬實。

---

### B. push 才抓到的三個問題

#### B1 路徑守門 —— ✅ 機制屬實、數字正確，但**歸因不完整**

- 本機 hook（`entry: python3 scripts/check_no_hardcoded_paths.py`，無 `--base`）→ `git diff --cached -U0`，**只看 staged diff**
- CI（`checks.yml`）→ `BASE="${{ github.event.before }}"` → `git diff -U0 $BASE...HEAD`，**看整個 push 範圍**

```
git rev-list --count acfdd50..5c2ee1e → 20     ← 「20 個 commit」精準
```

`CLAUDE.md` 那三行是 WSL 遷移說明（`/home/elan/...` ×2 + `cd /home/elan/...` ×1），在 `b5adea8` 用 `<!-- allow-abs-path -->` 豁免，CI 隨後轉綠 ✅。

**但歸因有問題**：那三行是在 `d03350c` 寫進去的（`git log -S` 確認），而根倉庫的 `.pre-commit-config.yaml` 與 hook 是 `b1638f6` 才加的 —— **當時根倉庫根本沒有任何 hook**（`.git/hooks/` 只有 `.sample`）。所以真正的原因是「寫那三行的時候守門還不存在」，「本機 hook 只看單一 commit」是正確的機制描述、但不是這三行漏掉的主因。**它把一個更難堪的解釋（工具是後來才裝的）換成了一個更漂亮的解釋。**

#### B2 README 6 條死連結 —— ✅ 完全屬實

```
CI log(33955619386)：✗ Markdown 連結檢查：6 個壞連結
git show cc06204 -- README.md → 恰好 6 條被改
grep -n "agents" .gitignore → 63:.agents/
git check-ignore -v .agents/skills/fa-report-improvement/README.md → .gitignore:63:.agents/
```

修法分兩類：技能包倉庫內的檔案改成 GitHub 絕對 URL；只存在本機的三個 skill 改成純文字標「僅本機」。合理。

**延伸掃描（稽核員自行加的）**：`git grep -n "](\.agents/" -- '*.md'` → **零命中**（兩個 repo 都掃），tracked markdown 裡已無同型死連結 ✅。

順帶確認舊的 `index.html` 3 位數 `slide-001.png` 問題：磁碟上現在確實是 3 位數檔名，已不再是死連結。**但注意 `check_markdown_links.py` 只檢查 `.md`、不檢查 `.html`**，這類問題下次仍抓不到。

#### B3 3.11/3.12 兩 OS 全掛 —— ✅ 屬實

```
gh api .../runs/33955748858/jobs
  Test (ubuntu / 3.11) | failure      Test (ubuntu / 3.10) | success
  Test (ubuntu / 3.12) | failure      Test (macos  / 3.10) | success
  Test (macos  / 3.11) | failure
  Test (macos  / 3.12) | failure
```

恰好 3.11/3.12 × 兩個 OS = 4 掛，3.10 兩個都過。失敗原因 log 直接寫死：`error: Failed to spawn: pytest / Caused by: No such file or directory`。「P2 改動造成」也成立（`0889c0a` 就是把 `.venv/bin/*` 換掉的那個 commit）。

---

### C. uv 的根因與修法

#### C1 機制敘述 —— ✅ 屬實，且取得一手證據

失敗 run 的 log 把整個過程演了一遍：

```
##[group]Run uv run python scripts/create_test_fixtures.py      ← 3.11 的 job
  Downloading cpython-3.10.18-linux-x86_64-gnu (27.5MiB)        ← 依 .python-version 抓 3.10
  Using CPython 3.10.18
  Removed virtual environment at: .venv                          ← 把 3.11 環境刪了
  Creating virtual environment at: .venv                         ← 重建
  Installed 11 packages in 7ms                                   ← 只有 11 個（無 dev extra）
##[group]Run uv run pytest tests/ ...
error: Failed to spawn: `pytest`
```

上一個步驟 `uv sync --locked --python 3.11 --extra dev --extra llm` 裝的是 50+ 個套件；`uv run` 不帶 `--python` / `--no-sync` 就依 `.python-version` 重解析，把它整個換掉。**它的敘述一字不差。**

```
cat .python-version → 3.10 ✓
uv run --help → --no-sync   Avoid syncing the virtual environment
uv --version  → uv 0.8.22
```

`--no-sync` 的語意是「不要同步環境，直接用既有的」，不是「進入既有 venv」的別名 —— **`uv run` 預設會同步（必要時重建），這正是問題根源**。

#### C2 「12 處」 —— ✅ 屬實，無漏網

```
grep -o "uv run" test.yml | wc -l           → 15
grep -o "uv run --no-sync" test.yml | wc -l → 12
```

差的 3 個在註解裡（`:21,22,25`，說明這條規則本身）。**實際會執行的 12 處全部帶 `--no-sync`。** 根倉庫 workflow 不用 uv，不受影響。

**修法判斷**：正確且副作用可接受。每個 job 在 `uv run` 之前都先跑了 `uv sync --locked --python ${{ matrix.python-version }} --extra dev --extra llm`，環境是確定的；`--locked` 保證不會偷改 lock。

**但有一處它沒提**：`.pre-commit-config.yaml` 的兩個 local hook 用的是 `uv run --frozen`（不是 `--no-sync`），而 **`--frozen` 只管 lockfile、不阻止 sync**。CI 的 Pre-commit job 是 `uv run --no-sync pre-commit run --all-files` 巢狀呼叫這些 hook —— **外層有保護，內層沒有**。本次沒炸是因為該 job 用 `PYTHON_DEFAULT: 3.10`、與 `.python-version` 一致（log 裡沒有 `Removed virtual environment`），是**版本剛好對上而不是被防護住**。哪天有人給 Pre-commit job 加一個非 3.10 的矩陣，同一個坑會再開一次。

---

## 3. D 節未竟事項總表：**8 完成 / 1 部分（D7）/ 1 已作廢（D9）**

| #      | 項目                                               | 判定        | 證據                                                                                                                                                                                   |
| ------ | -------------------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1     | 根 `README.md:6-7` badge                           | ✅          | 改成 `tests-235 passed (CI)` / `coverage-85% (CI)`，下方補兩情境說明                                                                                                                   |
| D2     | `docs/00_executive_summary.md:14`                  | ✅          | 「235 個測試(CI) / 238(真實客戶檔在位)，覆蓋率 85% / 89%」                                                                                                                             |
| D3     | `docs/USER_GUIDE.md:784`                           | ✅          | 表格三列改為兩情境並列（含 skip 數）                                                                                                                                                   |
| D4     | skill `README.md:164` ≥90% vs `AGENTS.md:275` ≥80% | ✅          | 現為「目標 ≥ 80%，與 AGENTS.md 一致」，打架解除                                                                                                                                        |
| D5     | `_editable_impl_fa_improver 2.pth`                 | ✅          | 只剩正本，衝突副本已刪                                                                                                                                                                 |
| D6     | `create_test_fixtures.py` bootstrap                | ✅          | `319283a` 加 `sys.path.insert(0, ...parents[1]/"src")`，註解說明「診斷工具本身不能跟著壞」                                                                                             |
| **D7** | `CLAUDE.md` 三條規則                               | ⚠️ **2/3**  | 規則 (1)(2) 在 `:202-205` ✅；**規則 (3)「時效性證據只能寫『無法驗證』不能寫『不實』」沒寫** —— `grep "無法驗證\|時效"` 零命中。它的 commit message 自稱「兩條流程規則」，**沒有謊報** |
| D8     | F1d 改回                                           | ✅          | `5c2ee1e` 改為「F1d（已於第六輪改判為成立）」，並自陳「認錯認過頭也是另一種不精確」                                                                                                    |
| **D9** | ~~`UV_PROJECT_ENVIRONMENT`~~（**已作廢，見第 6 節第 8 項**）                           | ❌ **未做** | 只寫進 `CLAUDE.md:95-99` 當「建議的根治（需 Kenny 決定）」。實測 20:13：`.venv` 仍在專案內、7,206 個 hidden 檔、`.pth` 仍 hidden、CLI 仍壞。**還在用 `chflags` 賭**。⚠️ **但此項已於 21:00 由柔伊收回，不要再做** —— 改為直接搬離 iCloud，理由見第 6 節第 8 項 |
| D10    | pre-commit 會擋 commit 的操作說明                  | ✅          | `CLAUDE.md:78-90`，含症狀對照表 + `chflags -R nohidden .` + 「紅是正常的，不是程式壞掉」                                                                                               |

---

## 4. 它這輪還沒說的問題

### E1 備份又過期 —— 連續兩輪同一個失誤

詳 A6。三個 commit 不在 bundle 裡，其中一個是這輪最關鍵的 CI 修正。**而且是在它自己剛把「宣稱完成前重跑驗收」寫進 `CLAUDE.md` 之後犯的。** 現有規則文字沒涵蓋「備份」，需要補。

### E2 剛改好的測試數已經是舊的 —— 第三次「改了一部分就宣告」

```
文件寫（README badge / CLAUDE.md:136 / exec_summary / USER_GUIDE）：
    CI 235 passed + 3 skipped / 85%；真實檔在位 238 passed + 0 skipped / 89%
HEAD(fc6fd2c) 的實際 CI，六個 job 一致：
    236 passed, 3 skipped                          ← 差 1
本機實測總測試數：239（236 passed + 3 failed）     ← 對應 239，不是 238
```

原因：數字量在 `b2309d0`，之後 `319283a` 又加了第三支 import 測試。**這正是它剛寫下的規則要防的事，規則寫完的同一輪就破功。**

### E3 branch protection 保護不到它剛修好的那個回歸

required contexts 只有 4 個：`Lint & Format`、`Pre-commit`、`Test (ubuntu-latest / Python 3.10)`、`Test (macos-latest / Python 3.10)`。**3.11 / 3.12 的四個 job 都不是 required** —— 這輪整整掛掉四個 job 的那個 bug，如果重來一次，**branch protection 會放行**。

### E4 技能包的成果不在 `main` 上，而 `main` 的 CI 產不出被要求的 check

```
git show origin/main:.github/workflows/test.yml
  56:  name: Test (Python ${{ matrix.python-version }})   ← 舊名稱，沒有 matrix.os
  62:  os: [ubuntu-latest]                                ← 沒有 macOS
```

`main` 現在被要求 `Test (macos-latest / Python 3.10)` 與 `Pre-commit` 兩個 check，但 **`main` 自己的 workflow 一個都產不出來**。走 PR 合併時 GitHub 用的是 PR head 的 workflow，所以合得進去；但「P3 完成」的成果目前不在預設分支上，**任何人 clone 拿到的還是舊 CI**。

### E5 文件還在教 `git push origin main`，而那條指令已對兩個 repo 失效

`README.md:112` 與 `AGENTS.md:295-299`。全 repo 的 tracked 文件裡找不到任何一句說明「現在必須走 PR」或「單人維護所以放棄 reviewer 這條」。計劃書 P3 第 5 步明文要求：

> 要在文件裡誠實寫明這個取捨，**不要宣稱流程防呆已經完整**

**這條沒做，而它宣告了「P3 完成（含第 5 步）」。**

### E6 CI 綠，但 Codecov 上傳一直是紅的、被吞掉了

```
ubuntu-3.10 job log:
error -- Commit creating failed: {"message":"Token required - not valid tokenless upload"}
error -- Report creating failed: ...
```

`fail_ci_if_error: false` + `CODECOV_TOKEN` secret 未設。**覆蓋率從來沒有真的上傳成功過，而 job 顯示綠色** —— 屬於「看起來正常但從來沒運作過」的同一類毛病，正是這個專案這幾輪一直在修的東西。

### E7 第 9 個 job `Build Distribution` 從沒在這條分支跑過

`if: github.ref == 'refs/heads/main' || tags`，且 `needs: [lint, test, pre-commit]`。「8/8 綠」是真的，但**打包這一環要等合併到 main 才第一次驗證**。

### E8 這輪沒有寫任何新的 handoff

`docs/handoff/` 最新一份是 16:29 的 `execution-findings`（那是 P0-P2 的）。P3 的成果 —— macOS runner、路徑守門、根倉庫 CI、branch protection、`uv --no-sync` 回歸 —— **沒有任何交接紀錄**。

### E9 `CLAUDE.md` 的「目前進度」整段已經是假的，而且已經 push 上遠端

`CLAUDE.md:32-45` 現在還寫著：

> | P0-P7 | **全部尚未開始**，程式碼一行未改 |
> | 根倉庫 | 有數個 commit 在本地 `main`，**未 push** |
> | 技能包倉庫 | 完全未動，HEAD 與 `origin/main` 同步 |
> **未經 Kenny 明確指示不要開始執行 P0，也不要 push。**

**四句話四句錯。** 這是下一個 session 開場第一個會讀到的檔。有一行免責（「這行字會過時」），但內容是**積極的錯誤陳述**，不是模糊。

### E10 技能包 `.git/hooks/pre-commit` 的 `INSTALL_PYTHON` 仍寫死 `.venv/bin/python`

就是那個被 iCloud 反覆弄壞的 venv。這是 pre-commit 產生的、不受版控，但跟這輪「不要假設 venv 內部佈局」的主軸直接衝突 —— venv 一重建 hook 就跟著壞（P0 已經修過一次同樣的事）。**若採用 D9，這個 hook 必須重新 `pre-commit install`。**

### E11 iCloud 衝突副本持續增生，已吃到 venv 的執行檔層級

`.venv/bin/fa-improve 2`、`.venv/lib 2`、`.coverage 2/3/4`、`.ruff_cache/0.16.5 2` …

**好消息**：全部被 gitignore 蓋住（兩個 repo `git status` 皆乾淨），`.git/` 內目前**無**衝突副本（`find .git -name "* [0-9]*"` 零命中，兩個 repo 都查）。
**壞消息**：20:13 實測 `.venv` 內 7,206 個 hidden 檔。

### E12 根倉庫 CI 只跑那兩支腳本，沒跑 pre-commit

根倉庫的 `check-yaml` / `check-json` / `detect-private-key` / `check-added-large-files` / `trailing-whitespace` 在 CI 上從未執行過。計劃書 P3 第 2 步的理由（「這些從來沒有在 PR 上被執行過」）**對根倉庫依然成立**。

---

## 5. branch protection 的獨立判斷

**整體是好的，但目前的設定值有一個實質缺口、一個未處理的操作代價。**

**該設，理由成立。** 這個專案連續兩輪發生「rebase 衝突標記沒清乾淨就直推 main」（`6e4089b`、`5b48690` 都在補這個），那是靠人記得攔不住的類型。`enforce_admins=true` 是對的 —— 設 `false` 等於留一個「我是 admin 我最懂」的後門。`required_approving_review_count: 0` 也是對的取捨：單人維護設 1 會鎖死自己，Codex 版計劃書那個顧慮是真的，採納正確。

**實質缺口（E3）**：required checks 只涵蓋 4/8 個 job，3.11/3.12 不在內。**它這輪剛親手修好的回歸，protection 擋不住。** 建議把六個 test job 全部列入 —— 反正 `fail-fast: false`、整條 pipeline 44 秒跑完，沒有成本理由不列。

**未處理的操作代價**：接下來每次改動都要 `git checkout -b` → push → `gh pr create` → 等 CI → `gh pr merge`。對這個專案的節奏（一輪稽核往往推 10~20 個 commit），會明顯變慢。三件事必須先講清楚而現在都沒講：

1. 文件（`README.md:112`、`AGENTS.md:295-299`）還在教 `git push origin main`，要改成 PR 流程
2. 這台機器上 pre-commit 會因 iCloud 週期性擋 commit，再疊一層 PR 流程，「送一個修正出去」的摩擦會變高
3. **緊急情況怎麼辦**：`enforce_admins=true` 代表沒有後門。要嘛接受「緊急時先 `gh api -X DELETE .../protection` 再補回」，要嘛就別喊緊急 —— **現在兩者都沒定義**

**結論：設是對的，但「設完就算完成」不對。** 它做完了 API 呼叫，沒做完流程改變該配的文件與心理準備 —— 而計劃書明文要求了後者。

---

## 6. 給 Claude Code 的指示（可直接執行）

> 以下由柔伊彙整，包含這輪稽核結果與肯尼大 的決定。**照順序做，做完回報。一樣不要 push 到 main，走 PR。**

### 🔴 立刻（止血，5 分鐘）

**1. 重拍 bundle —— ✅ 柔伊已於 21:04 執行完畢，跳過此項。** 原本的問題是 16:32 的備份差三個 commit（`b5adea8`、`cc06204`、`fc6fd2c`）。新備份已驗證涵蓋到現在的 HEAD。當時用的指令留在這裡供日後參考：

```bash
git -C <root>  bundle create ~/fa-report-refactor-backups/root-$(date +%Y%m%d-%H%M).bundle --all
git -C <skill> bundle create ~/fa-report-refactor-backups/skill-$(date +%Y%m%d-%H%M).bundle --all
```

然後**把「備份必須在最後一個 commit 之後」補進 `CLAUDE.md`** —— 你連兩輪栽在同一個地方，現有的規則文字沒涵蓋備份。

**2. 修 `CLAUDE.md:32-45` 的「目前進度」整段**（E9）。那是下一個 session 的第一印象，現在四句全錯。**建議直接改成「跑 `git log --oneline origin/main..HEAD` 與 `gh run list` 自己看」，不要再維護一份會過期的狀態快照** —— 這跟你把 pre-commit hook 名稱裡的測試數改成「全套測試」是同一個道理。

### 🟠 這輪的收尾（半小時）

**3. 測試數字對到 HEAD**（E2）。實測值：CI 情境 **236 passed + 3 skipped / 85%**；真實檔在位 **239 passed / 89%**（含 3 支 import 測試）。README badge、`CLAUDE.md:136`、`00_executive_summary.md:14`、`USER_GUIDE.md:782-786` 四處都差 1。**並照你自己剛寫的規則，附上量測時的 HEAD SHA。**

**4. 補 `CLAUDE.md` 的第三條規則**（D7）：

> **對「時效性證據」（會被覆寫、刪除、重新產生的檔案狀態）下判定時，只能寫「無法驗證」，不能寫「不實」。** 要寫「不實」必須有正面反證，不能只有「我重現不出來」。證據消失 ≠ 證據不存在過。

（這條是柔伊第五輪把你的 F1d 誤判成「不實」換來的教訓，寫進去讓雙方都別再踩。）

**5. 補 branch protection 的流程文件**（E5）：`README.md:112` 與 `AGENTS.md:295-299` 的 `git push origin main` 改成 PR 流程，並照計劃書 P3 第 5 步的要求**誠實寫明「reviewer 那項因單人維護放棄」這個取捨**。順便定義**緊急情況的處置**（要嘛明確寫「緊急時先 `gh api -X DELETE .../protection` 再補回」，要嘛明確寫「不設後門」）。

**6. 把 3.11/3.12 四個 job 加進 required status checks**（E3）—— 六個 test job + Lint & Format + Pre-commit 全列。

**7. 補一份 P3 的 handoff**（E8）。

### 🟢 決策題（**第 8、9 項皆已定案，照下方最新結論執行**）

**8. `UV_PROJECT_ENVIRONMENT` —— ❌ 柔伊已於 21:00 收回這個建議，不要做。改為直接搬離 iCloud。**

**收回的理由（實查後才發現的漏洞）**：

這個方案唯一的投遞管道是環境變數，而環境變數要靠 `direnv` 之類的機制注入 —— **`direnv` 掛在 shell 的提示符事件上，只有互動式終端機會觸發**。而你（Claude Code）執行指令、pre-commit hook 跑測試，用的都是非互動式 shell（`zsh -c "..."`），**根本不會觸發**。後果是：

```
環境變數沒設 → uv 退回找專案內的 .venv
            → 找不到（因為剛搬走）
            → uv 直接在專案內重建一個 → 又回到 iCloud 裡
```

**等於白搬，而且是靜默失敗**，直到 CLI 又壞掉才會發現。

也查過有沒有設定檔可以繞過：**`uv` 沒有任何 `uv.toml` / `pyproject.toml` 層級的等價選項**（`uv sync --help | grep -c project-environment` → 0），只吃環境變數。所以**不存在一個對所有呼叫路徑都可靠的專案級設法**。

**改為：直接把專案搬離 `~/Desktop`（iCloud 範圍）。** 搬家成本經實查極低：

```
技能包 tracked 檔裡寫死目前絕對路徑的：0 個   ← P1 的成果，搬完程式碼零修改
根倉庫：2 個（皆為 handoff 文件的敘述文字，不影響功能）
```

**搬家的步驟與時機由肯尼大 主導，你不要自己動手 `mv`。** 目前規劃的順序是：

1. 你先做完第 2 項（修 `CLAUDE.md` 的「目前進度」）—— **這一步必須在 `/clear` 之前完成**，因為那段是新 session 開場第一個讀到的檔，現在四句全錯，清空後你會直接讀到「什麼都還沒做、不准動手」而失憶
2. 你 `/clear`
3. 肯尼大 退出你的 session，由柔伊執行搬移
4. 你在新路徑重開，接 P4

**搬完之後需要處理的兩件事**（柔伊會做，這裡先記著）：

- `uv sync` 重建 venv（舊的 `.venv` 的 `pyvenv.cfg` 與 `bin/` shebang 都寫死絕對路徑，不能直接搬）
- 重跑 `pre-commit install`（E10：hook 的 `INSTALL_PYTHON` 也寫死舊 venv 路徑）

**9. branch protection —— ✅ 肯尼大 已於 2026-09-05 21:00 拍板並由柔伊執行完畢，不要再動 API。**

**決定與現況（已實測驗證）**：

```
fa-report-refactor       enforce_admins=true    ← 技能包維持嚴格
fa-report-refactor-root  enforce_admins=false   ← 根倉庫已放寬
兩個都保留：allow_force_pushes=false  allow_deletions=false  strict=true
```

⚠️ **這代表你先前那句「兩個 repo 都 `enforce_admins=true`」已經過期**，根倉庫的文件改動現在可以直推、不需要走 PR。技能包仍需走 PR。**請據此更新文件（第 5 點）。**

當初的判斷理由如下，供你寫文件時引用：

- **技能包 `fa-report-refactor`**：維持 `enforce_admins=true`。這是要交付給別的 Agent 使用的產品，嚴一點是對的
- **根倉庫 `-root`**：可考慮改成 `false`，但**保留 `allow_force_pushes=false` / `allow_deletions=false`**。理由是 —— `enforce_admins` 綁的只是「要不要走 PR review」，而真正怕的誤 force-push / 誤刪分支是另外兩個獨立開關管的，就算 `enforce_admins=false` 也照樣生效，**所以不存在「不走 PR = 裸奔」這回事**。根倉庫是單人維護、高頻小改的文件倉庫，自己開 PR 自己核准是演戲，而且會養成「無腦點過」的習慣，那比沒開更危險

**反方意見（Claude Code 的）也成立**：連續兩輪發生「rebase 衝突標記沒清乾淨就直推 main」（`6e4089b`、`5b48690`），設 `false` 等於退回靠自律。

**設定已完成，不需要你再動 API。** 你要做的是第 5 點：把這個分法、放棄 reviewer 的取捨、以及緊急情況的處置，寫進 `README.md` 與 `AGENTS.md`。

**10. 你問的「draft PR 佔位 vs 直接跑 P4」——柔伊建議直接跑 P4，不要開佔位 draft PR。** 分支已推、CI 已在 push 事件跑過，draft PR 邊際價值接近零，而橫跨 P4-P7 的長命 PR 只會累積雜訊、diff 大到沒人看得動。等真的有東西要合併時再開。P4（`get_title_placeholder()` 的結構性缺口）是稽核連三輪點名的優先 1，也是這批唯一動到母片幾何的改動。

（第 1 項柔伊已做完；第 2-7、10-13 項是明確的待辦，可以直接做；第 8、9 項已定案，照上面的最新結論走，**不需要再等任何人拍板**。）

### 🔵 順手可加

**11. Codecov 的 `CODECOV_TOKEN` 要嘛補上、要嘛把那個步驟拿掉**（E6）。現在每次 CI 都吐三行紅字然後被吞掉。

**12. `check_markdown_links.py` 只檢查 `.md` 不檢查 `.html`**（B2 延伸）—— 驗收頁的 `index.html` 那類死連結下次仍抓不到。

**13. `.pre-commit-config.yaml` 的兩個 local hook 用 `uv run --frozen`，而 `--frozen` 不阻止 sync**（C2）。本次沒炸是因為 `PYTHON_DEFAULT: 3.10` 剛好與 `.python-version` 一致，是**巧合不是防護**。建議一併改成 `--no-sync`。

---

## 附：本輪判定摘要

| 類別          | 結果                                                                    |
| ------------- | ----------------------------------------------------------------------- |
| CI / 技術聲明 | 幾乎全部屬實，數字精準（12 處、20 commit、6 條連結、macOS runner 為真） |
| `uv` 根因敘述 | ✅ 一手 CI log 證實，一字不差                                           |
| 備份聲明      | ❌ 不實（連續第二輪同一個坑）                                           |
| D 節未竟事項  | 8 完成 / 1 部分（D7，缺第三條規則）/ 1 作廢（D9，已收回改為搬家）                                     |
| 未揭露問題    | 12 項（E1–E12），其中 E3/E4/E5 影響「P3 完成」的成色                    |
