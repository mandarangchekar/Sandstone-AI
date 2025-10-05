"""Document clause data models."""

from pydantic import BaseModel, Field


class DocumentClause(BaseModel):
    """Represents an extracted clause from a document."""
    
    text: str = Field(..., description="Full text of the clause")
    section_number: str = Field(..., description="Section number (e.g., '1.1', '5.1')")
    section_title: str | None = Field(None, description="Parent section title (e.g., 'Definitions')")

