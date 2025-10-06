"""Task function for Pydantic Evals - runs the redlining pipeline."""

from sandstone.services.document_parser import DocumentParser
from sandstone.services.playbook_loader import PlaybookLoader
from sandstone.services.semantic_matcher import SemanticMatcher
from sandstone.services.issue_analyzer import IssueAnalyzer
from sandstone.models.redline import RedlineIssue
from sandstone.evals.models import TaskInputs
from sandstone.config import BAD_DOCUMENT_FILE, PLAYBOOK_FILE, OPENAI_API_KEY

# Cache the pipeline results to avoid running it 8 times
_cached_results: list[RedlineIssue] | None = None


async def redline_document(inputs: TaskInputs) -> RedlineIssue:
    """Run the NDA redlining pipeline and return the issue for the expected clause type.
    
    This function:
    1. Parses the document
    2. Loads the playbook
    3. Matches document clauses to playbook clauses
    4. Analyzes matches for legal issues
    5. Returns the RedlineIssue matching the expected clause type
    
    Args:
        inputs: TaskInputs with expected clause type
        
    Returns:
        RedlineIssue for the specified clause type
    """
    global _cached_results
    
    # Check cache
    if _cached_results is None:
        # Run the full pipeline once
        parser = DocumentParser()
        doc_clauses = parser.parse(BAD_DOCUMENT_FILE)
        
        loader = PlaybookLoader()
        loader.load(PLAYBOOK_FILE)
        
        matcher = SemanticMatcher(loader)
        matches = matcher.get_best_matches(doc_clauses, min_similarity=0.4)
        
        analyzer = IssueAnalyzer(api_key=OPENAI_API_KEY)
        
        redlines = analyzer.analyze_and_generate_redlines(matches, verbose=False)
        
        # Cache results
        _cached_results = redlines
    
    # Find the redline for this clause type
    matching_issues = [
        r for r in _cached_results
        if r.playbook_clause_reference == inputs.expected_clause_type
    ]
    
    if not matching_issues:
        raise ValueError(f"No redline found for clause type: {inputs.expected_clause_type}")
    
    # Return the first issue if multiple are found
    # Note: Currently only evaluating the first issue per clause type
    # Future improvement: aggregate or compare multiple issues if needed
    return matching_issues[0]
