# 測試規範 — v3.0

> **目標**:確保所有變更都有完整測試覆蓋,維持 92+ 測試通過
> **原則**:**TDD**(測試先行) + **母片保護**為最高優先

---

## 一、執行測試

### 快速指令

```bash
# 切到技能包目錄
cd .agents/skills/fa-report-improvement

# 全部測試
../venv/bin/python -m pytest tests/ -v

# 僅單元測試(快速)
../venv/bin/python -m pytest tests/unit/ -v

# 僅整合測試
../venv/bin/python -m pytest tests/integration/ -v

# 含覆蓋率
../venv/bin/python -m pytest tests/ --cov=src/fa_improver

# 跑特定測試
../venv/bin/python -m pytest tests/unit/test_filename_parser.py -v

# 跑特定測試類別
../venv/bin/python -m pytest tests/unit/test_visual_generators.py::TestChecklistGenerator -v
```

---

## 二、測試目錄結構

```
tests/
├── __init__.py
├── conftest.py                  # 共用 fixtures
│
├── unit/                         # 單元測試(快速、無外部依賴)
│   ├── __init__.py
│   ├── test_filename_parser.py
│   ├── test_evaluation_parser.py
│   ├── test_template_loader.py
│   ├── test_master_protection.py  # ★ 母片保護測試(最高優先)
│   ├── test_llm_evaluator.py
│   ├── test_mock_client.py
│   ├── test_openai_client.py      # 使用 Mock,不需要真實 API
│   ├── test_env_loading.py        # .env 載入測試
│   ├── test_visual_generators.py   # 視覺元素測試
│   ├── test_new_improvers.py      # Phase 4.5 新增測試
│   └── test_domain.py             # 領域模型測試
│
├── integration/                  # 端對端測試
│   ├── __init__.py
│   └── test_full_workflow.py      # 實際報告改善流程
│
└── fixtures/                     # 測試資料
    └── custom_templates/
        └── custom_basic_info.json
```

---

## 三、撰寫測試的規範

### 3.1 命名
- 檔案:`test_<模組名>.py`
- 類別:`Test<功能>` (PascalCase)
- 方法:`test_<情境>_<預期>` (snake_case)

範例:
```python
class TestEvaluationParser:
    def test_parse_simple_json(self): ...
    def test_parse_array_format(self): ...
    def test_missing_api_key_raises(self): ...
```

### 3.2 結構(AAA 模式)
```python
def test_addition_returns_correct_sum(self):
    # Arrange(準備)
    a, b = 2, 3
    calculator = Calculator()

    # Act(執行)
    result = calculator.add(a, b)

    # Assert(驗證)
    assert result == 5
```

### 3.3 Fixture 使用
```python
@pytest.fixture
def empty_prs():
    """空簡報(用於視覺元素測試)"""
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    yield slide, prs
    # 不需要清理(每個測試自己的 prs)

def test_something(empty_prs):
    slide, prs = empty_prs
    # ...
```

### 3.4 母片保護測試(必寫)

每當**新增**任何會修改 pptx 的功能,**必須**寫對應的母片保護測試:

```python
def test_new_feature_preserves_master(sample_pptx):
    """新功能不應破壞母片"""
    if not sample_pptx.exists():
        pytest.skip("範例 pptx 不存在")

    prs = Presentation(sample_pptx)
    protector = MasterProtector(prs)
    original_xml = prs.slide_masters[0].element.xml

    # 執行新功能
    new_feature(prs, ...)

    # 母片保護
    protector.verify_unchanged(prs)
    assert prs.slide_masters[0].element.xml == original_xml
```

---

## 四、測試覆蓋率目標

| 模組 | 目標覆蓋率 |
|------|-----------|
| `domain/` | ≥ 95% |
| `parsers/` | ≥ 90% |
| `layout/` | ≥ 95%(母片保護核心) |
| `improvers/` | ≥ 80% |
| `llm/` | ≥ 85% |
| `visuals/` | ≥ 80% |
| `templates/` | ≥ 85% |
| **整體** | **≥ 80%** |

---

## 五、CI 整合(未來)

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv sync
      - run: uv run pytest --cov=src/fa_improver --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## 六、測試資料管理

### 共用 Fixtures (`conftest.py`)

```python
@pytest.fixture
def sample_pptx():
    """範例 pptx 檔案"""
    return ROOT / "tests" / "fixtures" / "sample.pptx"

@pytest.fixture
def empty_prs():
    """空白簡報"""
    prs = Presentation()
    yield prs

@pytest.fixture(autouse=True)
def cleanup_env(monkeypatch):
    """每個測試後清理環境變數"""
    yield
    for key in ["OPENAI_API_KEY", "FA_IMPROVER_MODEL"]:
        monkeypatch.delenv(key, raising=False)
```

### 不使用真實 API
所有 LLM 測試**必須**使用 `MockLLMClient`,不可使用真實 API:
```python
def test_something():
    client = MockLLMClient()
    client.add_response("FA", '{"score": 80}')
    # ... 測試邏輯
```

---

## 七、除錯測試失敗

### 1. 查看失敗訊息
```bash
../venv/bin/python -m pytest tests/unit/test_xxx.py -v --tb=long
```

### 2. 進入 pdb 除錯
```bash
../venv/bin/python -m pytest tests/unit/test_xxx.py --pdb
```

### 3. 只跑失敗的測試
```bash
../venv/bin/python -m pytest --lf  # last failed
../venv/bin/python -m pytest --ff  # failed first
```

### 4. 詳細模式
```bash
../venv/bin/python -m pytest tests/ -vv --tb=long --capture=no
```

---

## 八、效能與並行

### 平行執行(未來)
```bash
../venv/bin/python -m pytest tests/ -n auto  # 需要 pytest-xdist
```

### 快速煙霧測試
```bash
../venv/bin/python -m pytest tests/ -x --tb=line -q
```

---

## 九、發布前檢查清單

每次發布前**必須**確認:

- [ ] 全部測試通過(`pytest tests/`)
- [ ] 母片保護測試全部通過
- [ ] 整合測試涵蓋所有報告樣本
- [ ] 覆蓋率 ≥ 80%
- [ ] 沒有殘留的 `.pyc` / `__pycache__` / `.env`
- [ ] `requirements.txt` 與 `pyproject.toml` 同步
- [ ] README / SKILL.md 文件更新
- [ ] CHANGELOG 記錄本次變更

---

## 十、測試失敗案例處理流程

```
測試失敗
  ↓
查看錯誤訊息
  ↓
判斷類型:
  ├─ 已知的環境問題(殘留 .env、venv 沒裝套件) → 修復環境
  ├─ 邏輯錯誤 → 修正程式碼
  ├─ 測試過時 → 更新測試
  └─ 母片保護失敗 → 絕對不能合併,先修程式碼
  ↓
確認修復
  ↓
新增對應測試(防止迴歸)
  ↓
重新跑全部測試
```

---

## 附錄:測試命名速查

| 測試類型 | 前綴 | 範例 |
|---------|------|------|
| 基本功能 | `test_<feature>_basic` | `test_add_slide_basic` |
| 邊界條件 | `test_<feature>_edge_case` | `test_parse_empty_content` |
| 錯誤處理 | `test_<feature>_raises` | `test_missing_key_raises` |
| 母片保護 | `test_<feature>_no_modify_master` | `test_visual_no_modify_master` |
| 整合 | `test_<flow>_integration` | `test_full_workflow_integration` |
| 效能 | `test_<feature>_performance` | (未來) |