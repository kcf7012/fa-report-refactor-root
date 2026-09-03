# Handoff：fa-report-refactor v3.1.2/v3.1.3 獨立稽核報告

> 交給：Pi Agent（Windows/WSL 端維護 `fa-report-refactor` 的 agent）
> 稽核者：柔伊（肯尼大 的 Mac 上跑的 Claude Code assistant），透過 `gh repo clone` 遠端稽核，沒有實際碰到 Windows 本機檔案
> 日期：2026-09-02

---

## 🟢 狀態更新：2026-09-03 v3.1.4 已全部修正

**依據**：`docs/handoff/2026-09-03-audit-remediation-plan-handoff.md` 計畫，Kenny 拍板後已全部完成。

### 修正完成（6 項發現中 4 項完整解決）

| # | 發現 | 修法 | 狀態 |
|---|------|------|------|
| 1 | CI 自 08-31 起幾乎每個 commit 都紅燈 | ruff format 修了 + pre-commit 升級 v0.1.9→v0.16.5 | ✅ **Run #23 5/5 jobs success** |
| 2 | 16 個視覺回歸測試在 CI 完全不跑 | 新增 3 個去識別化合成 pptx + `_fixture_resolver.py` | ✅ **CI 真在跑 16 個** |
| 3 | `conftest.py` fixture 陷阱（`Path("")`） | fixture 改回傳 `None` + 13 處呼叫端改判斷 | ✅ **全新 clone 0 fail** |
| 4 | 5-Why 流程圖內容 bug | 新增 `_truncate_step_text()` helper + 重寫 fallback 邏輯 | ✅ **14 個新單元測試全綠** |
| 5 | 版本號 3 處未同步 | `pyproject.toml` + `__init__.py` + `SKILL.md` → 3.1.4 | ✅ **v3.1.4 release 完成** |
| 6 | CHANGELOG 標籤表失真 | 重寫表格（加 GitHub Release 與本地 tag 兩欄） | ✅ **v3.1.4 release 完成** |

### 未來 release 待辦（降級為 backlog）

| # | 項目 | 狀態 |
|---|------|------|
| 稽核 #3 待確認 1 | `_safe_shape.py::get_title_placeholder()` 第 158-170 行死碼 | 🔵 backlog |
| 稽核 #3 待確認 2 | 旋轉/直排偵測只認字串 `"直排"`/`"Vertical"`，遇「垂直/縱向/Portrait」會失效 | 🔵 backlog |
| 稽核 #3 待確認 3 | 視覺驗證覆蓋面窄（`find_content_layout()` 每份報告共用 1 個 layout） | 🔵 backlog |

### 驗證結果

- **本機**：`233 passed, 3 skipped`（基線 219 + 14 新測試）
- **模擬 CI**（`FA_REPORT_PROJECT_ROOT=/nope/1`）：`233 passed, 3 skipped`，16 個視覺回歸測試真在跑（用合成 fixture），0 fail
- **CI Run #21**（合併後）：**5/5 jobs success** 含 Build Distribution
- **CI Run #23**（最終）：**5/5 jobs success**

### v3.1.4 Release

- **GitHub Release**：https://github.com/kcf7012/fa-report-refactor/releases/tag/v3.1.4
- **PR #1**：https://github.com/kcf7012/fa-report-refactor/pull/1
- **Tag**：`v3.1.4` → commit `5cb68a4`
- **改善計畫**：https://github.com/kcf7012/fa-report-refactor-root/blob/main/docs/handoff/2026-09-03-audit-remediation-plan-handoff.md

### 關鍵教訓（已實踐）

> 單元測試全綠 ≠ 改善完成（v3.1.3 handoff 已記）
> 測試在自己機器全綠 ≠ 這個驗證機制對其他人有效（本稽核新揭露）
> 往後每次宣稱「已修正」之前，問：這個結論拿到一台全新環境重跑，還會不會成立？

**稽核本身的目的已達成**——6 項發現完整處理，且測試機制本身也升級（不再依賴本機專屬檔案、不再被舊版 ruff 誤導）。✅ 稽核生命週期閉環。

---

## 1. 目前任務目標

肯尼大 要求對 `fa-report-refactor`（技能包）+ `fa-report-refactor-root`（handoff/文件倉庫）的 v3.1.2、v3.1.3 修正做一次「不採信 handoff 自述、實際查證」的獨立稽核，找出 Pi Agent 自己都沒發現的遺漏或未完成事項。起因：v3.1.1 版本曾被 Pi Agent 誤標「已修正」，實際還有 4 個視覺渲染 bug 沒修，這次要確認 v3.1.2/v3.1.3 是不是又重演了同一種「沒查證就宣稱完成」的模式。

## 2. 已完成內容

派 sub-agent 把兩個 repo `git clone` 到本機（`/tmp/fa-audit/`，稽核用，未清理，柔伊 這邊的機器上），逐條核對：
- 3 個關鍵 commit（`70fb30d` v3.1.2 主修正、`ec25cac` v3.1.3 修正、`b6d52d0` CHANGELOG 補遺）的 diff 內容是否跟 commit message 描述相符
- `_safe_shape.py` 新增的常數與 helper 邏輯是否真的存在、邏輯是否合理
- 7 個 improver 是否全部真的改用新 helper，還是只改了部分
- 測試檔案（`test_visual_quality.py`、`test_slide_rendering.py`）邏輯是否真的檢查實質幾何，還是空洞檢查
- 53 張視覺驗證 PNG 是否真的存在，並實際打開多張目視確認
- CI（GitHub Actions）實際紅綠燈狀態，並用跟 CI 完全相同的流程本地重跑一次驗證測試/覆蓋率數字能否重現
- 全 `src/` 搜尋殘留 TODO/FIXME/XXX/HACK
- CHANGELOG 記載的 tag 列表跟 `git tag -l` / GitHub API 實際回傳是否一致

## 3. 關鍵文件和位置

| 項目 | 位置 |
|---|---|
| 技能包倉庫 | `github.com/kcf7012/fa-report-refactor` |
| 文件倉庫 | `github.com/kcf7012/fa-report-refactor-root` |
| v3.1.2 主修正 commit | `70fb30d` |
| v3.1.3 修正 commit | `ec25cac` |
| CHANGELOG 補遺 commit | `b6d52d0` |
| 最新一次 CI 失敗 run | `33548540009`（對應 commit `b6d52d0`） |
| Safe shape helper | `src/fa_improver/improvers/_safe_shape.py` |
| 死碼位置 | `_safe_shape.py::get_title_placeholder()` 第 168-170 行 |
| 視覺回歸測試（CI 內失效） | `tests/integration/test_slide_rendering.py`（7 個）、`tests/integration/test_visual_quality.py`（9 個），皆寫死 `PROJECT_ROOT = Path("/home/elan/fa-report-refactor")` |
| fixture 陷阱 | `tests/conftest.py`（`sample_pptx`/`sample_eval_json`/`sample_eval_txt`，找不到檔案時回傳 `Path("")` 而非 `None`） |
| 5-Why 內容 bug | `src/fa_improver/improvers/root_cause.py::_add_5why_flow_diagram()` 約行 135-159 |
| 版本號未同步的 3 處 | `pyproject.toml`（`3.1.0`）、`src/fa_improver/__init__.py`（`3.0.0`）、`SKILL.md` frontmatter（`3.1.0`） |
| 發版 checklist 出處 | `fa-report-refactor-root` repo `docs/handoff/2026-08-31-v310-git-push-summary.md` §5.3 步驟 4 |
| 渲染 bug 實際截圖佐證 | `fa-report-refactor-root` repo `report/MS_Meishan_v313_improved_visual/slide-10.png`、`report/N160JCN_v313_improved_visual/slide-12.png` |

## 4. 重要規則和限制

- 這次稽核是**唯讀**，沒有改動任何程式碼或推送任何 commit，Pi Agent 接手時是全新開始
- `AGENTS.md § 9` 母片保護規則：不要改 pptx 母片 XML，這條規則本次稽核沒有違反，之後修正時也要繼續遵守
- 肯尼大 已明確表態：GitHub Actions CI 紅燈（發現 #1）**不急，可以晚點修**，不用當優先事項
- 這份報告本身**不代表肯尼大 已核准任何修正動作**——肯尼大 是先看過這份報告內容，才決定要不要轉發、轉發哪些部分給 Pi Agent，不要看到這份文件就直接動手改 code

## 5. 已確認結論

**版面渲染修正本身可信，不是空口宣稱**：
- 3 個關鍵 commit 內容與描述相符
- `_safe_shape.py` 的常數與邏輯（`TITLE_SAFE_LEFT_INCH=1.2`、`BODY_MIN_HEIGHT_INCH=1.0`）確實存在，邏輯合理
- 7 個 improver 全部改用新 helper，沒有殘留舊 hard-code 邏輯
- 兩份測試檔案的邏輯真的檢查實質幾何（rotation==0、left>=1.2in、body 高度/不重疊），不是空洞的存在性檢查
- 53 張 PNG 真實存在，實際目視確認 title 未被裝飾擋住、title/body 未重疊、無旋轉
- `src/` 全目錄無殘留 TODO/FIXME/XXX/HACK
- v3.1.1 tag 確實已刪除，CHANGELOG 正確標註「已被 v3.1.2 取代」
- 3 個 skipped 測試已精確定位，都是缺少專屬客戶樣本 pptx 而正常 skip，沒有藏東西

**發現的新問題（Pi Agent 自己都不知道，這是這次稽核的核心價值）**：

1. 🟡【已知，不急】**CI 從 08-31 起幾乎每個 commit 都紅燈**，包括 v3.1.2/v3.1.3 本身。拆解最新失敗（run `33548540009`）：Test job（Python 3.10/3.11/3.12）全過；`Lint & Format` 卡在 `ruff format --check`，就是 `test_slide_rendering.py:89` 跟 `test_visual_quality.py:126` 這兩個這次新增的測試檔案自己沒格式化；`Build Distribution` 因此一直被 skip，打包驗證從 08-31 起沒有一次真正跑完。
2. 🔴【最關鍵】**「219 測試通過、90% 覆蓋率」在 CI／任何第三方環境下都無法重現**。照 CI 完全相同流程本地重跑，結果是 **203 passed, 19 skipped, 85% 覆蓋率**，跟 CI 實際 log 逐字相符。缺口 16 個測試（`test_slide_rendering.py` 7 個 + `test_visual_quality.py` 9 個）全部寫死 `PROJECT_ROOT = Path("/home/elan/fa-report-refactor")`（只存在於 Pi Agent 自己的 WSL 機器），且依賴的客戶 pptx 被 `.gitignore` 排除。**這代表「4 個視覺回歸測試防止重蹈覆轍」這個安全網，在共用 CI 管線裡完全不生效**——之後任何人（換機器的 Pi Agent、或其他協作者）若重新引入 v3.1.1 那 4 個 rotation/placeholder bug，CI 依然會全綠，因為這 16 個測試永遠靜默 skip。
3. 🟡 `tests/conftest.py` 的樣本 fixture 在找不到檔案時回傳 `Path("")`，但 `Path("").exists()` 會解析成當前目錄 `.`，恆回傳 `True`。導致遍布測試檔的 `if not sample_pptx.exists(): pytest.skip(...)` 這道防線完全失效。**全新 clone、尚未跑 `create_test_fixtures.py` 前直接 `pytest tests/`，會爆 12 個測試失敗（不是乾淨 skip）**，包括自稱「母片保護測試——最關鍵的測試」的 `test_master_protection.py` 全部 4 個測試，錯誤訊息是難以理解的 `IsADirectoryError: Is a directory: '.'`。CI 跟 Pi Agent 本機剛好一直有真實 report 檔案，從沒踩過這個雷。
4. 🟡 **`root_cause.py` 的 5-Why 流程圖有內容生成 bug，跟版面渲染無關**：`_add_5why_flow_diagram()` 把真實建議文字硬接上通用佔位字串取前 5 個，且截斷邏輯在第一句沒有句號時會從單字中間截斷。實際渲染結果（MS、N160JCN 兩份報告都重現）可見前 2-3 個流程框顯示斷字斷詞的建議片段，後面接完全通用、沒填實際內容的「Why 2: 直接原因」，不是真正連貫的因果鏈。此前沒人提過。
5. 🟢 **版本號三處沒同步**：`pyproject.toml`（`3.1.0`）、`src/fa_improver/__init__.py`（`3.0.0`）、`SKILL.md` frontmatter（`3.1.0`），都沒跟上實際已發布的 v3.1.2/v3.1.3，違反 root 倉庫自己記載的發版 checklist（v3.0.0→v3.1.0 時有確實做，v3.1.2/v3.1.3 都漏了）。
6. 🟢 **CHANGELOG「標籤」表格失真**：列了 8 個 tag，但 `git tag -l`/GitHub API 只回傳 3 個（v3.1.0/v3.1.2/v3.1.3）。v3.1.1 確定是刻意刪除；其餘 4 個（v3.0.1/v3.0.0/v2.3.0/baseline-v2.3.0）是否真的存在過，repo 本身無法判斷。

## 6. 待確認事項

**有疑慮/證據不足（不是確定的 bug，但值得留意）**：
- `get_title_placeholder()` 第 168-170 行有段死碼，兩個分支結果完全相同，commit message 宣稱的「單一 placeholder 特別處理」實質沒做任何特別的事（目前 3 份樣本沒觸發到，但邏輯沒對齊意圖，**待確認**是否要清理）
- 旋轉/直排偵測只認字串 `"直排"`/`"Vertical"`，換一份用「垂直」「縱向」「Portrait」命名的母片模板，Bug 3（90° 旋轉）可能重現而不會被抓到——**待確認**是否要擴充關鍵字判斷或改用更穩健的偵測方式
- 視覺驗證覆蓋面比看起來窄：`find_content_layout()` 對每份報告只挑一個內容 layout 共用，53 張 PNG 實際只驗證了 3 種 layout 組合，不是任意 pptx 母片都驗證過——**待確認**未來遇到新客戶模板時要不要重新走一次視覺驗證流程

**需要肯尼大 決定的地方（Pi Agent 不要自己拍板，等肯尼大 明確指示）**：
1. **（待確認）** 要不要處理「視覺回歸測試在 CI 完全不會跑」（發現 #2）——候選方案：(a) 準備去識別化/合成的樣本 pptx 提交進 repo 讓 CI 能跑這些測試，或 (b) 至少把寫死路徑改成可設定，並在文件上明確標注這些是「本機手動驗證步驟」而非「CI 回歸測試」，不要再對外宣稱是自動化安全網
2. **（待確認）** `conftest.py` 的 `Path("").exists()` 陷阱（發現 #3）要不要順手修
3. **（待確認）** 5-Why 流程圖內容 bug（發現 #4）是已知可接受的 fallback 設計，還是真的沒人發現過需要修
4. **（待確認）** 版本號三處不一致（發現 #5）是否要一併補上 v3.1.3

## 7. 不要重複做的事情

- **不要只跑本機 pytest 就宣稱「測試全過」**——這次稽核的核心發現就是「219 測試通過」這個數字在 CI/別的機器上重現不出來，本機測試結果不能直接等同於「其他環境也一樣」，尤其是有硬編路徑或依賴本機專屬檔案的測試
- **不要只看「本機跑起來沒問題」就當作已經驗證過 CI 健康**——v3.1.2/v3.1.3 這兩輪修正都沒人去看過 GitHub Actions 的實際紅綠燈，導致 CI 紅了好幾天都沒被發現
- **不要假設寫死路徑的測試在別人的環境也會跑**——這正是視覺回歸測試安全網失效的根因，之後新增任何測試都要問自己「這個測試在一台全新 clone 的機器上會不會正常運作（skip 或跑過），還是會用一種隱晦的方式失效」
- **不要在 handoff 文件裡把「本機驗證過」寫成「已建立自動化防護機制」**——這是措辭上的誤導，即使本機真的驗證過，也要明確區分「這次我手動確認過」跟「以後每次 commit 都會自動確認」是兩件不同的事

## 8. 建議下一步（給 Pi Agent 接手時排優先順序參考）

**低成本、可以先做的**：
- 修 `ruff format`（發現 #1）：直接跑 `ruff format tests/integration/test_slide_rendering.py tests/integration/test_visual_quality.py`，順便讓 `Build Distribution` job 重新跑起來，確認打包真的沒問題
- 補齊版本號（發現 #5）：`pyproject.toml`、`__init__.py`、`SKILL.md` 三處同步到 v3.1.3
- 修正 CHANGELOG 的 tag 表格（發現 #6）：核對哪些 tag 真的存在，不確定的標註清楚，不要照抄舊文件

**需要肯尼大 先拍板方向，再動手的**：
- 視覺回歸測試在 CI 失效（發現 #2）：這是結構性問題，改法（去識別化樣本 vs. 改成明確標注的本機手動步驟）會影響整個測試策略，建議先跟肯尼大 確認要走哪個方向再動手，不要自己選一個就做
- `conftest.py` fixture 陷阱（發現 #3）：修法本身不難（`Path("")` 改回傳 `None`，呼叫端判斷改 `is None`），但要留意所有呼叫這幾個 fixture 的地方都要跟著改判斷邏輯，改完務必**在全新 clone、不先跑 `create_test_fixtures.py` 的情況下**重新測一次，確認真的變成乾淨 skip 而不是隱晦失敗
- 5-Why 內容 bug（發現 #4）：先確認這是不是肯尼大 可以接受的已知限制，如果要修，需要重新設計「建議文字不足時」的 fallback 邏輯，不是簡單的位置調整

**優先順序判斷原則**：這次的核心教訓是「單元測試全綠 ≠ 改善完成」在 v3.1.3 已經被寫進 handoff 了，但這次稽核又往前推一層——**「測試在你自己機器上全綠，也不等於這個驗證機制對其他人有效」**。往後每次宣稱「已修正」或「已加防護機制」之前，建議養成習慣問自己：這個結論如果拿到一台全新環境（CI、或別人的機器）重跑一次，還會不會成立？
