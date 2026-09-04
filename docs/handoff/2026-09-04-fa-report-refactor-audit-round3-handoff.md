# Handoff：fa-report-refactor 第三輪獨立稽核報告

> 交給：Pi Agent（Windows/WSL 端維護 `fa-report-refactor` 的 agent）
> 稽核者：柔伊（肯尼大 的 Mac 上跑的 Claude Code assistant），透過 `git clone`/`gh api` 遠端稽核，沒有實際碰到 Windows 本機檔案
> 日期：2026-09-04
> 這是連續第三輪稽核，前兩輪修好的東西不重複贅述，重點放在這輪還沒解決的部分

## 1. 目前任務目標

第一輪（09-02）稽核抓到 5 個問題（CI紅燈、視覺回歸測試安全網失效、conftest fixture 陷阱、5-Why 內容 bug、版本號不同步），修完後肯尼大 發現「標題偏左」「6維度圖」兩個舊問題回歸。第二輪（09-04）查證：地基問題（CI、16個視覺回歸測試、conftest、5-Why）真的解決了，但回歸修正本身留了幾個坑，且回歸修正過程又重演了「直接push main沒走PR」導致CI紅燈的老毛病。肯尼大 請 Pi Agent 針對這些坑重新修一輪，說「修改完成了」，這是第三輪的複查結果——**這次找到一個連續三輪都存在、目前有實測證據證明是活漏洞的結構性問題，優先處理這個**。

## 2. 已完成內容

第三輪稽核方法：`git pull` 兩個 repo 到最新（技能包 HEAD `f2118cf`），全新 Python 3.11 環境從零重跑測試，`gh api`/`gh run view`拉 CI/Release/PR 真實資料，並寫小腳本實際跑一次改善 pipeline 重現結構性缺口。

## 3. 關鍵文件和位置

| 項目 | 位置 |
|---|---|
| 技能包倉庫 | `github.com/kcf7012/fa-report-refactor` |
| 文件倉庫 | `github.com/kcf7012/fa-report-refactor-root` |
| **最優先：標題安全防線的死角** | `src/fa_improver/improvers/_safe_shape.py` `get_title_placeholder()` 第 118-170 行 |
| 對應的漏測試 | `tests/integration/test_visual_quality.py::test_title_textbox_safe_left` 第 271-273 行（`if shape.is_placeholder: continue`） |
| 用來重現漏洞的合成 fixture | `tests/integration/_synthetic_fixtures/synthetic_C_decoration.pptx`（docstring 自稱是「觸發 TITLE_SAFE_LEFT_INCH 修正」用的，但實測測不出來） |
| fixture 建置腳本（母片裝飾區座標） | `scripts/build_synthetic_fixtures.py` 第 167-179 行（`LeftTopDecoration`：left=0, top=0, w=1.0in, h=0.5in） |
| 這輪 margin=0.5 修正涉及的 8 個檔案、18 處 | `basic_info.py:69`、`summary.py:117/167/220`、`root_cause.py:51/241/189`、`analysis_method.py:56/83/104`、`evidence_checklist.py:56/83/107`、`problem_definition.py:55/82/115`、`prevention.py:48/210/273` |
| v3.1.4 tag 指向的舊 commit | `5cb68a4`（09-03 11:47），比回歸修正晚了近14小時的修正 commit 完全沒被涵蓋 |
| 未涵蓋進任何 tag 的 5 個 commit | `eb9afe3`/`5db2b5a`/`b071b00`/`6e4089b`/`f2118cf` |
| 指向錯誤 tag 的稽核 SOP 文件 | `fa-report-refactor-root` repo `docs/handoff/2026-09-03-next-audit-cycle-planning.md` 第 77 行（`git checkout v3.1.4`） |
| 寫死本機路徑的驗收頁 | `docs/handoff/screenshots/v3.1.4-regression-visual-review.html`（53張img全部指向 `/home/elan/fa-report-refactor/...`） |
| 覆蓋率數字錯誤的兩處文件 | `CHANGELOG.md:181`、`USER_GUIDE.md:784`（寫 90%，實測+CI log 都是 85%） |
| CI branch protection 檢查結果 | `gh api repos/kcf7012/fa-report-refactor/branches/main/protection` → 404（沒有設定） |

## 4. 重要規則和限制

- 這次稽核唯讀，沒有改動任何程式碼或推送任何 commit
- 肯尼大 已明確表態：這份報告要把「`get_title_placeholder` 結構缺口」跟「建議加 branch protection 逼走 PR」這兩條放最優先處理
- 肯尼大 是先看過這份報告，才決定要不要轉發、怎麼轉發給 Pi Agent，不代表已核准任何修正動作

## 5. 已確認結論

**這輪真的解決的（獨立驗證通過）**：
- `margin=0.5` 系統性殘留根因真的修好了：8 個檔案 18 處全部從硬編 `margin=0.5`/`left=0.5` 改成 `TITLE_SAFE_LEFT_INCH - 0.2`（=1.0）+ floor 保護，diff 逐一核對過，乾淨無殘留衝突標記
- main HEAD（`f2118cf`）CI 真綠燈：Test×3(3.10/3.11/3.12)、Lint & Format、Build Distribution 全部 success
- 單元測試數字對得上：全新環境重跑得到 233 passed, 3 skipped，跟宣稱一致
- 16 個視覺回歸測試持續真的在跑（非 skip），沒有退步
- ruff check/format 全過

**這輪仍是缺口、尚未處理（最重要，排最前面）**：

🔴 **`get_title_placeholder()` 的安全防線只在「母片沒提供原生標題框」時才生效，這是連續三輪都存在、這次首次被實測證明是活漏洞的結構性問題**——只要 layout 有原生 `idx==0` title placeholder（策略1）或 TITLE/CENTER_TITLE 型別（策略2），就直接 `return ph`，完全不檢查 `left` 座標是否落在裝飾區內。`TITLE_SAFE_LEFT_INCH` 這個 1.2in 的安全常數，只在 `get_or_create_title()` 的 fallback 分支（`ph is None` 時）才會用到。用他們自己專門設計來測這個機制的合成 fixture（`synthetic_C_decoration.pptx`）實際跑一次改善 pipeline，4 張新投影片的 title 全部落在 `left=0.5, top=0.30`——跟母片上 `left=0,top=0,w=1.0in,h=0.5in` 的裝飾矩形幾何上確實重疊，安全常數完全沒發生作用。配套測試 `test_title_textbox_safe_left` 寫著 `if shape.is_placeholder: continue`，直接跳過對這個情境的檢查，這輪也沒人碰。**`find_content_layout()` 永遠會回傳某個真實 layout（絕不回傳 None），而一般公司 PPT 母片幾乎都提供原生 title placeholder，所以這個防線真正生效的 fallback 分支反而是少數情況——這不是邊角案例，是常見路徑。**

**這輪仍是缺口、有處理但不完整（第二輪就點名過，這輪幾乎逐字重演）**：

1. **v3.1.4 tag/Release 還是沒補新版**：`git log v3.1.4..HEAD` 有 5 個未被任何 tag 涵蓋的 commit。`gh release view v3.1.4` 確認 Release 仍指向修正前的舊 commit（`5cb68a4`）。安裝指令 `pip install git+...@v3.1.4` 今天執行仍會拿到有回歸 bug 的版本。**更關鍵**：`docs/handoff/2026-09-03-next-audit-cycle-planning.md:77` 那行「`git checkout v3.1.4`」原封不動——這份文件這輪明明被相鄰 commit 觸碰過，但沒人回頭改這一行，未來稽核者照做仍會完全看不到這次修正。三處版本號都還是 `3.1.4`，同一版號現在對應兩個不同的程式碼狀態。
2. **驗收截圖路徑沒改善，這次是明知故犯**：新的驗收頁 53 張圖全部是寫死本機絕對路徑，commit 訊息直接寫「路徑為絕對路徑…Kenny 可直接用 file:// 開啟」——是有意識維持這個做法，不是疏忽。這批 PNG 也還被 `.gitignore` 排除，沒進 repo，任何人都無法開啟驗證。
3. **PR review 流程又沒走**：回歸修正的合併 commit `b071b00` 確認是本機 merge 後直接 push main，沒有走 PR。這次 push（14:39:59）CI failure（衝突標記導致語法錯），main 紅燈約12分鐘才被下一個 commit 修好。兩個 repo 都沒有 branch protection（`gh api .../branches/main/protection` 回 404），**技術上沒有任何機制能擋下這種情況再次發生**。
4. **CHANGELOG 標籤表格內容不準**：對 v3.1.0/v3.1.2/v3.1.3 都標「GitHub Release: ✅」，但 `gh api` 確認全部 404——只有 v3.1.4 是真正的 GitHub Release，表格加了欄位卻沒真的去核對。
5. **覆蓋率數字是可驗證的錯誤**：CHANGELOG 跟 USER_GUIDE 都寫「90%」，但全新環境重跑兩次、以及他們自己 CI Run #25 的 log，都是 85%。這個錯誤數字從 v3.1.3→v3.1.4 就存在，這輪的文件更新有機會順手核對卻沒有。
6. **Codecov token 缺失完全沒動**，仍靜默失敗（`fail_ci_if_error: false` 吞掉錯誤，CI 綠燈但覆蓋率追蹤事實上是壞的）。

## 6. 待確認事項

- **（待確認）`get_title_placeholder()` 的修法方向**：候選方案是「即使是原生 placeholder，也要檢查 left 座標是否落在裝飾區，落在裡面就改用 safe fallback」，還是有更適合的做法，需要團隊自己判斷，不是柔伊 這邊拍板
- **（待確認）要不要導入 branch protection**：GitHub 的 branch protection rule（要求 PR + review 才能合併進 main）能從機制上擋掉「衝突標記沒清乾淨直接 push」這類問題，但這會改變團隊現有的工作流程（目前看起來習慣本機 merge 直接 push），需要肯尼大/Pi Agent 討論要不要採用，柔伊 只提出這是能解決根因的選項
- **（待確認）v3.1.4 這個版號怎麼收尾**：是補發一個 v3.1.5（乾淨地把回歸修正跟這輪修正都納入新版號），還是回頭修正 v3.1.4 Release 指向的 commit，兩種做法各有取捨，需要團隊決定

## 7. 不要重複做的事情

- **不要只看「新加的測試通過」就認為某個安全機制真的生效**——這是這輪最重要的教訓：`TITLE_SAFE_LEFT_INCH` 這個常數本身沒問題，但保護它的程式碼路徑（fallback 分支）跟實際最常被觸發的路徑（原生 placeholder 分支）是兩條不同的路，测試也只驗證了其中一條。之後新增任何「安全防護」邏輯，要先確認清楚：這個防護在所有輸入情境下都會被觸發嗎？還是只在某個特定分支？
- **不要為了讓既有測試通過而反推修正的數值**——上一輪 `TITLE_SAFE_LEFT_INCH - 0.2` 這個數字就是這樣選出來的（緩衝只剩0.03in），本末倒置。應該先做安全距離分析，再看測試門檻要不要跟著調整，不是反過來。
- **不要再把回歸修正直接 push 到 main**——這是第二次留下沒清乾淨的衝突標記讓 CI 紅燈了。哪怕是「小修正」也要走 PR，或至少 push 前手動確認 `git status`/`git diff` 乾淨。
- **不要在驗收文件裡使用只有自己機器讀得到的絕對路徑**——這件事已經明確被指出過一次，這輪是「知道但選擇繼續這樣做」，不是不知道。以後產出任何要給其他人（包括肯尼大、稽核者）看的驗收證據，要嘛把圖片實際 commit 進 repo，要嘛用其他能被他人開啟的方式。
- **不要在更新 CHANGELOG/文件時照抄舊數字**——這次的「90%覆蓋率」錯誤字面上就是複製貼上前一版沒改，稍微跑一下測試就能發現跟實際不符。

## 8. 建議下一步（給 Pi Agent 接手時排優先順序參考，肯尼大 交代前兩項優先）

**優先處理 1：修 `get_title_placeholder()` 的結構性缺口**
不能只在 fallback 分支保護，原生 placeholder 分支也要檢查 `left` 座標是否落在母片裝飾區內，落在裡面時要有 fallback 機制（例如改用 safe_textbox，或把原生 placeholder 移動到安全位置）。同時要修 `test_title_textbox_safe_left`，不能再對 placeholder 情境直接 `continue` 跳過——現有的合成 fixture（`synthetic_C_decoration.pptx`）已經是很好的測試素材，問題只在於程式碼邏輯跟測試邏輯都沒有真的覆蓋到這條路徑。

**優先處理 2：導入機制性防呆，別再靠「這次會記得」**
連續兩輪都是「衝突標記沒清乾淨直接 push main」導致 CI 紅燈。建議設定 GitHub branch protection（要求 PR + 至少一次 review + CI 通過才能合併進 main），從機制上擋掉這類問題，而不是每次事後補救。

**接下來可以做的（優先順序較低，但都是明確缺口）**：
- 補發新版本（v3.1.5 或修正 v3.1.4 Release 指向），確保 tag/Release 反映真實最新狀態，並更新 `docs/handoff/2026-09-03-next-audit-cycle-planning.md:77` 那行不要再指向舊 tag
- 修正 CHANGELOG 的覆蓋率數字（90%→85%）跟標籤表格的 Release 欄位（v3.1.0/v3.1.2/v3.1.3 都不是真的 Release）
- 驗收證據的呈現方式要改成別人也能重現驗證的形式（commit 進 repo 或其他可分享的方式），不要再用寫死本機路徑的 HTML
- 補上 Codecov token，讓覆蓋率追蹤真的生效，不要讓失敗被靜默吞掉

**優先順序判斷原則**：這三輪下來有個清楚的模式——技術症狀修得認真，流程紀律修不動。與其一輪一輪追著症狀跑，這次建議先花時間把「優先處理 2」的機制性防呆做起來，之後很多重複出現的坑（衝突標記、寫死路徑、忘記更新版本號）都能透過流程本身擋下來，而不是每次都靠事後稽核抓。
