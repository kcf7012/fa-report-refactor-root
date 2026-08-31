# Phase 5: 最終發布準備 TODO

> **狀態**:✅ **全部完成於 v3.0.1**(2026-08-31)
> **v3.0.1 tag 已建立**:`v3.0.0` + `v3.0.1`
> **測試結果**:102 passed + 3 skipped,覆蓋率 85%,ruff All checks passed

## 目標
把 v3.0 從「可用」提升為「可發布」,包含 CI/CD、文件、版本標記。

## 子任務

### 5.1 整合 .ppt 轉換支援
- [ ] 讓 CLI 支援 .ppt 輸入(目前只支援 .pptx)
- [ ] LibreOffice / pywin32 自動偵測
- [ ] 轉換失敗時明確錯誤訊息
- [ ] 整合 `scripts/improve_fa_report.py` 為 thin wrapper

### 5.2 uv 整合
- [ ] 執行 `uv lock` 產生 `uv.lock`
- [ ] 確認 `uv sync` 可正常運作
- [ ] 文件化 uv 安裝方式

### 5.3 CI/CD
- [ ] `.github/workflows/test.yml`(跑 pytest)
- [ ] 母片保護必須通過才能 merge
- [ ] 覆蓋率上傳(可選 codecov)

### 5.4 文件化
- [ ] 更新 `SKILL.md` 反映 v3.0 新特性
- [ ] 寫 CHANGELOG.md(正式版)
- [ ] README 加入快速開始指南
- [ ] API 文件(可選)

### 5.5 版本標記
- [ ] 標記 `v3.0.0` tag
- [ ] 移除 `baseline-v2.3.0` tag(已過時)

### 5.6 發布檢查清單
- [x] ✅ 105 個測試全部通過(102 passed + 3 skipped)
- [x] ✅ 母片保護 100%(4 個專門測試全綠)
- [x] ✅ 端對端 LLM 測試成功(test_llm_end_to_end.py)
- [x] ✅ .ppt 轉換支援測試(13 個測試全綠)
- [x] ✅ 文件完整(USER_GUIDE + 10_api_reference + 4 份 handoff)
- [x] ✅ pyproject.toml 套件可安裝(uv sync --all-extras 成功)

## 預估工時
4-6 小時

## 成功標準
- [x] ✅ v3.0 可獨立打包分發(uv build)
- [x] ✅ CI 自動跑測試並驗證母片保護
- [x] ✅ SKILL.md / README 反映 v3.0 新架構
- [x] ✅ 任何團隊 clone 後 `uv sync && uv run pytest` 就能運作

## 實際交付
- **.ppt 轉換**:CLI 整合 `converter.convert_if_needed(input_path)`
- **uv 整合**:`uv.lock`(343 KB,51 個套件)+ `.venv/` 已使用
- **CI/CD**:`.github/workflows/test.yml` + `.pre-commit-config.yaml`(4 大類 hook)
- **文件**:SKILL.md / CHANGELOG.md / README.md / `docs/10_api_reference.md`
- **Git tag**:`v3.0.0`(2026-08-31)+ `v3.0.1`(2026-08-31)
- **舊 tag**:`baseline-v2.3.0` 已移除
- **測試結果(驗證)**:102 passed + 3 skipped
- **覆蓋率**:85%(目標 80%)
- **ruff**:All checks passed
- **母片保護測試**:4 個專門測試全綠
- **.ppt 轉換測試**:13 個專門測試全綠

對應 git tag: `v3.0.0` + `v3.0.1`