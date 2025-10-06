"""Data models for Pydantic Evals evaluation system."""

from pydantic import BaseModel


class TaskInputs(BaseModel):
    """Inputs for the redlining evaluation task.
    
    This model defines the contract between the dataset and the task function.
    Each test case specifies which clause type to evaluate.
    """
    
    expected_clause_type: str
