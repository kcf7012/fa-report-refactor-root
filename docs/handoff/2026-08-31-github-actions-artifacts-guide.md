# Handoff: GitHub Actions Artifacts 使用指南

> 建立日期:2026-08-31
> 對象:專案成員、維護者、未來接手 Agent
> 適用專案:`fa-improver`(kcf7012/fa-report-refactor)

## 1. 什麼是 Artifacts?

**GitHub Actions Artifacts** 是 CI/CD workflow 在執行期間產生的檔案,例如:
- 構建好的套件(`*.whl`、`*.tar.gz`)
- 測試覆蓋率報告(`coverage.xml`)
- 日誌檔、二進位檔、截圖等

可在每次 workflow run 結束後下載,**預設保留 14 天**(可在 workflow 設定調整)。

---

## 2. v3.1.0 的 Artifacts 設定

在 `.github/workflows/test.yml` 中,2 個 jobs 上傳 Artifacts:

### 2.1 Coverage Report(來自 Test Python 3.10)

```yaml
- name: Upload coverage to Codecov
  if: matrix.python-version == '3.10' && matrix.os == 'ubuntu-latest'
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
    flags: unittests
    fail_ci_if_error: false
    token: ${{ secrets.CODECOV_TOKEN }}

- name: Archive coverage report
  if: matrix.python-version == '3.10' && matrix.os == 'ubuntu-latest'
  uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: coverage.xml
    retention-days: 30
```

**產出**:`coverage-report.zip`(內含 `coverage.xml`,4.61 KB)

### 2.2 Build Distribution(僅 main 分支)

```yaml
- name: Upload artifacts
  uses: actions/upload-artifact@v4
  with:
    name: dist-${{ github.sha }}
    path: dist/
    retention-days: 14
```

**產出**:`dist-<commit-sha>.zip`(內含 sdist + wheel,約 252 KB)

---

## 3. 如何下載 Artifacts

### 方法 1:從 Workflow Run 頁面(推薦)

1. **進入 Run 頁面**
   - 直接從 GitHub 倉庫 → Actions → 選擇 run
   - URL 範例:`https://github.com/kcf7012/fa-report-refactor/actions/runs/<run-id>`

2. **滾到頁面底部**
   - 找到 **"Artifacts"** 區塊

3. **點擊下載**
   - GitHub 自動下載 zip 檔
   - 每次 run 可下載任何成功上傳的 Artifacts

### 方法 2:從 Summary 頁面

1. 進入 run 頁面後,點擊右上 **"Summary"** tab
2. 在 Artifacts 清單點擊下載

### 方法 3:使用 `gh` CLI(命令列)

```bash
# 列出最新 run 的 Artifacts
gh run view <run-id> --json artifacts --jq '.artifacts[] | {name, sizeInBytes, expired}'

# 下載特定 Artifact
gh run download <run-id> --name coverage-report
gh run download <run-id> --name dist-cd61936bdfaedba14a992e2a828eced0ea67c94c

# 下載到指定目錄
gh run download <run-id> --name coverage-report --dir ./downloads
```

### 方法 4:使用 `gh API`(進階)

```bash
# 取得下載 URL
gh api repos/kcf7012/fa-report-refactor/actions/runs/<run-id>/artifacts

# 直接下載(需要 token)
curl -L -H "Authorization: token $GITHUB_TOKEN" \
  -o artifact.zip \
  https://api.github.com/repos/kcf7012/fa-report-refactor/actions/artifacts/<artifact-id>/zip
```

---

## 4. Artifacts 內容解析

### 4.1 coverage-report.zip

**檔案結構**:
```
coverage-report.zip
└── coverage.xml
```

**coverage.xml** 是 Codecov 標準 XML 格式,包含:
- 每個 .py 檔案的 stmts / miss / cover
- 行級覆蓋率(line coverage)
- 分支覆蓋率(branch coverage)

**範例內容**:
```xml
<?xml version="1.0" ?>
<coverage version="7.7.0" timestamp="..." lines-valid="1786" lines-covered="1558" line-rate="0.87">
  <file path="src/fa_improver/domain/template.py">
    <class name="TemplateValidationError">
      <lines>
        <line number="91" hits="1"/>
        <line number="92" hits="0"/>  <!-- 未覆蓋 -->
        ...
      </lines>
    </class>
  </file>
  ...
</coverage>
```

### 4.2 dist-<sha>.zip

**檔案結構**:
```
dist-cd61936...zip
├── fa_improver-3.1.0-py3-none-any.whl   ← Wheel(可直接安裝)
└── fa_improver-3.1.0.tar.gz             ← Source distribution
```

**`fa_improver-3.1.0-py3-none-any.whl`** 結構:
```
fa_improver-3.1.0-py3-none-any.whl
├── fa_improver/
│   ├── __init__.py
│   ├── cli.py
│   ├── llm/
│   ├── improvers/
│   └── ...
├── fa_improver-3.1.0.dist-info/
│   ├── METADATA           ← 套件 metadata
│   ├── WHEEL              ← wheel 格式資訊
│   ├── entry_points.txt   ← CLI 入口( fa-improve = fa_improver.cli:main )
│   └── RECORD             ← 檔案清單與 SHA256
```

---

## 5. 實際使用範例

### 5.1 安裝 wheel 套件(本地測試 release)

```bash
# 下載後解壓
unzip dist-cd61936bdfaedba14a992e2a828eced0ea67c94c.zip

# 安裝 wheel(使用 pip)
pip install ./dist/fa_improver-3.1.0-py3-none-any.whl

# 或使用 uv
uv pip install ./dist/fa_improver-3.1.0-py3-none-any.whl

# 驗證安裝
fa-improve --help
# 應顯示 v3.0 CLI 幫助

# 從原始 wheel 安裝(無需解壓)
pip install dist/fa_improver-3.1.0-py3-none-any.whl

# 安裝時可選擇性 extras
pip install ./dist/fa_improver-3.1.0-py3-none-any.whl[llm]
```

### 5.2 從 sdist 安裝(源碼 build)

```bash
# sdist 需要 build 過程
pip install ./dist/fa_improver-3.1.0.tar.gz

# 或解壓後手動 build
tar -xzf dist/fa_improver-3.1.0.tar.gz
cd fa_improver-3.1.0/
pip install -e .
```

### 5.3 檢視 Coverage Report

```bash
# 解壓
unzip coverage-report.zip

# 命令列摘要
coverage report -m
# 顯示:
# Name                                        Stmts   Miss  Cover
# ---------------------------------------------------------------
# src/fa_improver/__init__.py                     1      0   100%
# src/fa_improver/cli.py                          98     26    73%
# ...

# HTML 詳細報告
coverage html
# 產生 htmlcov/index.html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 5.4 上傳到 Codecov(手動)

如果 CI 因為缺少 `CODECOD_TOKEN` 沒上傳:

```bash
# 安裝 codecov CLI
pip install codecov

# 手動上傳
codecov --file=coverage.xml --token=<your-codecov-token>
```

### 5.5 驗證 wheel 內容(發布前)

```bash
# 列出 wheel 內所有檔案
unzip -l dist/fa_improver-3.1.0-py3-none-any.whl

# 解壓到目錄查看
mkdir wheel-contents
unzip dist/fa_improver-3.1.0-py3-none-any.whl -d wheel-contents/

# 查看 metadata
cat wheel-contents/fa_improver-3.1.0.dist-info/METADATA

# 驗證 entry points
cat wheel-contents/fa_improver-3.1.0.dist-info/entry_points.txt
# 應顯示:[console_scripts]
#          fa-improve = fa_improver.cli:main
```

---

## 6. Artifacts 的實際用途

| 場景 | 使用方式 | 範例 |
|------|---------|------|
| **本地安裝測試 release** | 下載 wheel + pip install | `pip install dist/fa_improver-3.1.0.whl` |
| **驗證 release 正確性** | 檢視 wheel 內容 | `unzip -l dist/*.whl` |
| **無網路環境部署** | 下載 Artifacts 帶到目標環境 | `pip install fa_improver-3.1.0.whl` |
| **Coverage 分析** | 用 coverage 工具讀 XML | `coverage report -m` |
| **Bug 報告附件** | 提供 coverage 證明 | 在 issue 附上 `coverage.xml` |
| **PyPI 發布驗證** | 用 twine 檢查 wheel | `twine check dist/*` |
| **歷史歸檔** | 每次 commit 的構建產物 | GitHub 自動保留 14 天 |

---

## 7. 注意事項與限制

### 7.1 保留期限

| retention-days | 保留天數 |
|-----------------|---------|
| 預設 | 90 天(public repo) |
| 自訂 | 可設 1-90 天 |
| GitHub Actions Pro/Enterprise | 可達 400 天 |

```yaml
# 範例:保留 30 天
- uses: actions/upload-artifact@v4
  with:
    retention-days: 30
```

### 7.2 大小限制

- **單一 Artifact**:最大 10 GB(免費帳號)
- **單次 Workflow run**:所有 Artifacts 合計無限制
- **下載限制**:每月有下載頻寬限制(具體視方案)

### 7.3 私有性

- **Public repo** Artifacts:任何人都能下載(無需登入)
- **Private repo** Artifacts:需要 GitHub 帳號 + 倉庫讀權限
- 不建議在 Artifacts 中放敏感資料(API key 等)

### 7.4 命名規範

```yaml
# ✅ 推薦:語義化命名
- uses: actions/upload-artifact@v4
  with:
    name: coverage-report          # 固定名稱(每次覆蓋)
    # 或
    name: dist-${{ github.sha }}  # 含 commit SHA(每次不同,不會覆蓋)
```

### 7.5 路徑規範

- 路徑相對於 runner 工作目錄(預設 `github.workspace`)
- 支援 glob(例如 `dist/**`)
- 支援目錄上傳(會保留目錄結構)

---

## 8. 故障排除

### 8.1 Artifact 沒出現

可能原因:
- 上傳 step 被 `if:` 條件跳過
- 路徑不存在(檢查 path 是否正確)
- Artifact 名稱衝突(同一 run 內)

```yaml
# 加 debug 步驟檢查
- name: Check artifacts dir
  run: ls -la dist/
```

### 8.2 下載失敗

可能原因:
- Artifacts 已過期(超過 retention-days)
- 沒有倉庫讀權限
- 網路問題

```bash
# 用 gh CLI 重新驗證
gh auth status
gh run view <run-id> --json artifacts
```

### 8.3 Coverage XML 損壞

若 Codecov 上傳失敗但 Artifacts 已產生:

```bash
# 驗證 XML 格式
xmllint --noout coverage.xml

# 重新產生
.venv/bin/pytest tests/ \
  --cov=fa_improver \
  --cov-report=xml \
  --cov-report=term-missing
```

---

## 9. 參考資源

### 9.1 官方文件

- **GitHub Actions Artifacts**:https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts
- **upload-artifact Action**:https://github.com/actions/upload-artifact
- **download-artifact Action**:https://github.com/actions/download-artifact
- **Codecov**:https://docs.codecov.com/

### 9.2 本專案連結

- **Workflow 設定**:`.github/workflows/test.yml`
- **Latest Run #13**:https://github.com/kcf7012/fa-report-refactor/actions/runs/3336315385
- **本文件**:`docs/handoff/2026-08-31-github-actions-artifacts-guide.md`

### 9.3 CLI 速查

```bash
# 列出 workflow runs
gh run list --limit 10

# 查看特定 run
gh run view <run-id>

# 下載所有 Artifacts
gh run download <run-id>

# 下載特定 Artifact
gh run download <run-id> --name <artifact-name>

# 列出某 run 的 Artifacts
gh api repos/kcf7012/fa-report-refactor/actions/runs/<run-id>/artifacts | jq '.artifacts[] | {name, size_in_bytes}'
```

---

## 10. 給未來維護者

當 Artifacts 政策需要調整時,檢查清單:

1. **保留天數**:`retention-days:` 是否足夠?(目前 coverage 30 天、dist 14 天)
2. **Codecov 整合**:`CODECOV_TOKEN` secret 是否設定?
3. **Wheel 建置**:`build` extra 是否正確安裝?
4. **上傳條件**:`if:` 條件是否正確(矩陣 / 分支)?
5. **檔案大小**:若檔案過大,考慮加 `.gitignore` 排除

---

✅ 本檔已寫入:`/home/elan/fa-report-refactor/docs/handoff/2026-08-31-github-actions-artifacts-guide.md`
   包含:10 個區塊,4 種下載方法,5 個實際使用範例,7 項故障排除,完整 CLI 速查
