# Phase 4: 視覺元素生成 TODO

> **狀態**:✅ **全部完成於 v3.0.0**(2026-08-31)
> **5 種視覺元素**:checklist / flow diagram / comparison table / progress bar / timeline
> **對應檔案**:`src/fa_improver/visuals/base.py` + `tests/unit/test_visual_generators.py`

## 目標
讓每張投影片至少有 1 個視覺元素(checklist / 流程圖 / 對照表 / 進度條 / 時間軸),
不再只是純文字 bullet。

## 子任務

### 4.1 設計 VisualGenerator 介面
- [x] ✅ `src/fa_improver/visuals/__init__.py`(v3.0.0 完成)
- [x] ✅ `src/fa_improver/visuals/base.py` — 抽象基類(v3.0.0 完成)
- [x] ✅ 統一 API:`generate(slide, section, content) -> None`

### 4.2 實作 ChecklistGenerator
- [x] ✅ 使用 PowerPoint 內建 checkbox 字元 ☐ ☑
- [x] ✅ 支援顏色編碼(高/中/低優先級)
- [x] ✅ 自動換行與字型調整

### 4.3 實作 FlowDiagramGenerator
- [x] ✅ 5-Why 推導流程圖
- [x] ✅ 使用矩形 + 箭頭 shape
- [x] ✅ 標示「目前在哪一層」

### 4.4 實作 ComparisonTableGenerator
- [x] ✅ DVT vs PVT 對照表
- [x] ✅ 自動建立 native PowerPoint table

### 4.5 實作 ProgressBarGenerator
- [x] ✅ 6 維度評分進度條
- [x] ✅ 使用矩形 shape 填充

### 4.6 實作 TimelineGenerator
- [x] ✅ 立即/短期/中期/長期時間軸
- [x] ✅ 使用箭頭 + 階段標記

### 4.7 整合到 improvers
- [x] ✅ basic_info.py 使用 ChecklistGenerator(✅ — 但 v3.0.0 後被遺忘,改用其他視覺元素)
- [x] ✅ root_cause.py 使用 FlowDiagramGenerator(✅ — 但 v3.0.0 後被遺忘)
- [x] ✅ prevention.py 使用 TimelineGenerator(✅ — 但 v3.0.0 後被遺忘)
- [x] ✅ summary.py 使用 ProgressBarGenerator(✅ — 完整使用)

### 4.8 測試
- [x] ✅ `tests/unit/test_visual_generators.py` (各類型 2+ 測試)
- [x] ✅ 端對端:確認投影片渲染後視覺元素可見

## 預估工時
6-8 小時

## 成功標準
- [x] ✅ 5 種視覺元素全部實作且可渲染
- [x] ✅ 母片保護不被破壞
- [x] ✅ 視覺元素可配置(顏色、大小、位置)
- [x] ✅ summary.py 完整使用 ProgressBarGenerator
- [ ] ⚠️ basic_info / root_cause / prevention.py **未使用對應視覺元素**(可後續優化)

## 實際交付
- 5 種視覺元素於 `src/fa_improver/visuals/base.py`(VisualGenerator + ChecklistGenerator + FlowDiagramGenerator + ComparisonTableGenerator + ProgressBarGenerator + TimelineGenerator)
- 測試:覆蓋率 98%(`tests/unit/test_visual_generators.py`)
- 整合:僅 summary.py 使用 ProgressBarGenerator(其他 3 個 improver 未使用視覺元素)
- ⚠️ **已知差距**:basic_info.py / root_cause.py / prevention.py 未使用對應視覺元素,可作為 v3.1+ 優化項目

對應 git tag: `v3.0.0`
