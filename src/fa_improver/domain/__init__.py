"""Domain models - 純資料結構,不含業務邏輯"""

from .evaluation import (
    Dimension,
    DimensionScore,
    EvaluationResult,
    FailureType,
    GapSeverity,
    ReportContext,
)
from .suggestion import (
    ActionItem,
    Improvement,
    Priority,
    Suggestion,
)

__all__ = [
    "Dimension",
    "DimensionScore",
    "EvaluationResult",
    "FailureType",
    "GapSeverity",
    "ReportContext",
    "ActionItem",
    "Improvement",
    "Priority",
    "Suggestion",
]