# Phase 4: 視覺元素生成 TODO

> **狀態**:✅ **全部完成於 v3.0.0**(2026-08-31)
> **5 種視覺元素**:checklist / flow diagram / comparison table / progress bar / timeline
> **對應檔案**:`src/fa_improver/visuals/base.py` + `tests/unit/test_visual_generators.py`

## 目標
讓每張投影片至少有 1 個視覺元素(checklist / 流程圖 / 對照表 / 進度條 / 時間軸),
不再只是純文字 bullet。

## 子任務

### 4.1 設計 VisualGenerator 介面
- [ ] `src/fa_improver/visuals/__init__.py`
- [ ] `src/fa_improver/visuals/base.py` — 抽象基類
- [ ] 統一 API:`generate(slide, section, content) -> None`

### 4.2 實作 ChecklistGenerator
- [ ] 使用 PowerPoint 內建 checkbox 字元 ☐ ☑
- [ ] 支援顏色編碼(高/中/低優先級)
- [ ] 自動換行與字型調整

### 4.3 實作 FlowDiagramGenerator
- [ ] 5-Why 推導流程圖
- [ ] 使用矩形 + 箭頭 shape
- [ ] 標示「目前在哪一層」

### 4.4 實作 ComparisonTableGenerator
- [ ] DVT vs PVT 對照表
- [ ] 自動建立 native PowerPoint table

### 4.5 實作 ProgressBarGenerator
- [ ] 6 維度評分進度條
- [ ] 使用矩形 shape 填充

### 4.6 實作 TimelineGenerator
- [ ] 立即/短期/中期/長期時間軸
- [ ] 使用箭頭 + 階段標記

### 4.7 整合到 improvers
- [ ] basic_info.py 使用 ChecklistGenerator
- [ ] root_cause.py 使用 FlowDiagramGenerator
- [ ] prevention.py 使用 TimelineGenerator
- [ ] summary.py 使用 ProgressBarGenerator(評分視覺化)

### 4.8 測試
- [ ] `tests/unit/test_visual_generators.py` (各類型 2+ 測試)
- [ ] 端對端:確認投影片渲染後視覺元素可見

## 預估工時
6-8 小時

## 成功標準
- 5 種視覺元素全部實作且可渲染
- 母片保護不被破壞
- 視覺元素可配置(顏色、大小、位置)
- 投影片渲染後視覺元素清晰可見(非文字雲)