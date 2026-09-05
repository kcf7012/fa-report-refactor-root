# P4 — `get_title_placeholder()` 結構性缺口(已完成)

- 日期:2026-09-06
- 技能包 branch:`v3.1.5-cross-platform`(已推遠端,**未合併 main**)
- 驗收時 HEAD:`08e412add211dd4ebf9b1220a3da29ba70a968d0`(short `08e412a`)
- 對應計劃書:`docs/handoff/2026-09-05-cross-platform-migration-plan-handoff.md` 第 334 行起

---

## 一句話

原生 title placeholder 從此也要過安全左界檢查;順帶量出舊的 body margin
(1.00 in)本來就不夠,改成有量測依據的 1.35 in。

---

## 基準線與變動

| 項目 | P4 之前(`ea0c7fb`) | P4 之後(`08e412a`) |
|---|---|---|
| pytest | 239 passed / 0 skipped | **242 passed / 0 skipped** |
| 覆蓋率 | 89% | **89%** |
| CLI 兩條 | 通 | 通 |
| pre-commit | 12 hook 全過 | 12 hook 全過 |

**+3 是新增的三支測試**(見下方步驟 4),沒有任何既有測試被刪或改成較弱的斷言。
0 skipped 代表真實客戶檔有被讀到(這台機器的正常值);CI 上 `test_body_clears_master_left_decoration`
會 skip,屆時是 **241 passed + 1 skipped**。

> ⚠️ README badge 的數字這一輪仍**未動**(依第七輪報告第 3 項)。P4 已定案,
> 要對齊的話用上表的 242 / 89% @ `08e412a`。

---

## commit(4 個,順序本身就是證據)

```
cecd70a feat(scripts): 加母片裝飾量測腳本,結果寫進 _safe_shape 常數區   ← 只量測,不改值
306fd89 fix(safe_shape): 原生 title placeholder 也要過安全左界檢查
971d428 refactor(improvers): body margin 改用 BODY_SAFE_LEFT_INCH(19 處)
08e412a test(visual): placeholder 也要驗左界,加母片裝飾幾何重疊測試
```

實際 diff 的 10 個檔案(`git diff --name-only cecd70a^..HEAD`)已與待辦清單逐項對照過:

```
scripts/measure_master_decoration.py
src/fa_improver/improvers/_safe_shape.py
src/fa_improver/improvers/{analysis_method,basic_info,evidence_checklist,
                            prevention,problem_definition,root_cause,summary}.py
tests/integration/test_visual_quality.py
```

---

## 步驟 1:先量測,再定值

腳本:`.agents/skills/fa-report-improvement/scripts/measure_master_decoration.py`

```bash
cd .agents/skills/fa-report-improvement
uv run python scripts/measure_master_decoration.py
```

不帶參數時經 `fa_improver.paths.resolve_report_file()` 找**根倉庫** `report/` 的三份真實
客戶檔(技能包自己的 `report/` 只有 `test_sample.pptx`),外加三份合成 fixture。
找不到會明確列出缺哪一份,不靜默降級。

### 量測範圍的兩個判斷(這兩點決定了數字有沒有意義)

1. **只算「母片 + `find_content_layout()` 實際選中的那一個 layout」。**
   所有 improver 都經由 `find_content_layout(prs)` 取得 layout,一份簡報只會用到一個。
   把 Agenda / End / Chapter Idea 那些永遠用不到的 layout 算進來,數字會從 1.12 虛高到 4.73。
2. **滿版背景 / 橫幅不列入下限。** 260811 母片的 `Group 39` 佔 0.00~9.68 in,
   往右移一寸也閃不開,它本來就是 title 要疊在上面的設計元素。第一版腳本沒分類,
   結論是「`TITLE_SAFE_LEFT_INCH` 必須 > 13.33 in」——顯然無意義。
   排除了什麼**有印出來**,不做看不見的黑箱過濾。

### 結果

「可迴避左側裝飾」的最大右緣(in):

| 檔案 | 選中 layout | title 帶 | body 帶 |
|---|---|---|---|
| 260811_Kobo_ZHT_RA6080_SPcomFailI | 直排標題及文字 | — | **1.12** |
| MS_Meishan_ADO_445239_260716 | 2L - Topic | 0.97 | — |
| N160JCN-EEK … 260810 | Topic-Numbers | 0.97 | — |
| synthetic_C_decoration | Content with Caption | **1.00** | — |
| synthetic_A / synthetic_B | Content with Caption | — | — |

- title 帶(0.30~1.15 in)跨檔最大值 **1.00**
- body 帶(1.50 in ~ 底部 −0.5)跨檔最大值 **1.12** ← 260811 母片的 `Picture 14`
  (0.00~1.12,top 1.23~6.38)

**定值規則:量測最大值 + 0.20 in 緩衝,向上取到 0.05 的倍數。**

- title:1.00 + 0.20 = 1.20 → **1.20**,與既有值相同。
  量測獨立落回同一個數,不是為了配合既有測試才這樣選。
- body:1.12 + 0.20 = 1.32 → **1.35**。舊的 `TITLE_SAFE_LEFT_INCH - 0.2` = 1.00
  **不足**,比 `Picture 14` 右緣還左 0.12 in。

完整量測輸出已寫進 `_safe_shape.py` 常數區的註解,**跟著程式碼走**,不會像散落在
handoff 裡的數字那樣過期無人發現。

### 計劃書沒料到的一件事

計劃書假設「一般公司母片幾乎都提供原生 title placeholder,所以防線生效的那條路
反而是少數情況」。**實測相反**:三份真實客戶檔選中的 layout,沒有一份會走到原生
placeholder 分支——

- 260811 → layout 名含「直排」→ 第 141 行直接 `return None`
- MS `2L - Topic` / N160JCN `Topic-Numbers` → 該 layout **根本沒有** idx=0 或
  TITLE 型別的 placeholder(只有 idx=10 / idx=12 的 BODY),策略 1~3 全不命中

所以這個漏洞目前**只在合成 fixture `synthetic_C_decoration` 上實際觸發**。
漏洞是真的、修正是對的,但「三份真實報告現在正在漏」這個說法不成立,不要那樣寫。

---

## 步驟 2-3:修法與母片保護實證

`_ensure_title_left_safe(shape)` 套用在策略 1/2/3 的命中結果上。

- **移動而非放棄**:`ph.left = Inches(TITLE_SAFE_LEFT_INCH)`,保留母片給 placeholder
  的字型 / 顏色樣式。只有移完寬度 < `TITLE_MIN_WIDTH_INCH` 才降級成 `safe_textbox`。
- **寬度採「保留原本的右緣」**,不是補到投影片邊界。`Content with Caption` 的
  `Content Placeholder 2` 就緊接在 title 右邊(left=3.91),title 右緣 3.79 不動才不會撞上。
- **不自己追繼承鏈**:python-pptx 的 `_InheritsDimensions._effective_value()` 已做完
  「本層沒設就往 layout / master 取」,`ph.left` 就是有效值。只保留 `None` 判斷。
- `TITLE_MIN_WIDTH_INCH = 2.0` **不是量測值**,是可讀性下限的判斷值,已在常數註解裡
  與有量測依據的那幾個分開標示,免得被誤讀成也有母片量測背書。

### 母片保護:實際執行結果(不是推論)

```
--- test_master_protection.py ---
4 passed

--- 移動 title placeholder 前後,master / layout XML 逐字比對 ---
  移動前 title placeholder : left=0.50 w=3.29 in
  移動後 title placeholder : left=1.20 w=2.59 in
  右緣維持不變             : True
  master XML sha256 相同   : True
  layout XML sha256 全相同 : True
  layout 名稱/數量相同     : True  (11 個)
  幾何寫在 slide 層級 sp   : True
  MasterProtector 差異清單 : (空 —— 無任何違規)
```

計劃書「寫 slide 層級 `<a:xfrm>`、不動 master/layout」的推論**成立**,且已用
sha256 逐字比對與 `MasterProtector.diff()` 兩種方式各驗一次。

---

## 步驟 4-5:測試(含「修改前必須紅」的證據)

### 修既有測試

拿掉 `test_title_textbox_safe_left` 的 `if shape.is_placeholder: continue`。
順帶把 title 的 height 上限從 1.0 放寬到 1.5 —— 原生 title placeholder 常比 fallback
textbox 高(synthetic_C 是 1.27),用 1.0 會把它們整批濾掉,**又變成看不見的漏檢**。

### 新增三支(直接指名 `synthetic_C_decoration.pptx`)

不透過 `FIXTURE_FALLBACKS` 的 stem 對應:對應表會隨真實客戶檔在不在位改指到別的檔,
那樣本機與 CI 驗的不是同一件事,而且降級是靜默的。

| 測試 | 驗什麼 |
|---|---|
| `test_new_slide_titles_clear_safe_left` | title left >= `TITLE_SAFE_LEFT_INCH` |
| `test_no_new_shape_overlaps_left_decoration` | **幾何重疊**,而不是只驗程式碼與自己的常數一致 |
| `test_body_clears_master_left_decoration` | 守 body margin 修正;需真實客戶檔,CI 會 skip |

幾何測試同樣只採計「可迴避的左側裝飾」——把滿版橫幅算進去會變成必紅的假警報。

### 修改前紅的證據

pre-commit 的 pytest hook 是 `always_run`,**紅測試根本 commit 不進去**,所以這裡留
執行紀錄而非 commit。在 `cecd70a` + 只加測試的工作區上:

```
HEAD: cecd70a
工作區: 僅含新測試,src/ 尚未套用 P4 修正

tests/integration/test_visual_quality.py .FFF                            [100%]

E  AssertionError: title 落在安全左界之左:
E    Slide 6: 'Title 1' (placeholder=True) left=0.50 in < 1.2 in,text='FA 基本資訊'
E    Slide 7: 'Title 1' (placeholder=True) left=0.50 in < 1.2 in,text='5-Why 根因推導'
E    Slide 8: 'Title 1' (placeholder=True) left=0.50 in < 1.2 in,text='根因驗證及統計分析'
E    Slide 9: 'Title 1' (placeholder=True) left=0.50 in < 1.2 in,text='Executive Summary'

E  AssertionError: 新投影片壓到母片左側裝飾:
E    Slide 6: 'Title 1' (0.50,0.30)-(3.79,1.57) 壓到母片裝飾
E             'LeftTopDecoration' (0.00,0.00)-(1.00,0.50)
E    (Slide 7/8/9 同)

E  AssertionError: 新投影片壓到母片左側裝飾:
E    Slide 6: 'Rectangle 4'  (1.00,1.40)-(1.25,1.65) 壓到母片裝飾
E             'Picture 14' (0.00,1.23)-(1.12,6.38)
E    Slide 6: 'TextBox 18'   (1.00,5.50)-(9.00,7.00) 壓到母片裝飾 'Picture 14' 同上

3 failed, 1 passed, 8 deselected
```

套用 `306fd89` + `971d428` 後,同一條指令 → **4 passed**。

完整輸出留在本次 session 的 scratchpad(`p4-red-run.txt`、`p4-master-protection.txt`、
`p4-final-acceptance.txt`)。scratchpad 是 session 專屬、會被清掉的,**上面摘錄的段落
才是留存版本**——要重現就重跑 `git stash` 掉 src/ 的兩個 commit 再跑那條 `-k` 指令。

---

## P4 附帶的兩個 backlog

### (a) 死碼 —— 已處理:**刪掉**

```python
if len(list(slide.placeholders)) <= 1:
    return None
return None          # ← 兩個分支結果完全相同
```

不改成「移到策略 3 之前去真正實作原始意圖」的理由(已寫進程式碼註解):
improver 建立的新投影片一律來自 `find_content_layout()`,而它明文要求
`placeholder_count >= 2`(`layout/selector.py:22-24`),所以「只有 1 個 placeholder」
在這條路上**到不了**。把死碼改成會生效的分支,等於為一個不存在的情境新增行為變更。

### (b) 直排偵測 —— **P4 不做,留給 P7**(Kenny 2026-09-06 拍板)

理由:擴充關鍵字是丟棄式工作(改讀 `bodyPr/@vert` 之後整個作廢),而且只讓症狀變罕見、
機制照樣是猜名稱——這正是七輪稽核一直在抓的「看起來修好其實沒有」那一類。
P4 已含 19 處引用的行為變更且動到母片幾何,不再塞第三種變更。

已在 `_safe_shape.py` **兩處**留下明確註解(`get_title_placeholder()` 與
`get_body_placeholder()`),標明這是脆弱字串比對、只涵蓋 zh-TW / en、
zh-CN「竖排」與 ja「縦書き」會漏掉,並寫明「不要靠加關鍵字來修」。

---

## 交給 P7 的明確範圍(不要再降級成 backlog)

這兩處是**同一種脆弱比對**,要一起用「讀 XML 屬性而非猜名稱」的方式根治:

| 位置 | 現況 | 根治方向 |
|---|---|---|
| `src/fa_improver/improvers/_safe_shape.py` 的兩處直排偵測 | `if "直排" in layout_name or "Vertical" in layout_name` | 讀 `bodyPr` 的 `vert` 屬性 / placeholder 的 `orient` |
| `tests/integration/test_visual_quality.py:43` `RESIDUAL_TITLE_MARKERS` | `("按一下", "Click to add", "Click here to add")` | 同上;遇到 zh-CN / ja 母片會**假性通過** |

兩者都只涵蓋 zh-TW / en。這兩個 backlog 從第一輪稽核起「被降級後三輪都沒動」,
所以這次寫進文件而不是只留在對話裡。

---

## 這一輪順帶發現、但**沒有**在 P4 動的事

1. **`title` 與 `body` 可能解析到同一個 shape。** `get_title_placeholder()` 策略 2
   會回傳型別為 `TITLE` 的 placeholder;若它的 `idx != 0`,`get_body_placeholder()`
   的 `idx != 0` 條件會挑中**同一個 shape**,title 與 body 互相覆蓋。
   PowerPoint 產生的 title 一律 `idx=0`,現有六份 fixture 都到不了,屬低風險潛在缺陷。
   這是原本那段死碼「意圖」底下真正的風險,但與 placeholder 數量無關。
2. **殘留 63 個 iCloud 衝突副本 `.pyc`**(`* 2.pyc`),以及 `__pycache__` 內帶著
   **舊 Desktop 路徑**的 `co_filename` —— pytest verbose 會印出
   `<- ../../../../../Desktop/VibeProj/Claude/...`。已確認 `~/Projects/fa-report-refactor`
   **不是** symlink、舊路徑已不存在,純粹是搬家時一起被複製過來的過期 bytecode。
   本輪已 `find . -name '__pycache__' -exec rm -rf` 清掉。這些都在 `.gitignore` 內,
   不影響 commit,但**下次看到那個路徑不要以為搬家沒搬乾淨**。
3. **計劃書估「17 處引用」,實際 19 處。** 差異來源:`analysis_method.py` 的
   `table_left = ... + 4.0 + 0.3` 與各檔的 `import` 行。

---

## 給下一位接手者

1. **合併 P4**:技能包 `enforce_admins=true`,必須開 PR。branch 已推到
   `v3.1.5-cross-platform`,CI 綠了才能合。
2. **README badge / 版本號對齊**:P4 已定案,數字是 **242 passed / 89% @ `08e412a`**
   (CI 上 241 passed + 1 skipped)。計劃書 P6 那批四個 README 一起做。
3. **P5 之前先看** `2026-09-05-execution-findings-for-zoe-handoff.md` 發現 1
   ——計劃書 P5 的覆蓋率結論(85%)已被實測推翻。
4. 量測腳本可以重跑,母片換了直接看新數字,不要憑本文件的表格行動。
