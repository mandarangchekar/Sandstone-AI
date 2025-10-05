"""Playbook clause data models."""

from pydantic import BaseModel, Field


class PlaybookClause(BaseModel):
    """Represents a single clause definition from the playbook."""
    
    # Core identification
    clause: str = Field(..., description="Name of the clause")
    clause_definition: str = Field(..., description="Definition of the clause")
    is_required: bool = Field(..., description="Whether clause is mandatory")
    
    # Review criteria (used for semantic search + LLM analysis)
    review_instruction: str = Field(..., description="Instructions for reviewing")
    ideal: str = Field(..., description="Ideal clause characteristics")
    acceptable: str = Field(..., description="Acceptable variations")
    red_flag: str = Field(..., description="Red flag indicators")
    
    # Fix templates (used for suggested fixes in output)
    example_ideal_clause: str = Field(..., description="Example of ideal clause")
    example_fallback_clause: str = Field(..., description="Fallback clause example")
