"""CLI 入口"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pptx import Presentation

from .domain.evaluation import EvaluationResult
from .improvers.orchestrator import ImprovementOrchestrator
from .parsers.evaluation_parser import parse_evaluation


def main() -> int:
    """主入口"""
    parser = argparse.ArgumentParser(
        prog="fa-improve",
        description="半導體 FA 報告智慧化改善工具 v3.0",
    )
    parser.add_argument(
        "input",
        help="輸入 pptx 檔案路徑",
    )
    parser.add_argument(
        "--eval",
        "-e",
        required=True,
        help="評估檔(JSON 或 TXT)",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="輸出 pptx 檔案路徑",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="顯示詳細輸出",
    )
    args = parser.parse_args()

    try:
        return _run(args)
    except Exception as e:
        print(f"✗ 錯誤:{e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def _run(args) -> int:
    input_path = Path(args.input)
    eval_path = Path(args.eval)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"✗ 找不到輸入檔:{input_path}")
        return 1
    if not eval_path.exists():
        print(f"✗ 找不到評估檔:{eval_path}")
        return 1

    print(f"📖 解析評估檔:{eval_path}")
    evaluation = parse_evaluation(eval_path)
    print(f"   總分:{evaluation.total_score} ({evaluation.grade})")

    print(f"📊 載入簡報:{input_path}")
    prs = Presentation(input_path)
    print(f"   投影片數:{len(prs.slides)}")

    print(f"🔧 執行改善...")
    orchestrator = ImprovementOrchestrator(evaluation, input_path)
    result = orchestrator.execute(prs, output_path)

    print(f"\n✅ 完成!")
    print(f"   輸出:{result.output_path}")
    print(f"   投影片:{result.original_slide_count} → {result.final_slide_count}")
    print(f"   母片保護:{'✓' if result.master_preserved else '✗'}")
    print(f"   耗時:{result.duration_seconds:.1f}s")

    # 寫入 manifest
    manifest_path = output_path.with_suffix(output_path.suffix + ".manifest.json")
    manifest = {
        "execution_status": "success" if result.master_preserved else "failed",
        "input_file": str(input_path),
        "output_file": str(output_path),
        "original_slide_count": result.original_slide_count,
        "final_slide_count": result.final_slide_count,
        "master_preserved": result.master_preserved,
        "duration_seconds": result.duration_seconds,
        "actions": [a.value for a in result.plan.actions],
        "total_score_before": evaluation.total_score,
        "grade_before": evaluation.grade,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"   Manifest:{manifest_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())