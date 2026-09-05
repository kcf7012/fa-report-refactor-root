# Handoff：P3 — CI 與流程防呆

> 撰寫者:Claude Code
> 日期:2026-09-05
> 狀態:**完成並經柔伊兩輪獨立查證(第七、第八輪報告),含一次遠端 CI 回歸的即時修復**
> 上游:`docs/handoff/2026-09-05-cross-platform-migration-plan-handoff.md` P3

## 這份文件的定位

計劃書 P0-P2 執行完後一直沒有補 P3 的 handoff(柔伊第七輪查證 E8 點名)。
本文件補齊,彙整 P3 五個步驟做了什麼、push 後撞到什麼、以及最終狀態。
**不重複列逐條查證證據**——那些在 `2026-09-05-zoe-verification-round7-p3-ci.md`
與 `round8`(若有)裡,這裡只記結論與怎麼修的。

## P3 做了什麼(五步驟)

1. **macOS runner**:`.github/workflows/test.yml` 的 matrix 加入
   `macos-latest`,job 名稱改為 `Test (${{ matrix.os }} / Python ...)`
   (原本沒帶 `matrix.os`,兩個 OS 的 job 名稱會撞在一起)。
2. **pre-commit job**:新增獨立 job 跑 `pre-commit run --all-files`。
   之前 CI 只手動重複 ruff 兩個 hook,`check-merge-conflict` 這類從沒在
   PR 上真正跑過——這正是「rebase 衝突標記沒清乾淨就直推 main」能連續
   兩輪發生的原因。
3. **路徑守門**:新增 `scripts/check_no_hardcoded_paths.py`,只檢查
   **新增行**(不掃既有內容,`docs/handoff/` 是歷史紀錄)。接到兩個 repo
   的 local pre-commit hook 與 CI 的 lint job。
4. **根倉庫最小 workflow**:根倉庫此前**完全沒有任何 CI**、`.git/hooks/`
   也只有 `.sample`。新增 `.github/workflows/checks.yml` 跑路徑守門 +
   Markdown 連結檢查,以及根倉庫自己的 `.pre-commit-config.yaml`。
5. **branch protection**:兩個 repo 都設,規則不同(見下)。

## branch protection 最終狀態(2026-09-05 拍板)

| repo | `enforce_admins` | required status checks | 直推 main |
|---|---|---|---|
| 技能包(`fa-report-refactor`) | `true` | Lint & Format、Pre-commit、六個 `Test (<os> / Python <ver>)` job(全部 8 個) | ❌ 必須走 PR |
| 根倉庫(`fa-report-refactor-root`) | `false` | Path & Link Checks | ✅ 可以 |

**取捨,誠實記錄**(計劃書 P3 第 5 步明文要求):

- `required_approving_review_count: 0` 兩邊都是——單人維護,設 1 會鎖死自己
  (自己不能核准自己的 PR)。**「至少一次 review」這條稽核建議沒有完整落實。**
- 根倉庫 `enforce_admins=false` 是刻意放寬,不是疏漏:`enforce_admins`
  只管「要不要走 PR review」,`allow_force_pushes=false`/`allow_deletions=false`
  兩個 repo 都生效且與 `enforce_admins` 無關,所以「不走 PR」不等於「沒有防呆」。
  根倉庫是單人維護、高頻小改的文件倉庫,強制自己開 PR 自己核准是演戲。
- 技能包 required checks 一開始只列了 4 個(Lint、Pre-commit、Test ubuntu-3.10、
  Test macos-3.10),後來補齊六個 test job 全列——原本的缺口一度讓「剛修好的
  3.11/3.12 回歸」不在保護範圍內(見下)。
- 緊急情況預設**不留後門**:真的卡住時走 `gh api -X DELETE .../protection`
  暫時解除、推送、立刻補回同樣設定,並在後續 commit 說明原因。這是刻意留
  稽核軌跡,不是常態流程。文件化在 `README.md`「Commit 流程」與
  `AGENTS.md` 8.1.1。

## push 後撞到的三個問題(全部靠 CI 本身抓到,不是本機模擬出來的)

這正是「push 順便讓 CI 跑一次乾淨 clone 情境」的價值——本機全綠,遠端抓到:

1. **路徑守門紅在 `CLAUDE.md` 三行**:本機 hook 只看單一 commit 的 staged
   diff,CI 比對整個 push 範圍(20 個 commit),涵蓋了更早期就寫進去的
   WSL 遷移說明文字。三行都是描述問題本身的敘述,加 `<!-- allow-abs-path -->`
   豁免解決。
2. **README 6 條指向 `.agents/` 的連結對任何 clone 都是死的**:根 `.gitignore`
   排除 `.agents/`,所以只有本機(技能包實體存在)是好的。技能包內的檔案
   改用 GitHub URL;只存在本機的三個 skill 改成純文字標「僅本機」。
3. **CI 的 3.11/3.12 在兩個 OS 上全掛**(這是 P2 造成的既有回歸,P3 才第一次
   跑出真的 macOS + 多版本矩陣才暴露):`uv run` 不帶 `--python`/`--no-sync`
   時會依 `.python-version`(3.10)重新解析,在 3.11/3.12 job 上等於**重建
   一個不含 dev extra 的環境**,`error: Failed to spawn: pytest`。CI 的 12
   處 `uv run` 全部改 `uv run --no-sync`;稍後柔伊第七輪查證再指出
   `.pre-commit-config.yaml` 的 local hook 用 `--frozen`(只管 lockfile、
   不阻止 sync)不是真的防護,一併改成 `--no-sync`。

## 最終驗證(HEAD:root `cc06204` / skill `fc6fd2c` 之後又有後續 commit,見下)

技能包 CI 8/8 job 全綠(ubuntu×3 + macOS×3 + Lint + Pre-commit),第一次在
macOS runner 上通過。實測直接 `git push origin main`(技能包)→
`remote rejected` + `Changes must be made through a pull request`,protection
生效確認。

## 柔伊第七輪查證抓到的後續缺口(已處理)

第七輪報告(`2026-09-05-zoe-verification-round7-p3-ci.md`)技術面幾乎全部
屬實(8 個 job 精準、macOS runner 為真、uv 根因一字不差),但同一個模式犯了
兩次:備份 bundle 再次過期(已由柔伊本人重拍解決)、測試數字量完就過期
(加了第三支 import 測試後 235/238 變 236/239——**本輪刻意不重新量測**,
因為 iCloud 弄壞 `.pth` 時量到的是故障狀態的數字,等搬離 iCloud、環境穩定
後再量才是真的)。另外三個問題已在本文件與相關 commit 處理:

- required checks 只有 4/8 個 job → 補齊六個 test job 全列
- 文件仍教 `git push origin main` → `README.md`/`AGENTS.md` 改為兩 repo
  分開說明,含取捨與緊急情況處置
- Codecov 上傳從未成功過但 job 顯示綠色(`CODECOV_TOKEN` secret 未設,
  `fail_ci_if_error: false` 吞掉錯誤)→ 移除該步驟,保留不需要 token 的
  `Archive coverage report` artifact 上傳
- `check_markdown_links.py` 只查 `.md` 不查 `.html` → 擴充支援
  `<img src>`/`<a href>`,已用故意放壞連結的方式驗證機制有效
- `CLAUDE.md` 的「目前進度」整段(含相鄰的 WSL 遷移表格、AGENTS.md 已知
  錯誤清單)已經過期且相互矛盾 → 全部改為指向 `git log`/`gh run list`
  等即時查詢指令,不再維護會過期的快照
- `CLAUDE.md` 補第三條慣例規則:對時效性證據只能下「無法驗證」,不能下
  「不實」——這是 F1d 那次(見 round6 報告第 4 節)換來的教訓

## 尚未處理(留給下一輪)

- **搬離 iCloud**:`UV_PROJECT_ENVIRONMENT` 方案已否決(direnv 只在互動式
  shell 觸發,非互動呼叫會靜默失敗退回專案內建 venv)。決定直接搬出
  `~/Desktop`,由 Kenny/柔伊主導執行,技術前提已具備(P1 讓程式碼零修改)。
- **測試數字重新對齊**:等環境穩定後,把 README badge / `CLAUDE.md` /
  `docs/00_executive_summary.md` / `docs/USER_GUIDE.md` 的數字對到當時的
  HEAD SHA,不要用故障狀態量到的數字。
- **P4**:`get_title_placeholder()` 的結構性缺口(稽核連三輪點名優先 1),
  不需要等搬家,可以並行開跑。
- 技能包的 P3 成果目前全在 `v3.1.5-cross-platform` 分支,`main` 一動未動——
  等 P4-P7 有實質內容再開 PR 一次合併,不開佔位用的 draft PR。
