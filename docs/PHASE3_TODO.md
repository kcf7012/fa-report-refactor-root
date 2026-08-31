# Phase 3: LLM Client 抽象層 + OpenAI 實作 TODO

> **狀態**:✅ **全部完成於 v3.0.0**(2026-08-31)
> **詳見**:`docs/07_llm_agent.md`(LLM 整合詳細設計)

## 目標
讓技能包不依賴 Coding Agent,可獨立呼叫 LLM 評估 pptx 報告。

## 子任務

### 3.1 設計 LLMClient Protocol
- [x] ✅ `src/fa_improver/llm/base.py`(v3.0.0 完成)
  - `LLMClient` Protocol(任何 LLM 都應實作)
  - `LLMResponse` dataclass
  - `LLMError` 例外

### 3.2 設計 EvaluationPrompt
- [x] ✅ `src/fa_improver/llm/prompts.py`(v3.0.0 完成)
  - System Prompt(基於 evaluation-criteria.md)
  - User Prompt 模板(從 pptx 內容生成)

### 3.3 實作 OpenAI Client
- [x] ✅ `src/fa_improver/llm/openai_client.py`(v3.0.0 完成)
  - 自動讀取 OPENAI_API_KEY 環境變數
  - 使用 JSON mode 確保結構化輸出
  - 重試與 timeout(⚠️ timeout 有,重試機制未實作)
  - Token 使用追蹤

### 3.4 實作 Mock Client(測試用)
- [x] ✅ `src/fa_improver/llm/mock_client.py`(v3.0.0 完成)
  - 回傳預錄的評估結果
  - 支援場景式測試

### 3.5 實作 LLM Evaluator
- [x] ✅ `src/fa_improver/llm/evaluator.py`(v3.0.0 完成)
  - 從 pptx 提取文字內容
  - 呼叫 LLM 評估
  - 將 LLM 回應轉為 EvaluationResult

### 3.6 CLI 整合
- [x] ✅ `cli.py` 加入 `--llm-provider` 參數
- [x] ✅ `cli.py` 加入 `--model` 參數
- [x] ✅ 自動從 .env 讀取 API key

### 3.7 測試
- [x] ✅ `tests/unit/test_llm_evaluator.py`(取代原計畫的 test_llm_base.py)
- [x] ✅ `tests/unit/test_openai_client.py`(用 mock)
- [x] ✅ `tests/unit/test_mock_client.py`
- [x] ✅ `tests/integration/test_llm_workflow.py`

### 3.6 CLI 整合(補充驗證)
- [ ] ⚠️ **無 `--api-key` CLI 參數**(從環境變數 / .env 取得即可)

### 3.8 文件
- [x] ✅ 更新 SKILL.md 說明 LLM 整合
- [x] ✅ README 加入 LLM 使用範例

## 預估工時
8 小時

## 成功標準
- [x] ✅ LLMClient Protocol 可被任何實作替換
- [x] ✅ OpenAI Client 可正常運作(需 API key)
- [x] ✅ Mock Client 讓測試可在離線執行
- [x] ✅ LLM 評估結果可直接用於後續改善流程
- [ ] ⚠️ **個資遮罩未實作**(grep 無結果)
- [x] ✅ Token 使用與成本估算

## 已知差距(待 v3.1+ 修正)
- ⚠️ **重試機制未實作**(無 tenacity / with_retry / backoff)
- ⚠️ **個資遮罩未實作**
- ⚠️ **無 `--api-key` CLI 參數**(雖寫在 PHASE3,但實際只靠環境變數)

## 實際交付
- 模組:`llm/base.py` + `llm/openai_client.py` + `llm/mock_client.py` + `llm/evaluator.py` + `llm/prompts.py`
- 測試:3 個 LLM 單元測試 + 1 個 integration,總計 ~20 個測試
- CLI:`--llm-provider` / `--model` 參數(從環境變數讀 API key)
- 文件:`docs/07_llm_agent.md` 詳細設計

對應 git tag: `v3.0.0`