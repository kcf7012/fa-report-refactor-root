# Handoff: fa-report-refactor 根目錄重新命名

> **建立時間**:2026-08-31
> **狀態**:進行中(等使用者退出/重新進入以解決 pi 工具 bash 路徑快取)

---

## 1. 目前任務目標

把 `/home/elan/fa-report` 重新命名為 `/home/elan/fa-report-refactor`,並更新所有文件內部對應的絕對路徑。

## 2. 已完成內容

✅ 目錄重新命名(已用 `mv` 完成):
```
/home/elan/fa-report → /home/elan/fa-report-refactor
```

## 3. 關鍵文件和位置

- **專案根目錄**:`/home/elan/fa-report-refactor/`
- **雙 git 倉庫架構**:
  - 根倉庫:`/home/elan/fa-report-refactor/.git/`(追蹤 `docs/` + `report/`)
  - 技能包倉庫:`/home/elan/fa-report-refactor/.agents/skills/fa-report-improvement/.git/`(追蹤 `src/` + `tests/`)
- **docs/**(19 份開發文件,根倉庫)
- **.agents/skills/fa-report-improvement/**(技能包本體)

## 4. 重要規則和限制

### pi 工具問題
- **目前 bash 鎖在舊路徑**:`/home/elan/fa-report`(已不存在)
- **解決方案**:使用者需退出/重新進入,讓 pi 工具重新建立工作目錄
- **臨時方案**:`read` 工具可正常用絕對路徑讀檔,`write` 工具可建立新檔

### 不要做的事
- ❌ 不要用 `mv` 把目錄改回 `fa-report`(會再次造成路徑衝突)
- ❌ 不要刪除 `.git/` 目錄(會失去版本歷史)
- ❌ 不要修改技能包內 `.git/`(它是獨立的子倉庫)

## 5. 已確認結論

✅ `/home/elan/fa-report-refactor/` 確實存在(用 read 工具驗證 `docs/README.md` 可讀)
✅ 雙 git 倉庫結構完整(根倉庫 + 技能包子倉庫)
✅ v3.0 重構已完成(89 個測試、6 維度全覆蓋、LLM 整合)

## 6. 待確認事項

⚠️ **未完成的更新**:
- 文件內部提到 `/home/elan/fa-report` 的位置需要批次改為 `/home/elan/fa-report-refactor`
- 估計影響:89 個測試通過、19 份 docs、8 個 JSON 樣板、3 個 Markdown 文件(SKILL/README/CHANGELOG)

⚠️ **待執行的搜尋與替換**:
```bash
# 等 bash 恢復後執行
cd /home/elan/fa-report-refactor
grep -rl "/home/elan/fa-report" --include="*.md" --include="*.py" --include="*.yml" --include="*.toml" . | head -30
```

## 7. 不要重複做的事情

- 不要再次執行 `mv`(目錄已改名)
- 不要在舊路徑 `/home/elan/fa-report` 操作任何東西(該路徑已不存在)
- 不要重新建立目錄(可能造成混亂)

## 8. 建議下一步

### 立即(使用者重新進入後)
1. 確認 bash 已恢復:`cd /home/elan/fa-report-refactor && pwd`
2. 搜尋所有提到 `/home/elan/fa-report` 的檔案
3. 用 `sed` 或 `read`+`write` 批次替換為 `/home/elan/fa-report-refactor`
4. 在兩個 git 倉庫分別 commit:「docs: 重新命名根目錄路徑」

### 後續(可選)
- 更新 CLAUDE.md 或 README 引用新路徑
- 驗證所有端對端測試仍可運轉
- 確認 OpenAI Dashboard 連結(若有引用舊路徑)

### 驗證指令(待執行)
```bash
cd /home/elan/fa-report-refactor
ls -la  # 應看到 .agents/ docs/ report/ 等
cd .agents/skills/fa-report-improvement
uv run python -m fa_improver --help  # 確認 CLI 仍可運作
pytest tests/ -q  # 確認 89 個測試仍通過
```

---

## 最後確認事項

下次進入時,**第一個指令應該是**:
```bash
cd /home/elan/fa-report-refactor && pwd && ls
```

如果 `pwd` 不是 `/home/elan/fa-report-refactor`,表示 pi 工具的 bash 仍未恢復,需要再嘗試退出/重新進入。
