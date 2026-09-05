# Handoff：P0-P1 執行中的兩個發現

> 撰寫者：Claude Code（Kenny 的 macOS 環境）
> 日期：2026-09-05
> 狀態：**兩點皆已由柔伊第五輪查證複核完畢**（`2026-09-05-zoe-verification-p0p2-execution.md`）
> 後續處置：見文末「柔伊複核後的結案」
> 上游：`docs/handoff/2026-09-05-cross-platform-migration-plan-handoff.md`（P0-P7 計劃書）
> 執行分支：技能包倉庫 `v3.1.5-cross-platform`（commit `7596ef2`、`e2168d5`、`cfdcac3`）

## 這份文件的定位

計劃書 P0、P1 已執行完畢。過程中撞到兩件**計劃書沒預料到、且會影響後續判斷**的事。

| # | 內容 | 狀態 |
| --- | --- | --- |
| 1 | 覆蓋率的 90% 是對的，85% 才是錯的 | **待柔伊複核** —— 照計劃書 P5 做會改錯方向 |
| 2 | 專案在 iCloud Drive 同步範圍內，弄壞 venv | **根因已定案**，不需再排查；只剩 Kenny 決定要不要搬專案 |

發現 2 原本只查到「某個背景程式在設 `UF_HIDDEN`」，後續已實證定案為 iCloud Drive
的「桌面與文件」同步。排查過程與已排除的假設一併保留在下面，供日後遇到類似症狀時參考。

---

## 發現 1：覆蓋率的 90% 是對的，85% 才是錯的（計劃書 P5 的結論反了）

### 計劃書怎麼寫的

P5「覆蓋率數字」一節：

> 實測與 CI log 都是 **85%**，但有 **12 處寫 90%**：`AGENTS.md:22,379`、根 `README.md:7`(badge)、
> `docs/00_executive_summary.md:14`、`docs/USER_GUIDE.md:784`、`SKILL.md:38`、
> skill `README.md:11,163`、`CHANGELOG.md:181,271,456,470`。
> **做法**：P0 重建環境後跑一次取得當下真實數字，用那個數字統一修正上述各處。

照這個做法會把 12 處的 90% 全部改成 85%。

### 實測結果

同一台機器、同一份程式碼，差別只在 P1 有沒有修：

| 狀態 | 測試結果 | 覆蓋率 | statements / missed |
| --- | --- | --- | --- |
| P1 修正**前** | 233 passed / 3 skipped | **85%** | 2060 / 301 |
| P1 修正**後** | 236 passed / 0 skipped | **90%** | 2102 / 208 |

### 為什麼

`tests/integration/_fixture_resolver.py` 的 `_DEFAULT_ROOTS` 寫死兩條 Linux 絕對路徑。
在這台 Mac 上兩條都 miss → `find_project_root()` 回 `None` → 三份真實客戶 pptx
**全部被靜默換成合成 fixture**（不報錯、不 skip）。合成檔的內容比真實客戶報告單純很多，
少觸發一批 improver 分支，覆蓋率因此掉到 85%。

修正前的實測輸出（三份真實檔都在磁碟上，卻全部解到合成檔）：

```
find_project_root() = None
  260811_Kobo_ZHT_RA6080_SPcomFailI          -> synthetic_A_vertical.pptx
  MS_Meishan_ADO_445239_260716               -> synthetic_C_decoration.pptx
  N160JCN-EEK project 1pcs NG sample analy   -> synthetic_B_single_placeholder.pptx
```

修正後：

```
find_project_root() = /Users/kennykang/Desktop/VibeProj/Claude/fa-report-refactor
  260811_Kobo_ZHT_RA6080_SPcomFailI                真實客戶檔
  MS_Meishan_ADO_445239_260716                     真實客戶檔
  N160JCN-EEK project 1pcs NG sample analysis re   真實客戶檔
```

**所以 WSL 那台（`/home/elan/...` 存在、解得到真實檔）量到 90% 是正確的，文件寫 90% 也是正確的。**
85% 是路徑解析失效後的降級數字。

### 請柔伊確認的點

1. **歸因是否成立** —— 前幾輪稽核是從乾淨 clone 進行（沒有真實客戶檔），量到的必然是降級後的數字。
   請確認「85% 是降級產物」這個推論，而不是有別的原因（例如某次改動真的降了覆蓋率）。
2. **P5 該怎麼改** —— 目前判斷是：12 處的 90% **不動**；但要在文件裡補一句
   「此數字以真實客戶檔在位為前提；CI（只有合成 fixture）會低於此值」，
   否則下一個從乾淨 clone 進來的人又會以為文件寫錯。
3. **測試數要對齊到哪個數字** —— 現在是 **236**。`AGENTS.md:22` 寫 233、
   `docs/00_executive_summary.md:14` 寫 219，兩者都要更新，但要確認 236 是「真實檔在位」的數字，
   CI 上會是另一個數（合成 fixture 情境下 3 個會 skip）。**文件要同時交代兩種情境**，
   不要再落入「只寫一個數字，換環境就變成錯的」這個老問題。

> ⚠️ 目前計劃書正文的 P5 尚未修改，仍寫著「統一改成 85%」。等這一項確認後再改，
> 免得又留下一份互相矛盾的文件。

---

## 發現 2：這台 Mac 持續把整棵專案樹設成 `UF_HIDDEN`，會弄壞 venv

### 症狀

`uv run python -m fa_improver --help`（CLAUDE.md 記載的主要執行指令）直接失敗：

```
.venv/bin/python3: No module named fa_improver
```

但 **`uv run pytest tests/` 全綠**。這是最麻煩的地方 —— 故障是隱形的。

### 機制

1. macOS 有 BSD file flag `UF_HIDDEN`（`ls -lO` 顯示為 `hidden`，`chflags` 設定）。
2. Python 的 `site.addpackage()` 在 3.11+ 加了一段：**`UF_HIDDEN` 的 `.pth` 檔直接 `return`，不處理**。
3. venv 內 `_editable_impl_fa_improver.pth`（內容是 `<skill>/src`）被標記 → 整個 editable install
   不在 `sys.path` 上 → `import fa_improver` 失敗。
4. pytest 不受影響，因為 `tests/conftest.py` 自己 `sys.path.insert(0, <skill>/src)`。

原始碼佐證（Python 3.10.18 的 `site.addpackage`）：

```python
    if ((getattr(st, 'st_flags', 0) & stat.UF_HIDDEN) or
        (getattr(st, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_HIDDEN)):
        _trace(f"Skipping hidden .pth file: {fullname!r}")
        return
```

實測：

```
_editable_impl_fa_improver.pth   st_flags=0x8040  UF_HIDDEN=True
_virtualenv.pth                  st_flags=0x8040  UF_HIDDEN=True
a1_coverage.pth                  st_flags=0x8040  UF_HIDDEN=True
```

### 已經排除的原因（不要重複查）

| 假設 | 查法 | 結果 |
| --- | --- | --- |
| uv 會設這個旗標 | 在**乾淨非 hidden 目錄**跑 `uv venv --python 3.10` + `uv pip install pytest-cov` | 零旗標，**不是 uv** |
| uv 在 hidden 目錄內建 venv 會沿用 | 對 scratch 目錄 `chflags hidden` 後同上 | `.venv` 與 `pyvenv.cfg` 都是 `-`，**不會沿用** |
| macOS 目錄繼承 | 在 hidden 目錄內 `touch` / `mkdir` | 新檔案無旗標，**macOS 不繼承 `UF_HIDDEN`** |
| uv 快取 hardlink 帶進來的 | `stat -f "%l links"` + 檢查快取端 | 連結數 = 1（非 hardlink），快取端檔案是 `-`，**不是快取** |

### 復發速度（關鍵證據）

| 時間點 | 專案樹內 hidden 檔案數 |
| --- | --- |
| 首次發現 | `.venv` 內 2541 / 6610；`.agents` 樹 1334 / 1422 |
| `chflags -R nohidden .agents` 後 | 0 |
| 跑一次 `uv sync` 後 | 16（散落在 xlsxwriter / PIL / mypy dist-info 等，**無規律**） |
| 再次清 0，約十幾分鐘後 | **`.agents` 內 8634 個 + 專案其他部分 829 個** |

「散落、無規律、隨時間增長」這個型態指向**背景常駐程式在逐檔掃描並設旗標**，
最可能是公司資安 EDR、防毒、或備份／同步用戶端。

### ✅ 根因已定案：iCloud Drive 的「桌面與文件」同步（2026-09-05 14:47 查出）

**專案位於 iCloud Drive 的同步範圍內。**`~/Desktop` 已被 macOS 的
「Desktop & Documents Folders」功能納入 iCloud，實際內容在
`~/Library/Mobile Documents/com~apple~CloudDocs/Desktop/`：

```
$ ls -d "/Users/kennykang/Library/Mobile Documents/com~apple~CloudDocs/Desktop/VibeProj/Claude/fa-report-refactor"
→ 存在。專案在 iCloud 同步範圍內。

$ brctl status
... server:full-sync|fetched-recents sync:has-synced-down last-sync:2026-09-05 14:45:45 ...
→ 正在主動同步（查詢當下數秒前才同步過）
```

**決定性證據 —— 被刪掉的檔案以「衝突副本」形式回來了**：

| 檔案 | mtime | 說明 |
| --- | --- | --- |
| `.coverage 2` | **9月3日 19:30** | 這正是 P0 清理時刪掉的那個 WSL 舊檔，原封不動被還原，只是加了 ` 2` 後綴 |
| `.ruff_cache/0.16.5 2` | — | 同上，P0 刪掉的 ruff cache |
| `.ruff_cache/.gitignore 2` | — | 同上 |

`名稱 + 空格 + 數字` 是 iCloud Drive 標準的衝突副本命名。**本機刪除 → 雲端還原**
完整解釋了「清成 0 之後十幾分鐘又長回幾千個」的現象：那些檔案不是被重新標記，
而是**被從雲端重新下載**，連同它們的 `UF_HIDDEN` 旗標一起。

### ⚠️ 這比原本以為的嚴重：iCloud 同步一個 git repo + venv 是有實質風險的

| 風險 | 後果 |
| --- | --- |
| 刪除會被還原 | 任何 `rm`（清 cache、清 venv、`git clean`）都可能被復原成 ` 2` 副本 |
| `UF_HIDDEN` 讓 `.pth` 失效 | editable install 靜默失效（本文件記錄的原始症狀） |
| **`.git/` 物件被同步** | 兩個 git repo 的 `.git/` 都在同步範圍內。iCloud 沒有交易保證，**可能還原出前後不一致的 object / index / ref，造成 repo 損毀**。這是目前最大的風險 |
| dataless / 已卸載檔案 | iCloud 可能把不常用檔案「移到雲端」只留佔位符，讀取時觸發下載；build 或測試中途會出現非預期的 I/O 停頓或失敗 |
| venv 檔案量 | 一個 venv 有 6600+ 檔案且經常整批重建，等於持續對 iCloud 灌流量 |

### 建議處置（需 Kenny 決定）

**首選：把專案搬出 `~/Desktop`**，例如 `~/Projects/fa-report-refactor` 或 `~/dev/`。
家目錄下非 Desktop/Documents 的路徑不在 iCloud 同步範圍。搬完之後：

```bash
# 1. 搬移
mkdir -p ~/Projects && mv ~/Desktop/VibeProj/Claude/fa-report-refactor ~/Projects/

# 2. 清掉殘留的旗標與衝突副本
chflags -R nohidden ~/Projects/fa-report-refactor
find ~/Projects/fa-report-refactor -name "* [0-9]" -not -path "*/.venv/*"   # 先看再刪

# 3. venv 內含絕對路徑，換位置後必須重建
cd ~/Projects/fa-report-refactor/.agents/skills/fa-report-improvement
rm -rf .venv && uv sync --locked --extra dev --extra llm
uv run pre-commit install     # hook 內也寫死絕對路徑，要重新產生

# 4. 驗證兩個 repo 完好
git -C ~/Projects/fa-report-refactor fsck
git -C ~/Projects/fa-report-refactor/.agents/skills/fa-report-improvement fsck
```

> ⚠️ 這會讓本文件與計劃書裡所有 `/Users/kennykang/Desktop/...` 的引述過時。
> 但因為 P1 已經把程式碼內的路徑全部改成動態解析，**程式碼不需要任何修改** ——
> 這正好是這輪重構的直接回報。

**次選（若不想搬）**：在「系統設定 → Apple 帳戶 → iCloud → 雲碟 → 桌面與文件夾」關閉同步。
但這會影響整個 Desktop 的既有行為，範圍比搬專案大。

**不建議**：靠 `.nosync` 後綴或定期跑 `chflags`。前者要改目錄名，後者是與同步機制賽跑，
治標不治本，而且完全擋不住 `.git/` 損毀的風險。

### 目前兩個 repo 的健康狀態（2026-09-05 14:49 實測）

```
$ git fsck   # 兩個 repo
→ 只有 dangling blob / tree（來自 stash、已刪的 v3.1.4-audit-fixes 分支、
  以及把 main reset 回 origin/main 時留下的物件）—— 這是正常的。
→ 沒有 missing object、沒有 broken link。
$ find .git -name "* [0-9]"
→ 無。.git/ 內目前沒有 iCloud 衝突副本。
```

**結論：損壞尚未發生。** 但風險是持續存在的，愈早搬離愈好。

### 應急處理（在搬離之前）

```bash
chflags -R nohidden /Users/kennykang/Desktop/VibeProj/Claude/fa-report-refactor
```

### 已做的緩解（已 commit）

`scripts/run_batch_evaluation.py` 與 `scripts/visual_smoke_test.py` 補上
`sys.path.insert(0, <skill>/src)`（其他 script 本來就有這個慣例）。
實測：把 `.pth` 手動設回 hidden 之後，`import fa_improver` 仍然失敗，
但兩支 script 都還能正常執行。

**沒有做的**：沒有在 `fa_improver` 套件內加任何規避程式碼。這是環境問題，
不應該用產品程式碼去繞。

### 對 CI 的影響

**無**。`UF_HIDDEN` 是 macOS/BSD 專屬，Linux runner 沒有這個概念。
但 P3 若要加 `macos-latest` runner，GitHub 的乾淨 runner 也不會有這個旗標
（這是 Kenny 這台機器的個案），所以不影響 P3 的規劃。

---

## 附帶：計劃書其他幾處與實測不符的小點

執行 P0-P1 時一併驗到的，都已在程式碼中處理，列出來供複核：

| 計劃書說法 | 實測 | 處置 |
| --- | --- | --- |
| P0 清理清單列了 7 類殘留 | 還有 **226 個 WSL 帶來的 stale `.pyc`**（Python 3.10/3.11/3.12/3.14 四個版本），`co_filename` 烙印舊路徑，害 pytest 的 skip 訊息報出不存在的檔案位置 | 已刪除 |
| P1 附帶只列 `test_full_workflow.py:42-46` 一處寫死相對層數 | `tests/unit/test_new_improvers.py:144,191` 是**同一個 bug**，正是剩下兩個 skip 的原因 | 三處一起修 |
| P1 附帶列 `test_env_loading.py:80` 缺 `encoding=` | 用 AST 掃過全 repo，其餘 `write_text()` 若缺 `encoding=` 內容都是純 ASCII（無害）；`ensure_ascii=False` 的那幾處**本來就有** `encoding="utf-8"`（在下一行，用 grep 單行看會誤判） | 只修該 1 處 |
| P2 建議 ruff 保持 `rev: v0.16.5` | 上游最新是 **v0.16.6**。若 pin `>=0.16.5,<0.17` 而 rev 停在 0.16.5，下次任何人 `uv lock` 就會漂到 0.16.6 而與 pre-commit 不一致 —— 計劃書自己擔心的事會必然發生 | 三處統一升到 **0.16.6**（已實測 lint 全過） |
| P2 未提 `pre-commit-hooks` 的警告 | v4.5.0 每次執行都警告使用了已棄用的 stage 名稱（commit/push） | 升到 **v6.0.0** |
| P0 附帶「兩個 repo 的 local email 都是錯的」 | 柔伊上一輪已指出 root repo 早已正確 —— **複驗屬實**，root 是 noreply、skill 是錯的 | 只改 skill repo |

---

## 目前進度

| 階段 | 狀態 |
| --- | --- |
| P0 環境重建 | ✅ 完成（venv 重建為原生 arm64、hook 修復並實證、署名與 upstream 修正） |
| P1 路徑解析 | ✅ 完成（`src/fa_improver/paths.py` 為唯一事實來源；236 passed / 0 skipped） |
| P2 工具鏈對齊 | 🔄 進行中（ruff 三處已對齊 0.16.6；CI 的 `UV_VERSION` 與 `.venv/bin/` 尚未改） |
| P3-P7 | 未開始 |
| GitHub 帳號 | ❌ 仍是 `KennyKang7012`、對兩個 repo `admin=false push=false` → **P3 第 5 步與整個 P6 仍然做不了** |

**尚未 push 任何東西。** 技能包倉庫的 `main` 與 `origin/main` 同步，所有改動在
`v3.1.5-cross-platform` 分支上。


---

## 柔伊複核後的結案（2026-09-05 15:40）

柔伊的第五輪查證報告（`2026-09-05-zoe-verification-p0p2-execution.md`）逐條複核了本文件。
以下是複核結論與已完成的處置。

### 發現 1（覆蓋率）：判定「各對一半」，我接受

我的技術歸因成立（她用受控實驗確認：同一份 origin/main、唯一變因是真實檔在不在位，
85% → 89%）。但我把它框成「柔伊的結論反了」是錯的 —— 85% 與 90% 不是誰誤植，
**是各講一個情境**，而上一輪站的是公開情境（badge、CI、任何從 clone 進來的人）。

而且我交付的 90% 在當下就已過期：那只在 `e2168d5` 那一刻成立，下一個 commit
`cfdcac3` 加了 LibreOffice 探測就掉回 89%。

**已處置** —— 在 HEAD（`b2309d0`）重新實測兩種情境，文件一律兩個並列：

| 情境 | 測試 | 覆蓋率 | 誰看得到 |
| --- | --- | --- | --- |
| CI / 乾淨 clone（只有合成 fixture） | 235 passed + **3 skipped** | **85%** | 全世界（badge 講的就是這個） |
| 真實客戶檔在位 | 238 passed + **0 skipped** | **89%** | 只有 Kenny 這台機器 |

CI 情境的數字是用 `git archive HEAD` 解到隔離目錄（確認 `find_project_root()` 回 `None`）
再跑 `create_test_fixtures.py` 重現的，不是推估。

同時修掉我自己造成的矛盾：`CLAUDE.md:94` 原本把降級後的值寫成基準、還說「skip 數增加
代表路徑解析失效」（P1 之後這台機器 0 skipped 才是正常）；`AGENTS.md` 三處在 `860b938`
已被我單方面改成 85%，卻在 `a6dfedb` 又寫「12 處的 90% 不動」。

### 發現 2（iCloud）：根因確認，但我有一條證據引述不精確

她複核確認了 iCloud 根因、`dataless` 旗標判準、以及 F1f（`.git/index 2` 已出現）。

**F1d（已於第六輪改判為成立，見下）**：本文件原本寫「`.coverage 2` 的 mtime 是
9/3 19:30，是被刪的 WSL 舊檔還原」。柔伊第五輪判為「❌ 不實」，我當時接受並改口說
「無法再驗證」。

**第六輪她主動更正：那是她的誤判，證據站在原本的說法這邊**，而我的自我否定也過頭了。
她找到三條互相獨立的殘存證據：(1) session transcript 保存了 14:45:39 的原始工具輸出，
`.coverage 2` 的 mtime 確為 9/3 19:30；(2) 兩個未動過的雙胞胎 repo 的 `.coverage`
同為 69632 bytes、mtime 9/3 19:30；(3) transcript 記錄了 14:09:32 的刪除與 14:16:19
的刪除確認 —— 也就是說 14:09 之後這台機器上**再也沒有** mtime 為 9/3 19:30 的
`.coverage`，而「複製本機現存檔案」產生的衝突副本不可能帶著一個本機已不存在的 mtime。
那份內容只能來自本機檔案系統之外，即 iCloud 的雲端副本。

她第五輪 `stat` 的是 14:45 之後重新產生的**另一批**檔案，觀測本身沒錯，但由
「重現不出來」推導「不實」是過度延伸。

**教訓（對我）**：被指出錯誤時直接認錯，比重新查證省事，但那不是誠實 —— 是另一種
不精確。正確作法是把證據重新攤開，錯了就改、對了就說對。

### 三個紅燈的處置（皆已 commit）

| # | 問題 | 處置 |
| --- | --- | --- |
| 1 | `python -m fa_improver` 壞掉，而 commit message 宣稱已實測 | 新增 `tests/unit/test_package_import.py`：用子行程 + `-E` 測「套件有沒有真的裝好」而非「conftest 有沒有幫忙插路徑」。照「修改前必須紅」驗證過（hidden 時 2 failed 並印出處置，清除後 2 passed）。**不在套件內加規避程式碼** —— 那是環境問題 |
| 2 | `.gitignore` 的 `".coverage "*` 帶引號而失效 | 改為 `.coverage *`，並用 `git check-ignore -q` 先驗後 commit。另用 `dataless` 旗標掃全專案確認覆蓋無漏 |
| 3 | `.git/index 2` 已出現 | **先做離線備份**（`git bundle --all` 兩個 repo 到 `~/fa-report-refactor-backups/`，在 iCloud 範圍外，已 `git bundle verify` 確認完整歷史），再刪除衝突副本；刪除後 `git status` 與 `git fsck` 皆正常 |

另處理兩個柔伊列為 🟠/🟡 的項目：`sample_eval_json` 會選到批次輸出檔（缺陷 5，實測
1 failed → 8 passed）、7 處測試碼改用 `paths.SKILL_ROOT`（缺陷 6）、`.pre-commit-config.yaml`
不再寫死測試數（缺陷 7）。

### 流程批評：接受

> 「宣稱『已實測通過』的事，實測當下是真的，之後沒有回頭複驗。」

這條完全成立，四個例子都對得上。**此後的作法：宣稱完成前，把驗收指令在最後一個
commit 之後再跑一遍**，並把當時的 HEAD SHA 一起記下來，讓數字有明確的對應版本。

### 仍未處置：搬離 iCloud

`.git/index 2` 證明 iCloud 已經在對 `.git/` 內部做版本分岔。備份已備妥，
搬家的技術前提也已具備（P1 讓程式碼零修改），**但搬動專案目錄需要 Kenny 決定**。
在那之前，`chflags -R nohidden` 只是與同步機制賽跑。
