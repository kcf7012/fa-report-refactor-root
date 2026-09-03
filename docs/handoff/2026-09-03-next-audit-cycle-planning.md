# 下次稽核週期規劃(v3.1.5 / v3.2.0)

> 建立日期:2026-09-03
> 對象:未來稽核觸發人(可能是 Kenny 或下次請柔伊 再做一次獨立稽核)
> 狀態:**觸發機制設計完成,等待實際觸發條件成立**

---

## 0. 為什麼需要這份文件

v3.1.4 完成後,稽核生命週期已閉環。但稽核不是一次性工作——**每隔一段時間就要重新觸發**,因為:

1. **程式碼會演進**——新的 commit 可能引入新的 bug,或破壞 v3.1.3/v3.1.4 修正的場景
2. **測試會漂移**——合成 fixture 雖然去識別化,但客戶母片模板會改變,可能需要擴充
3. **流程會忘記**——v3.1.4 用的 pre-commit hook 修正(升級 ruff 到 0.16.5),下次有人 bump 時可能又忘記對齊

這份文件定義**觸發條件 + 觸發後要做什麼**,讓下次的稽核觸發不需要從零開始設計流程。

---

## 1. 觸發條件(任一成立就觸發)

### 1.1 時間型觸發(定期稽核)

| 觸發 | 頻率 | 建議時機 |
|------|------|----------|
| **定期稽核** | 每月 1 次 | 每個月第 1 個工作日 |
| **季度深度稽核** | 每季 1 次 | 每季第 1 個月初 |
| **年度架構稽核** | 每年 1 次 | 每年 1 月初 |

### 1.2 事件型觸發(及時稽核)

| 觸發 | 觸發時機 |
|------|----------|
| **重大 release 後** | v3.2.0 / v4.0.0 等 major/minor release 後 3 天內 |
| **CI 連續紅燈** | 連續 3 個 commit CI 紅燈未修 |
| **稽核發現未實作** | 發現 v3.1.4 backlog 3 項中任一項仍未處理 |
| **新測試類型加入** | 引入新的測試基礎設施(如另一個視覺化框架) |
| **客戶母片模板改變** | 真實客戶回報新母片格式(如全橫排/全縱排/雙語版面) |
| **流程違規** | 發現 agent 又走「沒查證就宣稱完成」模式(如 PR 沒看 CI 就 merge) |

### 1.3 觸發建議矩陣

```
                        觸發成本低
                            ↑
                            │
   自動監控 ←──────── 高頻率 ──→ 每月稽核
                            │
                            │
   季度深度 ←──────── 中頻率 ──→ 年度架構
                            │
                            ↓
                        觸發成本高
```

> **原則**:**主動監控 > 被動等待**。CI 紅燈、流程違規應該**自動通知**(透過 GitHub Actions 的 failure notification 或定期 cron)。

---

## 2. 觸發後要做什麼(稽核流程 SOP)

### 2.1 觸發通知(誰收到)

- **主要聯絡人**: Kenny(專案 owner)
- **稽核執行人**: 柔伊(Mac Claude Code assistant,gh repo clone 遠端稽核)
- **被稽核對象**: 技能包子倉庫 `kcf7012/fa-report-refactor`(若有 PR #2 也包含)

> **重要**:不要自己稽核自己——即使有 code-reviewer 技能,稽核需要**獨立視角**。柔伊 在不同機器用不同工具鏈,這是稽核有效性的基礎。

### 2.2 稽核輸入

```
1. git clone https://github.com/kcf7012/fa-report-refactor
2. cd fa-report-refactor
3. git log --oneline -20   # 看最近 commit
4. git checkout v3.1.4     # 對最新 release tag 進行稽核
5. pip install -e ".[dev,llm]"
6. uv sync --extra dev --extra llm
7. pytest tests/ -q --tb=line  # 看基線
```

### 2.3 稽核 checklist(下次稽核的人請逐項檢查)

#### 2.3.1 CI 健康度

- [ ] 從 commit b6d52d0 後的所有 commit,CI 是否都綠?
- [ ] Build Distribution job 是否每次都執行(不再被 skip)?
- [ ] pre-commit hook 與 CI ruff 版本是否一致?
- [ ] 測試 fixture(真實 + 合成)是否在 CI 環境可用?

#### 2.3.2 程式碼正確性

- [ ] `_safe_shape.py::get_title_placeholder()` 第 158-170 行死碼是否清理?
- [ ] 旋轉/直排偵測是否擴充關鍵字(中英文/Portrait/縱向/垂直)?
- [ ] 5-Why fallback 是否在多語系(中英日韓)報告上行為正確?
- [ ] 視覺回歸測試的 3 個合成 fixture 是否還能觸發原始 Bug?
- [ ] 新增的 14 個 5-Why 單元測試是否覆蓋了 edge cases?

#### 2.3.3 測試誠實度

- [ ] 是否所有測試都能在全新 clone 環境跑通?
- [ ] 是否所有測試都檢查「實質行為」(不是只有存在性檢查)?
- [ ] 是否還有寫死 `/home/elan/fa-report-refactor` 的測試?
- [ ] 是否有測試依賴客戶 pptx/JSON 但又 `if not X.exists(): skip`(其實是 fail)?
- [ ] 客戶母片模板改變時,合成 fixture 是否仍能觸發場景?

#### 2.3.4 流程規範

- [ ] 是否有 PR 沒看 CI 就 merge?
- [ ] 是否有 release commit 漏做版本號同步(三處一致)?
- [ ] 是否有 CHANGELOG 條目遺漏或順序錯誤?
- [ ] 是否有 tag 未推送(本地有但 GitHub 沒)?
- [ ] 是否所有 GitHub Release 都有對應 tag?

#### 2.3.5 文件誠實度

- [ ] 是否有 handoff 自述「已修」但實際沒修?
- [ ] 是否有「本機跑過」宣稱但 CI 環境無法重現?
- [ ] 是否有「測試覆蓋率 X%」但實際測試是空的?
- [ ] AGENTS.md / README.md / CHANGELOG.md 三者版本號是否一致?

### 2.4 稽核輸出範本

```markdown
# 稽核報告 — v3.1.5 候選

## A. 上次稽核(v3.1.4)發現的處理狀態
- ✅ 全部修正:列舉
- ⏸️ 部分修正:列舉
- ❌ 未修正:列舉(嚴重程度)

## B. 本次新發現
- 嚴重程度: P0(必修) / P1(應修) / P2(可延後)
- 每個發現包含:證據、影響、修復建議

## C. CI 健康度
- 最近 N 個 commit 的 CI 結果
- Build Distribution 是否正常
- 測試 fixture 狀態

## D. 流程違規
- 自上次稽核後的違規事件
- 違規嚴重程度

## E. 結論
- 給 Kenny 的建議:是否值得開 v3.1.5
- 若需要修,給改善計畫的 seed
```

---

## 3. 自動監控(可選但建議)

### 3.1 GitHub Actions 通知

`.github/workflows/notify-failure.yml`(可選,未來加):

```yaml
name: CI failure notify
on:
  workflow_run:
    workflows: ["Tests"]
    types: [completed]
jobs:
  notify:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - name: Notify Kenny
        run: |
          # 透過 gh CLI 或 webhook 通知
          echo "CI failed on commit ${{ github.event.workflow_run.head_sha }}"
```

### 3.2 定期 cron 觸發

`.github/workflows/monthly-audit-trigger.yml`(可選):

```yaml
name: Monthly audit trigger
on:
  schedule:
    - cron: '0 0 1 * *'  # 每月 1 號 00:00 UTC
jobs:
  create-issue:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: 'kcf7012',
              repo: 'fa-report-refactor',
              title: `月度稽核觸發 — ${new Date().toISOString().slice(0, 7)}`,
              body: '提醒:執行獨立稽核流程,參考 docs/handoff/2026-09-03-next-audit-cycle-planning.md',
              labels: ['audit']
            })
```

> **注意**:cron workflow 預設不會在 fork 或私人 repo 自動跑,但 `kcf7012/fa-report-refactor` 是 public,沒問題。

---

## 4. v3.1.5 backlog(從 v3.1.4 稽核降級)

這些是 v3.1.4 沒修完的項目,應在下次稽核週期優先處理:

| # | 項目 | 來源 | 優先級 | 工作量 |
|---|------|------|--------|--------|
| 1 | 清理 `_safe_shape.py::get_title_placeholder()` 死碼 | 稽核 #3 待確認 1 | P2 | 0.5 小時 |
| 2 | 擴充旋轉/直排偵測關鍵字(中英文/Portrait) | 稽核 #3 待確認 2 | P1 | 2-4 小時 |
| 3 | 視覺驗證流程適應新客戶母片模板 | 稽核 #3 待確認 3 | P1 | 1 天(看客戶回報) |
| 4 | 修 git history:`v3.0.0` / `v3.0.1` tag 本地有但 GitHub 沒 push(發版流程不完整) | 稽核 #6 | P2 | 1 小時(retag + push) |
| 5 | 加 GitHub Actions `notify-failure.yml`(§3.1) | 本文件建議 | P2 | 1 小時 |
| 6 | 加 GitHub Actions `monthly-audit-trigger.yml`(§3.2) | 本文件建議 | P2 | 1 小時 |

---

## 5. 從這份文件開始:稽核觸發的最小可行流程

### 5.1 如果只是「立即觸發」(發現 v3.1.4 backlog 沒人處理)

1. Kenny 開 issue:`[稽核觸發] v3.1.4 backlog 3 項未處理`
2. 標籤:`audit`、`v3.1.5`
3. 在 issue body 引用 `docs/handoff/2026-09-03-next-audit-cycle-planning.md`
4. 請柔伊 重新稽核,或在 issue 上 `@claude-code-assistant`

### 5.2 如果「定期觸發」(每月/每季)

1. 設 calendar reminder 或 cron(見 §3.2)
2. Kenny 收到提醒 → 開 issue(同 §5.1)
3. 流程同 §2

### 5.3 如果「CI 紅燈持續」自動觸發

1. CI 連續紅 3 個 commit(見 §1.2)
2. `notify-failure.yml`(若已加)自動開 issue
3. 流程同 §5.1

---

## 6. 稽核失敗的處理流程

如果下次稽核發現**未修正項目**:

1. **不要急著做新功能**——先修稽核發現
2. **走改善計畫流程**(`docs/handoff/2026-09-03-audit-remediation-plan-handoff.md` 是範本)
3. **計畫拍板後**才動手
4. **完成後發布 release**,並把 release commit 包含在改善計畫的驗證流程

---

## 7. 與其他文件的關聯

| 文件 | 關係 |
|------|------|
| `docs/handoff/2026-09-02-fa-report-refactor-audit-handoff.md` | 上次稽核報告(本文件的觸發起點) |
| `docs/handoff/2026-09-03-audit-remediation-plan-handoff.md` | 上次改善計畫(下次稽核的範本) |
| `docs/handoff/2026-09-03-pr-merge-flow-playwright-guide.md` | PR/Merge 流程教學(稽核發現的修復需要這些流程) |
| `docs/handoff/screenshots/pr-merge-flow/` | PR/Merge 截圖(稽核時可對照看 UI 行為) |
| `AGENTS.md` | agent 工作守則(稽核時可驗證 agent 是否遵守) |

---

## 8. 成功指標

下一次稽核應該:

1. **發現問題數 ≤ v3.1.4 的 6 項**(代表專案成熟度提升,問題減少)
2. **CI 全綠率 ≥ 95%**(從 v3.1.4 的 100% 開始下降一點也可接受,但不能連紅)
3. **backlog 清空率 ≥ 50%**(每次稽核週期至少清一半 backlog)
4. **新功能不引入 P0 bug**(這是底線)

如果下次稽核發現**超過 6 項**,代表 v3.1.4 的改善模式失敗,需要更根本的架構調整。

---

**完成確認**:
✅ `docs/handoff/2026-09-03-next-audit-cycle-planning.md` 已建立
   包含:8 章節(觸發條件 / 流程 SOP / 自動監控 / backlog / 最小可行流程 / 失敗處理 / 文件關聯 / 成功指標)
✅ 與 v3.1.4 改善計畫的範本對齊
✅ 給「下次稽核的人」明確的 checklist + 輸出範本
✅ 提供 3 種觸發路徑(立即 / 定期 / 自動 CI 通知)
