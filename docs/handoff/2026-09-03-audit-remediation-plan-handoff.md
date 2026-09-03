# Handoff: v3.1.2/v3.1.3 稽核發現 6 項問題之改善計畫(v3.1.4 待執行)

> 建立日期:2026-09-03
> 拍板日期:2026-09-03(Kenny 已回覆 4 項決策)
> 對象:Kenny + v3.1.4 接手 Agent
> 工作目錄:`/home/elan/fa-report-refactor`(根倉庫) + `.agents/skills/fa-report-improvement/`(技能包子倉庫,獨立 git)
> **狀態**:✅ **v3.1.4 已於 2026-09-03 完整執行並 release(本計畫閉環)**
> **依據**:`docs/handoff/2026-09-02-fa-report-refactor-audit-handoff.md`(柔伊 遠端稽核報告)
> **拍板結果摘要**:見 §10
**執行結果摘要**:見 §10.6(2026-09-03 完成)

---

## 0. 為什麼需要這份計畫

柔伊(在 Mac 上跑 Claude Code)以「不採信 handoff 自述、實際查證」方式,獨立稽核 v3.1.2/v3.1.3 修正,確認:

✅ **v3.1.2/v3.1.3 版面渲染修正本身可信**(commit 內容與描述相符、helper 邏輯合理、7 個 improver 都改用、測試檢查實質幾何、53 張 PNG 目視確認、沒有殘留 TODO)。

🆕 **但同時揭露了 6 項 Pi Agent 自己都沒發現的問題**,最嚴重的是:

- 🔴 **CI 宣稱的「219 測試通過、90% 覆蓋率」在 CI / 任何第三方環境都重現不出來**(本機實跑 203 passed, 19 skipped, 85%)。
- 🔴 **16 個視覺回歸測試在 CI 完全不跑**(硬編 `/home/elan/fa-report-refactor` 路徑 + 依賴 `.gitignore` 排除的客戶 pptx),v3.1.1 那種「修了卻沒人驗證」的隱憂會重演。
- 🟡 **`tests/conftest.py` 全新 clone 不跑 `create_test_fixtures.py` 會爆 12 個測試失敗**(包含聲稱「最關鍵」的母片保護測試),CI 與 Pi Agent 本機剛好一直有真實 report 檔案,從沒踩過。

這份計畫**只整理事實、排優先順序、給出明確行動選項**,**所有實質改動需 Kenny 先決定方向**再進行。

---

## 1. 任務目標

針對稽核報告的 6 項發現 + 3 項「有疑慮/證據不足」+ 4 項「需 Kenny 拍板」,提出一份:

1. **可立即執行**(符合根倉庫發版 checklist 規範、無破壞性)的低成本改善
2. **需先決策再執行**(影響測試策略或設計選擇)的高風險改善,連同至少 2 個候選方案供 Kenny 選
3. **明確的不做清單**(這次稽核要避免 Pi Agent 自己拍板)

---

## 2. 已完成內容(本次 session)

### 2.1 讀完稽核報告 + 實地查證關鍵發現

| # | 稽核發現 | 查證方式 | 結果 |
|---|---|---|---|
| 1 | CI 從 08-31 起每個 commit 都紅燈 | `web_fetch https://api.github.com/repos/kcf7012/fa-report-refactor/actions/runs?per_page=5` | ✅ **確認**:最近 5 個 run 中 run 14~17(對應 `900f867`、`70fb30d`、`ec25cac`、`b6d52d0`)全紅,只有 run 13(`cd61936` CI 修正)綠 |
| 2 | CHANGELOG 寫 8 個 tag,實際只有 3 個 | `web_fetch .../tags` 與本地 `git tag -l` | ✅ **確認 + 推進**:GitHub API 只回 `v3.1.0`、`v3.1.2`、`v3.1.3`;**本地 `git tag -l` 有 5 個**(`v3.0.0`、`v3.0.1`、`v3.1.0`、`v3.1.2`、`v3.1.3`),差異是 `v3.0.0`/`v3.0.1` 是**本地有 tag 但從未 push 到 GitHub** |
| 3 | 版本號 3 處未同步 | `grep` `pyproject.toml`、`__init__.py`、`SKILL.md` | ✅ **確認**:`pyproject.toml` `3.1.0`、`__init__.py` `3.0.0`、`SKILL.md` frontmatter `3.1.0`,皆落後於已發布的 v3.1.2/v3.1.3 |
| 4 | `_safe_shape.py::get_title_placeholder()` 死碼 | `read` 第 158-170 行 | ✅ **確認**:兩個 `if/return None / return None` 分支結果完全相同(目前 3 份樣本沒觸發,邏輯沒對齊 commit message 宣稱) |
| 5 | 5-Why 流程圖內容 bug | `read` `root_cause.py` 第 145-159 行 | ✅ **確認**:`s.split("。")[0][:15]` 在沒有「。」時回傳整段,再 `[:15]` 從單字中間切;15 字也太短 |
| 6 | 測試硬編路徑 | `grep -rn 'PROJECT_ROOT = Path(' tests/` | ✅ **確認**:`tests/integration/test_visual_quality.py:31` 與 `tests/integration/test_slide_rendering.py:33` 都寫死 `/home/elan/fa-report-refactor` |
| 7 | `conftest.py` fixture 陷阱 | `read` 第 103-136 行 + `python3 -c "Path('').exists()"` | ✅ **確認**:`Path("").exists()` 回 `True`、`Path("").resolve()` 解析成當前 cwd,符合稽核描述 |
| 8 | `.gitignore` 排除客戶 pptx | `read .gitignore` | ✅ **確認**:`report/*.pptx` 與 `report/*.json`、`report/*.txt` 都排除,測試依賴的本機專屬檔案 CI 永遠拿不到 |

### 2.2 額外推進的觀察(超出稽核報告)

| # | 觀察 | 證據 |
|---|---|---|
| A | v3.0.0/v3.0.1 是「本地有 tag 但 GitHub 沒 release」 | 本地 `show-ref --tags` 有這 2 個 refs,GitHub API `tags` endpoint 沒回——稽核說「v3.0.1/v3.0.0/v2.3.0/baseline-v2.3.0 是否真的存在過,repo 本身無法判斷」可推進為「v3.0.0/v3.0.1 是本地有但從未 push,v2.3.0/baseline-v2.3.0 連本地都沒有」 |
| B | 發版 checklist 漏步驟 4 的證據鏈完整 | `docs/handoff/2026-08-31-v310-git-push-summary.md §5.3 步驟 4` 明確列出「更新版本號」步驟,v3.0.0→v3.0.1→v3.1.0 期間顯然漏做,因此 v3.0.0/v3.0.1 既沒 push 也没 release;v3.1.0→v3.1.2→v3.1.3 又漏做,因此三處版本號仍是舊值 |

---

## 3. 6 項發現的事實彙整 + 計畫

### 3.1 發現 #1:CI 從 08-31 起幾乎每個 commit 都紅燈 🟡【不急】

**事實**:
- 影響:整個 CI pipeline(`Lint & Format` 卡 ruff format → `Build Distribution` 被 skip → 打包驗證從 08-31 起沒跑過一次)
- 唯一卡點:`test_slide_rendering.py:89` 與 `test_visual_quality.py:126` 這兩個新測試檔沒 `ruff format`
- Kenny 已表態:**不急,可晚點修**

**計畫**:
- ✅ **列入 v3.1.4(若開)或下次文件性 release 的待辦**,本計畫不動
- 📝 同步補進 `docs/PHASE2-5_TODO.md`(若開新一輪)或 `docs/handoff/` 新的「後續待辦」檔

**風險**:低(Kenny 已拍板延後,且不會阻擋其他發現的修正)。

---

### 3.2 發現 #2:16 個視覺回歸測試在 CI 完全不跑 🔴【最關鍵,v3.1.4 採方案 A】

**事實**:
- `test_slide_rendering.py`(7 個)與 `test_visual_quality.py`(9 個)寫死 `PROJECT_ROOT = Path("/home/elan/fa-report-refactor")`
- 依賴的客戶 pptx 被 `.gitignore` 排除
- CI 環境跑這些測試時,`Path("/home/...")` 會找不到,但**目前 16 個測試都是 skip 而不是 fail**(因為測試內部還有 `pytest.skip()` 防線,但這層防線本身又依賴上面 §3.7 將提到的 `Path("")` 陷阱)
- 結論:**v3.1.1 那種「沒查證就宣稱完成」的安全網,在共用 CI 完全失效**——任何協作者重新引入 rotation/placeholder bug,CI 仍全綠

**Kenny 拍板(2026-09-03)**:✅ **採方案 A:提交去識別化/合成的樣本 pptx**

**v3.1.4 執行計畫**:
- 在 `tests/fixtures/` 放 1-2 個**刻意做壞又修好**的合成 pptx(完全去識別化、無 ELAN 真實資料),GitHub 可見、CI 可抓
- 修法流程:
  1. 設計合成 pptx 的 layout 結構:
     - **至少 2 個 layout** 一個要能觸發 Bug 3 直排旋轉(layout name 含「直排」)
     - 另一個要能觸發 placeholder 重疊或 idx 不為 0 的場景
     - 母片要有左上裝飾以觸發 v3.1.3 修的 TITLE_SAFE_LEFT_INCH=1.2 場景
  2. 寫 fixture builder 腳本(可放在 `scripts/build_synthetic_fixtures.py`),程式化產生而非手刻 pptx,確保日後可重現
  3. 把硬編 `Path("/home/elan/fa-report-refactor")` 改成讀環境變數或預設 `Path.cwd() / "tests" / "fixtures"`
  4. `test_slide_rendering.py` 與 `test_visual_quality.py` 改用合成 pptx
  5. commit message 與 CHANGELOG v3.1.4 條目**保留「視覺回歸測試真在 CI 跑」措辭**(誠實的 CI 防護)
- 工作量大約:中等(1-2 個工作天)
- **風險**:中(合成 pptx 設計錯誤會讓測試誤判通過,需仔細驗證)
- **驗證**:v3.1.4 釋出前,在全新 clone 環境(無 `/home/elan/fa-report-refactor` 路徑)跑一次 `pytest tests/`,確認 16 個視覺回歸測試**真的跑**而不是 skip
- **⛔ 注意**:合成 pptx 一旦提交,等同公開——不可含任何 ELAN 真實資料、客戶名稱、機密文字

#### 為什麼不選方案 B / C

- **方案 B(誠實化標注)** 放棄了「CI 自動防護」目標,只解決文件誠實度——治標不治本
- **方案 C(硬規則)** 會把協作者體驗搞得很差,Pi Agent 自己 fork 一份到別處也跑不動——不可行

---

### 3.3 發現 #3:`conftest.py` fixture 陷阱 🟡【v3.1.4 採方案 1】

**事實**:
- 3 個 fixture(`sample_pptx`、`sample_eval_json`、`sample_eval_txt`)在找不到檔案時回傳 `Path("")`
- `Path("").exists()` 永遠 `True`、`Path("").resolve()` 解析成當前 cwd
- 結果:**全新 clone 後直接 `pytest tests/` 會爆 12 個測試失敗**(包括聲稱「最關鍵」的 `test_master_protection.py` 4 個測試),錯誤訊息是難以理解的 `IsADirectoryError: Is a directory: '.'`

**Kenny 拍板(2026-09-03)**:✅ **同意修,採方案 1:`Path("")` 改 `None`**

**v3.1.4 執行計畫**:
- 修法:`tests/conftest.py` 第 109、122、134 行 `return candidates[0] if candidates else Path("")` 改為 `return candidates[0] if candidates else None`
- 呼叫端改判斷:
  - `if not sample_pptx.exists(): pytest.skip(...)` 改為 `if sample_pptx is None: pytest.skip(...)`
  - 完整 grep 所有用 `sample_pptx` / `sample_eval_json` / `sample_eval_txt` 的測試檔,逐個改判斷
- 工作量大約:1-2 小時(grep + 改判斷邏輯 + 重測)
- **風險**:低,但**改完必須驗證全新 clone 行為**
- **驗證流程**:
  1. 在 `/tmp` 開一個全新 clone(`git clone ...` 到 `/tmp/fa-test-clean/`)
  2. 不跑 `create_test_fixtures.py`,直接 `pytest tests/`
  3. 確認 12 個原本會爆 `IsADirectoryError` 的測試現在**乾淨 skip**(不是 fail、不是 error)
  4. 特別驗證 `test_master_protection.py` 4 個測試都要 skip 而不是 fail
- **附加驗證**:在原 Pi Agent 本機環境(`/home/elan/fa-report-refactor`),確認 pytest 結果與改動前一致(只是把 fail 變 skip,不能把原本 pass 的弄成 skip)

---

### 3.4 發現 #4:5-Why 流程圖內容 bug 🟡【v3.1.4 採方案 1:重設計 fallback 邏輯】

**事實**:
- `root_cause.py::_add_5why_flow_diagram()` 第 150 行 `short = s.split("。")[0][:15] if len(s) > 15 else s`
- 兩處問題:
  1. 沒有「。」時 `split` 回傳整段,再 `[:15]` 從單字中間切(中文也一樣從字中間切)
  2. 15 字太短(中文 15 字差不多一句完整建議,英文 15 char 才 2-3 個單字)
- 結果:前 2-3 個流程框顯示斷字斷詞的建議片段,後面接完全通用、沒填實際內容的「Why 2: 直接原因」

**Kenny 拍板(2026-09-03)**:✅ **這是真的 bug 不是已知可接受限制,採方案 1:重設計 fallback 邏輯**

**v3.1.4 執行計畫**:
- 重設計 `_add_5why_flow_diagram()`(在 `src/fa_improver/improvers/root_cause.py` 第 145-159 行附近):
  1. 若 suggestions 不足 5 個,**不要硬塞通用「Why X: XXX」佔位符**,而是只顯示實際有的 suggestions(可能 2-3 個而非硬湊 5 個)
  2. 截斷邏輯改成「按句號切(中英文 `。` 與 `.` 都認)、若沒有句號就保留原句、不強制 15 字」
  3. 或:**若 suggestions < 5 個,允許流程圖只有 N 個框,但在框下方加一行小字標注「補完更多建議可獲得完整 5-Why 分析」**
- 新增單元測試(在 `tests/unit/test_root_cause.py` 或新建):
  - `test_5why_short_suggestion_no_hard_truncate`:確認「短於 15 字、無句號」的建議不會被切字中間
  - `test_5why_few_suggestions_no_fake_padding`:確認「只有 2 個 suggestions」時流程圖只有 2 個框(或不超過實際數),沒有「Why 3/4/5」的通用佔位
  - `test_5why_chinese_period_handling`:確認中文「。」與英文 `.` 都能正確切句
- 工作量大約:2-4 小時(含測試)
- **風險**:中(改了 fallback 邏輯,可能影響 v3.1.3 已通過的真實報告產出視覺——需重跑 MS、N160JCN、260811 三份批次,確認 5-Why 流程圖看起來合理)
- **驗證**:
  1. 跑 MS / N160JCN / 260811 三份報告(若環境有)
  2. 視覺確認 5-Why 流程圖沒有「斷字斷詞」與「通用佔位」
  3. 母片保護測試仍全綠(`test_master_protection.py` 4 個)

---

### 3.5 發現 #5:版本號 3 處未同步 🟢【低成本,v3.1.4 嚴格執行 checklist】

**事實**:
- `pyproject.toml`:`3.1.0`
- `src/fa_improver/__init__.py`:`3.0.0`
- `SKILL.md` frontmatter:`3.1.0`
- 違反根倉庫 `docs/handoff/2026-08-31-v310-git-push-summary.md §5.3 步驟 4` 的發版 checklist

**Kenny 拍板(2026-09-03)**:✅ **從下個版本 v3.1.4 開始嚴格執行 checklist,不再回頭補 v3.1.3 的版本號未同步問題**

**v3.1.4 執行計畫**:
- v3.1.4 釋出時,**嚴格執行 §5.3 步驟 4 checklist**:
  1. 升級 `pyproject.toml`:`3.1.3` → `3.1.4`
  2. 升級 `src/fa_improver/__init__.py`:`3.0.0` → `3.1.4`
  3. 升級 `SKILL.md` frontmatter:`3.1.0` → `3.1.4`
  4. 升級 CHANGELOG.md 新增 v3.1.4 條目
- 同步檢查 `references/*.md` 與 `README.md` 是否有版本號殘留
- 工作量大約:10 分鐘(純文字,且是釋出流程的一部分)
- **風險**:0(嚴格執行既有 checklist,不是新動作)
- **附加效益**:v3.1.4 的 commit 會自然包含版本號同步,CHANGELOG 與 release 也一致

---

### 3.6 發現 #6:CHANGELOG tag 表格失真 🟢【低成本,可先做】

**事實**:
- CHANGELOG「標籤」表格列了 8 個 tag:`v3.1.3`、`v3.1.2`、`v3.1.1`、`v3.1.0`、`v3.0.1`、`v3.0.0`、`v2.3.0`、`baseline-v2.3.0`
- 實際:
  - GitHub:`v3.1.0`、`v3.1.2`、`v3.1.3`(3 個)
  - 本地 `git tag -l`:`v3.0.0`、`v3.0.1`、`v3.1.0`、`v3.1.2`、`v3.1.3`(5 個)
  - `v3.1.1` 已刪除(刻意)
  - `v2.3.0` 與 `baseline-v2.3.0` 完全不存在

**計畫**:
- ✅ 修法明確:把表格重寫,加註每個 tag 的實際存在狀態
- 建議格式:

  | Tag | 對應版本 | GitHub Release | 本地 tag | 重點 |
  |-----|---------|----------------|---------|------|
  | `v3.1.3` | 2026-09-02 | ✅ | ✅ | 修 3 個版面問題 + 4 個視覺回歸測試 |
  | `v3.1.2` | 2026-09-01 | ✅ | ✅ | 修 4 類渲染問題 + 視覺驗證腳本 |
  | `v3.1.1` | 2026-08-31 | ❌ 已刪 | ❌ 已刪 | **注意**:被 v3.1.2 取代 |
  | `v3.1.0` | 2026-08-31 | ✅ | ✅ | LLM 安全強化 + TemplateLoader + ... |
  | `v3.0.1` | 2026-08-31 | ❌ | ✅(未 push) | 補 Pre-commit + uv(僅本地) |
  | `v3.0.0` | 2026-08-31 | ❌ | ✅(未 push) | 模組化 + 6 維度覆蓋(僅本地) |
  | `v2.3.0` | 2026-01-28 | ❌ | ❌ | 不存在(推測應為「原始 baseline」之稱) |
  | `baseline-v2.3.0` | — | ❌ | ❌ | 不存在 |

- **⛔ 仍建議先問 Kenny**:`v2.3.0` 與 `baseline-v2.3.0` 是否曾經真的存在過?(稽核報告已標「repo 本身無法判斷」,可能 Kenny 還記得歷史脈絡)
- 若確認不存在,直接從 CHANGELOG 表格刪除這兩列
- 工作量大約:10 分鐘

---

## 4. 3 項「有疑慮/證據不足」之處理

| # | 項目 | 處理 |
|---|---|---|
| 1 | `_safe_shape.py::get_title_placeholder()` 第 158-170 行死碼(2 個分支結果相同) | 📝 加入 v3.1.4 待辦清單:確認是否要清理(目前 3 份樣本沒觸發,但邏輯沒對齊 commit 意圖) |
| 2 | 旋轉/直排偵測只認字串 `"直排"`/`"Vertical"`,遇「垂直/縱向/Portrait」會失效 | 📝 加入 v3.1.4 待辦清單:擴充關鍵字判斷或改用更穩健的偵測方式(例如讀 `XML orientation` 屬性而非 layout name 比對) |
| 3 | 視覺驗證覆蓋面窄(`find_content_layout()` 每份報告共用 1 個 layout,53 張 PNG 只驗 3 種 layout 組合) | 📝 加入 v3.1.4 待辦清單:客戶新母片模板時重新走一次視覺驗證流程 |

**不列入本次 PR 範圍**(稽核報告只標「待確認」,未要求立即處理)。

---

## 5. 不重複做的事情(從稽核報告 §7 學到的教訓)

> 此段從稽核報告節錄,目的是讓接手 Agent 不要重蹈覆轍。

- 🚫 **不要只跑本機 pytest 就宣稱「測試全過」**——發現 #2 就是因為這樣才以為有防護網
- 🚫 **不要假設寫死路徑的測試在別人的環境也會跑**——新增測試前要問自己「全新 clone 的機器上會怎樣」
- 🚫 **不要在 handoff 文件裡把「本機驗證過」寫成「已建立自動化防護機制」**——這是措辭誤導
- 🚫 **不要在看到稽核報告就直接動 code**——Kenny 還沒拍板,本計畫只整理事實 + 提方案
- 🚫 **不要拍板 4 個「待 Kenny 決定」的問題**(#2 方案選擇、#3 fixture 修法、#4 5-Why fallback、#5 版本號時機)——這是肯尼大 明確說「Pi Agent 不要自己拍板」的

---

## 6. 建議下一步(給 Kenny 拍板的決策清單) — 2026-09-03 已全部拍板

### 6.1 立刻可做的(若 Kenny 同意,本週內可完成)

1. **修 #5 版本號**:3 處都同步到 `3.1.3`,連同一個 commit 修 #6 CHANGELOG tag 表格——這兩個都是純文字、無風險
2. **修 #1 CI ruff format**:跑 `ruff format tests/integration/test_slide_rendering.py tests/integration/test_visual_quality.py`,順便讓 Build Distribution job 重跑——但**此項 Kenny 已表態不急**,可延後

### 6.2 需先決策再動手的(本計畫最關鍵) — 2026-09-03 Kenny 已拍板

| 決策 | Kenny 拍板結果 | 詳見 |
|------|----------------|------|
| **#2 視覺回歸測試策略** | ✅ **採方案 A(合成 pptx)** | §3.2 |
| **#3 conftest.py fixture 陷阱** | ✅ **同意修,採方案 1(Path 改 None)** | §3.3 |
| **#4 5-Why fallback** | ✅ **這是真的 bug,採方案 1(重設計 fallback 邏輯)** | §3.4 |
| **#5 版本號同步時機** | ✅ **從下個版本 v3.1.4 開始嚴格執行 checklist,不再回頭補 v3.1.3** | §3.5 |

→ 4 項決策全部確認,完整細節見 §10「Kenny 拍板結果摘要」。

### 6.3 加入未來 release 待辦(不需決策,只是排隊)

- 清理 `_safe_shape.py::get_title_placeholder()` 死碼
- 擴充旋轉/直排偵測的關鍵字覆蓋
- 視覺驗證流程適應新客戶母片模板

### 6.4 優先順序判斷原則(從稽核學到)

**這次稽核的核心教訓**:
- 「單元測試全綠 ≠ 改善完成」(v3.1.3 handoff 寫過)
- 「測試在自己機器全綠 ≠ 這個驗證機制對其他人有效」(這次稽核往前推一層)

→ 往後每次宣稱「已修正」或「已加防護機制」之前,養成習慣問:**這個結論拿到一台全新環境(CI 或別人機器)重跑,還會不會成立?**

### 6.5 v3.1.4 釋出時的工作排序建議

1. **第一步(打底)**:#5 版本號同步 → 這是釋出流程必做,順手做掉
2. **第二步(風險低)**:#3 conftest fixture 改 `None` + 改呼叫端判斷 → 風險低、修完驗證全新 clone 變 skip
3. **第三步(風險中)**:#4 5-Why fallback 重設計 + 新增單元測試 → 改完跑 3 份批次視覺驗證
4. **第四步(風險中)**:#2 合成 pptx + 改硬編路徑 → 設計合成 pptx、最後跑 CI 驗證真的會跑
5. **可選**:#1 ruff format + #6 CHANGELOG tag 表格(可在任何時候做,不依賴上述)

**⛔ v3.1.4 釋出前必須完成的最後一道驗證**:
- 在 `/tmp` 全新 clone 環境跑 `pytest tests/` → 確認 0 fail
- 在 GitHub Actions 觸發 CI → 確認全綠
- 在本機 Pi Agent 環境跑 `pytest tests/` → 確認與改動前數字一致(只把 fail 變 skip)

---

## 7. 關鍵檔案位置(供接手 Agent 查)

| 檔案 | 用途 |
|---|---|
| `docs/handoff/2026-09-02-fa-report-refactor-audit-handoff.md` | **本計畫的依據**(柔伊 的稽核報告,必讀) |
| `.agents/skills/fa-report-improvement/src/fa_improver/improvers/_safe_shape.py` | 死碼位置(第 158-170 行)、`_safe_shape` 常數與 helper |
| `.agents/skills/fa-report-improvement/src/fa_improver/improvers/root_cause.py` | 5-Why 流程圖 bug(第 145-159 行) |
| `.agents/skills/fa-report-improvement/tests/conftest.py` | `Path("")` 陷阱(第 109、122、134 行) |
| `.agents/skills/fa-report-improvement/tests/integration/test_visual_quality.py` | 硬編 `/home/elan/fa-report-refactor`(第 31 行) |
| `.agents/skills/fa-report-improvement/tests/integration/test_slide_rendering.py` | 硬編 `/home/elan/fa-report-refactor`(第 33 行) + ruff format 未跑(第 89 行) |
| `.agents/skills/fa-report-improvement/pyproject.toml` | 版本號 `3.1.0`(第 3 行) |
| `.agents/skills/fa-report-improvement/src/fa_improver/__init__.py` | 版本號 `3.0.0`(第 3 行) |
| `.agents/skills/fa-report-improvement/SKILL.md` | frontmatter 版本號 `3.1.0` |
| `.agents/skills/fa-report-improvement/CHANGELOG.md` | 標籤表格失真(第 612-621 行) |
| `.agents/skills/fa-report-improvement/.gitignore` | 排除 `report/*.pptx/json/txt`(第 56-60 行) + `*_vq*.pptx` 與 `*_improved_visual/`(第 83-93 行) |
| `docs/handoff/2026-08-31-v310-git-push-summary.md` §5.3 步驟 4 | 發版 checklist(版本號同步規定的出處) |
| GitHub: `https://api.github.com/repos/kcf7012/fa-report-refactor/actions/runs?per_page=5` | CI 紅綠燈實況 |
| GitHub: `https://api.github.com/repos/kcf7012/fa-report-refactor/tags` | 實際存在的 tag 列表 |

---

## 8. 待確認事項

(無技術性待確認,所有關鍵發現都已實地查證。)

✅ **4 項 Kenny 拍板決策已於 2026-09-03 全部確認**(原列為待確認,現已閉環),詳見 §10。

---

## 10. Kenny 拍板結果摘要(2026-09-03)

> 本節記錄 Kenny 針對 §6.2 4 項決策的回覆,作為 v3.1.4 執行時的唯一依據。

### 10.1 拍板來源

Kenny 在本次 session 回覆 4 項決策,Pi Agent 收到後:

1. 立即更新本計畫文件,把決策結果同步到對應章節(§3.2 / §3.3 / §3.4 / §3.5)
2. 提交 git commit 記錄拍板(見下方完成確認)
3. **未動任何程式碼**——執行留待 v3.1.4 工作 session

### 10.2 決策結果一覽表

| # | 問題 | Kenny 決策 | 對應章節 |
|---|------|-----------|---------|
| 1 | #2 視覺回歸測試策略:選 A/B/C? | **✅ A(合成 pptx)** | §3.2 |
| 2 | #3 conftest.py fixture 陷阱:是否同意修方案 1? | **✅ 同意,採方案 1** | §3.3 |
| 3 | #4 5-Why fallback:已知限制還是 bug? | **✅ 真的 bug,採方案 1** | §3.4 |
| 4 | #5 版本號同步時機:現在補 v3.1.3 還是從下個版本開始? | **✅ 從 v3.1.4 開始嚴格執行** | §3.5 |

### 10.3 v3.1.4 執行藍圖(Kenny 拍板後定稿)

| 順序 | 項目 | 預估時間 | 驗證方式 |
|------|------|---------|---------|
| 1 | **#5 版本號同步**(三處 → v3.1.4) | 10 分鐘 | 釋出流程中自動包含 |
| 2 | **#3 conftest fixture 改 None** | 1-2 小時 | 全新 clone 跑 pytest,12 個測試從 fail 變 skip |
| 3 | **#4 5-Why fallback 重設計** | 2-4 小時 | 新單元測試 + 3 份批次視覺驗證 |
| 4 | **#2 合成 pptx + 改硬編路徑** | 1-2 天 | 全新 clone + GitHub Actions 雙重驗證 16 個視覺回歸測試**真在跑** |

**可選 / 任何時候做**:
- #1 ruff format(同步讓 Build Distribution 重跑)
- #6 CHANGELOG tag 表格重寫(順手做掉)
- 清理 `_safe_shape.py` 死碼 + 擴充旋轉偵測關鍵字(未來 release 待辦)

### 10.4 不可在 v3.1.4 做的事

- 🚫 **不要回頭補 v3.1.3 的版本號未同步**——Kenny 明確說「從下個版本開始」
- 🚫 **不要把「本機驗證過」寫成「CI 自動防護」**——直到 #2 合成 pptx 完成且 CI 真的會跑
- 🚫 **不要在 #3 fixture 改 None 之前先修 #2 視覺回歸測試**——會踩到 `Path("")` 陷阱,驗證流程會誤判

### 10.5 v3.1.4 釋出前的最後一道關卡

- ✅ `/tmp` 全新 clone → `pytest tests/` → 0 fail
- ✅ GitHub Actions 觸發 CI → 全綠(尤其 Build Distribution 不再被 skip)
- ✅ 本機 Pi Agent 環境 → pytest 數字與改動前一致(只把 fail 變 skip)
- ✅ MS / N160JCN / 260811 三份批次報告 5-Why 流程圖視覺正常
- ✅ 母片保護測試 `test_master_protection.py` 全綠

---

## 10.6 v3.1.4 執行結果摘要(2026-09-03 完成)

> 本節記錄 v3.1.4 工作 session 的實際執行結果,用於閉環追蹤。

### ✅ 完成的 4 項 Kenny 拍板決策

| # | 決策 | 結果 |
|---|------|------|
| 1 | #2 視覺回歸測試:採方案 A(合成 pptx) | ✅ 完成 — 新增 3 個合成 fixture + `_fixture_resolver.py` |
| 2 | #3 conftest fixture 改 None | ✅ 完成 — 13 處呼叫端修正,全新 clone 0 fail |
| 3 | #4 5-Why fallback 重設計 | ✅ 完成 — `_truncate_step_text()` + 14 個新測試 |
| 4 | #5 版本號從 v3.1.4 開始嚴格執行 | ✅ 完成 — pyproject + __init__ + SKILL.md 三處同步到 3.1.4 |

### 📦 最終 commits(合併到 main)

```
5cb68a4 chore(pre-commit): 升級 ruff-pre-commit v0.1.9 → v0.16.5 與本機 ruff 對齊
76f8efe docs: 版本號 v3.1.3 → v3.1.4 + CHANGELOG 新增條目與修正標籤表
95f93e4 Merge pull request #1 from kcf7012/v3.1.4-audit-fixes
5b48690 style: 修正 test_slide_rendering.py assert 格式(讓 CI ruff format check 通過)
fc521fb style: 修正 6 個測試檔案的 import 排序(讓 CI ruff check 通過)
27495b1 fix(tests): 視覺回歸測試改用合成 fixture,讓 CI 真在跑 16 個視覺回歸測試
c87136f fix(improvers): 5-Why fallback 重設計 — 避免從字中間切與硬補通用佔位
18bb4cd fix(tests): conftest fixture 找不到時改回 None,修正全新 clone 環境的 IsADirectoryError
```

### 🎯 驗證結果

| 驗證項 | 結果 |
|--------|------|
| 本機 pytest | **233 passed, 3 skipped**(基線 219 + 14 新測試) |
| 模擬 CI(`FA_REPORT_PROJECT_ROOT=/nope/1`) | **233 passed, 3 skipped**,0 fail |
| CI Run #21(合併到 main 後) | **5/5 jobs success** |
| CI Run #23(release commit + pre-commit 升級後) | **5/5 jobs success** |
| ruff check | ✅ All checks passed |
| ruff format --check | ✅ All 70 files formatted |
| 母片保護測試 | ✅ 100%(本地 + CI 一致) |
| 視覺回歸測試 CI | ✅ 16 個真在跑(用合成 fixture),不再是 skip |
| Build Distribution CI | ✅ 從一直被 skip 變成正常執行 |

### 🌐 v3.1.4 Release

- **GitHub Release**:https://github.com/kcf7012/fa-report-refactor/releases/tag/v3.1.4
- **PR #1**:https://github.com/kcf7012/fa-report-refactor/pull/1(已 merge + 分支刪除)
- **Tag**:`v3.1.4` → commit `5cb68a4`(完整 main HEAD)
- **稽核生命週期**:從「稽核發現問題」→「改善計畫拍板」→「分階段執行」→「CI 驗證」→ 「Release 公開」,完整閉環

### 🔵 backlog(未來 release 待辦)

從稽核報告的 3 項「待確認」降級:
- 清理 `_safe_shape.py::get_title_placeholder()` 第 158-170 行死碼
- 擴充旋轉/直排偵測的關鍵字覆蓋(目前只認 "直排" / "Vertical")
- 視覺驗證流程適應新客戶母片模板(目前用 `find_content_layout()` 1 個 layout)

### ⚠️ 額外發現:pre-commit hook 行為不一致

本機 ruff 是 0.16.5,但 `.pre-commit-config.yaml` 的 `ruff-pre-commit` 用 v0.1.9——hook 修 import 排序的行為跟本機 ruff 不一致,造成 6 個檔案 import 排序錯誤被 commit 進去,CI 才抓到。已在 v3.1.4 升級到 v0.16.5 解決。

**經驗教訓**:未來任何工具(lint/format/type-check)應該跟 CI 用同一個版本,避免 hook 跟 CI 行為分歧造成隱藏 bug。

---

**v3.1.4 計畫閉環確認**:
✅ 4 項 Kenny 拍板決策全部執行完成
✅ 8 個 commits 進入 main(v3.1.3 → v3.1.4)
✅ CI 從 v3.1.3 的紅燈轉為 v3.1.4 的 5/5 success
✅ v3.1.4 Release 公開、tag 已推送
✅ 改善計畫文件閉環,可作為下個稽核週期的範本
