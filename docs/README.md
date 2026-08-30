# FA Report 專案文件索引

> **目的**:讓任何 Agent 或開發者進入此專案時,能快速找到需要的文件
> **目標讀者**:外部 Coding Agent、文件 Agent、評估 Agent、開發者

---

## 📂 專案結構

```
/home/elan/fa-report/
├── .agents/skills/fa-report-improvement/   # ★ 技能包本體(獨立 git 版本控制)
│   ├── .git/                                # 技能包自己的版本歷史
│   ├── SKILL.md                            # 技能包入口文件
│   ├── scripts/                            # 執行腳本
│   └── references/                         # 領域參考文件
│   ↑ 本資料來不納入根倉庫 git(有自己的版控)
│
├── docs/                                   # ★ 專案評估與設計文件
│   ├── README.md (本檔)
│   ├── 00_executive_summary.md             # 三件最重要的事
│   ├── VISION.md                           # 智慧化願景
│   ├── 01_assessment.md                    # 問題評估
│   ├── 02_refactor_plan.md                 # 重構計畫
│   ├── 03_design_comparison.md             # 視覺設計對比
│   ├── 04_summary_design.md                # Summary 設計
│   ├── 05_prevention_design.md             # 改善對策設計
│   ├── 06_expansion_patterns.md            # 通用展開模式
│   ├── 07_llm_agent.md                     # Agent 設計
│   └── 08_uv_integration.md                # uv 套件管理
│
└── report/                                 # FA 報告與評估 JSON
    ├── *.pptx                              # 原始報告
    ├── *_improved.pptx                     # 改善後報告
    └── fa_report_*.json                    # 評估 JSON
```

### 🔀 雙倉庫架構說明

本專案使用 **雙 git 倉庫**:

| 倉庫 | 位置 | 追蹤內容 | 對象 |
|------|------|---------|------|
| 根倉庫 | `/home/elan/fa-report/` | docs/ + report/ | 外部 Agent、評估者 |
| 技能包倉庫 | `.agents/skills/fa-report-improvement/` | SKILL.md + scripts/ + references/ | 技能包使用者、開發者 |

**為何分開?**技能包未來可能:
- 獨立打包分發給其他團隊
- 在不同 FA 報告專案中重複使用
- 由不同的開發者貢獻

**怎麼讓 Agent 看到技能包?** 技能包位置固定為 `.agents/skills/fa-report-improvement/`,Agent 可以直接讀取(不受根 git 影響)。

---

## 🚀 我是 Agent,我該看哪份文件?

### 如果你想快速理解專案(30 秒)
→ 看 `00_executive_summary.md`

### 如果你想了解技術問題與重構方向
→ 看 `01_assessment.md`(問題清單)+ `02_refactor_plan.md`(解決方案)

### 如果你想理解設計原則
→ 看 `VISION.md`(願景)+ `03_design_comparison.md`(視覺對比)

### 如果你想實作特定功能
- LLM 整合 → `07_llm_agent.md`
- 套件管理 → `08_uv_integration.md`
- 投影片展開 → `06_expansion_patterns.md`
- Summary 強化 → `04_summary_design.md`
- 改善對策 → `05_prevention_design.md`

### 如果你是 Coding Agent 接手開發
→ 依序看:`00_executive_summary.md` → `VISION.md` → `02_refactor_plan.md` → 對應功能文件

---

## 📊 評估與改善狀態

| 報告 | 原始分數 | 等級 | 改善狀態 |
|------|---------|------|---------|
| 260811_Kobo_ZHT_RA6080_SPcomFailI | 63.5 | D | ✅ 已改善(本次 session) |
| N160JCN-EEK project 1pcs NG | 55.5 | F | ✅ 已改善(本次 session) |
| MS_Meishan_ADO_445239 | 41.5 | F | ✅ 已改善(本次 session) |

---

## 🎯 核心原則(給所有 Agent)

1. **🛡️ 母片絕對不能被破壞** — 任何改善必須保留 ELAN 母片完整
2. **🎨 一張投影片只講一件事** — 不要把多個主題塞在一張
3. **🤖 視覺元素優先** — 每張投影片至少有 1 個非純文字元素
4. **📐 留白 ≥30%** — 不要填滿整張投影片
5. **🧪 任何改動都要測試** — 特別是母片保護測試

---

## 🔗 與外部 Agent 協作

此專案設計為可被多個 Agent 協作:

| Agent 類型 | 負責 | 主要參考文件 |
|-----------|------|------------|
| 評估 Agent | 6 維度評分 | `01_assessment.md` + `references/evaluation-criteria.md` |
| 設計 Agent | 投影片版面設計 | `03_design_comparison.md` + `06_expansion_patterns.md` |
| 開發 Agent | 程式碼實作 | `02_refactor_plan.md` + `07_llm_agent.md` |
| 文件 Agent | 文件維護 | `docs/README.md` + `references/` |
| 測試 Agent | 品質驗證 | `02_refactor_plan.md` 測試策略章節 |

---

**最後更新**:2026-08-30
**維護者**:Kenny Kang (ELAN FA Report 專案)