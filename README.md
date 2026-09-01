# FA Report Refactor

> 半導體 **F**ailure **A**nalysis(FA)報告的智慧化改善工具集

[![Version](https://img.shields.io/badge/version-v3.1.3-blue)]()
[![Tests](https://img.shields.io/badge/tests-219%20passed-success)]()
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

---

## 專案總覽

本專案提供半導體 FA 報告的**智慧化改善工具**,基於 6 維度評分標準(基本資訊完整性 / 問題描述與定義 / 分析方法與流程 / 數據與證據支持 / 根因分析 / 改善對策),自動產生 Executive Summary、Key Improvements、5-Why 根因推導、改善對策時程圖等補充投影片。

**v3.1.3** 起新增:
- 修正「簡報標題偏左」(title 被母片左上裝飾擋住)
- 修正「標題與內容重疊」(body placeholder 太矮)
- 「6 維度評分分析」slide 預設關閉(用戶回饋)

---

## 快速開始

```bash
# 1. 安裝依賴(推薦 uv)
cd .agents/skills/fa-report-improvement
uv sync

# 2. 執行改善
uv run python -m fa_improver input.pptx \
  --eval eval.json \
  --output improved.pptx

# 3. 視覺驗證(選用)
uv run python scripts/visual_smoke_test.py --pptx improved.pptx
```

---

## 專案結構

```
fa-report-refactor/
├── README.md                           ← 本檔
├── AGENTS.md                           ← AI agent 規範
│
├── docs/                               ← 文件(根倉庫追蹤)
│   ├── 00_executive_summary.md         ← 重點摘要
│   ├── 01_assessment.md                ← 完整評估
│   ├── 02_refactor_plan.md             ← 5 階段重構計畫
│   ├── 07_llm_agent.md                 ← LLM 整合設計
│   ├── 10_api_reference.md             ← v3.0.1 公開 API 參考
│   ├── USER_GUIDE.md                   ← 終端使用者手冊
│   ├── TESTING.md                      ← 測試規範
│   ├── VISION.md                       ← v3.0 智慧化願景
│   └── handoff/                        ← 任務交接文檔(按日期組織)
│       ├── 2026-08-31-*-handoff.md
│       ├── 2026-09-01-v311-incomplete-rendering-handoff.md
│       ├── 2026-09-01-v312-final-fixes-handoff.md
│       └── 2026-09-01-v313-user-feedback-fixes-handoff.md  ← 最新
│
├── report/                             ← FA 報告與評估 JSON(根倉庫追蹤)
│   ├── fa_report_*.json
│   ├── *_improved.pptx                 ← 改善後的報告
│   └── *_visual/                       ← 視覺驗證圖片
│
└── .agents/                            ← 技能包總目錄(部分子仓库)
    ├── fa-report-improvement/          ← 主技能包(獨立 git 倉庫)
    │   ├── SKILL.md                    ← 技能包入口
    │   ├── CHANGELOG.md                ← 版本紀錄
    │   ├── src/fa_improver/            ← 主程式碼
    │   ├── tests/                      ← 219 個測試
    │   └── scripts/                    ← CLI 工具
    │
    ├── handoff-doc-generator/          ← 交接文檔產生器
    ├── commit-helper/                  ← Conventional commit 工具
    └── code-reviewer/                  ← 程式碼審查工具
```

---

## 雙倉庫架構

本專案使用**雙 git 倉庫**:

| 倉庫 | 追蹤範圍 | 工作目錄 |
|------|---------|---------|
| **根倉庫** | `docs/` + `report/` + `README.md` + `AGENTS.md` | `/home/elan/fa-report-refactor/` |
| **技能包倉庫** | `SKILL.md` + `src/` + `tests/` + `references/` | `/home/elan/fa-report-refactor/.agents/skills/fa-report-improvement/` |

### Commit 流程

```bash
# 1. 根倉庫(文件、改善後報告)
cd /home/elan/fa-report-refactor
git add docs/ report/ README.md
git commit -m "docs: 加 v3.1.3 交接文檔與最新改善報告"

# 2. 技能包倉庫(程式碼、測試)
cd .agents/skills/fa-report-improvement
git add src/ tests/ CHANGELOG.md
git commit -m "fix: 修 Kenny 回饋的 3 個版面問題"

# 3. Push
git push origin main  # 兩個倉庫各自獨立 push
```

---

## 版本歷史

| 版本 | 日期 | 重點 |
|------|------|------|
| **v3.1.3** | 2026-09-02 | 修 Kenny 回饋的 3 個版面問題(標題偏左/重疊/6 維度圖) |
| v3.1.2 | 2026-09-01 | 修 v3.1.1 殘留的 4 類版面渲染問題 + 加視覺驗證腳本 |
| v3.1.1 | 2026-08-31 | 修 v3.1.0 批次渲染空白頁 + 座標 bug |
| v3.1.0 | 2026-08-31 | 個資遮罩、tenacity 重試、TemplateLoader 整合、視覺元素 |
| v3.0.1 | 2026-08-30 | pre-commit + uv.lock + ppt_converter 測試 |
| v3.0.0 | 2026-08-30 | 模組化架構 + 6 維度完整覆蓋 + LLM 整合 |

完整紀錄:見 [.agents/skills/fa-report-improvement/CHANGELOG.md](.agents/skills/fa-report-improvement/CHANGELOG.md)

---

## 主要技能包(4 個)

| 技能包 | 用途 |
|--------|------|
| ⭐ [fa-report-improvement](.agents/skills/fa-report-improvement/SKILL.md) | FA 報告智慧化改善 |
| [handoff-doc-generator](.agents/skills/handoff-doc-generator/SKILL.md) | 任務交接文檔產生器 |
| [commit-helper](.agents/skills/commit-helper/SKILL.md) | Conventional commit 訊息產生器 |
| [code-reviewer](.agents/skills/code-reviewer/SKILL.md) | 自動化程式碼審查 |

---

## 給 AI Agent 的指引

開始工作前請讀:
1. **[AGENTS.md](AGENTS.md)** — 必讀(AI agent 工作規則)
2. **[docs/00_executive_summary.md](docs/00_executive_summary.md)** — 重點摘要
3. **[.agents/skills/fa-report-improvement/SKILL.md](.agents/skills/fa-report-improvement/SKILL.md)** — 主技能包入口

---

## 授權

MIT License

---

**最後更新**:2026-09-02(v3.1.3 發布)
**維護者**:Kenny Kang (ELAN FA Report 專案)