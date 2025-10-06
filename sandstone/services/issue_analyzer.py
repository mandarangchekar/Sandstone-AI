"""LLM-based issue analyzer using Instructor for structured outputs."""

from openai import OpenAI
import instructor

from sandstone.models.redline import ClauseMatch, IssueAnalysis, RedlineIssue
from sandstone.prompts.issue_detector import SYSTEM_PROMPT, create_analysis_prompt


class IssueAnalyzer:
    """Analyzes clause matches for legal issues using LLM."""
    
    def __init__(
        self, 
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1
    ):
        """Initialize issue analyzer.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o-mini for cost efficiency)
            temperature: Temperature for generation (low for consistency)
        """
        self.model = model
        self.temperature = temperature
        
        # Initialize Instructor client
        openai_client = OpenAI(api_key=api_key)
        self.client = instructor.from_openai(openai_client)
    
    def analyze_match(self, match: ClauseMatch) -> IssueAnalysis | None:
        """Analyze a clause match for legal issues.
        
        Uses LLM with structured output (Instructor) to analyze the document
        clause against playbook criteria.
        
        Args:
            match: ClauseMatch containing document and playbook clauses
            
        Returns:
            IssueAnalysis if successful, None if analysis fails
        """
        try:
            # Create prompt
            prompt = create_analysis_prompt(
                document_text=match.document_clause.text,
                playbook_clause=match.playbook_clause
            )
            
            # Call LLM with structured output
            analysis = self.client.chat.completions.create(
                model=self.model,
                response_model=IssueAnalysis,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature
            )
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing clause {match.document_clause.section_number}: {e}")
            return None
    
    def analyze_matches(
        self, 
        matches: list[ClauseMatch],
        verbose: bool = False
    ) -> list[tuple[ClauseMatch, IssueAnalysis]]:
        """Analyze multiple clause matches.
        
        Args:
            matches: List of ClauseMatch objects
            verbose: Whether to print progress
            
        Returns:
            List of (ClauseMatch, IssueAnalysis) tuples for clauses with issues
        """
        results = []
        
        for i, match in enumerate(matches, 1):
            if verbose:
                print(f"Analyzing {i}/{len(matches)}: Section {match.document_clause.section_number}...")
            
            analysis = self.analyze_match(match)
            
            if analysis and analysis.has_issue:
                results.append((match, analysis))
                if verbose:
                    print(f"  ✗ Red flag found")
            elif verbose:
                print(f"  ✓ No issues")
        
        return results
    
    def create_redline_issue(
        self,
        match: ClauseMatch,
        analysis: IssueAnalysis
    ) -> RedlineIssue:
        """Convert analysis to final redline issue format.
        
        Args:
            match: Original clause match
            analysis: Issue analysis from LLM (includes generated suggested fix)
            
        Returns:
            RedlineIssue in expected output format
        """
        return RedlineIssue(
            text_snippet=analysis.problematic_snippet,
            playbook_clause_reference=match.playbook_clause.clause,
            suggested_fix=analysis.suggested_fix
        )
    
    def analyze_and_generate_redlines(
        self,
        matches: list[ClauseMatch],
        verbose: bool = False
    ) -> list[RedlineIssue]:
        """Complete pipeline: analyze matches and generate redline issues.
        
        Args:
            matches: List of ClauseMatch objects
            verbose: Whether to print progress
            
        Returns:
            List of RedlineIssue objects
        """
        # Analyze all matches
        issue_pairs = self.analyze_matches(matches, verbose=verbose)
        
        # Convert to redline issues
        redlines = []
        for match, analysis in issue_pairs:
            redline = self.create_redline_issue(match, analysis)
            redlines.append(redline)
        
        return redlines
