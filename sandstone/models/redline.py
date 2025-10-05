"""Redlining output data models."""

from pydantic import BaseModel, Field

from sandstone.models.document import DocumentClause
from sandstone.models.playbook import PlaybookClause


class RedlineIssue(BaseModel):
    """Final output format matching expected_output.json."""
    
    text_snippet: str = Field(..., description="Exact problematic text from document")
    playbook_clause_reference: str = Field(..., description="Which playbook clause it violates")
    suggested_fix: str = Field(..., description="Suggested replacement text")


class IssueAnalysis(BaseModel):
    """Intermediate analysis result from LLM."""
    
    has_issue: bool = Field(..., description="Whether an issue was found")
    issue_type: str = Field(..., description="Type: red_flag, acceptable, or ideal")
    problematic_snippet: str = Field("", description="Specific problematic text")
    reasoning: str = Field("", description="Explanation of the issue")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class ClauseMatch(BaseModel):
    """Represents a match between document clause and playbook clause."""
    
    document_clause: DocumentClause = Field(..., description="Document clause")
    playbook_clause: PlaybookClause = Field(..., description="Matched playbook clause")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Semantic similarity score")
    rank: int = Field(..., ge=1, description="Rank of this match (1 = best)")
