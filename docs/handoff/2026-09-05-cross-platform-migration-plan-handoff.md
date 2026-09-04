# Handoff：跨平台遷移 + 第三輪稽核修正 — 執行計劃書

> 撰寫者：Claude Code（Kenny 的 macOS 環境）
> 日期：2026-09-05
> 狀態：**待 Kenny 確認**，尚未執行任何修改
> 上游依據：`docs/handoff/2026-09-04-fa-report-refactor-audit-round3-handoff.md`（柔伊第三輪稽核）
> 執行環境：macOS 15（Darwin 25.5.0）/ Apple Silicon / zsh
> 專案根目錄：`/Users/kennykang/Desktop/VibeProj/Claude/fa-report-refactor`（原 WSL 路徑 `/home/elan/fa-report-refactor`）

## 本文件的定位

這是一份**執行前的計劃書**，不是完成報告。所有「已實測確認」的項目都是唯讀查證（`git`/`gh`/`unzip`/`uv --dry-run`），**沒有修改任何檔案、沒有 commit、沒有 push**。

Kenny 確認後才會從 P0 開始執行。

---

## Context

這個專案原本在 **Windows WSL Ubuntu**（`/home/elan/fa-report-refactor/`）用 Pi Agent 開發，現在整包搬到 **macOS**（`/Users/kennykang/Desktop/VibeProj/Claude/fa-report-refactor`，Apple Silicon、zsh）。搬過來之後有兩層問題疊在一起：

1. **環境層面直接死掉** —— `.venv/` 是整份複製過來的 **Linux x86-64** virtualenv（`.venv/pyvenv.cfg` 寫 `home = /home/elan/.local/share/uv/python/cpython-3.10-linux-x86_64-gnu/bin`），`.venv/bin/python` 是 ELF 執行檔，跑起來是 `exec format error`。連 `uv sync` 都被它擋住。所有文件、`.pre-commit-config.yaml`、CI 裡寫的 `.venv/bin/python -m pytest` 全部是死指令。
2. **路徑與工具鏈假設寫死** —— 程式碼、測試、CI、文件散落 `/home/elan/...`、`/home/runner/work/...`、`.venv/bin/...`，加上 uv 有 **三個不同版本**（WSL 0.12.7 / CI 釘 0.5 / 本機 0.8.22）、ruff 在 CI 完全沒釘版本。

同時，柔伊的第三輪稽核報告（`docs/handoff/2026-09-04-fa-report-refactor-audit-round3-handoff.md`）點出的缺口全部複驗屬實，其中「`get_title_placeholder()` 安全防線在原生 placeholder 分支完全失效」是連續三輪都在、且有實測證據的結構性漏洞。

**預期結果**：在 macOS 與 Linux/WSL 兩邊都能用同一套指令乾淨跑起來；路徑一律動態解析；工具鏈版本三處（本機 / CI / pre-commit）對齊成單一數字；稽核四大項全部收掉；最後發 v3.1.5。

### 已拍板的決策（來自本次對話）

| 項目         | 決定                                                                                                                    |
| ------------ | ----------------------------------------------------------------------------------------------------------------------- |
| 範圍         | 跨平台遷移 + 稽核優先1（`get_title_placeholder`）+ 優先2（branch protection）+ 其餘項（版本/Release/CHANGELOG/覆蓋率）  |
| 目標平台     | **macOS + Linux/WSL 雙向可跑**（不做 Windows 原生，但指令選用天然相容 Windows 的形式）                                  |
| 文件路徑     | 只改「活的」指引文件；`docs/handoff/` 底下的歷史紀錄**保留原樣**（那是當時的事實）                                      |
| 版號收尾     | 這輪改完後發 **v3.1.5**，不動已發布的 v3.1.4                                                                            |
| 輸出檔相容性 | 納入（P7）：修 OOXML 不合法值 + 加自動合規測試 + 實際開檔驗收。字型替代與文字溢出先寫成「已知限制」，不改 improver 行為 |

---

## P0 — 環境重建（阻斷性，必須最先做）

1. 刪掉 Linux venv：`rm -rf .agents/skills/fa-report-improvement/.venv`
2. 同時清掉搬遷殘留：`.ruff_cache/0.1.9/`、`.pytest_cache/`、`.coverage`、`dist/fa_improver-3.1.0*`、`scripts/improve_fa_report.py.bak`、根目錄 `.playwright-cli/`、`.agents/skills/playwright-cli/` 底下 11 個 WSL `*:Zone.Identifier`
3. `uv python install 3.10`（`.python-version` = 3.10；系統 `python3` 是 3.9.6，不能用）
4. `uv sync --extra dev --extra llm` 重建
5. **重裝 git hook**：`cd .agents/skills/fa-report-improvement && uv run pre-commit install`
6. **確認 GitHub 帳號權限**（見下方第二個 ⚠️，這決定 P3/P6 能不能做）

> ⚠️ **`.git/hooks/pre-commit` 是從 WSL 整份搬過來的，現在任何 `git commit` 都會失敗**（實測）
>
> 技能包倉庫的 `.git/hooks/pre-commit` 內容寫死：
> ```
> INSTALL_PYTHON=/home/elan/fa-report-refactor/.agents/skills/fa-report-improvement/.venv/bin/python
> ```
> 判斷邏輯是「`INSTALL_PYTHON` 不存在 → 退而找 PATH 上的 `pre-commit` → 都沒有就 `exit 1`」。這台 Mac 兩個條件都不成立，所以 commit 會被 hook 擋掉。
>
> **跑完 P0 第 4 步之後仍然是壞的** —— 路徑寫死在 hook 檔案裡，`uv sync` 不會去改它，改 `.pre-commit-config.yaml` 也不會（YAML 是設定，hook 是 `pre-commit install` 產生的腳本，兩者分開）。必須執行第 5 步重新產生。
>
> 已查：`core.hooksPath` 三個層級（root repo / skill repo / global）**都未設定**，所以只需處理 `.git/hooks/pre-commit` 這一個檔案。根倉庫 `.git/hooks/` 只有 `.sample`，從來沒裝過 pre-commit —— P3 的路徑守門 hook 要在根倉庫另外 `pre-commit install` 一次。

> ⚠️ **這台 Mac 的 GitHub 帳號對兩個 repo 都沒有寫入權限**（實測，兩份計劃書都沒發現）
>
> | 項目 | 實測值 |
> |---|---|
> | `gh auth status` | 登入為 **`KennyKang7012`** |
> | repo owner | **`kcf7012`**（不同帳號） |
> | `gh api repos/kcf7012/fa-report-refactor` 的 permissions | `admin=false  push=false` |
> | `git push --dry-run` | `remote: Permission to kcf7012/fa-report-refactor.git denied to KennyKang7012.` → **403** |
> | git credential helper | `osxkeychain`（存的也是 KennyKang7012） |
> | 本機 commit 身分 | `Kenny Kang <kenny.kang@elan.com.tw>`（repo 內 14/15 個 commit 都是這個 email） |
>
> **影響**：P3 的 branch protection（需要 admin）、P6 的 tag push / `gh release create`、補 `CODECOV_TOKEN` secret、甚至最基本的 `git push` 與開 PR，**從這台機器全部做不到**。
>
> **已決定（Kenny 2026-09-05）**：進行到 P3／P6 時用 **`gh auth login` 重新以 `kcf7012` 登入**。
>
> 這條路徑比加協作者更直接，因為 **branch protection 需要 `admin` 權限，協作者的 `write` 不夠**。
>
> 另外要注意 `gh` 與 `git push` 是**兩套憑證**：`gh auth login` 只換 gh CLI 的 token，`git push` 走的是 `osxkeychain`。換帳號時要一併處理（`gh auth setup-git`，或手動更新 keychain 內 `github.com` 的項目），否則會出現「`gh` 可以但 `git push` 還是 403」。
>
> 補充實測（2026-09-05）：Kenny 表示已把 `KennyKang7012` 加為協作者，但複查 **權限仍是 `push=false`，且 `user/repository_invitations` 沒有待接受的邀請** —— 該設定沒有生效。因為已改走 `kcf7012` 登入，這一項不需再追。
>
> **三套獨立機制不要混為一談**（這是當時混淆的根源）：
>
> | 機制 | 本機目前值 | 決定什麼 |
> |---|---|---|
> | `git config user.email` | global `kenny7012@gmail.com`，但兩個 repo 的 **local 都覆蓋成 `kenny.kang@elan.com.tw`** | 只決定 commit 的作者署名，**與權限無關** |
> | credential（osxkeychain） | username = `14908981` = `KennyKang7012` | 決定 `git push` 的身分 —— 403 的真正來源 |
> | GitHub 協作者／擁有者 | repo 屬於 `kcf7012`（id 73571535） | 決定誰能 push、誰能設 branch protection |
>
> `kcf7012`（id 73571535）與 `KennyKang7012`（id 14908981，2015 建立）是**兩個不同的 GitHub 帳號**。在 GitHub「Add people」填 email，只有當該 email 是某帳號的「已驗證 email」時才會解析成帳號。
>
> **附帶**：兩個 repo 共 **59 個 commit** 的作者 `kenny.kang@elan.com.tw` 未連結任何 GitHub 帳號（灰頭像、不計入貢獻）。該位址**不存在**，無法驗證，所以回溯連結做不到 —— 詳見下方「commit 署名」。

### P0 附帶：`.git/` 是整份複製，不是 clone

Kenny 確認專案是從 WSL **整個目錄拷貝**過來的，所以 `.git/` 內部狀態（含 repo-local config 與已安裝的 hook）全部沿用 WSL 那台。實測掃描結果：

| repo | 遺留物 | 後果 | 修法 |
|---|---|---|---|
| skill | `.git/hooks/pre-commit` 寫死 `/home/elan/...` | **`git commit` 直接失敗** | P0 第 5 步 `uv run pre-commit install` |
| skill | **`main` 沒有 upstream 追蹤** —— `[branch "main"]` 只剩 `vscode-merge-base = origin/main`（VS Code 殘骸），正式的 `remote` / `merge` 兩行不存在 | `git pull` 在 main 上 fatal；`git status` 不顯示 ahead/behind | `git branch --set-upstream-to=origin/main main` |
| skill | 本地分支 `v3.1.4-audit-fixes` 追蹤的遠端分支**已刪除**（遠端只剩 `main` 與 `v3.1.4-regression-fix`） | 孤兒分支 | `git fetch --prune` 後刪除已合併的本地分支 |
| 兩者 | repo-local `user.email = kenny.kang@elan.com.tw`（**Kenny 確認這是 Pi Agent 當時設錯的位址**）蓋掉 Mac 的 global `kenny7012@gmail.com` | 兩個 repo 共 **59 個 commit** 在 GitHub 上未連結任何帳號 | 只改未來，不動歷史 —— 見下方「commit 署名」 |

**其餘都乾淨**：remote URL 正確、`core.filemode = true`（macOS 正確值）、無 `core.hooksPath`、無 LFS filter、無 credential 覆寫。root repo 的 `main` upstream 追蹤正常。

#### commit 署名：只修未來，不改歷史

**背景**：三個 Gmail／信箱一度被混為一談，釐清如下——

| 位置 | 值 | 說明 |
|---|---|---|
| kcf7012 GitHub 主要信箱 | `kcf7012@gmail.com`（Primary / Verified / **Private**） | 帳號唯一的驗證信箱 |
| Mac global git config | `kenny7012@gmail.com` | **與上者差一個字，是不同位址**；先前協作者設定沒生效多半源於此 |
| 兩個 repo 的 local git config | `kenny.kang@elan.com.tw` | **設錯的位址**（Pi Agent 當時的設定失誤），無法驗證 |

kcf7012 的兩個相關開關已實際確認（2026-09-05 截圖）：

| 設定 | 狀態 | 意義 |
|---|---|---|
| Keep my email addresses private | **On** | web-based Git operations 一律用 `73571535+kcf7012@users.noreply.github.com` |
| Block command line pushes that expose my email | **Off** | 不會出現 `GH007: Your push would publish a private email address` |

因此 **GH007 不是風險**。改署名的理由單純是「現在這個位址是錯的」，不是為了規避推送阻擋。

**決定**：
```bash
# root repo 與 skill repo 各執行一次
git config user.name  "Kenny Kang"
git config user.email "73571535+kcf7012@users.noreply.github.com"
```
未來 commit 歸屬 `kcf7012`，並與帳號既有的隱私設定一致。

**明確不做：改寫歷史**。曾評估「把設錯的 email 加進 GitHub verified emails 以回溯連結 59 個 commit」，但該位址無法驗證，此路不通。改用 `git filter-repo` 重寫作者的代價則完全不成比例：59 個 commit 全部換 SHA、兩個 repo 都要 force-push、已發布的 `v3.1.4` Release 指向的 `5cb68a4` 失效、稽核報告與各份 handoff 引用的 SHA（`f2118cf`／`b071b00`／`eb9afe3`／`5db2b5a`…）全變死引用。歷史 commit 顯示灰頭像、不計入貢獻圖，是**純外觀**問題。

> **已確認（Kenny 2026-09-05）**：`kenny.kang@elan.com.tw` 是**不存在的位址**（網域打錯，正確是 `emc.com.tw`），不是任何同事的信箱。因此沒有「公開他人公司信箱」的疑慮，**改寫歷史徹底排除**，此議題結案。

#### 清除這個不存在的信箱：完整清單

`kenny.kang@elan.com.tw` 不只在 git config，還散在套件 metadata 與文件裡。掃描結果（不含 `docs/handoff/` 歷史紀錄與本計劃書自身的引述）：

| 位置 | 性質 | 歸屬階段 |
|---|---|---|
| root repo `.git/config` → `user.email` | 本機設定，未追蹤 | **P0**（改 noreply） |
| skill repo `.git/config` → `user.email` | 本機設定，未追蹤 | **P0**（改 noreply） |
| `.agents/skills/fa-report-improvement/pyproject.toml:9` `authors` | **會被打包發布的套件 metadata** | **P5**（需 commit） |
| `docs/08_uv_integration.md:53` | 文件內的 pyproject 範例 | **P5** |
| `docs/10_api_reference.md:543` | 維護者聯絡資訊 | **P5** |

> ⚠️ 已建置的產出物也烙進去了：`dist/fa_improver-3.1.0-py3-none-any.whl` 的 METADATA 含 `Author-email: Kenny Kang <kenny.kang@elan.com.tw>`。CI 每次推 main 都會重新建置並上傳 artifact，所以改完 `pyproject.toml` 後產出物會自動更新；本機 `dist/` 那兩個舊檔在 P0 第 2 步一併清掉。
>
**兩種用途用不同的值**（Kenny 2026-09-05 拍板）：

| 用途 | 值 | 理由 |
|---|---|---|
| git commit 署名（兩個 repo 的 `.git/config`） | `73571535+kcf7012@users.noreply.github.com`，name 維持 `Kenny Kang` | 機器可讀，未來 commit 連結到 `kcf7012`；符合帳號的 private email 設定 |
| `pyproject.toml` `authors` | **只留名字，拿掉 email**：`authors = [{ name = "Kenny Kang" }]`（PEP 621 允許） | 不在 public repo 與每一份 wheel 的 METADATA 裡曝露任何信箱 |
| `docs/10_api_reference.md:543` 維護者資訊 | 改為 `Kenny Kang`，聯絡管道寫「問題回報請開 GitHub Issue」 | 同上；GitHub Issues 本來就是實際的聯絡管道 |
| `docs/08_uv_integration.md:53` | 同步更新該處的 pyproject 範例 | 範例要與實際檔案一致 |

> 掃描注意事項：Claude Code 的 shell 內 `grep` 是包裝函式且預設 `--exclude-dir=.git`，用 `grep -r` 掃 `.git/` 會**靜默回傳空結果**。要掃 `.git/` 必須用 `find .git -type f -exec command grep -l ... {} +`。

---

> **已實測確認**：本機 uv 0.8.22 讀得懂 `uv.lock`（`revision = 3`），dry-run 可解出 ruff 0.16.5 / pytest 9.1.1 / pre-commit 4.6.2 —— 所以 lockfile **不是**阻礙，唯一的阻礙是那個 Linux venv。
>
> `.gitignore` 已排除 `.venv/`，所以刪掉不影響任何 git 狀態。

**選配**：`brew install --cask libreoffice`。只有 `.ppt→.pptx` 轉檔與 `scripts/visual_smoke_test.py` 視覺驗證需要，**測試套件不需要**（純 XML 幾何斷言）。`pdftoppm` 已經有（`/opt/homebrew/bin`）。

---

## P1 — 路徑解析核心：一個共用 resolver

現在有 **三套互不相干**的路徑機制，這是所有路徑問題的根：

| 機制               | 位置                                                                        | 現況                                                                                            |
| ------------------ | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 向上搜尋 `report/` | `tests/conftest.py:16-31`                                                   | 動態，但會停在**技能包自己的** `report/`（因為有 `test_sample.pptx`），拿不到根倉庫的真實客戶檔 |
| 硬編候選清單       | `tests/integration/_fixture_resolver.py:32-36`                              | `/home/elan/...` + `/home/runner/work/...`，macOS 兩個都 miss                                   |
| 直接寫死           | `scripts/run_batch_evaluation.py:24,193`、`scripts/visual_smoke_test.py:25` | macOS 上腳本 100% 死掉                                                                          |

**做法：新增 `src/fa_improver/paths.py`**，成為套件內唯一的路徑事實來源（放在 `src/` 而非 `tests/`，這樣 scripts 與 tests 都能 import）。介面：

```python
SKILL_ROOT: Path                      # Path(__file__).resolve().parents[2]
def find_project_root(start=None) -> Path | None
def get_report_dir() -> Path
def resolve_report_file(name) -> Path | None
```

`find_project_root()` 的優先序：

1. `FA_REPORT_PROJECT_ROOT` 環境變數 —— 用 **`os.pathsep`** 切（不是寫死 `":"`，這行是 `_fixture_resolver.py:36` 目前的 Windows 地雷）
2. `GITHUB_WORKSPACE` 環境變數 —— 取代硬編的 `/home/runner/work/...`，這樣 ubuntu / macOS runner 都對（macOS runner 是 `/Users/runner/work/...`）
3. 從 `SKILL_ROOT` 向上走，找**同時**滿足「有 `report/`」且「有 `.agents/skills/fa-report-improvement/`」的目錄 —— 這個雙條件是關鍵，可以正確跳過技能包自己的 `report/`，找到外層根倉庫
4. 都沒有 → `None`（技能包被 `pip install` 獨立安裝時的正常情況，呼叫端要能優雅降級）

**改用它的地方**（全部改成 delegate，不再各自實作）：

- `tests/integration/_fixture_resolver.py` —— 刪掉 `_DEFAULT_ROOTS`，改呼叫 `paths.find_project_root()`
- `tests/conftest.py:16-31` —— 改呼叫同一支，並保留現有的 `needs_pptx` 等 skip 機制
- `scripts/run_batch_evaluation.py`、`scripts/visual_smoke_test.py` —— 移除 `/home/elan` 字面值，改用 `paths.get_report_dir()`，並加 `--report-dir` CLI 參數覆寫
- `scripts/create_test_fixtures.py:20` —— `Path("report")` 依賴 cwd，改成 `SKILL_ROOT / "report"`

**修完的直接效果**：這台 Mac 上 `report/` 明明有真實客戶 pptx（`260811_Kobo_*.pptx`、`MS_Meishan_*.pptx` + 對應 `fa_report_*.json/.txt`），現在 16 個視覺回歸測試卻全部靜默 fallback 去跑合成 fixture，**真實客戶檔的覆蓋等於整個消失**。修完就回來了。

### P1 附帶的小修

| 檔案:行                                                     | 問題                                                                                                                                                                 | 修法                                                                          |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `tests/integration/test_slide_rendering.py:127,150,197,261` | `pytest.skip(f"需要 {input_pptx.name}...")` —— `input_pptx` 可能是 `None`，會噴 `AttributeError`（error 而非 skip），正是 `conftest.py:106-109` 當初修掉的同一種 bug | 改成常數訊息（同檔 `:169,:230` 已經是對的寫法）                               |
| `tests/integration/test_full_workflow.py:42-46`             | `parent.parent.parent / "report"` 只到技能包根，N160JCN 檔在外層根倉庫 → 永遠 skip                                                                                   | 改用 `paths.resolve_report_file()`                                            |
| `tests/unit/test_env_loading.py:80`                         | 寫入含中文的 `write_text()` 沒給 `encoding=`                                                                                                                         | 補 `encoding="utf-8"`                                                         |
| `scripts/ppt_converter.py:143`                              | `__main__` 寫死 `C:\Users\KennyKang\Desktop\...`                                                                                                                     | 刪掉 `__main__` 區塊（`src/fa_improver/utils/ppt_converter.py` 已取代此腳本） |
| `test_llm_end_to_end.py:40`                                 | `default="/tmp/llm_improved.pptx"`                                                                                                                                   | 改用 `tempfile.gettempdir()`                                                  |

### P1 附帶：LibreOffice 探測統一

現在有 **四份不同**的 LibreOffice 尋找邏輯（`src/fa_improver/utils/ppt_converter.py:51-56`、`scripts/ppt_converter.py:36-42`、`scripts/install.py:107-113`、`scripts/visual_smoke_test.py:33-39`），彼此不一致。其中 `visual_smoke_test.py` 最糟：只 `shutil.which("libreoffice")`，macOS 裝了 LibreOffice 也**還是**會 `sys.exit(1)`（macOS 預設不把 `libreoffice` 或 `soffice` 放進 PATH），錯誤訊息還寫死 `apt install`。

在 `src/fa_improver/utils/ppt_converter.py` 匯出 `find_libreoffice() -> str | None`，順序：`shutil.which("soffice")` → `shutil.which("libreoffice")` → `/Applications/LibreOffice.app/Contents/MacOS/soffice` → `/opt/homebrew/bin/soffice` → `/usr/bin/libreoffice` → `/usr/bin/soffice` → Windows `C:\Program Files\...`。其餘三處全部改用它，錯誤訊息依平台給正確的安裝指令。

---

## P2 — 工具鏈版本對齊（一個數字，三個地方）

現況三處各說各話：

| 工具  | 本機               | CI                                                 | pre-commit / lock                                                  | 文件宣稱                                                                                           |
| ----- | ------------------ | -------------------------------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| uv    | **0.8.22**         | `UV_VERSION: "0.5"`（實測 CI log 抓 0.5.31）       | `.venv/pyvenv.cfg` 記 0.12.7                                       | `AGENTS.md:20`、`references/virtual-environment-guide.md:4` 寫「0.12.7+」                          |
| ruff  | 沒裝（靠 uv sync） | **完全沒釘**（`pyproject.toml:31` 是 `ruff>=0.1`） | `.pre-commit-config.yaml:11` `rev: v0.16.5`；`uv.lock` 解出 0.16.5 | `docs/08_uv_integration.md:257` 寫 `rev: v0.1.6`（第三個數字）                                     |
| black | 沒裝               | 沒跑                                               | `.pre-commit-config.yaml:21-27` 已註解停用                         | `AGENTS.md:23,95`、`docs/08_uv_integration.md:77,98,356`、skill `README.md:203,205` 都還說有 black |

**做法**：

1. `uv self update` 升到最新，記下版本號 `X.Y.Z`（本機 uv 0.8.22 是 2025-09 的舊版）。若不想升，維持 0.8.22 也可以 —— 已驗證能讀現有 lock，只是要把下面每個地方都填 0.8.22。
2. `uv lock` 重新產生 —— 現在 `uv.lock:286-287` 還把專案自己釘在 `version = "3.1.0"`，pyproject 是 3.1.4，lock 是**過期**的。
3. `pyproject.toml:31` `ruff>=0.1` → `ruff>=0.16.5,<0.17`，讓 lock 重產時不會靜默跳大版本。
4. CI `.github/workflows/test.yml:19` `UV_VERSION: "0.5"` → `"X.Y.Z"`（與本機同一個數字），並把三處 `uv sync` 改成 **`uv sync --locked`** —— 現在用的是不帶 flag 的 `uv sync`，lock 在 CI 事實上沒被強制執行。
5. `.pre-commit-config.yaml`：
   - `rev: v0.16.5` 保留（與 lock 一致）
   - `pre-commit/pre-commit-hooks` `rev: v4.5.0` 是 2023 年的版本 → 升到目前 release（用 `gh api repos/pre-commit/pre-commit-hooks/releases/latest` 查，不要憑印象填）
   - **`:50` local pytest hook `entry: .venv/bin/python -m pytest` → `entry: uv run --frozen pytest`**（`language: system`）—— 這行是目前唯一寫死 venv 內部佈局的地方，改掉之後 macOS / Linux / Windows 都對
6. 全面用 `uv run <cmd>` 取代 `.venv/bin/<cmd>`（CI 九處 + `SKILL.md:104,107` + skill `README.md:24,155-164` + `docs/TESTING.md:17-29`）。順帶把 `docs/TESTING.md:212-242` 那批 `../venv/bin/python`（注意是 `../venv`，指向不存在的路徑）一起改掉。

### P2 附帶（補：來自 Codex 版本規劃書的 ruff 一致性分析）

- **`pyproject.toml:31` 目前只是 `ruff>=0.1`，`uv.lock` 現在雖然解出 0.16.5，但這只是「目前剛好」，不是被鎖住的**——之後任何人重新 `uv lock` 都可能悄悄跳版本，跟 `.pre-commit-config.yaml` 的 `rev: v0.16.5` 對不上而不自知。這一項跟本節第 3 點（`ruff>=0.16.5,<0.17`）是同一件事，但 Codex 版本額外強調：**升級 ruff 時，dev pin／`uv.lock`／pre-commit `rev` 三處要放在同一個 PR 一起改**，不要分批改導致中間有一段時間三處不一致。
- **CI 目前跑 `uv sync` 後直接呼叫 `.venv/bin/ruff`，沒有明確用 `--locked` 強制鎖定**（跟本節第 4 點是同一個坑，這裡是從 ruff 這個工具的角度重申一次）。
- **本機 Git hook 與 YAML 是兩回事** —— 這條 Codex 的提醒方向完全正確，而且**實測證實已經壞了**，嚴重度比「提醒」高：`.git/hooks/pre-commit` 寫死 WSL 路徑，導致技能包倉庫現在任何 `git commit` 都會失敗。因此**已提升到 P0 第 5 步**（`uv run pre-commit install`），詳見 P0 的第一個 ⚠️ 區塊。`core.hooksPath` 已查過三個層級都未設定，不需處理。
- **這輪規劃不要跑 `ruff --fix`**：`.pre-commit-config.yaml` 現有的 ruff hook 帶 `--fix`，會直接改檔案。P0-P6 都還在「計劃書、待核准」階段，真的動手時要把「ruff 自動修正的差異」跟「唯讀 CI 檢查」分開記錄，不要把 hook 順手改掉的東西誤認成手動修正的一部分。

---

## P3 — CI 與流程防呆（稽核優先2）

`.github/workflows/test.yml` 是兩個 repo 裡唯一的 workflow（根倉庫**沒有任何 CI**）。

1. **加 macOS runner**：`:62` `os: [ubuntu-latest]` → `[ubuntu-latest, macos-latest]`。job 名稱 `:57` 要改成 `Test (${{ matrix.os }} / Python ${{ matrix.python-version }})`，否則兩個 OS 的 job 名稱會撞在一起。Codecov/artifact 步驟 `:105,:114` 已經有 `matrix.os == 'ubuntu-latest'` 的 gate，不用動。
   > 這一步要排在 P1 之後 —— 硬編的 `/home/runner/work/...` 在 macOS runner 上是錯的，先修 resolver 才有意義。
2. **新增 `pre-commit` job**：`uv run pre-commit run --all-files`。現在 pre-commit 完全沒在 CI 跑，CI 只手動重複了 ruff 那兩個 hook，`check-merge-conflict`／`check-yaml`／`detect-private-key` 這些從來沒有在 PR 上被執行過 —— 這正是「衝突標記沒清乾淨直接 push」能連續兩輪發生的原因。
3. **新增路徑守門 hook**：local pre-commit hook + CI 步驟，只要新增行在 `docs/handoff/` 以外出現 `/home/elan` 或 `/Users/kennykang` 就失敗。這是唯一能機制性阻止路徑回歸的東西。
4. **根倉庫加一個最小 workflow**：只跑上面第 3 條的路徑守門 + markdown 連結檢查。
5. **Branch protection**（兩個 repo，實測目前都是 404）：
   ```
   gh api -X PUT repos/kcf7012/fa-report-refactor/branches/main/protection ...
   ```
   要求：PR 才能合併、required status checks = `Lint & Format` + `Test (ubuntu-latest / Python 3.10)` + `Test (macos-latest / Python 3.10)` + `Pre-commit`、`strict: true`（分支需與 main 同步）。
   > ⚠️ 這會改變現有「本機 merge 直接 push main」的習慣。設定完之後 Kenny 自己 push 也會被擋，一定要走 PR。
   > ⚠️ **（補：來自 Codex 版本規劃書的提醒）Reviewer 安排要先確認**：如果 branch protection 要求「至少一位 reviewer 核准才能合併」，而目前這兩個 repo 實際上只有 Kenny 一人維護，設下去會變成**沒有人能核准、也就沒有人能合併任何 PR**（自己不能 approve 自己的 PR）。執行這一步前先確認：(a) 是否要找第二個帳號/協作者當 reviewer，或 (b) 只要求 CI 檢查通過、不強制 reviewer 核准（`required_pull_request_reviews` 留空或設 `required_approving_review_count: 0`）。不要設成無人能合併的狀態。
   >
   > 我這邊補一層前提：**這一步目前根本執行不了** —— `gh` 在這台 Mac 上是 `KennyKang7012`，對 `kcf7012/*` 是 `admin=false push=false`，設 branch protection 需要 admin。P0 的帳號問題沒解決之前，P3 第 5 步與整個 P6 都做不了。

**建議設定值**（帳號問題解決後）：

| 欄位 | 值 | 理由 |
|---|---|---|
| `required_status_checks.contexts` | `Lint & Format`、`Test (ubuntu-latest / Python 3.10)`、`Test (macos-latest / Python 3.10)`、`Pre-commit` | 對應 P3 第 1、2 步改完後的 job 名稱 |
| `required_status_checks.strict` | `true` | 分支需與 main 同步後才能合併 |
| `required_pull_request_reviews.required_approving_review_count` | **`0`** | 單人維護，設 1 會鎖死自己（Codex 的提醒） |
| `enforce_admins` | `true` | 若設 `false`，admin 可以繞過全部規則 —— 那就退回「靠記得」，等於沒做 |
| `allow_force_pushes` / `allow_deletions` | `false` | — |

> `required_approving_review_count: 0` 仍然強制「必須開 PR、CI 必須綠」才能合併，這已經能擋掉連兩輪發生的「衝突標記沒清乾淨直接 push main」。**reviewer 那一項是唯一因為單人維護而必須放棄的**，要在文件裡誠實寫明這個取捨，不要宣稱流程防呆已經完整。

---

## P4 — 稽核優先1：`get_title_placeholder()` 結構性缺口

**已複驗屬實。** `src/fa_improver/improvers/_safe_shape.py:145-158`：策略1（`idx == 0`）與策略2（`TITLE`/`CENTER_TITLE`）一旦命中就直接 `return ph`，**完全沒看 `left` 座標**。`TITLE_SAFE_LEFT_INCH = 1.2`（`:109`）只在 `get_or_create_title()` 的 `ph is None` fallback 分支（`:227-243`）才用得到。而 `find_content_layout()`（`src/fa_improver/layout/selector.py:9`）永遠回傳真實 layout，一般公司母片幾乎都提供原生 title placeholder —— 所以防線生效的那條路反而是少數情況。

配套測試 `tests/integration/test_visual_quality.py:271-273` 的 `if shape.is_placeholder: continue` 直接跳過這個情境。

**修法（順序不能顛倒）**：

1. **先量測，再定值。** 稽核明確警告「不要為了讓既有測試通過而反推數值」（上一輪 `TITLE_SAFE_LEFT_INCH - 0.2` = 1.0 就是這樣選出來的，緩衝只剩 0.03 in）。先寫一次性腳本，從 `report/` 的三份真實客戶 pptx 量出母片左上裝飾的實際 x 範圍，把結果寫進 `_safe_shape.py` 常數區的 docstring。再據此決定 `TITLE_SAFE_LEFT_INCH`（目前 1.2）與 body margin（目前 1.0，17 處引用 `TITLE_SAFE_LEFT_INCH - 0.2`）該不該調。

2. **加 `_effective_left(ph)` helper。** 關鍵細節：slide 上的 placeholder 常常 `left is None`（幾何繼承自 layout），必須往 layout（再往 master）用相同 `idx` 找回實際座標，否則檢查會全部誤判為安全。

3. **在策略1／策略2 命中後加安全檢查。** 建議 **把原生 placeholder 往右移**（`ph.left = Inches(TITLE_SAFE_LEFT_INCH)`，同步縮 width 不讓它超出投影片），而不是 `return None` 走 safe_textbox —— 因為移動 placeholder 保留母片的字型/顏色樣式，符合本專案「母片保護是最高優先」的原則。只有在移動後寬度小於合理下限時才降級成 safe_textbox。

   > 這是寫入 **slide 層級**的 `<a:xfrm>`，不動 master/layout，`tests/unit/test_master_protection.py` 不會被破壞 —— 但這條要在 PR 裡明確驗證。

4. **修測試。** 拿掉 `test_visual_quality.py:271-273` 的 `if shape.is_placeholder: continue`，改成對 placeholder 也用 `_effective_left()` 檢查。再加一個**直接指名** `synthetic_C_decoration.pptx` 的測試（不透過 `FIXTURE_FALLBACKS` 的 MS stem 對應），斷言每張新投影片的 title `left >= TITLE_SAFE_LEFT_INCH`。

   > 現有 fixture 已經是好素材：`scripts/build_synthetic_fixtures.py:167-179` 在母片放了 `left=0, top=0, w=1.0in, h=0.5in` 的裝飾矩形，實測 4 張新投影片的 title 全部落在 `left=0.5, top=0.30`，幾何上確實重疊。問題只在程式碼與測試都沒走到這條路。

5. **驗證修好了**：修改前先跑一次新測試確認它**紅**（能重現漏洞），修完再跑確認轉綠。這是稽核第 7 節「不要只看新加的測試通過就認為安全機制生效」的直接對策。

---

## P5 — 文件（只改「活的」，歷史 handoff 保留）

### 要改的檔案（實測命中數）

| 檔案                                            | `/home/elan`                                                                     | 其他要改的                                                                                                                   |
| ----------------------------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `AGENTS.md`                                     | 7 處（`:5,33,43,50,53,268,280`；其中 `:50,53,268,280` 是可直接複製的 `cd` 指令） | `:7` 日期、`:20` uv 版本、`:22` 覆蓋率 90→85 + 測試數、`:23/:95` black 已停用、`:326` `.venv/bin/python`、`:379` 「85%→90%」 |
| `README.md`（根）                               | 3 處（`:90,91,97`）                                                              | `:7` coverage badge 90%、`:116` 版本表最新列還是 v3.1.3、`:153` 最後更新日期                                                 |
| `docs/README.md`                                | 2 處（`:66,100`）                                                                | `:51,:179` 版本還寫 v3.1.3                                                                                                   |
| `docs/USER_GUIDE.md`                            | `:817` 敘述性（可留）                                                            | `:784` 覆蓋率 90→85                                                                                                          |
| `docs/TESTING.md`                               | 0                                                                                | `:17-29` `.venv/bin/python`、`:212-242` `../venv/bin/python`                                                                 |
| `SKILL.md`                                      | 0                                                                                | `:104,107` `.venv/bin/...`                                                                                                   |
| skill `README.md`                               | 0                                                                                | `:7` 版本停在 v3.1.3、`:11,163` 覆蓋率、`:203,205` black、`:24,155-164` `.venv/bin`                                          |
| `docs/08_uv_integration.md`                     | 0                                                                                | `:77,98,356` black、`:257` ruff `rev: v0.1.6`                                                                                |
| `docs/02_refactor_plan.md`                      | 0                                                                                | `:496`「pre-commit 4 大類」實際只有 3 類                                                                                     |
| `references/virtual-environment-guide.md`       | 0                                                                                | `:4` uv 版本                                                                                                                 |
| `.agents/skills/handoff-doc-generator/SKILL.md` | `:167` 範本行                                                                    | —                                                                                                                            |

路徑一律改成**相對於倉庫根**的寫法（`<PROJECT_ROOT>/docs/`、`cd .agents/skills/fa-report-improvement`），不要換成另一組寫死的絕對路徑。

**AGENTS.md 另加一節「跨平台路徑規則」**（呼應你的第 6 點）：禁止任何絕對路徑字面值、一律用 `src/fa_improver/paths.py`、指令一律 `uv run` 不用 `.venv/bin/...`、新文件用 `<PROJECT_ROOT>` 佔位。

### 稽核 SOP 文件

`docs/handoff/2026-09-03-next-audit-cycle-planning.md`（這份是**活的 SOP**，不是歷史紀錄）：

- **`:77` `git checkout v3.1.4` → `v3.1.5`** —— 這行連續兩輪被點名沒改，照做的人會完全看不到修正
- `:78-79` 同時 `pip install -e` 又 `uv sync`，重複且會衝突 → 只留 `uv sync --locked --extra dev --extra llm`
- `:104` 的檢查題目「是否還有寫死 `/home/elan`」→ 改成泛用的「是否有任何絕對路徑字面值」
- §8 的自動截圖比對評估理由 #3 綁死 WSL/Windows 渲染差異 → 補上 macOS 情境
- `:299,302` 寫死 `/tmp` → `tempfile.gettempdir()`

### 覆蓋率數字

實測與 CI log 都是 **85%**，但有 **12 處寫 90%**：`AGENTS.md:22,379`、根 `README.md:7`(badge)、`docs/00_executive_summary.md:14`、`docs/USER_GUIDE.md:784`、`SKILL.md:38`、skill `README.md:11,163`、`CHANGELOG.md:181,271,456,470`。
`AGENTS.md` 甚至自己打架：`:22` 說 90%，`:258` 說 85%。

**做法**：P0 重建環境後跑一次 `uv run pytest tests/ -q` 取得**當下真實數字**，用那個數字統一修正上述各處（不要照抄 85%，要以實跑為準）。`docs/00_executive_summary.md:14` 的「219 個測試」與 `AGENTS.md:22` 的「233」也一併對齊。

### 驗收頁 HTML（稽核連兩輪點名）

兩個頁面，共 109 張 `<img>`，全部寫死 `/home/elan/...`，且引用的 PNG 被根 `.gitignore:93`（`report/*_improved_visual/`）排除 —— 別人完全打不開。

| 頁面                                                            | img | PNG 實況                                                                                                                                      |
| --------------------------------------------------------------- | --- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/handoff/screenshots/v3.1.4-regression-visual-review.html` | 53  | **檔案都在**（`report/{260811,MS,N160JCN}_v3_final_improved_visual/`，15+18+20 完全對得上），只差把 `/home/elan/fa-report-refactor/` 前綴拿掉 |
| `docs/handoff/screenshots/v3.1.4-visual-review/index.html`      | 56  | **兩個獨立 bug**：除了路徑前綴，HTML 用 3 位數 `slide-001.png`，磁碟上是 2 位數 `slide-01.png` —— 這頁在任何機器上從來沒有正常顯示過          |

**做法**：把 109 張 PNG **重新壓縮**（現在 ~500KB/張、共 9.1MB @100 DPI；降到 ~150KB/張約 2.5MB）後複製進 `docs/handoff/screenshots/v3.1.4-regression/` 與 `.../v3.1.4-review/`，HTML 改成純相對路徑（`v3.1.4-regression/slide-01.png`）。這樣 `file://` 開得起來、GitHub 上也看得到、任何人都能驗證。順便修掉 index.html 的 zero-padding。

> 壓縮是必要的：`.pre-commit-config.yaml` 的 `check-added-large-files --maxkb=500` 會擋下部分原始檔（最大那張 499KB 已經貼線）。
> 根 `.gitignore:100-102` 那段註解宣稱 screenshots 是刻意 commit 的，但四行之後的 `:93` 就把實際引用的 109 張排除掉 —— 註解要一起修正。

---

## P6 — 版本收尾：發 v3.1.5

1. 三處版號 `3.1.4` → `3.1.5`：`pyproject.toml:3`、`src/fa_improver/__init__.py:3`、`SKILL.md:4`
2. `docs/USER_GUIDE.md:823` 定義的「三處必須一致」規則**漏掉了四個 README** —— 這正是它們一路漂移到 v3.1.3 的原因。規則要擴充成六處，並把 skill `README.md:7`、根 `README.md:116,153`、`docs/README.md:51,179` 補上。
3. `CHANGELOG.md`：
   - 新增 `## [3.1.5]` 章節
   - 現有最新章節是 `## [3.1.4-regression-fix]`(`:8`)，這個版號字串在**其他檔案都不存在**、也沒有 tag → 併入 v3.1.5 的說明或標註為 unreleased
   - 章節順序目前非單調（3.1.4-regression-fix → 3.1.4 → 3.1.3 → 3.1.2 → 3.1.0 → 3.0.0 → 2.3.0 → **3.0.1** → **3.1.1**）→ 重排
   - **修標籤表 `:804-812`**：`gh api` 實測 v3.1.0/v3.1.2/v3.1.3 的 GitHub Release 全部 404，表格卻都標 ✅ → 改成 ❌。只有 v3.1.4 是真的 Release（且指向修正前的 `5cb68a4`），這點要在表格備註寫清楚
4. `git tag v3.1.5` + push + `gh release create v3.1.5`（技能包倉庫）
5. `v3.0.0` / `v3.0.1` 兩個本地 tag 從未 push（SOP 文件 §4 backlog #4）→ 決定要 push 還是在表格誠實標「僅本地」
6. **Codecov token**：`.github/workflows/test.yml:109` `fail_ci_if_error: false` 把失敗吞掉，覆蓋率追蹤事實上是壞的。補 `CODECOV_TOKEN` secret 之後把它改成 `true`；若不打算補，就把整個 Codecov 步驟拿掉，不要留一個假的綠燈

---

## P7 — 輸出檔相容性：PowerPoint / Google Slides

前六階段都在處理「開發環境跨平台」。這一階段處理的是另一件事：**產出的 pptx 在不同簡報軟體裡是不是還長得對**。

### 已量到的事實

檔案格式本身沒問題 —— 純標準 OOXML，只用 `add_textbox` / `add_table` / preset 幾何（`MSO_SHAPE.RECTANGLE` / `ROUNDED_RECTANGLE` / `RIGHT_ARROW` / `OVAL`，`visuals/base.py`），無巨集、無嵌入物件。三個平台都開得起來。

風險在字型與版面。從真實客戶母片量到：

| 來源                               | 字型                                                                      | 平台                                       |
| ---------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------ |
| theme1.xml `majorFont`/`minorFont` | `latin="Arial"` / `"Verdana"`、**`ea="新細明體"`**                        | 新細明體為 Windows 專屬                    |
| 投影片內明確指定                   | `標楷體`×160、`新細明體`×119、`Wingdings`×125、`文鼎粗黑`×4、`DFKai-SB`×3 | 標楷體／文鼎粗黑／DFKai-SB 皆 Windows 專屬 |

工具注入的新文字**從不設 `font.name`**（刻意繼承母片主題，符合母片保護原則），所以會跟著一起被替代。

### P7.1 修 `orient` 的不合法值

`src/fa_improver/improvers/_safe_shape.py:212` 寫入 `ph_elem.set("orient", "horiz")`，但 OOXML `ST_Direction` 的合法值是 **`horz`** / `vert`（客戶母片 layout 內實際就是 `orient="vert"`）。

- 先驗證：確認 schema 合法值，並用最小 repro 產一個觸發此分支的檔案，在 PowerPoint 開看有無「需要修復」提示
- 確認後改 `"horiz"` → `"horz"`，補一個單元測試斷言寫出的屬性值
- 已檢查現有產出檔（`report/260811_v3_final_improved.pptx`）：此分支未被觸發（該 deck 的 layout 名稱含「直排」，`get_body_placeholder():192` 提早 `return None`），所以問題尚未實際發生 —— 是潛在缺陷，不是現行 bug

### P7.2 OOXML 合規測試（可自動化、進 CI、不需 Windows）

新增 `tests/integration/test_ooxml_compliance.py`，對改善後的 pptx 用 `zipfile` + `lxml` 檢查：

1. **round-trip** —— 產出檔能被 python-pptx 重新開啟
2. **`[Content_Types].xml`** —— 每個 part 都有對應的 Default/Override
3. **無孤兒 relationship** —— 每個 `*.rels` 的 target 檔案實際存在於 zip 內
4. **shape id 唯一** —— 同一 `spTree` 內 `<p:cNvPr id>` 不重複（這是 PowerPoint 跳修復提示最常見的原因，而 `clean_unused_placeholders()` 會從 spTree 移除 sp 之後再 `add_textbox`）
5. **移除 placeholder 沒留殘骸** —— `_safe_shape.py:100-101` 的 `sp.getparent().remove(sp)` 之後，該 sp 的 rel 不應殘留
6. **幾何完整** —— 新增的每個 shape 都有 `<a:xfrm>` 含 `<a:off>` 與 `<a:ext>`
7. **屬性值合法** —— `<p:ph orient>` 只能是 `horz`/`vert`（涵蓋 P7.1）

這組測試在 ubuntu 與 macOS runner 上都能跑，是唯一能持續守住相容性的機制。

### P7.3 Google Slides 自動驗收

流程：上傳 pptx → 用 Chrome 開 Google Slides → 逐頁截圖 → 與 LibreOffice 截圖並列放進驗收頁。

> ⚠️ **保密限制**：`AGENTS.md` §九 明訂 FA 報告含公司機密。**不上傳真實客戶 pptx 到 Google Drive**。
>
> 改用去識別化素材：新增 `synthetic_D_cjk_fonts.pptx`（在 `scripts/build_synthetic_fixtures.py` 內建置），theme 宣告與客戶母片相同的字型（`ea="新細明體"` + 內文用 `標楷體` + `Wingdings` 符號），但內容完全虛構、無 ELAN logo、無客戶名稱。這樣既能重現字型替代風險，又不外洩任何東西。
>
> 現有三份合成 fixture 用的是 python-pptx 內建範本（Calibri），**測不出**這個問題，所以需要新增第四份。

驗收要記錄：字型實際被替代成什麼、字寬變化是否造成溢出、Wingdings 符號是否錯位、表格框線與底色是否保留。

### P7.4 Windows PowerPoint 驗收清單（交給 Kenny 自己開）

真實客戶 pptx 只在你本機／公司環境開。產出一份對照清單，逐項打勾：

- [ ] 開檔時**沒有**「PowerPoint 發現無法讀取的內容／需要修復」提示
- [ ] 新增投影片的 title 沒有被母片左上裝飾擋住（P4 的最終驗證）
- [ ] 所有文字都在文字框內，沒有溢出或被裁切
- [ ] 表格框線、底色、欄寬正常
- [ ] Wingdings 符號（打勾、項目符號）顯示正確
- [ ] 母片 logo、機密等級標示、部門色系完全未變
- [ ] 與同一份檔案的 LibreOffice 截圖對照，記下所有差異

### P7.5 文件化已知限制

- `docs/USER_GUIDE.md` 新增「相容性與已知限制」章節：本工具**以 Windows PowerPoint 為主要目標平台**；Google Slides 與 macOS PowerPoint 會替代 Windows 專屬中文字型（新細明體／標楷體／文鼎粗黑），字寬改變後**可能撐破寫死英吋的文字框**；`tf.auto_size = None`（`_safe_shape.py:53`）關掉了自動縮放，所以溢出會直接可見
- 說明現有測試只斷言 XML 幾何、**不做渲染**，因此抓不到字型替代造成的溢出
- **驗收流程誠實化**：所有既有「視覺驗收截圖」都是 LibreOffice 渲染，要在驗收頁與 SOP 文件明確標註「LibreOffice 渲染 ≠ PowerPoint 渲染 ≠ Google Slides 渲染」，不能再拿 LibreOffice 截圖當作 PowerPoint 呈現正確的證據
- `docs/handoff/2026-09-03-next-audit-cycle-planning.md` §8（自動截圖比對 backlog）補上「三種渲染器差異」這一層考量

---

## 驗證

**每一階段都要在兩個平台的心智模型下檢查，但實跑以 macOS + CI(ubuntu/macos) 為準。**

| #   | 指令                                                                                                                                                                       | 通過條件                                                                                 |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 1   | `uv sync --locked --extra dev --extra llm`                                                                                                                                 | 乾淨完成，不重新解析                                                                     |
| 2   | `uv run pytest tests/ -q`                                                                                                                                                  | 233+ passed；**skip 數不得增加**（增加代表路徑解析又失效了）                             |
| 3   | `uv run pytest tests/unit/test_master_protection.py -v`                                                                                                                    | 全綠（P4 動了 placeholder 幾何，這關最重要）                                             |
| 4   | `uv run python -c "from fa_improver.paths import find_project_root; print(find_project_root())"`                                                                           | 印出 `/Users/kennykang/Desktop/VibeProj/Claude/fa-report-refactor`（**不是**技能包目錄） |
| 5   | `uv run pytest tests/integration/ -q -s \| grep -i synthetic`                                                                                                              | 確認 16 個視覺回歸測試跑的是**真實客戶 pptx**，不是合成 fixture                          |
| 6   | P4 新測試：修改前跑 → 修改後跑                                                                                                                                             | 修改前**必須紅**，修改後綠                                                               |
| 7   | `uv run ruff check src/ tests/ scripts/ && uv run ruff format --check src/ tests/ scripts/`                                                                                | 全過                                                                                     |
| 8   | `uv run pre-commit run --all-files`                                                                                                                                        | 全過（含新的路徑守門 hook）                                                              |
| 9   | `git grep -n "/home/elan" -- . ':!docs/handoff/'`（兩個 repo）                                                                                                             | 零命中                                                                                   |
| 10  | 瀏覽器開兩個驗收頁 HTML                                                                                                                                                    | 109 張圖全部顯示                                                                         |
| 11  | 開 PR → 看 CI                                                                                                                                                              | ubuntu × 3 + macOS × 3 + Lint + Pre-commit 全綠                                          |
| 12  | 直接 `git push origin main`                                                                                                                                                | **被 branch protection 擋下**（證明防呆生效）                                            |
| 13  | `uv run python -m fa_improver report/260811_Kobo_ZHT_RA6080_SPcomFailI.pptx --eval report/fa_report_260811_Kobo_ZHT_RA6080_SPcomFailI.json --output <tmp>/v315_check.pptx` | 產出成功，且新投影片 title `left >= 1.2 in`                                              |
| 14  | `uv run pytest tests/integration/test_ooxml_compliance.py -v`                                                                                                              | 全綠（round-trip、無孤兒 rel、shape id 唯一、`orient` 值合法）                           |
| 15  | 第 13 步的產出檔用 **Windows PowerPoint** 開                                                                                                                               | 無「需要修復」提示；P7.4 清單七項全打勾                                                  |
| 16  | `synthetic_D_cjk_fonts.pptx` 的改善產出上傳 Google Slides                                                                                                                  | 開得起來；記錄字型替代結果與是否溢出（此步只用去識別化素材）                             |

---

## 明確不做

- **Windows 原生開發支援**（非 WSL）—— 不加 `windows-latest` runner、不處理 `.venv\Scripts\`、不處理 cp950。但選用的寫法（`uv run`、`os.pathsep`、`pathlib`）天然不阻擋日後補上
  > 這跟 P7 是兩件事：P7 處理「產出檔在 Windows PowerPoint 開得對不對」，那個**有做**；這裡不做的是「開發環境跑在 Windows 原生」
- **改字型與文字溢出保護** —— 不給新建 textbox 明確指定字型、不做字數估算自動縮字級，維持「完全繼承母片樣式」的原則，改成在 P7.5 誠實記錄為已知限制。若 P7.3 的 Google Slides 驗收顯示溢出嚴重，再另開一輪處理
- **改寫 `docs/handoff/` 的 20+ 份歷史交接文件** —— 那是當時環境的事實紀錄
- **自動截圖比對**（SOP §8 的 backlog）—— 維持「v3.1.5 不做」的原判斷
- **不動已發布的 v3.1.4 tag/Release** —— 歷史保持誠實，新東西進 v3.1.5

## 風險

1. **P4 移動原生 placeholder 可能影響母片保護測試** —— 理論上寫的是 slide 層級 `<a:xfrm>`，不碰 master/layout，但這是本專案的最高優先原則，PR 裡要單獨驗證並在描述中說明
2. **Branch protection 會擋掉 Kenny 自己的直接 push** —— 這是刻意的，但要先確認你接受改用 PR 流程。另外因為單人維護，`required_approving_review_count` 只能設 0（見 P3），「至少一次 review」這條稽核建議這輪**無法完整落實**，要誠實記錄而不是假裝做到了
3. **GitHub 帳號權限未解決前，P3 第 5 步與整個 P6 都是死的** —— 這台 Mac 的 `gh`/keychain 都是 `KennyKang7012`，對 `kcf7012/*` 唯讀（實測 `git push` 403）。這是排在 P0 的前置決策，不是執行到後面再說
4. **字型替代造成的溢出，這輪只量不修** —— 母片實際用的新細明體／標楷體／文鼎粗黑／DFKai-SB 都是 Windows 專屬，在 Google Slides 與 macOS PowerPoint 一定會被替代。版面全是寫死英吋且 `tf.auto_size = None` 關掉了自動縮放，字寬一變就可能溢出。現有測試只斷言 XML 幾何、不看實際渲染，**抓不到這件事**。P7.3 會量出嚴重程度，但這輪不改 improver 行為
5. **P7.3 的保密邊界** —— 絕不上傳真實客戶 FA 報告到 Google Drive（`AGENTS.md` §九）。只用新建的去識別化 `synthetic_D_cjk_fonts.pptx`；真實檔的 PowerPoint 驗收由 Kenny 在自己環境做
6. **`uv self update` 需要網路**，且升版後 `uv lock` 重產可能小幅變動依賴版本 → 重產後要完整跑一次測試再 commit
