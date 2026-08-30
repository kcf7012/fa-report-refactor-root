# Phase 3: LLM Client 抽象層 + OpenAI 實作 TODO

## 目標
讓技能包不依賴 Coding Agent,可獨立呼叫 LLM 評估 pptx 報告。

## 子任務

### 3.1 設計 LLMClient Protocol
- [ ] `src/fa_improver/llm/base.py`
  - `LLMClient` Protocol(任何 LLM 都應實作)
  - `LLMResponse` dataclass
  - `LLMError` 例外

### 3.2 設計 EvaluationPrompt
- [ ] `src/fa_improver/llm/prompts.py`
  - System Prompt(基於 evaluation-criteria.md)
  - User Prompt 模板(從 pptx 內容生成)

### 3.3 實作 OpenAI Client
- [ ] `src/fa_improver/llm/openai_client.py`
  - 自動讀取 OPENAI_API_KEY 環境變數
  - 使用 JSON mode 確保結構化輸出
  - 重試與 timeout
  - Token 使用追蹤

### 3.4 實作 Mock Client(測試用)
- [ ] `src/fa_improver/llm/mock_client.py`
  - 回傳預錄的評估結果
  - 支援場景式測試

### 3.5 實作 LLM Evaluator
- [ ] `src/fa_improver/llm/evaluator.py`
  - 從 pptx 提取文字內容
  - 呼叫 LLM 評估
  - 將 LLM 回應轉為 EvaluationResult

### 3.6 CLI 整合
- [ ] `cli.py` 加入 `--llm-provider` 參數
- [ ] `cli.py` 加入 `--model` 參數
- [ ] 自動從 .env 讀取 API key

### 3.7 測試
- [ ] `tests/unit/test_llm_base.py`
- [ ] `tests/unit/test_openai_client.py`(用 mock)
- [ ] `tests/unit/test_mock_client.py`
- [ ] `tests/integration/test_llm_workflow.py`

### 3.8 文件
- [ ] 更新 SKILL.md 說明 LLM 整合
- [ ] README 加入 LLM 使用範例

## 預估工時
8 小時

## 成功標準
- LLMClient Protocol 可被任何實作替換
- OpenAI Client 可正常運作(需 API key)
- Mock Client 讓測試可在離線執行
- LLM 評估結果可直接用於後續改善流程
- 個資遮罩(姓名、電話自動遮罩)
- Token 使用與成本估算