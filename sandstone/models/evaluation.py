"""Evaluation metrics data models."""

from pydantic import BaseModel, Field


class EvaluationMetrics(BaseModel):
    """Performance metrics for redlining quality."""
    
    precision: float = Field(..., ge=0.0, le=1.0, description="Precision score")
    recall: float = Field(..., ge=0.0, le=1.0, description="Recall score")
    f1_score: float = Field(..., ge=0.0, le=1.0, description="F1 score")
    total_issues_found: int = Field(..., description="Total issues detected")
    total_issues_expected: int = Field(..., description="Total expected issues")
    correctly_identified: int = Field(..., description="Correctly identified issues")

