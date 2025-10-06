"""Prompt templates for LLM-based issue detection."""

from sandstone.models.playbook import PlaybookClause


SYSTEM_PROMPT = """You are a legal expert specializing in NDA (Non-Disclosure Agreement) review and analysis.

Your role is to:
1. Analyze document clauses against established legal best practices
2. Identify problematic language, missing protections, or red flags
3. Classify issues by severity (red_flag vs acceptable vs ideal)
4. Extract specific problematic text snippets
5. Provide clear reasoning for your assessments

Be precise, thorough, and focus on protecting the discloser's interests."""


def create_analysis_prompt(document_text: str, playbook_clause: PlaybookClause) -> str:
    """Create structured prompt for issue analysis.
    
    Args:
        document_text: The clause text from the document (FULL TEXT - no truncation)
        playbook_clause: The matched playbook clause with criteria
        
    Returns:
        Formatted prompt for LLM analysis
    """
    return f"""Analyze the following NDA clause against legal best practices.

CLAUSE TO REVIEW:
{document_text}

CLAUSE TYPE: {playbook_clause.clause}

REVIEW INSTRUCTIONS:
{playbook_clause.review_instruction}

RED FLAGS (Major Issues):
{playbook_clause.red_flag}

IDEAL CHARACTERISTICS (Best Practice):
{playbook_clause.ideal}

ACCEPTABLE VARIATIONS (Minor Concerns):
{playbook_clause.acceptable}

TASK:
1. Analyze the clause against the playbook criteria
2. Determine if this clause has RED FLAGS (major issues that need fixing)
3. Set has_issue=True ONLY if there are red flag issues
4. If red flags exist, extract the specific problematic text snippet (exact quote)
5. Explain clearly what the red flag is and why it matters
6. Generate a comprehensive suggested fix that addresses the specific red flag found
   - Base it on the ideal characteristics provided
   - Include ALL key components from the ideal clause (e.g., for Recipient's Obligations, ensure you include: confidentiality, limited use, access control, breach notification, AND standard exceptions)
   - Make it practical and focused on fixing the identified issue
   - Use clear, plain language where possible
   - Be thorough - don't omit important protective provisions even for brevity
   - Keep it legally sound and comprehensive
7. Provide a confidence score (0.0 to 1.0) for your assessment

Note: Acceptable variations are NOT issues - they're tolerable. Only red flags are issues.

EXAMPLE IDEAL CLAUSE (for reference):
{playbook_clause.example_ideal_clause}

Your suggested fix should address the specific issue found, drawing from the ideal characteristics and example above."""


def create_batch_analysis_prompt(
    document_clauses: list[str], 
    playbook_clauses: list[PlaybookClause]
) -> str:
    """Create prompt for batch analysis (future optimization - NOT CURRENTLY USED).
    
    Note: This is a placeholder for potential future batch processing.
    Currently we analyze clauses one-by-one for better accuracy.
    
    Args:
        document_clauses: List of clause texts (full text)
        playbook_clauses: List of corresponding playbook clauses
        
    Returns:
        Formatted batch prompt
    """
    clause_pairs = []
    for i, (doc_text, playbook) in enumerate(zip(document_clauses, playbook_clauses), 1):
        clause_pairs.append(f"""
CLAUSE {i}:
Document Text: {doc_text}
Clause Type: {playbook.clause}
Red Flags: {playbook.red_flag}
""")
    
    return f"""Analyze the following NDA clauses in batch:

{chr(10).join(clause_pairs)}

For each clause, determine if issues exist."""