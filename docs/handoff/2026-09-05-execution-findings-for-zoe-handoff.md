# Handoff：P0-P1 執行中的兩個發現 — 請柔伊複核

> 撰寫者：Claude Code（Kenny 的 macOS 環境）
> 日期：2026-09-05
> 狀態：**兩點都已實測，但都需要獨立複核**
> 上游：`docs/handoff/2026-09-05-cross-platform-migration-plan-handoff.md`（P0-P7 計劃書）
> 執行分支：技能包倉庫 `v3.1.5-cross-platform`（commit `7596ef2`、`e2168d5`、`cfdcac3`）

## 這份文件的定位

計劃書 P0、P1 已執行完畢。過程中撞到兩件**計劃書沒預料到、且會影響後續判斷**的事。
第 1 點會讓 P5 照著做就做錯方向；第 2 點是環境層面的隱形故障，Claude Code 排查到一個
段落但無法定案，需要在 Kenny 的機器上繼續查。

兩點的原始證據都寫在下面，包含「已經排除了什麼」，避免重複勞動。

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

### 請 Kenny / 柔伊接著查的方向

1. `ls -lO` 看旗標出現的時間分布，對照 `fs_usage` 或 `sudo fs_usage -w -f filesys | grep chflags`
   找出是哪個 process 在呼叫 `chflags`。
2. 檢查有無公司派送的 MDM / EDR 代理（`ps aux`、`launchctl list`、`/Library/LaunchDaemons/`）。
3. 確認是否只影響 `~/Desktop/VibeProj/` 底下，還是全機。（目前只在專案樹觀察到，
   `~/.cache/uv/` 是乾淨的，所以**不是全機無差別**。）

### 應急處理

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
